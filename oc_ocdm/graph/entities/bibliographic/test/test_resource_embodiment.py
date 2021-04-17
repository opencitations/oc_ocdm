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

from rdflib import URIRef, Literal, RDF

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet


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

        triple = self.re.res, GraphEntity.iri_has_format, media_type
        self.assertIn(triple, self.re.g)

    def test_has_starting_page(self):
        starting_page = "15"
        result = self.re.has_starting_page(starting_page)
        self.assertIsNone(result)

        triple = self.re.res, GraphEntity.iri_starting_page, Literal(starting_page)
        self.assertIn(triple, self.re.g)

    def test_has_ending_page(self):
        ending_page = "288"
        result = self.re.has_ending_page(ending_page)
        self.assertIsNone(result)

        triple = self.re.res, GraphEntity.iri_ending_page, Literal(ending_page)
        self.assertIn(triple, self.re.g)

    def test_has_url(self):
        url = URIRef("http://test/url")
        result = self.re.has_url(url)
        self.assertIsNone(result)

        triple = self.re.res, GraphEntity.iri_has_url, url
        self.assertIn(triple, self.re.g)

    def test_create_digital_embodiment(self):
        result = self.re.create_digital_embodiment()
        self.assertIsNone(result)

        triple = self.re.res, RDF.type, GraphEntity.iri_digital_manifestation
        self.assertIn(triple, self.re.g)

    def test_create_print_embodiment(self):
        result = self.re.create_print_embodiment()
        self.assertIsNone(result)

        triple = self.re.res, RDF.type, GraphEntity.iri_print_object
        self.assertIn(triple, self.re.g)


if __name__ == '__main__':
    unittest.main()
