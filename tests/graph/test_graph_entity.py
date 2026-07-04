#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

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


if __name__ == "__main__":
    unittest.main()
