#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from oc_ocdm.constants import XSD_STRING
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet
from triplelite import RDFTerm


class TestPointerList(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def setUp(self):
        self.rp = self.graph_set.add_rp(self.resp_agent)
        self.pl = self.graph_set.add_pl(self.resp_agent)

    def test_has_content(self):
        content = "Content"
        result = self.pl.has_content(content)
        self.assertIsNone(result)

        triple = self.pl.res, GraphEntity.iri_has_content, RDFTerm("literal", content, XSD_STRING)
        self.assertIn(triple, self.pl.g)

    def test_contains_element(self):
        result = self.pl.contains_element(self.rp)
        self.assertIsNone(result)

        triple = self.pl.res, GraphEntity.iri_has_element, RDFTerm("uri", str(self.rp.res))
        self.assertIn(triple, self.pl.g)


if __name__ == '__main__':
    unittest.main()
