#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from triplelite import RDFTerm

from oc_ocdm.graph.graph_set import GraphSet


class TestGraphEntity(unittest.TestCase):
    resp_agent = "http://resp_agent.test/"

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_merge_prefer_self_keeps_label(self):
        br1 = self.graph_set.add_br(self.resp_agent)
        br2 = self.graph_set.add_br(self.resp_agent)

        br1.create_label("self label")
        br2.create_label("other label")

        br1.merge(br2, prefer_self=True)

        self.assertEqual(br1.get_label(), "self label")

    def test_merge_prefer_self_fills_missing_label(self):
        br1 = self.graph_set.add_br(self.resp_agent)
        br2 = self.graph_set.add_br(self.resp_agent)

        br2.create_label("other label")

        br1.merge(br2, prefer_self=True)

        self.assertEqual(br1.get_label(), "other label")

    def test_merge_redirects_references_from_every_graph_set_entity_by_default(self):
        graph_set = GraphSet("http://test/")
        surviving_identifier = graph_set.add_id(self.resp_agent)
        merged_identifier = graph_set.add_id(self.resp_agent)
        first_source = graph_set.add_br(self.resp_agent)
        second_source = graph_set.add_ra(self.resp_agent)
        predicate = "http://example.org/refersTo"
        merged_term = RDFTerm("uri", str(merged_identifier.res))
        surviving_term = RDFTerm("uri", str(surviving_identifier.res))
        first_source.g.add((first_source.res, predicate, merged_term))
        second_source.g.add((second_source.res, predicate, merged_term))

        surviving_identifier.merge(merged_identifier)

        self.assertEqual(set(first_source.g.objects(first_source.res, predicate)), {surviving_term})
        self.assertEqual(set(second_source.g.objects(second_source.res, predicate)), {surviving_term})
        self.assertTrue(merged_identifier.to_be_deleted)

    def test_merge_redirects_references_only_from_supplied_sources(self):
        graph_set = GraphSet("http://test/")
        surviving_identifier = graph_set.add_id(self.resp_agent)
        merged_identifier = graph_set.add_id(self.resp_agent)
        supplied_source = graph_set.add_br(self.resp_agent)
        excluded_source = graph_set.add_ra(self.resp_agent)
        predicate = "http://example.org/refersTo"
        merged_term = RDFTerm("uri", str(merged_identifier.res))
        surviving_term = RDFTerm("uri", str(surviving_identifier.res))
        supplied_source.g.add((supplied_source.res, predicate, merged_term))
        excluded_source.g.add((excluded_source.res, predicate, merged_term))

        surviving_identifier.merge(merged_identifier, reference_sources=[supplied_source])

        self.assertEqual(set(supplied_source.g.objects(supplied_source.res, predicate)), {surviving_term})
        self.assertEqual(set(excluded_source.g.objects(excluded_source.res, predicate)), {merged_term})
        self.assertTrue(merged_identifier.to_be_deleted)

    def test_merge_preserves_reference_cleanup_across_different_graph_sets(self):
        surviving_graph_set = GraphSet("http://surviving/")
        merged_graph_set = GraphSet("http://merged/")
        surviving_identifier = surviving_graph_set.add_id(self.resp_agent)
        merged_identifier = merged_graph_set.add_id(self.resp_agent)
        surviving_source = surviving_graph_set.add_br(self.resp_agent)
        merged_source = merged_graph_set.add_br(self.resp_agent)
        predicate = "http://example.org/refersTo"
        merged_term = RDFTerm("uri", str(merged_identifier.res))
        surviving_term = RDFTerm("uri", str(surviving_identifier.res))
        surviving_source.g.add((surviving_source.res, predicate, merged_term))
        merged_source.g.add((merged_source.res, predicate, merged_term))

        surviving_identifier.merge(merged_identifier)

        self.assertEqual(set(surviving_source.g.objects(surviving_source.res, predicate)), {surviving_term})
        self.assertEqual(set(merged_source.g.objects(merged_source.res, predicate)), set())
        self.assertTrue(merged_identifier.to_be_deleted)


if __name__ == "__main__":
    unittest.main()
