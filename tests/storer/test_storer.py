#!/usr/bin/python

# SPDX-FileCopyrightText: 2025-2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import hashlib
import json
import os
import re
import tempfile
import unittest
from multiprocessing import Pool
from shutil import rmtree
from unittest.mock import patch
from zipfile import ZipFile

from rdflib import Dataset, Graph, URIRef, compare
from sparqlite import SPARQLClient
from triplelite import SubgraphView

from oc_ocdm.graph.entities.bibliographic.bibliographic_resource import BibliographicResource
from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.prov.prov_set import ProvSet
from oc_ocdm.reader import Reader, _expand_jsonld
from oc_ocdm.storer import Storer, _compact_jsonld, _entity_to_jsonld_dict
from oc_ocdm.support.reporter import Reporter


def dataset_to_graph(dataset: Dataset) -> Graph:
    """Convert a Dataset to a Graph for comparison purposes by flattening all quads."""
    g = Graph()
    for s, p, o, _ in dataset.quads((None, None, None, None)):
        g.add((s, p, o))
    return g


class TestStorer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ts = os.environ["SPARQL_TEST_ENDPOINT"]

    def reset_server(self) -> None:
        with SPARQLClient(self.ts) as client:
            for graph in {
                "https://w3id.org/oc/meta/br/",
                "https://w3id.org/oc/meta/ra/",
                "https://w3id.org/oc/meta/re/",
                "https://w3id.org/oc/meta/id/",
                "https://w3id.org/oc/meta/ar/",
                "http://default.graph/",
                "http://test/br/",
            }:
                client.update(f"CLEAR GRAPH <{graph}>")

    def setUp(self):
        self.resp_agent = "http://resp_agent.test/"
        self.base_iri = "http://test/"
        self.graph_set = GraphSet(self.base_iri, "", "060", False)
        self.prov_set = ProvSet(self.graph_set, self.base_iri, "", False)
        self.br = self.graph_set.add_br(self.resp_agent)
        self.data_dir = os.path.join("tests", "storer", "data")
        self.prov_dir = os.path.join("tests", "storer", "test_provenance")
        self.info_dir = os.path.join(self.prov_dir, "info_dir")
        if os.path.exists(self.data_dir):
            rmtree(self.data_dir)
        if os.path.exists(self.prov_dir):
            rmtree(self.prov_dir)

    def tearDown(self):
        if os.path.exists(self.data_dir):
            rmtree(self.data_dir)
        if os.path.exists(self.prov_dir):
            rmtree(os.path.join(self.prov_dir))

    def test_store_all(self):
        base_dir = os.path.join("tests", "storer", "data", "rdf") + os.sep
        with self.subTest("output_format=json-ld, zip_output=True"):
            modified_entities = self.prov_set.generate_provenance()
            prov_storer = Storer(
                self.prov_set,
                context_map={},
                dir_split=10000,
                n_file_item=1000,
                default_dir="_",
                output_format="json-ld",
                zip_output=True,
            )
            storer = Storer(
                self.graph_set,
                context_map={},
                dir_split=10000,
                n_file_item=1000,
                default_dir="_",
                output_format="json-ld",
                zip_output=True,
                modified_entities=modified_entities,
            )
            storer.store_all(base_dir, self.base_iri)
            prov_storer.store_all(base_dir, self.base_iri)
            self.graph_set.commit_changes()
            with ZipFile(os.path.join(base_dir, "br", "060", "10000", "1000.zip"), mode="r") as archive:
                with archive.open("1000.json") as f:
                    data = json.load(f)
                    self.assertEqual(
                        data,
                        [
                            {
                                "@graph": [
                                    {"@id": "http://test/br/0601", "@type": ["http://purl.org/spar/fabio/Expression"]}
                                ],
                                "@id": "http://test/br/",
                            }
                        ],
                    )
            with ZipFile(os.path.join(base_dir, "br", "060", "10000", "1000", "prov", "se.zip"), mode="r") as archive:
                with archive.open("se.json") as f:
                    data = [
                        {
                            g: [
                                {k: v for k, v in datum.items() if k != "http://www.w3.org/ns/prov#generatedAtTime"}
                                for datum in data
                            ]
                            if g == "@graph"
                            else data
                            for g, data in graph.items()
                        }
                        for graph in json.load(f)
                    ]
                    self.assertEqual(
                        data,
                        [
                            {
                                "@graph": [
                                    {
                                        "@id": "http://test/br/0601/prov/se/1",
                                        "@type": ["http://www.w3.org/ns/prov#Entity"],
                                        "http://purl.org/dc/terms/description": [
                                            {
                                                "@type": "http://www.w3.org/2001/XMLSchema#string",
                                                "@value": "The entity 'http://test/br/0601' has been created.",
                                            }
                                        ],
                                        "http://www.w3.org/ns/prov#specializationOf": [{"@id": "http://test/br/0601"}],
                                        "http://www.w3.org/ns/prov#wasAttributedTo": [
                                            {"@id": "http://resp_agent.test/"}
                                        ],
                                    }
                                ],
                                "@id": "http://test/br/0601/prov/",
                            }
                        ],
                    )
        with self.subTest("output_format=json-ld, zip_output=False"):
            base_dir_1 = os.path.join("tests", "storer", "data", "rdf_1") + os.sep
            storer = Storer(
                self.graph_set,
                context_map={},
                dir_split=10000,
                n_file_item=1000,
                default_dir="_",
                output_format="json-ld",
                zip_output=False,
            )
            self.prov_set.generate_provenance()
            prov_storer = Storer(
                self.prov_set,
                context_map={},
                dir_split=10000,
                n_file_item=1000,
                default_dir="_",
                output_format="json-ld",
                zip_output=False,
            )
            storer.store_all(base_dir_1, self.base_iri)
            prov_storer.store_all(base_dir_1, self.base_iri)
            self.graph_set.commit_changes()
            with open(os.path.join(base_dir_1, "br", "060", "10000", "1000.json")) as f:
                data = json.load(f)
                self.assertEqual(
                    data,
                    [
                        {
                            "@graph": [
                                {"@id": "http://test/br/0601", "@type": ["http://purl.org/spar/fabio/Expression"]}
                            ],
                            "@id": "http://test/br/",
                        }
                    ],
                )
            with open(os.path.join(base_dir_1, "br", "060", "10000", "1000", "prov", "se.json")) as f:
                data = [
                    {
                        g: [
                            {k: v for k, v in datum.items() if k != "http://www.w3.org/ns/prov#generatedAtTime"}
                            for datum in data
                        ]
                        if g == "@graph"
                        else data
                        for g, data in graph.items()
                    }
                    for graph in json.load(f)
                ]
                self.assertEqual(
                    data,
                    [
                        {
                            "@graph": [
                                {
                                    "@id": "http://test/br/0601/prov/se/1",
                                    "@type": ["http://www.w3.org/ns/prov#Entity"],
                                    "http://purl.org/dc/terms/description": [
                                        {
                                            "@type": "http://www.w3.org/2001/XMLSchema#string",
                                            "@value": "The entity 'http://test/br/0601' has been created.",
                                        }
                                    ],
                                    "http://www.w3.org/ns/prov#specializationOf": [{"@id": "http://test/br/0601"}],
                                    "http://www.w3.org/ns/prov#wasAttributedTo": [{"@id": "http://resp_agent.test/"}],
                                }
                            ],
                            "@id": "http://test/br/0601/prov/",
                        }
                    ],
                )
        with self.subTest("output_format=nquads, zip_output=True"):
            base_dir_2 = os.path.join("tests", "storer", "data", "rdf_2") + os.sep
            storer = Storer(
                self.graph_set,
                context_map={},
                dir_split=10000,
                n_file_item=1000,
                default_dir="_",
                output_format="nquads",
                zip_output=True,
            )
            self.prov_set.generate_provenance()
            prov_storer = Storer(
                self.prov_set,
                context_map={},
                dir_split=10000,
                n_file_item=1000,
                default_dir="_",
                output_format="nquads",
                zip_output=True,
            )
            storer.store_all(base_dir_2, self.base_iri)
            prov_storer.store_all(base_dir_2, self.base_iri)
            self.graph_set.commit_changes()
            with ZipFile(os.path.join(base_dir_2, "br", "060", "10000", "1000.zip"), mode="r") as archive:
                with archive.open("1000.nt") as f:
                    data = f.read().decode("utf-8")
                    self.assertEqual(
                        data,
                        "<http://test/br/0601> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/spar/fabio/Expression> <http://test/br/> .\n\n",
                    )
            with ZipFile(os.path.join(base_dir_2, "br", "060", "10000", "1000", "prov", "se.zip"), mode="r") as archive:
                with archive.open("se.nq") as f:
                    data = f.read().decode("utf-8")
                    data_g = Dataset()
                    expected_data_g = Dataset()
                    data_g.parse(data=data, format="nquads")
                    expected_data_g.parse(
                        data="""
                        <http://test/br/0601/prov/se/1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/prov#Entity> <http://test/br/0601/prov/> .
                        <http://test/br/0601/prov/se/1> <http://www.w3.org/ns/prov#specializationOf> <http://test/br/0601> <http://test/br/0601/prov/> .
                        <http://test/br/0601/prov/se/1> <http://www.w3.org/ns/prov#wasAttributedTo> <http://resp_agent.test/> <http://test/br/0601/prov/> .
                        <http://test/br/0601/prov/se/1> <http://purl.org/dc/terms/description> "The entity 'http://test/br/0601' has been created."^^<http://www.w3.org/2001/XMLSchema#string> <http://test/br/0601/prov/> .
                    """,
                        format="nquads",
                    )
                    for s, p, o, _ in data_g.quads():
                        if p == URIRef("http://www.w3.org/ns/prov#generatedAtTime"):
                            data_g.remove((s, p, o))
                    self.assertTrue(compare.isomorphic(dataset_to_graph(data_g), dataset_to_graph(expected_data_g)))
        with self.subTest("output_format=nquads, zip_output=False"):
            base_dir_3 = os.path.join("tests", "storer", "data", "rdf_3") + os.sep
            storer = Storer(
                self.graph_set,
                context_map={},
                dir_split=10000,
                n_file_item=1000,
                default_dir="_",
                output_format="nquads",
                zip_output=False,
            )
            self.prov_set.generate_provenance()
            prov_storer = Storer(
                self.prov_set,
                context_map={},
                dir_split=10000,
                n_file_item=1000,
                default_dir="_",
                output_format="nquads",
                zip_output=False,
            )
            storer.store_all(base_dir_3, self.base_iri)
            prov_storer.store_all(base_dir_3, self.base_iri)
            self.graph_set.commit_changes()
            prov_unzipped = Dataset()
            expected_prov_unzipped = Dataset()
            with open(os.path.join(base_dir_3, "br", "060", "10000", "1000.nt"), "r", encoding="utf-8") as f:
                data_unzipped = f.read()
            prov_unzipped.parse(
                source=os.path.join(base_dir_3, "br", "060", "10000", "1000", "prov", "se.nq"), format="nquads"
            )
            expected_prov_unzipped.parse(
                data="""
                <http://test/br/0601/prov/se/1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/prov#Entity> <http://test/br/0601/prov/> .
                <http://test/br/0601/prov/se/1> <http://www.w3.org/ns/prov#specializationOf> <http://test/br/0601> <http://test/br/0601/prov/> .
                <http://test/br/0601/prov/se/1> <http://www.w3.org/ns/prov#wasAttributedTo> <http://resp_agent.test/> <http://test/br/0601/prov/> .
                <http://test/br/0601/prov/se/1> <http://purl.org/dc/terms/description> "The entity 'http://test/br/0601' has been created."^^<http://www.w3.org/2001/XMLSchema#string> <http://test/br/0601/prov/> .
            """,
                format="nquads",
            )
            for s, p, o, _ in prov_unzipped.quads():
                if p == URIRef("http://www.w3.org/ns/prov#generatedAtTime"):
                    prov_unzipped.remove((s, p, o))
            self.assertEqual(
                data_unzipped,
                "<http://test/br/0601> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/spar/fabio/Expression> <http://test/br/> .\n\n",
            )
            self.assertTrue(
                compare.isomorphic(dataset_to_graph(prov_unzipped), dataset_to_graph(expected_prov_unzipped))
            )

    def test_store_graphs_in_file_multiprocessing(self):
        base_dir = os.path.join("tests", "storer", "data", "multiprocessing") + os.sep
        storer = Storer(
            self.graph_set,
            context_map={},
            dir_split=10000,
            n_file_item=1000,
            default_dir="_",
            output_format="json-ld",
            zip_output=False,
        )
        self.prov_set.generate_provenance()
        prov_storer = Storer(
            self.prov_set,
            context_map={},
            dir_split=10000,
            n_file_item=1000,
            default_dir="_",
            output_format="json-ld",
            zip_output=False,
        )
        storer.store_all(base_dir, self.base_iri, process_id=7)
        prov_storer.store_all(base_dir, self.base_iri, process_id=7)
        with open(os.path.join(base_dir, "br", "060", "10000", "1000_7.json")) as f:
            data = json.load(f)
            self.assertEqual(
                data,
                [
                    {
                        "@graph": [{"@id": "http://test/br/0601", "@type": ["http://purl.org/spar/fabio/Expression"]}],
                        "@id": "http://test/br/",
                    }
                ],
            )
        with open(os.path.join(base_dir, "br", "060", "10000", "1000", "prov", "se_7.json")) as f:
            data = [
                {
                    g: [
                        {k: v for k, v in datum.items() if k != "http://www.w3.org/ns/prov#generatedAtTime"}
                        for datum in data
                    ]
                    if g == "@graph"
                    else data
                    for g, data in graph.items()
                }
                for graph in json.load(f)
            ]
            self.assertEqual(
                data,
                [
                    {
                        "@graph": [
                            {
                                "@id": "http://test/br/0601/prov/se/1",
                                "@type": ["http://www.w3.org/ns/prov#Entity"],
                                "http://purl.org/dc/terms/description": [
                                    {
                                        "@type": "http://www.w3.org/2001/XMLSchema#string",
                                        "@value": "The entity 'http://test/br/0601' has been created.",
                                    }
                                ],
                                "http://www.w3.org/ns/prov#specializationOf": [{"@id": "http://test/br/0601"}],
                                "http://www.w3.org/ns/prov#wasAttributedTo": [{"@id": "http://resp_agent.test/"}],
                            }
                        ],
                        "@id": "http://test/br/0601/prov/",
                    }
                ],
            )

    def test_provenance(self):
        self.reset_server()
        graph_set = GraphSet(self.base_iri, "", "060", False)
        prov_set = ProvSet(graph_set, self.base_iri, info_dir=self.info_dir)
        base_dir = os.path.join("tests", "storer", "test_provenance") + os.sep
        graph_set.add_br(self.resp_agent)
        graph_set.add_br(self.resp_agent)
        graph_set.add_br(self.resp_agent)
        prov_set.generate_provenance()
        storer = Storer(
            graph_set,
            context_map={},
            dir_split=10000,
            n_file_item=1000,
            default_dir="_",
            output_format="json-ld",
            zip_output=False,
        )
        prov_storer = Storer(
            prov_set,
            context_map={},
            dir_split=10000,
            n_file_item=1000,
            default_dir="_",
            output_format="json-ld",
            zip_output=False,
        )
        prov_storer.store_all(base_dir, self.base_iri)
        storer.upload_all(self.ts, base_dir)
        graph_set.commit_changes()
        entities_to_process = [("http://test/br/0601",), ("http://test/br/0602",), ("http://test/br/0603",)]
        with Pool(processes=3) as pool:
            pool.starmap(process_entity, entities_to_process)

    def test_unsupported_output_format(self):
        """Test that ValueError is raised for unsupported output formats."""
        with self.assertRaises(ValueError) as context:
            Storer(self.graph_set, output_format="unsupported_format")
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
        context_data = {"@context": {"dc": "http://purl.org/dc/terms/", "title": "dc:title"}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(context_data, f)
            context_file = f.name

        try:
            context_map = {"http://example.org/context": context_file}
            storer = Storer(self.graph_set, context_map=context_map, output_format="json-ld")

            # Verify the context was loaded from file
            self.assertIn("http://example.org/context", storer.context_map)
            self.assertEqual(storer.context_map["http://example.org/context"], context_data)
        finally:
            os.unlink(context_file)

    def test_store_with_context_path(self):
        """Test that context_path replaces embedded context with URL and compacts URIs."""
        context_data = {"@context": {"fabio": "http://purl.org/spar/fabio/"}}
        context_url = "http://example.org/context"
        base_dir = os.path.join("tests", "storer", "data", "context_test") + os.sep

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(context_data, f)
            context_file = f.name

        try:
            os.makedirs(base_dir, exist_ok=True)
            context_map = {context_url: context_file}
            storer = Storer(
                self.graph_set,
                context_map=context_map,
                dir_split=10000,
                n_file_item=1000,
                output_format="json-ld",
                zip_output=False,
            )
            paths = storer.store_all(base_dir, "http://test/", context_path=context_url)
            self.assertGreater(len(paths), 0)

            with open(paths[0], "r") as out:
                data = json.load(out)
                self.assertIn("@context", data)
                self.assertEqual(data["@context"], context_url)
                self.assertIsInstance(data["@context"], str)
                self.assertIn("@graph", data)
                self.assertIsInstance(data["@graph"], list)
                json_str = json.dumps(data)
                self.assertIn("fabio:", json_str)
                self.assertNotIn("http://purl.org/spar/fabio/", json_str)
        finally:
            os.unlink(context_file)
            if os.path.exists(base_dir):
                rmtree(base_dir)

    def test_store_without_context_path(self):
        """Test that without context_path, URIs are not compacted."""
        base_dir = os.path.join("tests", "storer", "data", "no_context_test") + os.sep

        try:
            os.makedirs(base_dir, exist_ok=True)
            storer = Storer(
                self.graph_set,
                context_map={},
                dir_split=10000,
                n_file_item=1000,
                output_format="json-ld",
                zip_output=False,
            )
            paths = storer.store_all(base_dir, "http://test/")
            self.assertGreater(len(paths), 0)

            with open(paths[0], "r") as out:
                json_str = out.read()
                self.assertIn("http://purl.org/spar/fabio/", json_str)
                self.assertNotIn("fabio:", json_str)
        finally:
            if os.path.exists(base_dir):
                rmtree(base_dir)

    def test_store_graphs_in_file(self):
        """Test the store_graphs_in_file method."""
        base_dir = os.path.join("tests", "storer", "data", "direct_store") + os.sep
        os.makedirs(base_dir, exist_ok=True)

        try:
            file_path = os.path.join(base_dir, "output.json")
            storer = Storer(self.graph_set, output_format="json-ld", zip_output=False)

            storer.store_graphs_in_file(file_path)

            # Verify file was created
            self.assertTrue(os.path.exists(file_path))

            # Verify content
            with open(file_path, "r") as f:
                data = json.load(f)
                self.assertIsInstance(data, list)
                self.assertGreater(len(data), 0)
        finally:
            if os.path.exists(base_dir):
                rmtree(base_dir)

    def test_upload_with_failure_marker(self):
        """Test SPARQL upload that creates failure markers on error."""
        base_dir = os.path.join("tests", "storer", "data", "rdf_upload_fail") + os.sep
        storer = Storer(self.graph_set, output_format="json-ld", zip_output=False)
        storer.store_all(base_dir, self.base_iri)

        try:
            from sparqlite import EndpointError

            with patch("sparqlite.SPARQLClient.update") as mock_update:
                mock_update.side_effect = EndpointError("Connection failed")

                result = storer.upload_all("http://invalid-endpoint:9999/sparql", base_dir)
                self.assertFalse(result)

                tp_err_dir = os.path.join(base_dir, "tp_err")
                if os.path.exists(tp_err_dir):
                    err_files = [f for f in os.listdir(tp_err_dir) if f.endswith(".txt")]
                    self.assertGreater(len(err_files), 0)
        finally:
            if os.path.exists(base_dir):
                rmtree(base_dir)

    def test_zip_output_with_ntriples(self):
        """Test ZIP output with N-Triples format."""
        base_dir = os.path.join("tests", "storer", "data", "zip_nt") + os.sep
        storer = Storer(self.graph_set, output_format="nt", zip_output=True)
        storer.store_all(base_dir, self.base_iri)

        try:
            # Find the generated ZIP file
            for root, _, files in os.walk(base_dir):
                for file in files:
                    if file.endswith(".zip"):
                        zip_path = os.path.join(root, file)
                        with ZipFile(zip_path, "r") as zf:
                            # Check that ZIP contains .nt file
                            names = zf.namelist()
                            self.assertTrue(any(name.endswith(".nt") for name in names))
                            return
            self.fail("No ZIP file found")
        finally:
            if os.path.exists(base_dir):
                rmtree(base_dir)

    def test_upload_all_with_modified_entities_filtering(self):
        """Test that upload_all filters entities based on modified_entities."""
        self.reset_server()

        br1 = self.graph_set.add_br(self.resp_agent)
        br1.has_title("First Resource")
        br2 = self.graph_set.add_br(self.resp_agent)
        br2.has_title("Second Resource")
        br3 = self.graph_set.add_br(self.resp_agent)
        br3.has_title("Third Resource")

        modified_entities = {br1.res, br3.res}

        storer = Storer(self.graph_set, modified_entities=modified_entities)
        result = storer.upload_all(self.ts)

        self.assertTrue(result)

        with SPARQLClient(self.ts) as client:
            results = client.query(f"ASK {{ <{br1.res}> ?p ?o }}")
            self.assertTrue(results["boolean"])
            results = client.query(f"ASK {{ <{br2.res}> ?p ?o }}")
            self.assertFalse(results["boolean"])
            results = client.query(f"ASK {{ <{br3.res}> ?p ?o }}")
            self.assertTrue(results["boolean"])

    def test_store_graphs_save_queries(self):
        base_dir = os.path.join("tests", "storer", "data", "rdf_save_queries") + os.sep
        storer = Storer(
            self.graph_set,
            context_map={},
            dir_split=10000,
            n_file_item=1000,
            default_dir="_",
            output_format="json-ld",
            zip_output=False,
        )
        self.prov_set.generate_provenance()
        prov_storer = Storer(
            self.prov_set,
            context_map={},
            dir_split=10000,
            n_file_item=1000,
            default_dir="_",
            output_format="json-ld",
            zip_output=False,
        )
        storer.store_all(base_dir, self.base_iri)
        prov_storer.store_all(base_dir, self.base_iri)

        to_be_uploaded_dir = os.path.join(base_dir, "to_be_uploaded")
        storer.upload_all(self.ts, base_dir, save_queries=True)

        self.assertTrue(os.path.exists(to_be_uploaded_dir))

        saved_queries = os.listdir(to_be_uploaded_dir)
        self.assertGreater(len(saved_queries), 0)

        query_file = os.path.join(to_be_uploaded_dir, saved_queries[0])
        with open(query_file, "r", encoding="utf-8") as f:
            query_content = f.read()
            self.assertIn("INSERT DATA", query_content)

    def test_save_query_hash_determinism(self):
        """Test that _save_query uses deterministic hash-based filenames."""
        base_dir = os.path.join("tests", "storer", "data", "hash_determinism") + os.sep
        to_be_uploaded_dir = os.path.join(base_dir, "to_be_uploaded")
        os.makedirs(to_be_uploaded_dir, exist_ok=True)

        try:
            storer = Storer(self.graph_set, output_format="json-ld", zip_output=False)

            query1 = "INSERT DATA { <http://example.org/s1> <http://example.org/p1> <http://example.org/o1> . }"
            storer._save_query(query1, to_be_uploaded_dir, added_statements=1, removed_statements=0)
            files_after_first = set(os.listdir(to_be_uploaded_dir))
            self.assertEqual(len(files_after_first), 1)

            storer._save_query(query1, to_be_uploaded_dir, added_statements=1, removed_statements=0)
            files_after_second = set(os.listdir(to_be_uploaded_dir))
            self.assertEqual(len(files_after_second), 1)
            self.assertEqual(files_after_first, files_after_second)

            query2 = "INSERT DATA { <http://example.org/s2> <http://example.org/p2> <http://example.org/o2> . }"
            storer._save_query(query2, to_be_uploaded_dir, added_statements=1, removed_statements=0)
            files_after_third = set(os.listdir(to_be_uploaded_dir))
            self.assertEqual(len(files_after_third), 2)
            self.assertNotEqual(files_after_first, files_after_third)

            filename_pattern = re.compile(r"^[a-f0-9]{16}_add\d+_remove\d+\.sparql$")
            for filename in files_after_third:
                self.assertIsNotNone(
                    filename_pattern.match(filename), f"Filename '{filename}' does not match expected pattern"
                )

            expected_hash = hashlib.sha256(query1.encode("utf-8")).hexdigest()[:16]
            expected_filename = f"{expected_hash}_add1_remove0.sparql"
            self.assertIn(expected_filename, files_after_third)

            saved_file_path = os.path.join(to_be_uploaded_dir, expected_filename)
            with open(saved_file_path, "r", encoding="utf-8") as f:
                saved_content = f.read()
            self.assertEqual(saved_content, query1)

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
            query_files = [f for f in os.listdir(to_be_uploaded_dir) if f.endswith(".sparql")]
            self.assertGreater(len(query_files), 0)

            all_queries_content = ""
            for query_file in query_files:
                with open(os.path.join(to_be_uploaded_dir, query_file), "r") as f:
                    all_queries_content += f.read()

            self.assertIn("INSERT DATA", all_queries_content)
            self.assertIn("/prov/se/", all_queries_content)

        finally:
            if os.path.exists(base_dir):
                rmtree(base_dir)


class TestFastPath(unittest.TestCase):
    def setUp(self):
        self.resp_agent = "http://resp_agent.test/"
        self.base_iri = "http://test/"
        self.graph_set = GraphSet(self.base_iri, "", "060", False)
        self.prov_set = ProvSet(self.graph_set, self.base_iri, "", False)
        self.data_dir = os.path.join("tests", "storer", "data", "fast_path")
        if os.path.exists(self.data_dir):
            rmtree(self.data_dir)

    def tearDown(self):
        if os.path.exists(self.data_dir):
            rmtree(self.data_dir)

    def test_entity_to_jsonld_dict_basic(self):
        br = self.graph_set.add_br(self.resp_agent)
        self.assertEqual(
            _entity_to_jsonld_dict(br),
            {"@id": "http://test/br/0601", "@type": ["http://purl.org/spar/fabio/Expression"]},
        )

    def test_entity_to_jsonld_dict_with_title(self):
        br = self.graph_set.add_br(self.resp_agent)
        br.has_title("Test Title")
        self.assertEqual(
            _entity_to_jsonld_dict(br),
            {
                "@id": "http://test/br/0601",
                "@type": ["http://purl.org/spar/fabio/Expression"],
                "http://purl.org/dc/terms/title": [
                    {"@type": "http://www.w3.org/2001/XMLSchema#string", "@value": "Test Title"}
                ],
            },
        )

    def test_entity_to_jsonld_dict_uri_object(self):
        br = self.graph_set.add_br(self.resp_agent)
        id_entity = self.graph_set.add_id(self.resp_agent)
        br.has_identifier(id_entity)
        self.assertEqual(
            _entity_to_jsonld_dict(br),
            {
                "@id": "http://test/br/0601",
                "@type": ["http://purl.org/spar/fabio/Expression"],
                "http://purl.org/spar/datacite/hasIdentifier": [{"@id": "http://test/id/0601"}],
            },
        )

    def test_entity_to_jsonld_dict_multiple_types(self):
        br = self.graph_set.add_br(self.resp_agent)
        br.create_journal_article()
        self.assertEqual(
            _entity_to_jsonld_dict(br),
            {
                "@id": "http://test/br/0601",
                "@type": ["http://purl.org/spar/fabio/Expression", "http://purl.org/spar/fabio/JournalArticle"],
            },
        )

    def test_fast_path_store_all(self):
        base_dir = os.path.join(self.data_dir, "store_all") + os.sep
        br = self.graph_set.add_br(self.resp_agent)
        br.has_title("Comparison Test")
        br.create_journal_article()
        id_entity = self.graph_set.add_id(self.resp_agent)
        br.has_identifier(id_entity)

        storer = Storer(
            self.graph_set, context_map={}, dir_split=10000, n_file_item=1000,
            output_format="json-ld", zip_output=False,
        )
        storer.store_all(base_dir, self.base_iri)

        with open(os.path.join(base_dir, "br", "060", "10000", "1000.json")) as f:
            self.assertEqual(
                json.load(f),
                [
                    {
                        "@graph": [
                            {
                                "@id": "http://test/br/0601",
                                "@type": [
                                    "http://purl.org/spar/fabio/Expression",
                                    "http://purl.org/spar/fabio/JournalArticle",
                                ],
                                "http://purl.org/dc/terms/title": [
                                    {
                                        "@type": "http://www.w3.org/2001/XMLSchema#string",
                                        "@value": "Comparison Test",
                                    }
                                ],
                                "http://purl.org/spar/datacite/hasIdentifier": [
                                    {"@id": "http://test/id/0601"}
                                ],
                            }
                        ],
                        "@id": "http://test/br/",
                    }
                ],
            )

    def test_fast_path_existing_file_merge(self):
        base_dir = os.path.join(self.data_dir, "merge") + os.sep

        br1 = self.graph_set.add_br(self.resp_agent)
        br1.has_title("First")
        Storer(
            self.graph_set, context_map={}, dir_split=10000, n_file_item=1000,
            output_format="json-ld", zip_output=False,
        ).store_all(base_dir, self.base_iri)

        graph_set2 = GraphSet(self.base_iri, "", "060", False)
        br2 = graph_set2.add_br(self.resp_agent, res="http://test/br/0602")
        br2.has_title("Second")
        Storer(
            graph_set2, context_map={}, dir_split=10000, n_file_item=1000,
            output_format="json-ld", zip_output=False,
        ).store_all(base_dir, self.base_iri)

        with open(os.path.join(base_dir, "br", "060", "10000", "1000.json")) as f:
            self.assertEqual(
                json.load(f),
                [
                    {
                        "@graph": [
                            {
                                "@id": "http://test/br/0601",
                                "@type": ["http://purl.org/spar/fabio/Expression"],
                                "http://purl.org/dc/terms/title": [
                                    {"@type": "http://www.w3.org/2001/XMLSchema#string", "@value": "First"}
                                ],
                            },
                            {
                                "@id": "http://test/br/0602",
                                "@type": ["http://purl.org/spar/fabio/Expression"],
                                "http://purl.org/dc/terms/title": [
                                    {"@type": "http://www.w3.org/2001/XMLSchema#string", "@value": "Second"}
                                ],
                            },
                        ],
                        "@id": "http://test/br/",
                    }
                ],
            )

    def test_fast_path_delete_entity(self):
        base_dir = os.path.join(self.data_dir, "delete") + os.sep

        br = self.graph_set.add_br(self.resp_agent)
        br.has_title("To Delete")
        Storer(
            self.graph_set, context_map={}, dir_split=10000, n_file_item=1000,
            output_format="json-ld", zip_output=False,
        ).store_all(base_dir, self.base_iri)

        br._to_be_deleted = True
        Storer(
            self.graph_set, context_map={}, dir_split=10000, n_file_item=1000,
            output_format="json-ld", zip_output=False,
        ).store_all(base_dir, self.base_iri)

        with open(os.path.join(base_dir, "br", "060", "10000", "1000.json")) as f:
            self.assertEqual(json.load(f), [])

    def test_fast_path_replace_entity(self):
        base_dir = os.path.join(self.data_dir, "replace") + os.sep

        br = self.graph_set.add_br(self.resp_agent)
        br.has_title("Original")
        Storer(
            self.graph_set, context_map={}, dir_split=10000, n_file_item=1000,
            output_format="json-ld", zip_output=False,
        ).store_all(base_dir, self.base_iri)

        br._preexisting_triples = frozenset(br.g.triples((None, None, None)))
        br.has_title("Updated")
        Storer(
            self.graph_set, context_map={}, dir_split=10000, n_file_item=1000,
            output_format="json-ld", zip_output=False,
        ).store_all(base_dir, self.base_iri)

        with open(os.path.join(base_dir, "br", "060", "10000", "1000.json")) as f:
            self.assertEqual(
                json.load(f),
                [
                    {
                        "@graph": [
                            {
                                "@id": "http://test/br/0601",
                                "@type": ["http://purl.org/spar/fabio/Expression"],
                                "http://purl.org/dc/terms/title": [
                                    {"@type": "http://www.w3.org/2001/XMLSchema#string", "@value": "Updated"}
                                ],
                            }
                        ],
                        "@id": "http://test/br/",
                    }
                ],
            )

    def test_fast_path_prov_additive(self):
        base_dir = os.path.join(self.data_dir, "prov") + os.sep

        self.graph_set.add_br(self.resp_agent)
        self.prov_set.generate_provenance()
        Storer(
            self.prov_set, context_map={}, dir_split=10000, n_file_item=1000,
            output_format="json-ld", zip_output=False,
        ).store_all(base_dir, self.base_iri)

        prov_file = os.path.join(base_dir, "br", "060", "10000", "1000", "prov", "se.json")
        with open(prov_file) as f:
            data = [
                {
                    g: [
                        {k: v for k, v in datum.items() if k != "http://www.w3.org/ns/prov#generatedAtTime"}
                        for datum in data
                    ]
                    if g == "@graph"
                    else data
                    for g, data in graph.items()
                }
                for graph in json.load(f)
            ]
        self.assertEqual(
            data,
            [
                {
                    "@graph": [
                        {
                            "@id": "http://test/br/0601/prov/se/1",
                            "@type": ["http://www.w3.org/ns/prov#Entity"],
                            "http://purl.org/dc/terms/description": [
                                {
                                    "@type": "http://www.w3.org/2001/XMLSchema#string",
                                    "@value": "The entity 'http://test/br/0601' has been created.",
                                }
                            ],
                            "http://www.w3.org/ns/prov#specializationOf": [{"@id": "http://test/br/0601"}],
                            "http://www.w3.org/ns/prov#wasAttributedTo": [{"@id": "http://resp_agent.test/"}],
                        }
                    ],
                    "@id": "http://test/br/0601/prov/",
                }
            ],
        )

    def test_fast_path_prov_merge_existing_snapshot(self):
        base_dir = os.path.join(self.data_dir, "prov_merge") + os.sep

        br = self.graph_set.add_br(self.resp_agent)
        self.prov_set.generate_provenance()
        Storer(
            self.prov_set, context_map={}, dir_split=10000, n_file_item=1000,
            output_format="json-ld", zip_output=False,
        ).store_all(base_dir, self.base_iri)
        self.graph_set.commit_changes()

        graph_set2 = GraphSet(self.base_iri, "", "060", False)
        prov_set2 = ProvSet(graph_set2, self.base_iri, custom_counter_handler=self.prov_set.counter_handler)
        br2 = graph_set2.add_br(self.resp_agent, res=br.res, preexisting_graph=SubgraphView(br.g, br.res))
        br2.mark_as_to_be_deleted()
        prov_set2.generate_provenance()
        Storer(
            prov_set2, context_map={}, dir_split=10000, n_file_item=1000,
            output_format="json-ld", zip_output=False,
        ).store_all(base_dir, self.base_iri)

        prov_file = os.path.join(base_dir, "br", "060", "10000", "1000", "prov", "se.json")
        with open(prov_file) as f:
            data = json.load(f)
        graph = data[0]
        entities = {e["@id"]: e for e in graph["@graph"]}
        se1 = entities["http://test/br/0601/prov/se/1"]
        se2 = entities["http://test/br/0601/prov/se/2"]
        self.assertIn("http://www.w3.org/ns/prov#generatedAtTime", se1)
        self.assertIn("http://www.w3.org/ns/prov#invalidatedAtTime", se1)
        self.assertEqual(
            se1["http://purl.org/dc/terms/description"][0]["@value"],
            "The entity 'http://test/br/0601' has been created.",
        )
        self.assertEqual(
            se2["http://purl.org/dc/terms/description"][0]["@value"],
            "The entity 'http://test/br/0601' has been deleted.",
        )

    def test_fast_path_zip_output(self):
        base_dir = os.path.join(self.data_dir, "zip") + os.sep

        self.graph_set.add_br(self.resp_agent)
        Storer(
            self.graph_set, context_map={}, dir_split=10000, n_file_item=1000,
            output_format="json-ld", zip_output=True,
        ).store_all(base_dir, self.base_iri)

        with ZipFile(os.path.join(base_dir, "br", "060", "10000", "1000.zip")) as zf:
            with zf.open("1000.json") as f:
                self.assertEqual(
                    json.load(f),
                    [
                        {
                            "@graph": [
                                {"@id": "http://test/br/0601", "@type": ["http://purl.org/spar/fabio/Expression"]}
                            ],
                            "@id": "http://test/br/",
                        }
                    ],
                )

    def test_compact_jsonld(self):
        data = [
            {
                "@graph": [
                    {
                        "@id": "http://test/br/0601",
                        "@type": ["http://purl.org/spar/fabio/Expression"],
                        "http://purl.org/dc/terms/title": [
                            {"@type": "http://www.w3.org/2001/XMLSchema#string", "@value": "Test"}
                        ],
                    }
                ],
                "@id": "http://test/br/",
            }
        ]
        ns_to_prefix = [
            ("http://purl.org/spar/fabio/", "fabio"),
            ("http://purl.org/dc/terms/", "dcterms"),
            ("http://www.w3.org/2001/XMLSchema#", "xsd"),
        ]
        self.assertEqual(
            _compact_jsonld(data, "http://example.org/context", ns_to_prefix),
            {
                "@context": "http://example.org/context",
                "@graph": [
                    {
                        "@id": "http://test/br/0601",
                        "@type": ["fabio:Expression"],
                        "dcterms:title": [{"@type": "xsd:string", "@value": "Test"}],
                    }
                ],
                "@id": "http://test/br/",
            },
        )

    def test_expand_jsonld(self):
        data = [
            {
                "@graph": [
                    {
                        "@id": "http://test/br/0601",
                        "@type": ["fabio:Expression"],
                        "dcterms:title": [{"@type": "xsd:string", "@value": "Test"}],
                    }
                ],
                "@id": "http://test/br/",
            }
        ]
        prefix_to_ns = {
            "fabio": "http://purl.org/spar/fabio/",
            "dcterms": "http://purl.org/dc/terms/",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        }
        self.assertEqual(
            _expand_jsonld(data, prefix_to_ns),
            [
                {
                    "@graph": [
                        {
                            "@id": "http://test/br/0601",
                            "@type": ["http://purl.org/spar/fabio/Expression"],
                            "http://purl.org/dc/terms/title": [
                                {"@type": "http://www.w3.org/2001/XMLSchema#string", "@value": "Test"}
                            ],
                        }
                    ],
                    "@id": "http://test/br/",
                }
            ],
        )

    def test_fast_path_with_context_roundtrip(self):
        context_data = {"@context": {"fabio": "http://purl.org/spar/fabio/"}}
        context_url = "http://example.org/context"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(context_data, f)
            context_file = f.name

        base_dir = os.path.join(self.data_dir, "context_roundtrip") + os.sep
        try:
            context_map = {context_url: context_file}
            storer = Storer(
                self.graph_set, context_map=context_map, dir_split=10000,
                n_file_item=1000, output_format="json-ld", zip_output=False,
            )
            self.graph_set.add_br(self.resp_agent)
            paths = storer.store_all(base_dir, self.base_iri, context_path=context_url)

            with open(paths[0]) as f:
                self.assertEqual(
                    json.load(f),
                    {
                        "@context": context_url,
                        "@graph": [
                            {"@id": "http://test/br/0601", "@type": ["fabio:Expression"]}
                        ],
                        "@id": "http://test/br/",
                    },
                )

            reader = Reader(context_map=storer.context_map)
            self.assertEqual(
                reader.load_jsonld_dict(paths[0]),
                [
                    {
                        "@graph": [
                            {
                                "@id": "http://test/br/0601",
                                "@type": ["http://purl.org/spar/fabio/Expression"],
                            }
                        ],
                        "@id": "http://test/br/",
                    }
                ],
            )
        finally:
            os.unlink(context_file)


def process_entity(entity):
    base_iri = "http://test/"
    ts = os.environ["SPARQL_TEST_ENDPOINT"]
    resp_agent = "http://resp_agent.test/"
    base_dir = os.path.join("tests", "storer", "test_provenance") + os.sep
    info_dir = os.path.join("tests", "storer", "test_provenance", "info_dir")
    graph_set = GraphSet(base_iri, "", "060", False)
    Reader.import_entity_from_triplestore(graph_set, ts, URIRef(entity), resp_agent)
    br = graph_set.get_entity(entity)
    assert isinstance(br, BibliographicResource)
    br.has_title("Hola")
    prov_set = ProvSet(graph_set, base_iri, info_dir=info_dir)
    prov_set.generate_provenance()
    storer = Storer(
        graph_set,
        context_map={},
        dir_split=10000,
        n_file_item=1000,
        default_dir="_",
        output_format="json-ld",
        zip_output=False,
    )
    prov_storer = Storer(
        prov_set,
        context_map={},
        dir_split=10000,
        n_file_item=1000,
        default_dir="_",
        output_format="json-ld",
        zip_output=False,
    )
    prov_storer.store_all(base_dir, base_iri)
    storer.upload_all(ts, base_dir)


if __name__ == "__main__":
    unittest.main()
