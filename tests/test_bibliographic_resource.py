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

from oc_ocdm import GraphEntity
from oc_ocdm import GraphSet
from oc_ocdm.counter_handler import FilesystemCounterHandler


class TestBibliographicResource(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.counter_handler = FilesystemCounterHandler("./info_dir/")
        cls.graph_set = GraphSet("http://test/", "context_base", cls.counter_handler, "", wanted_label=False)

    def setUp(self):
        self.graph_set.g = []
        self.br1 = self.graph_set.add_br(self.__class__.__name__)
        self.br2 = self.graph_set.add_br(self.__class__.__name__)
        self.re = self.graph_set.add_re(self.__class__.__name__)
        self.be = self.graph_set.add_be(self.__class__.__name__)
        self.de = self.graph_set.add_de(self.__class__.__name__)

    def test_create_title(self):
        title = "Resource"
        result = self.br1.create_title(title)
        self.assertTrue(result)

        triple = self.br1.res, GraphEntity.title, Literal(title)
        self.assertIn(triple, self.br1.g)

    def test_create_subtitle(self):
        subtitle = "Resource"
        result = self.br1.create_subtitle(subtitle)
        self.assertTrue(result)

        triple = self.br1.res, GraphEntity.has_subtitle, Literal(subtitle)
        self.assertIn(triple, self.br1.g)

    def test_has_part(self):
        result = self.br1.has_part(self.br2)
        self.assertIsNone(result)

        triple = self.br2.res, GraphEntity.part_of, self.br1.res
        self.assertIn(triple, self.br2.g)

    def test_has_citation(self):
        result = self.br1.has_citation(self.br2)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.cites, self.br2.res
        self.assertIn(triple, self.br1.g)

    def test_create_pub_date(self):
        with self.subTest("date_list is [int, int, int]"):
            string = "2020-05-25"
            datatype = XSD.date
            result = self.br1.create_pub_date([2020, 5, 25])
            self.assertTrue(result)

            triple = self.br1.res, GraphEntity.has_publication_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.br1.g)
        with self.subTest("date_list is [int, int]"):
            string = "2020-05"
            datatype = XSD.gYearMonth
            result = self.br1.create_pub_date([2020, 5])
            self.assertTrue(result)

            triple = self.br1.res, GraphEntity.has_publication_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.br1.g)
        with self.subTest("date_list is [int]"):
            string = "2020"
            datatype = XSD.gYear
            result = self.br1.create_pub_date([2020])
            self.assertTrue(result)

            triple = self.br1.res, GraphEntity.has_publication_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.br1.g)
        with self.subTest("date_list is [int, None]"):
            string = "2020"
            datatype = XSD.gYear
            result = self.br1.create_pub_date([2020, None])
            self.assertTrue(result)

            triple = self.br1.res, GraphEntity.has_publication_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.br1.g)
        with self.subTest("date_list is [int, None, None]"):
            string = "2020"
            datatype = XSD.gYear
            result = self.br1.create_pub_date([2020, None, None])
            self.assertTrue(result)

            triple = self.br1.res, GraphEntity.has_publication_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.br1.g)
        with self.subTest("date_list is [None, None, None]"):
            prev_len = len(self.br1.g)
            result = self.br1.create_pub_date([None, None, None])
            self.assertFalse(result)
            self.assertIsNotNone(result)

            after_len = len(self.br1.g)
            self.assertEqual(prev_len, after_len)
        with self.subTest("date_list is empty"):
            prev_len = len(self.br1.g)
            result = self.br1.create_pub_date([])
            self.assertFalse(result)
            self.assertIsNotNone(result)

            after_len = len(self.br1.g)
            self.assertEqual(prev_len, after_len)
        with self.subTest("date_list is None"):
            prev_len = len(self.br1.g)
            result = self.br1.create_pub_date()
            self.assertFalse(result)
            self.assertIsNotNone(result)

            after_len = len(self.br1.g)
            self.assertEqual(prev_len, after_len)
        with self.subTest("date_list is [int, 1, int]"):
            string = "2020-01-25"
            datatype = XSD.date
            result = self.br1.create_pub_date([2020, 1, 25])
            self.assertTrue(result)

            triple = self.br1.res, GraphEntity.has_publication_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.br1.g)
        with self.subTest("date_list is [int, 1, 1]"):
            string = "2020"
            datatype = XSD.gYear
            result = self.br1.create_pub_date([2020, 1, 1])
            self.assertTrue(result)

            triple = self.br1.res, GraphEntity.has_publication_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.br1.g)
        with self.subTest("date_list is [int, 5, 1]"):
            string = "2020-05-01"
            datatype = XSD.date
            result = self.br1.create_pub_date([2020, 5, 1])
            self.assertTrue(result)

            triple = self.br1.res, GraphEntity.has_publication_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.br1.g)

    def test_has_format(self):
        result = self.br1.has_format(self.re)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.embodiment, self.re.res
        self.assertIn(triple, self.br1.g)

    def test_create_number(self):
        number = "1234"
        result = self.br1.create_number(number)
        self.assertTrue(result)

        triple = self.br1.res, GraphEntity.has_sequence_identifier, Literal(number)
        self.assertIn(triple, self.br1.g)

    def test_has_edition(self):
        edition = "abcde"
        result = self.br1.has_edition(edition)
        self.assertTrue(result)

        triple = self.br1.res, GraphEntity.has_edition, Literal(edition)
        self.assertIn(triple, self.br1.g)

    def test_contains_in_reference_list(self):
        result = self.br1.contains_in_reference_list(self.be)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.contains_reference, self.be.res
        self.assertIn(triple, self.br1.g)

    def test_contains_discourse_element(self):
        result = self.br1.contains_discourse_element(self.de)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.contains_de, self.de.res
        self.assertIn(triple, self.br1.g)

    def test_has_reference(self):
        result = self.br1.has_reference(self.be)
        self.assertIsNone(result)

        triple = self.be.res, GraphEntity.references, self.br1.res
        self.assertIn(triple, self.be.g)

    def test_has_related_document(self):
        document = URIRef("http://test/document")
        result = self.br1.has_related_document(document)
        self.assertIsNone(result)

        triple = self.br1.res, GraphEntity.relation, document
        self.assertIn(triple, self.br1.g)

    def test_create_archival_document(self):
        result = self.br1.create_archival_document()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.archival_document
        self.assertIn(triple, self.br1.g)

    def test_create_book(self):
        result = self.br1.create_book()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.book
        self.assertIn(triple, self.br1.g)

    def test_create_book_chapter(self):
        result = self.br1.create_book_chapter()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.book_chapter
        self.assertIn(triple, self.br1.g)

    def test_create_book_part(self):
        result = self.br1.create_book_part()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.part
        self.assertIn(triple, self.br1.g)

    def test_create_book_section(self):
        result = self.br1.create_book_section()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.expression_collection
        self.assertIn(triple, self.br1.g)

    def test_create_book_series(self):
        result = self.br1.create_book_series()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.book_series
        self.assertIn(triple, self.br1.g)

    def test_create_book_set(self):
        result = self.br1.create_book_set()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.book_set
        self.assertIn(triple, self.br1.g)

    def test_create_book_track(self):
        result = self.br1.create_book_track()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.expression
        self.assertIn(triple, self.br1.g)

    def test_create_component(self):
        result = self.br1.create_component()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.expression
        self.assertIn(triple, self.br1.g)

    def test_create_dataset(self):
        result = self.br1.create_dataset()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.data_file
        self.assertIn(triple, self.br1.g)

    def test_create_dissertation(self):
        result = self.br1.create_dissertation()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.thesis
        self.assertIn(triple, self.br1.g)

    def test_create_edited_book(self):
        result = self.br1.create_edited_book()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.book
        self.assertIn(triple, self.br1.g)

    def test_create_journal_article(self):
        result = self.br1.create_journal_article()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.journal_article
        self.assertIn(triple, self.br1.g)

    def test_create_issue(self):
        result = self.br1.create_issue()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.journal_issue
        self.assertIn(triple, self.br1.g)

    def test_create_volume(self):
        result = self.br1.create_volume()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.journal_volume
        self.assertIn(triple, self.br1.g)

    def test_create_journal(self):
        result = self.br1.create_journal()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.journal
        self.assertIn(triple, self.br1.g)

    def test_create_monograph(self):
        result = self.br1.create_monograph()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.book
        self.assertIn(triple, self.br1.g)

    def test_create_proceedings_article(self):
        result = self.br1.create_proceedings_article()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.proceedings_paper
        self.assertIn(triple, self.br1.g)

    def test_create_proceedings(self):
        result = self.br1.create_proceedings()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.academic_proceedings
        self.assertIn(triple, self.br1.g)

    def test_create_reference_book(self):
        result = self.br1.create_reference_book()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.reference_book
        self.assertIn(triple, self.br1.g)

    def test_create_reference_entry(self):
        result = self.br1.create_reference_entry()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.reference_entry
        self.assertIn(triple, self.br1.g)

    def test_create_report_series(self):
        result = self.br1.create_report_series()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.series
        self.assertIn(triple, self.br1.g)

    def test_create_report(self):
        result = self.br1.create_report()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.report_document
        self.assertIn(triple, self.br1.g)

    def test_create_standard_series(self):
        result = self.br1.create_standard_series()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.series
        self.assertIn(triple, self.br1.g)

    def test_create_standard(self):
        result = self.br1.create_standard()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.specification_document
        self.assertIn(triple, self.br1.g)

    def test_create_series(self):
        result = self.br1.create_series()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.series
        self.assertIn(triple, self.br1.g)

    def test_create_expression_collection(self):
        result = self.br1.create_expression_collection()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.expression_collection
        self.assertIn(triple, self.br1.g)

    def test_create_other(self):
        result = self.br1.create_other()
        self.assertIsNone(result)

        triple = self.br1.res, RDF.type, GraphEntity.expression
        self.assertIn(triple, self.br1.g)


if __name__ == '__main__':
    unittest.main()
