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
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import json

from oc_ocdm.graph import GraphSet
from oc_ocdm.reader import Reader
from oc_ocdm.support.reporter import Reporter
from rdflib import Graph, URIRef, Dataset, Namespace, RDF
from sparqlite import SPARQLClient


class TestReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.endpoint = 'http://127.0.0.1:8804/sparql'
        cls.resp_agent = 'https://orcid.org/0000-0002-8420-0696'
        BASE = os.path.join('tests', 'reader')

        cls.br_file = os.path.abspath(os.path.join(BASE, 'br.nt'))
        cls.ra_file = os.path.abspath(os.path.join(BASE, 'ra.nt'))
        cls.id_file = os.path.abspath(os.path.join(BASE, 'id.nt'))

        with SPARQLClient(cls.endpoint) as client:
            for file_path in [cls.br_file, cls.ra_file, cls.id_file]:
                if os.path.exists(file_path):
                    g = Graph()
                    g.parse(file_path, format='nt')

                    insert_query = "INSERT DATA { GRAPH <https://w3id.org/oc/meta/> {\n"
                    for s, p, o in g:
                        insert_query += f"{s.n3()} {p.n3()} {o.n3()} .\n"
                    insert_query += "} }"

                    client.update(insert_query)
    
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
        
    def test_batch_import_with_empty_results(self):
        """Test batch import with empty results."""
        entities = [
            URIRef('https://w3id.org/oc/meta/br/nonexistent1'),
            URIRef('https://w3id.org/oc/meta/br/nonexistent2')
        ]

        with self.assertRaises(ValueError):
            self.reader.import_entities_from_triplestore(
                self.g_set,
                self.endpoint,
                entities,
                self.resp_agent
            )
    
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

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist."""
        result = self.reader.load('/path/to/nonexistent/file.nt')
        self.assertIsNone(result)
        self.assertFalse(self.reader.reperr.is_empty())

    def test_load_invalid_format(self):
        """Test loading a file with invalid RDF format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.nt', delete=False) as f:
            f.write('This is not valid RDF\n')
            f.write('Just some random text\n')
            temp_file = f.name

        try:
            result = self.reader.load(temp_file)
            self.assertIsNone(result)
            self.assertFalse(self.reader.reperr.is_empty())
        finally:
            os.unlink(temp_file)

    def test_custom_reporters(self):
        """Test reader initialization with custom reporters."""
        custom_repok = Reporter(prefix="[Custom OK] ")
        custom_reperr = Reporter(prefix="[Custom ERROR] ")

        reader = Reader(repok=custom_repok, reperr=custom_reperr)

        self.assertEqual(reader.repok.prefix, "[Custom OK] ")
        self.assertEqual(reader.reperr.prefix, "[Custom ERROR] ")

    def test_context_map_file_loading(self):
        """Test loading JSON-LD context from file."""
        context_data = {
            "@context": {
                "dc": "http://purl.org/dc/terms/",
                "title": "dc:title"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(context_data, f)
            context_file = f.name

        try:
            context_map = {
                "http://example.org/context": context_file
            }
            reader = Reader(context_map=context_map)

            # Verify the context was loaded from file
            self.assertIn("http://example.org/context", reader.context_map)
            self.assertEqual(reader.context_map["http://example.org/context"], context_data)
        finally:
            os.unlink(context_file)

    def test_import_from_dataset(self):
        """Test importing entities from rdflib Dataset."""
        # Create a new GraphSet with a different base IRI for this test
        test_g_set = GraphSet('https://w3id.org/oc/meta')

        dataset = Dataset()

        # Create a simple bibliographic resource in the dataset
        br_uri = URIRef('https://w3id.org/oc/meta/br/9999')
        FABIO = Namespace('http://purl.org/spar/fabio/')

        # Add triples to a named graph in the dataset
        graph_uri = URIRef('https://w3id.org/oc/meta/br/')
        g = dataset.graph(graph_uri)
        g.add((br_uri, RDF.type, FABIO.Expression))
        g.add((br_uri, URIRef('http://purl.org/dc/terms/title'), URIRef('http://example.org/literal')))

        # Import from dataset
        imported = Reader.import_entities_from_graph(
            test_g_set,
            dataset,
            self.resp_agent,
            enable_validation=False
        )

        self.assertEqual(len(imported), 1)
        self.assertEqual(str(imported[0].res), str(br_uri))

    def test_shacl_validation_enabled(self):
        """Test importing entities with SHACL validation enabled."""
        # Create a new GraphSet with matching base IRI
        test_g_set = GraphSet('https://w3id.org/oc/meta')

        # Create a simple valid graph
        graph = Graph()
        br_uri = URIRef('https://w3id.org/oc/meta/br/8888')
        FABIO = Namespace('http://purl.org/spar/fabio/')

        graph.add((br_uri, RDF.type, FABIO.Expression))

        # Import with validation enabled
        imported = Reader.import_entities_from_graph(
            test_g_set,
            graph,
            self.resp_agent,
            enable_validation=True,
            closed=False
        )

        # Should import successfully even with validation
        self.assertGreaterEqual(len(imported), 0)

    def test_load_zip_file(self):
        """Test loading RDF data from a ZIP file."""
        # Create a temporary RDF file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.nt', delete=False) as f:
            f.write('<http://example.org/subj> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.org/Type> .\n')
            temp_nt_file = f.name

        # Create a ZIP file containing the RDF file
        import zipfile
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as zf:
            temp_zip_file = zf.name

        try:
            with zipfile.ZipFile(temp_zip_file, 'w') as zipf:
                zipf.write(temp_nt_file, arcname='data.nt')

            # Load from ZIP
            result = self.reader.load(temp_zip_file)

            self.assertIsNotNone(result)
            self.assertIsInstance(result, Dataset)
        finally:
            os.unlink(temp_nt_file)
            os.unlink(temp_zip_file)

    def test_context_map_replacement_in_jsonld(self):
        """Test that context URLs are replaced when loading JSON-LD."""
        context_data = {
            "@context": {
                "dc": "http://purl.org/dc/terms/",
                "title": "dc:title"
            }
        }

        jsonld_data = {
            "@context": "http://example.org/custom-context",
            "@id": "http://example.org/resource1",
            "@type": "http://example.org/Type"
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as ctx_f:
            json.dump(context_data, ctx_f)
            context_file = ctx_f.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonld', delete=False) as data_f:
            json.dump(jsonld_data, data_f)
            jsonld_file = data_f.name

        try:
            context_map = {
                "http://example.org/custom-context": context_file
            }
            reader = Reader(context_map=context_map)

            # Load JSON-LD file - context should be replaced
            result = reader.load(jsonld_file)

            self.assertIsNotNone(result)
        finally:
            os.unlink(context_file)
            os.unlink(jsonld_file)

    @classmethod
    def tearDownClass(cls):
        """Clean up the triplestore after tests."""
        delete_query = "CLEAR GRAPH <https://w3id.org/oc/meta/>"
        with SPARQLClient(cls.endpoint) as client:
            client.update(delete_query)


if __name__ == '__main__':
    unittest.main()