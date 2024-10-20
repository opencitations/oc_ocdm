#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2023, Arcangelo Massari <arcangelo.massari@unibo.it>
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

import os
import unittest

from oc_ocdm.graph import GraphSet
from oc_ocdm.reader import Reader
from rdflib import Graph, URIRef
from SPARQLWrapper import POST, SPARQLWrapper


class TestReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.endpoint = 'http://127.0.0.1:8804/sparql'
        BASE = os.path.join('oc_ocdm', 'test', 'reader')
        file_path = os.path.abspath(os.path.join(BASE, 'br.nt'))

        g = Graph()
        g.parse(file_path, format='nt')

        insert_query = "INSERT DATA { GRAPH <https://w3id.org/oc/meta/> {\n"
        for s, p, o in g:
            insert_query += f"{s.n3()} {p.n3()} {o.n3()} .\n"
        insert_query += "} }"
        server = SPARQLWrapper(cls.endpoint)
        server.setMethod(POST)
        server.setQuery(insert_query)
        server.query()
    
    def test_import_entity_from_triplestore(self):
        reader = Reader()
        g_set = GraphSet('https://w3id.org/oc/meta')
        reader.import_entity_from_triplestore(g_set, self.endpoint, URIRef('https://w3id.org/oc/meta/br/0605'), 'https://orcid.org/0000-0002-8420-0696', False)
        self.assertEqual(set(str(s) for s in g_set.res_to_entity.keys()), {'https://w3id.org/oc/meta/br/0605'})