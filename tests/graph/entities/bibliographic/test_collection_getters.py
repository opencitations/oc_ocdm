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

from oc_ocdm.graph.graph_set import GraphSet


class TestBibliographicReferenceGetters(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_get_content(self):
        be = self.graph_set.add_be(self.resp_agent)
        content = "Test content"
        be.has_content(content)

        result = be.get_content()
        self.assertEqual(result, content)

    def test_get_content_empty(self):
        be = self.graph_set.add_be(self.resp_agent)
        result = be.get_content()
        self.assertIsNone(result)

    def test_get_annotations(self):
        be = self.graph_set.add_be(self.resp_agent)
        an1 = self.graph_set.add_an(self.resp_agent)
        an2 = self.graph_set.add_an(self.resp_agent)

        be.has_annotation(an1)
        be.has_annotation(an2)

        result = be.get_annotations()
        self.assertEqual(len(result), 2)

    def test_get_annotations_empty(self):
        be = self.graph_set.add_be(self.resp_agent)
        result = be.get_annotations()
        self.assertEqual(len(result), 0)

    def test_get_referenced_br(self):
        be = self.graph_set.add_be(self.resp_agent)
        br = self.graph_set.add_br(self.resp_agent)

        be.references_br(br)

        result = be.get_referenced_br()
        self.assertIsNotNone(result)
        self.assertEqual(result.res, br.res)

    def test_get_referenced_br_empty(self):
        be = self.graph_set.add_be(self.resp_agent)
        result = be.get_referenced_br()
        self.assertIsNone(result)


class TestReferencePointerGetters(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_get_content(self):
        rp = self.graph_set.add_rp(self.resp_agent)
        content = "[1]"
        rp.has_content(content)

        result = rp.get_content()
        self.assertEqual(result, content)

    def test_get_next_rp(self):
        rp1 = self.graph_set.add_rp(self.resp_agent)
        rp2 = self.graph_set.add_rp(self.resp_agent)

        rp1.has_next_rp(rp2)

        result = rp1.get_next_rp()
        self.assertIsNotNone(result)
        self.assertEqual(result.res, rp2.res)

    def test_get_next_rp_empty(self):
        rp = self.graph_set.add_rp(self.resp_agent)
        result = rp.get_next_rp()
        self.assertIsNone(result)

    def test_get_denoted_be(self):
        rp = self.graph_set.add_rp(self.resp_agent)
        be = self.graph_set.add_be(self.resp_agent)

        rp.denotes_be(be)

        result = rp.get_denoted_be()
        self.assertIsNotNone(result)
        self.assertEqual(result.res, be.res)

    def test_get_denoted_be_empty(self):
        rp = self.graph_set.add_rp(self.resp_agent)
        result = rp.get_denoted_be()
        self.assertIsNone(result)

    def test_get_annotations(self):
        rp = self.graph_set.add_rp(self.resp_agent)
        an1 = self.graph_set.add_an(self.resp_agent)
        an2 = self.graph_set.add_an(self.resp_agent)

        rp.has_annotation(an1)
        rp.has_annotation(an2)

        result = rp.get_annotations()
        self.assertEqual(len(result), 2)


class TestPointerListGetters(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_get_contained_elements(self):
        pl = self.graph_set.add_pl(self.resp_agent)
        rp1 = self.graph_set.add_rp(self.resp_agent)
        rp2 = self.graph_set.add_rp(self.resp_agent)

        pl.contains_element(rp1)
        pl.contains_element(rp2)

        result = pl.get_contained_elements()
        self.assertEqual(len(result), 2)

    def test_get_contained_elements_empty(self):
        pl = self.graph_set.add_pl(self.resp_agent)
        result = pl.get_contained_elements()
        self.assertEqual(len(result), 0)


class TestDiscourseElementGetters(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_get_title(self):
        de = self.graph_set.add_de(self.resp_agent)
        title = "Introduction"
        de.has_title(title)

        result = de.get_title()
        self.assertEqual(result, title)

    def test_get_content(self):
        de = self.graph_set.add_de(self.resp_agent)
        content = "Section content"
        de.has_content(content)

        result = de.get_content()
        self.assertEqual(result, content)

    def test_get_number(self):
        de = self.graph_set.add_de(self.resp_agent)
        number = "1"
        de.has_number(number)

        result = de.get_number()
        self.assertEqual(result, number)

    def test_get_contained_discourse_elements(self):
        de1 = self.graph_set.add_de(self.resp_agent)
        de2 = self.graph_set.add_de(self.resp_agent)
        de3 = self.graph_set.add_de(self.resp_agent)

        de1.contains_discourse_element(de2)
        de1.contains_discourse_element(de3)

        result = de1.get_contained_discourse_elements()
        self.assertEqual(len(result), 2)

    def test_get_contained_discourse_elements_empty(self):
        de = self.graph_set.add_de(self.resp_agent)
        result = de.get_contained_discourse_elements()
        self.assertEqual(len(result), 0)

    def test_get_next_de(self):
        de1 = self.graph_set.add_de(self.resp_agent)
        de2 = self.graph_set.add_de(self.resp_agent)

        de1.has_next_de(de2)

        result = de1.get_next_de()
        self.assertIsNotNone(result)
        self.assertEqual(result.res, de2.res)

    def test_get_next_de_empty(self):
        de = self.graph_set.add_de(self.resp_agent)
        result = de.get_next_de()
        self.assertIsNone(result)

    def test_get_is_context_of_rp(self):
        de = self.graph_set.add_de(self.resp_agent)
        rp1 = self.graph_set.add_rp(self.resp_agent)
        rp2 = self.graph_set.add_rp(self.resp_agent)

        de.is_context_of_rp(rp1)
        de.is_context_of_rp(rp2)

        result = de.get_is_context_of_rp()
        self.assertEqual(len(result), 2)

    def test_get_is_context_of_rp_empty(self):
        de = self.graph_set.add_de(self.resp_agent)
        result = de.get_is_context_of_rp()
        self.assertEqual(len(result), 0)

    def test_get_is_context_of_pl(self):
        de = self.graph_set.add_de(self.resp_agent)
        pl1 = self.graph_set.add_pl(self.resp_agent)
        pl2 = self.graph_set.add_pl(self.resp_agent)

        de.is_context_of_pl(pl1)
        de.is_context_of_pl(pl2)

        result = de.get_is_context_of_pl()
        self.assertEqual(len(result), 2)

    def test_get_is_context_of_pl_empty(self):
        de = self.graph_set.add_de(self.resp_agent)
        result = de.get_is_context_of_pl()
        self.assertEqual(len(result), 0)


class TestResponsibleAgentGetters(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_get_name(self):
        ra = self.graph_set.add_ra(self.resp_agent)
        name = "John Doe"
        ra.has_name(name)

        result = ra.get_name()
        self.assertEqual(result, name)

    def test_get_given_name(self):
        ra = self.graph_set.add_ra(self.resp_agent)
        given_name = "John"
        ra.has_given_name(given_name)

        result = ra.get_given_name()
        self.assertEqual(result, given_name)

    def test_get_family_name(self):
        ra = self.graph_set.add_ra(self.resp_agent)
        family_name = "Doe"
        ra.has_family_name(family_name)

        result = ra.get_family_name()
        self.assertEqual(result, family_name)


class TestResourceEmbodimentGetters(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_get_starting_page(self):
        re = self.graph_set.add_re(self.resp_agent)
        page = "10"
        re.has_starting_page(page)

        result = re.get_starting_page()
        self.assertEqual(result, page)

    def test_get_ending_page(self):
        re = self.graph_set.add_re(self.resp_agent)
        page = "20"
        re.has_ending_page(page)

        result = re.get_ending_page()
        self.assertEqual(result, page)


class TestCitationGetters(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_get_citing_entity(self):
        ci = self.graph_set.add_ci(self.resp_agent)
        br = self.graph_set.add_br(self.resp_agent)

        ci.has_citing_entity(br)

        result = ci.get_citing_entity()
        self.assertIsNotNone(result)
        self.assertEqual(result.res, br.res)

    def test_get_cited_entity(self):
        ci = self.graph_set.add_ci(self.resp_agent)
        br = self.graph_set.add_br(self.resp_agent)

        ci.has_cited_entity(br)

        result = ci.get_cited_entity()
        self.assertIsNotNone(result)
        self.assertEqual(result.res, br.res)


if __name__ == '__main__':
    unittest.main()
