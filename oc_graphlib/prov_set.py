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

import os
from datetime import datetime

from rdflib import Graph, ConjunctiveGraph
from rdflib.compare import to_isomorphic, graph_diff

from oc_graphlib.graph_entity import GraphEntity
from oc_graphlib.graph_set import GraphSet
from oc_graphlib.prov_entity import ProvEntity
from oc_graphlib.support.support import find_paths


class ProvSet(GraphSet):
    def __init__(self, prov_subj_graph_set, base_iri, context_path, default_dir, info_dir,
                 resource_finder, dir_split, n_file_item, supplier_prefix, triplestore_url,wanted_label=True):
        super(ProvSet, self).__init__(base_iri, context_path, info_dir, n_file_item, supplier_prefix,wanted_label=wanted_label)
        self.rf = resource_finder
        self.dir_split = dir_split
        self.default_dir = default_dir
        if triplestore_url is None:
            self.ts = None
        else:
            self.triplestore_url = triplestore_url
            self.ts = ConjunctiveGraph('SPARQLUpdateStore')
            self.ts.open((triplestore_url, triplestore_url))

        self.all_subjects = set()
        for cur_subj_g in prov_subj_graph_set.graphs():
            self.all_subjects.add(next(cur_subj_g.subjects(None, None)))
        self.resp = "SPACIN ProvSet"
        self.prov_g = prov_subj_graph_set

        if wanted_label:
            GraphSet.labels.update(
                 {
                    "pa": "provenance agent",
                    "se": "snapshot of entity metadata"
                }
             )

    # Add resources related to provenance information

    def add_se(self, resp_agent=None, prov_subject=None, res=None):
        return self._add_prov("se", ProvEntity.entity, res, resp_agent, prov_subject)

    def generate_provenance(self, resp_agent, c_time=None, do_insert=True, remove_entity=False):
        time_string = '%Y-%m-%dT%H:%M:%S'
        if c_time is None:
            cur_time = datetime.now().strftime(time_string)
        else:
            cur_time = datetime.fromtimestamp(c_time).strftime(time_string)

        # Add all existing information for provenance agents
        self.rf.add_prov_triples_in_filesystem(self.base_iri)

        if resp_agent is None:
            resp_agent = self.cur_name
        # The 'all_subjects' set includes only the subject of the created graphs that
        # have at least some new triples to add
        for prov_subject in self.all_subjects:
            cur_subj = self.prov_g.get_entity(prov_subject)

            # Load all provenance data of snapshots for that subject
            self.rf.add_prov_triples_in_filesystem(str(prov_subject), "se")
            last_snapshot = None
            last_snapshot_res = self.rf.retrieve_last_snapshot(prov_subject)
            if last_snapshot_res is not None:
                last_snapshot = self.add_se(resp_agent, cur_subj, last_snapshot_res)
            # Snapshot
            cur_snapshot = None
            cur_snapshot = self.add_se(resp_agent, cur_subj)
            cur_snapshot.snapshot_of(cur_subj)
            cur_snapshot.create_generation_time(cur_time)
            if cur_subj.source is not None:
                cur_snapshot.has_primary_source(cur_subj.source)
            cur_snapshot.has_resp_agent(resp_agent)

            # Old snapshot
            if last_snapshot is None and do_insert:  # Create a new entity
                cur_snapshot.create_description("The entity '%s' has been created." % str(cur_subj.res))
            else:
                if self._are_added_triples(cur_subj): # if diff != 0:
                    update_query_data = None
                    update_description = None
                    if do_insert:
                        update_query_data = self._are_added_triples(cur_subj)
                        update_description = "The entity '%s' has been extended with new statements." % str(cur_subj.res)
                    else:
                        update_query_data = self._create_delete_query(cur_subj.g)
                        if remove_entity:
                            update_description = "The entity '%s' has been removed." % str(cur_subj.res)
                        else:
                            update_description = "Some data of the entity '%s' have been removed. " % str(cur_subj.res)

                    cur_snapshot.create_description(update_description)
                    cur_snapshot.create_update_query(update_query_data)

                # Note: due to previous processing errors, it would be possible that no snapshot has been created
                # in the past for an entity, even if the entity actually exists. In this case, since we have to modify
                # the entity somehow, we create a new modification snapshot here without linking expicitly with the
                # previous one – which does not (currently) exist. However, the common expectation is that such
                # missing snapshop situation cannot happen.
                if last_snapshot is not None:
                    cur_snapshot.derives_from(last_snapshot)
                    last_snapshot.create_invalidation_time(cur_time)
                    cur_snapshot.invalidates(last_snapshot)

                # Invalidate the new snapshot if the entity has been removed
                if remove_entity:
                    cur_snapshot.invalidates(cur_snapshot)
                    cur_snapshot.create_invalidation_time(cur_time)

    @staticmethod
    def _create_insert_query(cur_subj_g):
        query_string, are_citations, are_ids, are_others = ProvSet.__create_process_query(cur_subj_g)

        return u"INSERT DATA { " + query_string + " }", are_citations, are_ids, are_others

    @staticmethod
    def _create_delete_query(cur_subj_g):
        query_string, are_citations, are_ids, are_others = ProvSet.__create_process_query(cur_subj_g)

        return u"DELETE DATA { " + query_string + " }", are_citations, are_ids, are_others

    def _are_added_triples(self, cur_subj):
        subj = cur_subj
        cur_subj_g = cur_subj.g
        prev_subj_g = Graph()
        query = "CONSTRUCT {<%s> ?p ?o} WHERE {<%s> ?p ?o}" % (subj , subj)
        print(query, '\n')
        result = self.ts.query(query)

        if result:
            for s,p,o in result:
                prev_subj_g.add((s,p,o))

            iso1 = to_isomorphic(prev_subj_g)
            iso2 = to_isomorphic(cur_subj_g)
            if iso1 == iso2: # the graphs are the same
                return None
            else:
                in_both, in_first, in_second = graph_diff(iso1, iso2)
                query_string = u"INSERT DATA { GRAPH <%s> { " % cur_subj_g.identifier
                query_string += in_second.serialize(format="nt11", encoding="utf-8").decode("utf-8")
                return query_string.replace('\n\n','') + "} }"

    @staticmethod
    def __create_process_query(cur_subj_g):
        query_string = u"GRAPH <%s> { " % cur_subj_g.identifier
        is_first = True
        are_citations = False
        are_ids = False
        are_others = False

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

    def _add_prov(self, short_name, prov_type, res, resp_agent, prov_subject=None):
        if prov_subject is None:
            g_prov = self.base_iri + "prov/"

            prov_info_path = \
                g_prov.replace(self.base_iri, self.info_dir.rsplit(os.sep, 2)[0] + os.sep) + short_name + ".txt"
        else:
            g_prov = str(prov_subject) + "/prov/"

            res_file_path = \
                find_paths(str(prov_subject), self.info_dir, self.base_iri, self.default_dir,
                           self.dir_split, self.n_file_item)[1][:-5]

            prov_info_path = res_file_path + os.sep + "prov" + os.sep + short_name + ".txt"
            #prov_info_path = \
            #    g_prov.replace(self.base_iri, self.info_dir.rsplit(os.sep, 2)[0] + os.sep) + short_name + ".txt"

        list_of_entities = [] if prov_subject is None else [prov_subject]
        cur_g, count, label = self._add(graph_url=self.g_prov, res=res, info_file_path=prov_info_path, short_name=short_name,
                                        list_of_entities=list_of_entities)
        return ProvEntity(list_of_entities[0] if list_of_entities else None, cur_g, res=res, res_type=prov_type, short_name=short_name,
                          resp_agent=resp_agent,
                          source_agent=None, source=None, count=count,
                          label=label, g_set=self)

    def _set_ns(self, g):
        super(ProvSet, self)._set_ns(g)
        g.namespace_manager.bind("oco", ProvEntity.OCO)
        g.namespace_manager.bind("prov", ProvEntity.PROV)
