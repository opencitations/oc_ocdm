#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from rdflib import XSD

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

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", orcid, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_orcid))
        self.assertIn(triple, self.identifier.g)

    def test_create_doi(self):
        doi = "abcdefghi"
        result = self.identifier.create_doi(doi)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", doi, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_doi))
        self.assertIn(triple, self.identifier.g)

    def test_create_pmid(self):
        pmid = "abcdefghi"
        result = self.identifier.create_pmid(pmid)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", pmid, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_pmid))
        self.assertIn(triple, self.identifier.g)

    def test_create_pmcid(self):
        pmcid = "abcdefghi"
        result = self.identifier.create_pmcid(pmcid)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", pmcid, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_pmcid))
        self.assertIn(triple, self.identifier.g)

    def test_create_issn(self):
        issn = "abcdefghi"
        result = self.identifier.create_issn(issn)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", issn, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_issn))
        self.assertIn(triple, self.identifier.g)

    def test_create_isbn(self):
        isbn = "abcdefghi"
        result = self.identifier.create_isbn(isbn)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", isbn, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_isbn))
        self.assertIn(triple, self.identifier.g)

    def test_create_url(self):
        url = "abcdefghi"
        result = self.identifier.create_url(url)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", url, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_url))
        self.assertIn(triple, self.identifier.g)

    def test_create_xpath(self):
        xpath = "abcdefghi"
        result = self.identifier.create_xpath(xpath)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", xpath, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_xpath))
        self.assertIn(triple, self.identifier.g)

    def test_create_intrepid(self):
        intrepid = "abcdefghi"
        result = self.identifier.create_intrepid(intrepid)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", intrepid, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_intrepid))
        self.assertIn(triple, self.identifier.g)

    def test_create_xmlid(self):
        xmlid = "abcdefghi"
        result = self.identifier.create_xmlid(xmlid)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", xmlid, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_xmlid))
        self.assertIn(triple, self.identifier.g)

    def test_create_wikidata(self):
        wikidata = "abcdefghi"
        result = self.identifier.create_wikidata(wikidata)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", wikidata, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_wikidata))
        self.assertIn(triple, self.identifier.g)

    def test_create_wikipedia(self):
        wikipedia = "abcdefghi"
        result = self.identifier.create_wikipedia(wikipedia)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", wikipedia, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_wikipedia))
        self.assertIn(triple, self.identifier.g)

    def test_create_crossref(self):
        crossref = "abcdefghi"
        result = self.identifier.create_crossref(crossref)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", crossref, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_crossref))
        self.assertIn(triple, self.identifier.g)

    def test_create_datacite(self):
        datacite = "332"
        result = self.identifier.create_datacite(datacite)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", datacite, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_datacite))
        self.assertIn(triple, self.identifier.g)

    def test_create_viaf(self):
        viaf = "abcdefghi"
        result = self.identifier.create_viaf(viaf)
        self.assertIsNone(result)

        triple = self.identifier.res, GraphEntity.iri_has_literal_value, RDFTerm("literal", viaf, str(XSD.string))
        self.assertIn(triple, self.identifier.g)

        triple = self.identifier.res, GraphEntity.iri_uses_identifier_scheme, RDFTerm("uri", str(GraphEntity.iri_viaf))
        self.assertIn(triple, self.identifier.g)


if __name__ == '__main__':
    unittest.main()
