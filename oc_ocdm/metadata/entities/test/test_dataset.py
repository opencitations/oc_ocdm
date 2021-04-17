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


class TestDataset(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.metadata_set = MetadataSet("http://test/", "./info_dir/", False)

    def setUp(self):
        self.dataset = self.metadata_set.add_dataset("ocdmTest", self.resp_agent)
        self.sub_dataset = self.metadata_set.add_dataset("subDataset", self.resp_agent)
        self.di = self.metadata_set.add_di("ocdmTest", self.resp_agent)

    def test_has_title(self):
        title = "Resource"
        result = self.dataset.has_title(title)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_title, Literal(title)
        self.assertIn(triple, self.dataset.g)

    def test_has_description(self):
        description = "Resource"
        result = self.dataset.has_description(description)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_description, Literal(description)
        self.assertIn(triple, self.dataset.g)

    def test_has_publication_date(self):
        string = "2020-05-25T12:12:00"
        result = self.dataset.has_publication_date(string)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_issued, Literal(string, datatype=XSD.dateTime,
                                                                      normalize=False)
        self.assertIn(triple, self.dataset.g)

    def test_has_modification_date(self):
        string = "2020-05-25T12:12:00"
        result = self.dataset.has_modification_date(string)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_modified, Literal(string, datatype=XSD.dateTime,
                                                                        normalize=False)
        self.assertIn(triple, self.dataset.g)

    def test_has_keyword(self):
        keyword = "Resource"
        result = self.dataset.has_keyword(keyword)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_keyword, Literal(keyword)
        self.assertIn(triple, self.dataset.g)

    def test_has_subject(self):
        subject = URIRef("http://subject/")
        result = self.dataset.has_subject(subject)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_subject, subject
        self.assertIn(triple, self.dataset.g)

    def test_has_landing_page(self):
        page = URIRef("http://landing.page/")
        result = self.dataset.has_landing_page(page)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_landing_page, page
        self.assertIn(triple, self.dataset.g)

    def test_has_sub_dataset(self):
        result = self.dataset.has_sub_dataset(self.sub_dataset)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_subset, self.sub_dataset.res
        self.assertIn(triple, self.dataset.g)

    def test_has_sparql_endpoint(self):
        endpoint = URIRef("http://sparql/")
        result = self.dataset.has_sparql_endpoint(endpoint)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_sparql_endpoint, endpoint
        self.assertIn(triple, self.dataset.g)

    def test_has_distribution(self):
        result = self.dataset.has_distribution(self.di)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_distribution, self.di.res
        self.assertIn(triple, self.dataset.g)


if __name__ == '__main__':
    unittest.main()
