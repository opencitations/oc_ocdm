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

from oc_graphlib.graph_entity import GraphEntity
from oc_graphlib.graph_set import GraphSet


class TestResourceEmbodiment(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "context_base", "./info_dir/info_file_", 0, "", wanted_label=False)

    def setUp(self):
        self.graph_set.g = []
        self.re = self.graph_set.add_re(self.__class__.__name__)

    def test_has_media_type(self):
        media_type = "MediaType"
        result = self.re.has_media_type(media_type)
        self.assertTrue(result)

        triple = URIRef(str(self.re)), GraphEntity.has_format, Literal(media_type)
        self.assertIn(triple, self.re.g)

    def test_create_starting_page(self):
        starting_page = "15"
        result = self.re.create_starting_page(starting_page)
        self.assertTrue(result)

        triple = URIRef(str(self.re)), GraphEntity.starting_page, Literal(starting_page)
        self.assertIn(triple, self.re.g)

    def test_create_ending_page(self):
        ending_page = "288"
        result = self.re.create_ending_page(ending_page)
        self.assertTrue(result)

        triple = URIRef(str(self.re)), GraphEntity.ending_page, Literal(ending_page)
        self.assertIn(triple, self.re.g)

    def test_has_url(self):
        url = "http://test/url"
        result = self.re.has_url(url)
        self.assertTrue(result)

        triple = URIRef(str(self.re)), GraphEntity.has_url, Literal(url)
        self.assertIn(triple, self.re.g)

    def test_create_digital_embodiment(self):
        result = self.re.create_digital_embodiment()
        self.assertIsNone(result)

        triple = URIRef(str(self.re)), RDF.type, GraphEntity.digital_manifestation
        self.assertIn(triple, self.re.g)

    def test_create_print_embodiment(self):
        result = self.re.create_print_embodiment()
        self.assertIsNone(result)

        triple = URIRef(str(self.re)), RDF.type, GraphEntity.print_object
        self.assertIn(triple, self.re.g)


if __name__ == '__main__':
    unittest.main()
