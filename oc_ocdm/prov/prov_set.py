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

from datetime import datetime
from typing import TYPE_CHECKING, Dict, ClassVar

from oc_ocdm.abstract_set import AbstractSet
from oc_ocdm.prov.entities.entity_snapshot import EntitySnapshot
from oc_ocdm.support.query_utils import get_update_query

if TYPE_CHECKING:
    from typing import Optional, Tuple, List
    from oc_ocdm.graph.graph_entity import GraphEntity

from rdflib import Graph, URIRef

from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.prov.prov_entity import ProvEntity
from oc_ocdm.counter_handler.counter_handler import CounterHandler
from oc_ocdm.counter_handler.filesystem_counter_handler import FilesystemCounterHandler
from oc_ocdm.counter_handler.in_memory_counter_handler import InMemoryCounterHandler
from oc_ocdm.support.support import get_short_name, get_count, get_prefix


class ProvSet(AbstractSet):
    # Labels
    labels: ClassVar[Dict[str, str]] = {
        "se": "snapshot of entity metadata"
    }

    def __init__(self, prov_subj_graph_set: GraphSet, base_iri: str, info_dir: str = "",
                 supplier_prefix: str = "", wanted_label: bool = True) -> None:
        super(ProvSet, self).__init__()
        self.prov_g: GraphSet = prov_subj_graph_set
        # The following variable maps a URIRef with the related provenance entity
        self.res_to_entity: Dict[URIRef, ProvEntity] = {}
        self.base_iri: str = base_iri
        self.supplier_prefix: str = supplier_prefix
        self.wanted_label: bool = wanted_label

        if info_dir is not None and info_dir != "":
            self.counter_handler: CounterHandler = FilesystemCounterHandler(info_dir)
        else:
            self.counter_handler: CounterHandler = InMemoryCounterHandler()

    def get_entity(self, res: URIRef) -> Optional[ProvEntity]:
        if res in self.res_to_entity:
            return self.res_to_entity[res]

    def add_se(self, prov_subject: GraphEntity, res: URIRef = None) -> EntitySnapshot:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        g_prov: str = str(prov_subject) + "/prov/"
        cur_g, count, label = self._add_prov(g_prov, res, "se", prov_subject)
        return EntitySnapshot(prov_subject, cur_g, self, res, prov_subject.resp_agent,
                              prov_subject.source_agent, prov_subject.source,
                              ProvEntity.iri_entity, count, label, "se")

    def _create_snapshot(self, cur_subj: GraphEntity, cur_time: str) -> EntitySnapshot:
        new_snapshot: EntitySnapshot = self.add_se(prov_subject=cur_subj)
        new_snapshot.is_snapshot_of(cur_subj)
        new_snapshot.has_generation_time(cur_time)
        if cur_subj.source is not None:
            new_snapshot.has_primary_source(URIRef(cur_subj.source))
        if cur_subj.resp_agent is not None:
            new_snapshot.has_resp_agent(URIRef(cur_subj.resp_agent))
        return new_snapshot

    def _get_snapshots_from_merge_list(self, cur_subj: GraphEntity) -> List[EntitySnapshot]:
        snapshots_list: List[EntitySnapshot] = []
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
            if cur_subj is None or (not cur_subj.was_merged or cur_subj.to_be_deleted):
                # Here we must skip every entity that was not merged or that must be deleted.
                continue

            # Previous snapshot
            last_snapshot_res: Optional[URIRef] = self._retrieve_last_snapshot(cur_subj.res)
            if last_snapshot_res is None:
                # CREATION SNAPSHOT
                cur_snapshot: EntitySnapshot = self._create_snapshot(cur_subj, cur_time)
                cur_snapshot.has_description(f"The entity '{cur_subj.res}' has been created.")
            else:
                update_query: str = get_update_query(cur_subj, entity_type="graph")[0]
                was_modified: bool = (update_query != "")
                snapshots_list: List[ProvEntity] = self._get_snapshots_from_merge_list(cur_subj)

                if was_modified and len(snapshots_list) <= 0:
                    # MODIFICATION SNAPSHOT
                    last_snapshot: EntitySnapshot = self.add_se(prov_subject=cur_subj, res=last_snapshot_res)
                    last_snapshot.has_invalidation_time(cur_time)

                    cur_snapshot: EntitySnapshot = self._create_snapshot(cur_subj, cur_time)
                    cur_snapshot.derives_from(last_snapshot)
                    cur_snapshot.has_update_action(update_query)
                    cur_snapshot.has_description(f"The entity '{cur_subj.res}' has been modified.")
                elif len(snapshots_list) > 0:
                    # MERGE SNAPSHOT
                    last_snapshot: EntitySnapshot = self.add_se(prov_subject=cur_subj, res=last_snapshot_res)
                    last_snapshot.has_invalidation_time(cur_time)

                    cur_snapshot: EntitySnapshot = self._create_snapshot(cur_subj, cur_time)
                    cur_snapshot.derives_from(last_snapshot)
                    for snapshot in snapshots_list:
                        cur_snapshot.derives_from(snapshot)
                    cur_snapshot.has_description(self._get_merge_description(cur_subj, snapshots_list))

        # EVERY OTHER ENTITY
        for cur_subj in self.prov_g.res_to_entity.values():
            if cur_subj is None or (cur_subj.was_merged and not cur_subj.to_be_deleted):
                # Here we must skip every entity which was merged while not being marked as to be deleted,
                # since we already processed those entities in the previous loop.
                continue

            last_snapshot_res: Optional[URIRef] = self._retrieve_last_snapshot(cur_subj.res)
            if last_snapshot_res is None:
                if cur_subj.to_be_deleted:
                    # We can ignore this entity because it was deleted even before being created.
                    pass
                else:
                    # CREATION SNAPSHOT
                    cur_snapshot: EntitySnapshot = self._create_snapshot(cur_subj, cur_time)
                    cur_snapshot.has_description(f"The entity '{cur_subj.res}' has been created.")
            else:
                update_query: str = get_update_query(cur_subj, entity_type="graph")[0]
                was_modified: bool = (update_query != "")

                if cur_subj.to_be_deleted:
                    # DELETION SNAPSHOT
                    last_snapshot: EntitySnapshot = self.add_se(prov_subject=cur_subj, res=last_snapshot_res)
                    last_snapshot.has_invalidation_time(cur_time)

                    cur_snapshot: EntitySnapshot = self._create_snapshot(cur_subj, cur_time)
                    cur_snapshot.derives_from(last_snapshot)
                    cur_snapshot.has_invalidation_time(cur_time)
                    cur_snapshot.has_description(f"The entity '{cur_subj.res}' has been deleted.")
                    cur_snapshot.has_update_action(update_query)
                elif was_modified:
                    # MODIFICATION SNAPSHOT
                    last_snapshot: EntitySnapshot = self.add_se(prov_subject=cur_subj, res=last_snapshot_res)
                    last_snapshot.has_invalidation_time(cur_time)

                    cur_snapshot: EntitySnapshot = self._create_snapshot(cur_subj, cur_time)
                    cur_snapshot.derives_from(last_snapshot)
                    cur_snapshot.has_description(f"The entity '{cur_subj.res}' has been modified.")
                    cur_snapshot.has_update_action(update_query)

    def _add_prov(self, graph_url: str, res: URIRef, short_name: str,
                  prov_subject: GraphEntity) -> Tuple[Graph, Optional[str], Optional[str]]:
        cur_g: Graph = Graph(identifier=graph_url)
        self._set_ns(cur_g)

        count: Optional[str] = None
        label: Optional[str] = None

        if res is not None:
            try:
                res_count: int = int(get_count(res))
            except ValueError:
                res_count: int = -1
            if res_count > self.counter_handler.read_counter(prov_subject.short_name, "se",
                                                             int(get_count(prov_subject.res))):
                self.counter_handler.set_counter(res_count, prov_subject.short_name, "se",
                                                 int(get_count(prov_subject.res)))
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

    @staticmethod
    def _set_ns(g: Graph) -> None:
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

    def get_se(self) -> Tuple[EntitySnapshot]:
        result: Tuple[EntitySnapshot] = tuple()
        for ref in self.res_to_entity:
            entity: ProvEntity = self.res_to_entity[ref]
            if isinstance(entity, EntitySnapshot):
                result += (entity, )
        return result
