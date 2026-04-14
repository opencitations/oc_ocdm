#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.light_graph import RDFTerm


class TestAgentRole(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def setUp(self):
        self.ar1 = self.graph_set.add_ar(self.resp_agent)
        self.ar2 = self.graph_set.add_ar(self.resp_agent)
        self.ra = self.graph_set.add_ra(self.resp_agent)
        self.br = self.graph_set.add_br(self.resp_agent)

    def test_has_next(self):
        result = self.ar1.has_next(self.ar2)
        self.assertIsNone(result)

        triple = self.ar1.res, GraphEntity.iri_has_next, RDFTerm("uri", str(self.ar2.res))
        self.assertIn(triple, self.ar1.g)

    def test_is_held_by(self):
        result = self.ar1.is_held_by(self.ra)
        self.assertIsNone(result)

        triple = self.ar1.res, GraphEntity.iri_is_held_by, RDFTerm("uri", str(self.ra.res))
        self.assertIn(triple, self.ar1.g)

    def test_create_publisher(self):
        result = self.ar1.create_publisher()
        self.assertIsNone(result)

        triple = self.ar1.res, GraphEntity.iri_with_role, RDFTerm("uri", str(GraphEntity.iri_publisher))
        self.assertIn(triple, self.ar1.g)

    def test_create_author(self):
        result = self.ar1.create_author()
        self.assertIsNone(result)

        triple = self.ar1.res, GraphEntity.iri_with_role, RDFTerm("uri", str(GraphEntity.iri_author))
        self.assertIn(triple, self.ar1.g)

    def test_create_editor(self):
        result = self.ar1.create_editor()
        self.assertIsNone(result)

        triple = self.ar1.res, GraphEntity.iri_with_role, RDFTerm("uri", str(GraphEntity.iri_editor))
        self.assertIn(triple, self.ar1.g)


if __name__ == '__main__':
    unittest.main()