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

from oc_ocdm.graph.graph_set import GraphSet
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

        triple = self.se.res, ProvEntity.iri_generated_at_time, Literal(time, datatype=datatype,
                                                                        normalize=False)
        self.assertIn(triple, self.se.g)

    def test_has_invalidation_time(self):
        time = "2001-10-26T21:32:52"
        datatype = XSD.dateTime
        result = self.se.has_invalidation_time(time)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_invalidated_at_time, Literal(time, datatype=datatype,
                                                                          normalize=False)
        self.assertIn(triple, self.se.g)

    def test_is_snapshot_of(self):
        ar = self.graph_set.add_ar(self.resp_agent)
        result = self.se.is_snapshot_of(self.prov_subject)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_specialization_of, self.prov_subject.res
        self.assertIn(triple, self.se.g)

    def test_derives_from(self):
        result = self.se.derives_from(self.prev_se)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_was_derived_from, self.prev_se.res
        self.assertIn(triple, self.se.g)

    def test_has_primary_source(self):
        primary_source = URIRef("http://test/primarySource")
        result = self.se.has_primary_source(primary_source)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_had_primary_source, primary_source
        self.assertIn(triple, self.se.g)

    def test_has_update_action(self):
        update_query = "DELETE {} INSERT {}"
        result = self.se.has_update_action(update_query)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_has_update_query, Literal(update_query)
        self.assertIn(triple, self.se.g)

    def test_has_description(self):
        description = "Description"
        result = self.se.has_description(description)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_description, Literal(description)
        self.assertIn(triple, self.se.g)

    def test_has_resp_agent(self):
        ra = URIRef("http://test/ra")
        result = self.se.has_resp_agent(ra)
        self.assertIsNone(result)

        triple = self.se.res, ProvEntity.iri_was_attributed_to, ra
        self.assertIn(triple, self.se.g)


if __name__ == '__main__':
    unittest.main()
