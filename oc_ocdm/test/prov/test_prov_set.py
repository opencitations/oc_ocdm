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

from rdflib import Graph, Literal, URIRef

from oc_ocdm.counter_handler.sqlite_counter_handler import SqliteCounterHandler
from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.prov.entities.snapshot_entity import SnapshotEntity
from oc_ocdm.prov.prov_set import ProvSet


class TestProvSet(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    def setUp(self):
        self.graph_set = GraphSet("http://test/", "./info_dir/", "", False)
        self.prov_set = ProvSet(self.graph_set, "http://test/", "./info_dir/", False, custom_counters={'ci': SqliteCounterHandler('oc_ocdm/test/prov/prov_counter.db')}, supplier_prefix="")

    def test_add_se(self):
        prov_subj = self.graph_set.add_br(self.resp_agent)
        se = self.prov_set.add_se(prov_subj)

        self.assertIsNotNone(se)
        self.assertIsInstance(se, SnapshotEntity)
        self.assertEqual(str(se.g.identifier), str(prov_subj.res) + "/prov/")

    def test_generate_provenance(self):
        cur_time = 1607375859.846196
        cur_time_str = '2020-12-07T21:17:39+00:00'

        with self.subTest('Creation [Merged entity]'):
            a = self.graph_set.add_br(self.resp_agent)
            b = self.graph_set.add_br(self.resp_agent)
            a.merge(b)

            result = self.prov_set.generate_provenance(cur_time)

            se_a = self.prov_set.get_entity(URIRef(a.res + '/prov/se/1'))
            self.assertIsNotNone(se_a)
            self.assertIsInstance(se_a, SnapshotEntity)
            self.assertEqual(a.res, se_a.get_is_snapshot_of())
            self.assertEqual(cur_time_str, se_a.get_generation_time())
            if a.source is not None:
                self.assertEqual(a.source, str(se_a.get_primary_source()))
            if a.resp_agent is not None:
                self.assertEqual(a.resp_agent, str(se_a.get_resp_agent()))

            self.assertEqual(f"The entity '{a.res}' has been created.", se_a.get_description())
        with self.subTest('No snapshot [Merged entity]'):
            a = self.graph_set.add_br(self.resp_agent)
            b = self.graph_set.add_br(self.resp_agent)
            a.merge(b)
            se_a_1 = self.prov_set.add_se(a)

            # This avoids that the presence of the mandatory rdf:type gets interpreted
            # as a modification with respect to an empty preexisting_graph:
            a.remove_every_triple()

            result = self.prov_set.generate_provenance(cur_time)
            

            se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
            self.assertIsNone(se_a_2)
        with self.subTest('Modification [Merged entity]'):
            title = "TEST TITLE"
            a = self.graph_set.add_br(self.resp_agent)
            b = self.graph_set.add_br(self.resp_agent)
            b.has_title(title)
            a.merge(b)
            se_a_1 = self.prov_set.add_se(a)

            result = self.prov_set.generate_provenance(cur_time)
            
            self.assertEqual(cur_time_str, se_a_1.get_invalidation_time())

            se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
            self.assertIsNotNone(se_a_2)
            self.assertIsInstance(se_a_2, SnapshotEntity)
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
            a = self.graph_set.add_br(self.resp_agent)
            b = self.graph_set.add_br(self.resp_agent)
            c = self.graph_set.add_br(self.resp_agent)
            a.merge(b)
            a.merge(c)
            se_a_1 = self.prov_set.add_se(a)
            se_b_1 = self.prov_set.add_se(b)

            result = self.prov_set.generate_provenance(cur_time)
            

            self.assertEqual(cur_time_str, se_a_1.get_invalidation_time())

            se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
            self.assertIsNotNone(se_a_2)
            self.assertIsInstance(se_a_2, SnapshotEntity)
            self.assertEqual(a.res, se_a_2.get_is_snapshot_of())
            self.assertEqual(cur_time_str, se_a_2.get_generation_time())
            if a.source is not None:
                self.assertEqual(a.source, str(se_a_2.get_primary_source()))
            if a.resp_agent is not None:
                self.assertEqual(a.resp_agent, str(se_a_2.get_resp_agent()))

            self.assertSetEqual({se_a_1, se_b_1}, set(se_a_2.get_derives_from()))
            self.assertEqual(f"The entity '{a.res}' has been merged with '{b.res}'.", se_a_2.get_description())
        with self.subTest('Creation [Non-Merged entity]'):
            a = self.graph_set.add_br(self.resp_agent)

            result = self.prov_set.generate_provenance(cur_time)
            

            se_a = self.prov_set.get_entity(URIRef(a.res + '/prov/se/1'))
            self.assertIsNotNone(se_a)
            self.assertIsInstance(se_a, SnapshotEntity)
            self.assertEqual(a.res, se_a.get_is_snapshot_of())
            self.assertEqual(cur_time_str, se_a.get_generation_time())
            if a.source is not None:
                self.assertEqual(a.source, str(se_a.get_primary_source()))
            if a.resp_agent is not None:
                self.assertEqual(a.resp_agent, str(se_a.get_resp_agent()))

            self.assertEqual(f"The entity '{a.res}' has been created.", se_a.get_description())
        with self.subTest('No snapshot [Non-Merged entity] (Scenario 1)'):
            a = self.graph_set.add_br(self.resp_agent)
            a.mark_as_to_be_deleted()

            result = self.prov_set.generate_provenance(cur_time)
            

            se_a = self.prov_set.get_entity(URIRef(a.res + '/prov/se/1'))
            self.assertIsNone(se_a)
        with self.subTest('No snapshot [Merged entity] (Scenario 2)'):
            a = self.graph_set.add_br(self.resp_agent)
            se_a_1 = self.prov_set.add_se(a)

            # This avoids that the presence of the mandatory rdf:type gets interpreted
            # as a modification with respect to an empty preexisting_graph:
            a.remove_every_triple()

            result = self.prov_set.generate_provenance(cur_time)
            

            se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
            self.assertIsNone(se_a_2)
        with self.subTest('Deletion [Non-Merged entity]'):
            title = "TEST TITLE"
            a = self.graph_set.add_br(self.resp_agent)
            se_a_1 = self.prov_set.add_se(a)
            a.has_title(title)
            a.mark_as_to_be_deleted()

            result = self.prov_set.generate_provenance(cur_time)
            

            self.assertEqual(cur_time_str, se_a_1.get_invalidation_time())

            se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
            self.assertIsNotNone(se_a_2)
            self.assertIsInstance(se_a_2, SnapshotEntity)
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
            a = self.graph_set.add_br(self.resp_agent)
            se_a_1 = self.prov_set.add_se(a)
            a.has_title(title)

            result = self.prov_set.generate_provenance(cur_time)
            

            self.assertEqual(cur_time_str, se_a_1.get_invalidation_time())

            se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
            self.assertIsNotNone(se_a_2)
            self.assertIsInstance(se_a_2, SnapshotEntity)
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
        br = self.graph_set.add_br(self.resp_agent)
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

    def test_generate_provenance_for_citations(self):
        preexisting_graph = Graph()
        preexisting_graph.add((
            URIRef('https://w3id.org/oc/index/coci/ci/020010000023601000907630001040258020000010008010559090238044008040338381018136312231227010309014203370037122439026325-020010305093619112227370109090937010437073701020309'),
            URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
            URIRef('http://purl.org/spar/cito/Citation')))
        preexisting_graph.add((
            URIRef('https://w3id.org/oc/index/coci/ci/020010000023601000907630001040258020000010008010559090238044008040338381018136312231227010309014203370037122439026325-020010305093619112227370109090937010437073701020309'),
            URIRef('http://purl.org/spar/cito/hasCitationCreationDate'),
            Literal('2022', datatype='http://www.w3.org/2001/XMLSchema#gYear')))
        ci = self.graph_set.add_ci(self.resp_agent, res=URIRef('https://w3id.org/oc/index/coci/ci/020010000023601000907630001040258020000010008010559090238044008040338381018136312231227010309014203370037122439026325-020010305093619112227370109090937010437073701020309'), preexisting_graph=preexisting_graph)
        self.prov_set.generate_provenance()
        self.graph_set.commit_changes()
        ci.has_citation_creation_date('2022')
        self.prov_set.generate_provenance()
        prov_entity = self.prov_set._retrieve_last_snapshot(URIRef('https://w3id.org/oc/index/coci/ci/020010000023601000907630001040258020000010008010559090238044008040338381018136312231227010309014203370037122439026325-020010305093619112227370109090937010437073701020309'))
        self.assertEqual(prov_entity, URIRef('https://w3id.org/oc/index/coci/ci/020010000023601000907630001040258020000010008010559090238044008040338381018136312231227010309014203370037122439026325-020010305093619112227370109090937010437073701020309/prov/se/1'))

if __name__ == '__main__':
    unittest.main()
