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

from typing import TYPE_CHECKING

from SPARQLWrapper import RDFXML, SPARQLWrapper

from oc_ocdm.abstract_set import AbstractSet
from oc_ocdm.reader import Reader
from oc_ocdm.support.support import get_count, get_short_name, get_prefix

if TYPE_CHECKING:
    from typing import Dict, ClassVar, Tuple, Optional, List, Set
    from rdflib import ConjunctiveGraph

from rdflib import Graph, Namespace, URIRef

from oc_ocdm.counter_handler.counter_handler import CounterHandler
from oc_ocdm.counter_handler.filesystem_counter_handler import \
    FilesystemCounterHandler
from oc_ocdm.counter_handler.in_memory_counter_handler import \
    InMemoryCounterHandler
from oc_ocdm.graph.entities.bibliographic.agent_role import AgentRole
from oc_ocdm.graph.entities.bibliographic.bibliographic_reference import \
    BibliographicReference
from oc_ocdm.graph.entities.bibliographic.bibliographic_resource import \
    BibliographicResource
from oc_ocdm.graph.entities.bibliographic.citation import Citation
from oc_ocdm.graph.entities.bibliographic.discourse_element import \
    DiscourseElement
from oc_ocdm.graph.entities.bibliographic.pointer_list import PointerList
from oc_ocdm.graph.entities.bibliographic.reference_annotation import \
    ReferenceAnnotation
from oc_ocdm.graph.entities.bibliographic.reference_pointer import \
    ReferencePointer
from oc_ocdm.graph.entities.bibliographic.resource_embodiment import \
    ResourceEmbodiment
from oc_ocdm.graph.entities.bibliographic.responsible_agent import \
    ResponsibleAgent
from oc_ocdm.graph.entities.identifier import Identifier
from oc_ocdm.graph.graph_entity import GraphEntity


class GraphSet(AbstractSet):
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
                 wanted_label: bool = True) -> None:
        super(GraphSet, self).__init__()
        # The following variable maps a URIRef with the related graph entity
        self.res_to_entity: Dict[URIRef, GraphEntity] = {}
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

        if info_dir is not None and info_dir != "":
            self.counter_handler: CounterHandler = FilesystemCounterHandler(info_dir, supplier_prefix)
        else:
            self.counter_handler: CounterHandler = InMemoryCounterHandler()

    def get_entity(self, res: URIRef) -> Optional[GraphEntity]:
        if res in self.res_to_entity:
            return self.res_to_entity[res]

    # Add resources related to bibliographic entities
    def add_an(self, resp_agent: str, source: str = None, res: URIRef = None,
               preexisting_graph: Graph = None) -> ReferenceAnnotation:
        if res is not None and get_short_name(res) != "an":
            raise ValueError(f"Given res: <{res}> is inappropriate for a ReferenceAnnotation entity.")
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(self.g_an, "an", res)
        return ReferenceAnnotation(cur_g, self, res, GraphEntity.iri_note,
                                   resp_agent, source, count, label, "an",
                                   preexisting_graph)

    def add_ar(self, resp_agent: str, source: str = None, res: URIRef = None,
               preexisting_graph: Graph = None) -> AgentRole:
        if res is not None and get_short_name(res) != "ar":
            raise ValueError(f"Given res: <{res}> is inappropriate for an AgentRole entity.")
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(self.g_ar, "ar", res)
        return AgentRole(cur_g, self, res, GraphEntity.iri_role_in_time,
                         resp_agent, source, count, label, "ar",
                         preexisting_graph)

    def add_be(self, resp_agent: str, source: str = None, res: URIRef = None,
               preexisting_graph: Graph = None) -> BibliographicReference:
        if res is not None and get_short_name(res) != "be":
            raise ValueError(f"Given res: <{res}> is inappropriate for a BibliographicReference entity.")
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(self.g_be, "be", res)
        return BibliographicReference(cur_g, self, res, GraphEntity.iri_bibliographic_reference,
                                      resp_agent, source, count, label, "be",
                                      preexisting_graph)

    def add_br(self, resp_agent: str, source: str = None, res: URIRef = None,
               preexisting_graph: Graph = None) -> BibliographicResource:
        if res is not None and get_short_name(res) != "br":
            raise ValueError(f"Given res: <{res}> is inappropriate for a BibliographicResource entity.")
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(self.g_br, "br", res)
        return BibliographicResource(cur_g, self, res, GraphEntity.iri_expression,
                                     resp_agent, source, count, label, "br",
                                     preexisting_graph)

    def add_ci(self, resp_agent: str, source: str = None, res: URIRef = None,
               preexisting_graph: Graph = None) -> Citation:
        if res is not None and get_short_name(res) != "ci":
            raise ValueError(f"Given res: <{res}> is inappropriate for a Citation entity.")
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(self.g_ci, "ci", res)
        return Citation(cur_g, self, res, GraphEntity.iri_citation,
                        resp_agent, source, count, label, "ci",
                        preexisting_graph)

    def add_de(self, resp_agent: str, source: str = None, res: URIRef = None,
               preexisting_graph: Graph = None) -> DiscourseElement:
        if res is not None and get_short_name(res) != "de":
            raise ValueError(f"Given res: <{res}> is inappropriate for a DiscourseElement entity.")
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(self.g_de, "de", res)
        return DiscourseElement(cur_g, self, res, GraphEntity.iri_discourse_element,
                                resp_agent, source, count, label, "de",
                                preexisting_graph)

    def add_id(self, resp_agent: str, source: str = None, res: URIRef = None,
               preexisting_graph: Graph = None) -> Identifier:
        if res is not None and get_short_name(res) != "id":
            raise ValueError(f"Given res: <{res}> is inappropriate for an Identifier entity.")
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(self.g_id, "id", res)
        return Identifier(cur_g, self, res, GraphEntity.iri_identifier,
                          resp_agent, source, count, label, "id",
                          preexisting_graph)

    def add_pl(self, resp_agent: str, source: str = None, res: URIRef = None,
               preexisting_graph: Graph = None) -> PointerList:
        if res is not None and get_short_name(res) != "pl":
            raise ValueError(f"Given res: <{res}> is inappropriate for a PointerList entity.")
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(self.g_pl, "pl", res)
        return PointerList(cur_g, self, res, GraphEntity.iri_singleloc_pointer_list,
                           resp_agent, source, count, label, "pl",
                           preexisting_graph)

    def add_rp(self, resp_agent: str, source: str = None, res: URIRef = None,
               preexisting_graph: Graph = None) -> ReferencePointer:
        if res is not None and get_short_name(res) != "rp":
            raise ValueError(f"Given res: <{res}> is inappropriate for a ReferencePointer entity.")
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(self.g_rp, "rp", res)
        return ReferencePointer(cur_g, self, res, GraphEntity.iri_intextref_pointer,
                                resp_agent, source, count, label, "rp",
                                preexisting_graph)

    def add_ra(self, resp_agent: str, source: str = None, res: URIRef = None,
               preexisting_graph: Graph = None) -> ResponsibleAgent:
        if res is not None and get_short_name(res) != "ra":
            raise ValueError(f"Given res: <{res}> is inappropriate for a ResponsibleAgent entity.")
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(self.g_ra, "ra", res)
        return ResponsibleAgent(cur_g, self, res, GraphEntity.iri_agent,
                                resp_agent, source, count, label, "ra",
                                preexisting_graph)

    def add_re(self, resp_agent: str, source: str = None, res: URIRef = None,
               preexisting_graph: Graph = None) -> ResourceEmbodiment:
        if res is not None and get_short_name(res) != "re":
            raise ValueError(f"Given res: <{res}> is inappropriate for a ResourceEmbodiment entity.")
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(self.g_re, "re", res)
        return ResourceEmbodiment(cur_g, self, res, GraphEntity.iri_manifestation,
                                  resp_agent, source, count, label, "re",
                                  preexisting_graph)

    def _add(self, graph_url: str, short_name: str, res: URIRef = None) -> Tuple[Graph, Optional[str], Optional[str]]:
        cur_g: Graph = Graph(identifier=graph_url)
        self._set_ns(cur_g)

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
        full_set_of_entities: Set[URIRef] = set(self.res_to_entity.keys())
        referenced_entities: Set[URIRef] = set()
        for res, entity in self.res_to_entity.items():
            for obj in entity.g.objects(subject=res, predicate=None):
                if type(obj) == URIRef:
                    referenced_entities.add(obj)
        set_of_orphan_res: Set[URIRef] = full_set_of_entities - referenced_entities

        result_list: List[GraphEntity] = []
        for orphan_res in set_of_orphan_res:
            entity: Optional[GraphEntity] = self.get_entity(orphan_res)
            if entity is not None:
                result_list.append(entity)

        return result_list

    def remove_orphans_from_triplestore(self, ts_url: str, resp_agent: str) -> None:
        sparql: SPARQLWrapper = SPARQLWrapper(ts_url)

        for entity_res, entity in self.res_to_entity.items():
            if entity.to_be_deleted:
                query: str = f"CONSTRUCT {{?s ?p ?o}} WHERE {{?s ?p ?o ; ?p_1 <{entity_res}>}}"
                sparql.setQuery(query)
                sparql.setMethod('GET')
                sparql.setReturnFormat(RDFXML)

                result: ConjunctiveGraph = sparql.query().convert()
                if result is not None:
                    imported_entities: List[GraphEntity] = Reader.import_entities_from_graph(self, result, resp_agent)
                    for imported_entity in imported_entities:
                        imported_entity.g.remove((imported_entity.res, None, entity_res))

    def commit_changes(self):
        for res, entity in self.res_to_entity.items():
            entity.commit_changes()
            if entity.to_be_deleted:
                del self.res_to_entity[res]

    def _set_ns(self, g: Graph) -> None:
        g.namespace_manager.bind("an", Namespace(self.g_an))
        g.namespace_manager.bind("ar", Namespace(self.g_ar))
        g.namespace_manager.bind("be", Namespace(self.g_be))
        g.namespace_manager.bind("ci", Namespace(self.g_ci))
        g.namespace_manager.bind("de", Namespace(self.g_de))
        g.namespace_manager.bind("br", Namespace(self.g_br))
        g.namespace_manager.bind("id", Namespace(self.g_id))
        g.namespace_manager.bind("pl", Namespace(self.g_pl))
        g.namespace_manager.bind("ra", Namespace(self.g_ra))
        g.namespace_manager.bind("re", Namespace(self.g_re))
        g.namespace_manager.bind("rp", Namespace(self.g_rp))
        g.namespace_manager.bind("biro", GraphEntity.BIRO)
        g.namespace_manager.bind("co", GraphEntity.CO)
        g.namespace_manager.bind("c4o", GraphEntity.C4O)
        g.namespace_manager.bind("cito", GraphEntity.CITO)
        g.namespace_manager.bind("datacite", GraphEntity.DATACITE)
        g.namespace_manager.bind("dcterms", GraphEntity.DCTERMS)
        g.namespace_manager.bind("deo", GraphEntity.DEO)
        g.namespace_manager.bind("doco", GraphEntity.DOCO)
        g.namespace_manager.bind("fabio", GraphEntity.FABIO)
        g.namespace_manager.bind("foaf", GraphEntity.FOAF)
        g.namespace_manager.bind("frbr", GraphEntity.FRBR)
        g.namespace_manager.bind("literal", GraphEntity.LITERAL)
        g.namespace_manager.bind("oa", GraphEntity.OA)
        g.namespace_manager.bind("oco", GraphEntity.OCO)
        g.namespace_manager.bind("prism", GraphEntity.PRISM)
        g.namespace_manager.bind("pro", GraphEntity.PRO)

    def get_an(self) -> Tuple[ReferenceAnnotation]:
        result: Tuple[ReferenceAnnotation] = tuple()
        for ref in self.res_to_entity:
            entity: GraphEntity = self.res_to_entity[ref]
            if isinstance(entity, ReferenceAnnotation):
                result += (entity, )
        return result

    def get_ar(self) -> Tuple[AgentRole]:
        result: Tuple[AgentRole] = tuple()
        for ref in self.res_to_entity:
            entity: GraphEntity = self.res_to_entity[ref]
            if isinstance(entity, AgentRole):
                result += (entity, )
        return result

    def get_be(self) -> Tuple[BibliographicReference]:
        result: Tuple[BibliographicReference] = tuple()
        for ref in self.res_to_entity:
            entity: GraphEntity = self.res_to_entity[ref]
            if isinstance(entity, BibliographicReference):
                result += (entity, )
        return result

    def get_br(self) -> Tuple[BibliographicResource]:
        result: Tuple[BibliographicResource] = tuple()
        for ref in self.res_to_entity:
            entity: GraphEntity = self.res_to_entity[ref]
            if isinstance(entity, BibliographicResource):
                result += (entity, )
        return result

    def get_ci(self) -> Tuple[Citation]:
        result: Tuple[Citation] = tuple()
        for ref in self.res_to_entity:
            entity: GraphEntity = self.res_to_entity[ref]
            if isinstance(entity, Citation):
                result += (entity, )
        return result

    def get_de(self) -> Tuple[DiscourseElement]:
        result: Tuple[DiscourseElement] = tuple()
        for ref in self.res_to_entity:
            entity: GraphEntity = self.res_to_entity[ref]
            if isinstance(entity, DiscourseElement):
                result += (entity, )
        return result

    def get_id(self) -> Tuple[Identifier]:
        result: Tuple[Identifier] = tuple()
        for ref in self.res_to_entity:
            entity: GraphEntity = self.res_to_entity[ref]
            if isinstance(entity, Identifier):
                result += (entity, )
        return result

    def get_pl(self) -> Tuple[PointerList]:
        result: Tuple[PointerList] = tuple()
        for ref in self.res_to_entity:
            entity: GraphEntity = self.res_to_entity[ref]
            if isinstance(entity, PointerList):
                result += (entity, )
        return result

    def get_rp(self) -> Tuple[ReferencePointer]:
        result: Tuple[ReferencePointer] = tuple()
        for ref in self.res_to_entity:
            entity: GraphEntity = self.res_to_entity[ref]
            if isinstance(entity, ReferencePointer):
                result += (entity, )
        return result

    def get_ra(self) -> Tuple[ResponsibleAgent]:
        result: Tuple[ResponsibleAgent] = tuple()
        for ref in self.res_to_entity:
            entity: GraphEntity = self.res_to_entity[ref]
            if isinstance(entity, ResponsibleAgent):
                result += (entity, )
        return result

    def get_re(self) -> Tuple[ResourceEmbodiment]:
        result: Tuple[ResourceEmbodiment] = tuple()
        for ref in self.res_to_entity:
            entity: GraphEntity = self.res_to_entity[ref]
            if isinstance(entity, ResourceEmbodiment):
                result += (entity, )
        return result
