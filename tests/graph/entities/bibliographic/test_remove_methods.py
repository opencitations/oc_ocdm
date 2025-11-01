#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Arcangelo Massari <arcangelo.massari@unibo.it>
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

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet


class TestBibliographicReferenceRemovers(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_remove_annotation_specific(self):
        be = self.graph_set.add_be(self.resp_agent)
        an1 = self.graph_set.add_an(self.resp_agent)
        an2 = self.graph_set.add_an(self.resp_agent)

        be.has_annotation(an1)
        be.has_annotation(an2)

        be.remove_annotation(an1)

        result = be.get_annotations()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].res, an2.res)

    def test_remove_annotation_all(self):
        be = self.graph_set.add_be(self.resp_agent)
        an1 = self.graph_set.add_an(self.resp_agent)
        an2 = self.graph_set.add_an(self.resp_agent)

        be.has_annotation(an1)
        be.has_annotation(an2)

        be.remove_annotation()

        result = be.get_annotations()
        self.assertEqual(len(result), 0)


class TestReferencePointerRemovers(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_remove_annotation_specific(self):
        rp = self.graph_set.add_rp(self.resp_agent)
        an1 = self.graph_set.add_an(self.resp_agent)
        an2 = self.graph_set.add_an(self.resp_agent)

        rp.has_annotation(an1)
        rp.has_annotation(an2)

        rp.remove_annotation(an1)

        result = rp.get_annotations()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].res, an2.res)

    def test_remove_annotation_all(self):
        rp = self.graph_set.add_rp(self.resp_agent)
        an1 = self.graph_set.add_an(self.resp_agent)
        an2 = self.graph_set.add_an(self.resp_agent)

        rp.has_annotation(an1)
        rp.has_annotation(an2)

        rp.remove_annotation()

        result = rp.get_annotations()
        self.assertEqual(len(result), 0)


class TestPointerListRemovers(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_remove_contained_element_specific(self):
        pl = self.graph_set.add_pl(self.resp_agent)
        rp1 = self.graph_set.add_rp(self.resp_agent)
        rp2 = self.graph_set.add_rp(self.resp_agent)

        pl.contains_element(rp1)
        pl.contains_element(rp2)

        pl.remove_contained_element(rp1)

        result = pl.get_contained_elements()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].res, rp2.res)

    def test_remove_contained_element_all(self):
        pl = self.graph_set.add_pl(self.resp_agent)
        rp1 = self.graph_set.add_rp(self.resp_agent)
        rp2 = self.graph_set.add_rp(self.resp_agent)

        pl.contains_element(rp1)
        pl.contains_element(rp2)

        pl.remove_contained_element()

        result = pl.get_contained_elements()
        self.assertEqual(len(result), 0)


class TestDiscourseElementRemovers(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_remove_contained_discourse_element_specific(self):
        de1 = self.graph_set.add_de(self.resp_agent)
        de2 = self.graph_set.add_de(self.resp_agent)
        de3 = self.graph_set.add_de(self.resp_agent)

        de1.contains_discourse_element(de2)
        de1.contains_discourse_element(de3)

        de1.remove_contained_discourse_element(de2)

        result = de1.get_contained_discourse_elements()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].res, de3.res)

    def test_remove_contained_discourse_element_all(self):
        de1 = self.graph_set.add_de(self.resp_agent)
        de2 = self.graph_set.add_de(self.resp_agent)
        de3 = self.graph_set.add_de(self.resp_agent)

        de1.contains_discourse_element(de2)
        de1.contains_discourse_element(de3)

        de1.remove_contained_discourse_element()

        result = de1.get_contained_discourse_elements()
        self.assertEqual(len(result), 0)

    def test_remove_is_context_of_rp_specific(self):
        de = self.graph_set.add_de(self.resp_agent)
        rp1 = self.graph_set.add_rp(self.resp_agent)
        rp2 = self.graph_set.add_rp(self.resp_agent)

        de.is_context_of_rp(rp1)
        de.is_context_of_rp(rp2)

        de.remove_is_context_of_rp(rp1)

        result = de.get_is_context_of_rp()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].res, rp2.res)

    def test_remove_is_context_of_rp_all(self):
        de = self.graph_set.add_de(self.resp_agent)
        rp1 = self.graph_set.add_rp(self.resp_agent)
        rp2 = self.graph_set.add_rp(self.resp_agent)

        de.is_context_of_rp(rp1)
        de.is_context_of_rp(rp2)

        de.remove_is_context_of_rp()

        result = de.get_is_context_of_rp()
        self.assertEqual(len(result), 0)

    def test_remove_is_context_of_pl_specific(self):
        de = self.graph_set.add_de(self.resp_agent)
        pl1 = self.graph_set.add_pl(self.resp_agent)
        pl2 = self.graph_set.add_pl(self.resp_agent)

        de.is_context_of_pl(pl1)
        de.is_context_of_pl(pl2)

        de.remove_is_context_of_pl(pl1)

        result = de.get_is_context_of_pl()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].res, pl2.res)

    def test_remove_is_context_of_pl_all(self):
        de = self.graph_set.add_de(self.resp_agent)
        pl1 = self.graph_set.add_pl(self.resp_agent)
        pl2 = self.graph_set.add_pl(self.resp_agent)

        de.is_context_of_pl(pl1)
        de.is_context_of_pl(pl2)

        de.remove_is_context_of_pl()

        result = de.get_is_context_of_pl()
        self.assertEqual(len(result), 0)

    def test_remove_number(self):
        de = self.graph_set.add_de(self.resp_agent)
        number = "1"
        de.has_number(number)

        de.remove_number()

        result = de.get_number()
        self.assertIsNone(result)

    def test_remove_content(self):
        de = self.graph_set.add_de(self.resp_agent)
        content = "Section content"
        de.has_content(content)

        de.remove_content()

        result = de.get_content()
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
