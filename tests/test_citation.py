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

from rdflib import URIRef, XSD, Literal, RDF

from oc_ocdm import GraphEntity
from oc_ocdm import GraphSet
from oc_ocdm.counter_handler import FilesystemCounterHandler


class TestCitation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.counter_handler = FilesystemCounterHandler("./info_dir/")
        cls.graph_set = GraphSet("http://test/", "context_base", cls.counter_handler, "", wanted_label=False)

    def setUp(self):
        self.graph_set.g = []
        self.br1 = self.graph_set.add_br(self.__class__.__name__)
        self.br2 = self.graph_set.add_br(self.__class__.__name__)
        self.ci = self.graph_set.add_ci(self.__class__.__name__)

    def test_create_citing_entity(self):
        result = self.ci.create_citing_entity(self.br1)
        self.assertIsNone(result)

        triple = self.ci.res, GraphEntity.has_citing_entity, self.br1.res
        self.assertIn(triple, self.ci.g)

    def test_create_cited_entity(self):
        result = self.ci.create_cited_entity(self.br2)
        self.assertIsNone(result)

        triple = self.ci.res, GraphEntity.has_cited_entity, self.br2.res
        self.assertIn(triple, self.ci.g)

    def test_has_citation_creation_date(self):
        with self.subTest("date_list is [int, int, int]"):
            string = "2020-05-25"
            datatype = XSD.date
            result = self.ci.has_citation_creation_date([2020, 5, 25])
            self.assertTrue(result)

            triple = self.ci.res, GraphEntity.has_citation_creation_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.ci.g)
        with self.subTest("date_list is [int, int]"):
            string = "2020-05"
            datatype = XSD.gYearMonth
            result = self.ci.has_citation_creation_date([2020, 5])
            self.assertTrue(result)

            triple = self.ci.res, GraphEntity.has_citation_creation_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.ci.g)
        with self.subTest("date_list is [int]"):
            string = "2020"
            datatype = XSD.gYear
            result = self.ci.has_citation_creation_date([2020])
            self.assertTrue(result)

            triple = self.ci.res, GraphEntity.has_citation_creation_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.ci.g)
        with self.subTest("date_list is [int, None]"):
            string = "2020"
            datatype = XSD.gYear
            result = self.ci.has_citation_creation_date([2020, None])
            self.assertTrue(result)

            triple = self.ci.res, GraphEntity.has_citation_creation_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.ci.g)
        with self.subTest("date_list is [int, None, None]"):
            string = "2020"
            datatype = XSD.gYear
            result = self.ci.has_citation_creation_date([2020, None, None])
            self.assertTrue(result)

            triple = self.ci.res, GraphEntity.has_citation_creation_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.ci.g)
        with self.subTest("date_list is [None, None, None]"):
            prev_len = len(self.ci.g)
            result = self.ci.has_citation_creation_date([None, None, None])
            self.assertFalse(result)
            self.assertIsNotNone(result)

            after_len = len(self.ci.g)
            self.assertEqual(prev_len, after_len)
        with self.subTest("date_list is empty"):
            prev_len = len(self.ci.g)
            result = self.ci.has_citation_creation_date([])
            self.assertFalse(result)
            self.assertIsNotNone(result)

            after_len = len(self.ci.g)
            self.assertEqual(prev_len, after_len)
        with self.subTest("date_list is None"):
            prev_len = len(self.ci.g)
            result = self.ci.has_citation_creation_date()
            self.assertFalse(result)
            self.assertIsNotNone(result)

            after_len = len(self.ci.g)
            self.assertEqual(prev_len, after_len)
        with self.subTest("date_list is [int, 1, int]"):
            string = "2020-01-25"
            datatype = XSD.date
            result = self.ci.has_citation_creation_date([2020, 1, 25])
            self.assertTrue(result)

            triple = self.ci.res, GraphEntity.has_citation_creation_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.ci.g)
        with self.subTest("date_list is [int, 1, 1]"):
            string = "2020"
            datatype = XSD.gYear
            result = self.ci.has_citation_creation_date([2020, 1, 1])
            self.assertTrue(result)

            triple = self.ci.res, GraphEntity.has_citation_creation_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.ci.g)
        with self.subTest("date_list is [int, 5, 1]"):
            string = "2020-05-01"
            datatype = XSD.date
            result = self.ci.has_citation_creation_date([2020, 5, 1])
            self.assertTrue(result)

            triple = self.ci.res, GraphEntity.has_citation_creation_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.ci.g)

    def test_has_citation_time_span(self):
        duration = "P2Y6M5DT12H35M30S"  # 2 years, 6 months, 5 days, 12 hours, 35 minutes, 30 seconds
        datatype = XSD.duration
        result = self.ci.has_citation_time_span(duration)
        self.assertTrue(result)

        triple = self.ci.res, GraphEntity.has_citation_time_span, Literal(duration, datatype=datatype,
                                                                                       normalize=False)
        self.assertIn(triple, self.ci.g)

    def test_has_citation_characterization(self):
        characterization = URIRef("http://test/characterization")
        result = self.ci.has_citation_characterization(characterization)
        self.assertIsNone(result)

        triple = self.ci.res, GraphEntity.citation_characterisation, characterization
        self.assertIn(triple, self.ci.g)

    def test_create_self_citation(self):
        result = self.ci.create_self_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.self_citation
        self.assertIn(triple, self.ci.g)

    def test_create_affiliation_self_citation(self):
        result = self.ci.create_affiliation_self_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.affiliation_self_citation
        self.assertIn(triple, self.ci.g)

    def test_create_author_network_self_citation(self):
        result = self.ci.create_author_network_self_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.author_network_self_citation
        self.assertIn(triple, self.ci.g)

    def test_create_author_self_citation(self):
        result = self.ci.create_author_self_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.author_self_citation
        self.assertIn(triple, self.ci.g)

    def test_create_funder_self_citation(self):
        result = self.ci.create_funder_self_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.funder_self_citation
        self.assertIn(triple, self.ci.g)

    def test_create_journal_self_citation(self):
        result = self.ci.create_journal_self_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.journal_self_citation
        self.assertIn(triple, self.ci.g)

    def test_create_journal_cartel_citation(self):
        result = self.ci.create_journal_cartel_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.journal_cartel_citation
        self.assertIn(triple, self.ci.g)

    def test_create_distant_citation(self):
        result = self.ci.create_distant_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.distant_citation
        self.assertIn(triple, self.ci.g)


if __name__ == '__main__':
    unittest.main()
