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
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, DCTERMS

from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.prov.prov_set import ProvSet
from oc_ocdm.support.query_utils import (
    get_update_query, get_insert_query, get_delete_query,
    get_separated_queries, serialize_graph_to_nquads, _compute_graph_changes
)


class TestQueryUtils(unittest.TestCase):
    """Test suite for query_utils functions."""

    def setUp(self):
        self.base_iri = "https://test.org/"
        self.graph_set = GraphSet(self.base_iri, "", "060", False)

    def test_get_insert_query_empty_set(self):
        """Test get_insert_query with empty set returns empty list."""
        graph_iri = URIRef("https://test.org/graph/1")
        empty_set = set()

        queries, count = get_insert_query(graph_iri, empty_set)

        self.assertEqual(queries, [])
        self.assertEqual(count, 0)

    def test_get_insert_query_with_triples(self):
        """Test get_insert_query with triples generates correct query."""
        graph_iri = URIRef("https://test.org/graph/1")
        subject = URIRef("https://test.org/resource/1")
        triples = {
            (subject, RDF.type, URIRef("https://test.org/Class")),
            (subject, DCTERMS.title, Literal("Test")),
        }

        queries, count = get_insert_query(graph_iri, triples)

        self.assertEqual(len(queries), 1)
        self.assertIn("INSERT DATA", queries[0])
        self.assertIn(str(graph_iri), queries[0])
        self.assertEqual(count, 2)

    def test_get_delete_query_empty_set(self):
        """Test get_delete_query with empty set returns empty list."""
        graph_iri = URIRef("https://test.org/graph/1")
        empty_set = set()

        queries, count = get_delete_query(graph_iri, empty_set)

        self.assertEqual(queries, [])
        self.assertEqual(count, 0)

    def test_get_delete_query_with_triples(self):
        """Test get_delete_query with triples generates correct query."""
        graph_iri = URIRef("https://test.org/graph/1")
        subject = URIRef("https://test.org/resource/1")
        triples = {(subject, RDF.type, URIRef("https://test.org/Class"))}

        queries, count = get_delete_query(graph_iri, triples)

        self.assertEqual(len(queries), 1)
        self.assertIn("DELETE DATA", queries[0])
        self.assertIn(str(graph_iri), queries[0])
        self.assertEqual(count, 1)

    def test_get_update_query_unchanged_entity(self):
        """Test get_update_query returns empty for unchanged entity."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("Test Title")
        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        queries, added, removed = get_update_query(br, entity_type="graph")

        self.assertEqual(queries, [])
        self.assertEqual(added, 0)
        self.assertEqual(removed, 0)

    def test_get_update_query_new_entity(self):
        """Test get_update_query for new entity generates INSERT."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("New Title")

        queries, added, removed = get_update_query(br, entity_type="graph")

        self.assertTrue(len(queries) >= 1)
        self.assertTrue(any("INSERT DATA" in q for q in queries))
        self.assertEqual(added, 2)
        self.assertEqual(removed, 0)

    def test_get_update_query_modified_entity(self):
        """Test get_update_query for modified entity with changes."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("Original Title")

        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        br.g.add((br.res, URIRef("http://example.org/newProp"), Literal("New Value")))

        queries, added, removed = get_update_query(br, entity_type="graph")

        self.assertTrue(len(queries) >= 1)
        self.assertTrue(any("INSERT DATA" in q for q in queries))
        self.assertEqual(added, 1)
        self.assertEqual(removed, 0)

    def test_get_update_query_deleted_entity(self):
        """Test get_update_query for deleted entity generates DELETE."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("To Delete")
        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        br.mark_as_to_be_deleted()

        queries, added, removed = get_update_query(br, entity_type="graph")

        self.assertTrue(len(queries) >= 1)
        self.assertTrue(any("DELETE DATA" in q for q in queries))
        self.assertFalse(any("INSERT DATA" in q for q in queries))
        self.assertEqual(added, 0)
        self.assertEqual(removed, 2)

    def test_get_update_query_prov_entity_optimization(self):
        """Test get_update_query for prov entity skips graph_diff."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("Test")

        prov_set = ProvSet(self.graph_set, self.base_iri)
        se = prov_set.add_se(br)
        se.has_description("Creation")

        queries, added, removed = get_update_query(se, entity_type="prov")

        self.assertTrue(len(queries) >= 1)
        self.assertTrue(any("INSERT DATA" in q for q in queries))
        self.assertFalse(any("DELETE DATA" in q for q in queries))
        self.assertEqual(added, len(se.g))
        self.assertEqual(removed, 0)

    def test_get_update_query_early_exit_same_length(self):
        """Test early-exit optimization when graphs have same length."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("Test Title")
        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        queries, added, removed = get_update_query(br, entity_type="graph")

        self.assertEqual(queries, [])
        self.assertEqual(added, 0)
        self.assertEqual(removed, 0)

    def test_get_update_query_different_length_graphs(self):
        """Test that graphs with different lengths generate queries."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("Original")
        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        br.has_subtitle("New Subtitle")

        queries, added, removed = get_update_query(br, entity_type="graph")

        self.assertTrue(len(queries) >= 1)
        self.assertTrue(any("INSERT DATA" in q for q in queries))
        self.assertEqual(added, 1)
        self.assertEqual(removed, 0)

    def test_get_update_query_entity_with_only_additions(self):
        """Test entity with only new triples generates INSERT only."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("Original")
        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        br.has_subtitle("Additional Info")

        queries, added, removed = get_update_query(br, entity_type="graph")

        self.assertTrue(len(queries) >= 1)
        self.assertTrue(any("INSERT DATA" in q for q in queries))
        self.assertFalse(any("DELETE DATA" in q for q in queries))
        self.assertEqual(added, 1)
        self.assertEqual(removed, 0)

    def test_compute_graph_changes_prov_entity(self):
        """Test _compute_graph_changes with provenance entity."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("Test")

        prov_set = ProvSet(self.graph_set, self.base_iri)
        se = prov_set.add_se(br)
        se.has_description("Creation")

        to_insert, to_delete, added, removed = _compute_graph_changes(se, "prov")

        self.assertEqual(len(to_insert), len(se.g))
        self.assertEqual(len(to_delete), 0)
        self.assertEqual(added, len(se.g))
        self.assertEqual(removed, 0)

    def test_compute_graph_changes_deleted_entity(self):
        """Test _compute_graph_changes with deleted entity."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("To Delete")
        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        original_count = len(br.preexisting_graph)
        br.mark_as_to_be_deleted()

        to_insert, to_delete, added, removed = _compute_graph_changes(br, "graph")

        self.assertEqual(len(to_insert), 0)
        self.assertEqual(len(to_delete), original_count)
        self.assertEqual(added, 0)
        self.assertEqual(removed, original_count)

    def test_compute_graph_changes_unchanged_entity(self):
        """Test _compute_graph_changes with unchanged entity."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("Test")
        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        to_insert, to_delete, added, removed = _compute_graph_changes(br, "graph")

        self.assertEqual(len(to_insert), 0)
        self.assertEqual(len(to_delete), 0)
        self.assertEqual(added, 0)
        self.assertEqual(removed, 0)

    def test_compute_graph_changes_modified_entity(self):
        """Test _compute_graph_changes with modified entity."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("Original")
        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        br.has_subtitle("New Subtitle")

        to_insert, to_delete, added, removed = _compute_graph_changes(br, "graph")

        self.assertEqual(len(to_insert), 1)
        self.assertEqual(len(to_delete), 0)
        self.assertEqual(added, 1)
        self.assertEqual(removed, 0)

    def test_serialize_graph_to_nquads(self):
        """Test serialize_graph_to_nquads generates valid N-Quads."""
        subject = URIRef("https://test.org/resource/1")
        triples = {
            (subject, RDF.type, URIRef("https://test.org/Class")),
            (subject, DCTERMS.title, Literal("Test")),
        }
        graph_iri = URIRef("https://test.org/graph/1")

        nquads = serialize_graph_to_nquads(triples, graph_iri)

        self.assertEqual(len(nquads), 2)
        for nquad in nquads:
            self.assertIn(str(graph_iri), nquad)
            self.assertTrue(nquad.endswith(" .\n"))
            self.assertIn("<", nquad)

    def test_get_separated_queries(self):
        """Test get_separated_queries returns separate INSERT and DELETE."""
        br = self.graph_set.add_br(self.base_iri + "br/1")

        with self.subTest("new_entity"):
            br.has_title("New Title")
            insert_queries, delete_queries, n_added, n_removed, insert_g = get_separated_queries(br, "graph")

            self.assertTrue(len(insert_queries) >= 1)
            self.assertTrue(any("INSERT DATA" in q for q in insert_queries))
            self.assertEqual(delete_queries, [])
            self.assertEqual(n_added, 2)
            self.assertEqual(n_removed, 0)
            self.assertEqual(len(insert_g), 2)

        with self.subTest("unchanged_entity"):
            br.preexisting_graph = Graph(identifier=br.g.identifier)
            for triple in br.g:
                br.preexisting_graph.add(triple)

            insert_queries, delete_queries, n_added, n_removed, insert_g = get_separated_queries(br, "graph")

            self.assertEqual(insert_queries, [])
            self.assertEqual(delete_queries, [])
            self.assertEqual(n_added, 0)
            self.assertEqual(n_removed, 0)
            self.assertEqual(len(insert_g), 0)

        with self.subTest("modified_entity"):
            br.has_subtitle("New Subtitle")
            insert_queries, delete_queries, n_added, n_removed, insert_g = get_separated_queries(br, "graph")

            self.assertTrue(len(insert_queries) >= 1)
            self.assertTrue(any("INSERT DATA" in q for q in insert_queries))
            self.assertEqual(delete_queries, [])
            self.assertEqual(n_added, 1)
            self.assertEqual(n_removed, 0)
            self.assertEqual(len(insert_g), 1)

        with self.subTest("deleted_entity"):
            br.mark_as_to_be_deleted()
            insert_queries, delete_queries, n_added, n_removed, insert_g = get_separated_queries(br, "graph")

            self.assertEqual(insert_queries, [])
            self.assertTrue(len(delete_queries) >= 1)
            self.assertTrue(any("DELETE DATA" in q for q in delete_queries))
            self.assertEqual(n_added, 0)
            self.assertEqual(n_removed, 2)
            self.assertEqual(len(insert_g), 0)


if __name__ == '__main__':
    unittest.main()
