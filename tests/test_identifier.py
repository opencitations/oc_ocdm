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

from rdflib import URIRef, Literal

from oc_ocdm import GraphEntity
from oc_ocdm import GraphSet
from oc_ocdm.counter_handler import FilesystemCounterHandler


class TestIdentifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.counter_handler = FilesystemCounterHandler("./info_dir/")
        cls.graph_set = GraphSet("http://test/", "context_base", cls.counter_handler, "", wanted_label=False)

    def setUp(self):
        self.graph_set.g = []
        self.id = self.graph_set.add_id(self.__class__.__name__)

    def test_create_orcid(self):
        orcid = "abcdefghi"
        result = self.id.create_orcid(orcid)
        self.assertTrue(result)

        triple = self.id.res, GraphEntity.has_literal_value, Literal(orcid)
        self.assertIn(triple, self.id.g)

        triple = self.id.res, GraphEntity.uses_identifier_scheme, GraphEntity.orcid
        self.assertIn(triple, self.id.g)

    def test_create_doi(self):
        doi = "abcdefghi"
        result = self.id.create_doi(doi)
        self.assertTrue(result)

        triple = self.id.res, GraphEntity.has_literal_value, Literal(doi)
        self.assertIn(triple, self.id.g)

        triple = self.id.res, GraphEntity.uses_identifier_scheme, GraphEntity.doi
        self.assertIn(triple, self.id.g)

    def test_create_pmid(self):
        pmid = "abcdefghi"
        result = self.id.create_pmid(pmid)
        self.assertTrue(result)

        triple = self.id.res, GraphEntity.has_literal_value, Literal(pmid)
        self.assertIn(triple, self.id.g)

        triple = self.id.res, GraphEntity.uses_identifier_scheme, GraphEntity.pmid
        self.assertIn(triple, self.id.g)

    def test_create_pmcid(self):
        pmcid = "abcdefghi"
        result = self.id.create_pmcid(pmcid)
        self.assertTrue(result)

        triple = self.id.res, GraphEntity.has_literal_value, Literal(pmcid)
        self.assertIn(triple, self.id.g)

        triple = self.id.res, GraphEntity.uses_identifier_scheme, GraphEntity.pmcid
        self.assertIn(triple, self.id.g)

    def test_create_issn(self):
        issn = "abcdefghi"
        result = self.id.create_issn(issn)
        self.assertTrue(result)

        triple = self.id.res, GraphEntity.has_literal_value, Literal(issn)
        self.assertIn(triple, self.id.g)

        triple = self.id.res, GraphEntity.uses_identifier_scheme, GraphEntity.issn
        self.assertIn(triple, self.id.g)

    def test_create_isbn(self):
        isbn = "abcdefghi"
        result = self.id.create_isbn(isbn)
        self.assertTrue(result)

        triple = self.id.res, GraphEntity.has_literal_value, Literal(isbn)
        self.assertIn(triple, self.id.g)

        triple = self.id.res, GraphEntity.uses_identifier_scheme, GraphEntity.isbn
        self.assertIn(triple, self.id.g)

    def test_create_url(self):
        url = "abcdefghi"
        result = self.id.create_url(url)
        self.assertTrue(result)

        triple = self.id.res, GraphEntity.has_literal_value, Literal(url)
        self.assertIn(triple, self.id.g)

        triple = self.id.res, GraphEntity.uses_identifier_scheme, GraphEntity.url
        self.assertIn(triple, self.id.g)

    def test_create_xpath(self):
        xpath = "abcdefghi"
        result = self.id.create_xpath(xpath)
        self.assertTrue(result)

        triple = self.id.res, GraphEntity.has_literal_value, Literal(xpath)
        self.assertIn(triple, self.id.g)

        triple = self.id.res, GraphEntity.uses_identifier_scheme, GraphEntity.xpath
        self.assertIn(triple, self.id.g)

    def test_create_intrepid(self):
        intrepid = "abcdefghi"
        result = self.id.create_intrepid(intrepid)
        self.assertTrue(result)

        triple = self.id.res, GraphEntity.has_literal_value, Literal(intrepid)
        self.assertIn(triple, self.id.g)

        triple = self.id.res, GraphEntity.uses_identifier_scheme, GraphEntity.intrepid
        self.assertIn(triple, self.id.g)

    def test_create_xmlid(self):
        xmlid = "abcdefghi"
        result = self.id.create_xmlid(xmlid)
        self.assertTrue(result)

        triple = self.id.res, GraphEntity.has_literal_value, Literal(xmlid)
        self.assertIn(triple, self.id.g)

        triple = self.id.res, GraphEntity.uses_identifier_scheme, GraphEntity.xmlid
        self.assertIn(triple, self.id.g)

    def test_create_wikidata(self):
        wikidata = "abcdefghi"
        result = self.id.create_wikidata(wikidata)
        self.assertTrue(result)

        triple = self.id.res, GraphEntity.has_literal_value, Literal(wikidata)
        self.assertIn(triple, self.id.g)

        triple = self.id.res, GraphEntity.uses_identifier_scheme, GraphEntity.wikidata
        self.assertIn(triple, self.id.g)

    def test_create_crossref(self):
        crossref = "abcdefghi"
        result = self.id.create_crossref(crossref)
        self.assertTrue(result)

        triple = self.id.res, GraphEntity.has_literal_value, Literal(crossref)
        self.assertIn(triple, self.id.g)

        triple = self.id.res, GraphEntity.uses_identifier_scheme, GraphEntity.crossref
        self.assertIn(triple, self.id.g)

    def test_create_viaf(self):
        viaf = "abcdefghi"
        result = self.id.create_viaf(viaf)
        self.assertTrue(result)

        triple = self.id.res, GraphEntity.has_literal_value, Literal(viaf)
        self.assertIn(triple, self.id.g)

        triple = self.id.res, GraphEntity.uses_identifier_scheme, GraphEntity.viaf
        self.assertIn(triple, self.id.g)


if __name__ == '__main__':
    unittest.main()
