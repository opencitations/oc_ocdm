#!/usr/bin/python

# SPDX-FileCopyrightText: 2020 Simone Persiani <iosonopersia@gmail.com>
# SPDX-FileCopyrightText: 2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-

from oc_ocdm.support.query_utils import get_delete_query, get_insert_query, get_update_query
from oc_ocdm.support.reporter import Reporter
from oc_ocdm.support.support import (
    create_date,
    create_literal,
    create_type,
    encode_url,
    find_local_line_id,
    find_paths,
    get_count,
    get_datatype_from_iso_8601,
    get_prefix,
    get_resource_number,
    get_short_name,
    has_supplier_prefix,
    is_dataset,
    is_string_empty,
    sparql_binding_to_term,
)
