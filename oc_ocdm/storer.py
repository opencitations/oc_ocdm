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

from SPARQLWrapper import SPARQLWrapper
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from typing import Dict, List, Set, Tuple, Any, Callable, Optional
    from rdflib import Graph, URIRef
    from oc_ocdm import GraphSet

from oc_ocdm.support import Reporter
import os
from rdflib import BNode, ConjunctiveGraph
import shutil
import json
from datetime import datetime
import io
from oc_ocdm.support import find_paths
from rdflib.term import _toPythonMapping
from rdflib import XSD


class Storer(object):

    def __init__(self, graph_set: GraphSet = None, repok: Reporter = None, reperr: Reporter = None,
                 context_map: Dict[str, Any] = None, default_dir: str = "_", dir_split: int = 0, n_file_item: int = 1,
                 nt: bool = False, nq: bool = False) -> None:
        self.nt: bool = nt
        self.nq: bool = nq
        self.dir_split: int = dir_split
        self.n_file_item: int = n_file_item
        self.default_dir: str = default_dir
        self.preface_query: str = ""

        if not nt and not nq:
            if context_map is not None:
                self.context_map: Dict[str, Any] = context_map
            else:
                self.context_map: Dict[str, Any] = {}
            for context_url in context_map:
                ctx_file_path = context_map[context_url]
                with open(ctx_file_path) as ctx_f:
                    context_json: Any = json.load(ctx_f)
                    self.context_map[context_url] = context_json

        if graph_set is None:
            self.g: List[Graph] = []
        else:
            self.g: List[Graph] = graph_set.graphs()

        if repok is None:
            self.repok: Reporter = Reporter(prefix="[Storer: INFO] ")
        else:
            self.repok: Reporter = repok

        if reperr is None:
            self.reperr: Reporter = Reporter(prefix="[Storer: ERROR] ")
        else:
            self.reperr: Reporter = reperr

    @staticmethod
    def hack_dates() -> None:
        if XSD.gYear in _toPythonMapping:
            _toPythonMapping.pop(XSD.gYear)
        if XSD.gYearMonth in _toPythonMapping:
            _toPythonMapping.pop(XSD.gYearMonth)

    def store_graphs_in_file(self, file_path: str, context_path: str) -> None:
        self.repok.new_article()
        self.reperr.new_article()
        self.repok.add_sentence("Store the graphs into a file: starting process")

        cg: ConjunctiveGraph = ConjunctiveGraph()
        for g in self.g:
            cg.addN([item + (g.identifier,) for item in list(g)])

        self.__store_in_file(cg, file_path, context_path)

    def store_all(self, base_dir: str, base_iri: str, context_path: str, tmp_dir: str = None,
                  g_set: List[Graph] = None, override: bool = False, remove_data: bool = False):
        if g_set is None:
            g_set: List[Graph] = []
        for g in g_set:
            self.g += [g]

        self.repok.new_article()
        self.reperr.new_article()

        self.repok.add_sentence("Starting the process")

        processed_graphs: Dict[str, ConjunctiveGraph] = {}
        for cur_g in self.g:
            processed_graphs = self.store(cur_g, base_dir, base_iri, context_path, tmp_dir,
                                          override, processed_graphs, False, remove_data)

        stored_graph_path: List[str] = []
        for cur_file_path in processed_graphs:
            stored_graph_path += [cur_file_path]

            self.__store_in_file(processed_graphs[cur_file_path], cur_file_path, context_path)

        return stored_graph_path

    def upload_and_store(self, base_dir: str, triplestore_url: str, base_iri: str, context_path: str,
                         tmp_dir: str = None, g_set: List[Graph] = None, override: bool = False) -> None:
        if g_set is None:
            g_set: List[Graph] = []
        stored_graph_path: List[str] = self.store_all(base_dir, base_iri, context_path, tmp_dir, g_set, override)

        # Some graphs were not stored properly, then no one will be uploaded to the triplestore
        # but we highlights those ones that could be added in principle, by mentioning them
        # with a ".notupdloaded" marker
        if None in stored_graph_path:
            for file_path in stored_graph_path:
                # Create a marker for the file not uploaded in the triplestore
                open(f"{file_path}.notuploaded", "w").close()
                self.reperr.add_sentence("[6] "
                                         f"The statements of in the JSON-LD file '{file_path}' were not "
                                         "uploaded into the triplestore.")
        else:  # All the files have been stored
            self.upload_all(self.g, triplestore_url, base_dir)

    def query(self, query_string: str, triplestore_url: str, n_statements: int = None, base_dir: str = None) -> bool:
        if query_string != "":
            try:
                tp: SPARQLWrapper = SPARQLWrapper(triplestore_url)
                tp.setMethod('POST')
                tp.setQuery(query_string)
                tp.query()

                if n_statements is None:
                    self.repok.add_sentence(
                        "Triplestore updated by means of a SPARQL Update query.")
                else:
                    self.repok.add_sentence(
                        f"Triplestore updated with {n_statements} more RDF statements.")

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

    def _do_action_all(self, all_g: List[Graph], triplestore_url: str, base_dir: str,
                       query_f: Callable[[Graph], str]) -> bool:
        result: bool = True

        self.repok.new_article()
        self.reperr.new_article()

        query_string: Optional[str] = None
        total_new_statements: Optional[int] = None

        for idx, cur_g in enumerate(all_g):
            cur_idx: int = idx % 10
            if cur_idx == 0:
                if query_string is not None:
                    result &= self.query(query_string, triplestore_url, total_new_statements, base_dir)
                query_string = ""
                total_new_statements = 0
            else:
                query_string += " ; "
                total_new_statements += len(cur_g)

            query_string += self.get_preface_query(cur_g) + query_f(cur_g)

        if query_string is not None and query_string != "":
            result &= self.query(query_string, triplestore_url, total_new_statements, base_dir)

        return result

    def update_all(self, all_add_g: List[Graph], all_remove_g: List[Graph], triplestore_url: str,
                   base_dir: str) -> bool:
        return self._do_action_all(all_remove_g, triplestore_url, base_dir, Storer._make_delete_query) and \
               self.upload_all(all_add_g, triplestore_url, base_dir)

    def upload_all(self, all_g: List[Graph], triplestore_url: str, base_dir: str) -> bool:
        return self._do_action_all(all_g, triplestore_url, base_dir, Storer._make_insert_query)

    def execute_upload_query(self, query_string: str, triplestore_url: str) -> bool:
        self.repok.new_article()
        self.reperr.new_article()

        return self.query(query_string, triplestore_url)

    def upload(self, cur_g: Graph, triplestore_url: str) -> bool:
        self.repok.new_article()
        self.reperr.new_article()

        query_string: str = Storer._make_insert_query(cur_g)

        return self.query(query_string, triplestore_url, len(cur_g))

    def set_preface_query(self, query_string: str) -> None:
        self.preface_query = query_string

    def get_preface_query(self, cur_g: Graph) -> str:
        if self.preface_query != "":
            if type(cur_g.identifier) is BNode:
                return "CLEAR DEFAULT ; "
            else:
                return "WITH <%s> " % str(cur_g.identifier) + self.preface_query + " ; "
        else:
            return ""

    @staticmethod
    def _make_insert_query(cur_g: Graph) -> str:
        return Storer.__make_query(cur_g, "INSERT")

    @staticmethod
    def _make_delete_query(cur_g: Graph) -> str:
        return Storer.__make_query(cur_g, "DELETE")

    @staticmethod
    def __make_query(cur_g: Graph, query_type: str = "INSERT") -> str:
        if type(cur_g.identifier) is BNode:
            return f"{query_type} DATA {{ {cur_g.serialize(format='nt11', encoding='utf-8').decode('utf-8')} }}"
        else:
            return f"{query_type} DATA {{ GRAPH <{cur_g.identifier}> " \
                   f"{{ {cur_g.serialize(format='nt11', encoding='utf-8').decode('utf-8')} }}" \
                   f" }}"

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

        if not self.nt and not self.nq and context_path:
            cur_json_ld: Any = json.loads(
                new_g.serialize(format="json-ld", context=self.__get_context(context_path)).decode("utf-8"))

            if isinstance(cur_json_ld, dict):
                cur_json_ld["@context"] = context_path
            else:  # it is a list
                for item in cur_json_ld:
                    item["@context"] = context_path

            with open(cur_file_path, "w", encoding='utf8') as f:
                json.dump(cur_json_ld, f, indent=4, ensure_ascii=False)
        elif self.nt:
            new_g.serialize(cur_file_path, format="nt11", encoding="utf-8")
        elif self.nq:
            new_g.serialize(cur_file_path, format="nquads", encoding="utf-8")

        self.repok.add_sentence(f"File '{cur_file_path}' added.")

    def dir_and_file_paths(self, cur_g: Graph, base_dir: str, base_iri: str) -> Tuple[str, str]:
        cur_subject: Set[URIRef] = set(cur_g.subjects(None, None)).pop()
        if self.nt or self.nq:
            is_json: bool = False
        else:
            is_json: bool = True
        return find_paths(
            str(cur_subject), base_dir, base_iri, self.default_dir, self.dir_split, self.n_file_item, is_json=is_json)

    def update(self, add_g: ConjunctiveGraph, remove_g: Graph, base_dir: str, base_iri: str, context_path: str,
               tmp_dir: str = None, override: bool = False, already_processed: Dict[str, ConjunctiveGraph] = None,
               store_now: bool = True) -> Dict[str, ConjunctiveGraph]:
        self.repok.new_article()
        self.reperr.new_article()

        if already_processed is None:
            already_processed: Dict[str, ConjunctiveGraph] = {}
        if len(remove_g) > 0:
            cur_dir_path, cur_file_path = self.dir_and_file_paths(remove_g, base_dir, base_iri)

            if cur_file_path in already_processed:
                final_g: ConjunctiveGraph = already_processed[cur_file_path]
            elif os.path.exists(cur_file_path):
                # This is a conjunctive graph that contains all the triples (and graphs)
                # the file is actually defining - they could be more than those using
                # 'cur_subject' as subject.
                final_g: ConjunctiveGraph = self.load(cur_file_path, tmp_dir=tmp_dir)
                already_processed[cur_file_path] = final_g

            for s, p, o, g in [item + (remove_g.identifier,) for item in list(remove_g)]:
                # TODO: what if final_g is None?
                final_g.remove((s, p, o, g))

        if len(add_g) > 0:
            self.store(add_g, base_dir, base_iri, context_path, tmp_dir, override, already_processed, store_now)
        elif len(remove_g) > 0 and store_now:
            self.__store_in_file(final_g, cur_file_path, context_path)

        return already_processed

    def store(self, cur_g: Graph, base_dir: str, base_iri: str, context_path: str, tmp_dir: str = None,
              override: bool = False, already_processed: Dict[str, ConjunctiveGraph] = None, store_now: bool = True,
              remove_data: bool = False) -> Optional[dict[str, ConjunctiveGraph]]:
        self.repok.new_article()
        self.reperr.new_article()

        if already_processed is None:
            already_processed: Dict[str, ConjunctiveGraph] = {}
        if len(cur_g) > 0:
            cur_dir_path, cur_file_path = self.dir_and_file_paths(cur_g, base_dir, base_iri)

            try:
                if not os.path.exists(cur_dir_path):
                    os.makedirs(cur_dir_path)

                final_g: ConjunctiveGraph = ConjunctiveGraph()
                final_g.addN([item + (cur_g.identifier,) for item in list(cur_g)])

                # Remove the data
                if remove_data:
                    stored_g: Optional[ConjunctiveGraph] = None
                    if cur_file_path in already_processed:
                        stored_g = already_processed[cur_file_path]
                    elif os.path.exists(cur_file_path):
                        stored_g = self.load(cur_file_path, cur_g, tmp_dir)

                    for s, p, o, g in final_g.quads((None, None, None, None)):
                        stored_g.remove((s, p, o, g))

                    final_g = stored_g
                elif not override:  # Merging the data
                    if cur_file_path in already_processed:
                        stored_g: ConjunctiveGraph = already_processed[cur_file_path]
                        stored_g.addN(final_g.quads((None, None, None, None)))
                        final_g = stored_g
                    elif os.path.exists(cur_file_path):
                        # This is a conjunctive graph that contains all the triples (and graphs)
                        # the file is actually defining - they could be more than those using
                        # 'cur_subject' as subject.
                        final_g = self.load(cur_file_path, cur_g, tmp_dir)

                already_processed[cur_file_path] = final_g

                if store_now:
                    self.__store_in_file(final_g, cur_file_path, context_path)

                return already_processed
            except Exception as e:
                self.reperr.add_sentence(f"[5] It was impossible to store the RDF statements in {cur_file_path}. {e}")

        return None

    def __get_context(self, context_url: str) -> Union[Any, str]:
        if context_url in self.context_map:
            return self.context_map[context_url]
        else:
            # TODO: bug here? This function should return Optional[Any]
            return context_url

    def __get_first_context(self) -> Any:
        for context_url in self.context_map:
            return self.context_map[context_url]

    def load(self, rdf_file_path: str, cur_graph: Graph = None, tmp_dir: str = None) -> ConjunctiveGraph:
        self.repok.new_article()
        self.reperr.new_article()

        if os.path.isfile(rdf_file_path):
            Storer.hack_dates()
            # The line above has been added for handling gYear and gYearMonth correctly.
            # More info at https://github.com/RDFLib/rdflib/issues/806.

            try:
                cur_graph: ConjunctiveGraph = self.__load_graph(rdf_file_path, cur_graph)
            except IOError:
                if tmp_dir is not None:
                    current_file_path: str = tmp_dir + os.sep + "tmp_rdf_file.rdf"
                    shutil.copyfile(rdf_file_path, current_file_path)
                    try:
                        cur_graph: ConjunctiveGraph = self.__load_graph(current_file_path, cur_graph)
                    except IOError as e:
                        self.reperr.add_sentence("[2] "
                                                 "It was impossible to handle the format used for "
                                                 f"storing the file (stored in the temporary path) "
                                                 f"'{current_file_path}'. Additional details: {e}")
                    os.remove(current_file_path)
                else:
                    self.reperr.add_sentence("[3] "
                                             "It was impossible to try to load the file from the "
                                             f"temporary path '{rdf_file_path}' since that has not been specified in "
                                             "advance")
        else:
            self.reperr.add_sentence("[4] "
                                     f"The file specified ('{rdf_file_path}') doesn't exist.")

        return cur_graph

    def __load_graph(self, file_path: str, cur_graph: ConjunctiveGraph = None) -> ConjunctiveGraph:
        formats: List[str] = ["json-ld", "rdfxml", "turtle", "trig", "nt11", "nquads"]

        current_graph: ConjunctiveGraph = ConjunctiveGraph()

        if cur_graph is not None:
            current_graph.parse(data=cur_graph.serialize(format="trig"), format="trig")

        errors: str = ""
        for cur_format in formats:
            try:
                if cur_format == "json-ld":
                    with open(file_path) as f:
                        json_ld_file: Any = json.load(f)
                        if isinstance(json_ld_file, dict):
                            json_ld_file: List[Any] = [json_ld_file]

                        for json_ld_resource in json_ld_file:
                            # Trick to force the use of a pre-loaded context if the format
                            # specified is JSON-LD
                            if "@context" in json_ld_resource:
                                cur_context: str = json_ld_resource["@context"]
                                if cur_context in self.context_map:
                                    context_json: Any = self.__get_context(cur_context)["@context"]
                                    json_ld_resource["@context"] = context_json

                            current_graph.parse(data=json.dumps(json_ld_resource, ensure_ascii=False),
                                                format=cur_format)
                else:
                    current_graph.parse(file_path, format=cur_format)

                return current_graph
            except Exception as e:
                errors += f" | {e}"  # Try another format

        raise IOError("1", f"It was impossible to handle the format used for storing the file '{file_path}'{errors}")
