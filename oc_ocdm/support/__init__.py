#!/usr/bin/python

# SPDX-FileCopyrightText: 2020 Simone Persiani <iosonopersia@gmail.com>
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-

from oc_ocdm.support.support import create_date, get_datatype_from_iso_8601, encode_url, create_literal,\
                                    create_type, is_string_empty, get_short_name, get_prefix, get_count,\
                                    get_resource_number, find_local_line_id, find_paths, has_supplier_prefix,\
                                    is_dataset, sparql_binding_to_term
from oc_ocdm.support.reporter import Reporter
from oc_ocdm.support.query_utils import get_update_query, get_insert_query, get_delete_query