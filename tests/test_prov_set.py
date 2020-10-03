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

from oc_ocdm import GraphSet
from oc_ocdm import ProvSet
from oc_ocdm.counter_handler import FilesystemCounterHandler


class TestProvSet(unittest.TestCase):

    def setUp(self):
        self.counter_handler = FilesystemCounterHandler("./info_dir/")
        self.prov_subj_graph_set = GraphSet("http://test/", "context_base", self.counter_handler, "",
                                           wanted_label=False)

        self.prov_set = ProvSet(prov_subj_graph_set=self.prov_subj_graph_set, base_iri="http://test/",
                               context_path="context_base", counter_handler=self.counter_handler,
                               wanted_label=False, supplier_prefix="070",
                               triplestore_url="http://localhost:9999/blazegraph/sparql")

    def test_retrieve_last_snapshot(self):
        br = self.prov_subj_graph_set.add_br(self.__class__.__name__)
        br_res = URIRef(str(br))
        result = self.prov_set._retrieve_last_snapshot(br_res)
        self.assertIsNone(result)

        se = self.prov_set.add_se(self.__class__.__name__, prov_subject=br)
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
