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

        triple = self.pl.res, GraphEntity.iri_has_content, Literal(content)
        self.assertIn(triple, self.pl.g)

    def test_contains_element(self):
        result = self.pl.contains_element(self.rp)
        self.assertIsNone(result)

        triple = self.pl.res, GraphEntity.iri_has_element, self.rp.res
        self.assertIn(triple, self.pl.g)


if __name__ == '__main__':
    unittest.main()
