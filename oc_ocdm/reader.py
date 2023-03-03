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

import json
import os
from typing import TYPE_CHECKING
from zipfile import ZipFile

import rdflib
from filelock import FileLock
from rdflib import RDF, ConjunctiveGraph, Graph, Namespace, URIRef
from SPARQLWrapper import RDFXML, SPARQLWrapper

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.support.reporter import Reporter

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Set

    from rdflib import term

    from oc_ocdm.graph.graph_set import GraphSet

from pyshacl import validate


class Reader(object):

    def __init__(self, repok: Reporter = None, reperr: Reporter = None, context_map: Dict[str, Any] = None) -> None:

        if context_map is not None:
            self.context_map: Dict[str, Any] = context_map
        else:
            self.context_map: Dict[str, Any] = {}
        for context_url in self.context_map:
            ctx_file_path: Any = self.context_map[context_url]
            if type(ctx_file_path) == str and os.path.isfile(ctx_file_path):
                # This expensive operation is done only when it's really needed
                with open(ctx_file_path, 'rt', encoding='utf-8') as ctx_f:
                    self.context_map[context_url] = json.load(ctx_f)

        if repok is None:
            self.repok: Reporter = Reporter(prefix="[Reader: INFO] ")
        else:
            self.repok: Reporter = repok

        if reperr is None:
            self.reperr: Reporter = Reporter(prefix="[Reader: ERROR] ")
        else:
            self.reperr: Reporter = reperr

    def load(self, rdf_file_path: str) -> Optional[ConjunctiveGraph]:
        self.repok.new_article()
        self.reperr.new_article()

        loaded_graph: Optional[ConjunctiveGraph] = None
        if os.path.isfile(rdf_file_path):

            try:
                loaded_graph = self._load_graph(rdf_file_path)
            except Exception as e:
                self.reperr.add_sentence("[1] "
                                         "It was impossible to handle the format used for "
                                         "storing the file (stored in the temporary path) "
                                         f"'{rdf_file_path}'. Additional details: {e}")
        else:
            self.reperr.add_sentence("[2] "
                                     f"The file specified ('{rdf_file_path}') doesn't exist.")

        return loaded_graph

    def _load_graph(self, file_path: str) -> ConjunctiveGraph:
        formats: List[str] = ["json-ld", "rdfxml", "turtle", "trig", "nt11", "nquads"]

        loaded_graph: ConjunctiveGraph = ConjunctiveGraph()

        errors: str = ""
        for cur_format in formats:
            try:
                lock = FileLock(f"{file_path}.lock")
                with lock:
                    if file_path.endswith('.zip'):
                        with ZipFile(file=file_path, mode="r") as archive:
                            for zf_name in archive.namelist():
                                f = archive.open(zf_name)
                    else:
                        f = open(file_path, 'rt', encoding='utf-8')
                    if cur_format == "json-ld":
                        json_ld_file: Any = json.load(f)
                        if isinstance(json_ld_file, dict):
                            json_ld_file: List[Any] = [json_ld_file]

                        for json_ld_resource in json_ld_file:
                            # Trick to force the use of a pre-loaded context if the format
                            # specified is JSON-LD
                            if "@context" in json_ld_resource:
                                cur_context: str = json_ld_resource["@context"]
                                if cur_context in self.context_map:
                                    context_json: Any = self.context_map[cur_context]["@context"]
                                    json_ld_resource["@context"] = context_json

                            loaded_graph.parse(data=json.dumps(json_ld_resource, ensure_ascii=False),
                                            format=cur_format)
                    else:
                        loaded_graph.parse(file=f, format=cur_format)
                    f.close()
                return loaded_graph
            except Exception as e:
                errors += f" | {e}"  # Try another format

        raise IOError("1", f"It was impossible to handle the format used for storing the file '{file_path}'{errors}")

    @staticmethod
    def get_graph_from_subject(graph: Graph, subject: URIRef) -> Graph:
        g: Graph = Graph(identifier=graph.identifier)
        for p, o in graph.predicate_objects(subject):
            if isinstance(o, rdflib.term.Literal):
                o = rdflib.term.Literal(lexical_or_value=str(o), datatype=None)
            g.add((subject, p, o))
        return g

    @staticmethod
    def _extract_subjects(graph: Graph) -> Set[URIRef]:
        subjects: Set[URIRef] = set()
        for s in graph.subjects():
            subjects.add(s)
        return subjects

    def graph_validation(self, graph: Graph, closed: bool = False) -> Graph:
        valid_graph: Graph = Graph(identifier=graph.identifier)
        sg = Graph()
        if closed:
            sg.parse(os.path.join('oc_ocdm', 'resources', 'shacle_closed.ttl'))
        else:
            sg.parse(os.path.join('oc_ocdm', 'resources', 'shacle.ttl'))
        _, report_g, _ = validate(graph,
            shacl_graph=sg,
            ont_graph=None,
            inference=None,
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            meta_shacl=False,
            advanced=False,
            js=False,
            debug=False)
        invalid_nodes = set()
        for triple in report_g.triples((None, URIRef('http://www.w3.org/ns/shacl#focusNode'), None)):
            invalid_nodes.add(triple[2])
        for subject in self._extract_subjects(graph):
            if subject not in invalid_nodes:
                for valid_subject_triple in graph.triples((subject, None, None)):
                    valid_graph.add(valid_subject_triple)
        return valid_graph

    @staticmethod
    def import_entities_from_graph(g_set: GraphSet, graph: Graph, resp_agent: str,
                                   enable_validation: bool = False, closed: bool = False) -> List[GraphEntity]:
        if enable_validation:
            reader = Reader()
            graph = reader.graph_validation(graph, closed)
        imported_entities: List[GraphEntity] = []
        for subject in Reader._extract_subjects(graph):
            types: List[term] = []
            for o in graph.objects(subject, RDF.type):
                types.append(o)
            # ReferenceAnnotation
            if GraphEntity.iri_note in types:
                imported_entities.append(g_set.add_an(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=Reader.get_graph_from_subject(graph, subject)))
            # AgentRole
            elif GraphEntity.iri_role_in_time in types:
                imported_entities.append(g_set.add_ar(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=Reader.get_graph_from_subject(graph, subject)))
            # BibliographicReference
            elif GraphEntity.iri_bibliographic_reference in types:
                imported_entities.append(g_set.add_be(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=Reader.get_graph_from_subject(graph, subject)))
            # BibliographicResource
            elif GraphEntity.iri_expression in types:
                imported_entities.append(g_set.add_br(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=Reader.get_graph_from_subject(graph, subject)))
            # Citation
            elif GraphEntity.iri_citation in types:
                imported_entities.append(g_set.add_ci(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=Reader.get_graph_from_subject(graph, subject)))
            # DiscourseElement
            elif GraphEntity.iri_discourse_element in types:
                imported_entities.append(g_set.add_de(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=Reader.get_graph_from_subject(graph, subject)))
            # Identifier
            elif GraphEntity.iri_identifier in types:
                imported_entities.append(g_set.add_id(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=Reader.get_graph_from_subject(graph, subject)))
            # PointerList
            elif GraphEntity.iri_singleloc_pointer_list in types:
                imported_entities.append(g_set.add_pl(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=Reader.get_graph_from_subject(graph, subject)))
            # ResponsibleAgent
            elif GraphEntity.iri_agent in types:
                imported_entities.append(g_set.add_ra(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=Reader.get_graph_from_subject(graph, subject)))
            # ResourceEmbodiment
            elif GraphEntity.iri_manifestation in types:
                imported_entities.append(g_set.add_re(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=Reader.get_graph_from_subject(graph, subject)))
            # ReferencePointer
            elif GraphEntity.iri_intextref_pointer in types:
                imported_entities.append(g_set.add_rp(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=Reader.get_graph_from_subject(graph, subject)))
        return imported_entities

    @staticmethod
    def import_entity_from_triplestore(g_set: GraphSet, ts_url: str, res: URIRef, resp_agent: str,
                                       enable_validation: bool = False) -> GraphEntity:
        sparql: SPARQLWrapper = SPARQLWrapper(ts_url)
        query: str = f"CONSTRUCT {{<{res}> ?p ?o}} WHERE {{<{res}> ?p ?o}}"
        sparql.setQuery(query)
        sparql.setMethod('GET')
        sparql.setReturnFormat(RDFXML)
        result: ConjunctiveGraph = sparql.query().convert()
        if result is not None:
            imported_entities: List[GraphEntity] = Reader.import_entities_from_graph(g_set, result,
                                                                                     resp_agent, enable_validation)
            if len(imported_entities) <= 0:
                raise ValueError("The requested entity was not found or was not recognized as a proper OCDM entity.")
            else:
                return imported_entities[0]