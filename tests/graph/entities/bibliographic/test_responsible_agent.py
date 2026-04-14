#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from rdflib import XSD, URIRef

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.light_graph import RDFTerm


class TestResponsibleAgent(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def setUp(self):
        self.ra = self.graph_set.add_ra(self.resp_agent)
        self.ar = self.graph_set.add_ar(self.resp_agent)

    def test_has_name(self):
        name = "Name"
        result = self.ra.has_name(name)
        self.assertIsNone(result)

        triple = self.ra.res, GraphEntity.iri_name, RDFTerm("literal", name, str(XSD.string))
        self.assertIn(triple, self.ra.g)

    def test_has_given_name(self):
        given_name = "GivenName"
        result = self.ra.has_given_name(given_name)
        self.assertIsNone(result)

        triple = self.ra.res, GraphEntity.iri_given_name, RDFTerm("literal", given_name, str(XSD.string))
        self.assertIn(triple, self.ra.g)

    def test_has_family_name(self):
        family_name = "GivenName"
        result = self.ra.has_family_name(family_name)
        self.assertIsNone(result)

        triple = self.ra.res, GraphEntity.iri_family_name, RDFTerm("literal", family_name, str(XSD.string))
        self.assertIn(triple, self.ra.g)

    def test_has_related_agent(self):
        related_agent = URIRef("http://test/RelatedAgent")
        result = self.ra.has_related_agent(related_agent)
        self.assertIsNone(result)

        triple = self.ra.res, GraphEntity.iri_relation, RDFTerm("uri", str(related_agent))
        self.assertIn(triple, self.ra.g)


if __name__ == '__main__':
    unittest.main()
