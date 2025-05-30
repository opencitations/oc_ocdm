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

from rdflib import URIRef, Literal, XSD, RDF

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet


class TestBibliographicResource(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def setUp(self):
        self.br1 = self.graph_set.add_br(self.resp_agent)
        self.br2 = self.graph_set.add_br(self.resp_agent)
        self.re = self.graph_set.add_re(self.resp_agent)
        self.be = self.graph_set.add_be(self.resp_agent)
        self.de = self.graph_set.add_de(self.resp_agent)
        self.ar = self.graph_set.add_ar(self.resp_agent)

    def test_has_title(self):
        title = "Resource"
        result = self.br1.has_title(title)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.iri_title, Literal(title, datatype=XSD.string)
        self.assertIn(triple, self.br1.g)

    def test_has_subtitle(self):
        subtitle = "Resource"
        result = self.br1.has_subtitle(subtitle)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.iri_has_subtitle, Literal(subtitle, datatype=XSD.string)
        self.assertIn(triple, self.br1.g)

    def test_is_part_of(self):
        result = self.br1.is_part_of(self.br2)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.iri_part_of, self.br2.res
        self.assertIn(triple, self.br1.g)

    def test_has_citation(self):
        result = self.br1.has_citation(self.br2)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.iri_cites, self.br2.res
        self.assertIn(triple, self.br1.g)

    def test_has_pub_date(self):
        with self.subTest("date is '2020-05-25'"):
            string = "2020-05-25"
            datatype = XSD.date
            result = self.br1.has_pub_date(string)
            self.assertIsNone(result)

            triple = self.br1.res, GraphEntity.iri_has_publication_date, Literal(string, datatype=datatype,
                                                                                 normalize=False)
            self.assertIn(triple, self.br1.g)
        with self.subTest("date is '2020-05'"):
            string = "2020-05"
            datatype = XSD.gYearMonth
            result = self.br1.has_pub_date(string)
            self.assertIsNone(result)

            triple = self.br1.res, GraphEntity.iri_has_publication_date, Literal(string, datatype=datatype,
                                                                                 normalize=False)
            self.assertIn(triple, self.br1.g)
        with self.subTest("date is '2020'"):
            string = "2020"
            datatype = XSD.gYear
            result = self.br1.has_pub_date(string)
            self.assertIsNone(result)

            triple = self.br1.res, GraphEntity.iri_has_publication_date, Literal(string, datatype=datatype,
                                                                                 normalize=False)
            self.assertIn(triple, self.br1.g)

    def test_has_format(self):
        result = self.br1.has_format(self.re)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.iri_embodiment, self.re.res
        self.assertIn(triple, self.br1.g)

    def test_create_number(self):
        number = "1234"
        result = self.br1.has_number(number)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.iri_has_sequence_identifier, Literal(number, datatype=XSD.string)
        self.assertIn(triple, self.br1.g)

    def test_has_edition(self):
        edition = "abcde"
        result = self.br1.has_edition(edition)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.iri_has_edition, Literal(edition, datatype=XSD.string)
        self.assertIn(triple, self.br1.g)

    def test_contains_in_reference_list(self):
        result = self.br1.contains_in_reference_list(self.be)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.iri_contains_reference, self.be.res
        self.assertIn(triple, self.br1.g)

    def test_contains_discourse_element(self):
        result = self.br1.contains_discourse_element(self.de)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.iri_contains_de, self.de.res
        self.assertIn(triple, self.br1.g)

    def test_has_contributor(self):
        result = self.br1.has_contributor(self.ar)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.iri_is_document_context_for, self.ar.res
        self.assertIn(triple, self.br1.g)

    def test_has_related_document(self):
        document = URIRef("http://test/document")
        result = self.br1.has_related_document(document)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.iri_relation, document
        self.assertIn(triple, self.br1.g)

    def test_create_archival_document(self):
        result = self.br1.create_archival_document()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_archival_document
        self.assertIn(triple, self.br1.g)

    def test_create_book(self):
        result = self.br1.create_book()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_book
        self.assertIn(triple, self.br1.g)

    def test_create_book_chapter(self):
        result = self.br1.create_book_chapter()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_book_chapter
        self.assertIn(triple, self.br1.g)

    def test_create_book_part(self):
        result = self.br1.create_book_part()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_part
        self.assertIn(triple, self.br1.g)

    def test_create_book_section(self):
        result = self.br1.create_book_section()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_expression_collection
        self.assertIn(triple, self.br1.g)

    def test_create_book_series(self):
        result = self.br1.create_book_series()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_book_series
        self.assertIn(triple, self.br1.g)

    def test_create_book_set(self):
        result = self.br1.create_book_set()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_book_set
        self.assertIn(triple, self.br1.g)

    def test_create_book_track(self):
        result = self.br1.create_book_track()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_expression
        self.assertIn(triple, self.br1.g)

    def test_create_component(self):
        result = self.br1.create_component()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_expression
        self.assertIn(triple, self.br1.g)

    def test_create_dataset(self):
        result = self.br1.create_dataset()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_data_file
        self.assertIn(triple, self.br1.g)

    def test_create_dissertation(self):
        result = self.br1.create_dissertation()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_thesis
        self.assertIn(triple, self.br1.g)

    def test_create_edited_book(self):
        result = self.br1.create_edited_book()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_book
        self.assertIn(triple, self.br1.g)

    def test_create_journal_article(self):
        result = self.br1.create_journal_article()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_journal_article
        self.assertIn(triple, self.br1.g)

    def test_create_issue(self):
        result = self.br1.create_issue()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_journal_issue
        self.assertIn(triple, self.br1.g)

    def test_create_volume(self):
        result = self.br1.create_volume()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_journal_volume
        self.assertIn(triple, self.br1.g)

    def test_create_journal(self):
        result = self.br1.create_journal()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_journal
        self.assertIn(triple, self.br1.g)

    def test_create_monograph(self):
        result = self.br1.create_monograph()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_book
        self.assertIn(triple, self.br1.g)

    def test_create_proceedings_article(self):
        result = self.br1.create_proceedings_article()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_proceedings_paper
        self.assertIn(triple, self.br1.g)

    def test_create_proceedings(self):
        result = self.br1.create_proceedings()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_academic_proceedings
        self.assertIn(triple, self.br1.g)

    def test_create_reference_book(self):
        result = self.br1.create_reference_book()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_reference_book
        self.assertIn(triple, self.br1.g)

    def test_create_reference_entry(self):
        result = self.br1.create_reference_entry()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_reference_entry
        self.assertIn(triple, self.br1.g)

    def test_create_report_series(self):
        result = self.br1.create_report_series()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_series
        self.assertIn(triple, self.br1.g)

    def test_create_report(self):
        result = self.br1.create_report()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_report_document
        self.assertIn(triple, self.br1.g)

    def test_create_standard_series(self):
        result = self.br1.create_standard_series()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_series
        self.assertIn(triple, self.br1.g)

    def test_create_standard(self):
        result = self.br1.create_standard()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_specification_document
        self.assertIn(triple, self.br1.g)

    def test_create_series(self):
        result = self.br1.create_series()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_series
        self.assertIn(triple, self.br1.g)

    def test_create_expression_collection(self):
        result = self.br1.create_expression_collection()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_expression_collection
        self.assertIn(triple, self.br1.g)

    def test_create_other(self):
        result = self.br1.create_other()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.iri_expression
        self.assertIn(triple, self.br1.g)

    def test_assign_more_types_br(self):
        result1 = self.br1.create_series()
        self.assertIsNone(result1)
        result2 = self.br1.create_preprint()
        self.assertIsNone(result2)

        triple1 = self.br1.res, RDF.type, GraphEntity.iri_series
        triple2 = self.br1.res, RDF.type, GraphEntity.iri_preprint
        self.assertIn(triple2, self.br1.g) and not self.assertIn(triple1, self.br1.g)

    def test_merge_specific_types(self):
        """Test merging entities with specific types"""
        
        # Case 1: Merge specific type into generic type
        br_specific = self.graph_set.add_br(self.resp_agent)
        br_generic = self.graph_set.add_br(self.resp_agent)
        
        br_specific.create_journal_article()
        
        # Verify initial types
        self.assertIn((br_specific.res, RDF.type, GraphEntity.iri_journal_article), br_specific.g)
        self.assertIn((br_specific.res, RDF.type, GraphEntity.iri_expression), br_specific.g)
        self.assertIn((br_generic.res, RDF.type, GraphEntity.iri_expression), br_generic.g)
        
        # Merge and verify types are preserved correctly
        br_generic.merge(br_specific)
        self.assertIn((br_generic.res, RDF.type, GraphEntity.iri_journal_article), br_generic.g)
        self.assertIn((br_generic.res, RDF.type, GraphEntity.iri_expression), br_generic.g)
        
        # Case 2: Merge generic type into specific type
        br_specific_2 = self.graph_set.add_br(self.resp_agent)
        br_generic_2 = self.graph_set.add_br(self.resp_agent)
        
        br_specific_2.create_journal_article()
        
        br_specific_2.merge(br_generic_2)
        self.assertIn((br_specific_2.res, RDF.type, GraphEntity.iri_journal_article), br_specific_2.g)
        self.assertIn((br_specific_2.res, RDF.type, GraphEntity.iri_expression), br_specific_2.g)
        
        # Case 3: Merge between two specific types (prefer_self=True)
        br_article = self.graph_set.add_br(self.resp_agent)
        br_book = self.graph_set.add_br(self.resp_agent)
        
        br_article.create_journal_article()
        br_book.create_book()
        
        br_article.merge(br_book, prefer_self=True)
        self.assertIn((br_article.res, RDF.type, GraphEntity.iri_journal_article), br_article.g)
        self.assertIn((br_article.res, RDF.type, GraphEntity.iri_expression), br_article.g)
        self.assertNotIn((br_article.res, RDF.type, GraphEntity.iri_book), br_article.g)
        
        # Case 4: Merge between two specific types (prefer_self=False)
        br_article_2 = self.graph_set.add_br(self.resp_agent)
        br_book_2 = self.graph_set.add_br(self.resp_agent)
        
        br_article_2.create_journal_article()
        br_book_2.create_book()
        
        br_article_2.merge(br_book_2, prefer_self=False)
        self.assertIn((br_article_2.res, RDF.type, GraphEntity.iri_book), br_article_2.g)
        self.assertIn((br_article_2.res, RDF.type, GraphEntity.iri_expression), br_article_2.g)
        self.assertNotIn((br_article_2.res, RDF.type, GraphEntity.iri_journal_article), br_article_2.g)

        # Case 5: Merge a generic entity into a specific entity (prefer_self=True)
        br_specific_3 = self.graph_set.add_br(self.resp_agent)
        br_generic_3 = self.graph_set.add_br(self.resp_agent)
        
        br_specific_3.create_journal_article()
        
        # Verify initial types
        self.assertIn((br_specific_3.res, RDF.type, GraphEntity.iri_journal_article), br_specific_3.g)
        self.assertIn((br_specific_3.res, RDF.type, GraphEntity.iri_expression), br_specific_3.g)
        self.assertIn((br_generic_3.res, RDF.type, GraphEntity.iri_expression), br_generic_3.g)
        
        # Merge and verify types are preserved correctly
        br_specific_3.merge(br_generic_3, prefer_self=True)
        self.assertIn((br_specific_3.res, RDF.type, GraphEntity.iri_journal_article), br_specific_3.g)
        self.assertIn((br_specific_3.res, RDF.type, GraphEntity.iri_expression), br_specific_3.g)

        # Case 6: Merge a generic entity into a specific entity (prefer_self=False)
        br_specific_4 = self.graph_set.add_br(self.resp_agent)
        br_generic_4 = self.graph_set.add_br(self.resp_agent)
        
        br_specific_4.create_journal_article()
        
        br_specific_4.merge(br_generic_4, prefer_self=False)
        self.assertIn((br_specific_4.res, RDF.type, GraphEntity.iri_expression), br_specific_4.g)
        self.assertIn((br_specific_4.res, RDF.type, GraphEntity.iri_journal_article), br_specific_4.g)

if __name__ == '__main__':
    unittest.main()
