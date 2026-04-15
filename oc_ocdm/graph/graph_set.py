# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
# SPDX-FileCopyrightText: 2023-2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING, cast

from rdflib import Graph
from sparqlite import SPARQLClient

from oc_ocdm.abstract_set import AbstractSet
from oc_ocdm.counter_handler.counter_handler import CounterHandler
from oc_ocdm.counter_handler.filesystem_counter_handler import FilesystemCounterHandler
from oc_ocdm.counter_handler.in_memory_counter_handler import InMemoryCounterHandler
from oc_ocdm.graph.entities.bibliographic.agent_role import AgentRole
from oc_ocdm.graph.entities.bibliographic.bibliographic_reference import BibliographicReference
from oc_ocdm.graph.entities.bibliographic.bibliographic_resource import BibliographicResource
from oc_ocdm.graph.entities.bibliographic.citation import Citation
from oc_ocdm.graph.entities.bibliographic.discourse_element import DiscourseElement
from oc_ocdm.graph.entities.bibliographic.pointer_list import PointerList
from oc_ocdm.graph.entities.bibliographic.reference_annotation import ReferenceAnnotation
from oc_ocdm.graph.entities.bibliographic.reference_pointer import ReferencePointer
from oc_ocdm.graph.entities.bibliographic.resource_embodiment import ResourceEmbodiment
from oc_ocdm.graph.entities.bibliographic.responsible_agent import ResponsibleAgent
from oc_ocdm.graph.entities.identifier import Identifier
from oc_ocdm.graph.graph_entity import GraphEntity
from triplelite import RDFTerm, TripleLite
from oc_ocdm.support.support import get_count, get_prefix, get_short_name

if TYPE_CHECKING:
    from typing import ClassVar, Dict, List, Optional, Set



class GraphSet(AbstractSet[GraphEntity]):
    # Labels
    labels: ClassVar[Dict[str, str]] = {
        "an": "annotation",
        "ar": "agent role",
        "be": "bibliographic entry",
        "br": "bibliographic resource",
        "ci": "citation",
        "de": "discourse element",
        "id": "identifier",
        "pl": "single location pointer list",
        "ra": "responsible agent",
        "re": "resource embodiment",
        "rp": "in-text reference pointer"
    }

    def __init__(self, base_iri: str, info_dir: str = "", supplier_prefix: str = "",
                 wanted_label: bool = True, custom_counter_handler: CounterHandler | None = None) -> None:
        super(GraphSet, self).__init__()
        # The following variable maps a URIRef with the related graph entity
        self.res_to_entity: Dict[str, GraphEntity] = {}
        self.base_iri: str = base_iri
        self.info_dir: str = info_dir
        self.supplier_prefix: str = supplier_prefix
        self.wanted_label: bool = wanted_label
        # Graphs
        # The following structure of URL is quite important for the other classes
        # developed and should not be changed. The only part that can change is the
        # value of the base_iri
        self.g_an: str = base_iri + "an/"
        self.g_ar: str = base_iri + "ar/"
        self.g_be: str = base_iri + "be/"
        self.g_br: str = base_iri + "br/"
        self.g_ci: str = base_iri + "ci/"
        self.g_de: str = base_iri + "de/"
        self.g_id: str = base_iri + "id/"
        self.g_pl: str = base_iri + "pl/"
        self.g_ra: str = base_iri + "ra/"
        self.g_re: str = base_iri + "re/"
        self.g_rp: str = base_iri + "rp/"

        if custom_counter_handler:
            self.counter_handler = custom_counter_handler
        elif info_dir is not None and info_dir != "":
            self.counter_handler = FilesystemCounterHandler(info_dir, supplier_prefix)
        else:
            self.counter_handler = InMemoryCounterHandler()

    def get_entity(self, res: str) -> Optional[GraphEntity]:
        if res in self.res_to_entity:
            return self.res_to_entity[res]

    # Add resources related to bibliographic entities
    def add_an(self, resp_agent: str | None, source: str | None = None, res: str | None = None,
               preexisting_graph: TripleLite | None = None) -> ReferenceAnnotation:
        if res is not None and get_short_name(res) != "an":
            raise ValueError(f"Given res: <{res}> is inappropriate for a ReferenceAnnotation entity.")
        if res is not None and res in self.res_to_entity:
            return cast(ReferenceAnnotation, self.res_to_entity[res])
        cur_g, count, label = self._add(self.g_an, "an", res)
        return ReferenceAnnotation(cur_g, self, GraphEntity.iri_note, res,
                                   resp_agent, source, count, label, "an",
                                   preexisting_graph)

    def add_ar(self, resp_agent: str | None, source: str | None = None, res: str | None = None,
               preexisting_graph: TripleLite | None = None) -> AgentRole:
        if res is not None and get_short_name(res) != "ar":
            raise ValueError(f"Given res: <{res}> is inappropriate for an AgentRole entity.")
        if res is not None and res in self.res_to_entity:
            return cast(AgentRole, self.res_to_entity[res])
        cur_g, count, label = self._add(self.g_ar, "ar", res)
        return AgentRole(cur_g, self, GraphEntity.iri_role_in_time, res,
                         resp_agent, source, count, label, "ar",
                         preexisting_graph)

    def add_be(self, resp_agent: str | None, source: str | None = None, res: str | None = None,
               preexisting_graph: TripleLite | None = None) -> BibliographicReference:
        if res is not None and get_short_name(res) != "be":
            raise ValueError(f"Given res: <{res}> is inappropriate for a BibliographicReference entity.")
        if res is not None and res in self.res_to_entity:
            return cast(BibliographicReference, self.res_to_entity[res])
        cur_g, count, label = self._add(self.g_be, "be", res)
        return BibliographicReference(cur_g, self, GraphEntity.iri_bibliographic_reference, res,
                                      resp_agent, source, count, label, "be",
                                      preexisting_graph)

    def add_br(self, resp_agent: str | None, source: str | None = None, res: str | None = None,
               preexisting_graph: TripleLite | None = None) -> BibliographicResource:
        if res is not None and get_short_name(res) != "br":
            raise ValueError(f"Given res: <{res}> is inappropriate for a BibliographicResource entity.")
        if res is not None and res in self.res_to_entity:
            return cast(BibliographicResource, self.res_to_entity[res])
        cur_g, count, label = self._add(self.g_br, "br", res)
        return BibliographicResource(cur_g, self, GraphEntity.iri_expression, res,
                                     resp_agent, source, count, label, "br",
                                     preexisting_graph)

    def add_ci(self, resp_agent: str | None, source: str | None = None, res: str | None = None,
               preexisting_graph: TripleLite | None = None) -> Citation:
        if res is not None and get_short_name(res) != "ci":
            raise ValueError(f"Given res: <{res}> is inappropriate for a Citation entity.")
        if res is not None and res in self.res_to_entity:
            return cast(Citation, self.res_to_entity[res])
        cur_g, count, label = self._add(self.g_ci, "ci", res)
        return Citation(cur_g, self, GraphEntity.iri_citation, res,
                        resp_agent, source, count, label, "ci",
                        preexisting_graph)

    def add_de(self, resp_agent: str | None, source: str | None = None, res: str | None = None,
               preexisting_graph: TripleLite | None = None) -> DiscourseElement:
        if res is not None and get_short_name(res) != "de":
            raise ValueError(f"Given res: <{res}> is inappropriate for a DiscourseElement entity.")
        if res is not None and res in self.res_to_entity:
            return cast(DiscourseElement, self.res_to_entity[res])
        cur_g, count, label = self._add(self.g_de, "de", res)
        return DiscourseElement(cur_g, self, GraphEntity.iri_discourse_element, res,
                                resp_agent, source, count, label, "de",
                                preexisting_graph)

    def add_id(self, resp_agent: str | None, source: str | None = None, res: str | None = None,
               preexisting_graph: TripleLite | None = None) -> Identifier:
        if res is not None and get_short_name(res) != "id":
            raise ValueError(f"Given res: <{res}> is inappropriate for an Identifier entity.")
        if res is not None and res in self.res_to_entity:
            return cast(Identifier, self.res_to_entity[res])
        cur_g, count, label = self._add(self.g_id, "id", res)
        return Identifier(cur_g, self, GraphEntity.iri_identifier, res,
                          resp_agent, source, count, label, "id",
                          preexisting_graph)

    def add_pl(self, resp_agent: str | None, source: str | None = None, res: str | None = None,
               preexisting_graph: TripleLite | None = None) -> PointerList:
        if res is not None and get_short_name(res) != "pl":
            raise ValueError(f"Given res: <{res}> is inappropriate for a PointerList entity.")
        if res is not None and res in self.res_to_entity:
            return cast(PointerList, self.res_to_entity[res])
        cur_g, count, label = self._add(self.g_pl, "pl", res)
        return PointerList(cur_g, self, GraphEntity.iri_singleloc_pointer_list, res,
                           resp_agent, source, count, label, "pl",
                           preexisting_graph)

    def add_rp(self, resp_agent: str | None, source: str | None = None, res: str | None = None,
               preexisting_graph: TripleLite | None = None) -> ReferencePointer:
        if res is not None and get_short_name(res) != "rp":
            raise ValueError(f"Given res: <{res}> is inappropriate for a ReferencePointer entity.")
        if res is not None and res in self.res_to_entity:
            return cast(ReferencePointer, self.res_to_entity[res])
        cur_g, count, label = self._add(self.g_rp, "rp", res)
        return ReferencePointer(cur_g, self, GraphEntity.iri_intextref_pointer, res,
                                resp_agent, source, count, label, "rp",
                                preexisting_graph)

    def add_ra(self, resp_agent: str | None, source: str | None = None, res: str | None = None,
               preexisting_graph: TripleLite | None = None) -> ResponsibleAgent:
        if res is not None and get_short_name(res) != "ra":
            raise ValueError(f"Given res: <{res}> is inappropriate for a ResponsibleAgent entity.")
        if res is not None and res in self.res_to_entity:
            return cast(ResponsibleAgent, self.res_to_entity[res])
        cur_g, count, label = self._add(self.g_ra, "ra", res)
        return ResponsibleAgent(cur_g, self, GraphEntity.iri_agent, res,
                                resp_agent, source, count, label, "ra",
                                preexisting_graph)

    def add_re(self, resp_agent: str | None, source: str | None = None, res: str | None = None,
               preexisting_graph: TripleLite | None = None) -> ResourceEmbodiment:
        if res is not None and get_short_name(res) != "re":
            raise ValueError(f"Given res: <{res}> is inappropriate for a ResourceEmbodiment entity.")
        if res is not None and res in self.res_to_entity:
            return cast(ResourceEmbodiment, self.res_to_entity[res])
        cur_g, count, label = self._add(self.g_re, "re", res)
        return ResourceEmbodiment(cur_g, self, GraphEntity.iri_manifestation, res,
                                  resp_agent, source, count, label, "re",
                                  preexisting_graph)

    def _add(self, graph_url: str, short_name: str, res: str | None = None) -> tuple[TripleLite, str | None, str | None]:
        cur_g = TripleLite(identifier=graph_url)

        count: Optional[str] = None
        label: Optional[str] = None
        supplier_prefix = get_prefix(res) if res is not None else self.supplier_prefix
        if res is not None:
            try:
                res_count: int = int(get_count(res))
            except ValueError:
                res_count: int = -1
            if res_count > self.counter_handler.read_counter(short_name, supplier_prefix=supplier_prefix):
                self.counter_handler.set_counter(res_count, short_name, supplier_prefix=supplier_prefix)
            return cur_g, count, label

        count = supplier_prefix + str(self.counter_handler.increment_counter(short_name, supplier_prefix=supplier_prefix))

        if self.wanted_label:
            label = "%s %s [%s/%s]" % (self.labels[short_name], count, short_name, count)

        return cur_g, count, label

    def get_orphans(self) -> List[GraphEntity]:
        full_set_of_entities: Set[str] = set(self.res_to_entity.keys())
        referenced_entities: Set[str] = set()
        for res, entity in self.res_to_entity.items():
            for obj in entity.g.objects(subject=res, predicate=None):
                if obj.type == "uri":
                    referenced_entities.add(obj.value)
        set_of_orphan_res: Set[str] = full_set_of_entities - referenced_entities

        result_list: List[GraphEntity] = []
        for orphan_res in set_of_orphan_res:
            entity: Optional[GraphEntity] = self.get_entity(orphan_res)
            if entity is not None:
                result_list.append(entity)

        return result_list

    def remove_orphans_from_triplestore(self, ts_url: str, resp_agent: str) -> None:
        with SPARQLClient(ts_url) as client:
            for entity_res, entity in self.res_to_entity.items():
                if entity.to_be_deleted:
                    query: str = f"CONSTRUCT {{?s ?p ?o}} WHERE {{?s ?p ?o ; ?p_1 <{entity_res}>}}"
                    nt_bytes = client.construct(query)
                    if nt_bytes:
                        from oc_ocdm.reader import Reader
                        result: Graph = Graph()
                        result.parse(BytesIO(nt_bytes), format='nt')
                        imported_entities: List[GraphEntity] = Reader.import_entities_from_graph(self, result, resp_agent)
                        for imported_entity in imported_entities:
                            imported_entity.g.remove((imported_entity.res, None, RDFTerm("uri", str(entity_res))))

    def commit_changes(self):
        for res, entity in self.res_to_entity.items():
            entity.commit_changes()
            if entity.to_be_deleted:
                del self.res_to_entity[res]

    def get_an(self) -> tuple[ReferenceAnnotation, ...]:
        return tuple(entity for entity in self.res_to_entity.values() if isinstance(entity, ReferenceAnnotation))

    def get_ar(self) -> tuple[AgentRole, ...]:
        return tuple(entity for entity in self.res_to_entity.values() if isinstance(entity, AgentRole))

    def get_be(self) -> tuple[BibliographicReference, ...]:
        return tuple(entity for entity in self.res_to_entity.values() if isinstance(entity, BibliographicReference))

    def get_br(self) -> tuple[BibliographicResource, ...]:
        return tuple(entity for entity in self.res_to_entity.values() if isinstance(entity, BibliographicResource))

    def get_ci(self) -> tuple[Citation, ...]:
        return tuple(entity for entity in self.res_to_entity.values() if isinstance(entity, Citation))

    def get_de(self) -> tuple[DiscourseElement, ...]:
        return tuple(entity for entity in self.res_to_entity.values() if isinstance(entity, DiscourseElement))

    def get_id(self) -> tuple[Identifier, ...]:
        return tuple(entity for entity in self.res_to_entity.values() if isinstance(entity, Identifier))

    def get_pl(self) -> tuple[PointerList, ...]:
        return tuple(entity for entity in self.res_to_entity.values() if isinstance(entity, PointerList))

    def get_rp(self) -> tuple[ReferencePointer, ...]:
        return tuple(entity for entity in self.res_to_entity.values() if isinstance(entity, ReferencePointer))

    def get_ra(self) -> tuple[ResponsibleAgent, ...]:
        return tuple(entity for entity in self.res_to_entity.values() if isinstance(entity, ResponsibleAgent))

    def get_re(self) -> tuple[ResourceEmbodiment, ...]:
        return tuple(entity for entity in self.res_to_entity.values() if isinstance(entity, ResourceEmbodiment))
