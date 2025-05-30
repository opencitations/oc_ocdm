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
from unittest.mock import patch

from oc_ocdm.graph import GraphSet
from oc_ocdm.reader import Reader
from rdflib import Graph, URIRef
from SPARQLWrapper import POST, SPARQLWrapper


class TestReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.endpoint = 'http://127.0.0.1:8804/sparql'
        cls.resp_agent = 'https://orcid.org/0000-0002-8420-0696'
        BASE = os.path.join('tests', 'reader')
        
        cls.br_file = os.path.abspath(os.path.join(BASE, 'br.nt'))
        cls.ra_file = os.path.abspath(os.path.join(BASE, 'ra.nt'))
        cls.id_file = os.path.abspath(os.path.join(BASE, 'id.nt'))
        
        for file_path in [cls.br_file, cls.ra_file, cls.id_file]:
            if os.path.exists(file_path):
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
    
    def setUp(self):
        self.reader = Reader()
        self.g_set = GraphSet('https://w3id.org/oc/meta')
    
    def test_import_entity_from_triplestore(self):
        """Test importing a single entity from triplestore."""
        self.reader.import_entity_from_triplestore(
            self.g_set, 
            self.endpoint, 
            URIRef('https://w3id.org/oc/meta/br/0605'), 
            self.resp_agent, 
            False
        )
        self.assertEqual(
            set(str(s) for s in self.g_set.res_to_entity.keys()),
            {'https://w3id.org/oc/meta/br/0605'}
        )
    
    def test_import_entities_from_triplestore_batch(self):
        """Test importing multiple entities in batch."""
        entities = [
            URIRef('https://w3id.org/oc/meta/br/0605'),
            URIRef('https://w3id.org/oc/meta/br/0636066666')
        ]
        
        imported = self.reader.import_entities_from_triplestore(
            self.g_set,
            self.endpoint,
            entities,
            self.resp_agent,
            batch_size=1  # Test with small batch size
        )
        
        # Check if all entities were imported
        imported_uris = set(str(s) for s in self.g_set.res_to_entity.keys())
        expected_uris = set(str(e) for e in entities)
        self.assertEqual(imported_uris, expected_uris)
        
        # Check if number of imported entities matches
        self.assertEqual(len(imported), len(entities))
        
        # Check if specific properties were imported correctly
        br_0605 = self.g_set.get_entity(URIRef('https://w3id.org/oc/meta/br/0605'))
        self.assertIsNotNone(br_0605)
        # Check title
        title = next(br_0605.g.objects(br_0605.res, URIRef('http://purl.org/dc/terms/title')))
        self.assertEqual(str(title), "A Review Of Hemolytic Uremic Syndrome In Patients Treated With Gemcitabine Therapy")
    
    def test_import_invalid_entity(self):
        """Test importing a non-existent entity."""
        with self.assertRaises(ValueError):
            self.reader.import_entity_from_triplestore(
                self.g_set,
                self.endpoint,
                URIRef('https://w3id.org/oc/meta/br/99999'),
                self.resp_agent,
                False
            )
        
    def test_batch_import_with_retry(self):
        """Test batch import with connection failure and retry."""
        entities = [
            URIRef('https://w3id.org/oc/meta/br/0605'),
            URIRef('https://w3id.org/oc/meta/br/0636066666')
        ]
        
        # Mock SPARQLWrapper to fail once then succeed
        with patch('SPARQLWrapper.SPARQLWrapper.queryAndConvert') as mock_query:
            mock_query.side_effect = [
                Exception("Connection failed"),  # First attempt fails
                {'results': {'bindings': []}}    # Second attempt succeeds
            ]
            
            # This should retry and eventually succeed
            with self.assertRaises(ValueError):  # Empty results raise ValueError
                self.reader.import_entities_from_triplestore(
                    self.g_set,
                    self.endpoint,
                    entities,
                    self.resp_agent
                )
            
            # Verify that retry happened
            self.assertEqual(mock_query.call_count, 2)
    
    def test_import_mixed_entity_types(self):
        """Test importing different types of entities in the same batch."""
        entities = [
            URIRef('https://w3id.org/oc/meta/br/0605'),       # Bibliographic Resource
            URIRef('https://w3id.org/oc/meta/id/0605'),       # Identifier
            URIRef('https://w3id.org/oc/meta/re/0605')        # Resource Embodiment
        ]
        
        imported = self.reader.import_entities_from_triplestore(
            self.g_set,
            self.endpoint,
            entities,
            self.resp_agent
        )
        
        # Check if entities of different types were imported correctly
        entity_types = set()
        for entity in imported:
            for _, _, o in entity.g.triples((entity.res, URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), None)):
                entity_types.add(str(o))
                
        self.assertTrue(len(entity_types) >= 2)  # Should have multiple types
    
    def test_empty_batch_import(self):
        """Test importing an empty list of entities."""
        with self.assertRaises(ValueError):
            self.reader.import_entities_from_triplestore(
                self.g_set,
                self.endpoint,
                [],
                self.resp_agent
            )

    @classmethod
    def tearDownClass(cls):
        """Clean up the triplestore after tests."""
        delete_query = "CLEAR GRAPH <https://w3id.org/oc/meta/>"
        server = SPARQLWrapper(cls.endpoint)
        server.setMethod(POST)
        server.setQuery(delete_query)
        server.query()


if __name__ == '__main__':
    unittest.main()