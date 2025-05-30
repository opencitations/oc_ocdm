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

import os
import unittest

from oc_ocdm.counter_handler.sqlite_counter_handler import SqliteCounterHandler
from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.prov.entities.snapshot_entity import SnapshotEntity
from oc_ocdm.prov.prov_set import ProvSet
from oc_ocdm.reader import Reader
from oc_ocdm.storer import Storer
from rdflib import URIRef


class TestProvSet(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    def setUp(self):
        self.graph_set = GraphSet("http://test/", "./info_dir/", "", False)
        counter_db_path = 'oc_ocdm/test/prov/prov_counter.db'
        if os.path.exists(counter_db_path):
            os.remove(counter_db_path)
        self.prov_set = ProvSet(self.graph_set, "http://test/", "./info_dir/", False, custom_counter_handler=SqliteCounterHandler(counter_db_path), supplier_prefix="")
        self.cur_time = 1607375859.846196
        self.cur_time_str = '2020-12-07T21:17:39+00:00'

    def test_add_se(self):
        prov_subj = self.graph_set.add_br(self.resp_agent)
        se = self.prov_set.add_se(prov_subj)

        self.assertIsNotNone(se)
        self.assertIsInstance(se, SnapshotEntity)
        self.assertEqual(str(se.g.identifier), str(prov_subj.res) + "/prov/")

    def test_creation_merged_entity(self):
        a = self.graph_set.add_br(self.resp_agent)
        b = self.graph_set.add_br(self.resp_agent)
        a.merge(b, prefer_self=True)

        result = self.prov_set.generate_provenance(self.cur_time)
        se_a = self.prov_set.get_entity(URIRef(a.res + '/prov/se/1'))
        self.assertIsNotNone(se_a)
        self.assertIsInstance(se_a, SnapshotEntity)
        self.assertEqual(a.res, se_a.get_is_snapshot_of())
        self.assertEqual(self.cur_time_str, se_a.get_generation_time())
        if a.source is not None:
            self.assertEqual(a.source, str(se_a.get_primary_source()))
        if a.resp_agent is not None:
            self.assertEqual(a.resp_agent, str(se_a.get_resp_agent()))
        self.assertEqual(f"The entity '{a.res}' has been created.", se_a.get_description())

    def test_no_snapshot_merged_entity(self):
        a = self.graph_set.add_br(self.resp_agent)
        b = self.graph_set.add_br(self.resp_agent)
        a.merge(b)
        se_a_1 = self.prov_set.add_se(a)

        # This avoids that the presence of the mandatory rdf:type gets interpreted
        # as a modification with respect to an empty preexisting_graph:
        a.remove_every_triple()

        result = self.prov_set.generate_provenance(self.cur_time)
        
        se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
        self.assertIsNone(se_a_2)

    def test_modification_merged_entity(self):
        title = "TEST TITLE"
        a = self.graph_set.add_br(self.resp_agent)
        b = self.graph_set.add_br(self.resp_agent)
        b.has_title(title)
        a.merge(b)
        se_a_1 = self.prov_set.add_se(a)

        result = self.prov_set.generate_provenance(self.cur_time)
        
        self.assertEqual(self.cur_time_str, se_a_1.get_invalidation_time())

        se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
        self.assertIsNotNone(se_a_2)
        self.assertIsInstance(se_a_2, SnapshotEntity)
        self.assertEqual(a.res, se_a_2.get_is_snapshot_of())
        self.assertEqual(self.cur_time_str, se_a_2.get_generation_time())
        if a.source is not None:
            self.assertEqual(a.source, str(se_a_2.get_primary_source()))
        if a.resp_agent is not None:
            self.assertEqual(a.resp_agent, str(se_a_2.get_resp_agent()))
        self.assertSetEqual({se_a_1}, set(se_a_2.get_derives_from()))
        self.assertIsNotNone(se_a_2.get_update_action())
        self.assertEqual(f"The entity '{a.res}' has been modified.", se_a_2.get_description())

    def test_merge_merged_entity(self):
        a = self.graph_set.add_br(self.resp_agent)
        b = self.graph_set.add_br(self.resp_agent)
        c = self.graph_set.add_br(self.resp_agent)

        se_a_1 = self.prov_set.add_se(a)
        se_a_1.has_generation_time("2020-01-01T00:00:00+00:00")
        se_a_1.has_primary_source(URIRef("http://example.org/source_a"))
        
        se_b_1 = self.prov_set.add_se(b)
        se_b_1.has_generation_time("2020-02-01T00:00:00+00:00")
        se_b_1.has_primary_source(URIRef("http://example.org/source_b"))
        
        se_c_1 = self.prov_set.add_se(c)
        se_c_1.has_generation_time("2020-03-01T00:00:00+00:00")
        se_c_1.has_primary_source(URIRef("http://example.org/source_c"))

        a.merge(b)
        a.merge(c)

        result = self.prov_set.generate_provenance(self.cur_time)

        se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
        self.assertIsNotNone(se_a_2)
        self.assertIsInstance(se_a_2, SnapshotEntity)
        self.assertEqual(a.res, se_a_2.get_is_snapshot_of())
        self.assertEqual(self.cur_time_str, se_a_2.get_generation_time())
        if a.source is not None:
            self.assertEqual(a.source, str(se_a_2.get_primary_source()))
        if a.resp_agent is not None:
            self.assertEqual(a.resp_agent, str(se_a_2.get_resp_agent()))
        self.assertNotEqual("2020-01-01T00:00:00+00:00", se_a_2.get_generation_time())
        self.assertNotEqual(URIRef("http://example.org/source_a"), se_a_2.get_primary_source())
        self.assertEqual(self.cur_time_str, se_a_2.get_generation_time())
        if a.source is not None:
            self.assertEqual(a.source, str(se_a_2.get_primary_source()))
        self.assertSetEqual({se_a_1, se_b_1, se_c_1}, set(se_a_2.get_derives_from()))
        self.assertEqual(self.cur_time_str, se_a_1.get_invalidation_time())
        self.assertEqual(f"The entity '{a.res}' has been merged with '{b.res}', '{c.res}'.", se_a_2.get_description())

    def test_creation_non_merged_entity(self):
        a = self.graph_set.add_br(self.resp_agent)

        result = self.prov_set.generate_provenance(self.cur_time)
        
        se_a = self.prov_set.get_entity(URIRef(a.res + '/prov/se/1'))
        self.assertIsNotNone(se_a)
        self.assertIsInstance(se_a, SnapshotEntity)
        self.assertEqual(a.res, se_a.get_is_snapshot_of())
        self.assertEqual(self.cur_time_str, se_a.get_generation_time())
        if a.source is not None:
            self.assertEqual(a.source, str(se_a.get_primary_source()))
        if a.resp_agent is not None:
            self.assertEqual(a.resp_agent, str(se_a.get_resp_agent()))
        self.assertEqual(f"The entity '{a.res}' has been created.", se_a.get_description())

    def test_no_snapshot_non_merged_entity_scenario1(self):
        a = self.graph_set.add_br(self.resp_agent)
        a.mark_as_to_be_deleted()

        result = self.prov_set.generate_provenance(self.cur_time)
        
        se_a = self.prov_set.get_entity(URIRef(a.res + '/prov/se/1'))
        self.assertIsNone(se_a)

    def test_no_snapshot_merged_entity_scenario2(self):
        a = self.graph_set.add_br(self.resp_agent)
        se_a_1 = self.prov_set.add_se(a)

        # This avoids that the presence of the mandatory rdf:type gets interpreted
        # as a modification with respect to an empty preexisting_graph:
        a.remove_every_triple()

        result = self.prov_set.generate_provenance(self.cur_time)
        
        se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
        self.assertIsNone(se_a_2)

    def test_deletion_non_merged_entity(self):
        title = "TEST TITLE"
        a = self.graph_set.add_br(self.resp_agent)
        se_a_1 = self.prov_set.add_se(a)
        a.has_title(title)
        a.mark_as_to_be_deleted()

        result = self.prov_set.generate_provenance(self.cur_time)
        
        self.assertEqual(self.cur_time_str, se_a_1.get_invalidation_time())

        se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
        self.assertIsNotNone(se_a_2)
        self.assertIsInstance(se_a_2, SnapshotEntity)
        self.assertEqual(a.res, se_a_2.get_is_snapshot_of())
        self.assertEqual(self.cur_time_str, se_a_2.get_generation_time())
        if a.source is not None:
            self.assertEqual(a.source, str(se_a_2.get_primary_source()))
        if a.resp_agent is not None:
            self.assertEqual(a.resp_agent, str(se_a_2.get_resp_agent()))
        self.assertSetEqual({se_a_1}, set(se_a_2.get_derives_from()))
        self.assertEqual(f"The entity '{a.res}' has been deleted.", se_a_2.get_description())

    def test_modification_non_merged_entity(self):
        title = "TEST TITLE"
        a = self.graph_set.add_br(self.resp_agent)
        se_a_1 = self.prov_set.add_se(a)
        a.has_title(title)

        result = self.prov_set.generate_provenance(self.cur_time)
        
        self.assertEqual(self.cur_time_str, se_a_1.get_invalidation_time())

        se_a_2 = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
        self.assertIsNotNone(se_a_2)
        self.assertIsInstance(se_a_2, SnapshotEntity)
        self.assertEqual(a.res, se_a_2.get_is_snapshot_of())
        self.assertEqual(self.cur_time_str, se_a_2.get_generation_time())
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

    def test_restore_deleted_entity(self):
        # Create and delete an entity first
        a = self.graph_set.add_br(self.resp_agent)

        # Generate provenance for dcreation
        self.prov_set.generate_provenance(self.cur_time)

        a.mark_as_to_be_deleted()
        
        # Generate provenance for deletion
        self.prov_set.generate_provenance(self.cur_time)
        deletion_time = self.cur_time_str
        
        # Get the deletion snapshot
        se_a_2: SnapshotEntity = self.prov_set.get_entity(URIRef(a.res + '/prov/se/2'))
        self.assertIsNotNone(se_a_2)
        self.assertEqual(deletion_time, se_a_2.get_generation_time())
        self.assertEqual(deletion_time, se_a_2.get_invalidation_time())
        
        # Now restore the entity
        a.mark_as_restored()
        a.has_title("Restored Title")  # Add some modification
        
        # Generate provenance after restoration
        restoration_time = "2020-12-08T21:17:39+00:00"
        result = self.prov_set.generate_provenance(1607462259.846196)  # One day later
        
        # Check the restoration snapshot
        se_a_3: SnapshotEntity = self.prov_set.get_entity(URIRef(a.res + '/prov/se/3'))
        self.assertIsNotNone(se_a_3)
        self.assertEqual(restoration_time, se_a_3.get_generation_time())
        self.assertIsNone(se_a_3.get_invalidation_time())  # No invalidation time for restoration
        self.assertEqual(f"The entity '{a.res}' has been restored.", se_a_3.get_description())
        self.assertSetEqual({se_a_2}, set(se_a_3.get_derives_from()))
        self.assertIsNotNone(se_a_3.get_update_action())

class TestProvSetWorkflow(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join('oc_ocdm', 'test', 'prov', 'provset_workflow_data') + os.sep
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        self.base_iri = "http://test/"
        self.resp_agent = 'http://resp_agent.test/'

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)

    def test_full_workflow(self):
        # Step 1: Create initial data
        graph_set = GraphSet(self.base_iri, self.test_dir, supplier_prefix="060")
        prov_set = ProvSet(graph_set, self.base_iri, self.test_dir, supplier_prefix="060")

        a = graph_set.add_br(self.resp_agent)
        b = graph_set.add_br(self.resp_agent)
        c = graph_set.add_br(self.resp_agent)

        # Create initial snapshots with specific metadata
        se_a = prov_set.add_se(a)
        se_a.has_generation_time("2020-01-01T00:00:00Z")
        se_a.has_primary_source(URIRef("http://example.org/source_a"))

        se_b = prov_set.add_se(b)
        se_b.has_generation_time("2020-02-01T00:00:00Z")
        se_b.has_primary_source(URIRef("http://example.org/source_b"))

        se_c = prov_set.add_se(c)
        se_c.has_generation_time("2020-03-01T00:00:00Z")
        se_c.has_primary_source(URIRef("http://example.org/source_c"))

        # Step 2: Save the data
        storer = Storer(graph_set)
        storer.store_all(self.test_dir, self.base_iri)

        prov_storer = Storer(prov_set)
        prov_storer.store_all(self.test_dir, self.base_iri)

        graph_set.commit_changes()

        # Step 3: Create a new GraphSet and ProvSet, and load the saved data
        new_graph_set = GraphSet(self.base_iri, self.test_dir, supplier_prefix="")
        new_prov_set = ProvSet(new_graph_set, self.base_iri, self.test_dir, supplier_prefix="")

        reader = Reader()
        for dirpath, dirnames, filenames in os.walk(self.test_dir):
            for filename in filenames:
                if filename.endswith('.json') and not dirpath.endswith('prov'):
                    full_path = os.path.join(dirpath, filename)
                    loaded_graph = reader.load(full_path)
                    reader.import_entities_from_graph(new_graph_set, results=loaded_graph, resp_agent=self.resp_agent)

        # Step 4: Perform merge operation
        new_a = new_graph_set.get_entity(a.res)
        new_b = new_graph_set.get_entity(b.res)
        new_c = new_graph_set.get_entity(c.res)

        new_a.merge(new_b)
        new_a.merge(new_c)

        # Step 5: Generate new provenance
        cur_time = 1585692000
        new_prov_set.generate_provenance(cur_time)

        # Step 6: Save the updated data
        new_storer = Storer(new_graph_set)
        new_storer.store_all(self.test_dir, self.base_iri)

        new_prov_storer = Storer(new_prov_set)
        new_prov_storer.store_all(self.test_dir, self.base_iri)

        # Step 7: Load and check the final state
        final_graph_set = GraphSet(self.base_iri, self.test_dir, supplier_prefix="")
        final_prov_set = ProvSet(final_graph_set, self.base_iri, self.test_dir, supplier_prefix="")

        final_reader = Reader()
        for dirpath, dirnames, filenames in os.walk(self.test_dir):
            for filename in filenames:
                if filename.endswith('.json') and not dirpath.endswith('prov'):
                    full_path = os.path.join(dirpath, filename)
                    loaded_graph = reader.load(full_path)
                    final_reader.import_entities_from_graph(final_graph_set, results=loaded_graph, resp_agent=self.resp_agent)

        # Check the final state
        final_a = final_graph_set.get_entity(a.res)
        final_se_a = new_prov_set.get_entity(URIRef(a.res + '/prov/se/2'))

        self.assertIsNotNone(final_se_a)
        # self.assertEqual(cur_time, final_se_a.get_generation_time())
        # self.assertNotEqual("2020-01-01T00:00:00Z", final_se_a.get_generation_time())
        # self.assertNotEqual(URIRef("http://example.org/source_a"), final_se_a.get_primary_source())

        # # Check that it derives from all previous snapshots
        # derived_from = set(final_se_a.get_derives_from())
        # self.assertEqual(3, len(derived_from))
        # self.assertTrue(all(se.res in derived_from for se in [se_a, se_b, se_c]))


if __name__ == '__main__':
    unittest.main()