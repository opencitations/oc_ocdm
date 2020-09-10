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

from rdflib import URIRef, Literal, XSD, RDF

from oc_graphlib.WIP.resfinder import ResourceFinder
from oc_graphlib.graph_set import GraphSet
from oc_graphlib.prov_entity import ProvEntity
from oc_graphlib.prov_set import ProvSet


class TestProvEntity(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prov_subj_graph_set = GraphSet("http://test/", "context_base", "./info_dir/info_file_", 0, "",
                                           wanted_label=False)

        cls.rf = ResourceFinder(base_dir="./ccc/", base_iri="https://w3id.org/oc/ccc/",
                                tmp_dir="tmp/",
                                context_map={
                                       "https://w3id.org/oc/ccc/context.json": "./context.json"
                                },
                                dir_split=10000,
                                n_file_item=1000,
                                default_dir="/")

        cls.prov_set = ProvSet(prov_subj_graph_set=cls.prov_subj_graph_set, base_iri="http://test/",
                               context_path="context_base", info_dir="./info_dir/info_file_",
                               wanted_label=False, dir_split=10000, n_file_item=1000, supplier_prefix="070",
                               triplestore_url="http://localhost:9999/blazegraph/sparql", default_dir="/",
                               resource_finder=cls.rf)

    def setUp(self):
        self.prov_set.g = []
        self.prov_subj_graph_set.g = []
        self.prov_subject = self.prov_subj_graph_set.add_br(self.__class__.__name__)
        self.se = self.prov_set.add_se(self.__class__.__name__, self.prov_subject)
        self.prev_se = self.prov_set.add_se(self.__class__.__name__, self.prov_subject)

    def test_create_generation_time(self):
        time = "2001-10-26T21:32:52"
        datatype=XSD.dateTime
        result = self.se.create_generation_time(time)
        self.assertTrue(result)

        triple = URIRef(str(self.se)), ProvEntity.generated_at_time, Literal(time, datatype=datatype,
                                                                             normalize=False)
        self.assertIn(triple, self.se.g)

    def test_create_invalidation_time(self):
        time = "2001-10-26T21:32:52"
        datatype=XSD.dateTime
        result = self.se.create_invalidation_time(time)
        self.assertTrue(result)

        triple = URIRef(str(self.se)), ProvEntity.invalidated_at_time, Literal(time, datatype=datatype,
                                                                               normalize=False)
        self.assertIn(triple, self.se.g)

    def test_snapshot_of(self):
        ar = self.prov_set.add_ar(self.__class__.__name__)
        result = self.se.snapshot_of(self.prov_subject)
        self.assertIsNone(result)

        triple = URIRef(str(self.se)), ProvEntity.specialization_of, URIRef(str(self.prov_subject))
        self.assertIn(triple, self.se.g)

    def test_derives_from(self):
        result = self.se.derives_from(self.prev_se)
        self.assertIsNone(result)

        triple = URIRef(str(self.se)), ProvEntity.was_derived_from, URIRef(str(self.prev_se))
        self.assertIn(triple, self.se.g)

    def test_has_primary_source(self):
        primary_source = URIRef("http://test/primarySource")
        result = self.se.has_primary_source(primary_source)
        self.assertIsNone(result)

        triple = URIRef(str(self.se)), ProvEntity.had_primary_source, primary_source
        self.assertIn(triple, self.se.g)

    def test_create_update_query(self):
        update_query = "DELETE {} INSERT {}"
        result = self.se.create_update_query(update_query)
        self.assertTrue(result)

        triple = URIRef(str(self.se)), ProvEntity.has_update_query, Literal(update_query)
        self.assertIn(triple, self.se.g)

    def test_create_description(self):
        description = "Description"
        result = self.se.create_description(description)
        self.assertTrue(result)

        triple = URIRef(str(self.se)), ProvEntity.description, Literal(description)
        self.assertIn(triple, self.se.g)

    def test_has_resp_agent(self):
        ra = URIRef("http://test/ra")
        result = self.se.has_resp_agent(ra)
        self.assertIsNone(result)

        triple = URIRef(str(self.se)), ProvEntity.was_attributed_to, ra
        self.assertIn(triple, self.se.g)

    def test_create_creation_activity(self):
        result = self.se.create_creation_activity()
        self.assertIsNone(result)

        triple = URIRef(str(self.se)), RDF.type, ProvEntity.create
        self.assertIn(triple, self.se.g)

    def test_create_update_activity(self):
        result = self.se.create_update_activity()
        self.assertIsNone(result)

        triple = URIRef(str(self.se)), RDF.type, ProvEntity.modify
        self.assertIn(triple, self.se.g)

    def test_create_merging_activity(self):
        result = self.se.create_merging_activity()
        self.assertIsNone(result)

        triple = URIRef(str(self.se)), RDF.type, ProvEntity.replace
        self.assertIn(triple, self.se.g)


if __name__ == '__main__':
    unittest.main()
