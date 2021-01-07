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

from SPARQLWrapper import SPARQLWrapper
from typing import TYPE_CHECKING

from oc_ocdm.prov.prov_entity import ProvEntity
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.metadata.metadata_entity import MetadataEntity
from oc_ocdm.reader import Reader
from oc_ocdm.support.query_utils import get_update_query

if TYPE_CHECKING:
    from typing import Dict, List, Tuple, Any, Optional, Type
    from rdflib import URIRef
    from oc_ocdm.abstract_entity import AbstractEntity
    from oc_ocdm.abstract_set import AbstractSet

from oc_ocdm.support.reporter import Reporter
import os
from rdflib import ConjunctiveGraph
import json
from datetime import datetime
import io
from oc_ocdm.support.support import find_paths


class Storer(object):

    def __init__(self, abstract_set: AbstractSet, repok: Reporter = None, reperr: Reporter = None,
                 context_map: Dict[str, Any] = None, default_dir: str = "_", dir_split: int = 0,
                 n_file_item: int = 1, output_format: str = "json-ld") -> None:
        self.output_format: str = output_format
        self.dir_split: int = dir_split
        self.n_file_item: int = n_file_item
        self.default_dir: str = default_dir
        self.a_set: AbstractSet = abstract_set

        if context_map is not None:
            self.context_map: Dict[str, Any] = context_map
        else:
            self.context_map: Dict[str, Any] = {}

        if self.output_format == "json-ld":
            for context_url in self.context_map:
                ctx_file_path: Any = self.context_map[context_url]
                if type(ctx_file_path) == str and os.path.isfile(ctx_file_path):
                    # This expensive operation is done only when it's really needed
                    with open(ctx_file_path, "rt") as ctx_f:
                        self.context_map[context_url] = json.load(ctx_f)

        if repok is None:
            self.repok: Reporter = Reporter(prefix="[Storer: INFO] ")
        else:
            self.repok: Reporter = repok

        if reperr is None:
            self.reperr: Reporter = Reporter(prefix="[Storer: ERROR] ")
        else:
            self.reperr: Reporter = reperr

    def store_graphs_in_file(self, file_path: str, context_path: str) -> None:
        self.repok.new_article()
        self.reperr.new_article()
        self.repok.add_sentence("Store the graphs into a file: starting process")

        cg: ConjunctiveGraph = ConjunctiveGraph()
        for g in self.a_set.graphs():
            cg.addN([item + (g.identifier,) for item in list(g)])

        self.__store_in_file(cg, file_path, context_path)

    def __store_in_file(self, cur_g: ConjunctiveGraph, cur_file_path: str, context_path: str) -> None:
        # Note: the following lines from here and until 'cur_json_ld' are a sort of hack for including all
        # the triples of the input graph into the final stored file. Some how, some of them are not written
        # in such file otherwise - in particular the provenance ones.
        new_g: ConjunctiveGraph = ConjunctiveGraph()
        for s, p, o in cur_g.triples((None, None, None)):
            g_iri: Optional[URIRef] = None
            for g_context in cur_g.contexts((s, p, o)):
                g_iri = g_context.identifier
                break

            new_g.addN([(s, p, o, g_iri)])

        if self.output_format == "json-ld" and context_path in self.context_map:
            cur_json_ld: Any = json.loads(
                new_g.serialize(format="json-ld", context=self.context_map[context_path]).decode("utf-8"))

            if isinstance(cur_json_ld, dict):
                cur_json_ld["@context"] = context_path
            else:  # it is a list
                for item in cur_json_ld:
                    item["@context"] = context_path

            with open(cur_file_path, "wt", encoding='utf-8') as f:
                json.dump(cur_json_ld, f, indent=4, ensure_ascii=False)
        elif self.output_format == "nt11":
            new_g.serialize(cur_file_path, format="nt11", encoding="utf-8")
        elif self.output_format == "nquads":
            new_g.serialize(cur_file_path, format="nquads", encoding="utf-8")

        self.repok.add_sentence(f"File '{cur_file_path}' added.")

    def store_all(self, base_dir: str, base_iri: str, context_path: str) -> List[str]:
        self.repok.new_article()
        self.reperr.new_article()

        self.repok.add_sentence("Starting the process")

        processed_graphs: Dict[str, ConjunctiveGraph] = {}
        for entity in self.a_set.res_to_entity.values():
            processed_graphs = self.store(entity, base_dir, base_iri, context_path,
                                          processed_graphs, False)

        stored_graph_path: List[str] = []
        for cur_file_path in processed_graphs:
            stored_graph_path.append(cur_file_path)
            self.__store_in_file(processed_graphs[cur_file_path], cur_file_path, context_path)

        return stored_graph_path

    def store(self, entity: AbstractEntity, base_dir: str, base_iri: str, context_path: str,
              already_processed: Dict[str, ConjunctiveGraph] = None,
              store_now: bool = True) -> Optional[Dict[str, ConjunctiveGraph]]:
        self.repok.new_article()
        self.reperr.new_article()

        if already_processed is None:
            already_processed: Dict[str, ConjunctiveGraph] = {}

        cur_dir_path, cur_file_path = self._dir_and_file_paths(entity.res, base_dir, base_iri)

        try:
            if not os.path.exists(cur_dir_path):
                os.makedirs(cur_dir_path)

            stored_g: Optional[ConjunctiveGraph] = None

            # Here we try to obtain a reference to the currently stored graph
            if cur_file_path in already_processed:
                stored_g = already_processed[cur_file_path]
            elif os.path.exists(cur_file_path):
                stored_g = Reader(self.repok, self.reperr, self.context_map).load(cur_file_path)

            if stored_g is None:
                stored_g = ConjunctiveGraph()

            if isinstance(entity, ProvEntity):
                quads: List[Tuple] = []
                graph_identifier: URIRef = entity.g.identifier
                for triple in entity.g.triples((None, None, None)):
                    quads.append((*triple, graph_identifier))
                stored_g.addN(quads)
            elif isinstance(entity, GraphEntity) or isinstance(entity, MetadataEntity):
                if entity.to_be_deleted:
                    stored_g.remove((entity.res, None, None, None))
                else:
                    if len(entity.preexisting_graph) > 0:
                        """
                        We're not in 'append mode', so we need to remove
                        the entity that we're going to overwrite.
                        """
                        stored_g.remove((entity.res, None, None, None))
                    """
                    Here we copy data from the entity into the stored graph.
                    If the entity was marked as to be deleted, then we're
                    done because we already removed all of its triples.
                    """
                    quads: List[Tuple] = []
                    graph_identifier: URIRef = entity.g.identifier
                    for triple in entity.g.triples((None, None, None)):
                        quads.append((*triple, graph_identifier))
                    stored_g.addN(quads)

            # We must ensure that the graph is correctly stored in our cache
            if cur_file_path not in already_processed:
                already_processed[cur_file_path] = stored_g

            if store_now:
                self.__store_in_file(stored_g, cur_file_path, context_path)

            return already_processed
        except Exception as e:
            self.reperr.add_sentence(f"[5] It was impossible to store the RDF statements in {cur_file_path}. {e}")

    def upload_and_store(self, base_dir: str, triplestore_url: str, base_iri: str, context_path: str,
                         tmp_dir: str = None) -> None:
        stored_graph_path: List[str] = self.store_all(base_dir, base_iri, context_path, tmp_dir)

        # If some graphs were not stored properly, then no one will be uploaded to the triplestore
        # Anyway, we should highlight those ones that could have been added in principle, by
        # mentioning them with a ".notupdloaded" marker
        if None in stored_graph_path:
            for file_path in stored_graph_path:
                if file_path is not None:
                    # Create a marker for the file not uploaded in the triplestore
                    open(f"{file_path}.notuploaded", "wt").close()
                    self.reperr.add_sentence("[6] "
                                             f"The statements contained in the JSON-LD file '{file_path}' "
                                             "were not uploaded into the triplestore.")
        else:  # All the files have been stored
            self.upload_all(triplestore_url, base_dir)

    def _dir_and_file_paths(self, res: URIRef, base_dir: str, base_iri: str) -> Tuple[str, str]:
        is_json: bool = (self.output_format == "json-ld")
        return find_paths(
            str(res), base_dir, base_iri, self.default_dir, self.dir_split, self.n_file_item, is_json=is_json)

    def upload_all(self, triplestore_url: str, base_dir: str = None, batch_size: int = 10) -> bool:
        self.repok.new_article()
        self.reperr.new_article()

        if batch_size <= 0:
            batch_size = 10

        query_string: str = ""
        added_statements: int = 0
        removed_statements: int = 0
        result: bool = True
        class_to_entity_type: Dict[Type, str] = {
            GraphEntity: "graph",
            ProvEntity: "prov",
            MetadataEntity: "metadata"
        }
        for idx, entity in enumerate(self.a_set.res_to_entity.values()):
            update_query, n_added, n_removed = get_update_query(entity, entity_type=class_to_entity_type[type(entity)])

            if idx % batch_size == 0:
                query_string = update_query
                added_statements = n_added
                removed_statements = n_removed
            else:
                if update_query != "":
                    if query_string != "":
                        query_string += " ; "
                    query_string += update_query
                added_statements += n_added
                removed_statements += n_removed

            if idx > 0 and idx % batch_size == 0:
                result &= self._query(query_string, triplestore_url, base_dir, added_statements, removed_statements)
                query_string = ""

        if query_string != "":
            result &= self._query(query_string, triplestore_url, base_dir, added_statements, removed_statements)

        return result

    def upload(self, entity: AbstractEntity, triplestore_url: str, base_dir: str = None) -> bool:
        self.repok.new_article()
        self.reperr.new_article()

        class_to_entity_type: Dict[Type, str] = {
            GraphEntity: "graph",
            ProvEntity: "prov",
            MetadataEntity: "metadata"
        }
        update_query, n_added, n_removed = get_update_query(entity, entity_type=class_to_entity_type[type(entity)])

        return self._query(update_query, triplestore_url, base_dir, n_added, n_removed)

    def execute_query(self, query_string: str, triplestore_url: str) -> bool:
        self.repok.new_article()
        self.reperr.new_article()

        return self._query(query_string, triplestore_url)

    def _query(self, query_string: str, triplestore_url: str, base_dir: str = None,
               added_statements: int = 0, removed_statements: int = 0) -> bool:
        if query_string != "":
            try:
                tp: SPARQLWrapper = SPARQLWrapper(triplestore_url)
                tp.setMethod('POST')
                tp.setQuery(query_string)
                tp.query()

                self.repok.add_sentence(
                    f"Triplestore updated with {added_statements} added statements and "
                    f"with {removed_statements} removed statements.")

                return True

            except Exception as e:
                self.reperr.add_sentence("[1] "
                                         "Graph was not loaded into the "
                                         f"triplestore due to communication problems: {e}")
                if base_dir is not None:
                    tp_err_dir: str = base_dir + os.sep + "tp_err"
                    if not os.path.exists(tp_err_dir):
                        os.makedirs(tp_err_dir)
                    cur_file_err: str = tp_err_dir + os.sep + \
                                        datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f_not_uploaded.txt')
                    with io.open(cur_file_err, "w", encoding="utf-8") as f:
                        f.write(query_string)

        return False
