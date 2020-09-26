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

from rdflib import URIRef, Graph

from oc_ocdm.entities.bibliographic.agent_role import AgentRole
from oc_ocdm.entities.bibliographic.bibliographic_reference import BibliographicReference
from oc_ocdm.entities.bibliographic.bibliographic_resource import BibliographicResource
from oc_ocdm.entities.bibliographic.citation import Citation
from oc_ocdm.entities.bibliographic.discourse_element import DiscourseElement
from oc_ocdm.graph_set import GraphSet
from oc_ocdm.entities.identifier import Identifier
from oc_ocdm.entities.bibliographic.pointer_list import PointerList
from oc_ocdm.entities.bibliographic.reference_annotation import ReferenceAnnotation
from oc_ocdm.entities.bibliographic.reference_pointer import ReferencePointer
from oc_ocdm.entities.bibliographic.resource_embodiment import ResourceEmbodiment
from oc_ocdm.entities.bibliographic.responsible_agent import ResponsibleAgent


class TestGraphSet(unittest.TestCase):

    def setUp(self):
        self.graph_set = GraphSet("http://test/", "context_base", "./info_dir/info_file_", 0, "", wanted_label=False)

    def test_res_count(self):
        count = 10
        for i in range(count):
            self.graph_set.add_ar(self.__class__.__name__)
        result = self.graph_set.res_count()
        self.assertIsNotNone(result)
        self.assertEqual(result, count)
        self.assertEqual(result, self.graph_set.r_count)

    def test_get_entity(self):
        ar = self.graph_set.add_ar(self.__class__.__name__)
        ref = URIRef(str(ar))
        result = self.graph_set.get_entity(ref)
        self.assertIsNotNone(result)
        self.assertIs(result, ar)

    def test_add_an(self):
        count1 = self.graph_set.r_count
        an = self.graph_set.add_an(self.__class__.__name__)
        count2 = self.graph_set.r_count

        self.assertIsNotNone(an)
        self.assertEqual(count2, count1+1)
        self.assertIsInstance(an, ReferenceAnnotation)
        self.assertEqual(str(an.g.identifier), self.graph_set.g_an)

    def test_add_ar(self):
        count1 = self.graph_set.r_count
        ar = self.graph_set.add_ar(self.__class__.__name__)
        count2 = self.graph_set.r_count

        self.assertIsNotNone(ar)
        self.assertEqual(count2, count1 + 1)
        self.assertIsInstance(ar, AgentRole)
        self.assertEqual(str(ar.g.identifier), self.graph_set.g_ar)

    def test_add_be(self):
        count1 = self.graph_set.r_count
        be = self.graph_set.add_be(self.__class__.__name__)
        count2 = self.graph_set.r_count

        self.assertIsNotNone(be)
        self.assertEqual(count2, count1 + 1)
        self.assertIsInstance(be, BibliographicReference)
        self.assertEqual(str(be.g.identifier), self.graph_set.g_be)

    def test_add_br(self):
        count1 = self.graph_set.r_count
        br = self.graph_set.add_br(self.__class__.__name__)
        count2 = self.graph_set.r_count

        self.assertIsNotNone(br)
        self.assertEqual(count2, count1 + 1)
        self.assertIsInstance(br, BibliographicResource)
        self.assertEqual(str(br.g.identifier), self.graph_set.g_br)

    def test_add_ci(self):
        br1 = self.graph_set.add_br(self.__class__.__name__)
        br2 = self.graph_set.add_br(self.__class__.__name__)
        count1 = self.graph_set.r_count
        ci = self.graph_set.add_ci(self.__class__.__name__, br1, br2)
        count2 = self.graph_set.r_count

        self.assertIsNotNone(ci)
        self.assertEqual(count2, count1 + 1)
        self.assertIsInstance(ci, Citation)
        self.assertEqual(str(ci.g.identifier), self.graph_set.g_ci)

    def test_add_de(self):
        count1 = self.graph_set.r_count
        de = self.graph_set.add_de(self.__class__.__name__)
        count2 = self.graph_set.r_count

        self.assertIsNotNone(de)
        self.assertEqual(count2, count1 + 1)
        self.assertIsInstance(de, DiscourseElement)
        self.assertEqual(str(de.g.identifier), self.graph_set.g_de)

    def test_add_id(self):
        count1 = self.graph_set.r_count
        identifier = self.graph_set.add_id(self.__class__.__name__)
        count2 = self.graph_set.r_count

        self.assertIsNotNone(identifier)
        self.assertEqual(count2, count1 + 1)
        self.assertIsInstance(identifier, Identifier)
        self.assertEqual(str(identifier.g.identifier), self.graph_set.g_id)

    def test_add_pl(self):
        count1 = self.graph_set.r_count
        pl = self.graph_set.add_pl(self.__class__.__name__)
        count2 = self.graph_set.r_count

        self.assertIsNotNone(pl)
        self.assertEqual(count2, count1 + 1)
        self.assertIsInstance(pl, PointerList)
        self.assertEqual(str(pl.g.identifier), self.graph_set.g_pl)

    def test_add_rp(self):
        count1 = self.graph_set.r_count
        rp = self.graph_set.add_rp(self.__class__.__name__)
        count2 = self.graph_set.r_count

        self.assertIsNotNone(rp)
        self.assertEqual(count2, count1 + 1)
        self.assertIsInstance(rp, ReferencePointer)
        self.assertEqual(str(rp.g.identifier), self.graph_set.g_rp)

    def test_add_ra(self):
        count1 = self.graph_set.r_count
        ra = self.graph_set.add_ra(self.__class__.__name__)
        count2 = self.graph_set.r_count

        self.assertIsNotNone(ra)
        self.assertEqual(count2, count1 + 1)
        self.assertIsInstance(ra, ResponsibleAgent)
        self.assertEqual(str(ra.g.identifier), self.graph_set.g_ra)

    def test_add_re(self):
        count1 = self.graph_set.r_count
        re = self.graph_set.add_re(self.__class__.__name__)
        count2 = self.graph_set.r_count

        self.assertIsNotNone(re)
        self.assertEqual(count2, count1 + 1)
        self.assertIsInstance(re, ResourceEmbodiment)
        self.assertEqual(str(re.g.identifier), self.graph_set.g_re)

    def test_graphs(self):
        count = 10
        for i in range(count):
            self.graph_set.add_ar(self.__class__.__name__)
        result = self.graph_set.graphs()
        self.assertIsNotNone(result)
        self.assertEqual(len(result), count)
        for graph in result:
            self.assertIsInstance(graph, Graph)

    def test_get_graph_iri(self):
        ar = self.graph_set.add_ar(self.__class__.__name__)
        iri = str(ar.g.identifier)
        result = GraphSet.get_graph_iri(ar.g)
        self.assertIsNotNone(result)
        self.assertEqual(iri, result)


if __name__ == '__main__':
    unittest.main()
