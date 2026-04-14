#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from rdflib import XSD, URIRef

from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.light_graph import RDFTerm
from oc_ocdm.prov.prov_entity import ProvEntity
from oc_ocdm.prov.prov_set import ProvSet


class TestSnapshotEntity(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)
        cls.prov_set = ProvSet(cls.graph_set, "http://test/", "./info_dir/", False)

    def setUp(self):
        self.prov_subject = self.graph_set.add_br(self.resp_agent)
        self.se = self.prov_set.add_se(self.prov_subject)
        self.prev_se = self.prov_set.add_se(self.prov_subject)

    def test_has_generation_time(self):
        time = "2001-10-26T21:32:52"
        datatype = XSD.dateTime
        result = self.se.has_generation_time(time)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_generated_at_time, RDFTerm("literal", time, str(datatype))
        self.assertIn(triple, self.se.g)

    def test_has_invalidation_time(self):
        time = "2001-10-26T21:32:52"
        datatype = XSD.dateTime
        result = self.se.has_invalidation_time(time)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_invalidated_at_time, RDFTerm("literal", time, str(datatype))
        self.assertIn(triple, self.se.g)

    def test_is_snapshot_of(self):
        ar = self.graph_set.add_ar(self.resp_agent)
        result = self.se.is_snapshot_of(self.prov_subject)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_specialization_of, RDFTerm("uri", str(self.prov_subject.res))
        self.assertIn(triple, self.se.g)

    def test_derives_from(self):
        result = self.se.derives_from(self.prev_se)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_was_derived_from, RDFTerm("uri", str(self.prev_se.res))
        self.assertIn(triple, self.se.g)

    def test_has_primary_source(self):
        primary_source = URIRef("http://test/primarySource")
        result = self.se.has_primary_source(primary_source)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_had_primary_source, RDFTerm("uri", str(primary_source))
        self.assertIn(triple, self.se.g)

    def test_has_update_action(self):
        update_query = "DELETE {} INSERT {}"
        result = self.se.has_update_action(update_query)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_has_update_query, RDFTerm("literal", update_query, str(XSD.string))
        self.assertIn(triple, self.se.g)

    def test_has_description(self):
        description = "Description"
        result = self.se.has_description(description)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_description, RDFTerm("literal", description, str(XSD.string))
        self.assertIn(triple, self.se.g)

    def test_has_resp_agent(self):
        ra = URIRef("http://test/ra")
        result = self.se.has_resp_agent(ra)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_was_attributed_to, RDFTerm("uri", str(ra))
        self.assertIn(triple, self.se.g)


if __name__ == '__main__':
    unittest.main()
