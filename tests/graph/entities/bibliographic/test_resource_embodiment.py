#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from rdflib import RDF, XSD, URIRef

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet
from triplelite import RDFTerm


class TestResourceEmbodiment(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def setUp(self):
        self.re = self.graph_set.add_re(self.resp_agent)

    def test_has_media_type(self):
        media_type = URIRef("http://test/MediaType")
        result = self.re.has_media_type(media_type)
        self.assertIsNone(result)

        triple = self.re.res, GraphEntity.iri_has_format, RDFTerm("uri", str(media_type))
        self.assertIn(triple, self.re.g)

    def test_has_starting_page(self):
        starting_page = "15"
        result = self.re.has_starting_page(starting_page)
        self.assertIsNone(result)

        triple = self.re.res, GraphEntity.iri_starting_page, RDFTerm("literal", starting_page, str(XSD.string))
        self.assertIn(triple, self.re.g)

    def test_has_ending_page(self):
        ending_page = "288"
        result = self.re.has_ending_page(ending_page)
        self.assertIsNone(result)

        triple = self.re.res, GraphEntity.iri_ending_page, RDFTerm("literal", ending_page, str(XSD.string))
        self.assertIn(triple, self.re.g)

    def test_has_url(self):
        url = URIRef("http://test/url")
        result = self.re.has_url(url)
        self.assertIsNone(result)

        triple = self.re.res, GraphEntity.iri_has_url, RDFTerm("uri", str(url))
        self.assertIn(triple, self.re.g)

    def test_create_digital_embodiment(self):
        result = self.re.create_digital_embodiment()
        self.assertIsNone(result)

        triple = self.re.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_digital_manifestation))
        self.assertIn(triple, self.re.g)

    def test_create_print_embodiment(self):
        result = self.re.create_print_embodiment()
        self.assertIsNone(result)

        triple = self.re.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_print_object))
        self.assertIn(triple, self.re.g)


if __name__ == '__main__':
    unittest.main()
