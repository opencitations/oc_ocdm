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

import os
from datetime import datetime
from typing import Optional, Tuple, List, Any, Set
from shutil import copymode, move
from tempfile import mkstemp

from typing.io import BinaryIO

from rdflib import Graph, ConjunctiveGraph, URIRef
from rdflib.compare import to_isomorphic, graph_diff, IsomorphicGraph
from rdflib.query import Result

from oc_ocdm.graph_entity import GraphEntity
from oc_ocdm.graph_set import GraphSet
from oc_ocdm.prov_entity import ProvEntity


class ProvSet(GraphSet):
    def __init__(self, prov_subj_graph_set: GraphSet, base_iri: str, context_path: str, default_dir: str, info_dir: str,
                 resource_finder: Any, dir_split: int, n_file_item: int, supplier_prefix: str, triplestore_url: str,
                 wanted_label: bool = True) -> None:
        super(ProvSet, self).__init__(base_iri, context_path, info_dir, n_file_item, supplier_prefix,
                                      wanted_label=wanted_label)
        self.rf: Any = resource_finder  # external class ResourceFinder from spacin
        self.dir_split: int = dir_split
        self.default_dir: str = default_dir
        if triplestore_url is None:
            self.ts: Optional[ConjunctiveGraph] = None
        else:
            self.triplestore_url: str = triplestore_url
            self.ts: Optional[ConjunctiveGraph] = ConjunctiveGraph('SPARQLUpdateStore')
            self.ts.open((triplestore_url, triplestore_url))

        self.all_subjects: Set[URIRef] = set()
        for cur_subj_g in prov_subj_graph_set.graphs():
            self.all_subjects.add(next(cur_subj_g.subjects(None, None)))
        self.resp: str = "SPACIN ProvSet"
        self.prov_g: GraphSet = prov_subj_graph_set

        if wanted_label:
            GraphSet.labels.update(
                {
                    "pa": "provenance agent",
                    "se": "snapshot of entity metadata"
                }
            )

    # Add resources related to provenance information

    def add_se(self, resp_agent: str = None, prov_subject: GraphEntity = None, res: URIRef = None) -> ProvEntity:
        return self._add_prov("se", ProvEntity.entity, res, resp_agent, prov_subject)

    def generate_provenance(self, resp_agent: Optional[str], c_time: float = None, do_insert: bool = True,
                            remove_entity: bool = False) -> None:
        time_string: str = '%Y-%m-%dT%H:%M:%S'
        if c_time is None:
            cur_time: str = datetime.now().strftime(time_string)
        else:
            cur_time: str = datetime.fromtimestamp(c_time).strftime(time_string)

        # Add all existing information for provenance agents
        self.rf.add_prov_triples_in_filesystem(self.base_iri)

        if resp_agent is None:
            resp_agent = self.cur_name
        # The 'all_subjects' set includes only the subject of the created graphs that
        # have at least some new triples to add
        for prov_subject in self.all_subjects:
            cur_subj: GraphEntity = self.prov_g.get_entity(prov_subject)

            # Load all provenance data of snapshots for that subject
            self.rf.add_prov_triples_in_filesystem(str(prov_subject), "se")
            last_snapshot: Optional[ProvEntity] = None
            last_snapshot_res: Optional[URIRef] = self.rf.retrieve_last_snapshot(prov_subject)
            if last_snapshot_res is not None:
                last_snapshot: ProvEntity = self.add_se(resp_agent, cur_subj, last_snapshot_res)
            # Snapshot
            cur_snapshot: ProvEntity = self.add_se(resp_agent, cur_subj)
            cur_snapshot.snapshot_of(cur_subj)
            cur_snapshot.create_generation_time(cur_time)
            if cur_subj.source is not None:
                cur_snapshot.has_primary_source(cur_subj.source)
            cur_snapshot.has_resp_agent(resp_agent)

            # Old snapshot
            if last_snapshot is None and do_insert:  # Create a new entity
                cur_snapshot.create_description("The entity '%s' has been created." % str(cur_subj.res))
            else:
                if self._are_added_triples(cur_subj):  # if diff != 0:
                    if do_insert:
                        update_query_data: Optional[str] = self._are_added_triples(cur_subj)
                        update_description: str = "The entity '%s' has been extended with new statements." \
                                                  % str(cur_subj.res)
                    else:
                        update_query_data: Optional[str] = self._create_delete_query(cur_subj.g)[0]
                        if remove_entity:
                            update_description: str = "The entity '%s' has been removed." % str(cur_subj.res)
                        else:
                            update_description: str = "Some data of the entity '%s' have been removed. " \
                                                      % str(cur_subj.res)

                    cur_snapshot.create_description(update_description)
                    cur_snapshot.create_update_query(update_query_data)

                # Note: due to previous processing errors, it would be possible that no snapshot has been created
                # in the past for an entity, even if the entity actually exists. In this case, since we have to modify
                # the entity somehow, we create a new modification snapshot here without linking explicitly with the
                # previous one – which does not (currently) exist. However, the common expectation is that such
                # missing snapshot situation cannot happen.
                if last_snapshot is not None:
                    cur_snapshot.derives_from(last_snapshot)
                    last_snapshot.create_invalidation_time(cur_time)
                    cur_snapshot.invalidates(last_snapshot)

                # Invalidate the new snapshot if the entity has been removed
                if remove_entity:
                    cur_snapshot.invalidates(cur_snapshot)
                    cur_snapshot.create_invalidation_time(cur_time)

    @staticmethod
    def _create_insert_query(cur_subj_g: Graph) -> Tuple[str, bool, bool, bool]:
        query_string, are_citations, are_ids, are_others = ProvSet.__create_process_query(cur_subj_g)

        return u"INSERT DATA { " + query_string + " }", are_citations, are_ids, are_others

    @staticmethod
    def _create_delete_query(cur_subj_g: Graph) -> Tuple[str, bool, bool, bool]:
        query_string, are_citations, are_ids, are_others = ProvSet.__create_process_query(cur_subj_g)

        return u"DELETE DATA { " + query_string + " }", are_citations, are_ids, are_others

    def _are_added_triples(self, cur_subj: GraphEntity) -> Optional[str]:
        subj: GraphEntity = cur_subj
        cur_subj_g: Graph = cur_subj.g
        prev_subj_g: Graph = Graph()
        query: str = "CONSTRUCT {<%s> ?p ?o} WHERE {<%s> ?p ?o}" % (subj, subj)
        print(query, '\n')
        result: Result = self.ts.query(query)

        if result:
            for s, p, o in result:
                prev_subj_g.add((s, p, o))

            iso1: IsomorphicGraph = to_isomorphic(prev_subj_g)
            iso2: IsomorphicGraph = to_isomorphic(cur_subj_g)
            if iso1 == iso2:  # the graphs are the same
                return None
            else:
                in_both, in_first, in_second = graph_diff(iso1, iso2)
                query_string: str = u"INSERT DATA { GRAPH <%s> { " % cur_subj_g.identifier
                query_string += in_second.serialize(format="nt11", encoding="utf-8").decode("utf-8")
                return query_string.replace('\n\n', '') + "} }"

    @staticmethod
    def __create_process_query(cur_subj_g: Graph) -> Tuple[str, bool, bool, bool]:
        query_string: str = u"GRAPH <%s> { " % cur_subj_g.identifier
        is_first: bool = True
        are_citations: bool = False
        are_ids: bool = False
        are_others: bool = False

        for s, p, o in cur_subj_g.triples((None, None, None)):
            if p == GraphEntity.cites:
                are_citations = True
            elif p == GraphEntity.has_identifier:
                are_ids = True
            else:
                are_others = True
        # HERE query ts and do the diff
        query_string += cur_subj_g.serialize(format="nt11", encoding="utf-8").decode("utf-8")

        return query_string + "}", are_citations, are_ids, are_others

    def _add_prov(self, short_name: str, prov_type: URIRef, res: URIRef, resp_agent: str,
                  prov_subject: GraphEntity = None) -> ProvEntity:
        if prov_subject is None:
            g_prov: str = self.base_iri + "prov/"

            prov_info_path: str = \
                g_prov.replace(self.base_iri, self.info_dir.rsplit(os.sep, 2)[0] + os.sep) + short_name + ".txt"
        else:
            g_prov: str = str(prov_subject) + "/prov/"

            prov_info_path: str = self.info_dir.replace('info_file', 'prov_file') + prov_subject.short_name + ".txt"

        list_of_entities: List[GraphEntity] = [] if prov_subject is None else [prov_subject]
        cur_g, count, label = self._add(graph_url=g_prov, res=res, info_file_path=prov_info_path, short_name=short_name,
                                        list_of_entities=list_of_entities)
        return ProvEntity(list_of_entities[0] if list_of_entities else None, cur_g, res=res, res_type=prov_type,
                          short_name=short_name, resp_agent=resp_agent, source_agent=None, source=None, count=count,
                          label=label, g_set=self)

    def _set_ns(self, g: Graph) -> None:
        super(ProvSet, self)._set_ns(g)
        g.namespace_manager.bind("oco", ProvEntity.OCO)
        g.namespace_manager.bind("prov", ProvEntity.PROV)

    ################################################################################################
    initial_line_len: int = 3
    trailing_char: str = ' '

    @staticmethod
    def _get_line_len(file: BinaryIO) -> int:
        cur_char: str = file.read(1).decode('ascii')
        count: int = 1
        while cur_char is not None and len(cur_char) == 1 and cur_char != '\0':
            cur_char = file.read(1).decode('ascii')
            count += 1
            if cur_char == '\n':
                break

        # Undo I/O pointer updates
        file.seek(0)

        if cur_char is None:
            raise EOFError('Reached end-of-file without encountering a line separator!')
        elif cur_char == '\0':
            raise ValueError('Encountered a NULL byte!')
        else:
            return count

    @staticmethod
    def _increase_line_len(file_path: str, new_length: int = 0) -> None:
        if new_length <= 0:
            raise ValueError('new_length must be a positive non-zero integer number!')

        with open(file_path, 'rb') as cur_file:
            if ProvSet._get_line_len(cur_file) >= new_length:
                raise ValueError('Current line length is greater than new_length!')

        fh, abs_path = mkstemp()
        with os.fdopen(fh, 'wb') as new_file:
            with open(file_path, 'rt', encoding='ascii') as old_file:
                for line in old_file:
                    number: str = line.rstrip(ProvSet.trailing_char + '\n')
                    new_line: str = str(number).ljust(new_length - 1, ProvSet.trailing_char) + '\n'
                    new_file.write(new_line.encode('ascii'))

        # Copy the file permissions from the old file to the new file
        copymode(file_path, abs_path)

        # Replace original file
        os.remove(file_path)
        move(abs_path, file_path)

    @staticmethod
    def _is_a_valid_line(buf: bytes) -> bool:
        string: str = buf.decode('ascii')
        return (string[-1] == '\n') and ('\0' not in string[:-1])

    @staticmethod
    def _fix_previous_lines(file: BinaryIO, line_len: int) -> None:
        if line_len < ProvSet.initial_line_len:
            raise ValueError('line_len should be at least %d!' % ProvSet.initial_line_len)

        while file.tell() >= line_len:
            file.seek(-line_len, os.SEEK_CUR)
            buf: bytes = file.read(line_len)
            if ProvSet._is_a_valid_line(buf) or len(buf) < line_len:
                break
            else:
                file.seek(-line_len, os.SEEK_CUR)
                fixed_line: str = (ProvSet.trailing_char * (line_len - 1)) + '\n'
                file.write(fixed_line.encode('ascii'))
                file.seek(-line_len, os.SEEK_CUR)

    @staticmethod
    def _read_number(file_path: str, line_number: int = 1) -> Tuple[int, int]:
        if line_number <= 0:
            raise ValueError('line_number must be a positive non-zero integer number!')

        cur_number: int = 0
        cur_line_len: int = 0
        try:
            with open(file_path, "rb") as file:
                cur_line_len = ProvSet._get_line_len(file)
                line_offset = (line_number - 1) * cur_line_len
                file.seek(line_offset)
                line = file.readline(cur_line_len).decode('ascii')
                cur_number = int(line.rstrip(ProvSet.trailing_char + '\n'))
        except ValueError:
            cur_number = 0
        except Exception as e:
            print(e)

        return cur_number, cur_line_len

    @staticmethod
    def _add_number(file_path: str, line_number: int = 1) -> int:
        if line_number <= 0:
            raise ValueError('line_number must be a positive non-zero integer number!')

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        if not os.path.isfile(file_path):
            with open(file_path, "wb") as file:
                first_line = ProvSet.trailing_char * (ProvSet.initial_line_len - 1) + '\n'
                file.write(first_line.encode('ascii'))

        cur_number, cur_line_len = ProvSet._read_number(file_path, line_number)
        cur_number += 1

        cur_number_len: int = len(str(cur_number)) + 1
        if cur_number_len > cur_line_len:
            ProvSet._increase_line_len(file_path, new_length=cur_number_len)
            cur_line_len = cur_number_len

        with open(file_path, "r+b") as file:
            line_offset: int = (line_number - 1) * cur_line_len
            file.seek(line_offset)
            line: str = str(cur_number).ljust(cur_line_len - 1, ProvSet.trailing_char) + '\n'
            file.write(line.encode('ascii'))
            file.seek(-cur_line_len, os.SEEK_CUR)
            ProvSet._fix_previous_lines(file, cur_line_len)
        return cur_number
