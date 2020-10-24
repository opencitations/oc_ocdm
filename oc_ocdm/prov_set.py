#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2016, Silvio Peroni <essepuntato@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.
from __future__ import annotations

__author__ = 'essepuntato'

from datetime import datetime
from typing import Optional, Tuple, Set

from rdflib import Graph, ConjunctiveGraph, URIRef
from rdflib.compare import to_isomorphic, graph_diff, IsomorphicGraph
from rdflib.query import Result

from oc_ocdm import GraphEntity
from oc_ocdm import GraphSet
from oc_ocdm import ProvEntity
from oc_ocdm.counter_handler import CounterHandler
from oc_ocdm.support import get_short_name, get_count, get_prefix


class ProvSet(GraphSet):
    def __init__(self, prov_subj_graph_set: GraphSet, base_iri: str, context_path: str,
                 counter_handler: CounterHandler, supplier_prefix: str,
                 triplestore_url: str, wanted_label: bool = True) -> None:
        super(ProvSet, self).__init__(base_iri, context_path, counter_handler, supplier_prefix,
                                      wanted_label=wanted_label)
        if triplestore_url is None:
            self.ts: Optional[ConjunctiveGraph] = None
        else:
            self.triplestore_url: str = triplestore_url
            self.ts: Optional[ConjunctiveGraph] = ConjunctiveGraph('SPARQLUpdateStore')
            self.ts.open((triplestore_url, triplestore_url))

        self.all_subjects: Set[URIRef] = set()
        for cur_subj_g in prov_subj_graph_set.graphs():
            self.all_subjects.add(next(cur_subj_g.subjects(None, None)))
        self.resp: str = "SPACIN ProvSet"
        self.prov_g: GraphSet = prov_subj_graph_set

        if wanted_label:
            GraphSet.labels.update(
                {
                    "pa": "provenance agent",
                    "se": "snapshot of entity metadata"
                }
            )

    # Add resources related to provenance information

    def add_se(self, resp_agent: str = None, prov_subject: GraphEntity = None, res: URIRef = None) -> ProvEntity:
        g_prov: str = str(prov_subject) + "/prov/"
        list_of_entities: Tuple[GraphEntity] = () if prov_subject is None else (prov_subject,)
        cur_g, count, label = self._add_prov(graph_url=g_prov, res=res, short_name="se",
                                             list_of_entities=list_of_entities)
        return ProvEntity(list_of_entities[0] if list_of_entities else None, cur_g, res=res, res_type=ProvEntity.entity,
                          short_name="se", resp_agent=resp_agent, source_agent=None, source=None, count=count,
                          label=label, g_set=self)

    def generate_provenance(self, resp_agent: Optional[str], c_time: float = None, do_insert: bool = True,
                            remove_entity: bool = False) -> None:
        time_string: str = '%Y-%m-%dT%H:%M:%S'
        if c_time is None:
            cur_time: str = datetime.now().strftime(time_string)
        else:
            cur_time: str = datetime.fromtimestamp(c_time).strftime(time_string)

        if resp_agent is None:
            resp_agent = self.cur_name
        # The 'all_subjects' set includes only the subject of the created graphs that
        # have at least some new triples to add
        for prov_subject in self.all_subjects:
            cur_subj: GraphEntity = self.prov_g.get_entity(prov_subject)

            last_snapshot: Optional[ProvEntity] = None
            last_snapshot_res: Optional[URIRef] = self._retrieve_last_snapshot(prov_subject)
            if last_snapshot_res is not None:
                last_snapshot: ProvEntity = self.add_se(resp_agent, cur_subj, last_snapshot_res)
            # Snapshot
            cur_snapshot: ProvEntity = self.add_se(resp_agent, cur_subj)
            cur_snapshot.snapshot_of(cur_subj)
            cur_snapshot.has_generation_time(cur_time)
            if cur_subj.source is not None:
                cur_snapshot.has_primary_source(URIRef(cur_subj.source))
            cur_snapshot.has_resp_agent(URIRef(resp_agent))

            # Old snapshot
            if last_snapshot is None and do_insert:  # Create a new entity
                cur_snapshot.has_description("The entity '%s' has been created." % str(cur_subj.res))
            else:
                if self._are_added_triples(cur_subj):  # if diff != 0:
                    if do_insert:
                        update_query_data: Optional[str] = self._are_added_triples(cur_subj)
                        update_description: str = "The entity '%s' has been extended with new statements." \
                                                  % str(cur_subj.res)
                    else:
                        update_query_data: Optional[str] = self._create_delete_query(cur_subj.g)[0]
                        if remove_entity:
                            update_description: str = "The entity '%s' has been removed." % str(cur_subj.res)
                        else:
                            update_description: str = "Some data of the entity '%s' have been removed. " \
                                                      % str(cur_subj.res)

                    cur_snapshot.has_description(update_description)
                    cur_snapshot.has_update_action(update_query_data)

                # Note: due to previous processing errors, it would be possible that no snapshot has been created
                # in the past for an entity, even if the entity actually exists. In this case, since we have to modify
                # the entity somehow, we create a new modification snapshot here without linking explicitly with the
                # previous one – which does not (currently) exist. However, the common expectation is that such
                # missing snapshot situation cannot happen.
                if last_snapshot is not None:
                    cur_snapshot.derives_from(last_snapshot)
                    last_snapshot.has_invalidation_time(cur_time)
                    cur_snapshot.invalidates(last_snapshot)

                # Invalidate the new snapshot if the entity has been removed
                if remove_entity:
                    cur_snapshot.invalidates(cur_snapshot)
                    cur_snapshot.has_invalidation_time(cur_time)

    @staticmethod
    def _create_insert_query(cur_subj_g: Graph) -> Tuple[str, bool, bool, bool]:
        query_string, are_citations, are_ids, are_others = ProvSet.__create_process_query(cur_subj_g)

        return u"INSERT DATA { " + query_string + " }", are_citations, are_ids, are_others

    @staticmethod
    def _create_delete_query(cur_subj_g: Graph) -> Tuple[str, bool, bool, bool]:
        query_string, are_citations, are_ids, are_others = ProvSet.__create_process_query(cur_subj_g)

        return u"DELETE DATA { " + query_string + " }", are_citations, are_ids, are_others

    def _are_added_triples(self, cur_subj: GraphEntity) -> Optional[str]:
        subj: GraphEntity = cur_subj
        cur_subj_g: Graph = cur_subj.g
        prev_subj_g: Graph = Graph()
        query: str = "CONSTRUCT {<%s> ?p ?o} WHERE {<%s> ?p ?o}" % (subj, subj)
        print(query, '\n')
        result: Result = self.ts.query(query)

        if result:
            for s, p, o in result:
                prev_subj_g.add((s, p, o))

            iso1: IsomorphicGraph = to_isomorphic(prev_subj_g)
            iso2: IsomorphicGraph = to_isomorphic(cur_subj_g)
            if iso1 == iso2:  # the graphs are the same
                return None
            else:
                in_both, in_first, in_second = graph_diff(iso1, iso2)
                query_string: str = u"INSERT DATA { GRAPH <%s> { " % cur_subj_g.identifier
                query_string += in_second.serialize(format="nt11", encoding="utf-8").decode("utf-8")
                return query_string.replace('\n\n', '') + "} }"

    @staticmethod
    def __create_process_query(cur_subj_g: Graph) -> Tuple[str, bool, bool, bool]:
        query_string: str = u"GRAPH <%s> { " % cur_subj_g.identifier
        are_citations: bool = False
        are_ids: bool = False
        are_others: bool = False

        for s, p, o in cur_subj_g.triples((None, None, None)):
            if p == GraphEntity.cites:
                are_citations = True
            elif p == GraphEntity.has_identifier:
                are_ids = True
            else:
                are_others = True
        # HERE query ts and do the diff
        query_string += cur_subj_g.serialize(format="nt11", encoding="utf-8").decode("utf-8")

        return query_string + "}", are_citations, are_ids, are_others

    def _add_prov(self, graph_url: str, res: URIRef, short_name: str,
                  list_of_entities: Tuple[GraphEntity] = ()) -> Tuple[Graph, Optional[str], Optional[str]]:
        cur_g: Graph = Graph(identifier=graph_url)
        self._set_ns(cur_g)
        self.g += [cur_g]

        count: Optional[str] = None
        label: Optional[str] = None

        # This is the case when 'res_or_resp_agent' is a resource. It allows one to create
        # the graph entity starting from and existing URIRef, without incrementing anything
        # at the graph set level. However, a new graph is created and reserved for such resource
        # and it is added to the graph set.
        if res is not None:
            return cur_g, count, label

        # This is the case when 'res_or_resp_agent' is actually a string representing the name
        # of the responsible agent. In this case, a new individual will be created.
        related_to_label: str = ""
        related_to_short_label: str = ""
        # Note: even if list of entities is actually a list, it seems
        # that it would be composed by at most one item (e.g. for provenance)
        if list_of_entities:
            entity_res: URIRef = list_of_entities[0].res
            count = str(self.counter_handler.increment_counter(
                get_short_name(entity_res), "se", int(get_count(entity_res))))
            related_to_label += " related to"
            related_to_short_label += " ->"
            for idx, cur_entity in enumerate(list_of_entities):
                if idx > 0:
                    related_to_label += ","
                    related_to_short_label += ","
                cur_short_name = get_short_name(cur_entity)
                cur_entity_count = get_count(cur_entity)
                cur_entity_prefix = get_prefix(cur_entity)
                if cur_short_name == 'ci':
                    related_to_label += " %s %s" % (
                        self.labels[cur_short_name], cur_entity_count)
                    related_to_short_label += " %s/%s" % (
                        cur_short_name, cur_entity_count)
                else:
                    related_to_label += " %s %s%s" % (
                        self.labels[cur_short_name], cur_entity_prefix, cur_entity_count)
                    related_to_short_label += " %s/%s%s" % (
                        cur_short_name, cur_entity_prefix, cur_entity_count)
        else:
            count = self.supplier_prefix + str(self.counter_handler.increment_counter(short_name))

        if self.wanted_label:
            label = "%s %s%s [%s/%s%s]" % (
                self.labels[short_name], count, related_to_label,
                short_name, count, related_to_short_label)

        return cur_g, count, label

    def _set_ns(self, g: Graph) -> None:
        super(ProvSet, self)._set_ns(g)
        g.namespace_manager.bind("oco", ProvEntity.OCO)
        g.namespace_manager.bind("prov", ProvEntity.PROV)

    def _retrieve_last_snapshot(self, prov_subject: URIRef) -> Optional[URIRef]:
        subj_short_name: str = get_short_name(prov_subject)
        subj_count: str = get_count(prov_subject)
        try:
            if int(subj_count) <= 0:
                raise ValueError('prov_subject is not a valid URIRef. Extracted count value should be a positive '
                                 'non-zero integer number!')
        except ValueError:
            raise ValueError('prov_subject is not a valid URIRef. Unable to extract the count value!')

        last_snapshot_count: str = str(self.counter_handler.read_counter(subj_short_name, "se", int(subj_count)))
        if int(last_snapshot_count) <= 0:
            return None
        else:
            return URIRef(str(prov_subject) + '/prov/se/' + last_snapshot_count)
