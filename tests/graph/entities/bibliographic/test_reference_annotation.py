#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.light_graph import RDFTerm


class TestReferenceAnnotation(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def setUp(self):
        self.an = self.graph_set.add_an(self.resp_agent)
        self.br1 = self.graph_set.add_br(self.resp_agent)
        self.br2 = self.graph_set.add_br(self.resp_agent)
        self.ci = self.graph_set.add_ci(self.resp_agent)

    def test_has_body_annotation(self):
        result = self.an.has_body_annotation(self.ci)
        self.assertIsNone(result)

        triple = self.an.res, GraphEntity.iri_has_body, RDFTerm("uri", str(self.ci.res))
        self.assertIn(triple, self.an.g)


if __name__ == '__main__':
    unittest.main()
