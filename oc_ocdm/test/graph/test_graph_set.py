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

from rdflib import Graph

from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.graph.entities.identifier import Identifier
from oc_ocdm.graph.entities.bibliographic.agent_role import AgentRole
from oc_ocdm.graph.entities.bibliographic.bibliographic_reference import BibliographicReference
from oc_ocdm.graph.entities.bibliographic.bibliographic_resource import BibliographicResource
from oc_ocdm.graph.entities.bibliographic.citation import Citation
from oc_ocdm.graph.entities.bibliographic.discourse_element import DiscourseElement
from oc_ocdm.graph.entities.bibliographic.pointer_list import PointerList
from oc_ocdm.graph.entities.bibliographic.reference_annotation import ReferenceAnnotation
from oc_ocdm.graph.entities.bibliographic.reference_pointer import ReferencePointer
from oc_ocdm.graph.entities.bibliographic.resource_embodiment import ResourceEmbodiment
from oc_ocdm.graph.entities.bibliographic.responsible_agent import ResponsibleAgent


class TestGraphSet(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    def setUp(self):
        self.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def test_get_entity(self):
        ar = self.graph_set.add_ar(self.resp_agent)
        ref = ar.res
        result = self.graph_set.get_entity(ref)
        self.assertIsNotNone(result)
        self.assertIs(result, ar)

    def test_add_an(self):
        an = self.graph_set.add_an(self.resp_agent)

        self.assertIsNotNone(an)
        self.assertIsInstance(an, ReferenceAnnotation)
        self.assertEqual(str(an.g.identifier), self.graph_set.g_an)

    def test_add_ar(self):
        ar = self.graph_set.add_ar(self.resp_agent)

        self.assertIsNotNone(ar)
        self.assertIsInstance(ar, AgentRole)
        self.assertEqual(str(ar.g.identifier), self.graph_set.g_ar)

    def test_add_be(self):
        be = self.graph_set.add_be(self.resp_agent)

        self.assertIsNotNone(be)
        self.assertIsInstance(be, BibliographicReference)
        self.assertEqual(str(be.g.identifier), self.graph_set.g_be)

    def test_add_br(self):
        br = self.graph_set.add_br(self.resp_agent)

        self.assertIsNotNone(br)
        self.assertIsInstance(br, BibliographicResource)
        self.assertEqual(str(br.g.identifier), self.graph_set.g_br)

    def test_add_ci(self):
        ci = self.graph_set.add_ci(self.resp_agent)

        self.assertIsNotNone(ci)
        self.assertIsInstance(ci, Citation)
        self.assertEqual(str(ci.g.identifier), self.graph_set.g_ci)

    def test_add_de(self):
        de = self.graph_set.add_de(self.resp_agent)

        self.assertIsNotNone(de)
        self.assertIsInstance(de, DiscourseElement)
        self.assertEqual(str(de.g.identifier), self.graph_set.g_de)

    def test_add_id(self):
        identifier = self.graph_set.add_id(self.resp_agent)

        self.assertIsNotNone(identifier)
        self.assertIsInstance(identifier, Identifier)
        self.assertEqual(str(identifier.g.identifier), self.graph_set.g_id)

    def test_add_pl(self):
        pl = self.graph_set.add_pl(self.resp_agent)

        self.assertIsNotNone(pl)
        self.assertIsInstance(pl, PointerList)
        self.assertEqual(str(pl.g.identifier), self.graph_set.g_pl)

    def test_add_rp(self):
        rp = self.graph_set.add_rp(self.resp_agent)

        self.assertIsNotNone(rp)
        self.assertIsInstance(rp, ReferencePointer)
        self.assertEqual(str(rp.g.identifier), self.graph_set.g_rp)

    def test_add_ra(self):
        ra = self.graph_set.add_ra(self.resp_agent)

        self.assertIsNotNone(ra)
        self.assertIsInstance(ra, ResponsibleAgent)
        self.assertEqual(str(ra.g.identifier), self.graph_set.g_ra)

    def test_add_re(self):
        re = self.graph_set.add_re(self.resp_agent)

        self.assertIsNotNone(re)
        self.assertIsInstance(re, ResourceEmbodiment)
        self.assertEqual(str(re.g.identifier), self.graph_set.g_re)

    def test_graphs(self):
        count = 10
        for i in range(count):
            self.graph_set.add_ar(self.resp_agent)
        result = self.graph_set.graphs()
        self.assertIsNotNone(result)
        self.assertEqual(len(result), count)
        for graph in result:
            self.assertIsInstance(graph, Graph)

    def test_get_graph_iri(self):
        ar = self.graph_set.add_ar(self.resp_agent)
        iri = str(ar.g.identifier)
        result = GraphSet.get_graph_iri(ar.g)
        self.assertIsNotNone(result)
        self.assertEqual(iri, result)

    def test_get_orphans(self):
        br = self.graph_set.add_br(self.resp_agent)
        ar = self.graph_set.add_ar(self.resp_agent)
        ra = self.graph_set.add_ra(self.resp_agent)

        with self.subTest("subtest 1"):
            orphans = self.graph_set.get_orphans()
            self.assertIsNotNone(orphans)

            orphans_set = {o.res for o in orphans}
            self.assertSetEqual({br.res, ar.res, ra.res}, orphans_set)

        with self.subTest("subtest 2"):
            # Here we link br and ar:
            br.has_contributor(ar)

            orphans = self.graph_set.get_orphans()
            self.assertIsNotNone(orphans)

            orphans_set = {o.res for o in orphans}
            self.assertSetEqual({br.res, ra.res}, orphans_set)

        with self.subTest("subtest 3"):
            # Here we link ar and ra:
            ar.is_held_by(ra)

            orphans = self.graph_set.get_orphans()
            self.assertIsNotNone(orphans)

            orphans_set = {o.res for o in orphans}
            self.assertSetEqual({br.res}, orphans_set)


if __name__ == '__main__':
    unittest.main()
