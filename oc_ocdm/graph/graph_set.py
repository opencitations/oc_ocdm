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

from typing import TYPE_CHECKING

from oc_ocdm.reader import import_entities_from_graph
from oc_ocdm.abstract_set import AbstractSet

if TYPE_CHECKING:
    from typing import Dict, ClassVar, Tuple, Optional, List
    from rdflib.query import Result

from rdflib import Graph, Namespace, URIRef, ConjunctiveGraph

from oc_ocdm.graph import GraphEntity
from oc_ocdm.counter_handler import CounterHandler
from oc_ocdm.graph.entities import Identifier
from oc_ocdm.graph.entities.bibliographic import AgentRole
from oc_ocdm.graph.entities.bibliographic import BibliographicReference
from oc_ocdm.graph.entities.bibliographic import BibliographicResource
from oc_ocdm.graph.entities.bibliographic import Citation
from oc_ocdm.graph.entities.bibliographic import DiscourseElement
from oc_ocdm.graph.entities.bibliographic import PointerList
from oc_ocdm.graph.entities.bibliographic import ReferenceAnnotation
from oc_ocdm.graph.entities.bibliographic import ReferencePointer
from oc_ocdm.graph.entities.bibliographic import ResourceEmbodiment
from oc_ocdm.graph.entities.bibliographic import ResponsibleAgent


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

    def __init__(self, base_iri: str, counter_handler: CounterHandler, supplier_prefix: str = "",
                 wanted_label: bool = True) -> None:
        super(GraphSet, self).__init__()
        # The following variable maps a URIRef with the related graph entity
        self.res_to_entity: Dict[URIRef, GraphEntity] = {}
        self.base_iri: str = base_iri
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

        self.counter_handler: CounterHandler = counter_handler

    def get_entity(self, res: URIRef) -> Optional[GraphEntity]:
        if res in self.res_to_entity:
            return self.res_to_entity[res]

    # Add resources related to bibliographic entities
    def add_an(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None, preexisting_graph: Graph = None) -> ReferenceAnnotation:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(graph_url=self.g_an, res=res, short_name="an")
        return ReferenceAnnotation(cur_g, res=res, res_type=GraphEntity.iri_note, short_name="an", resp_agent=resp_agent,
                                   source_agent=source_agent, source=source, count=count,
                                   label=label, g_set=self, preexisting_graph=preexisting_graph)

    def add_ar(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None, preexisting_graph: Graph = None) -> AgentRole:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(graph_url=self.g_ar, res=res, short_name="ar")
        return AgentRole(cur_g, res=res, res_type=GraphEntity.iri_role_in_time, short_name="ar", resp_agent=resp_agent,
                         source_agent=source_agent, source=source, count=count,
                         label=label, g_set=self, preexisting_graph=preexisting_graph)

    def add_be(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None, preexisting_graph: Graph = None) -> BibliographicReference:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(graph_url=self.g_be, res=res, short_name="be")
        return BibliographicReference(cur_g, res=res, res_type=GraphEntity.iri_bibliographic_reference, short_name="be",
                                      resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                                      label=label, g_set=self, preexisting_graph=preexisting_graph)

    def add_br(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None, preexisting_graph: Graph = None) -> BibliographicResource:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(graph_url=self.g_br, res=res, short_name="br")
        return BibliographicResource(cur_g, res=res, res_type=GraphEntity.iri_expression, short_name="br",
                                     resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                                     label=label, g_set=self, preexisting_graph=preexisting_graph)

    def add_ci(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None, preexisting_graph: Graph = None) -> Citation:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(graph_url=self.g_ci, res=res, short_name="ci")
        return Citation(cur_g, res=res, res_type=GraphEntity.iri_citation, short_name="ci",
                        resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                        label=label, g_set=self, preexisting_graph=preexisting_graph)

    def add_de(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None, preexisting_graph: Graph = None) -> DiscourseElement:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(graph_url=self.g_de, res=res, short_name="de")
        return DiscourseElement(cur_g, res=res, res_type=GraphEntity.iri_discourse_element, short_name="de",
                                resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                                label=label, g_set=self, preexisting_graph=preexisting_graph)

    def add_id(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None, preexisting_graph: Graph = None) -> Identifier:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(graph_url=self.g_id, res=res, short_name="id")
        return Identifier(cur_g, res=res, res_type=GraphEntity.iri_identifier, short_name="id",
                          resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                          label=label, g_set=self, preexisting_graph=preexisting_graph)

    def add_pl(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None, preexisting_graph: Graph = None) -> PointerList:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(graph_url=self.g_pl, res=res, short_name="pl")
        return PointerList(cur_g, res=res, res_type=GraphEntity.iri_singleloc_pointer_list, short_name="pl",
                           resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                           label=label, g_set=self, preexisting_graph=preexisting_graph)

    def add_rp(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None, preexisting_graph: Graph = None) -> ReferencePointer:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(graph_url=self.g_rp, res=res, short_name="rp")
        return ReferencePointer(cur_g, res=res, res_type=GraphEntity.iri_intextref_pointer, short_name="rp",
                                resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                                label=label, g_set=self, preexisting_graph=preexisting_graph)

    def add_ra(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None, preexisting_graph: Graph = None) -> ResponsibleAgent:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(graph_url=self.g_ra, res=res, short_name="ra")
        return ResponsibleAgent(cur_g, res=res, res_type=GraphEntity.iri_agent, short_name="ra",
                                resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                                label=label, g_set=self, preexisting_graph=preexisting_graph)

    def add_re(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None, preexisting_graph: Graph = None) -> ResourceEmbodiment:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add(graph_url=self.g_re, res=res, short_name="re")
        return ResourceEmbodiment(cur_g, res=res, res_type=GraphEntity.iri_manifestation, short_name="re",
                                  resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                                  label=label, g_set=self, preexisting_graph=preexisting_graph)

    def _add(self, graph_url: str, res: URIRef, short_name: str) -> Tuple[Graph, Optional[str], Optional[str]]:
        cur_g: Graph = Graph(identifier=graph_url)
        self._set_ns(cur_g)

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
        count = self.supplier_prefix + str(self.counter_handler.increment_counter(short_name))

        if self.wanted_label:
            label = "%s %s [%s/%s]" % (self.labels[short_name], count, short_name, count)

        return cur_g, count, label

    def sync_with_triplestore(self, ts_url: str) -> None:
        ts: ConjunctiveGraph = ConjunctiveGraph()
        ts.open((ts_url, ts_url))
        for entity_res, entity in self.res_to_entity.items():
            if entity.to_be_deleted:
                query: str = f"CONSTRUCT {{?s ?p ?o}} WHERE {{?s ?p ?o ; ?p_1 <{entity_res}>}}"
                result: Result = ts.query(query)
                if result is not None:
                    imported_entities: List[GraphEntity] = import_entities_from_graph(self, result.graph)
                    for imported_entity in imported_entities:
                        imported_entity.g.remove((imported_entity.res, None, entity_res))
        ts.close()

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