#!/usr/bin/python

# SPDX-FileCopyrightText: 2025-2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import os
import unittest

from rdflib import XSD, Graph, Literal, Namespace, URIRef

from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.prov.prov_set import ProvSet
from oc_ocdm.support.support import (
    build_graph_from_results,
    create_date,
    create_literal,
    find_paths,
    get_datatype_from_iso_8601,
    get_ordered_contributors_from_br,
    normalize_graph_literals,
    sparql_binding_to_term,
)


class TestSupport(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'
    pro = Namespace("http://purl.org/spar/pro/")

    def setUp(self):
        self.graph_set = GraphSet("http://test/", "./info_dir/", "", False)
        self.prov_set = ProvSet(self.graph_set, "http://test/", "./info_dir/", False)

        self.br = self.graph_set.add_br(self.resp_agent)

    def _prepare_ordered_authors_list(self, list_len):
        # First of all, we must cleanup the GraphSet:
        self.br.remove_contributor()

        for ar in self.graph_set.get_ar():
            del self.graph_set.res_to_entity[ar.res]
        for ra in self.graph_set.get_ra():
            del self.graph_set.res_to_entity[ra.res]

        # Then, we initialize a new well-formed linked list of authors:
        ar_ordered_list = []

        for i in range(list_len):
            ra = self.graph_set.add_ra(self.resp_agent)

            ar = self.graph_set.add_ar(self.resp_agent)
            ar.create_author()
            ar.is_held_by(ra)

            self.br.has_contributor(ar)
            ar_ordered_list.append(ar)

        # Here each node of the list gets linked to the next one:
        for i in range(list_len - 1):
            ar_ordered_list[i].has_next(ar_ordered_list[i + 1])

        return ar_ordered_list

    @staticmethod
    def _extract_ra_list(ar_list):
        # Here the RA list is built and returned:
        ra_list = []
        for i in range(len(ar_list)):
            ra = ar_list[i].get_is_held_by()
            if ra is not None:
                ra_list.append(ra)

        return ra_list

    def test_get_ordered_contributors_from_br(self):
        list_len = 100
        with self.subTest("Empty linked list"):
            result = get_ordered_contributors_from_br(self.br, self.pro.author)

            self.assertIsNotNone(result)
            self.assertListEqual([], result)

        with self.subTest("Well-formed linked list"):
            correct_list = self._prepare_ordered_authors_list(list_len)
            result = get_ordered_contributors_from_br(self.br, self.pro.author)

            self.assertIsNotNone(result)
            ar_list = self._extract_ra_list(correct_list)
            self.assertListEqual(ar_list, result)

        with self.subTest("Linked list with a loop"):
            correct_list = self._prepare_ordered_authors_list(list_len)
            # Here we corrupt the well-formed linked list introducing a loop:
            correct_list[80].has_next(correct_list[50])

            self.assertRaises(ValueError, get_ordered_contributors_from_br, self.br, self.pro.author)

        with self.subTest("Linked list split in two sub-lists"):
            correct_list = self._prepare_ordered_authors_list(list_len)
            # Here we corrupt the well-formed linked list introducing a loop:
            correct_list[64].remove_next()

            self.assertRaises(ValueError, get_ordered_contributors_from_br, self.br, self.pro.author)
    
    def test_find_paths(self):
        cur_dir_path, cur_file_path = find_paths(
            res = URIRef('https://w3id.org/oc/meta/br/060169'),
            base_dir = os.path.join('support', 'test', 'data', 'rdf'),
            base_iri = 'https://w3id.org/oc/meta',
            default_dir = '_',
            dir_split = 10000,
            n_file_item = 1000,
            is_json = True)
        self.assertEqual((cur_dir_path, cur_file_path), (os.path.join('support', 'test', 'data', 'rdfbr', '060', '10000'), os.path.join('support', 'test', 'data', 'rdfbr', '060', '10000', '1000.json')))

    def test_find_paths_prov(self):
        cur_dir_path, cur_file_path = find_paths(
            res = URIRef('https://w3id.org/oc/meta/br/060165/prov/se/1'),
            base_dir = os.path.join('support', 'test', 'data', 'rdf'),
            base_iri = 'https://w3id.org/oc/meta',
            default_dir = '_',
            dir_split = 10000,
            n_file_item = 1000,
            is_json = True)
        self.assertEqual((cur_dir_path, cur_file_path), (os.path.join('support', 'test', 'data', 'rdfbr', '060', '10000', '1000', 'prov'), os.path.join('support', 'test', 'data', 'rdfbr', '060', '10000', '1000', 'prov', 'se.json')))


class TestSparqlBindingToTerm(unittest.TestCase):

    def test_uri_binding(self):
        binding = {'type': 'uri', 'value': 'http://example.org/resource'}
        result = sparql_binding_to_term(binding)
        self.assertEqual(result, URIRef('http://example.org/resource'))

    def test_literal_with_datatype(self):
        binding = {
            'type': 'literal',
            'value': '42',
            'datatype': 'http://www.w3.org/2001/XMLSchema#integer'
        }
        result = sparql_binding_to_term(binding)
        self.assertEqual(result, Literal('42', datatype=XSD.integer))

    def test_literal_with_language(self):
        binding = {'type': 'literal', 'value': 'hello', 'xml:lang': 'en'}
        result = sparql_binding_to_term(binding)
        self.assertEqual(result, Literal('hello', lang='en'))
        self.assertIsInstance(result, Literal)
        assert isinstance(result, Literal)
        self.assertEqual(result.language, 'en')

    def test_simple_literal_normalized_to_xsd_string(self):
        binding = {'type': 'literal', 'value': 'plain text'}
        result = sparql_binding_to_term(binding)
        self.assertEqual(result, Literal('plain text', datatype=XSD.string))
        self.assertIsInstance(result, Literal)
        assert isinstance(result, Literal)
        self.assertEqual(result.datatype, XSD.string)


class TestNormalizeGraphLiterals(unittest.TestCase):

    def test_simple_literal_gets_xsd_string(self):
        g = Graph()
        s = URIRef('http://example.org/s')
        p = URIRef('http://example.org/p')
        g.add((s, p, Literal('plain')))
        normalize_graph_literals(g)
        obj = list(g.objects(s, p))[0]
        assert isinstance(obj, Literal)
        self.assertEqual(obj.datatype, XSD.string)

    def test_typed_literal_unchanged(self):
        g = Graph()
        s = URIRef('http://example.org/s')
        p = URIRef('http://example.org/p')
        original = Literal('42', datatype=XSD.integer)
        g.add((s, p, original))
        normalize_graph_literals(g)
        obj = list(g.objects(s, p))[0]
        assert isinstance(obj, Literal)
        self.assertEqual(obj.datatype, XSD.integer)

    def test_lang_literal_unchanged(self):
        g = Graph()
        s = URIRef('http://example.org/s')
        p = URIRef('http://example.org/p')
        original = Literal('ciao', lang='it')
        g.add((s, p, original))
        normalize_graph_literals(g)
        obj = list(g.objects(s, p))[0]
        assert isinstance(obj, Literal)
        self.assertEqual(obj.language, 'it')
        self.assertIsNone(obj.datatype)

    def test_empty_graph(self):
        g = Graph()
        normalize_graph_literals(g)
        self.assertEqual(len(g), 0)


class TestCreateDate(unittest.TestCase):

    def test_none_returns_none(self):
        self.assertIsNone(create_date(None))

    def test_empty_list_returns_none(self):
        self.assertIsNone(create_date([]))

    def test_year_only(self):
        self.assertEqual(create_date([2023]), '2023')

    def test_year_month(self):
        self.assertEqual(create_date([2023, 6]), '2023-06')

    def test_full_date(self):
        self.assertEqual(create_date([2023, 6, 15]), '2023-06-15')

    def test_full_date_jan_1_returns_year_month(self):
        self.assertEqual(create_date([2023, 1, 1]), '2023-01')

    def test_three_elements_month_none_day_none_returns_year(self):
        self.assertEqual(create_date([2023, None, None]), '2023')

    def test_three_elements_with_month_and_day_1(self):
        self.assertEqual(create_date([2023, 3, 1]), '2023-03-01')

    def test_first_element_none(self):
        self.assertIsNone(create_date([None]))


class TestGetDatatypeFromIso8601(unittest.TestCase):

    def test_full_date(self):
        dt, val = get_datatype_from_iso_8601('2023-06-15')
        self.assertEqual(dt, XSD.date)
        self.assertEqual(val, '2023-06-15')

    def test_year_month(self):
        dt, val = get_datatype_from_iso_8601('2023-06')
        self.assertEqual(dt, XSD.gYearMonth)
        self.assertEqual(val, '2023-06')

    def test_year_only(self):
        dt, val = get_datatype_from_iso_8601('2023')
        self.assertEqual(dt, XSD.gYear)
        self.assertEqual(val, '2023')

    def test_truncates_after_10_chars(self):
        dt, val = get_datatype_from_iso_8601('2023-06-15T10:30:00')
        self.assertEqual(dt, XSD.date)
        self.assertEqual(val, '2023-06-15')

    def test_invalid_string_raises(self):
        with self.assertRaises(ValueError):
            get_datatype_from_iso_8601('not-a-date')


class TestCreateLiteral(unittest.TestCase):

    def test_adds_literal_with_default_xsd_string(self):
        g = Graph()
        res = URIRef('http://example.org/s')
        p = URIRef('http://example.org/p')
        create_literal(g, res, p, 'hello')
        obj = list(g.objects(res, p))[0]
        assert isinstance(obj, Literal)
        self.assertEqual(str(obj), 'hello')
        self.assertEqual(obj.datatype, XSD.string)

    def test_adds_literal_with_explicit_datatype(self):
        g = Graph()
        res = URIRef('http://example.org/s')
        p = URIRef('http://example.org/p')
        create_literal(g, res, p, '42', dt=XSD.integer)
        obj = list(g.objects(res, p))[0]
        assert isinstance(obj, Literal)
        self.assertEqual(obj.datatype, XSD.integer)

    def test_empty_string_adds_nothing(self):
        g = Graph()
        res = URIRef('http://example.org/s')
        p = URIRef('http://example.org/p')
        create_literal(g, res, p, '')
        self.assertEqual(len(g), 0)

    def test_whitespace_only_adds_nothing(self):
        g = Graph()
        res = URIRef('http://example.org/s')
        p = URIRef('http://example.org/p')
        create_literal(g, res, p, '   ')
        self.assertEqual(len(g), 0)


class TestBuildGraphFromResults(unittest.TestCase):

    def test_uri_triple(self):
        results = [{
            's': {'type': 'uri', 'value': 'http://example.org/s'},
            'p': {'type': 'uri', 'value': 'http://example.org/p'},
            'o': {'type': 'uri', 'value': 'http://example.org/o'}
        }]
        g = build_graph_from_results(results)
        self.assertEqual(len(g), 1)
        s, p, o = next(iter(g))
        self.assertEqual(s, URIRef('http://example.org/s'))
        self.assertEqual(o, URIRef('http://example.org/o'))

    def test_literal_object_with_datatype(self):
        results = [{
            's': {'type': 'uri', 'value': 'http://example.org/s'},
            'p': {'type': 'uri', 'value': 'http://example.org/p'},
            'o': {'type': 'literal', 'value': '42', 'datatype': 'http://www.w3.org/2001/XMLSchema#integer'}
        }]
        g = build_graph_from_results(results)
        o = list(g.objects())[0]
        assert isinstance(o, Literal)
        self.assertEqual(o.datatype, XSD.integer)

    def test_literal_object_without_datatype_gets_xsd_string(self):
        results = [{
            's': {'type': 'uri', 'value': 'http://example.org/s'},
            'p': {'type': 'uri', 'value': 'http://example.org/p'},
            'o': {'type': 'literal', 'value': 'plain'}
        }]
        g = build_graph_from_results(results)
        o = list(g.objects())[0]
        assert isinstance(o, Literal)
        self.assertEqual(o.datatype, XSD.string)

    def test_literal_object_with_language(self):
        results = [{
            's': {'type': 'uri', 'value': 'http://example.org/s'},
            'p': {'type': 'uri', 'value': 'http://example.org/p'},
            'o': {'type': 'literal', 'value': 'bonjour', 'xml:lang': 'fr'}
        }]
        g = build_graph_from_results(results)
        o = list(g.objects())[0]
        assert isinstance(o, Literal)
        self.assertEqual(o.language, 'fr')

    def test_empty_results(self):
        g = build_graph_from_results([])
        self.assertEqual(len(g), 0)


if __name__ == '__main__':
    unittest.main()