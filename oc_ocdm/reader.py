#!/usr/bin/python

# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
# SPDX-FileCopyrightText: 2022-2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING
from zipfile import ZipFile

import orjson
from rdflib import Dataset, Graph, URIRef
from triplelite import TripleLite, from_rdflib

from oc_ocdm.constants import RDF_TYPE
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.support.reporter import Reporter
from oc_ocdm.support.sparql import SPARQLEndpointError, sparql_query
from oc_ocdm.support.support import build_graph_from_results, normalize_graph_literals

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, Dict, List, Optional

    from oc_ocdm.graph.graph_set import GraphSet

from pyshacl import validate


def _transform_jsonld_value(value: dict | str, uri_fn: Callable[[str], str]) -> dict | str:
    if isinstance(value, dict):
        if "@id" in value:
            return {"@id": uri_fn(value["@id"])}
        result: dict = {}
        if "@value" in value:
            result["@value"] = value["@value"]
        if "@type" in value:
            result["@type"] = uri_fn(value["@type"])
        if "@language" in value:
            result["@language"] = value["@language"]
        return result
    return value


def _transform_jsonld_entity(entity: dict, uri_fn: Callable[[str], str]) -> dict:
    transformed: dict = {}
    for key, value in entity.items():
        if key == "@id":
            transformed["@id"] = uri_fn(value)
        elif key == "@type":
            transformed["@type"] = [uri_fn(t) for t in value] if isinstance(value, list) else [uri_fn(value)]
        elif key.startswith("@"):
            continue
        else:
            new_key = uri_fn(key)
            if isinstance(value, list):
                transformed[new_key] = [_transform_jsonld_value(v, uri_fn) for v in value]
            else:
                transformed[new_key] = _transform_jsonld_value(value, uri_fn)
    return transformed


def _transform_jsonld_graphs(data: list[dict], uri_fn: Callable[[str], str]) -> list[dict]:
    result = []
    for graph_obj in data:
        new_graph: dict = {}
        if "@id" in graph_obj:
            new_graph["@id"] = uri_fn(graph_obj["@id"])
        if "@graph" in graph_obj:
            new_graph["@graph"] = [_transform_jsonld_entity(e, uri_fn) for e in graph_obj["@graph"]]
        result.append(new_graph)
    return result


def _expand_uri(curie: str, prefix_to_ns: dict[str, str]) -> str:
    colon = curie.find(":")
    if colon > 0:
        prefix = curie[:colon]
        ns = prefix_to_ns.get(prefix)
        if ns is not None:
            return ns + curie[colon + 1:]
    return curie


def _expand_jsonld(data: list[dict], prefix_to_ns: dict[str, str]) -> list[dict]:
    return _transform_jsonld_graphs(data, lambda uri: _expand_uri(uri, prefix_to_ns))


class Reader(object):

    def __init__(self, repok: Optional[Reporter] = None, reperr: Optional[Reporter] = None, context_map: Optional[Dict[str, Any]] = None) -> None:

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

    def load(self, rdf_file_path: str) -> Optional[Dataset]:
        self.repok.new_article()
        self.reperr.new_article()

        loaded_graph: Optional[Dataset] = None
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

    _EXT_TO_FORMATS: dict[str, list[str]] = {
        ".json": ["json-ld"],
        ".jsonld": ["json-ld"],
        ".xml": ["rdfxml"],
        ".rdf": ["rdfxml"],
        ".ttl": ["turtle"],
        ".trig": ["trig"],
        ".nt": ["nt11"],
        ".nq": ["nquads"],
    }
    _ALL_FORMATS: list[str] = ["json-ld", "rdfxml", "turtle", "trig", "nt11", "nquads"]

    @staticmethod
    def _formats_for_file(file_name: str) -> list[str]:
        ext = os.path.splitext(file_name)[1].lower()
        preferred = Reader._EXT_TO_FORMATS.get(ext)
        if preferred is not None:
            return preferred + [f for f in Reader._ALL_FORMATS if f not in preferred]
        return Reader._ALL_FORMATS

    def _load_graph(self, file_path: str) -> Dataset:
        loaded_graph = Dataset()

        if file_path.endswith('.zip'):
            try:
                with ZipFile(file=file_path, mode="r") as archive:
                    for zf_name in archive.namelist():
                        formats = self._formats_for_file(zf_name)
                        with archive.open(zf_name) as f:
                            if self._try_parse(loaded_graph, f, formats):
                                for graph in loaded_graph.graphs():
                                    normalize_graph_literals(graph)
                                return loaded_graph
            except Exception as e:
                raise IOError(f"Error opening or reading zip file '{file_path}': {e}")
        else:
            formats = self._formats_for_file(file_path)
            try:
                with open(file_path, 'rt', encoding='utf-8') as f:
                    if self._try_parse(loaded_graph, f, formats):
                        for graph in loaded_graph.graphs():
                            normalize_graph_literals(graph)
                        return loaded_graph
            except Exception as e:
                raise IOError(f"Error opening or reading file '{file_path}': {e}")

        raise IOError(f"It was impossible to load the file '{file_path}' with supported formats.")

    def _try_parse(self, graph: Dataset, file_obj, formats: List[str]) -> bool:
        for cur_format in formats:
            file_obj.seek(0)
            try:
                if cur_format == "json-ld":
                    json_ld_file = json.load(file_obj)
                    if isinstance(json_ld_file, dict):
                        json_ld_file = [json_ld_file]
                    for json_ld_resource in json_ld_file:
                        if "@context" in json_ld_resource and json_ld_resource["@context"] in self.context_map:
                            json_ld_resource["@context"] = self.context_map[json_ld_resource["@context"]]["@context"]
                    graph.parse(data=json.dumps(json_ld_file, ensure_ascii=False), format=cur_format)
                else:
                    graph.parse(file=file_obj, format=cur_format)
                return True
            except Exception:
                continue
        return False

    def load_jsonld_dict(self, rdf_file_path: str) -> list[dict]:
        if rdf_file_path.endswith('.zip'):
            with ZipFile(file=rdf_file_path, mode="r") as archive:
                for zf_name in archive.namelist():
                    ext = os.path.splitext(zf_name)[1].lower()
                    if ext in ('.json', '.jsonld'):
                        with archive.open(zf_name) as f:
                            data = orjson.loads(f.read())
                            break
                else:
                    raise IOError(f"No JSON/JSON-LD file found inside ZIP archive '{rdf_file_path}'.")
        else:
            with open(rdf_file_path, 'rb') as f:
                data = orjson.loads(f.read())
        if isinstance(data, dict):
            data = [data]
        prefix_to_ns: dict[str, str] | None = None
        for graph_obj in data:
            ctx_url = graph_obj.get("@context")
            if ctx_url and ctx_url in self.context_map:
                ctx = self.context_map[ctx_url]
                if isinstance(ctx, dict) and "@context" in ctx:
                    ctx = ctx["@context"]
                prefix_to_ns = {
                    k: v for k, v in ctx.items()
                    if isinstance(v, str) and not k.startswith("@")
                }
                break
        if prefix_to_ns is not None:
            data = _expand_jsonld(data, prefix_to_ns)
        return data

    def graph_validation(self, graph: Graph, closed: bool = False) -> Graph:
        valid_graph: Graph = Graph(identifier=graph.identifier)
        sg = Graph()
        if closed:
            sg.parse(os.path.join('oc_ocdm', 'resources', 'shacle_closed.ttl'))
        else:
            sg.parse(os.path.join('oc_ocdm', 'resources', 'shacle.ttl'))
        _, report_result, _ = validate(graph,
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
        if not isinstance(report_result, Graph):
            raise TypeError(f"Expected Graph from SHACL validation, got {type(report_result)}")
        invalid_nodes = set()
        for triple in report_result.triples((None, URIRef('http://www.w3.org/ns/shacl#focusNode'), None)):
            invalid_nodes.add(triple[2])
        for s in graph.subjects(unique=True):
            if isinstance(s, URIRef) and s not in invalid_nodes:
                for valid_subject_triple in graph.triples((s, None, None)):
                    valid_graph.add(valid_subject_triple)
        return valid_graph

    @staticmethod
    def import_entities_from_graph(g_set: GraphSet, results: List[Dict] | TripleLite | Graph | Dataset, resp_agent: str,
                                   enable_validation: bool = False, closed: bool = False) -> List[GraphEntity]:
        if isinstance(results, list):
            graph: TripleLite | Graph = build_graph_from_results(results)
        elif isinstance(results, Dataset):
            merged = TripleLite()
            for tl in from_rdflib(results):
                for triple in tl.triples((None, None, None)):
                    merged.add(triple)
            graph = merged
        elif isinstance(results, Graph):
            graph = results
        else:
            graph = results
        if enable_validation:
            reader = Reader()
            if not isinstance(graph, Graph):
                graph = graph.to_rdflib()
            graph = reader.graph_validation(graph, closed)
        if isinstance(graph, Graph):
            graph = from_rdflib(graph)[0]
        imported_entities: List[GraphEntity] = []
        for subject in graph.subjects():
            types: List[str] = [o.value for o in graph.objects(subject, RDF_TYPE)]
            preexisting = graph.subgraph(subject)
            if GraphEntity.iri_note in types:
                imported_entities.append(g_set.add_an(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=preexisting))
            elif GraphEntity.iri_role_in_time in types:
                imported_entities.append(g_set.add_ar(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=preexisting))
            elif GraphEntity.iri_bibliographic_reference in types:
                imported_entities.append(g_set.add_be(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=preexisting))
            elif GraphEntity.iri_expression in types:
                imported_entities.append(g_set.add_br(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=preexisting))
            elif GraphEntity.iri_citation in types:
                imported_entities.append(g_set.add_ci(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=preexisting))
            elif GraphEntity.iri_discourse_element in types:
                imported_entities.append(g_set.add_de(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=preexisting))
            elif GraphEntity.iri_identifier in types:
                imported_entities.append(g_set.add_id(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=preexisting))
            elif GraphEntity.iri_singleloc_pointer_list in types:
                imported_entities.append(g_set.add_pl(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=preexisting))
            elif GraphEntity.iri_agent in types:
                imported_entities.append(g_set.add_ra(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=preexisting))
            elif GraphEntity.iri_manifestation in types:
                imported_entities.append(g_set.add_re(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=preexisting))
            elif GraphEntity.iri_intextref_pointer in types:
                imported_entities.append(g_set.add_rp(resp_agent=resp_agent, res=subject,
                                         preexisting_graph=preexisting))
        return imported_entities

    @staticmethod
    def import_entity_from_triplestore(g_set: GraphSet, ts_url: str, res: str, resp_agent: str,
                                    enable_validation: bool = False) -> GraphEntity:
        query: str = f"SELECT ?s ?p ?o WHERE {{BIND (<{res}> AS ?s). ?s ?p ?o.}}"
        try:
            result = sparql_query(ts_url, query, max_retries=3, backoff_factor=2.5)['results']['bindings']

            if not result:
                raise ValueError(f"The requested entity {res} was not found in the triplestore.")

            imported_entities: List[GraphEntity] = Reader.import_entities_from_graph(g_set, result, resp_agent, enable_validation)
            if len(imported_entities) <= 0:
                raise ValueError("The requested entity was not recognized as a proper OCDM entity.")
            return imported_entities[0]

        except ValueError:
            raise
        except SPARQLEndpointError as e:
            print(f"[3] Could not import entity due to communication problems: {e}")
            raise

    @staticmethod
    def import_entities_from_triplestore(g_set: GraphSet, ts_url: str, entities: List[str], resp_agent: str,
                                    enable_validation: bool = False, batch_size: int = 1000) -> List[GraphEntity]:
        if not entities:
            raise ValueError("No entities provided for import")

        imported_entities: List[GraphEntity] = []

        try:
            for i in range(0, len(entities), batch_size):
                batch = entities[i:i + batch_size]
                not_found_entities = set(batch)

                union_patterns = []
                for entity in batch:
                    union_patterns.append(f"{{ BIND(<{entity}> AS ?s) ?s ?p ?o }}")

                query = f"""
                SELECT ?s ?p ?o
                WHERE {{
                    {' UNION '.join(union_patterns)}
                }}
                """

                results = sparql_query(ts_url, query, max_retries=3, backoff_factor=2.5)['results']['bindings']

                if not results:
                    entities_str = ', '.join(not_found_entities)
                    raise ValueError(f"The requested entities were not found in the triplestore: {entities_str}")

                for result in results:
                    if 's' in result and 'value' in result['s']:
                        not_found_entities.discard(result['s']['value'])

                batch_entities = Reader.import_entities_from_graph(
                    g_set=g_set,
                    results=results,
                    resp_agent=resp_agent,
                    enable_validation=enable_validation
                )
                imported_entities.extend(batch_entities)

                if not_found_entities:
                    entities_str = ', '.join(not_found_entities)
                    raise ValueError(f"The following entities were not recognized as proper OCDM entities: {entities_str}")

        except ValueError:
            raise
        except SPARQLEndpointError as e:
            print(f"[3] Could not import batch due to communication problems: {e}")
            raise

        if not imported_entities:
            raise ValueError("None of the requested entities were found or recognized as proper OCDM entities.")

        return imported_entities