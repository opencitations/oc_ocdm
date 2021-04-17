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

from rdflib import Literal, RDF

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet


class TestDiscourseElement(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def setUp(self):
        self.rp = self.graph_set.add_rp(self.resp_agent)
        self.pl = self.graph_set.add_pl(self.resp_agent)
        self.de1 = self.graph_set.add_de(self.resp_agent)
        self.de2 = self.graph_set.add_de(self.resp_agent)

    def test_has_title(self):
        title = "DiscourseElement"
        result = self.de1.has_title(title)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.iri_title, Literal(title)
        self.assertIn(triple, self.de1.g)

    def test_contains_discourse_element(self):
        result = self.de1.contains_discourse_element(self.de2)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.iri_contains_de, self.de2.res
        self.assertIn(triple, self.de1.g)

    def test_has_next_de(self):
        result = self.de1.has_next_de(self.de2)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.iri_has_next, self.de2.res
        self.assertIn(triple, self.de1.g)

    def test_is_context_of_rp(self):
        result = self.de1.is_context_of_rp(self.rp)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.iri_is_context_of, self.rp.res
        self.assertIn(triple, self.de1.g)

    def test_is_context_of_pl(self):
        result = self.de1.is_context_of_pl(self.pl)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.iri_is_context_of, self.pl.res
        self.assertIn(triple, self.de1.g)

    def test_has_content(self):
        content = "Content"
        result = self.de1.has_content(content)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.iri_has_content, Literal(content)
        self.assertIn(triple, self.de1.g)

    def test_create_section(self):
        result = self.de1.create_section()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.iri_section
        self.assertIn(triple, self.de1.g)

    def test_create_section_title(self):
        result = self.de1.create_section_title()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.iri_section_title
        self.assertIn(triple, self.de1.g)

    def test_create_paragraph(self):
        result = self.de1.create_paragraph()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.iri_paragraph
        self.assertIn(triple, self.de1.g)

    def test_create_sentence(self):
        result = self.de1.create_sentence()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.iri_sentence
        self.assertIn(triple, self.de1.g)

    def test_create_text_chunk(self):
        result = self.de1.create_text_chunk()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.iri_text_chunk
        self.assertIn(triple, self.de1.g)

    def test_create_table(self):
        result = self.de1.create_table()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.iri_table
        self.assertIn(triple, self.de1.g)

    def test_create_footnote(self):
        result = self.de1.create_footnote()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.iri_footnote
        self.assertIn(triple, self.de1.g)

    def test_create_caption(self):
        result = self.de1.create_caption()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.iri_caption
        self.assertIn(triple, self.de1.g)


if __name__ == '__main__':
    unittest.main()
