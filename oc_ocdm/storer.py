#!/usr/bin/python

# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
# SPDX-FileCopyrightText: 2022-2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from typing import TYPE_CHECKING
from zipfile import ZIP_DEFLATED, ZipFile

import orjson
from filelock import FileLock
from rdflib import Dataset, Literal, URIRef
from triplelite import TripleLite

from oc_ocdm.constants import RDF_TYPE, XSD_STRING
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.metadata.metadata_entity import MetadataEntity
from oc_ocdm.prov.prov_entity import ProvEntity
from oc_ocdm.reader import Reader, _transform_jsonld_graphs
from oc_ocdm.support.query_utils import get_update_query
from oc_ocdm.support.reporter import Reporter
from oc_ocdm.support.sparql import SPARQLEndpointError, sparql_update
from oc_ocdm.support.support import find_paths

if TYPE_CHECKING:
    from typing import Any, Dict, List, Set, Tuple

    from oc_ocdm.abstract_entity import AbstractEntity
    from oc_ocdm.abstract_set import AbstractSet


def _entity_to_jsonld_dict(entity) -> dict:
    result: dict = {"@id": entity.res}
    types: list[str] = []
    props: dict[str, list] = {}
    for _, p, o in entity.g.triples((entity.res, None, None)):
        if p == RDF_TYPE:
            types.append(o.value)
        else:
            if o.type == "uri":
                val: dict = {"@id": o.value}
            elif o.lang:
                val = {"@language": o.lang, "@value": o.value}
            else:
                val = {"@type": o.datatype if o.datatype else XSD_STRING, "@value": o.value}
            props.setdefault(p, []).append(val)
    if types:
        result["@type"] = types
    result.update(props)
    return result


def _compact_uri(uri: str, ns_to_prefix: list[tuple[str, str]]) -> str:
    for ns, prefix in ns_to_prefix:
        if uri.startswith(ns):
            return prefix + ":" + uri[len(ns):]
    return uri


def _compact_jsonld(data: list[dict], context_path: str, ns_to_prefix: list[tuple[str, str]]) -> dict | list[dict]:
    compacted = _transform_jsonld_graphs(data, lambda uri: _compact_uri(uri, ns_to_prefix))
    for graph_obj in compacted:
        graph_obj["@context"] = context_path
    if len(compacted) == 1:
        return compacted[0]
    return compacted


class _JsonLdDoc:
    __slots__ = ("_entities",)

    def __init__(self, data: list[dict]) -> None:
        self._entities: dict[str, dict[str, dict]] = {}
        for graph_obj in data:
            graph_iri = graph_obj["@id"]
            entity_index: dict[str, dict] = {}
            for entity_dict in graph_obj["@graph"]:
                entity_index[entity_dict["@id"]] = entity_dict
            self._entities[graph_iri] = entity_index

    def upsert_entity(self, graph_iri: str, entity_uri: str, entity_dict: dict) -> None:
        if graph_iri not in self._entities:
            self._entities[graph_iri] = {}
        self._entities[graph_iri][entity_uri] = entity_dict

    def merge_entity(self, graph_iri: str, entity_uri: str, entity_dict: dict) -> None:
        if graph_iri not in self._entities:
            self._entities[graph_iri] = {}
        existing = self._entities[graph_iri].get(entity_uri)
        if existing is None:
            self._entities[graph_iri][entity_uri] = entity_dict
            return
        for key, value in entity_dict.items():
            if key == "@id":
                continue
            if key not in existing:
                existing[key] = value
            else:
                for v in value:
                    if v not in existing[key]:
                        existing[key].append(v)

    def remove_entity(self, graph_iri: str, entity_uri: str) -> None:
        if graph_iri in self._entities and entity_uri in self._entities[graph_iri]:
            del self._entities[graph_iri][entity_uri]

    def to_list(self) -> list[dict]:
        return [
            {"@id": graph_iri, "@graph": list(entities.values())}
            for graph_iri, entities in self._entities.items()
            if entities
        ]


class Storer(object):

    def __init__(self, abstract_set: AbstractSet, repok: Reporter | None = None, reperr: Reporter | None = None,
                 context_map: Dict[str, Any] | None = None, default_dir: str = "_", dir_split: int = 0,
                 n_file_item: int = 1, output_format: str = "json-ld", zip_output: bool = False, modified_entities: set | None = None) -> None:
        # We only accept format strings that:
        # 1. are supported by rdflib
        # 2. correspond to an output format which is effectively either NT or NQ
        # The only exception to this rule is the 'json-ld' format, which is the default value of 'output_format'.
        supported_formats: Set[str] = {'application/n-triples', 'ntriples', 'nt', 'nt11',
                                       'application/n-quads', 'nquads', 'json-ld'}
        if output_format not in supported_formats:
            raise ValueError(f"Given output_format '{output_format}' is not supported."
                             f" Available formats: {supported_formats}.")
        else:
            self.output_format: str = output_format
        self.zip_output = zip_output
        self.dir_split: int = dir_split
        self.n_file_item: int = n_file_item
        self.default_dir: str = default_dir if default_dir != "" else "_"
        self.a_set: AbstractSet = abstract_set
        self.modified_entities = modified_entities

        if context_map is not None:
            self.context_map: Dict[str, Any] = context_map
        else:
            self.context_map: Dict[str, Any] = {}

        if self.output_format == "json-ld":
            for context_url in self.context_map:
                ctx_file_path: Any = self.context_map[context_url]
                if type(ctx_file_path) == str and os.path.isfile(ctx_file_path):
                    # This expensive operation is done only when it's really needed
                    with open(ctx_file_path, 'rt', encoding='utf-8') as ctx_f:
                        self.context_map[context_url] = json.load(ctx_f)

        if repok is None:
            self.repok: Reporter = Reporter(prefix="[Storer: INFO] ")
        else:
            self.repok: Reporter = repok

        if reperr is None:
            self.reperr: Reporter = Reporter(prefix="[Storer: ERROR] ")
        else:
            self.reperr: Reporter = reperr

    @staticmethod
    def _to_rdflib_obj(o) -> URIRef | Literal:
        if o.type == "literal":
            if o.lang:
                return Literal(o.value, lang=o.lang)
            return Literal(o.value, datatype=URIRef(o.datatype))
        return URIRef(o.value)

    @staticmethod
    def _entity_quads(entity_g) -> list:
        if isinstance(entity_g, TripleLite):
            graph_id = URIRef(entity_g.identifier) if entity_g.identifier else None
            return [(URIRef(s), URIRef(p), Storer._to_rdflib_obj(o), graph_id)
                    for s, p, o in entity_g]
        graph_id = entity_g.identifier
        return [(*item, graph_id) for item in entity_g]

    def store_graphs_in_file(self, file_path: str, context_path: str | None = None) -> None:
        self.repok.new_article()
        self.reperr.new_article()
        self.repok.add_sentence("Store the graphs into a file: starting process")

        if self.output_format == "json-ld":
            self._store_graphs_in_file_jsonld_fast(file_path, context_path)
            return

        cg: Dataset = Dataset()
        for g in self.a_set.graphs():
            cg.addN(self._entity_quads(g))

        self._store_in_file(cg, file_path, context_path)

    def _store_in_file(self, cur_g: Dataset, cur_file_path: str, context_path: str | None = None) -> None:
        zip_file_path = cur_file_path.replace(os.path.splitext(cur_file_path)[1], ".zip")

        if self.zip_output:
            with ZipFile(zip_file_path, mode="w", compression=ZIP_DEFLATED, allowZip64=True) as zip_file:
                self._write_graph(cur_g, zip_file, cur_file_path, context_path)
        else:
            self._write_graph(cur_g, None, cur_file_path, context_path)

        self.repok.add_sentence(f"File '{cur_file_path}' added.")

    def _write_graph(self, graph: Dataset, zip_file: ZipFile | None, cur_file_path: str, context_path: str | None) -> None:
        if self.output_format == "json-ld":
            if context_path is not None and context_path in self.context_map:
                cur_json_ld = json.loads(graph.serialize(format="json-ld", context=self.context_map[context_path]))
                if isinstance(cur_json_ld, dict):
                    cur_json_ld["@context"] = context_path
                else:
                    for item in cur_json_ld:
                        item["@context"] = context_path
                if zip_file is not None:
                    data = json.dumps(cur_json_ld, ensure_ascii=False).encode('utf-8')
                    zip_file.writestr(zinfo_or_arcname=os.path.basename(cur_file_path), data=data)
                else:
                    with open(cur_file_path, 'wt', encoding='utf-8') as f:
                        json.dump(cur_json_ld, f, ensure_ascii=False)
            else:
                if zip_file is not None:
                    data = graph.serialize(format="json-ld").encode('utf-8')
                    zip_file.writestr(zinfo_or_arcname=os.path.basename(cur_file_path), data=data)
                else:
                    graph.serialize(destination=cur_file_path, format="json-ld")
        else:
            # Handle other RDF formats
            if zip_file is not None:
                rdf_serialization = graph.serialize(destination=None, format=self.output_format, encoding="utf-8")
                zip_file.writestr(zinfo_or_arcname=os.path.basename(cur_file_path), data=rdf_serialization)
            else:
                graph.serialize(destination=cur_file_path, format=self.output_format, encoding="utf-8")

    def store_all(self, base_dir: str, base_iri: str, context_path: str | None = None, process_id: int | str | None = None) -> List[str]:
        self.repok.new_article()
        self.reperr.new_article()

        self.repok.add_sentence("Starting the process")

        relevant_paths: Dict[str, list] = dict()
        created_dirs = set()
        for entity in self.a_set.res_to_entity.values():
            is_relevant = True
            if self.modified_entities is not None and entity.res.split('/prov/se/')[0] not in self.modified_entities:
                is_relevant = False
            if is_relevant:
                cur_dir_path, cur_file_path = self._dir_and_file_paths(entity.res, base_dir, base_iri, process_id)
                if cur_dir_path not in created_dirs:
                    os.makedirs(cur_dir_path, exist_ok=True)
                    created_dirs.add(cur_dir_path)
                relevant_paths.setdefault(cur_file_path, list())
                relevant_paths[cur_file_path].append(entity)

        if self.output_format == "json-ld":
            return self._store_all_jsonld_fast(relevant_paths, context_path)

        reader = Reader(context_map=self.context_map)
        for relevant_path, entities_in_path in relevant_paths.items():
            stored_g = None
            output_filepath = relevant_path.replace(os.path.splitext(relevant_path)[1], ".zip") if self.zip_output else relevant_path
            lock = FileLock(f"{output_filepath}.lock")
            with lock:
                if os.path.exists(output_filepath):
                    stored_g = reader.load(output_filepath)
                if stored_g is None:
                    stored_g = Dataset()
                for entity_in_path in entities_in_path:
                    self.store(entity_in_path, stored_g, relevant_path, context_path, False)
                self._store_in_file(stored_g, relevant_path, context_path)

        return list(relevant_paths.keys())

    def _entity_triples_as_rdflib_quads(self, entity: AbstractEntity) -> List[Tuple]:
        graph_id = URIRef(entity.g.identifier) if entity.g.identifier else None
        return [(URIRef(s), URIRef(p), self._to_rdflib_obj(o), graph_id)
                for s, p, o in entity.g.triples((entity.res, None, None))]

    def store(self, entity: AbstractEntity, destination_g: Dataset, cur_file_path: str, context_path: str | None = None, store_now: bool = True) -> Dataset | None:
        self.repok.new_article()
        self.reperr.new_article()

        try:
            if isinstance(entity, ProvEntity):
                destination_g.addN(self._entity_triples_as_rdflib_quads(entity))
            elif isinstance(entity, GraphEntity) or isinstance(entity, MetadataEntity):
                if entity.to_be_deleted:
                    destination_g.remove((URIRef(entity.res), None, None, None))  # type: ignore[arg-type]
                else:
                    if len(entity._preexisting_triples) > 0:
                        destination_g.remove((URIRef(entity.res), None, None, None))  # type: ignore[arg-type]
                    destination_g.addN(self._entity_triples_as_rdflib_quads(entity))

            if store_now:
                self._store_in_file(destination_g, cur_file_path, context_path)

            return destination_g
        except Exception as e:
            self.reperr.add_sentence(f"[1] It was impossible to store the RDF statements in {cur_file_path}. {e}")

    def _build_ns_to_prefix(self, context_path: str) -> list[tuple[str, str]]:
        ctx = self.context_map[context_path]
        if isinstance(ctx, dict) and "@context" in ctx:
            ctx = ctx["@context"]
        pairs = [
            (ns, prefix) for prefix, ns in ctx.items()
            if isinstance(ns, str) and not prefix.startswith("@")
        ]
        pairs.sort(key=lambda x: len(x[0]), reverse=True)
        return pairs

    def _write_jsonld_fast(self, json_bytes: bytes, relevant_path: str) -> None:
        if self.zip_output:
            zip_file_path = relevant_path.replace(os.path.splitext(relevant_path)[1], ".zip")
            with ZipFile(zip_file_path, mode="w", compression=ZIP_DEFLATED, allowZip64=True) as zf:
                zf.writestr(os.path.basename(relevant_path), json_bytes)
        else:
            with open(relevant_path, 'wb') as f:
                f.write(json_bytes)
        self.repok.add_sentence(f"File '{relevant_path}' added.")

    def _store_all_jsonld_fast(self, relevant_paths: Dict[str, list], context_path: str | None) -> List[str]:
        reader = Reader(context_map=self.context_map)
        ns_to_prefix: list[tuple[str, str]] | None = None
        if context_path is not None and context_path in self.context_map:
            ns_to_prefix = self._build_ns_to_prefix(context_path)

        for relevant_path, entities_in_path in relevant_paths.items():
            output_filepath = relevant_path.replace(os.path.splitext(relevant_path)[1], ".zip") if self.zip_output else relevant_path
            lock = FileLock(f"{output_filepath}.lock")
            with lock:
                existing_data: list[dict] | None = None
                if os.path.exists(output_filepath):
                    existing_data = reader.load_jsonld_dict(output_filepath)
                doc = _JsonLdDoc(existing_data if existing_data is not None else [])

                for entity in entities_in_path:
                    graph_iri = entity.g.identifier
                    if isinstance(entity, ProvEntity):
                        doc.merge_entity(graph_iri, entity.res, _entity_to_jsonld_dict(entity))
                    elif isinstance(entity, (GraphEntity, MetadataEntity)):
                        if entity.to_be_deleted:
                            doc.remove_entity(graph_iri, entity.res)
                        else:
                            if len(entity._preexisting_triples) > 0:
                                doc.remove_entity(graph_iri, entity.res)
                            doc.upsert_entity(graph_iri, entity.res, _entity_to_jsonld_dict(entity))

                output_data: list[dict] | dict = doc.to_list()
                if context_path is not None and ns_to_prefix is not None:
                    output_data = _compact_jsonld(output_data, context_path, ns_to_prefix)
                json_bytes = orjson.dumps(output_data)
                self._write_jsonld_fast(json_bytes, relevant_path)

        return list(relevant_paths.keys())

    def _store_graphs_in_file_jsonld_fast(self, file_path: str, context_path: str | None) -> None:
        doc = _JsonLdDoc([])
        for entity in self.a_set.res_to_entity.values():
            if len(entity.g) > 0:
                graph_iri = entity.g.identifier
                doc.upsert_entity(graph_iri, entity.res, _entity_to_jsonld_dict(entity))

        output_data: list[dict] | dict = doc.to_list()
        if context_path is not None and context_path in self.context_map:
            ns_to_prefix = self._build_ns_to_prefix(context_path)
            output_data = _compact_jsonld(output_data, context_path, ns_to_prefix)
        json_bytes = orjson.dumps(output_data)
        self._write_jsonld_fast(json_bytes, file_path)

    def upload_and_store(self, base_dir: str, triplestore_url: str, base_iri: str, context_path: str | None = None,
                         batch_size: int = 10) -> None:
        stored_graph_path: List[str] = self.store_all(base_dir, base_iri, context_path)

        # If some graphs were not stored properly, then no one will be uploaded to the triplestore
        # Anyway, we should highlight those ones that could have been added in principle, by
        # mentioning them with a ".notuploaded" marker
        if None in stored_graph_path:
            for file_path in stored_graph_path:
                if file_path is not None:
                    # Create a marker for the file not uploaded in the triplestore
                    open(f'{file_path}.notuploaded', 'wt', encoding='utf-8').close()
                    self.reperr.add_sentence("[2] "
                                             f"The statements contained in the JSON-LD file '{file_path}' "
                                             "were not uploaded into the triplestore.")
        else:  # All the files have been stored
            self.upload_all(triplestore_url, base_dir, batch_size)

    def _dir_and_file_paths(self, res: URIRef, base_dir: str, base_iri: str, process_id: int | str | None = None) -> Tuple[str, str]:
        is_json: bool = (self.output_format == "json-ld")
        return find_paths(res, base_dir, base_iri, self.default_dir, self.dir_split, self.n_file_item, is_json=is_json, process_id=process_id)

    @staticmethod
    def _class_to_entity_type(entity: AbstractEntity) -> str:
        if isinstance(entity, GraphEntity):
            return "graph"
        elif isinstance(entity, ProvEntity):
            return "prov"
        else:
            return "metadata"

    def upload_all(self, triplestore_url: str, base_dir: str | None = None, batch_size: int = 10,
                   save_queries: bool = False) -> bool:
        """
        Upload SPARQL update queries to the triplestore in batches, or save them to disk.

        Args:
            triplestore_url: SPARQL endpoint URL
            base_dir: Base directory for output files (required when save_queries is True)
            batch_size: Number of queries per SPARQL batch
            save_queries: If True, save combined SPARQL queries to disk instead of uploading

        Returns:
            True if all batches were processed successfully, False otherwise
        """
        self.repok.new_article()
        self.reperr.new_article()

        if batch_size <= 0:
            batch_size = 10

        query_batch: list = []
        added_statements: int = 0
        removed_statements: int = 0
        result: bool = True
        to_be_uploaded_dir: str = ""

        if base_dir:
            to_be_uploaded_dir = os.path.join(base_dir, "to_be_uploaded")
            os.makedirs(to_be_uploaded_dir, exist_ok=True)

        entities_to_process = self.a_set.res_to_entity.values()
        if self.modified_entities is not None:
            entities_to_process = [
                entity for entity in entities_to_process
                if str(entity.res).split('/prov/se/')[0] in self.modified_entities
            ]

        for entity in entities_to_process:
            entity_type = self._class_to_entity_type(entity)
            update_queries, n_added, n_removed = get_update_query(entity, entity_type=entity_type)

            if not update_queries:
                continue

            for query in update_queries:
                query_batch.append(query)
                added_statements += n_added // len(update_queries)
                removed_statements += n_removed // len(update_queries)

                if len(query_batch) >= batch_size:
                    query_string = " ; ".join(query_batch)
                    if save_queries:
                        self._save_query(query_string, to_be_uploaded_dir, added_statements, removed_statements)
                    else:
                        result &= self._query(query_string, triplestore_url, base_dir, added_statements, removed_statements)
                    query_batch = []
                    added_statements = 0
                    removed_statements = 0

        if query_batch:
            query_string = " ; ".join(query_batch)
            if save_queries:
                self._save_query(query_string, to_be_uploaded_dir, added_statements, removed_statements)
            else:
                result &= self._query(query_string, triplestore_url, base_dir, added_statements, removed_statements)

        return result

    def _save_query(self, query_string: str, directory: str, added_statements: int, removed_statements: int) -> None:
        content_hash = hashlib.sha256(query_string.encode('utf-8')).hexdigest()[:16]
        file_name = f"{content_hash}_add{added_statements}_remove{removed_statements}.sparql"
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(query_string)

    def upload(self, entity: AbstractEntity, triplestore_url: str, base_dir: str | None = None) -> bool:
        self.repok.new_article()
        self.reperr.new_article()

        entity_type = self._class_to_entity_type(entity)
        update_queries, n_added, n_removed = get_update_query(entity, entity_type=entity_type)
        query_string = " ; ".join(update_queries) if update_queries else ""
        return self._query(query_string, triplestore_url, base_dir, n_added, n_removed)

    def execute_query(self, query_string: str, triplestore_url: str) -> bool:
        self.repok.new_article()
        self.reperr.new_article()

        return self._query(query_string, triplestore_url)

    def _query(self, query_string: str, triplestore_url: str, base_dir: str | None = None,
            added_statements: int = 0, removed_statements: int = 0) -> bool:
        if query_string != "":
            try:
                sparql_update(triplestore_url, query_string, max_retries=3, backoff_factor=2.5)

                self.repok.add_sentence(
                    f"Triplestore updated with {added_statements} added statements and "
                    f"with {removed_statements} removed statements.")

                return True

            except SPARQLEndpointError as e:
                self.reperr.add_sentence("[3] "
                                        "Graph was not loaded into the "
                                        f"triplestore due to communication problems: {e}")
                if base_dir is not None:
                    tp_err_dir: str = base_dir + os.sep + "tp_err"
                    if not os.path.exists(tp_err_dir):
                        os.makedirs(tp_err_dir, exist_ok=True)
                    cur_file_err: str = tp_err_dir + os.sep + \
                        datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f_not_uploaded.txt')
                    with open(cur_file_err, 'wt', encoding='utf-8') as f:
                        f.write(query_string)

        return False