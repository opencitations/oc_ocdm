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


class TestIdentifier(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def setUp(self):
        self.identifier = self.graph_set.add_id(self.resp_agent)

    def test_create_orcid(self):
        orcid = "abcdefghi"
        result = self.identifier.create_orcid(orcid)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(orcid)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_orcid
        self.assertIn(triple, self.identifier.g)

    def test_create_doi(self):
        doi = "abcdefghi"
        result = self.identifier.create_doi(doi)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(doi)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_doi
        self.assertIn(triple, self.identifier.g)

    def test_create_pmid(self):
        pmid = "abcdefghi"
        result = self.identifier.create_pmid(pmid)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(pmid)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_pmid
        self.assertIn(triple, self.identifier.g)

    def test_create_pmcid(self):
        pmcid = "abcdefghi"
        result = self.identifier.create_pmcid(pmcid)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(pmcid)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_pmcid
        self.assertIn(triple, self.identifier.g)

    def test_create_issn(self):
        issn = "abcdefghi"
        result = self.identifier.create_issn(issn)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(issn)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_issn
        self.assertIn(triple, self.identifier.g)

    def test_create_isbn(self):
        isbn = "abcdefghi"
        result = self.identifier.create_isbn(isbn)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(isbn)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_isbn
        self.assertIn(triple, self.identifier.g)

    def test_create_url(self):
        url = "abcdefghi"
        result = self.identifier.create_url(url)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(url)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_url
        self.assertIn(triple, self.identifier.g)

    def test_create_xpath(self):
        xpath = "abcdefghi"
        result = self.identifier.create_xpath(xpath)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(xpath)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_xpath
        self.assertIn(triple, self.identifier.g)

    def test_create_intrepid(self):
        intrepid = "abcdefghi"
        result = self.identifier.create_intrepid(intrepid)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(intrepid)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_intrepid
        self.assertIn(triple, self.identifier.g)

    def test_create_xmlid(self):
        xmlid = "abcdefghi"
        result = self.identifier.create_xmlid(xmlid)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(xmlid)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_xmlid
        self.assertIn(triple, self.identifier.g)

    def test_create_wikidata(self):
        wikidata = "abcdefghi"
        result = self.identifier.create_wikidata(wikidata)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(wikidata)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_wikidata
        self.assertIn(triple, self.identifier.g)

    def test_create_wikipedia(self):
        wikipedia = "abcdefghi"
        result = self.identifier.create_wikipedia(wikipedia)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(wikipedia)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_wikipedia
        self.assertIn(triple, self.identifier.g)

    def test_create_crossref(self):
        crossref = "abcdefghi"
        result = self.identifier.create_crossref(crossref)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(crossref)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_crossref
        self.assertIn(triple, self.identifier.g)

    def test_create_datacite(self):
        datacite = "332"
        result = self.identifier.create_datacite(datacite)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(datacite)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_datacite
        self.assertIn(triple, self.identifier.g)

    def test_create_viaf(self):
        viaf = "abcdefghi"
        result = self.identifier.create_viaf(viaf)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, Literal(viaf)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, GraphEntity.iri_viaf
        self.assertIn(triple, self.identifier.g)


if __name__ == '__main__':
    unittest.main()
