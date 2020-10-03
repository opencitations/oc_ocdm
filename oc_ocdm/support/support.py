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

__author__ = 'essepuntato'

import os
import re
from datetime import datetime
from typing import Optional, List, Tuple
from urllib.parse import quote

from rdflib import Literal, RDF, URIRef, XSD


def create_date(date_list: List[Optional[int]] = None) -> Tuple[Optional[URIRef], Optional[str]]:
    cur_type = None
    string = None
    if date_list is not None:
        l_date_list = len(date_list)
        if l_date_list != 0 and date_list[0] is not None:
            if l_date_list == 3 and \
                    ((date_list[1] is not None and date_list[1] != 1) or
                     (date_list[2] is not None and date_list[2] != 1)):
                cur_type = XSD.date
                string = datetime(
                    date_list[0], date_list[1], date_list[2], 0, 0).strftime('%Y-%m-%d')
            elif l_date_list == 2 and date_list[1] is not None:
                cur_type = XSD.gYearMonth
                string = datetime(
                    date_list[0], date_list[1], 1, 0, 0).strftime('%Y-%m')
            else:
                cur_type = XSD.gYear
                string = datetime(date_list[0], 1, 1, 0, 0).strftime('%Y')
    return cur_type, string


def encode_url(u):
    return quote(u, "://")


def create_literal(g, res, p, s, dt=None, nor=True):
    string = s
    if not is_string_empty(string):
        g.add((res, p, Literal(string, datatype=dt, normalize=nor)))
        return True
    return False


def create_type(g, res, res_type):
    g.add((res, RDF.type, res_type))


def is_string_empty(string):
    return string is None or string.strip() == ""


def get_short_name(res):
    """
    if "/ci/" in str(res):
        return re.sub("^.+/([a-z][a-z])/((0[1-9]+0)?[1-9][0-9]*-(0[1-9]+0)?[1-9][0-9]*(/[1-9][0-9]*)?)$", "\\1", str(res))
    else:
        return re.sub("^.+/([a-z][a-z])(/[0-9]+)?$", "\\1", str(res))
    """
    return re.sub("^.+/([a-z][a-z])(/[0-9]+)?$", "\\1", str(res))


def get_prefix(res):
    """
    if "/ci/" in str(res):
        return re.sub("^.+/[a-z][a-z]/((0[1-9]+0)?[1-9][0-9]*-(0[1-9]+0)?[1-9][0-9]*(/[1-9][0-9]*)?)$", "\\2", str(res))
    else:
        return re.sub("^.+/[a-z][a-z]/(0[1-9]+0)?([1-9][0-9]*)$", "\\1", str(res))
    """
    return re.sub("^.+/[a-z][a-z]/(0[1-9]+0)?([1-9][0-9]*)$", "\\1", str(res))


def get_count(res):
    """
    if "/ci/" in str(res):
        return re.sub("^.+/[a-z][a-z]/((0[1-9]+0)?[1-9][0-9]*-(0[1-9]+0)?[1-9][0-9]*(/[1-9][0-9]*)?)$", "\\1", str(res))
    else:
        return re.sub("^.+/[a-z][a-z]/(0[1-9]+0)?([1-9][0-9]*)$", "\\2", str(res))
    """
    return re.sub("^.+/[a-z][a-z]/(0[1-9]+0)?([1-9][0-9]*)$", "\\2", str(res))


def get_resource_number(string_iri):
    cur_number = 0
    if "/prov/" in string_iri:
        if "/pa/" not in string_iri:
            if "/ci/" not in string_iri:
                cur_number = int(re.sub(prov_regex, "\\3", string_iri))
            else:
                cur_number = int(re.sub(ci_prov_regex, "\\3", string_iri))
    else:
        if "/ci/" in string_iri:
            cur_number = int(re.sub(ci_regex, "\\3", string_iri))
        else:
            cur_number = int(re.sub(res_regex, "\\3", string_iri))

    return cur_number


def find_local_line_id(res, n_file_item=1):
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
res_regex = "(.+)/(0[1-9]+0)?([1-9][0-9]*)$"
ci_regex = "(.+)/(0[1-9]+0)?([1-9][0-9]*)(-)(0[1-9]+0)?([1-9][0-9]*)(/[1-9][0-9]*)?$"
prov_regex = "(.+)/(0[1-9]+0)?([1-9][0-9]*)(/prov)/(.+)/([0-9]+)$"
ci_prov_regex = "(.+)/(0[1-9]+0)?([1-9][0-9]*)(-)(0[1-9]+0)?([1-9][0-9]*)(/[1-9][0-9]*)?(/prov)/(.+)/([0-9]+)$"


def find_paths(string_iri, base_dir, base_iri, default_dir, dir_split, n_file_item,is_json=True):
    """
    This function is responsible for looking for the correct JSON file that contains the data related to the
    resource identified by the variable 'string_iri'. This search takes into account the organisation in
    directories and files, as well as the particular supplier prefix for bibliographic entities, if specified.
    In case no supplier prefix is specified, the 'default_dir' (usually set to "_") is used instead.
    """
    cur_file_path = None
    if is_json:
        format_string = ".json"
    else:
        format_string = ".ttl"

    if is_dataset(string_iri):
        cur_dir_path = (base_dir + re.sub("^%s(.*)$" % base_iri, "\\1", string_iri))[:-1]
        # In case of dataset, the file path is different from regular files, e.g.
        # /corpus/br/index.json
        cur_file_path = cur_dir_path + os.sep + "index.json"
        print("is_dataset",cur_dir_path, cur_file_path)

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
                if "/ci/" not in string_iri:
                    cur_dir_path = base_dir + \
                                   re.sub(("^%s" + prov_regex) % base_iri,
                                          ("\\1%s\\2" % os.sep if has_supplier_prefix(string_iri, base_iri) else
                                           "\\1%s%s" % (os.sep, default_dir)), string_iri) + \
                                   os.sep + str(cur_split) + os.sep + str(cur_file_split) + os.sep + "prov"
                    cur_file_path = cur_dir_path + os.sep + re.sub(
                        ("^%s" + prov_regex) % base_iri, "\\5", string_iri) + format_string
                else:
                    cur_dir_path = base_dir + \
                                   re.sub(("^%s" + ci_prov_regex) % base_iri,
                                          ("\\1%s\\2" % os.sep if has_supplier_prefix(string_iri, base_iri) else
                                           "\\1%s%s" % (os.sep, default_dir)), string_iri) + \
                                   os.sep + str(cur_split) + os.sep + str(cur_file_split) + os.sep + "prov"
                    cur_file_path = cur_dir_path + os.sep + re.sub(
                        ("^%s" + ci_prov_regex) % base_iri, "\\9", string_iri) + format_string
            else:  # regular bibliographic entity
                if "/ci/" not in string_iri:
                    cur_dir_path = base_dir + \
                                   re.sub(("^%s" + res_regex) % base_iri,
                                          ("\\1%s\\2" % os.sep if has_supplier_prefix(string_iri, base_iri) else
                                           "\\1%s%s" % (os.sep, default_dir)),
                                          string_iri) + \
                                   os.sep + str(cur_split)

                    cur_file_path = cur_dir_path + os.sep + str(cur_file_split) + format_string
                else:
                    cur_dir_path = base_dir + \
                                   re.sub(("^%s" + ci_regex) % base_iri,
                                          ("\\1%s\\2" % os.sep if has_supplier_prefix(string_iri, base_iri) else
                                           "\\1%s%s" % (os.sep, default_dir)),
                                          string_iri) + \
                                   os.sep + str(cur_split)

                    cur_file_path = cur_dir_path + os.sep + str(cur_file_split) + format_string
        # Enter here if no split is needed
        elif dir_split == 0:
            if "/prov/" in string_iri:
                if "/ci/" not in string_iri:
                    cur_dir_path = base_dir + \
                                   re.sub(("^%s" + prov_regex) % base_iri,
                                          ("\\1%s\\2" % os.sep if has_supplier_prefix(string_iri, base_iri) else
                                           "\\1%s%s" % (os.sep, default_dir)), string_iri) + \
                                   os.sep + str(cur_file_split) + os.sep + "prov"
                    cur_file_path = cur_dir_path + os.sep + re.sub(
                        ("^%s" + prov_regex) % base_iri, "\\5", string_iri) + format_string
                else:
                    cur_dir_path = base_dir + \
                                   re.sub(("^%s" + ci_prov_regex) % base_iri,
                                          ("\\1%s\\2" % os.sep if has_supplier_prefix(string_iri, base_iri) else
                                           "\\1%s%s" % (os.sep, default_dir)), string_iri) + \
                                   os.sep + str(cur_file_split) + os.sep + "prov"
                    cur_file_path = cur_dir_path + os.sep + re.sub(
                        ("^%s" + ci_prov_regex) % base_iri, "\\9", string_iri) + format_string
            else:
                if "/ci/" not in string_iri:
                    cur_dir_path = base_dir + \
                                   re.sub(("^%s" + res_regex) % base_iri,
                                          ("\\1%s\\2" % os.sep if has_supplier_prefix(string_iri, base_iri) else
                                           "\\1%s%s" % (os.sep, default_dir)),
                                          string_iri)

                    cur_file_path = cur_dir_path + os.sep + str(cur_file_split) + format_string
                else:
                    cur_dir_path = base_dir + \
                                   re.sub(("^%s" + ci_regex) % base_iri,
                                          ("\\1%s\\2" % os.sep if has_supplier_prefix(string_iri, base_iri) else
                                           "\\1%s%s" % (os.sep, default_dir)),
                                          string_iri)

                    cur_file_path = cur_dir_path + os.sep + str(cur_file_split) + format_string
        # Enter here if the data is about a provenance agent, e.g.,
        # /corpus/prov/
        else:
            cur_dir_path = base_dir + re.sub(("^%s" + res_regex) % base_iri, "\\1", string_iri)
            cur_file_path = cur_dir_path + os.sep + re.sub(res_regex, "\\2\\3", string_iri) + format_string
            print("else:",cur_dir_path, cur_file_path)
            # if "/ci/" not in string_iri:
            #     cur_dir_path = base_dir + re.sub(("^%s" + res_regex) % base_iri, "\\1", string_iri)
            #     cur_file_path = cur_dir_path + os.sep + re.sub(res_regex, "\\2\\3", string_iri) + ".json"
            # else:
            #     cur_dir_path = base_dir + re.sub(("^%s" + ci_res_regex) % base_iri, "\\1", string_iri)
            #     cur_file_path = cur_dir_path + os.sep + re.sub(ci_regex, "\\2\\3", string_iri) + ".json"

    return cur_dir_path, cur_file_path


def has_supplier_prefix(string_iri, base_iri):
    return re.search("^%s[a-z][a-z]/0" % base_iri, string_iri) is not None


def is_dataset(string_iri):
    # return re.search("^.+/[0-9]+$", string_iri) is None
    return re.search("^.+/[0-9]+(-[0-9]+)?(/[0-9]+)?$", string_iri) is None
