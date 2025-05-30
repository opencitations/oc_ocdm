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

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet
from rdflib import XSD, Literal


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

        triple = self.rp1.res, GraphEntity.iri_has_content, Literal(content, datatype=XSD.string)
        self.assertIn(triple, self.rp1.g)

    def test_has_next_rp(self):
        result = self.rp1.has_next_rp(self.rp2)
        self.assertIsNone(result)

        triple = self.rp1.res, GraphEntity.iri_has_next, self.rp2.res
        self.assertIn(triple, self.rp1.g)

    def test_denotes_be(self):
        result = self.rp1.denotes_be(self.be)
        self.assertIsNone(result)

        triple = self.rp1.res, GraphEntity.iri_denotes, self.be.res
        self.assertIn(triple, self.rp1.g)

    def test_has_annotation(self):
        result = self.rp1.has_annotation(self.an)
        self.assertIsNone(result)

        triple = self.rp1.res, GraphEntity.iri_has_annotation, self.an.res
        self.assertIn(triple, self.rp1.g)


if __name__ == '__main__':
    unittest.main()
