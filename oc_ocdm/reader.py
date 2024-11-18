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
import time
from typing import TYPE_CHECKING
from zipfile import ZipFile

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.support.reporter import Reporter
from oc_ocdm.support.support import build_graph_from_results
from rdflib import RDF, ConjunctiveGraph, Graph, URIRef
from SPARQLWrapper import JSON, POST, SPARQLWrapper

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Set
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
        formats = ["json-ld", "rdfxml", "turtle", "trig", "nt11", "nquads"]
        loaded_graph = ConjunctiveGraph()

        if file_path.endswith('.zip'):
            try:
                with ZipFile(file=file_path, mode="r") as archive:
                    for zf_name in archive.namelist():
                        with archive.open(zf_name) as f:
                            if self._try_parse(loaded_graph, f, formats):
                                return loaded_graph
            except Exception as e:
                raise IOError(f"Error opening or reading zip file '{file_path}': {e}")
        else:
            try:
                with open(file_path, 'rt', encoding='utf-8') as f:
                    if self._try_parse(loaded_graph, f, formats):
                        return loaded_graph
            except Exception as e:
                raise IOError(f"Error opening or reading file '{file_path}': {e}")

        raise IOError(f"It was impossible to load the file '{file_path}' with supported formats.")

    def _try_parse(self, graph: ConjunctiveGraph, file_obj, formats: List[str]) -> bool:
        for cur_format in formats:
            file_obj.seek(0)  # Reset file pointer to the beginning for each new attempt
            try:
                if cur_format == "json-ld":
                    json_ld_file = json.load(file_obj)
                    if isinstance(json_ld_file, dict):
                        json_ld_file = [json_ld_file]
                    for json_ld_resource in json_ld_file:
                        if "@context" in json_ld_resource and json_ld_resource["@context"] in self.context_map:
                            json_ld_resource["@context"] = self.context_map[json_ld_resource["@context"]]["@context"]
                    data = json.dumps(json_ld_file, ensure_ascii=False)
                    graph.parse(data=data, format=cur_format)
                else:
                    graph.parse(file=file_obj, format=cur_format)
                return True  # Success, no need to try other formats
            except Exception as e:
                continue  # Try the next format
        return False  # None of the formats succeeded

    @staticmethod
    def get_graph_from_subject(graph: Graph, subject: URIRef) -> Graph:
        g: Graph = Graph(identifier=graph.identifier)
        for p, o in graph.predicate_objects(subject, unique=True):
            g.add((subject, p, o))
        return g

    @staticmethod
    def _extract_subjects(graph: Graph) -> Set[URIRef]:
        subjects: Set[URIRef] = set()
        for s in graph.subjects(unique=True):
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
    def import_entities_from_graph(g_set: GraphSet, results: List[Dict]|Graph, resp_agent: str,
                                   enable_validation: bool = False, closed: bool = False) -> List[GraphEntity]:
        graph = build_graph_from_results(results) if isinstance(results, list) else results
        if enable_validation:
            reader = Reader()
            graph = reader.graph_validation(graph, closed)
        imported_entities: List[GraphEntity] = []
        for subject in Reader._extract_subjects(graph):
            types = []
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
        query: str = f"SELECT ?s ?p ?o WHERE {{BIND (<{res}> AS ?s). ?s ?p ?o.}}"
        attempt = 0
        max_attempts = 3
        wait_time = 5  # Initial wait time in seconds

        while attempt < max_attempts:
            try:
                sparql: SPARQLWrapper = SPARQLWrapper(ts_url)
                sparql.setQuery(query)
                sparql.setMethod('GET')
                sparql.setReturnFormat(JSON)
                result = sparql.queryAndConvert()['results']['bindings']
                
                if not result:  # Se non ci sono risultati, l'entità non esiste
                    raise ValueError(f"The requested entity {res} was not found in the triplestore.")
                    
                imported_entities: List[GraphEntity] = Reader.import_entities_from_graph(g_set, result, resp_agent, enable_validation)
                if len(imported_entities) <= 0:
                    raise ValueError("The requested entity was not recognized as a proper OCDM entity.")
                return imported_entities[0]

            except ValueError as ve:  # Non facciamo retry per errori di validazione
                raise ve
            except Exception as e:
                attempt += 1
                if attempt < max_attempts:
                    print(f"[3] Attempt {attempt} failed. Could not import entity due to communication problems: {e}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    wait_time *= 2
                else:
                    print(f"[3] All {max_attempts} attempts failed. Could not import entity due to communication problems: {e}")
                    raise

        raise Exception("Max attempts reached. Failed to import entity from triplestore.")

    @staticmethod
    def import_entities_from_triplestore(g_set: GraphSet, ts_url: str, entities: List[URIRef], resp_agent: str,
                                    enable_validation: bool = False, batch_size: int = 1000) -> List[GraphEntity]:
        """
        Import multiple entities from a triplestore in batches using a single SPARQL query per batch.
        
        Args:
            g_set: The GraphSet to import entities into
            ts_url: The triplestore URL endpoint
            entities: List of URIRef entities to import
            resp_agent: The responsible agent string
            enable_validation: Whether to validate the imported graphs
            batch_size: Number of entities to import in each batch
            
        Returns:
            List of imported GraphEntity objects
        """
        if not entities:
            raise ValueError("No entities provided for import")
            
        imported_entities: List[GraphEntity] = []
        max_attempts = 3
        wait_time = 5  # Initial wait time in seconds
        
        # Process entities in batches
        for i in range(0, len(entities), batch_size):
            batch = entities[i:i + batch_size]
            not_found_entities = set(str(entity) for entity in batch)
            
            # Construct SPARQL query for batch using UNION pattern for Virtuoso
            union_patterns = []
            for entity in batch:
                union_patterns.append(f"{{ BIND(<{str(entity)}> AS ?s) ?s ?p ?o }}")
            
            query = f"""
            SELECT ?s ?p ?o
            WHERE {{
                {' UNION '.join(union_patterns)}
            }}
            """
            
            # Execute query with retry logic
            attempt = 0
            while attempt < max_attempts:
                try:
                    sparql: SPARQLWrapper = SPARQLWrapper(ts_url)
                    sparql.setQuery(query)
                    sparql.setMethod('GET')
                    sparql.setReturnFormat(JSON)
                    results = sparql.queryAndConvert()['results']['bindings']
                    
                    if not results:  # Se non ci sono risultati per questo batch
                        entities_str = ', '.join(not_found_entities)
                        raise ValueError(f"The requested entities were not found in the triplestore: {entities_str}")
                    
                    # Teniamo traccia delle entità trovate
                    for result in results:
                        if 's' in result and 'value' in result['s']:
                            not_found_entities.discard(result['s']['value'])
                    
                    # Import entities from results
                    try:
                        batch_entities = Reader.import_entities_from_graph(
                            g_set=g_set,
                            results=results,
                            resp_agent=resp_agent,
                            enable_validation=enable_validation
                        )
                        imported_entities.extend(batch_entities)
                        
                        # Se alcune entità non sono state trovate, lo segnaliamo
                        if not_found_entities:
                            entities_str = ', '.join(not_found_entities)
                            raise ValueError(f"The following entities were not recognized as proper OCDM entities: {entities_str}")
                        
                        break  # Usciamo dal ciclo di retry se tutto è andato bene
                        
                    except ValueError as ve:  # Errori di validazione non richiedono retry
                        raise ve
                        
                except ValueError as ve:  # Non facciamo retry per errori di validazione o entità non trovate
                    raise ve
                except Exception as e:
                    attempt += 1
                    if attempt < max_attempts:
                        print(f"[3] Attempt {attempt} failed. Could not import batch due to communication problems: {e}")
                        print(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        wait_time *= 2
                    else:
                        print(f"[3] All {max_attempts} attempts failed. Could not import batch due to communication problems: {e}")
                        raise
        
        if not imported_entities:
            raise ValueError("None of the requested entities were found or recognized as proper OCDM entities.")
            
        return imported_entities