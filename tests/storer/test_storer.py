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
import gzip
import hashlib
import json
import os
import re
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from zipfile import ZipFile
from multiprocessing import Pool
from SPARQLWrapper import POST, SPARQLWrapper

from rdflib import Dataset, Graph, URIRef, compare
from rdflib.compare import to_isomorphic, graph_diff

from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.prov.prov_set import ProvSet
from oc_ocdm.storer import Storer
from oc_ocdm.reader import Reader
from oc_ocdm.support.reporter import Reporter
from oc_ocdm.support.query_utils import serialize_graph_to_nquads

from shutil import rmtree


def dataset_to_graph(dataset: Dataset) -> Graph:
    """Convert a Dataset to a Graph for comparison purposes by flattening all quads."""
    g = Graph()
    for s, p, o, _ in dataset.quads((None, None, None, None)):
        g.add((s, p, o))
    return g


class TestStorer(unittest.TestCase):
    ts = 'http://127.0.0.1:8804/sparql'

    def reset_server(self, server:str=ts) -> None:
        ts = SPARQLWrapper(server)
        for graph in {'https://w3id.org/oc/meta/br/', 'https://w3id.org/oc/meta/ra/', 'https://w3id.org/oc/meta/re/', 'https://w3id.org/oc/meta/id/', 'https://w3id.org/oc/meta/ar/', 'http://default.graph/'}:
            ts.setQuery(f'CLEAR GRAPH <{graph}>')
            ts.setMethod(POST)
            ts.query()

    def setUp(self):
        self.resp_agent = "http://resp_agent.test/"
        self.base_iri = "http://test/"
        self.ts = self.ts
        self.graph_set = GraphSet(self.base_iri, "", "060", False)
        self.prov_set = ProvSet(self.graph_set, self.base_iri, "", False)
        self.br = self.graph_set.add_br(self.resp_agent)
        self.data_dir = os.path.join("tests", "storer", "data")
        self.prov_dir = os.path.join("tests", "storer", "test_provenance")
        self.info_dir = os.path.join(self.prov_dir, "info_dir")
        self.reset_server()

    def tearDown(self):
        if os.path.exists(self.data_dir):
            rmtree(self.data_dir)
        if os.path.exists(self.prov_dir):
            rmtree(os.path.join(self.prov_dir))

    def test_store_graphs_in_file(self):
        base_dir = os.path.join("tests", "storer", "data", "rdf") + os.sep
        with self.subTest("output_format=json-ld, zip_output=True"):
            modified_entities = self.prov_set.generate_provenance()
            prov_storer = Storer(self.prov_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='json-ld', zip_output=True)
            storer = Storer(self.graph_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='json-ld', zip_output=True, modified_entities=modified_entities)
            storer.store_all(base_dir, self.base_iri)
            prov_storer.store_all(base_dir, self.base_iri)
            self.graph_set.commit_changes()
            with ZipFile(os.path.join(base_dir, "br", "060", "10000", "1000.zip"), mode="r") as archive:
                with archive.open("1000.json") as f:
                    data = json.load(f)
                    self.assertEqual(data, [{'@graph': [{'@id': 'http://test/br/0601', '@type': ['http://purl.org/spar/fabio/Expression']}], '@id': 'http://test/br/'}])
            with ZipFile(os.path.join(base_dir, "br", "060", "10000", "1000", "prov", "se.zip"), mode="r") as archive:
                with archive.open("se.json") as f:
                    data = [{g:[{k:v for k,v in datum.items() if k != "http://www.w3.org/ns/prov#generatedAtTime"} for datum in data] if g == "@graph" else data for g, data in graph.items()} for graph in json.load(f)]
                    self.assertEqual(data, [{'@graph': [{
                        '@id': 'http://test/br/0601/prov/se/1', 
                        '@type': ['http://www.w3.org/ns/prov#Entity'], 
                        'http://purl.org/dc/terms/description': [{'@type': 'http://www.w3.org/2001/XMLSchema#string', '@value': "The entity 'http://test/br/0601' has been created."}], 
                        'http://www.w3.org/ns/prov#specializationOf': [{'@id': 'http://test/br/0601'}], 
                        'http://www.w3.org/ns/prov#wasAttributedTo': [{'@id': 'http://resp_agent.test/'}]}], '@id': 'http://test/br/0601/prov/'}])
        with self.subTest("output_format=json-ld, zip_output=False"):
            base_dir_1 = os.path.join("tests", "storer", "data", "rdf_1") + os.sep
            storer = Storer(self.graph_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='json-ld', zip_output=False)
            self.prov_set.generate_provenance()
            prov_storer = Storer(self.prov_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='json-ld', zip_output=False)
            storer.store_all(base_dir_1, self.base_iri)
            prov_storer.store_all(base_dir_1, self.base_iri)
            self.graph_set.commit_changes()
            with open(os.path.join(base_dir_1, "br", "060", "10000", "1000.json")) as f:
                data = json.load(f)
                self.assertEqual(data, [{'@graph': [{'@id': 'http://test/br/0601', '@type': ['http://purl.org/spar/fabio/Expression']}], '@id': 'http://test/br/'}])
            with open(os.path.join(base_dir_1, "br", "060", "10000", "1000", "prov", "se.json")) as f:
                data = [{g:[{k:v for k,v in datum.items() if k != "http://www.w3.org/ns/prov#generatedAtTime"} for datum in data] if g == "@graph" else data for g, data in graph.items()} for graph in json.load(f)]
                self.assertEqual(data, [{'@graph': [{
                    '@id': 'http://test/br/0601/prov/se/1', 
                    '@type': ['http://www.w3.org/ns/prov#Entity'], 
                    'http://purl.org/dc/terms/description': [{'@type': 'http://www.w3.org/2001/XMLSchema#string', '@value': "The entity 'http://test/br/0601' has been created."}], 
                    'http://www.w3.org/ns/prov#specializationOf': [{'@id': 'http://test/br/0601'}], 
                    'http://www.w3.org/ns/prov#wasAttributedTo': [{'@id': 'http://resp_agent.test/'}]}], '@id': 'http://test/br/0601/prov/'}])
        with self.subTest("output_format=nquads, zip_output=True"):
            base_dir_2 = os.path.join("tests", "storer", "data", "rdf_2") + os.sep
            storer = Storer(self.graph_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='nquads', zip_output=True)
            self.prov_set.generate_provenance()
            prov_storer = Storer(self.prov_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='nquads', zip_output=True)
            storer.store_all(base_dir_2, self.base_iri)
            prov_storer.store_all(base_dir_2, self.base_iri)
            self.graph_set.commit_changes()
            with ZipFile(os.path.join(base_dir_2, "br", "060", "10000", "1000.zip"), mode="r") as archive:
                with archive.open("1000.nt") as f:
                    data = f.read().decode("utf-8")
                    self.assertEqual(data, "<http://test/br/0601> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/spar/fabio/Expression> <http://test/br/> .\n\n")
            with ZipFile(os.path.join(base_dir_2, "br", "060", "10000", "1000", "prov", "se.zip"), mode="r") as archive:
                with archive.open("se.nq") as f:
                    data = f.read().decode("utf-8")
                    data_g = Dataset()
                    expected_data_g = Dataset()
                    data_g.parse(data=data, format="nquads")
                    expected_data_g.parse(data="""
                        <http://test/br/0601/prov/se/1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/prov#Entity> <http://test/br/0601/prov/> .
                        <http://test/br/0601/prov/se/1> <http://www.w3.org/ns/prov#specializationOf> <http://test/br/0601> <http://test/br/0601/prov/> .
                        <http://test/br/0601/prov/se/1> <http://www.w3.org/ns/prov#wasAttributedTo> <http://resp_agent.test/> <http://test/br/0601/prov/> .
                        <http://test/br/0601/prov/se/1> <http://purl.org/dc/terms/description> "The entity 'http://test/br/0601' has been created."^^<http://www.w3.org/2001/XMLSchema#string> <http://test/br/0601/prov/> .
                    """, format="nquads")
                    for s, p, o, c in data_g.quads():
                        if p == URIRef("http://www.w3.org/ns/prov#generatedAtTime"):
                            data_g.remove((s, p, o, c))
                    self.assertTrue(compare.isomorphic(dataset_to_graph(data_g), dataset_to_graph(expected_data_g)))
        with self.subTest("output_format=nquads, zip_output=False"):
            base_dir_3 = os.path.join("tests", "storer", "data", "rdf_3") + os.sep
            storer = Storer(self.graph_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='nquads', zip_output=False)
            self.prov_set.generate_provenance()
            prov_storer = Storer(self.prov_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='nquads', zip_output=False)
            storer.store_all(base_dir_3, self.base_iri)
            prov_storer.store_all(base_dir_3, self.base_iri)
            self.graph_set.commit_changes()
            prov_unzipped = Dataset()
            expected_prov_unzipped = Dataset()
            with open(os.path.join(base_dir_3, "br", "060", "10000", "1000.nt"), "r", encoding="utf-8") as f:
                data_unzipped = f.read()
            prov_unzipped.parse(source=os.path.join(base_dir_3, "br", "060", "10000", "1000", "prov", "se.nq"), format="nquads")
            expected_prov_unzipped.parse(data="""
                <http://test/br/0601/prov/se/1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/prov#Entity> <http://test/br/0601/prov/> .
                <http://test/br/0601/prov/se/1> <http://www.w3.org/ns/prov#specializationOf> <http://test/br/0601> <http://test/br/0601/prov/> .
                <http://test/br/0601/prov/se/1> <http://www.w3.org/ns/prov#wasAttributedTo> <http://resp_agent.test/> <http://test/br/0601/prov/> .
                <http://test/br/0601/prov/se/1> <http://purl.org/dc/terms/description> "The entity 'http://test/br/0601' has been created."^^<http://www.w3.org/2001/XMLSchema#string> <http://test/br/0601/prov/> .
            """, format="nquads")
            for s, p, o, c in prov_unzipped.quads():
                if p == URIRef("http://www.w3.org/ns/prov#generatedAtTime"):
                    prov_unzipped.remove((s, p, o, c))
            self.assertEqual(data_unzipped, "<http://test/br/0601> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/spar/fabio/Expression> <http://test/br/> .\n\n")
            self.assertTrue(compare.isomorphic(dataset_to_graph(prov_unzipped), dataset_to_graph(expected_prov_unzipped)))

    def test_store_graphs_in_file_multiprocessing(self):
        base_dir = os.path.join("tests", "storer", "data", "multiprocessing") + os.sep
        storer = Storer(self.graph_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='json-ld', zip_output=False)
        self.prov_set.generate_provenance()
        prov_storer = Storer(self.prov_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='json-ld', zip_output=False)
        storer.store_all(base_dir, self.base_iri, process_id=7)
        prov_storer.store_all(base_dir, self.base_iri, process_id=7)
        with open(os.path.join(base_dir, "br", "060", "10000", "1000_7.json")) as f:
            data = json.load(f)
            self.assertEqual(data, [{'@graph': [{'@id': 'http://test/br/0601', '@type': ['http://purl.org/spar/fabio/Expression']}], '@id': 'http://test/br/'}])
        with open(os.path.join(base_dir, "br", "060", "10000", "1000", "prov", "se_7.json")) as f:
            data = [{g:[{k:v for k,v in datum.items() if k != "http://www.w3.org/ns/prov#generatedAtTime"} for datum in data] if g == "@graph" else data for g, data in graph.items()} for graph in json.load(f)]
            self.assertEqual(data, [{'@graph': [{
                '@id': 'http://test/br/0601/prov/se/1', 
                '@type': ['http://www.w3.org/ns/prov#Entity'], 
                'http://purl.org/dc/terms/description': [{'@type': 'http://www.w3.org/2001/XMLSchema#string', '@value': "The entity 'http://test/br/0601' has been created."}], 
                'http://www.w3.org/ns/prov#specializationOf': [{'@id': 'http://test/br/0601'}], 
                'http://www.w3.org/ns/prov#wasAttributedTo': [{'@id': 'http://resp_agent.test/'}]}], '@id': 'http://test/br/0601/prov/'}])

    def test_provenance(self):
        graph_set = GraphSet(self.base_iri, "", "060", False)
        prov_set = ProvSet(graph_set, self.base_iri, info_dir=self.info_dir)
        base_dir = os.path.join("tests", "storer", "test_provenance") + os.sep
        graph_set.add_br(self.resp_agent)
        graph_set.add_br(self.resp_agent)
        graph_set.add_br(self.resp_agent)
        prov_set.generate_provenance()
        storer = Storer(graph_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='json-ld', zip_output=False)
        prov_storer = Storer(prov_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='json-ld', zip_output=False)
        prov_storer.store_all(base_dir, self.base_iri)
        storer.upload_all(self.ts, base_dir)
        graph_set.commit_changes()
        entities_to_process = [('http://test/br/0601',), ('http://test/br/0602',), ('http://test/br/0603',)]
        with Pool(processes=3) as pool:
            pool.starmap(process_entity, entities_to_process)

    def test_store_graphs_save_queries(self):
        base_dir = os.path.join("tests", "storer", "data", "rdf_save_queries") + os.sep
        storer = Storer(self.graph_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='json-ld', zip_output=False)
        self.prov_set.generate_provenance()
        prov_storer = Storer(self.prov_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='json-ld', zip_output=False)
        storer.store_all(base_dir, self.base_iri)
        prov_storer.store_all(base_dir, self.base_iri)

        to_be_uploaded_dir = os.path.join(base_dir, "to_be_uploaded")
        storer.upload_all(self.ts, base_dir, save_queries=True)

        # Check that the to_be_uploaded directory exists
        self.assertTrue(os.path.exists(to_be_uploaded_dir))

        # Check that there is at least one file in the to_be_uploaded directory
        saved_queries = os.listdir(to_be_uploaded_dir)
        self.assertGreater(len(saved_queries), 0)

        # Check the content of one of the saved files
        query_file = os.path.join(to_be_uploaded_dir, saved_queries[0])
        with open(query_file, 'r', encoding='utf-8') as f:
            query_content = f.read()
            self.assertIn("INSERT DATA", query_content)

    def test_save_query_hash_determinism(self):
        """Test that _save_query uses deterministic hash-based filenames."""
        base_dir = os.path.join("tests", "storer", "data", "hash_determinism") + os.sep
        to_be_uploaded_dir = os.path.join(base_dir, "to_be_uploaded")
        os.makedirs(to_be_uploaded_dir, exist_ok=True)

        try:
            storer = Storer(self.graph_set, output_format='json-ld', zip_output=False)

            # Test 1: Same query generates same filename
            query1 = "INSERT DATA { <http://example.org/s1> <http://example.org/p1> <http://example.org/o1> . }"
            storer._save_query(query1, to_be_uploaded_dir, added_statements=1, removed_statements=0)
            files_after_first = set(os.listdir(to_be_uploaded_dir))
            self.assertEqual(len(files_after_first), 1)
            first_filename = list(files_after_first)[0]

            # Save the same query again
            storer._save_query(query1, to_be_uploaded_dir, added_statements=1, removed_statements=0)
            files_after_second = set(os.listdir(to_be_uploaded_dir))

            # Should still be only one file (same filename, overwritten)
            self.assertEqual(len(files_after_second), 1)
            self.assertEqual(files_after_first, files_after_second)

            # Test 2: Different query generates different filename
            query2 = "INSERT DATA { <http://example.org/s2> <http://example.org/p2> <http://example.org/o2> . }"
            storer._save_query(query2, to_be_uploaded_dir, added_statements=1, removed_statements=0)
            files_after_third = set(os.listdir(to_be_uploaded_dir))

            # Should now have two files
            self.assertEqual(len(files_after_third), 2)
            self.assertNotEqual(files_after_first, files_after_third)

            # Test 3: Verify filename format matches pattern {hash}_add{n}_remove{m}.sparql
            filename_pattern = re.compile(r'^[a-f0-9]{16}_add\d+_remove\d+\.sparql$')
            for filename in files_after_third:
                self.assertIsNotNone(filename_pattern.match(filename),
                                     f"Filename '{filename}' does not match expected pattern")

            # Test 4: Verify hash is correctly computed
            expected_hash = hashlib.sha256(query1.encode('utf-8')).hexdigest()[:16]
            expected_filename = f"{expected_hash}_add1_remove0.sparql"
            self.assertIn(expected_filename, files_after_third)

            # Test 5: Verify saved content matches original query
            saved_file_path = os.path.join(to_be_uploaded_dir, expected_filename)
            with open(saved_file_path, 'r', encoding='utf-8') as f:
                saved_content = f.read()
            self.assertEqual(saved_content, query1)

        finally:
            if os.path.exists(base_dir):
                rmtree(base_dir)

    def test_unsupported_output_format(self):
        """Test that ValueError is raised for unsupported output formats."""
        with self.assertRaises(ValueError) as context:
            Storer(self.graph_set, output_format='unsupported_format')
        self.assertIn("not supported", str(context.exception))

    def test_custom_reporters(self):
        """Test storer initialization with custom reporters."""
        custom_repok = Reporter(prefix="[Custom OK] ")
        custom_reperr = Reporter(prefix="[Custom ERROR] ")

        storer = Storer(self.graph_set, repok=custom_repok, reperr=custom_reperr)

        self.assertEqual(storer.repok.prefix, "[Custom OK] ")
        self.assertEqual(storer.reperr.prefix, "[Custom ERROR] ")

    def test_context_map_file_loading(self):
        """Test loading JSON-LD context from file in storer."""
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
            storer = Storer(self.graph_set, context_map=context_map, output_format='json-ld')

            # Verify the context was loaded from file
            self.assertIn("http://example.org/context", storer.context_map)
            self.assertEqual(storer.context_map["http://example.org/context"], context_data)
        finally:
            os.unlink(context_file)

    def test_store_graphs_in_file(self):
        """Test the store_graphs_in_file method."""
        base_dir = os.path.join("tests", "storer", "data", "direct_store") + os.sep
        os.makedirs(base_dir, exist_ok=True)

        try:
            file_path = os.path.join(base_dir, "output.json")
            storer = Storer(self.graph_set, output_format='json-ld', zip_output=False)

            storer.store_graphs_in_file(file_path)

            # Verify file was created
            self.assertTrue(os.path.exists(file_path))

            # Verify content
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.assertIsInstance(data, list)
                self.assertGreater(len(data), 0)
        finally:
            if os.path.exists(base_dir):
                rmtree(base_dir)

    def test_upload_with_failure_marker(self):
        """Test SPARQL upload that creates failure markers on error."""
        base_dir = os.path.join("tests", "storer", "data", "rdf_upload_fail") + os.sep
        storer = Storer(self.graph_set, output_format='json-ld', zip_output=False)
        storer.store_all(base_dir, self.base_iri)

        try:
            # Mock SPARQLWrapper to simulate failure
            with patch('SPARQLWrapper.SPARQLWrapper.query') as mock_query:
                mock_query.side_effect = Exception("Connection failed")

                # This should create failure markers
                try:
                    storer.upload_all("http://invalid-endpoint:9999/sparql", base_dir)
                except:
                    pass  # Expected to fail

                # Check that failure marker files were created
                for root, dirs, files in os.walk(base_dir):
                    for file in files:
                        if file.endswith('.json'):
                            marker_file = os.path.join(root, file + '.failed')
                            # Failure markers should exist
                            if os.path.exists(marker_file):
                                self.assertTrue(True)
                                return
        finally:
            if os.path.exists(base_dir):
                rmtree(base_dir)

    def test_zip_output_with_ntriples(self):
        """Test ZIP output with N-Triples format."""
        base_dir = os.path.join("tests", "storer", "data", "zip_nt") + os.sep
        storer = Storer(self.graph_set, output_format='nt', zip_output=True)
        storer.store_all(base_dir, self.base_iri)

        try:
            # Find the generated ZIP file
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file.endswith('.zip'):
                        zip_path = os.path.join(root, file)
                        with ZipFile(zip_path, 'r') as zf:
                            # Check that ZIP contains .nt file
                            names = zf.namelist()
                            self.assertTrue(any(name.endswith('.nt') for name in names))
                            return
            self.fail("No ZIP file found")
        finally:
            if os.path.exists(base_dir):
                rmtree(base_dir)

    def test_upload_all_with_modified_entities_filtering(self):
        """Test that upload_all filters entities based on modified_entities."""
        base_dir = os.path.join("tests", "storer", "data", "modified_entities_filter") + os.sep

        br1 = self.graph_set.add_br(self.resp_agent)
        br1.has_title("First Resource")
        br2 = self.graph_set.add_br(self.resp_agent)
        br2.has_title("Second Resource")
        br3 = self.graph_set.add_br(self.resp_agent)
        br3.has_title("Third Resource")

        modified_entities = {URIRef(br1.res), URIRef(br3.res)}

        storer = Storer(self.graph_set, modified_entities=modified_entities)
        result = storer.upload_all(self.ts, base_dir, save_queries=True)

        try:
            self.assertTrue(result)
            to_be_uploaded_dir = os.path.join(base_dir, "to_be_uploaded")
            self.assertTrue(os.path.exists(to_be_uploaded_dir))

            query_files = [f for f in os.listdir(to_be_uploaded_dir) if f.endswith('.sparql')]
            self.assertGreater(len(query_files), 0)

            all_queries_content = ""
            for query_file in query_files:
                with open(os.path.join(to_be_uploaded_dir, query_file), 'r') as f:
                    all_queries_content += f.read()

            self.assertIn(str(br1.res), all_queries_content)
            self.assertNotIn(str(br2.res), all_queries_content)
            self.assertIn(str(br3.res), all_queries_content)

        finally:
            if os.path.exists(base_dir):
                rmtree(base_dir)

    def test_upload_all_save_queries_with_provenance_entities(self):
        """Test save_queries includes prov entities for modified graph entities."""
        base_dir = os.path.join("tests", "storer", "data", "prov_queries") + os.sep

        br1 = self.graph_set.add_br(self.base_iri + "br/1")
        br1.has_title("Resource with Provenance")

        prov_set = ProvSet(self.graph_set, self.base_iri, info_dir=os.path.join(base_dir, "info_dir"))
        modified_entities = prov_set.generate_provenance()

        storer = Storer(self.graph_set, modified_entities=modified_entities)
        prov_storer = Storer(prov_set, modified_entities=modified_entities)

        result = storer.upload_all(self.ts, base_dir, save_queries=True)
        prov_result = prov_storer.upload_all(self.ts, base_dir, save_queries=True)

        try:
            self.assertTrue(result)
            self.assertTrue(prov_result)

            to_be_uploaded_dir = os.path.join(base_dir, "to_be_uploaded")
            query_files = [f for f in os.listdir(to_be_uploaded_dir) if f.endswith('.sparql')]
            self.assertGreater(len(query_files), 0)

            all_queries_content = ""
            for query_file in query_files:
                with open(os.path.join(to_be_uploaded_dir, query_file), 'r') as f:
                    content = f.read()
                    all_queries_content += content

            self.assertIn("INSERT DATA", all_queries_content)
            self.assertIn("/prov/se/", all_queries_content)

        finally:
            if os.path.exists(base_dir):
                rmtree(base_dir)

    def test_upload_all_separate_inserts_deletes(self):
        """Test upload_all with separate_inserts_deletes parameter."""
        test_graph_set = GraphSet(self.base_iri, "", "060", False)

        br = test_graph_set.add_br(self.resp_agent)
        br.has_title("Test Title")

        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        br.has_subtitle("New Subtitle")

        expected_insert_graph = Graph()
        for s, p, o in br.g:
            if (s, p, o) not in br.preexisting_graph:
                expected_insert_graph.add((s, p, o))

        self.assertEqual(len(expected_insert_graph), 1)

        base_dir = os.path.join("tests", "storer", "data", "separate_queries")
        os.makedirs(base_dir, exist_ok=True)

        storer = Storer(test_graph_set, output_format='json-ld')
        result = storer.upload_all(
            self.ts,
            base_dir=base_dir,
            batch_size=10,
            save_queries=True,
            separate_inserts_deletes=True
        )

        self.assertTrue(result)

        to_be_uploaded_dir = os.path.join(base_dir, "to_be_uploaded")
        self.assertTrue(os.path.exists(to_be_uploaded_dir))

        sparql_files = [f for f in os.listdir(to_be_uploaded_dir) if f.endswith('.sparql')]

        insert_files = [f for f in sparql_files if 'add' in f and 'remove0' in f]
        delete_files = [f for f in sparql_files if 'remove' in f and not 'remove0' in f]

        self.assertEqual(len(insert_files), 1)
        self.assertEqual(len(delete_files), 0)

        insert_file = insert_files[0]
        parts = insert_file.split('_')
        add_count = int(parts[1].replace('add', ''))
        remove_count = int(parts[2].replace('remove', '').replace('.sparql', ''))
        self.assertEqual(add_count, 1)
        self.assertEqual(remove_count, 0)

        with open(os.path.join(to_be_uploaded_dir, insert_file), 'r') as f:
            content = f.read()
            self.assertIn("INSERT DATA", content)
            self.assertNotIn("DELETE DATA", content)
            self.assertIn(str(br.res), content)
            self.assertIn("New Subtitle", content)
            self.assertIn("hasSubtitle", content)

    def test_upload_all_save_inserts_as_nquads(self):
        """Test upload_all with save_inserts_as_nquads parameter."""
        test_graph_set = GraphSet(self.base_iri, "", "060", False)

        br = test_graph_set.add_br(self.resp_agent)
        br.has_title("Test Title")
        br.has_subtitle("Test Subtitle")

        ar = test_graph_set.add_ar(self.resp_agent)

        expected_br_quads = set(quad.rstrip('\n') for quad in serialize_graph_to_nquads(br.g, br.g.identifier))
        expected_ar_quads = set(quad.rstrip('\n') for quad in serialize_graph_to_nquads(ar.g, ar.g.identifier))
        expected_all_quads = expected_br_quads | expected_ar_quads

        base_dir = os.path.join("tests", "storer", "data", "nquads_test")
        nquads_output_dir = os.path.join(base_dir, "nquads")
        os.makedirs(base_dir, exist_ok=True)

        storer = Storer(test_graph_set, output_format='json-ld')
        result = storer.upload_all(
            self.ts,
            base_dir=base_dir,
            batch_size=10,
            separate_inserts_deletes=True,
            save_inserts_as_nquads=True,
            nquads_output_dir=nquads_output_dir,
            nquads_batch_size=100
        )

        self.assertTrue(result)
        self.assertTrue(os.path.exists(nquads_output_dir))

        nquads_files = sorted([f for f in os.listdir(nquads_output_dir) if f.endswith('.nq.gz')])
        self.assertEqual(len(nquads_files), 1)

        all_quads_from_file = []
        for nquads_file in nquads_files:
            file_path = os.path.join(nquads_output_dir, nquads_file)
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                content = f.read()
                lines = [line.rstrip('\n') for line in content.split('\n') if line.strip()]
                all_quads_from_file.extend(lines)

        actual_quads = set(all_quads_from_file)

        self.assertEqual(len(actual_quads), len(expected_all_quads))
        self.assertEqual(actual_quads, expected_all_quads)

        to_be_uploaded_dir = os.path.join(base_dir, "to_be_uploaded")
        if os.path.exists(to_be_uploaded_dir):
            sparql_files = [f for f in os.listdir(to_be_uploaded_dir) if f.endswith('.sparql')]
            insert_sparql_files = [f for f in sparql_files if 'INSERT DATA' in open(os.path.join(to_be_uploaded_dir, f)).read()]
            self.assertEqual(len(insert_sparql_files), 0)

    def test_write_nquads_file(self):
        """Test _write_nquads_file method with batching."""
        br = self.graph_set.add_br(self.resp_agent)
        br.has_title("Test Title")

        nquads_expected = serialize_graph_to_nquads(br.g, br.g.identifier)
        expected_set = set(nquads_expected)

        output_dir = os.path.join("tests", "storer", "data", "nquads_write_test")
        os.makedirs(output_dir, exist_ok=True)

        storer = Storer(self.graph_set, output_format='json-ld')
        storer.repok.new_article()
        storer._write_nquads_file(nquads_expected, output_dir, 0)

        expected_file = os.path.join(output_dir, "bulk_load_00000.nq.gz")
        self.assertTrue(os.path.exists(expected_file))

        with gzip.open(expected_file, 'rt', encoding='utf-8') as f:
            content = f.read()
            lines = [line.rstrip('\n') for line in content.split('\n') if line.strip()]
            actual_set = set(lines)

        expected_set_normalized = {line.rstrip('\n') for line in expected_set}

        self.assertEqual(len(actual_set), len(expected_set_normalized))
        self.assertEqual(actual_set, expected_set_normalized)

        second_batch = ["<http://example.org/s> <http://example.org/p> <http://example.org/o> <http://example.org/g> .\n"]
        expected_second = set(second_batch)

        storer._write_nquads_file(second_batch, output_dir, 1)

        second_file = os.path.join(output_dir, "bulk_load_00001.nq.gz")
        self.assertTrue(os.path.exists(second_file))

        with gzip.open(second_file, 'rt', encoding='utf-8') as f:
            content = f.read()
            lines = [line.rstrip('\n') for line in content.split('\n') if line.strip()]
            actual_second = set(lines)

        expected_second_normalized = {line.rstrip('\n') for line in expected_second}

        self.assertEqual(len(actual_second), 1)
        self.assertEqual(actual_second, expected_second_normalized)

    def test_upload_all_separate_with_deletes(self):
        """Test upload_all with DELETE queries when entities are modified and deleted."""
        test_graph_set = GraphSet(self.base_iri, "", "060", False)

        br = test_graph_set.add_br(self.resp_agent)
        br.has_title("Original Title")
        br.has_subtitle("Original Subtitle")

        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        br.remove_title()
        br.has_title("Modified Title")

        _, br_to_delete, br_to_insert = graph_diff(to_isomorphic(br.preexisting_graph), to_isomorphic(br.g))
        expected_br_insert_count = len(br_to_insert)
        expected_br_delete_count = len(br_to_delete)

        self.assertEqual(expected_br_insert_count, 1)
        self.assertEqual(expected_br_delete_count, 1)

        br2 = test_graph_set.add_br(self.resp_agent)
        br2.has_title("To Be Deleted")
        br2.preexisting_graph = Graph(identifier=br2.g.identifier)
        for triple in br2.g:
            br2.preexisting_graph.add(triple)
        expected_br2_delete_count = len(br2.preexisting_graph)
        br2.mark_as_to_be_deleted()

        expected_total_insert = expected_br_insert_count
        expected_total_delete = expected_br_delete_count + expected_br2_delete_count

        base_dir = os.path.join("tests", "storer", "data", "separate_with_deletes")
        os.makedirs(base_dir, exist_ok=True)

        storer = Storer(test_graph_set, output_format='json-ld')
        result = storer.upload_all(
            self.ts,
            base_dir=base_dir,
            batch_size=10,
            save_queries=True,
            separate_inserts_deletes=True
        )

        self.assertTrue(result)

        to_be_uploaded_dir = os.path.join(base_dir, "to_be_uploaded")
        self.assertTrue(os.path.exists(to_be_uploaded_dir))

        sparql_files = [f for f in os.listdir(to_be_uploaded_dir) if f.endswith('.sparql')]

        insert_files = []
        delete_files = []

        for file in sparql_files:
            with open(os.path.join(to_be_uploaded_dir, file), 'r') as f:
                content = f.read()
                if "INSERT DATA" in content:
                    self.assertNotIn("DELETE DATA", content)
                    insert_files.append((file, content))
                elif "DELETE DATA" in content:
                    self.assertNotIn("INSERT DATA", content)
                    delete_files.append((file, content))

        self.assertEqual(len(insert_files), 1)
        self.assertEqual(len(delete_files), 1)

        insert_file, insert_content = insert_files[0]
        parts = insert_file.split('_')
        add_count = int(parts[1].replace('add', ''))
        remove_count = int(parts[2].replace('remove', '').replace('.sparql', ''))
        self.assertEqual(add_count, expected_total_insert)
        self.assertEqual(remove_count, 0)
        self.assertIn("Modified Title", insert_content)
        self.assertIn(str(br.res), insert_content)

        delete_file, delete_content = delete_files[0]
        parts = delete_file.split('_')
        add_count = int(parts[1].replace('add', ''))
        remove_count = int(parts[2].replace('remove', '').replace('.sparql', ''))
        self.assertEqual(add_count, 0)
        self.assertEqual(remove_count, expected_total_delete)
        self.assertIn(str(br.res), delete_content)
        self.assertIn(str(br2.res), delete_content)

    def test_upload_all_nquads_inserts_sparql_deletes(self):
        """Test that INSERT queries go to nquads and DELETE queries go to SPARQL files."""
        test_graph_set = GraphSet(self.base_iri, "", "060", False)

        br = test_graph_set.add_br(self.resp_agent)
        br.has_title("Original Title")
        br.has_subtitle("Original Subtitle")

        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        br.remove_title()
        br.has_title("Modified Title")

        _, br_to_delete, br_to_insert = graph_diff(to_isomorphic(br.preexisting_graph), to_isomorphic(br.g))

        expected_insert_quads = set(quad.rstrip('\n') for quad in serialize_graph_to_nquads(br_to_insert, br.g.identifier))
        expected_delete_count = len(br_to_delete)

        base_dir = os.path.join("tests", "storer", "data", "nquads_sparql_mixed")
        nquads_output_dir = os.path.join(base_dir, "nquads")
        os.makedirs(base_dir, exist_ok=True)

        storer = Storer(test_graph_set, output_format='json-ld')
        result = storer.upload_all(
            self.ts,
            base_dir=base_dir,
            batch_size=10,
            separate_inserts_deletes=True,
            save_inserts_as_nquads=True,
            nquads_output_dir=nquads_output_dir,
            nquads_batch_size=100
        )

        self.assertTrue(result)

        nquads_files = [f for f in os.listdir(nquads_output_dir) if f.endswith('.nq.gz')]
        self.assertEqual(len(nquads_files), 1)

        actual_insert_quads = []
        for nquads_file in nquads_files:
            file_path = os.path.join(nquads_output_dir, nquads_file)
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                content = f.read()
                lines = [line.rstrip('\n') for line in content.split('\n') if line.strip()]
                actual_insert_quads.extend(lines)

        actual_insert_set = set(actual_insert_quads)
        self.assertEqual(actual_insert_set, expected_insert_quads)

        to_be_uploaded_dir = os.path.join(base_dir, "to_be_uploaded")
        self.assertTrue(os.path.exists(to_be_uploaded_dir))

        sparql_files = [f for f in os.listdir(to_be_uploaded_dir) if f.endswith('.sparql')]

        insert_sparql_files = []
        delete_sparql_files = []

        for file in sparql_files:
            with open(os.path.join(to_be_uploaded_dir, file), 'r') as f:
                content = f.read()
                if "INSERT DATA" in content:
                    insert_sparql_files.append(file)
                elif "DELETE DATA" in content:
                    delete_sparql_files.append(file)

        self.assertEqual(len(insert_sparql_files), 0)
        self.assertEqual(len(delete_sparql_files), 1)

        delete_file = delete_sparql_files[0]
        parts = delete_file.split('_')
        add_count = int(parts[1].replace('add', ''))
        remove_count = int(parts[2].replace('remove', '').replace('.sparql', ''))
        self.assertEqual(add_count, 0)
        self.assertEqual(remove_count, expected_delete_count)

    def test_upload_all_nquads_validation_errors(self):
        """Test upload_all parameter validation for N-Quads functionality."""
        storer = Storer(self.graph_set, output_format='json-ld')

        with self.subTest("missing_nquads_output_dir"):
            result = storer.upload_all(
                self.ts,
                base_dir="tests/storer/data/validation",
                save_inserts_as_nquads=True,
                separate_inserts_deletes=True
            )
            self.assertFalse(result)

        with self.subTest("separate_inserts_deletes_not_enabled"):
            result = storer.upload_all(
                self.ts,
                base_dir="tests/storer/data/validation",
                save_inserts_as_nquads=True,
                nquads_output_dir="tests/storer/data/validation/nquads"
            )
            self.assertFalse(result)


def process_entity(entity):
    base_iri = "http://test/"
    ts = 'http://127.0.0.1:8804/sparql'
    resp_agent = "http://resp_agent.test/"
    base_dir = os.path.join("tests", "storer", "test_provenance") + os.sep
    info_dir = os.path.join("tests", "storer", "test_provenance", "info_dir")
    graph_set = GraphSet(base_iri, "", "060", False)
    Reader.import_entity_from_triplestore(graph_set, ts, URIRef(entity), resp_agent)
    br = graph_set.get_entity(URIRef(entity))
    br.has_title("Hola")
    prov_set = ProvSet(graph_set, base_iri, info_dir=info_dir)
    prov_set.generate_provenance()
    storer = Storer(graph_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='json-ld', zip_output=False)
    prov_storer = Storer(prov_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='json-ld', zip_output=False)
    prov_storer.store_all(base_dir, base_iri)
    storer.upload_all(ts, base_dir)


if __name__ == '__main__':
    unittest.main()