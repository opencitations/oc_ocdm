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

from rdflib import Literal, URIRef

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet


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

        triple = self.ra.res, GraphEntity.iri_name, Literal(name)
        self.assertIn(triple, self.ra.g)

    def test_has_given_name(self):
        given_name = "GivenName"
        result = self.ra.has_given_name(given_name)
        self.assertIsNone(result)

        triple = self.ra.res, GraphEntity.iri_given_name, Literal(given_name)
        self.assertIn(triple, self.ra.g)

    def test_has_family_name(self):
        family_name = "GivenName"
        result = self.ra.has_family_name(family_name)
        self.assertIsNone(result)

        triple = self.ra.res, GraphEntity.iri_family_name, Literal(family_name)
        self.assertIn(triple, self.ra.g)

    def test_has_related_agent(self):
        related_agent = URIRef("http://test/RelatedAgent")
        result = self.ra.has_related_agent(related_agent)
        self.assertIsNone(result)

        triple = self.ra.res, GraphEntity.iri_relation, related_agent
        self.assertIn(triple, self.ra.g)


if __name__ == '__main__':
    unittest.main()
