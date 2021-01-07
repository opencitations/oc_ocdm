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
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List, Tuple
from urllib.parse import quote

from rdflib import Literal, RDF, URIRef, XSD, Graph


def create_date(date_list: List[Optional[int]] = None) -> Optional[str]:
    string = None
    if date_list is not None:
        l_date_list = len(date_list)
        if l_date_list != 0 and date_list[0] is not None:
            if l_date_list == 3 and \
                    ((date_list[1] is not None and date_list[1] != 1) or
                     (date_list[2] is not None and date_list[2] != 1)):
                string = datetime(date_list[0], date_list[1], date_list[2]).strftime('%Y-%m-%d')
            elif l_date_list == 2 and date_list[1] is not None:
                string = datetime(date_list[0], date_list[1], 1).strftime('%Y-%m')
            else:
                string = datetime(date_list[0], 1, 1,).strftime('%Y')
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


def encode_url(u: str) -> str:
    return quote(u, "://")


def create_literal(g: Graph, res: URIRef, p: URIRef, s: str, dt: URIRef = None, nor: bool = True) -> None:
    string = s
    if not is_string_empty(string):
        g.add((res, p, Literal(string, datatype=dt, normalize=nor)))


def create_type(g: Graph, res: URIRef, res_type: URIRef) -> None:
    g.add((res, RDF.type, res_type))


def is_string_empty(string: str) -> bool:
    return string is None or string.strip() == ""


def get_short_name(res: URIRef) -> str:
    return re.sub("^.+/([a-z][a-z])(/[0-9]+)?$", "\\1", str(res))


def get_prefix(res: URIRef) -> str:
    return re.sub("^.+/[a-z][a-z]/(0[1-9]+0)?([1-9][0-9]*)$", "\\1", str(res))


def get_count(res: URIRef) -> str:
    return re.sub("^.+/[a-z][a-z]/(0[1-9]+0)?([1-9][0-9]*)$", "\\2", str(res))


def get_resource_number(string_iri: str) -> int:
    if "/prov/" in string_iri:
        return int(re.sub(prov_regex, "\\3", string_iri))
    else:
        return int(re.sub(res_regex, "\\3", string_iri))


def find_local_line_id(res: URIRef, n_file_item: int = 1) -> int:
    cur_number = get_resource_number(str(res))

    cur_file_split = 0
    while True:
        if cur_number > cur_file_split:
            cur_file_split += n_file_item
        else:
            cur_file_split -= n_file_item
            break

    return cur_number - cur_file_split


# Variable used in several functions
res_regex: str = "(.+)/(0[1-9]+0)?([1-9][0-9]*)$"
prov_regex: str = "(.+)/(0[1-9]+0)?([1-9][0-9]*)(/prov)/(.+)/([0-9]+)$"


def find_paths(string_iri: str, base_dir: str, base_iri: str, default_dir: str, dir_split: int,
               n_file_item: int, is_json: bool = True) -> Tuple[str, str]:
    """
    This function is responsible for looking for the correct JSON file that contains the data related to the
    resource identified by the variable 'string_iri'. This search takes into account the organisation in
    directories and files, as well as the particular supplier prefix for bibliographic entities, if specified.
    In case no supplier prefix is specified, the 'default_dir' (usually set to "_") is used instead.
    """
    if is_json:
        format_string = ".json"
    else:
        format_string = ".ttl"

    if is_dataset(string_iri):
        cur_dir_path = (base_dir + re.sub("^%s(.*)$" % base_iri, "\\1", string_iri))[:-1]
        # In case of dataset, the file path is different from regular files, e.g.
        # /corpus/br/index.json
        cur_file_path = cur_dir_path + os.sep + "index.json"
        print("is_dataset", cur_dir_path, cur_file_path)

    else:
        cur_number = get_resource_number(string_iri)

        # Find the correct file number where to save the resources
        cur_file_split = 0
        while True:
            if cur_number > cur_file_split:
                cur_file_split += n_file_item
            else:
                break

        # The data have been split in multiple directories and it is not something related
        # with the provenance data of the whole corpus (e.g. provenance agents)
        if dir_split and not string_iri.startswith(base_iri + "prov/"):
            # Find the correct directory number where to save the file
            cur_split = 0
            while True:
                if cur_number > cur_split:
                    cur_split += dir_split
                else:
                    break

            if "/prov/" in string_iri:  # provenance file of a bibliographic entity
                cur_dir_path = base_dir + \
                               re.sub(("^%s" + prov_regex) % base_iri,
                                      ("\\1%s\\2" % os.sep if has_supplier_prefix(string_iri, base_iri) else
                                       "\\1%s%s" % (os.sep, default_dir)), string_iri) + \
                               os.sep + str(cur_split) + os.sep + str(cur_file_split) + os.sep + "prov"
                cur_file_path = cur_dir_path + os.sep + re.sub(
                    ("^%s" + prov_regex) % base_iri, "\\5", string_iri) + format_string
            else:  # regular bibliographic entity
                cur_dir_path = base_dir + \
                               re.sub(("^%s" + res_regex) % base_iri,
                                      ("\\1%s\\2" % os.sep if has_supplier_prefix(string_iri, base_iri) else
                                       "\\1%s%s" % (os.sep, default_dir)),
                                      string_iri) + \
                               os.sep + str(cur_split)

                cur_file_path = cur_dir_path + os.sep + str(cur_file_split) + format_string
        # Enter here if no split is needed
        elif dir_split == 0:
            if "/prov/" in string_iri:
                cur_dir_path = base_dir + \
                               re.sub(("^%s" + prov_regex) % base_iri,
                                      ("\\1%s\\2" % os.sep if has_supplier_prefix(string_iri, base_iri) else
                                       "\\1%s%s" % (os.sep, default_dir)), string_iri) + \
                               os.sep + str(cur_file_split) + os.sep + "prov"
                cur_file_path = cur_dir_path + os.sep + re.sub(
                    ("^%s" + prov_regex) % base_iri, "\\5", string_iri) + format_string
            else:
                cur_dir_path = base_dir + \
                               re.sub(("^%s" + res_regex) % base_iri,
                                      ("\\1%s\\2" % os.sep if has_supplier_prefix(string_iri, base_iri) else
                                       "\\1%s%s" % (os.sep, default_dir)),
                                      string_iri)

                cur_file_path = cur_dir_path + os.sep + str(cur_file_split) + format_string
        # Enter here if the data is about a provenance agent, e.g.,
        # /corpus/prov/
        else:
            cur_dir_path = base_dir + re.sub(("^%s" + res_regex) % base_iri, "\\1", string_iri)
            cur_file_path = cur_dir_path + os.sep + re.sub(res_regex, "\\2\\3", string_iri) + format_string
            print("else:", cur_dir_path, cur_file_path)

    return cur_dir_path, cur_file_path


def has_supplier_prefix(string_iri: str, base_iri: str) -> bool:
    return re.search("^%s[a-z][a-z]/0" % base_iri, string_iri) is not None


def is_dataset(string_iri: str) -> bool:
    return re.search("^.+/[0-9]+(-[0-9]+)?(/[0-9]+)?$", string_iri) is None
