#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from rdflib import URIRef
from triplelite import RDFTerm

from oc_ocdm.constants import XSD_DATETIME, XSD_DECIMAL, XSD_STRING
from oc_ocdm.metadata.metadata_entity import MetadataEntity
from oc_ocdm.metadata.metadata_set import MetadataSet


class TestBibliographicResource(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.metadata_set = MetadataSet("http://test/", "./info_dir/", False)

    def setUp(self):
        self.di = self.metadata_set.add_di("ocdmTest", self.resp_agent)

    def test_has_title(self):
        title = "Resource"
        result = self.di.has_title(title)
        self.assertIsNone(result)

        triple = self.di.res, MetadataEntity.iri_title, RDFTerm("literal", title, XSD_STRING)
        self.assertIn(triple, self.di.g)

    def test_has_description(self):
        description = "Resource"
        result = self.di.has_description(description)
        self.assertIsNone(result)

        triple = self.di.res, MetadataEntity.iri_description, RDFTerm("literal", description, XSD_STRING)
        self.assertIn(triple, self.di.g)

    def test_has_publication_date(self):
        string = "2020-05-25T12:12:00"
        result = self.di.has_publication_date(string)
        self.assertIsNone(result)

        triple = self.di.res, MetadataEntity.iri_issued, RDFTerm("literal", string, XSD_DATETIME)
        self.assertIn(triple, self.di.g)

    def test_has_license(self):
        license = URIRef("http://license/")
        result = self.di.has_license(license)
        self.assertIsNone(result)

        triple = self.di.res, MetadataEntity.iri_license, RDFTerm("uri", str(license))
        self.assertIn(triple, self.di.g)

    def test_has_download_url(self):
        download_url = URIRef("http://download.here/")
        result = self.di.has_download_url(download_url)
        self.assertIsNone(result)

        triple = self.di.res, MetadataEntity.iri_download_url, RDFTerm("uri", str(download_url))
        self.assertIn(triple, self.di.g)

    def test_has_media_type(self):
        media_type = URIRef("http://media.type/")
        result = self.di.has_media_type(media_type)
        self.assertIsNone(result)

        triple = self.di.res, MetadataEntity.iri_media_type, RDFTerm("uri", str(media_type))
        self.assertIn(triple, self.di.g)

    def test_has_byte_size(self):
        byte_size = "1024"
        result = self.di.has_byte_size(byte_size)
        self.assertIsNone(result)

        triple = self.di.res, MetadataEntity.iri_byte_size, RDFTerm("literal", byte_size, XSD_DECIMAL)
        self.assertIn(triple, self.di.g)

    def test_merge_with_title(self):
        di1 = self.metadata_set.add_di("di1", self.resp_agent)
        di2 = self.metadata_set.add_di("di2", self.resp_agent)

        title = "Test Distribution"
        di2.has_title(title)

        di1.merge(di2)

        self.assertEqual(di1.get_title(), title)
        self.assertTrue(di2.to_be_deleted)

    def test_merge_with_description(self):
        di1 = self.metadata_set.add_di("di1", self.resp_agent)
        di2 = self.metadata_set.add_di("di2", self.resp_agent)

        description = "Test description"
        di2.has_description(description)

        di1.merge(di2)

        self.assertEqual(di1.get_description(), description)

    def test_merge_with_publication_date(self):
        di1 = self.metadata_set.add_di("di1", self.resp_agent)
        di2 = self.metadata_set.add_di("di2", self.resp_agent)

        pub_date = "2020-01-01T00:00:00"
        di2.has_publication_date(pub_date)

        di1.merge(di2)

        self.assertEqual(di1.get_publication_date(), pub_date)

    def test_merge_with_byte_size(self):
        di1 = self.metadata_set.add_di("di1", self.resp_agent)
        di2 = self.metadata_set.add_di("di2", self.resp_agent)

        byte_size = "2048"
        di2.has_byte_size(byte_size)

        di1.merge(di2)

        self.assertEqual(di1.get_byte_size(), byte_size)

    def test_merge_basic(self):
        di1 = self.metadata_set.add_di("di1", self.resp_agent)
        di2 = self.metadata_set.add_di("di2", self.resp_agent)

        title = "Test"
        di2.has_title(title)

        di1.merge(di2)
        self.assertTrue(di2.to_be_deleted)

    def test_get_title(self):
        title = "Test Distribution"
        self.di.has_title(title)
        self.assertEqual(self.di.get_title(), title)

    def test_get_description(self):
        description = "Test description"
        self.di.has_description(description)
        self.assertEqual(self.di.get_description(), description)

    def test_get_publication_date(self):
        pub_date = "2020-01-01T00:00:00"
        self.di.has_publication_date(pub_date)
        self.assertEqual(self.di.get_publication_date(), pub_date)

    def test_get_byte_size(self):
        byte_size = "2048"
        self.di.has_byte_size(byte_size)
        self.assertEqual(self.di.get_byte_size(), byte_size)


if __name__ == '__main__':
    unittest.main()
