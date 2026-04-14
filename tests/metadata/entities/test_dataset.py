#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from rdflib import XSD, URIRef

from oc_ocdm.light_graph import RDFTerm
from oc_ocdm.metadata.metadata_entity import MetadataEntity
from oc_ocdm.metadata.metadata_set import MetadataSet


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

        triple = self.dataset.res, MetadataEntity.iri_title, RDFTerm("literal", title, str(XSD.string))
        self.assertIn(triple, self.dataset.g)

    def test_has_description(self):
        description = "Resource"
        result = self.dataset.has_description(description)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_description, RDFTerm("literal", description, str(XSD.string))
        self.assertIn(triple, self.dataset.g)

    def test_has_publication_date(self):
        string = "2020-05-25T12:12:00"
        result = self.dataset.has_publication_date(string)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_issued, RDFTerm("literal", string, str(XSD.dateTime))
        self.assertIn(triple, self.dataset.g)

    def test_has_modification_date(self):
        string = "2020-05-25T12:12:00"
        result = self.dataset.has_modification_date(string)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_modified, RDFTerm("literal", string, str(XSD.dateTime))
        self.assertIn(triple, self.dataset.g)

    def test_has_keyword(self):
        keyword = "Resource"
        result = self.dataset.has_keyword(keyword)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_keyword, RDFTerm("literal", keyword, str(XSD.string))
        self.assertIn(triple, self.dataset.g)

    def test_has_subject(self):
        subject = URIRef("http://subject/")
        result = self.dataset.has_subject(subject)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_subject, RDFTerm("uri", str(subject))
        self.assertIn(triple, self.dataset.g)

    def test_has_landing_page(self):
        page = URIRef("http://landing.page/")
        result = self.dataset.has_landing_page(page)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_landing_page, RDFTerm("uri", str(page))
        self.assertIn(triple, self.dataset.g)

    def test_has_sub_dataset(self):
        result = self.dataset.has_sub_dataset(self.sub_dataset)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_subset, RDFTerm("uri", str(self.sub_dataset.res))
        self.assertIn(triple, self.dataset.g)

    def test_has_sparql_endpoint(self):
        endpoint = URIRef("http://sparql/")
        result = self.dataset.has_sparql_endpoint(endpoint)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_sparql_endpoint, RDFTerm("uri", str(endpoint))
        self.assertIn(triple, self.dataset.g)

    def test_has_distribution(self):
        result = self.dataset.has_distribution(self.di)
        self.assertIsNone(result)

        triple = self.dataset.res, MetadataEntity.iri_distribution, RDFTerm("uri", str(self.di.res))
        self.assertIn(triple, self.dataset.g)

    def test_merge_with_title(self):
        ds1 = self.metadata_set.add_dataset("ds1", self.resp_agent)
        ds2 = self.metadata_set.add_dataset("ds2", self.resp_agent)

        title = "Test Dataset"
        ds2.has_title(title)

        ds1.merge(ds2)

        self.assertEqual(ds1.get_title(), title)
        self.assertTrue(ds2.to_be_deleted)

    def test_merge_with_description(self):
        ds1 = self.metadata_set.add_dataset("ds1", self.resp_agent)
        ds2 = self.metadata_set.add_dataset("ds2", self.resp_agent)

        description = "Test description"
        ds2.has_description(description)

        ds1.merge(ds2)

        self.assertEqual(ds1.get_description(), description)

    def test_merge_with_dates(self):
        ds1 = self.metadata_set.add_dataset("ds1", self.resp_agent)
        ds2 = self.metadata_set.add_dataset("ds2", self.resp_agent)

        pub_date = "2020-01-01T00:00:00"
        mod_date = "2020-12-31T23:59:59"
        ds2.has_publication_date(pub_date)
        ds2.has_modification_date(mod_date)

        ds1.merge(ds2)

        self.assertEqual(ds1.get_publication_date(), pub_date)
        self.assertEqual(ds1.get_modification_date(), mod_date)

    def test_merge_with_keywords(self):
        ds1 = self.metadata_set.add_dataset("ds1", self.resp_agent)
        ds2 = self.metadata_set.add_dataset("ds2", self.resp_agent)

        ds2.has_keyword("keyword1")
        ds2.has_keyword("keyword2")

        ds1.merge(ds2)

        keywords = ds1.get_keywords()
        self.assertEqual(len(keywords), 2)

    def test_merge_with_subjects(self):
        ds1 = self.metadata_set.add_dataset("ds1", self.resp_agent)
        ds2 = self.metadata_set.add_dataset("ds2", self.resp_agent)

        subject1 = URIRef("http://subject1/")
        subject2 = URIRef("http://subject2/")
        ds2.has_subject(subject1)
        ds2.has_subject(subject2)

        ds1.merge(ds2)

        subjects = ds1.get_subjects()
        self.assertEqual(len(subjects), 2)

    def test_merge_basic(self):
        ds1 = self.metadata_set.add_dataset("ds1", self.resp_agent)
        ds2 = self.metadata_set.add_dataset("ds2", self.resp_agent)

        title = "Test"
        ds2.has_title(title)

        ds1.merge(ds2)
        self.assertTrue(ds2.to_be_deleted)

    def test_merge_with_sub_datasets(self):
        ds1 = self.metadata_set.add_dataset("ds1", self.resp_agent)
        ds2 = self.metadata_set.add_dataset("ds2", self.resp_agent)
        sub_ds = self.metadata_set.add_dataset("sub", self.resp_agent)

        ds2.has_sub_dataset(sub_ds)

        ds1.merge(ds2)

        sub_datasets = ds1.get_sub_datasets()
        self.assertEqual(len(sub_datasets), 1)

    def test_merge_with_sparql_endpoint(self):
        ds1 = self.metadata_set.add_dataset("ds1", self.resp_agent)
        ds2 = self.metadata_set.add_dataset("ds2", self.resp_agent)

        endpoint = "http://sparql.endpoint/"
        ds2.has_sparql_endpoint(endpoint)

        ds1.merge(ds2)

        self.assertEqual(ds1.get_sparql_endpoint(), endpoint)

    def test_merge_with_distributions(self):
        ds1 = self.metadata_set.add_dataset("ds1", self.resp_agent)
        ds2 = self.metadata_set.add_dataset("ds2", self.resp_agent)
        di = self.metadata_set.add_di("di", self.resp_agent)

        ds2.has_distribution(di)

        ds1.merge(ds2)

        distributions = ds1.get_distributions()
        self.assertEqual(len(distributions), 1)

    def test_get_title(self):
        title = "Test Dataset"
        self.dataset.has_title(title)
        self.assertEqual(self.dataset.get_title(), title)

    def test_get_description(self):
        description = "Test description"
        self.dataset.has_description(description)
        self.assertEqual(self.dataset.get_description(), description)

    def test_get_publication_date(self):
        pub_date = "2020-01-01T00:00:00"
        self.dataset.has_publication_date(pub_date)
        self.assertEqual(self.dataset.get_publication_date(), pub_date)

    def test_get_modification_date(self):
        mod_date = "2020-12-31T23:59:59"
        self.dataset.has_modification_date(mod_date)
        self.assertEqual(self.dataset.get_modification_date(), mod_date)

    def test_get_keywords(self):
        self.dataset.has_keyword("keyword1")
        self.dataset.has_keyword("keyword2")
        keywords = self.dataset.get_keywords()
        self.assertEqual(len(keywords), 2)

    def test_get_subjects(self):
        subject1 = URIRef("http://subject1/")
        subject2 = URIRef("http://subject2/")
        self.dataset.has_subject(subject1)
        self.dataset.has_subject(subject2)
        subjects = self.dataset.get_subjects()
        self.assertEqual(len(subjects), 2)


    def test_get_sub_datasets(self):
        self.dataset.has_sub_dataset(self.sub_dataset)
        sub_datasets = self.dataset.get_sub_datasets()
        self.assertEqual(len(sub_datasets), 1)

    def test_get_sparql_endpoint(self):
        endpoint = "http://sparql.endpoint/"
        self.dataset.has_sparql_endpoint(endpoint)
        self.assertEqual(self.dataset.get_sparql_endpoint(), endpoint)

    def test_get_distributions(self):
        self.dataset.has_distribution(self.di)
        distributions = self.dataset.get_distributions()
        self.assertEqual(len(distributions), 1)


if __name__ == '__main__':
    unittest.main()
