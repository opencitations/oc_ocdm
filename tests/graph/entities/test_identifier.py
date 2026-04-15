#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from oc_ocdm.constants import XSD_STRING
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet
from triplelite import RDFTerm


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

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", orcid, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_orcid)
        self.assertIn(triple, self.identifier.g)

    def test_create_doi(self):
        doi = "abcdefghi"
        result = self.identifier.create_doi(doi)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", doi, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_doi)
        self.assertIn(triple, self.identifier.g)

    def test_create_pmid(self):
        pmid = "abcdefghi"
        result = self.identifier.create_pmid(pmid)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", pmid, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_pmid)
        self.assertIn(triple, self.identifier.g)

    def test_create_pmcid(self):
        pmcid = "abcdefghi"
        result = self.identifier.create_pmcid(pmcid)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", pmcid, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_pmcid)
        self.assertIn(triple, self.identifier.g)

    def test_create_issn(self):
        issn = "abcdefghi"
        result = self.identifier.create_issn(issn)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", issn, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_issn)
        self.assertIn(triple, self.identifier.g)

    def test_create_isbn(self):
        isbn = "abcdefghi"
        result = self.identifier.create_isbn(isbn)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", isbn, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_isbn)
        self.assertIn(triple, self.identifier.g)

    def test_create_url(self):
        url = "abcdefghi"
        result = self.identifier.create_url(url)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", url, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_url)
        self.assertIn(triple, self.identifier.g)

    def test_create_xpath(self):
        xpath = "abcdefghi"
        result = self.identifier.create_xpath(xpath)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", xpath, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_xpath)
        self.assertIn(triple, self.identifier.g)

    def test_create_intrepid(self):
        intrepid = "abcdefghi"
        result = self.identifier.create_intrepid(intrepid)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", intrepid, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_intrepid)
        self.assertIn(triple, self.identifier.g)

    def test_create_xmlid(self):
        xmlid = "abcdefghi"
        result = self.identifier.create_xmlid(xmlid)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", xmlid, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_xmlid)
        self.assertIn(triple, self.identifier.g)

    def test_create_wikidata(self):
        wikidata = "abcdefghi"
        result = self.identifier.create_wikidata(wikidata)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", wikidata, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_wikidata)
        self.assertIn(triple, self.identifier.g)

    def test_create_wikipedia(self):
        wikipedia = "abcdefghi"
        result = self.identifier.create_wikipedia(wikipedia)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", wikipedia, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_wikipedia)
        self.assertIn(triple, self.identifier.g)

    def test_create_crossref(self):
        crossref = "abcdefghi"
        result = self.identifier.create_crossref(crossref)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", crossref, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_crossref)
        self.assertIn(triple, self.identifier.g)

    def test_create_datacite(self):
        datacite = "332"
        result = self.identifier.create_datacite(datacite)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", datacite, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_datacite)
        self.assertIn(triple, self.identifier.g)

    def test_create_viaf(self):
        viaf = "abcdefghi"
        result = self.identifier.create_viaf(viaf)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", viaf, XSD_STRING)
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", GraphEntity.iri_viaf)
        self.assertIn(triple, self.identifier.g)


if __name__ == '__main__':
    unittest.main()
