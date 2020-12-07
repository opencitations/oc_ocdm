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
from typing import Optional, Tuple, List

from rdflib import Graph, ConjunctiveGraph, URIRef
from rdflib.compare import to_isomorphic, graph_diff, IsomorphicGraph

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

        self.prov_g: GraphSet = prov_subj_graph_set

        if wanted_label:
            GraphSet.labels.update(
                {
                    "se": "snapshot of entity metadata"
                }
            )

    def add_se(self, prov_subject: GraphEntity, res: URIRef = None) -> ProvEntity:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        g_prov: str = str(prov_subject) + "/prov/"
        cur_g, count, label = self._add_prov(graph_url=g_prov, res=res, short_name="se", prov_subject=prov_subject)
        return ProvEntity(prov_subject, cur_g, res=res, res_type=ProvEntity.iri_entity, short_name="se",
                          resp_agent=prov_subject.resp_agent, source_agent=prov_subject.source_agent,
                          source=prov_subject.source, count=count, label=label, g_set=self)

    def _create_snapshot(self, cur_subj: GraphEntity, cur_time: str) -> ProvEntity:
        new_snapshot: ProvEntity = self.add_se(prov_subject=cur_subj)
        new_snapshot.snapshot_of(cur_subj)
        new_snapshot.has_generation_time(cur_time)
        if cur_subj.source is not None:
            new_snapshot.has_primary_source(URIRef(cur_subj.source))
        if cur_subj.resp_agent is not None:
            new_snapshot.has_resp_agent(URIRef(cur_subj.resp_agent))
        return new_snapshot

    def _get_snapshots_from_merge_list(self, cur_subj: GraphEntity) -> List[ProvEntity]:
        snapshots_list: List[ProvEntity] = []
        for entity in cur_subj.merge_list:
            last_entity_snapshot_res: Optional[URIRef] = self._retrieve_last_snapshot(entity.res)
            if last_entity_snapshot_res is not None:
                snapshots_list.append(self.add_se(prov_subject=entity, res=last_entity_snapshot_res))
        return snapshots_list

    @staticmethod
    def _get_merge_description(cur_subj: GraphEntity, snapshots_list: List[ProvEntity]) -> str:
        merge_description: str = f"The entity '{cur_subj.res}' has been merged"
        is_first: bool = True
        for snapshot in snapshots_list:
            if is_first:
                merge_description += f" with '{snapshot.prov_subject.res}'"
                is_first = False
            else:
                merge_description += f", '{snapshot.prov_subject.res}'"
        merge_description += "."
        return merge_description

    def generate_provenance(self, c_time: float = None) -> None:
        time_string: str = '%Y-%m-%dT%H:%M:%S'
        if c_time is None:
            cur_time: str = datetime.now().strftime(time_string)
        else:
            cur_time: str = datetime.fromtimestamp(c_time).strftime(time_string)

        # MERGED ENTITIES
        for cur_subj in self.prov_g.res_to_entity.values():
            if cur_subj is None or (not cur_subj._was_merged or cur_subj._to_be_deleted):
                # Here we must skip every entity that was not merged or that must be deleted.
                continue

            # Previous snapshot
            last_snapshot_res: Optional[URIRef] = self._retrieve_last_snapshot(cur_subj.res)
            if last_snapshot_res is None:
                # CREATION SNAPSHOT
                cur_snapshot: ProvEntity = self._create_snapshot(cur_subj, cur_time)
                cur_snapshot.has_description(f"The entity '{cur_subj.res}' has been created.")
            else:
                update_query: Optional[str] = self._get_update_query(cur_subj)
                was_modified: bool = update_query is not None
                snapshots_list: List[ProvEntity] = self._get_snapshots_from_merge_list(cur_subj)

                if was_modified and len(snapshots_list) <= 0:
                    # MODIFICATION SNAPSHOT
                    last_snapshot: ProvEntity = self.add_se(prov_subject=cur_subj, res=last_snapshot_res)
                    last_snapshot.has_invalidation_time(cur_time)

                    cur_snapshot: ProvEntity = self._create_snapshot(cur_subj, cur_time)
                    cur_snapshot.derives_from(last_snapshot)
                    cur_snapshot.has_update_action(update_query)
                    cur_snapshot.has_description(f"The entity '{cur_subj.res}' has been modified.")
                elif len(snapshots_list) > 0:
                    # MERGE SNAPSHOT
                    last_snapshot: ProvEntity = self.add_se(prov_subject=cur_subj, res=last_snapshot_res)
                    last_snapshot.has_invalidation_time(cur_time)

                    cur_snapshot: ProvEntity = self._create_snapshot(cur_subj, cur_time)
                    cur_snapshot.derives_from(last_snapshot)
                    for snapshot in snapshots_list:
                        cur_snapshot.derives_from(snapshot)
                    cur_snapshot.has_description(self._get_merge_description(cur_subj, snapshots_list))

        # EVERY OTHER ENTITY
        for cur_subj in self.prov_g.res_to_entity.values():
            if cur_subj is None or (cur_subj._was_merged and not cur_subj._to_be_deleted):
                # Here we must skip every entity which was merged while not being marked as to be deleted,
                # since we already processed those entities in the previous loop.
                continue

            last_snapshot_res: Optional[URIRef] = self._retrieve_last_snapshot(cur_subj.res)
            if last_snapshot_res is None:
                if cur_subj._to_be_deleted:
                    # We can ignore this entity because it was deleted even before being created.
                    continue
                # CREATION SNAPSHOT
                cur_snapshot: ProvEntity = self._create_snapshot(cur_subj, cur_time)
                cur_snapshot.has_description(f"The entity '{cur_subj.res}' has been created.")
            else:
                update_query: Optional[str] = self._get_update_query(cur_subj)
                was_modified: bool = update_query is not None

                if cur_subj._to_be_deleted:
                    # DELETION SNAPSHOT
                    last_snapshot: ProvEntity = self.add_se(prov_subject=cur_subj, res=last_snapshot_res)
                    last_snapshot.has_invalidation_time(cur_time)

                    cur_snapshot: ProvEntity = self._create_snapshot(cur_subj, cur_time)
                    cur_snapshot.derives_from(last_snapshot)
                    cur_snapshot.has_invalidation_time(cur_time)
                    cur_snapshot.has_description(f"The entity '{cur_subj.res}' has been deleted.")
                    cur_snapshot.has_update_action(update_query)
                elif was_modified:
                    # MODIFICATION SNAPSHOT
                    last_snapshot: ProvEntity = self.add_se(prov_subject=cur_subj, res=last_snapshot_res)
                    last_snapshot.has_invalidation_time(cur_time)

                    cur_snapshot: ProvEntity = self._create_snapshot(cur_subj, cur_time)
                    cur_snapshot.derives_from(last_snapshot)
                    cur_snapshot.has_description(f"The entity '{cur_subj.res}' has been modified.")
                    cur_snapshot.has_update_action(update_query)

    @staticmethod
    def __get_delete_query(graph_iri: URIRef, data: Graph) -> Optional[str]:
        if len(data) == 0:
            return None
        delete_string: str = f"DELETE DATA {{ GRAPH <{graph_iri}> {{ "
        delete_string += data.serialize(format="nt11", encoding="utf-8").decode("utf-8")
        return delete_string.replace('\n\n', '') + "} }"

    @staticmethod
    def __get_insert_query(graph_iri: URIRef, data: Graph) -> Optional[str]:
        if len(data) == 0:
            return None
        insert_string: str = f"INSERT DATA {{ GRAPH <{graph_iri}> {{ "
        insert_string += data.serialize(format="nt11", encoding="utf-8").decode("utf-8")
        return insert_string.replace('\n\n', '') + "} }"

    @staticmethod
    def _get_update_query(cur_subj: GraphEntity) -> Optional[str]:
        current_graph: Graph = cur_subj.g
        preexisting_graph: Graph = cur_subj.preexisting_graph

        if cur_subj._to_be_deleted:
            return ProvSet.__get_delete_query(current_graph.identifier, preexisting_graph)
        else:
            preexisting_iso: IsomorphicGraph = to_isomorphic(preexisting_graph)
            current_iso: IsomorphicGraph = to_isomorphic(current_graph)
            if preexisting_iso == current_iso:
                # Both graphs have exactly the same content!
                return None
            in_both, in_first, in_second = graph_diff(preexisting_iso, current_iso)
            delete_string: Optional[str] = ProvSet.__get_delete_query(current_graph.identifier, in_first)
            insert_string: Optional[str] = ProvSet.__get_insert_query(current_graph.identifier, in_second)

            if delete_string is not None and insert_string is not None:
                return delete_string + ' ' + insert_string
            elif delete_string is not None:
                return delete_string
            elif insert_string is not None:
                return insert_string
            else:
                return None

    def _add_prov(self, graph_url: str, res: URIRef, short_name: str,
                  prov_subject: GraphEntity) -> Tuple[Graph, Optional[str], Optional[str]]:
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

        count = str(self.counter_handler.increment_counter(
            prov_subject.short_name, "se", int(get_count(prov_subject.res))))

        if self.wanted_label:
            cur_short_name = prov_subject.short_name
            cur_entity_count = get_count(prov_subject.res)
            cur_entity_prefix = get_prefix(prov_subject.res)

            related_to_label = "related to %s %s%s" % (self.labels[cur_short_name], cur_entity_prefix, cur_entity_count)
            related_to_short_label = "-> %s/%s%s" % (cur_short_name, cur_entity_prefix, cur_entity_count)

            label = "%s %s %s [%s/%s %s]" % (self.labels[short_name], count, related_to_label, short_name, count,
                                             related_to_short_label)

        return cur_g, count, label

    def _set_ns(self, g: Graph) -> None:
        super(ProvSet, self)._set_ns(g)
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
