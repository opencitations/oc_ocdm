#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from rdflib import XSD

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.light_graph import RDFTerm


class TestBibliographicReference(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def setUp(self):
        self.be = self.graph_set.add_be(self.resp_agent)
        self.br = self.graph_set.add_br(self.resp_agent)
        self.an = self.graph_set.add_an(self.resp_agent)

    def test_has_content(self):
        content = "Content"
        result = self.be.has_content(content)
        self.assertIsNone(result)

        triple = self.be.res, GraphEntity.iri_has_content, RDFTerm("literal", content, str(XSD.string))
        self.assertIn(triple, self.be.g)

    def test_has_annotation(self):
        result = self.be.has_annotation(self.an)
        self.assertIsNone(result)

        triple = self.be.res, GraphEntity.iri_has_annotation, RDFTerm("uri", str(self.an.res))
        self.assertIn(triple, self.be.g)

    def test_references(self):
        result = self.be.references_br(self.br)
        self.assertIsNone(result)

        triple = self.be.res, GraphEntity.iri_references, RDFTerm("uri", str(self.br.res))
        self.assertIn(triple, self.be.g)


if __name__ == '__main__':
    unittest.main()
