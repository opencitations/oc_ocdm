#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from rdflib import RDF, XSD

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet
from triplelite import RDFTerm


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

        triple = self.de1.res, GraphEntity.iri_title, RDFTerm("literal", title, str(XSD.string))
        self.assertIn(triple, self.de1.g)

    def test_contains_discourse_element(self):
        result = self.de1.contains_discourse_element(self.de2)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.iri_contains_de, RDFTerm("uri", str(self.de2.res))
        self.assertIn(triple, self.de1.g)

    def test_has_next_de(self):
        result = self.de1.has_next_de(self.de2)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.iri_has_next, RDFTerm("uri", str(self.de2.res))
        self.assertIn(triple, self.de1.g)

    def test_is_context_of_rp(self):
        result = self.de1.is_context_of_rp(self.rp)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.iri_is_context_of, RDFTerm("uri", str(self.rp.res))
        self.assertIn(triple, self.de1.g)

    def test_is_context_of_pl(self):
        result = self.de1.is_context_of_pl(self.pl)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.iri_is_context_of, RDFTerm("uri", str(self.pl.res))
        self.assertIn(triple, self.de1.g)

    def test_has_content(self):
        content = "Content"
        result = self.de1.has_content(content)
        self.assertIsNone(result)

        triple = self.de1.res, GraphEntity.iri_has_content, RDFTerm("literal", content, str(XSD.string))
        self.assertIn(triple, self.de1.g)

    def test_create_section(self):
        result = self.de1.create_section()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_section))
        self.assertIn(triple, self.de1.g)

    def test_create_section_title(self):
        result = self.de1.create_section_title()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_section_title))
        self.assertIn(triple, self.de1.g)

    def test_create_paragraph(self):
        result = self.de1.create_paragraph()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_paragraph))
        self.assertIn(triple, self.de1.g)

    def test_create_sentence(self):
        result = self.de1.create_sentence()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_sentence))
        self.assertIn(triple, self.de1.g)

    def test_create_text_chunk(self):
        result = self.de1.create_text_chunk()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_text_chunk))
        self.assertIn(triple, self.de1.g)

    def test_create_table(self):
        result = self.de1.create_table()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_table))
        self.assertIn(triple, self.de1.g)

    def test_create_footnote(self):
        result = self.de1.create_footnote()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_footnote))
        self.assertIn(triple, self.de1.g)

    def test_create_caption(self):
        result = self.de1.create_caption()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_caption))
        self.assertIn(triple, self.de1.g)

    def test_assign_more_structural_types_de(self):
        result1 = self.de1.create_table()
        self.assertIsNone(result1)
        result2 = self.de1.create_footnote()
        self.assertIsNone(result2)

        triple1 = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_table))
        triple2 = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_footnote))
        self.assertIn(triple2, self.de1.g)
        self.assertNotIn(triple1, self.de1.g)

    def test_assign_more_rhetorical_types_de(self):
        result1 = self.de1.create_materials()
        self.assertIsNone(result1)
        result2 = self.de1.create_methods()
        self.assertIsNone(result2)

        triple1 = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_materials))
        triple2 = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_methods))
        self.assertIn(triple2, self.de1.g)
        self.assertIn(triple1, self.de1.g)

    def test_create_introduction(self):
        result = self.de1.create_introduction()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_introduction))
        self.assertIn(triple, self.de1.g)

    def test_create_related_work(self):
        result = self.de1.create_related_work()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_related_work))
        self.assertIn(triple, self.de1.g)

    def test_create_results(self):
        result = self.de1.create_results()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_results))
        self.assertIn(triple, self.de1.g)

    def test_create_discussion(self):
        result = self.de1.create_discussion()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_discussion))
        self.assertIn(triple, self.de1.g)

    def test_create_conclusion(self):
        result = self.de1.create_conclusion()
        self.assertIsNone(result)

        triple = self.de1.res, RDF.type, RDFTerm("uri", str(GraphEntity.iri_conclusion))
        self.assertIn(triple, self.de1.g)


if __name__ == '__main__':
    unittest.main()
