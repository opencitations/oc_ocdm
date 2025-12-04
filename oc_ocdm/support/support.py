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

import os
import re
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import TYPE_CHECKING
from rdflib import URIRef, Graph

if TYPE_CHECKING:
    from typing import Optional, List, Tuple, Match, Dict, Set
    from oc_ocdm.graph.entities.bibliographic.bibliographic_resource import BibliographicResource
    from oc_ocdm.graph.entities.bibliographic.responsible_agent import ResponsibleAgent
    from oc_ocdm.graph.entities.bibliographic.agent_role import AgentRole

from urllib.parse import quote


@dataclass
class ParsedURI:
    base_iri: str
    short_name: str
    prefix: str
    count: str
    is_prov: bool
    prov_subject_short_name: str
    prov_subject_prefix: str
    prov_subject_count: str

from rdflib import RDF, XSD, Literal


def create_date(date_list: List[Optional[int]] = None) -> Optional[str]:
    string: Optional[str] = None
    if date_list is not None:
        l_date_list: int = len(date_list)
        if l_date_list != 0 and date_list[0] is not None:
            if l_date_list == 3 and \
                    ((date_list[1] is not None and date_list[1] != 1) or
                     (date_list[2] is not None and date_list[2] != 1)):
                string = datetime(date_list[0], date_list[1], date_list[2]).strftime('%Y-%m-%d')
            elif l_date_list == 2 and date_list[1] is not None:
                string = datetime(date_list[0], date_list[1], 1).strftime('%Y-%m')
            else:
                string = datetime(date_list[0], 1, 1).strftime('%Y')
    return string


def get_datatype_from_iso_8601(string: str) -> Tuple[URIRef, str]:
    # Keep only the "yyyy-mm-dd" part of the string
    string = string[:10]

    try:
        date_parts: List[int] = [int(s) for s in string.split(sep='-', maxsplit=2)]
    except ValueError:
        raise ValueError("The provided date string is not ISO-8601 compliant!")

    num_of_parts: int = len(date_parts)
    if num_of_parts == 3:
        return XSD.date, datetime(*date_parts).strftime('%Y-%m-%d')
    elif num_of_parts == 2:
        return XSD.gYearMonth, datetime(*date_parts, 1).strftime('%Y-%m')
    else:
        return XSD.gYear, datetime(*date_parts, 1, 1).strftime('%Y')

def get_ordered_contributors_from_br(br: BibliographicResource,
                                     contributor_type: URIRef):

    ar_list: List[AgentRole] = br.get_contributors()

    list_id: int = 0
    heads: Dict[URIRef, Dict] = {}
    tails: Dict[URIRef, Dict] = {}
    sub_lists: List[Dict] = []
    from_id_to_res_in_heads: Dict[int, URIRef] = {}
    for ar in ar_list:
        role_type: URIRef = ar.get_role_type()
        ra: ResponsibleAgent = ar.get_is_held_by()
        next_ar: AgentRole = ar.get_next()
        if next_ar is not None:
            next_ar_res: Optional[URIRef] = next_ar.res
        else:
            next_ar_res: Optional[URIRef] = None

        if role_type is not None and role_type == contributor_type and ra is not None:
            if next_ar_res is not None and next_ar_res in heads:
                sub_list: Dict = heads[next_ar_res]
                sub_list['list'].insert(0, ra)
                del heads[next_ar_res]
                heads[ar.res] = sub_list
                from_id_to_res_in_heads[sub_list['id']] = ar.res
            elif ar.res is not None and ar.res in tails:
                sub_list: Dict = tails[ar.res]
                sub_list['list'].append(ra)
                del tails[ar.res]

                if next_ar_res is not None:
                    tails[next_ar_res] = sub_list
            else:
                # This AR cannot be inserted into any list, so
                # we need to create an entirely new list for it:
                sub_list: Dict = {'id': list_id, 'list': [ra]}
                list_id += 1
                sub_lists.append(sub_list)

                heads[ar.res] = sub_list
                from_id_to_res_in_heads[sub_list['id']] = ar.res
                if next_ar_res is not None:
                    tails[next_ar_res] = sub_list

    ids_in_heads: Set[int] = {val['id'] for val in heads.values()}
    ids_in_tails: Set[int] = {val['id'] for val in tails.values()}
    diff_set: Set[int] = ids_in_heads - ids_in_tails
    if len(diff_set) == 0:
        # No contributor was found!
        return []
    elif len(diff_set) != 1:
        raise ValueError('A malformed list of AgentRole entities was given.')
    else:
        result_list: List[ResponsibleAgent] = []
        cur_id: int = diff_set.pop()
        already_merged_list_ids: Set[int] = set()
        finished: bool = False
        while not finished:
            found: bool = False
            if cur_id in from_id_to_res_in_heads:
                res: URIRef = from_id_to_res_in_heads[cur_id]
                subl: Dict = heads[res]
                subl_id: int = subl['id']
                if subl_id not in already_merged_list_ids:
                    found = True
                    already_merged_list_ids.add(subl_id)
                    result_list = subl['list'] + result_list

                    # Now we need to get the next cur_id value:
                    if res in tails:
                        cur_id = tails[res]['id']
                    else:
                        finished = True

            if not found:
                raise ValueError('A malformed list of AgentRole entities was given.')

        unmerged_list_ids: Set[int] = ids_in_heads - already_merged_list_ids
        if len(unmerged_list_ids) != 0:
            raise ValueError('A malformed list of AgentRole entities was given.')

        return result_list


def encode_url(u: str) -> str:
    return quote(u, "://")


def create_literal(g: Graph, res: URIRef, p: URIRef, s: str, dt: URIRef = None, nor: bool = True) -> None:
    if not is_string_empty(s):
        dt = dt if dt is not None else XSD.string
        g.add((res, p, Literal(s, datatype=dt, normalize=nor)))


def create_type(g: Graph, res: URIRef, res_type: URIRef) -> None:
    g.add((res, RDF.type, res_type))


def is_string_empty(string: str) -> bool:
    return string is None or string.strip() == ""


# Variable used in several functions
entity_regex: str = r"^(.+)/([a-z][a-z])/(0[1-9]+0)?((?:[1-9][0-9]*)|(?:\d+-\d+))$"
prov_regex: str = r"^(.+)/([a-z][a-z])/(0[1-9]+0)?((?:[1-9][0-9]*)|(?:\d+-\d+))/prov/([a-z][a-z])/([1-9][0-9]*)$"

_compiled_entity_regex = re.compile(entity_regex)
_compiled_prov_regex = re.compile(prov_regex)


@lru_cache(maxsize=4096)
def parse_uri(res: URIRef) -> ParsedURI:
    string_iri = str(res)
    if "/prov/" in string_iri:
        match = _compiled_prov_regex.match(string_iri)
        if match:
            return ParsedURI(
                base_iri=match.group(1),
                short_name=match.group(5),
                prefix="",
                count=match.group(6),
                is_prov=True,
                prov_subject_short_name=match.group(2),
                prov_subject_prefix=match.group(3) or "",
                prov_subject_count=match.group(4),
            )
    else:
        match = _compiled_entity_regex.match(string_iri)
        if match:
            return ParsedURI(
                base_iri=match.group(1),
                short_name=match.group(2),
                prefix=match.group(3) or "",
                count=match.group(4),
                is_prov=False,
                prov_subject_short_name="",
                prov_subject_prefix="",
                prov_subject_count="",
            )
    return ParsedURI("", "", "", "", False, "", "", "")


def get_base_iri(res: URIRef) -> str:
    return parse_uri(res).base_iri


def get_short_name(res: URIRef) -> str:
    return parse_uri(res).short_name


def get_prefix(res: URIRef) -> str:
    return parse_uri(res).prefix


def get_count(res: URIRef) -> str:
    return parse_uri(res).count


def get_resource_number(res: URIRef) -> int:
    parsed = parse_uri(res)
    count = parsed.prov_subject_count if parsed.is_prov else parsed.count
    return int(count) if count else 0


def find_local_line_id(res: URIRef, n_file_item: int = 1) -> int:
    cur_number: int = get_resource_number(res)

    cur_file_split: int = 0
    while True:
        if cur_number > cur_file_split:
            cur_file_split += n_file_item
        else:
            cur_file_split -= n_file_item
            break

    return cur_number - cur_file_split


def find_paths(res: URIRef, base_dir: str, base_iri: str, default_dir: str, dir_split: int,
               n_file_item: int, is_json: bool = True, process_id: int|str = None) -> Tuple[str, str]:
    """
    This function is responsible for looking for the correct JSON file that contains the data related to the
    resource identified by the variable 'string_iri'. This search takes into account the organisation in
    directories and files, as well as the particular supplier prefix for bibliographic entities, if specified.
    In case no supplier prefix is specified, the 'default_dir' (usually set to "_") is used instead.
    """
    string_iri: str = str(res)
    process_id_str: str = f"_{process_id}" if process_id else ""

    if is_dataset(res):
        cur_dir_path: str = (base_dir + re.sub(r"^%s(.*)$" % base_iri, r"\1", string_iri))[:-1]
        cur_file_path: str = cur_dir_path + os.sep + "index" + process_id_str + ".json"
        return cur_dir_path, cur_file_path

    parsed = parse_uri(res)
    cur_number: int = int(parsed.prov_subject_count) if parsed.is_prov else int(parsed.count)

    cur_file_split: int = 0
    while cur_number > cur_file_split:
        cur_file_split += n_file_item

    if dir_split and not string_iri.startswith(base_iri + "prov/"):
        cur_split: int = 0
        while cur_number > cur_split:
            cur_split += dir_split

        if parsed.is_prov:
            sub_folder = parsed.prov_subject_prefix or default_dir or "_"
            file_extension = '.json' if is_json else '.nq'
            cur_dir_path = base_dir + parsed.prov_subject_short_name + os.sep + sub_folder + \
                os.sep + str(cur_split) + os.sep + str(cur_file_split) + os.sep + "prov"
            cur_file_path = cur_dir_path + os.sep + parsed.short_name + process_id_str + file_extension
        else:
            sub_folder = parsed.prefix or default_dir or "_"
            file_extension = '.json' if is_json else '.nt'
            cur_dir_path = base_dir + parsed.short_name + os.sep + sub_folder + os.sep + str(cur_split)
            cur_file_path = cur_dir_path + os.sep + str(cur_file_split) + process_id_str + file_extension
    elif dir_split == 0:
        if parsed.is_prov:
            sub_folder = parsed.prov_subject_prefix or default_dir or "_"
            file_extension = '.json' if is_json else '.nq'
            cur_dir_path = base_dir + parsed.prov_subject_short_name + os.sep + sub_folder + \
                os.sep + str(cur_file_split) + os.sep + "prov"
            cur_file_path = cur_dir_path + os.sep + parsed.short_name + process_id_str + file_extension
        else:
            sub_folder = parsed.prefix or default_dir or "_"
            file_extension = '.json' if is_json else '.nt'
            cur_dir_path = base_dir + parsed.short_name + os.sep + sub_folder
            cur_file_path = cur_dir_path + os.sep + str(cur_file_split) + process_id_str + file_extension
    else:
        file_extension = '.json' if is_json else '.nq'
        cur_dir_path = base_dir + parsed.short_name
        cur_file_path = cur_dir_path + os.sep + parsed.prefix + parsed.count + process_id_str + file_extension

    return cur_dir_path, cur_file_path

def has_supplier_prefix(res: URIRef, base_iri: str) -> bool:
    string_iri: str = str(res)
    return re.search(r"^%s[a-z][a-z]/0" % base_iri, string_iri) is not None

def build_graph_from_results(results: List[Dict]) -> Graph:
    graph = Graph()
    for triple in results:
        s = URIRef(triple['s']['value'])
        p = URIRef(triple['p']['value'])
        if triple['o']['type'] == 'uri':
            o = URIRef(triple['o']['value'])
        else:
            datatype = triple['o'].get('datatype', None)
            datatype = URIRef(datatype) if datatype is not None else None
            o = Literal(triple['o']['value'], datatype=datatype)
        graph.add((s, p, o))
    return graph


def is_dataset(res: URIRef) -> bool:
    string_iri: str = str(res)
    return re.search(r"^.+/[0-9]+(-[0-9]+)?(/[0-9]+)?$", string_iri) is None