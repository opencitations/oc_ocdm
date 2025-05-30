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
import unittest

from rdflib import Graph, BNode

from oc_ocdm.graph.graph_set import GraphSet

from oc_ocdm.metadata.metadata_set import MetadataSet
from oc_ocdm.metadata.entities.dataset import Dataset
from oc_ocdm.metadata.entities.distribution import Distribution


class TestMetadataSet(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    def setUp(self):
        self.metadata_set = MetadataSet("http://test/", "./info_dir/", False)

    def test_get_entity(self):
        di = self.metadata_set.add_di("ocdmTest", self.resp_agent)
        ref = di.res
        result = self.metadata_set.get_entity(ref)
        self.assertIsNotNone(result)
        self.assertIs(result, di)

    def test_add_dataset(self):
        dataset = self.metadata_set.add_dataset("ocdmTest", self.resp_agent)

        self.assertIsNotNone(dataset)
        self.assertIsInstance(dataset, Dataset)
        self.assertIsInstance(dataset.g.identifier, BNode)

    def test_add_di(self):
        di = self.metadata_set.add_di("ocdmTest", self.resp_agent)

        self.assertIsNotNone(di)
        self.assertIsInstance(di, Distribution)
        self.assertIsInstance(di.g.identifier, BNode)

    def test_graphs(self):
        count = 10
        for i in range(count):
            self.metadata_set.add_di("ocdmTest", self.resp_agent)
        result = self.metadata_set.graphs()
        self.assertIsNotNone(result)
        self.assertEqual(len(result), count)
        for graph in result:
            self.assertIsInstance(graph, Graph)

    def test_get_graph_iri(self):
        ar = self.metadata_set.add_dataset("ocdmTest", self.resp_agent)
        iri = str(ar.g.identifier)
        result = GraphSet.get_graph_iri(ar.g)
        self.assertIsNotNone(result)
        self.assertEqual(iri, result)


if __name__ == '__main__':
    unittest.main()
