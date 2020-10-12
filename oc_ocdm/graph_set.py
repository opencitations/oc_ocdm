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

from typing import Dict, List, ClassVar, Tuple, Optional

from rdflib import Graph, Namespace, URIRef

from oc_ocdm import GraphEntity
from oc_ocdm.counter_handler import CounterHandler
from oc_ocdm.entities import Identifier
from oc_ocdm.entities.bibliographic import AgentRole
from oc_ocdm.entities.bibliographic import BibliographicReference
from oc_ocdm.entities.bibliographic import BibliographicResource
from oc_ocdm.entities.bibliographic import Citation
from oc_ocdm.entities.bibliographic import DiscourseElement
from oc_ocdm.entities.bibliographic import PointerList
from oc_ocdm.entities.bibliographic import ReferenceAnnotation
from oc_ocdm.entities.bibliographic import ReferencePointer
from oc_ocdm.entities.bibliographic import ResourceEmbodiment
from oc_ocdm.entities.bibliographic import ResponsibleAgent


class GraphSet(object):
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

    def __init__(self, base_iri: str, context_path: str, counter_handler: CounterHandler,
                 supplier_prefix: str = "", forced_type: bool = False, wanted_label: bool = True) -> None:
        # A list of rdflib.Graphs, one for subject entity
        self.g: List[Graph] = []
        # The following variable maps a URIRef with the graph in the graph list related to them
        self.entity_g: Dict[URIRef, Graph] = {}
        # The following variable maps a URIRef with the related graph entity
        self.res_to_entity: Dict[URIRef, GraphEntity] = {}
        self.base_iri: str = base_iri
        self.context_path: str = context_path
        self.cur_name: str = "OCDM " + self.__class__.__name__
        self.supplier_prefix: str = supplier_prefix
        self.wanted_label: bool = wanted_label
        self.forced_type: bool = forced_type
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

    def get_entity(self, res: URIRef) -> GraphEntity:
        if res in self.res_to_entity:
            return self.res_to_entity[res]

    # Add resources related to bibliographic entities
    def add_an(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None) -> ReferenceAnnotation:
        cur_g, count, label = self._add(graph_url=self.g_an, res=res, short_name="an")
        return ReferenceAnnotation(cur_g, res=res, res_type=GraphEntity.note, short_name="an", resp_agent=resp_agent,
                                   source_agent=source_agent, source=source, count=count,
                                   label=label, g_set=self, forced_type=self.forced_type)

    def add_ar(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None) -> AgentRole:
        cur_g, count, label = self._add(graph_url=self.g_ar, res=res, short_name="ar")
        return AgentRole(cur_g, res=res, res_type=GraphEntity.role_in_time, short_name="ar", resp_agent=resp_agent,
                         source_agent=source_agent, source=source, count=count,
                         label=label, g_set=self, forced_type=self.forced_type)

    def add_be(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None) -> BibliographicReference:
        cur_g, count, label = self._add(graph_url=self.g_be, res=res, short_name="be")
        return BibliographicReference(cur_g, res=res, res_type=GraphEntity.bibliographic_reference, short_name="be",
                                      resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                                      label=label, g_set=self, forced_type=self.forced_type)

    def add_br(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None) -> BibliographicResource:
        cur_g, count, label = self._add(graph_url=self.g_br, res=res, short_name="br")
        return BibliographicResource(cur_g, res=res, res_type=GraphEntity.expression, short_name="br",
                                     resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                                     label=label, g_set=self, forced_type=self.forced_type)

    def add_ci(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None) -> Citation:
        cur_g, count, label = self._add(graph_url=self.g_ci, res=res, short_name="ci")
        return Citation(cur_g, res=res, res_type=GraphEntity.citation, short_name="ci",
                        resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                        label=None, g_set=self, forced_type=self.forced_type)

    def add_de(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None) -> DiscourseElement:
        cur_g, count, label = self._add(graph_url=self.g_de, res=res, short_name="de")
        return DiscourseElement(cur_g, res=res, res_type=GraphEntity.discourse_element, short_name="de",
                                resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                                label=label, g_set=self, forced_type=self.forced_type)

    def add_id(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None) -> Identifier:
        cur_g, count, label = self._add(graph_url=self.g_id, res=res, short_name="id")
        return Identifier(cur_g, res=res, res_type=GraphEntity.identifier, short_name="id",
                          resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                          label=label, g_set=self, forced_type=self.forced_type)

    def add_pl(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None) -> PointerList:
        cur_g, count, label = self._add(graph_url=self.g_pl, res=res, short_name="pl")
        return PointerList(cur_g, res=res, res_type=GraphEntity.singleloc_pointer_list, short_name="pl",
                           resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                           label=label, g_set=self, forced_type=self.forced_type)

    def add_rp(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None) -> ReferencePointer:
        cur_g, count, label = self._add(graph_url=self.g_rp, res=res, short_name="rp")
        return ReferencePointer(cur_g, res=res, res_type=GraphEntity.intextref_pointer, short_name="rp",
                                resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                                label=label, g_set=self, forced_type=self.forced_type)

    def add_ra(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None) -> ResponsibleAgent:
        cur_g, count, label = self._add(graph_url=self.g_ra, res=res, short_name="ra")
        return ResponsibleAgent(cur_g, res=res, res_type=GraphEntity.agent, short_name="ra",
                                resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                                label=label, g_set=self, forced_type=self.forced_type)

    def add_re(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None) -> ResourceEmbodiment:
        cur_g, count, label = self._add(graph_url=self.g_re, res=res, short_name="re")
        return ResourceEmbodiment(cur_g, res=res, res_type=GraphEntity.manifestation, short_name="re",
                                  resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                                  label=label, g_set=self, forced_type=self.forced_type)

    def _add(self, graph_url: str, res: URIRef, short_name: str) -> Tuple[Graph, Optional[str], Optional[str]]:
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
        count = self.supplier_prefix + str(self.counter_handler.increment_counter(short_name))

        if self.wanted_label:
            label = "%s %s [%s/%s]" % (self.labels[short_name], count, short_name, count)

        return cur_g, count, label

    def graphs(self) -> List[Graph]:
        result = []
        for cur_g in self.g:
            if len(cur_g) > 0:
                result += [cur_g]
        return result

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

    @staticmethod
    def get_graph_iri(g: Graph) -> str:
        return str(g.identifier)

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
