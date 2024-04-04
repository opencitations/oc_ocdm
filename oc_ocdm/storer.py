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
from datetime import datetime
from typing import TYPE_CHECKING
from zipfile import ZIP_DEFLATED, ZipFile

from rdflib import ConjunctiveGraph
from SPARQLWrapper import SPARQLWrapper

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.metadata.metadata_entity import MetadataEntity
from oc_ocdm.prov.prov_entity import ProvEntity
from oc_ocdm.reader import Reader
from oc_ocdm.support.query_utils import get_update_query
from oc_ocdm.support.reporter import Reporter
from oc_ocdm.support.support import find_paths
from filelock import FileLock

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Set, Tuple

    from rdflib import URIRef

    from oc_ocdm.abstract_entity import AbstractEntity
    from oc_ocdm.abstract_set import AbstractSet


class Storer(object):

    def __init__(self, abstract_set: AbstractSet, repok: Reporter = None, reperr: Reporter = None,
                 context_map: Dict[str, Any] = None, default_dir: str = "_", dir_split: int = 0,
                 n_file_item: int = 1, output_format: str = "json-ld", zip_output: bool = False, modified_entities: set = None) -> None:
        # We only accept format strings that:
        # 1. are supported by rdflib
        # 2. correspond to an output format which is effectively either NT or NQ
        # The only exception to this rule is the 'json-ld' format, which is the default value of 'output_format'.
        supported_formats: Set[str] = {'application/n-triples', 'ntriples', 'nt', 'nt11',
                                       'application/n-quads', 'nquads', 'json-ld'}
        if output_format not in supported_formats:
            raise ValueError(f"Given output_format '{self.output_format}' is not supported."
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

    def store_graphs_in_file(self, file_path: str, context_path: str = None) -> None:
        self.repok.new_article()
        self.reperr.new_article()
        self.repok.add_sentence("Store the graphs into a file: starting process")

        cg: ConjunctiveGraph = ConjunctiveGraph()
        for g in self.a_set.graphs():
            cg.addN([item + (g.identifier,) for item in list(g)])

        self._store_in_file(cg, file_path, context_path)

    def _store_in_file(self, cur_g: ConjunctiveGraph, cur_file_path: str, context_path: str = None) -> None:
        # Note: the following lines from here and until 'cur_json_ld' are a sort of hack for including all
        # the triples of the input graph into the final stored file. Somehow, some of them are not written
        # in such file otherwise - in particular the provenance ones.
        new_g: ConjunctiveGraph = ConjunctiveGraph()
        for s, p, o in cur_g.triples((None, None, None)):
            g_iri: Optional[URIRef] = None
            for g_context in cur_g.contexts((s, p, o)):
                g_iri = g_context.identifier
                break
            new_g.addN([(s, p, o, g_iri)])

        zip_file_path = cur_file_path.replace(os.path.splitext(cur_file_path)[1], ".zip")
        
        if self.zip_output:
            with ZipFile(zip_file_path, mode="w", compression=ZIP_DEFLATED, allowZip64=True) as zip_file:
                self._write_graph(new_g, zip_file, cur_file_path, context_path)
        else:
            # Handle non-zipped output directly to a file
            self._write_graph(new_g, None, cur_file_path, context_path)

        self.repok.add_sentence(f"File '{cur_file_path}' added.")

    def _write_graph(self, graph: ConjunctiveGraph, zip_file: ZipFile, cur_file_path, context_path):
        if self.output_format == "json-ld":
            # Serialize the graph in JSON-LD format
            cur_json_ld = json.loads(graph.serialize(format="json-ld", context=self.context_map.get(context_path)))
            if context_path is not None and context_path in self.context_map:
                if isinstance(cur_json_ld, dict):
                    cur_json_ld["@context"] = context_path
                else:  # When cur_json_ld is a list
                    for item in cur_json_ld:
                        item["@context"] = context_path

            # Determine how to write based on zip file presence
            if zip_file is not None:
                dumped_json = json.dumps(cur_json_ld, ensure_ascii=False).encode('utf-8')
                zip_file.writestr(zinfo_or_arcname=os.path.basename(cur_file_path), data=dumped_json)
            else:
                with open(cur_file_path, 'wt', encoding='utf-8') as f:
                    json.dump(cur_json_ld, f, ensure_ascii=False)
        else:
            # Handle other RDF formats
            if zip_file is not None:
                rdf_serialization = graph.serialize(destination=None, format=self.output_format, encoding="utf-8")
                zip_file.writestr(zinfo_or_arcname=os.path.basename(cur_file_path), data=rdf_serialization)
            else:
                graph.serialize(destination=cur_file_path, format=self.output_format, encoding="utf-8")

    def store_all(self, base_dir: str, base_iri: str, context_path: str = None, process_id: int|str = None) -> List[str]:
        self.repok.new_article()
        self.reperr.new_article()

        self.repok.add_sentence("Starting the process")

        relevant_paths: Dict[str, list] = dict()
        for entity in self.a_set.res_to_entity.values():
            is_relevant = True
            if self.modified_entities is not None and entity.res not in self.modified_entities:
                is_relevant = False
            if is_relevant:
                cur_dir_path, cur_file_path = self._dir_and_file_paths(entity.res, base_dir, base_iri, process_id)
                if not os.path.exists(cur_dir_path):
                    os.makedirs(cur_dir_path)
                relevant_paths.setdefault(cur_file_path, list())
                relevant_paths[cur_file_path].append(entity)

        for relevant_path, entities_in_path in relevant_paths.items():
            stored_g = None
            # Here we try to obtain a reference to the currently stored graph
            output_filepath = relevant_path.replace(os.path.splitext(relevant_path)[1], ".zip") if self.zip_output else relevant_path
            lock = FileLock(f"{output_filepath}.lock")
            with lock:
                if os.path.exists(output_filepath):
                    stored_g = Reader(context_map=self.context_map).load(output_filepath)
                if stored_g is None:
                    stored_g = ConjunctiveGraph()
                for entity_in_path in entities_in_path:
                    self.store(entity_in_path, stored_g, relevant_path, context_path, False)
                self._store_in_file(stored_g, relevant_path, context_path)

        return list(relevant_paths.keys())

    def store(self, entity: AbstractEntity, destination_g: ConjunctiveGraph, cur_file_path: str, context_path: str = None, store_now: bool = True) -> ConjunctiveGraph:
        self.repok.new_article()
        self.reperr.new_article()

        try:
            if isinstance(entity, ProvEntity):
                quads: List[Tuple] = []
                graph_identifier: URIRef = entity.g.identifier
                for triple in entity.g.triples((entity.res, None, None)):
                    quads.append((*triple, graph_identifier))
                destination_g.addN(quads)
            elif isinstance(entity, GraphEntity) or isinstance(entity, MetadataEntity):
                if entity.to_be_deleted:
                    destination_g.remove((entity.res, None, None, None))
                else:
                    if len(entity.preexisting_graph) > 0:
                        """
                        We're not in 'append mode', so we need to remove
                        the entity that we're going to overwrite.
                        """
                        destination_g.remove((entity.res, None, None, None))
                    """
                    Here we copy data from the entity into the stored graph.
                    If the entity was marked as to be deleted, then we're
                    done because we already removed all of its triples.
                    """
                    quads: List[Tuple] = []
                    graph_identifier: URIRef = entity.g.identifier
                    for triple in entity.g.triples((entity.res, None, None)):
                        quads.append((*triple, graph_identifier))
                    destination_g.addN(quads)

            if store_now:
                self._store_in_file(destination_g, cur_file_path, context_path)

            return destination_g
        except Exception as e:
            self.reperr.add_sentence(f"[1] It was impossible to store the RDF statements in {cur_file_path}. {e}")

    def upload_and_store(self, base_dir: str, triplestore_url: str, base_iri: str, context_path: str = None,
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

    def _dir_and_file_paths(self, res: URIRef, base_dir: str, base_iri: str, process_id: int|str = None) -> Tuple[str, str]:
        is_json: bool = (self.output_format == "json-ld")
        return find_paths(res, base_dir, base_iri, self.default_dir, self.dir_split, self.n_file_item, is_json=is_json, process_id=process_id)

    @staticmethod
    def _class_to_entity_type(entity: AbstractEntity) -> Optional[str]:
        if isinstance(entity, GraphEntity):
            return "graph"
        elif isinstance(entity, ProvEntity):
            return "prov"
        elif isinstance(entity, MetadataEntity):
            return "metadata"
        else:
            return None

    def upload_all(self, triplestore_url: str, base_dir: str = None, batch_size: int = 10) -> bool:
        self.repok.new_article()
        self.reperr.new_article()

        if batch_size <= 0:
            batch_size = 10

        query_string: str = ""
        added_statements: int = 0
        removed_statements: int = 0
        skipped_queries: int = 0
        result: bool = True

        for idx, entity in enumerate(self.a_set.res_to_entity.values()):
            update_query, n_added, n_removed = get_update_query(entity, entity_type=self._class_to_entity_type(entity))

            if update_query == "":
                skipped_queries += 1
            else:
                index = idx - skipped_queries
                if index == 0:
                    # First query
                    query_string = update_query
                    added_statements = n_added
                    removed_statements = n_removed
                elif index % batch_size == 0:
                    # batch_size-multiple query
                    result &= self._query(query_string, triplestore_url, base_dir, added_statements, removed_statements)
                    query_string = update_query
                    added_statements = n_added
                    removed_statements = n_removed
                else:
                    # Accumulated query
                    query_string += " ; " + update_query
                    added_statements += n_added
                    removed_statements += n_removed

        if query_string != "":
            result &= self._query(query_string, triplestore_url, base_dir, added_statements, removed_statements)

        return result

    def upload(self, entity: AbstractEntity, triplestore_url: str, base_dir: str = None) -> bool:
        self.repok.new_article()
        self.reperr.new_article()

        update_query, n_added, n_removed = get_update_query(entity, entity_type=self._class_to_entity_type(entity))

        return self._query(update_query, triplestore_url, base_dir, n_added, n_removed)

    def execute_query(self, query_string: str, triplestore_url: str) -> bool:
        self.repok.new_article()
        self.reperr.new_article()

        return self._query(query_string, triplestore_url)

    def _query(self, query_string: str, triplestore_url: str, base_dir: str = None,
               added_statements: int = 0, removed_statements: int = 0) -> bool:
        if query_string != "":
            try:
                sparql: SPARQLWrapper = SPARQLWrapper(triplestore_url)
                sparql.setQuery(query_string)
                sparql.setMethod('POST')

                sparql.query()

                self.repok.add_sentence(
                    f"Triplestore updated with {added_statements} added statements and "
                    f"with {removed_statements} removed statements.")

                return True

            except Exception as e:
                self.reperr.add_sentence("[3] "
                                         "Graph was not loaded into the "
                                         f"triplestore due to communication problems: {e}")
                if base_dir is not None:
                    tp_err_dir: str = base_dir + os.sep + "tp_err"
                    if not os.path.exists(tp_err_dir):
                        os.makedirs(tp_err_dir)
                    cur_file_err: str = tp_err_dir + os.sep + \
                        datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f_not_uploaded.txt')
                    with open(cur_file_err, 'wt', encoding='utf-8') as f:
                        f.write(query_string)

        return False