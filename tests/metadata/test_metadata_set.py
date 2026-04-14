#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.metadata.entities.dataset import Dataset
from oc_ocdm.metadata.entities.distribution import Distribution
from oc_ocdm.metadata.metadata_set import MetadataSet


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
        self.assertIsNone(dataset.g.identifier)

    def test_add_di(self):
        di = self.metadata_set.add_di("ocdmTest", self.resp_agent)

        self.assertIsNotNone(di)
        self.assertIsInstance(di, Distribution)
        self.assertIsNone(di.g.identifier)

    def test_graphs(self):
        count = 10
        for i in range(count):
            self.metadata_set.add_di("ocdmTest", self.resp_agent)
        result = self.metadata_set.graphs()
        self.assertIsNotNone(result)
        self.assertEqual(len(result), count)
        for graph in result:
            self.assertTrue(len(graph) > 0)

    def test_get_graph_iri(self):
        ar = self.metadata_set.add_dataset("ocdmTest", self.resp_agent)
        iri = str(ar.g.identifier)
        result = GraphSet.get_graph_iri(ar.g)
        self.assertIsNotNone(result)
        self.assertEqual(iri, result)


if __name__ == '__main__':
    unittest.main()
