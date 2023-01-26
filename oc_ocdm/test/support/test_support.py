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

from rdflib import Namespace, URIRef

from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.prov.prov_set import ProvSet
from oc_ocdm.support.support import (find_paths,
                                     get_ordered_contributors_from_br)


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


if __name__ == '__main__':
    unittest.main()