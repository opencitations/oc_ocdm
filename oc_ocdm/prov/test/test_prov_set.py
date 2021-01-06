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

from rdflib import URIRef

from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.prov.prov_set import ProvSet
from oc_ocdm.prov.entities.entity_snapshot import EntitySnapshot


class TestProvSet(unittest.TestCase):

    def setUp(self):
        self.graph_set = GraphSet("http://test/", "./info_dir/", "", False)
        self.prov_set = ProvSet(self.graph_set, "http://test/", "./info_dir/", "070", False)

    def test_add_se(self):
        prov_subj = self.graph_set.add_br(self.__class__.__name__)
        se = self.prov_set.add_se(prov_subj)

        self.assertIsNotNone(se)
        self.assertIsInstance(se, EntitySnapshot)
        self.assertEqual(str(se.g.identifier), str(prov_subj.res) + "/prov/")

    def test_generate_provenance(self):
        cur_time = 1607375859.846196
        cur_time_str = '2020-12-07T22:17:39'

        with self.subTest('Creation [Merged entity]'):
            a = self.graph_set.add_br(self.__class__.__name__)
            b = self.graph_set.add_br(self.__class__.__name__)
            a.merge(b)

            result = self.prov_set.generate_provenance(cur_time)
            self.assertIsNone(result)

            se_a = self.prov_set.get_entity(URIRef(a.res + '/prov/se/1'))
            self.assertIsNotNone(se_a)
            self.assertIsInstance(se_a, EntitySnapshot)
            self.assertEqual(a.res, se_a.get_is_snapshot_of())
            self.assertEqual(cur_time_str, se_a.get_generation_time())
            if a.source is not None:
                self.assertEqual(a.source, str(se_a.get_primary_source()))
            if a.resp_agent is not None:
                self.assertEqual(a.resp_agent, str(se_a.get_resp_agent()))

            self.assertEqual(f"The entity '{a.res}' has been created.", se_a.get_description())
        with self.subTest('No snapshot [Merged entity]'):
            a = self.graph_set.add_br(self.__class__.__name__)
            b = self.graph_set.add_br(self.__class__.__name__)
            a.merge(b)
            se_a_1 = self.prov_set.add_se(a)

            # This avoids that the presence of the mandatory rdf:type gets interpreted
            # as a modification with respect to an empty preexisting_graph:
            a.remove_every_triple()

            result = self.prov_set.generate_provenance(cur_time)
            self.assertIsNone(result)

            se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
            self.assertIsNone(se_a_2)
        with self.subTest('Modification [Merged entity]'):
            title = "TEST TITLE"
            a = self.graph_set.add_br(self.__class__.__name__)
            b = self.graph_set.add_br(self.__class__.__name__)
            b.has_title(title)
            a.merge(b)
            se_a_1 = self.prov_set.add_se(a)

            result = self.prov_set.generate_provenance(cur_time)
            self.assertIsNone(result)

            self.assertEqual(cur_time_str, se_a_1.get_invalidation_time())

            se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
            self.assertIsNotNone(se_a_2)
            self.assertIsInstance(se_a_2, EntitySnapshot)
            self.assertEqual(a.res, se_a_2.get_is_snapshot_of())
            self.assertEqual(cur_time_str, se_a_2.get_generation_time())
            if a.source is not None:
                self.assertEqual(a.source, str(se_a_2.get_primary_source()))
            if a.resp_agent is not None:
                self.assertEqual(a.resp_agent, str(se_a_2.get_resp_agent()))

            self.assertSetEqual({se_a_1}, set(se_a_2.get_derives_from()))
            self.assertIsNotNone(se_a_2.get_update_action())
            self.assertEqual(f"The entity '{a.res}' has been modified.", se_a_2.get_description())
        with self.subTest('Merge [Merged entity]'):
            a = self.graph_set.add_br(self.__class__.__name__)
            b = self.graph_set.add_br(self.__class__.__name__)
            c = self.graph_set.add_br(self.__class__.__name__)
            a.merge(b)
            a.merge(c)
            se_a_1 = self.prov_set.add_se(a)
            se_b_1 = self.prov_set.add_se(b)

            result = self.prov_set.generate_provenance(cur_time)
            self.assertIsNone(result)

            self.assertEqual(cur_time_str, se_a_1.get_invalidation_time())

            se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
            self.assertIsNotNone(se_a_2)
            self.assertIsInstance(se_a_2, EntitySnapshot)
            self.assertEqual(a.res, se_a_2.get_is_snapshot_of())
            self.assertEqual(cur_time_str, se_a_2.get_generation_time())
            if a.source is not None:
                self.assertEqual(a.source, str(se_a_2.get_primary_source()))
            if a.resp_agent is not None:
                self.assertEqual(a.resp_agent, str(se_a_2.get_resp_agent()))

            self.assertSetEqual({se_a_1, se_b_1}, set(se_a_2.get_derives_from()))
            self.assertEqual(f"The entity '{a.res}' has been merged with '{b.res}'.", se_a_2.get_description())
        with self.subTest('Creation [Non-Merged entity]'):
            a = self.graph_set.add_br(self.__class__.__name__)

            result = self.prov_set.generate_provenance(cur_time)
            self.assertIsNone(result)

            se_a = self.prov_set.get_entity(URIRef(a.res + '/prov/se/1'))
            self.assertIsNotNone(se_a)
            self.assertIsInstance(se_a, EntitySnapshot)
            self.assertEqual(a.res, se_a.get_is_snapshot_of())
            self.assertEqual(cur_time_str, se_a.get_generation_time())
            if a.source is not None:
                self.assertEqual(a.source, str(se_a.get_primary_source()))
            if a.resp_agent is not None:
                self.assertEqual(a.resp_agent, str(se_a.get_resp_agent()))

            self.assertEqual(f"The entity '{a.res}' has been created.", se_a.get_description())
        with self.subTest('No snapshot [Non-Merged entity] (Scenario 1)'):
            a = self.graph_set.add_br(self.__class__.__name__)
            a.mark_as_to_be_deleted()

            result = self.prov_set.generate_provenance(cur_time)
            self.assertIsNone(result)

            se_a = self.prov_set.get_entity(URIRef(a.res + '/prov/se/1'))
            self.assertIsNone(se_a)
        with self.subTest('No snapshot [Merged entity] (Scenario 2)'):
            a = self.graph_set.add_br(self.__class__.__name__)
            se_a_1 = self.prov_set.add_se(a)

            # This avoids that the presence of the mandatory rdf:type gets interpreted
            # as a modification with respect to an empty preexisting_graph:
            a.remove_every_triple()

            result = self.prov_set.generate_provenance(cur_time)
            self.assertIsNone(result)

            se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
            self.assertIsNone(se_a_2)
        with self.subTest('Deletion [Non-Merged entity]'):
            a = self.graph_set.add_br(self.__class__.__name__)
            se_a_1 = self.prov_set.add_se(a)
            a.has_title('ciao')
            a.mark_as_to_be_deleted()

            result = self.prov_set.generate_provenance(cur_time)
            self.assertIsNone(result)

            self.assertEqual(cur_time_str, se_a_1.get_invalidation_time())

            se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
            self.assertIsNotNone(se_a_2)
            self.assertIsInstance(se_a_2, EntitySnapshot)
            self.assertEqual(a.res, se_a_2.get_is_snapshot_of())
            self.assertEqual(cur_time_str, se_a_2.get_generation_time())
            if a.source is not None:
                self.assertEqual(a.source, str(se_a_2.get_primary_source()))
            if a.resp_agent is not None:
                self.assertEqual(a.resp_agent, str(se_a_2.get_resp_agent()))

            self.assertSetEqual({se_a_1}, set(se_a_2.get_derives_from()))
            self.assertEqual(f"The entity '{a.res}' has been deleted.", se_a_2.get_description())
        with self.subTest('Modification [Non-Merged entity]'):
            title = "TEST TITLE"
            a = self.graph_set.add_br(self.__class__.__name__)
            se_a_1 = self.prov_set.add_se(a)
            a.has_title(title)

            result = self.prov_set.generate_provenance(cur_time)
            self.assertIsNone(result)

            self.assertEqual(cur_time_str, se_a_1.get_invalidation_time())

            se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
            self.assertIsNotNone(se_a_2)
            self.assertIsInstance(se_a_2, EntitySnapshot)
            self.assertEqual(a.res, se_a_2.get_is_snapshot_of())
            self.assertEqual(cur_time_str, se_a_2.get_generation_time())
            if a.source is not None:
                self.assertEqual(a.source, str(se_a_2.get_primary_source()))
            if a.resp_agent is not None:
                self.assertEqual(a.resp_agent, str(se_a_2.get_resp_agent()))

            self.assertSetEqual({se_a_1}, set(se_a_2.get_derives_from()))
            self.assertIsNotNone(se_a_2.get_update_action())
            self.assertEqual(f"The entity '{a.res}' has been modified.", se_a_2.get_description())

    def test_retrieve_last_snapshot(self):
        br = self.graph_set.add_br(self.__class__.__name__)
        br_res = br.res
        result = self.prov_set._retrieve_last_snapshot(br_res)
        self.assertIsNone(result)

        se = self.prov_set.add_se(br)
        result = self.prov_set._retrieve_last_snapshot(br_res)
        self.assertIsNotNone(result)
        self.assertEqual(str(result), str(se))

        prov_subject = URIRef('https://w3id.org/oc/corpus/br/0')
        self.assertRaises(ValueError, self.prov_set._retrieve_last_snapshot, prov_subject)

        prov_subject = URIRef('https://w3id.org/oc/corpus/br/-1')
        self.assertRaises(ValueError, self.prov_set._retrieve_last_snapshot, prov_subject)

        prov_subject = URIRef('https://w3id.org/oc/corpus/br/abc')
        self.assertRaises(ValueError, self.prov_set._retrieve_last_snapshot, prov_subject)


if __name__ == '__main__':
    unittest.main()
