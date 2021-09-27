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

from rdflib import Literal

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet


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

        triple = self.be.res, GraphEntity.iri_has_content, Literal(content)
        self.assertIn(triple, self.be.g)

    def test_has_annotation(self):
        result = self.be.has_annotation(self.an)
        self.assertIsNone(result)

        triple = self.be.res, GraphEntity.iri_has_annotation, self.an.res
        self.assertIn(triple, self.be.g)

    def test_references(self):
        result = self.be.references_br(self.br)
        self.assertIsNone(result)

        triple = self.be.res, GraphEntity.iri_references, self.br.res
        self.assertIn(triple, self.be.g)


if __name__ == '__main__':
    unittest.main()
