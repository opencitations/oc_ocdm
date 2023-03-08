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

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet

from oc_ocdm.counter_handler.sqlite_counter_handler import SqliteCounterHandler


class TestCitation(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("https://w3id.org/oc/index/coci/", "./info_dir/", "", False)

    def setUp(self):
        self.br1 = self.graph_set.add_br(self.resp_agent)
        self.br2 = self.graph_set.add_br(self.resp_agent)
        self.ci = self.graph_set.add_ci(self.resp_agent)
        self.ci_oci = self.graph_set.add_ci(self.resp_agent, res=URIRef('https://w3id.org/oc/index/coci/ci/020010000023601000907630001040258020000010008010559090238044008040338381018136312231227010309014203370037122439026325-020010305093619112227370109090937010437073701020309'))

    def test_has_citing_entity(self):
        result = self.ci.has_citing_entity(self.br1)
        self.assertIsNone(result)

        triple = self.ci.res, GraphEntity.iri_has_citing_entity, self.br1.res
        self.assertIn(triple, self.ci.g)

    def test_create_cited_entity(self):
        result = self.ci.has_cited_entity(self.br2)
        self.assertIsNone(result)

        triple = self.ci.res, GraphEntity.iri_has_cited_entity, self.br2.res
        self.assertIn(triple, self.ci.g)

    def test_has_citation_creation_date(self):
        with self.subTest("date is '2020-05-25'"):
            string = "2020-05-25"
            datatype = XSD.date
            result = self.ci.has_citation_creation_date(string)
            self.assertIsNone(result)

            triple = self.ci.res, GraphEntity.iri_has_citation_creation_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.ci.g)
        with self.subTest("date is '2020-05'"):
            string = "2020-05"
            datatype = XSD.gYearMonth
            result = self.ci.has_citation_creation_date(string)
            self.assertIsNone(result)

            triple = self.ci.res, GraphEntity.iri_has_citation_creation_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.ci.g)
        with self.subTest("date is '2020'"):
            string = "2020"
            datatype = XSD.gYear
            result = self.ci.has_citation_creation_date(string)
            self.assertIsNone(result)

            triple = self.ci.res, GraphEntity.iri_has_citation_creation_date, Literal(string, datatype=datatype,
                                                                                      normalize=False)
            self.assertIn(triple, self.ci.g)

    def test_has_citation_time_span(self):
        duration = "P2Y6M5DT12H35M30S"  # 2 years, 6 months, 5 days, 12 hours, 35 minutes, 30 seconds
        datatype = XSD.duration
        result = self.ci.has_citation_time_span(duration)
        self.assertIsNone(result)

        triple = self.ci.res, GraphEntity.iri_has_citation_time_span, Literal(duration, datatype=datatype,
                                                                              normalize=False)
        self.assertIn(triple, self.ci.g)

    def test_has_citation_characterization(self):
        characterization = URIRef("http://test/characterization")
        result = self.ci.has_citation_characterization(characterization)
        self.assertIsNone(result)

        triple = self.ci.res, GraphEntity.iri_citation_characterisation, characterization
        self.assertIn(triple, self.ci.g)

    def test_create_self_citation(self):
        result = self.ci.create_self_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.iri_self_citation
        self.assertIn(triple, self.ci.g)

    def test_create_affiliation_self_citation(self):
        result = self.ci.create_affiliation_self_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.iri_affiliation_self_citation
        self.assertIn(triple, self.ci.g)

    def test_create_author_network_self_citation(self):
        result = self.ci.create_author_network_self_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.iri_author_network_self_citation
        self.assertIn(triple, self.ci.g)

    def test_create_author_self_citation(self):
        result = self.ci.create_author_self_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.iri_author_self_citation
        self.assertIn(triple, self.ci.g)

    def test_create_funder_self_citation(self):
        result = self.ci.create_funder_self_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.iri_funder_self_citation
        self.assertIn(triple, self.ci.g)

    def test_create_journal_self_citation(self):
        result = self.ci.create_journal_self_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.iri_journal_self_citation
        self.assertIn(triple, self.ci.g)

    def test_create_journal_cartel_citation(self):
        result = self.ci.create_journal_cartel_citation()
        self.assertIsNone(result)

        triple = self.ci.res, RDF.type, GraphEntity.iri_journal_cartel_citation
        self.assertIn(triple, self.ci.g)

    def test_create_distant_citation(self):
        result = self.ci.create_distant_citation()
        self.assertIsNone(result)
        triple = self.ci.res, RDF.type, GraphEntity.iri_distant_citation
        self.assertIn(triple, self.ci.g)


if __name__ == '__main__':
    unittest.main()
