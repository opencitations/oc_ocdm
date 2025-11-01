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
from oc_ocdm.metadata.metadata_set import MetadataSet
from oc_ocdm.prov.prov_set import ProvSet
from rdflib import URIRef


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


class TestCitationRemovers(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_remove_citing_entity(self):
        ci = self.graph_set.add_ci(self.resp_agent)
        br = self.graph_set.add_br(self.resp_agent)

        ci.has_citing_entity(br)

        ci.remove_citing_entity()

        result = ci.get_citing_entity()
        self.assertIsNone(result)

    def test_remove_cited_entity(self):
        ci = self.graph_set.add_ci(self.resp_agent)
        br = self.graph_set.add_br(self.resp_agent)

        ci.has_cited_entity(br)
        ci.remove_cited_entity()

        result = ci.get_cited_entity()
        self.assertIsNone(result)


class TestResponsibleAgentRemovers(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_remove_name(self):
        ra = self.graph_set.add_ra(self.resp_agent)
        ra.has_name("John Doe")

        ra.remove_name()

        result = ra.get_name()
        self.assertIsNone(result)

    def test_remove_given_name(self):
        ra = self.graph_set.add_ra(self.resp_agent)
        ra.has_given_name("John")

        ra.remove_given_name()

        result = ra.get_given_name()
        self.assertIsNone(result)

    def test_remove_family_name(self):
        ra = self.graph_set.add_ra(self.resp_agent)
        ra.has_family_name("Doe")

        ra.remove_family_name()

        result = ra.get_family_name()
        self.assertIsNone(result)


class TestMetadataRemovers(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.metadata_set = MetadataSet("http://test/metadata/", "./info_dir/", "")

    def test_remove_dataset_title(self):
        ds = self.metadata_set.add_dataset("test_dataset", self.resp_agent)
        ds.has_title("Test Dataset")

        ds.remove_title()

        result = ds.get_title()
        self.assertIsNone(result)

    def test_remove_dataset_description(self):
        ds = self.metadata_set.add_dataset("test_dataset2", self.resp_agent)
        ds.has_description("Test description")

        ds.remove_description()

        result = ds.get_description()
        self.assertIsNone(result)

    def test_remove_dataset_publication_date(self):
        ds = self.metadata_set.add_dataset("test_dataset3", self.resp_agent)
        ds.has_publication_date("2025-01-01")

        ds.remove_publication_date()

        result = ds.get_publication_date()
        self.assertIsNone(result)

    def test_remove_dataset_modification_date(self):
        ds = self.metadata_set.add_dataset("test_dataset4", self.resp_agent)
        ds.has_modification_date("2025-01-01")

        ds.remove_modification_date()

        result = ds.get_modification_date()
        self.assertIsNone(result)

    def test_remove_dataset_keyword(self):
        ds = self.metadata_set.add_dataset("test_dataset5", self.resp_agent)
        ds.has_keyword("test")
        ds.has_keyword("data")

        # Remove all keywords
        ds.remove_keyword()

        result = ds.get_keywords()
        self.assertEqual(len(result), 0)

    def test_remove_dataset_subject(self):
        ds = self.metadata_set.add_dataset("test_dataset6", self.resp_agent)
        subject = URIRef("http://example.org/subject1")
        ds.has_subject(subject)

        ds.remove_subject()

        result = ds.get_subjects()
        self.assertEqual(len(result), 0)

    def test_remove_dataset_landing_page(self):
        ds = self.metadata_set.add_dataset("test_dataset7", self.resp_agent)
        ds.has_landing_page(URIRef("http://example.org/landing"))

        ds.remove_landing_page()

        result = ds.get_landing_page()
        self.assertIsNone(result)

    def test_remove_distribution_title(self):
        di = self.metadata_set.add_di("test_dist", self.resp_agent)
        di.has_title("Distribution Title")

        di.remove_title()

        result = di.get_title()
        self.assertIsNone(result)

    def test_remove_distribution_description(self):
        di = self.metadata_set.add_di("test_dist2", self.resp_agent)
        di.has_description("Distribution description")

        di.remove_description()

        result = di.get_description()
        self.assertIsNone(result)

    def test_remove_distribution_license(self):
        di = self.metadata_set.add_di("test_dist3", self.resp_agent)
        di.has_license(URIRef("http://creativecommons.org/licenses/by/4.0/"))

        di.remove_license()

        result = di.get_license()
        self.assertIsNone(result)


class TestProvRemovers(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)
        cls.prov_set = ProvSet(cls.graph_set, "http://test/", "./info_dir/")

    def test_remove_description(self):
        br = self.graph_set.add_br(self.resp_agent)
        self.prov_set.generate_provenance()

        # Get the snapshot entity
        se = list(self.prov_set.res_to_entity.values())[0]

        # Check description exists
        desc = se.get_description()
        self.assertIsNotNone(desc)

        # Remove description
        se.remove_description()

        # Check description is removed
        desc = se.get_description()
        self.assertIsNone(desc)

    def test_remove_update_action(self):
        br = self.graph_set.add_br(self.resp_agent)
        self.prov_set.generate_provenance()

        se = list(self.prov_set.res_to_entity.values())[0]
        se.has_update_action("UPDATE")

        se.remove_update_action()

        result = se.get_update_action()
        self.assertIsNone(result)

    def test_remove_invalidation_time(self):
        br = self.graph_set.add_br(self.resp_agent)
        self.prov_set.generate_provenance()

        se = list(self.prov_set.res_to_entity.values())[0]
        se.has_invalidation_time("2025-01-01T00:00:00Z")

        se.remove_invalidation_time()

        result = se.get_invalidation_time()
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
