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

from rdflib import URIRef, Literal, XSD

from oc_ocdm.metadata.metadata_set import MetadataSet
from oc_ocdm.metadata.metadata_entity import MetadataEntity


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

        triple = self.di.res, MetadataEntity.iri_title, Literal(title)
        self.assertIn(triple, self.di.g)

    def test_has_description(self):
        description = "Resource"
        result = self.di.has_description(description)
        self.assertIsNone(result)

        triple = self.di.res, MetadataEntity.iri_description, Literal(description)
        self.assertIn(triple, self.di.g)

    def test_has_publication_date(self):
        string = "2020-05-25T12:12:00"
        result = self.di.has_publication_date(string)
        self.assertIsNone(result)

        triple = self.di.res, MetadataEntity.iri_issued, Literal(string, datatype=XSD.dateTime,
                                                                 normalize=False)
        self.assertIn(triple, self.di.g)

    def test_has_license(self):
        license = URIRef("http://license/")
        result = self.di.has_license(license)
        self.assertIsNone(result)

        triple = self.di.res, MetadataEntity.iri_license, license
        self.assertIn(triple, self.di.g)

    def test_has_download_url(self):
        download_url = URIRef("http://download.here/")
        result = self.di.has_download_url(download_url)
        self.assertIsNone(result)

        triple = self.di.res, MetadataEntity.iri_download_url, download_url
        self.assertIn(triple, self.di.g)

    def test_has_media_type(self):
        media_type = URIRef("http://media.type/")
        result = self.di.has_media_type(media_type)
        self.assertIsNone(result)

        triple = self.di.res, MetadataEntity.iri_media_type, media_type
        self.assertIn(triple, self.di.g)

    def test_has_byte_size(self):
        byte_size = "1024"
        result = self.di.has_byte_size(byte_size)
        self.assertIsNone(result)

        triple = self.di.res, MetadataEntity.iri_byte_size, Literal(byte_size, datatype=XSD.decimal,
                                                                    normalize=False)
        self.assertIn(triple, self.di.g)


if __name__ == '__main__':
    unittest.main()
