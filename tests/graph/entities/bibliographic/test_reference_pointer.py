#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from rdflib import XSD

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet
from triplelite import RDFTerm


class TestReferencePointer(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def setUp(self):
        self.an = self.graph_set.add_an(self.resp_agent)
        self.rp1 = self.graph_set.add_rp(self.resp_agent)
        self.rp2 = self.graph_set.add_rp(self.resp_agent)
        self.be = self.graph_set.add_be(self.resp_agent)

    def test_has_content(self):
        content = "Content"
        result = self.rp1.has_content(content)
        self.assertIsNone(result)

        triple = self.rp1.res, GraphEntity.iri_has_content, RDFTerm("literal", content, str(XSD.string))
        self.assertIn(triple, self.rp1.g)

    def test_has_next_rp(self):
        result = self.rp1.has_next_rp(self.rp2)
        self.assertIsNone(result)

        triple = self.rp1.res, GraphEntity.iri_has_next, RDFTerm("uri", str(self.rp2.res))
        self.assertIn(triple, self.rp1.g)

    def test_denotes_be(self):
        result = self.rp1.denotes_be(self.be)
        self.assertIsNone(result)

        triple = self.rp1.res, GraphEntity.iri_denotes, RDFTerm("uri", str(self.be.res))
        self.assertIn(triple, self.rp1.g)

    def test_has_annotation(self):
        result = self.rp1.has_annotation(self.an)
        self.assertIsNone(result)

        triple = self.rp1.res, GraphEntity.iri_has_annotation, RDFTerm("uri", str(self.an.res))
        self.assertIn(triple, self.rp1.g)


if __name__ == '__main__':
    unittest.main()
