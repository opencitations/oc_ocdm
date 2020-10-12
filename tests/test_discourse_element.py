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

from oc_ocdm import GraphEntity
from oc_ocdm import GraphSet
from oc_ocdm.counter_handler import FilesystemCounterHandler


class TestDiscourseElement(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.counter_handler = FilesystemCounterHandler("./info_dir/")
        cls.graph_set = GraphSet("http://test/", "context_base", cls.counter_handler, "", wanted_label=False)

    def setUp(self):
        self.graph_set.g = []
        self.rp = self.graph_set.add_rp(self.__class__.__name__)
        self.pl = self.graph_set.add_pl(self.__class__.__name__)
        self.de1 = self.graph_set.add_de(self.__class__.__name__)
        self.de2 = self.graph_set.add_de(self.__class__.__name__)

    def test_create_title(self):
        title = "DiscourseElement"
        result = self.de1.create_title(title)
        self.assertTrue(result)

        triple = self.de1.res, GraphEntity.title, Literal(title)
        self.assertIn(triple, self.de1.g)

    def test_contains_discourse_element(self):
        result = self.de1.contains_discourse_element(self.de2)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.contains_de, self.de2.res
        self.assertIn(triple, self.de1.g)

    def test_has_next_de(self):
        result = self.de1.has_next_de(self.de2)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.has_next, self.de2.res
        self.assertIn(triple, self.de1.g)

    def test_is_context_of_rp(self):
        result = self.de1.is_context_of_rp(self.rp)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.is_context_of, self.rp.res
        self.assertIn(triple, self.de1.g)

    def test_is_context_of_pl(self):
        result = self.de1.is_context_of_pl(self.pl)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.is_context_of, self.pl.res
        self.assertIn(triple, self.de1.g)

    def test_create_content(self):
        content = "Content"
        result = self.de1.create_content(content)
        self.assertTrue(result)

        triple = self.de1.res, GraphEntity.has_content, Literal(content)
        self.assertIn(triple, self.de1.g)

    def test_create_section(self):
        result = self.de1.create_section()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.section
        self.assertIn(triple, self.de1.g)

    def test_create_section_title(self):
        result = self.de1.create_section_title()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.section_title
        self.assertIn(triple, self.de1.g)

    def test_create_paragraph(self):
        result = self.de1.create_paragraph()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.paragraph
        self.assertIn(triple, self.de1.g)

    def test_create_sentence(self):
        result = self.de1.create_sentence()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.sentence
        self.assertIn(triple, self.de1.g)

    def test_create_text_chunk(self):
        result = self.de1.create_text_chunk()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.text_chunk
        self.assertIn(triple, self.de1.g)

    def test_create_table(self):
        result = self.de1.create_table()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.table
        self.assertIn(triple, self.de1.g)

    def test_create_footnote(self):
        result = self.de1.create_footnote()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.footnote
        self.assertIn(triple, self.de1.g)

    def test_create_caption(self):
        result = self.de1.create_caption()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, GraphEntity.caption
        self.assertIn(triple, self.de1.g)


if __name__ == '__main__':
    unittest.main()
