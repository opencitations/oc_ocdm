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
from oc_ocdm.support.query_utils import get_update_query, get_insert_query, get_delete_query


class TestQueryUtils(unittest.TestCase):
    """Test suite for query_utils functions."""

    def setUp(self):
        self.base_iri = "https://test.org/"
        self.graph_set = GraphSet(self.base_iri, "", "060", False)

    def test_get_insert_query_empty_graph(self):
        """Test get_insert_query with empty graph returns empty string."""
        graph_iri = URIRef("https://test.org/graph/1")
        empty_graph = Graph()

        query, count = get_insert_query(graph_iri, empty_graph)

        self.assertEqual(query, "")
        self.assertEqual(count, 0)

    def test_get_insert_query_with_triples(self):
        """Test get_insert_query with triples generates correct query."""
        graph_iri = URIRef("https://test.org/graph/1")
        graph = Graph()
        subject = URIRef("https://test.org/resource/1")
        graph.add((subject, RDF.type, URIRef("https://test.org/Class")))
        graph.add((subject, DCTERMS.title, Literal("Test")))

        query, count = get_insert_query(graph_iri, graph)

        self.assertIn("INSERT DATA", query)
        self.assertIn(str(graph_iri), query)
        self.assertEqual(count, 2)

    def test_get_delete_query_empty_graph(self):
        """Test get_delete_query with empty graph returns empty string."""
        graph_iri = URIRef("https://test.org/graph/1")
        empty_graph = Graph()

        query, count = get_delete_query(graph_iri, empty_graph)

        self.assertEqual(query, "")
        self.assertEqual(count, 0)

    def test_get_delete_query_with_triples(self):
        """Test get_delete_query with triples generates correct query."""
        graph_iri = URIRef("https://test.org/graph/1")
        graph = Graph()
        subject = URIRef("https://test.org/resource/1")
        graph.add((subject, RDF.type, URIRef("https://test.org/Class")))

        query, count = get_delete_query(graph_iri, graph)

        self.assertIn("DELETE DATA", query)
        self.assertIn(str(graph_iri), query)
        self.assertEqual(count, 1)

    def test_get_update_query_unchanged_entity(self):
        """Test get_update_query returns empty for unchanged entity."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("Test Title")
        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        query, added, removed = get_update_query(br, entity_type="graph")

        self.assertEqual(query, "")
        self.assertEqual(added, 0)
        self.assertEqual(removed, 0)

    def test_get_update_query_new_entity(self):
        """Test get_update_query for new entity generates INSERT."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("New Title")

        query, added, removed = get_update_query(br, entity_type="graph")

        self.assertIn("INSERT DATA", query)
        self.assertGreater(added, 0)
        self.assertEqual(removed, 0)

    def test_get_update_query_modified_entity(self):
        """Test get_update_query for modified entity with changes."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("Original Title")

        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        br.g.add((br.res, URIRef("http://example.org/newProp"), Literal("New Value")))

        query, added, removed = get_update_query(br, entity_type="graph")

        self.assertIn("INSERT DATA", query)
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

        query, added, removed = get_update_query(br, entity_type="graph")

        self.assertIn("DELETE DATA", query)
        self.assertNotIn("INSERT DATA", query)
        self.assertEqual(added, 0)
        self.assertGreater(removed, 0)

    def test_get_update_query_prov_entity_optimization(self):
        """Test get_update_query for prov entity skips graph_diff."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("Test")

        prov_set = ProvSet(self.graph_set, self.base_iri)
        se = prov_set.add_se(br)
        se.has_description("Creation")

        query, added, removed = get_update_query(se, entity_type="prov")

        self.assertIn("INSERT DATA", query)
        self.assertNotIn("DELETE DATA", query)
        self.assertGreater(added, 0)
        self.assertEqual(removed, 0)

    def test_get_update_query_early_exit_same_length(self):
        """Test early-exit optimization when graphs have same length."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("Test Title")
        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        query, added, removed = get_update_query(br, entity_type="graph")

        self.assertEqual(query, "")
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

        query, added, removed = get_update_query(br, entity_type="graph")

        self.assertNotEqual(query, "")
        self.assertGreater(added, 0)

    def test_get_update_query_entity_with_only_additions(self):
        """Test entity with only new triples generates INSERT only."""
        br = self.graph_set.add_br(self.base_iri + "br/1")
        br.has_title("Original")
        br.preexisting_graph = Graph(identifier=br.g.identifier)
        for triple in br.g:
            br.preexisting_graph.add(triple)

        br.has_subtitle("Additional Info")

        query, added, removed = get_update_query(br, entity_type="graph")

        self.assertIn("INSERT DATA", query)
        self.assertNotIn("DELETE DATA", query)
        self.assertGreater(added, 0)
        self.assertEqual(removed, 0)


if __name__ == '__main__':
    unittest.main()
