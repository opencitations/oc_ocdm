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
import json
import os
import unittest
from platform import system
from zipfile import ZipFile
from multiprocessing import Pool
from SPARQLWrapper import POST, SPARQLWrapper

from rdflib import ConjunctiveGraph, URIRef, compare

from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.prov.prov_set import ProvSet
from oc_ocdm.storer import Storer
from oc_ocdm.reader import Reader

from shutil import rmtree

class TestStorer(unittest.TestCase):
    def setUp(self):
        self.resp_agent = "http://resp_agent.test/"
        self.base_iri = "http://test/"
        self.ts = 'http://127.0.0.1:9999/blazegraph/sparql'
        self.graph_set = GraphSet(self.base_iri, "", "060", False)
        self.prov_set = ProvSet(self.graph_set, self.base_iri, "", False)
        self.br = self.graph_set.add_br(self.resp_agent)
        self.data_dir = os.path.join("oc_ocdm", "test", "storer", "data")
        self.prov_dir = os.path.join("oc_ocdm", "test", "storer", "test_provenance")
        self.info_dir = os.path.join(self.prov_dir, "info_dir")

    def tearDown(self):
        if os.path.exists(self.data_dir):
            rmtree(self.data_dir)
        if os.path.exists(self.prov_dir):
            rmtree(os.path.join(self.prov_dir))

    def test_store_graphs_in_file(self):
        base_dir = os.path.join("oc_ocdm", "test", "storer", "data", "rdf") + os.sep
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
                        'http://purl.org/dc/terms/description': [{'@value': "The entity 'http://test/br/0601' has been created."}], 
                        'http://www.w3.org/ns/prov#specializationOf': [{'@id': 'http://test/br/0601'}], 
                        'http://www.w3.org/ns/prov#wasAttributedTo': [{'@id': 'http://resp_agent.test/'}]}], '@id': 'http://test/br/0601/prov/'}])
        with self.subTest("output_format=json-ld, zip_output=False"):
            base_dir_1 = os.path.join("oc_ocdm", "test", "storer", "data", "rdf_1") + os.sep
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
                    'http://purl.org/dc/terms/description': [{'@value': "The entity 'http://test/br/0601' has been created."}], 
                    'http://www.w3.org/ns/prov#specializationOf': [{'@id': 'http://test/br/0601'}], 
                    'http://www.w3.org/ns/prov#wasAttributedTo': [{'@id': 'http://resp_agent.test/'}]}], '@id': 'http://test/br/0601/prov/'}])
        with self.subTest("output_format=nquads, zip_output=True"):
            base_dir_2 = os.path.join("oc_ocdm", "test", "storer", "data", "rdf_2") + os.sep
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
                    data_g = ConjunctiveGraph()
                    expected_data_g = ConjunctiveGraph()
                    data_g.parse(data=data, format="nquads")
                    expected_data_g.parse(data="""
                        <http://test/br/0601/prov/se/1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/prov#Entity> <http://test/br/0601/prov/> .
                        <http://test/br/0601/prov/se/1> <http://www.w3.org/ns/prov#specializationOf> <http://test/br/0601> <http://test/br/0601/prov/> .
                        <http://test/br/0601/prov/se/1> <http://www.w3.org/ns/prov#wasAttributedTo> <http://resp_agent.test/> <http://test/br/0601/prov/> .
                        <http://test/br/0601/prov/se/1> <http://purl.org/dc/terms/description> "The entity 'http://test/br/0601' has been created." <http://test/br/0601/prov/> .
                    """, format="nquads")
                    for s, p, o, c in data_g.quads():
                        if p == URIRef("http://www.w3.org/ns/prov#generatedAtTime"):
                            data_g.remove((s, p, o, c))
                    self.assertTrue(compare.isomorphic(data_g, expected_data_g))
        with self.subTest("output_format=nquads, zip_output=False"):
            base_dir_3 = os.path.join("oc_ocdm", "test", "storer", "data", "rdf_3") + os.sep
            storer = Storer(self.graph_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='nquads', zip_output=False)
            self.prov_set.generate_provenance()
            prov_storer = Storer(self.prov_set, context_map={}, dir_split=10000, n_file_item=1000, default_dir="_", output_format='nquads', zip_output=False)
            storer.store_all(base_dir_3, self.base_iri)
            prov_storer.store_all(base_dir_3, self.base_iri)
            self.graph_set.commit_changes()
            prov_unzipped = ConjunctiveGraph()
            expected_prov_unzipped = ConjunctiveGraph()
            with open(os.path.join(base_dir_3, "br", "060", "10000", "1000.nt"), "r", encoding="utf-8") as f:
                data_unzipped = f.read()
            prov_unzipped.parse(source=os.path.join(base_dir_3, "br", "060", "10000", "1000", "prov", "se.nq"), format="nquads")
            expected_prov_unzipped.parse(data="""
                <http://test/br/0601/prov/se/1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/prov#Entity> <http://test/br/0601/prov/> .
                <http://test/br/0601/prov/se/1> <http://www.w3.org/ns/prov#specializationOf> <http://test/br/0601> <http://test/br/0601/prov/> .
                <http://test/br/0601/prov/se/1> <http://www.w3.org/ns/prov#wasAttributedTo> <http://resp_agent.test/> <http://test/br/0601/prov/> .
                <http://test/br/0601/prov/se/1> <http://purl.org/dc/terms/description> "The entity 'http://test/br/0601' has been created." <http://test/br/0601/prov/> .
            """, format="nquads")
            for s, p, o, c in prov_unzipped.quads():
                if p == URIRef("http://www.w3.org/ns/prov#generatedAtTime"):
                    prov_unzipped.remove((s, p, o, c))
            self.assertEqual(data_unzipped, "<http://test/br/0601> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/spar/fabio/Expression> <http://test/br/> .\n\n")
            self.assertTrue(compare.isomorphic(prov_unzipped, expected_prov_unzipped))

    def test_store_graphs_in_file_multiprocessing(self):
        base_dir = os.path.join("oc_ocdm", "test", "storer", "data", "multiprocessing") + os.sep
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
                'http://purl.org/dc/terms/description': [{'@value': "The entity 'http://test/br/0601' has been created."}], 
                'http://www.w3.org/ns/prov#specializationOf': [{'@id': 'http://test/br/0601'}], 
                'http://www.w3.org/ns/prov#wasAttributedTo': [{'@id': 'http://resp_agent.test/'}]}], '@id': 'http://test/br/0601/prov/'}])

    def test_provenance(self):
        ts = SPARQLWrapper(self.ts)
        ts.setQuery('delete{?x ?y ?z} where{?x ?y ?z}')
        ts.setMethod(POST)
        ts.query()
        graph_set = GraphSet(self.base_iri, "", "060", False)
        prov_set = ProvSet(graph_set, self.base_iri, info_dir=self.info_dir)
        base_dir = os.path.join("oc_ocdm", "test", "storer", "test_provenance") + os.sep
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

def process_entity(entity):
    base_iri = "http://test/"
    ts = 'http://127.0.0.1:9999/blazegraph/sparql'
    resp_agent = "http://resp_agent.test/"
    base_dir = os.path.join("oc_ocdm", "test", "storer", "test_provenance") + os.sep
    info_dir = os.path.join("oc_ocdm", "test", "storer", "test_provenance", "info_dir")
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