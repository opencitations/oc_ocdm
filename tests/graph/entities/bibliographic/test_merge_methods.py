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


class TestBibliographicReferenceMerge(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_merge_with_content(self):
        be1 = self.graph_set.add_be(self.resp_agent)
        be2 = self.graph_set.add_be(self.resp_agent)

        content = "Test content"
        be2.has_content(content)

        be1.merge(be2)

        self.assertEqual(be1.get_content(), content)
        self.assertTrue(be2.to_be_deleted)

    def test_merge_with_annotation(self):
        be1 = self.graph_set.add_be(self.resp_agent)
        be2 = self.graph_set.add_be(self.resp_agent)
        an = self.graph_set.add_an(self.resp_agent)

        be2.has_annotation(an)

        be1.merge(be2)

        annotations = be1.get_annotations()
        self.assertEqual(len(annotations), 1)
        self.assertEqual(annotations[0].res, an.res)

    def test_merge_with_referenced_br(self):
        be1 = self.graph_set.add_be(self.resp_agent)
        be2 = self.graph_set.add_be(self.resp_agent)
        br = self.graph_set.add_br(self.resp_agent)

        be2.references_br(br)

        be1.merge(be2)

        referenced = be1.get_referenced_br()
        self.assertIsNotNone(referenced)
        self.assertEqual(referenced.res, br.res)


class TestReferencePointerMerge(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_merge_with_content(self):
        rp1 = self.graph_set.add_rp(self.resp_agent)
        rp2 = self.graph_set.add_rp(self.resp_agent)

        content = "[1]"
        rp2.has_content(content)

        rp1.merge(rp2)

        self.assertEqual(rp1.get_content(), content)
        self.assertTrue(rp2.to_be_deleted)

    def test_merge_with_next_rp(self):
        rp1 = self.graph_set.add_rp(self.resp_agent)
        rp2 = self.graph_set.add_rp(self.resp_agent)
        rp3 = self.graph_set.add_rp(self.resp_agent)

        rp2.has_next_rp(rp3)

        rp1.merge(rp2)

        next_rp = rp1.get_next_rp()
        self.assertIsNotNone(next_rp)
        self.assertEqual(next_rp.res, rp3.res)

    def test_merge_with_denoted_be(self):
        rp1 = self.graph_set.add_rp(self.resp_agent)
        rp2 = self.graph_set.add_rp(self.resp_agent)
        be = self.graph_set.add_be(self.resp_agent)

        rp2.denotes_be(be)

        rp1.merge(rp2)

        denoted = rp1.get_denoted_be()
        self.assertIsNotNone(denoted)
        self.assertEqual(denoted.res, be.res)

    def test_merge_with_annotations(self):
        rp1 = self.graph_set.add_rp(self.resp_agent)
        rp2 = self.graph_set.add_rp(self.resp_agent)
        an = self.graph_set.add_an(self.resp_agent)

        rp2.has_annotation(an)

        rp1.merge(rp2)

        annotations = rp1.get_annotations()
        self.assertEqual(len(annotations), 1)


class TestPointerListMerge(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_merge_with_contained_elements(self):
        pl1 = self.graph_set.add_pl(self.resp_agent)
        pl2 = self.graph_set.add_pl(self.resp_agent)
        rp = self.graph_set.add_rp(self.resp_agent)

        pl2.contains_element(rp)

        pl1.merge(pl2)

        elements = pl1.get_contained_elements()
        self.assertEqual(len(elements), 1)
        self.assertTrue(pl2.to_be_deleted)


class TestAgentRoleMerge(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_merge_with_next(self):
        ar1 = self.graph_set.add_ar(self.resp_agent)
        ar2 = self.graph_set.add_ar(self.resp_agent)
        ar3 = self.graph_set.add_ar(self.resp_agent)

        ar2.has_next(ar3)

        ar1.merge(ar2)

        next_ar = ar1.get_next()
        self.assertIsNotNone(next_ar)
        self.assertEqual(next_ar.res, ar3.res)

    def test_merge_with_held_by(self):
        ar1 = self.graph_set.add_ar(self.resp_agent)
        ar2 = self.graph_set.add_ar(self.resp_agent)
        ra = self.graph_set.add_ra(self.resp_agent)

        ar2.is_held_by(ra)

        ar1.merge(ar2)

        held_by = ar1.get_is_held_by()
        self.assertIsNotNone(held_by)
        self.assertEqual(held_by.res, ra.res)

    def test_merge_with_publisher_role(self):
        ar1 = self.graph_set.add_ar(self.resp_agent)
        ar2 = self.graph_set.add_ar(self.resp_agent)

        ar2.create_publisher()

        ar1.merge(ar2)

        role_type = ar1.get_role_type()
        self.assertEqual(role_type, GraphEntity.iri_publisher)

    def test_merge_with_author_role(self):
        ar1 = self.graph_set.add_ar(self.resp_agent)
        ar2 = self.graph_set.add_ar(self.resp_agent)

        ar2.create_author()

        ar1.merge(ar2)

        role_type = ar1.get_role_type()
        self.assertEqual(role_type, GraphEntity.iri_author)

    def test_merge_with_editor_role(self):
        ar1 = self.graph_set.add_ar(self.resp_agent)
        ar2 = self.graph_set.add_ar(self.resp_agent)

        ar2.create_editor()

        ar1.merge(ar2)

        role_type = ar1.get_role_type()
        self.assertEqual(role_type, GraphEntity.iri_editor)


class TestResponsibleAgentMerge(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_merge_with_name(self):
        ra1 = self.graph_set.add_ra(self.resp_agent)
        ra2 = self.graph_set.add_ra(self.resp_agent)

        name = "John Doe"
        ra2.has_name(name)

        ra1.merge(ra2)

        self.assertEqual(ra1.get_name(), name)
        self.assertTrue(ra2.to_be_deleted)

    def test_merge_with_given_name(self):
        ra1 = self.graph_set.add_ra(self.resp_agent)
        ra2 = self.graph_set.add_ra(self.resp_agent)

        given_name = "John"
        ra2.has_given_name(given_name)

        ra1.merge(ra2)

        self.assertEqual(ra1.get_given_name(), given_name)

    def test_merge_with_family_name(self):
        ra1 = self.graph_set.add_ra(self.resp_agent)
        ra2 = self.graph_set.add_ra(self.resp_agent)

        family_name = "Doe"
        ra2.has_family_name(family_name)

        ra1.merge(ra2)

        self.assertEqual(ra1.get_family_name(), family_name)


class TestResourceEmbodimentMerge(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_merge_with_starting_page(self):
        re1 = self.graph_set.add_re(self.resp_agent)
        re2 = self.graph_set.add_re(self.resp_agent)

        page = "10"
        re2.has_starting_page(page)

        re1.merge(re2)

        self.assertEqual(re1.get_starting_page(), page)
        self.assertTrue(re2.to_be_deleted)

    def test_merge_with_ending_page(self):
        re1 = self.graph_set.add_re(self.resp_agent)
        re2 = self.graph_set.add_re(self.resp_agent)

        page = "20"
        re2.has_ending_page(page)

        re1.merge(re2)

        self.assertEqual(re1.get_ending_page(), page)


class TestCitationMerge(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_merge_with_citing_entity(self):
        ci1 = self.graph_set.add_ci(self.resp_agent)
        ci2 = self.graph_set.add_ci(self.resp_agent)
        br = self.graph_set.add_br(self.resp_agent)

        ci2.has_citing_entity(br)

        ci1.merge(ci2)

        citing = ci1.get_citing_entity()
        self.assertIsNotNone(citing)
        self.assertEqual(citing.res, br.res)
        self.assertTrue(ci2.to_be_deleted)

    def test_merge_with_cited_entity(self):
        ci1 = self.graph_set.add_ci(self.resp_agent)
        ci2 = self.graph_set.add_ci(self.resp_agent)
        br = self.graph_set.add_br(self.resp_agent)

        ci2.has_cited_entity(br)

        ci1.merge(ci2)

        cited = ci1.get_cited_entity()
        self.assertIsNotNone(cited)
        self.assertEqual(cited.res, br.res)


if __name__ == '__main__':
    unittest.main()
