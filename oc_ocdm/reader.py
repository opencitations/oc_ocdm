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

from importlib import resources
from pyshex import ShExEvaluator
from rdflib import RDF
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List
    from oc_ocdm import GraphSet, GraphEntity
    from rdflib import Graph, URIRef, term


class Reader(object):

    @staticmethod
    def get_graph_from_subject(graph: Graph, subject: URIRef):
        g: Graph = Graph(identifier=graph.identifier)
        for p, o in graph.predicate_objects(subject):
            g.add((subject, p, o))
        return g

    @staticmethod
    def graph_validation(graph: Graph, closed: bool = False):
        valid_graph: Graph = Graph(identifier=graph.identifier)
        if closed:
            shex = resources.read_text('resources', 'shexc_closed.txt')
        else:
            shex = resources.read_text('resources', 'shexc.txt')
        for node_result in ShExEvaluator().evaluate(rdf=graph, shex=shex):
            if node_result.result and node_result.focus is not None:
                valid_graph.add(graph.triples(node_result.focus, None, None))
        return valid_graph

    def import_entities_from_graph(self, g_set: GraphSet, graph: Graph, enable_validation: bool = True,
                                   closed: bool = False):
        if enable_validation:
            graph = self.graph_validation(graph, closed)

        for subject in graph.subjects():
            types: List[term] = []
            for o in graph.objects(subject, RDF.type):
                types.append(o)

            # ReferenceAnnotation
            if GraphEntity.iri_note in types:
                g_set.add_an(resp_agent='importer', res=subject,
                             preexisting_graph=self.get_graph_from_subject(graph, subject))
            # AgentRole
            elif GraphEntity.iri_role_in_time in types:
                g_set.add_ar(resp_agent='importer', res=subject,
                             preexisting_graph=self.get_graph_from_subject(graph, subject))
            # BibliographicReference
            elif GraphEntity.iri_bibliographic_reference in types:
                g_set.add_be(resp_agent='importer', res=subject,
                             preexisting_graph=self.get_graph_from_subject(graph, subject))
            # BibliographicResource
            elif GraphEntity.iri_expression in types:
                g_set.add_br(resp_agent='importer', res=subject,
                             preexisting_graph=self.get_graph_from_subject(graph, subject))
            # Citation
            elif GraphEntity.iri_citation in types:
                g_set.add_ci(resp_agent='importer', res=subject,
                             preexisting_graph=self.get_graph_from_subject(graph, subject))
            # DiscourseElement
            elif GraphEntity.iri_discourse_element in types:
                g_set.add_de(resp_agent='importer', res=subject,
                             preexisting_graph=self.get_graph_from_subject(graph, subject))
            # Identifier
            elif GraphEntity.iri_identifier in types:
                g_set.add_id(resp_agent='importer', res=subject,
                             preexisting_graph=self.get_graph_from_subject(graph, subject))
            # PointerList
            elif GraphEntity.iri_singleloc_pointer_list in types:
                g_set.add_pl(resp_agent='importer', res=subject,
                             preexisting_graph=self.get_graph_from_subject(graph, subject))
            # ResponsibleAgent
            elif GraphEntity.iri_agent in types:
                g_set.add_ra(resp_agent='importer', res=subject,
                             preexisting_graph=self.get_graph_from_subject(graph, subject))
            # ResourceEmbodiment
            elif GraphEntity.iri_manifestation in types:
                g_set.add_re(resp_agent='importer', res=subject,
                             preexisting_graph=self.get_graph_from_subject(graph, subject))
            # ReferencePointer
            elif GraphEntity.iri_intextref_pointer in types:
                g_set.add_rp(resp_agent='importer', res=subject,
                             preexisting_graph=self.get_graph_from_subject(graph, subject))
