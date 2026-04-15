#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import unittest

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.graph_set import GraphSet
from triplelite import RDFTerm


class TestBibliographicEntity(unittest.TestCase):
    resp_agent = 'http://resp_agent.test/'

    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_set = GraphSet("http://test/", "./info_dir/", "", False)

    def setUp(self):
        self.entity = self.graph_set.add_ar(self.resp_agent)
        self.identifier = self.graph_set.add_id(self.resp_agent)

    def test_has_identifier(self):
        result = self.entity.has_identifier(self.identifier)
        self.assertIsNone(result)

        triple = self.entity.res, GraphEntity.iri_has_identifier, RDFTerm("uri", str(self.identifier.res))
        self.assertIn(triple, self.entity.g)

    def test_remove_duplicated_identifiers(self):
        id1 = self.graph_set.add_id(self.resp_agent)
        id2 = self.graph_set.add_id(self.resp_agent)
        id3 = self.graph_set.add_id(self.resp_agent)
        id4 = self.graph_set.add_id(self.resp_agent)

        id1.create_issn('1111-2222')
        id2.create_doi('1111-2222')
        id3.create_issn('3333-4444')
        id4.create_issn('1111-2222')

        self.entity.has_identifier(id1)
        self.entity.has_identifier(id2)
        self.entity.has_identifier(id3)
        self.entity.has_identifier(id4)

        result = self.entity.remove_duplicated_identifiers()

        self.assertIsNone(result)

        id_list = self.entity.get_identifiers()
        self.assertEqual(3, len(id_list))

        # Tuples were used down below inside the sets because they're are hashable (since they're immutable):
        id_list_set = {(i.get_scheme(), i.get_literal_value()) for i in id_list}

        non_duplicated_ids = {(GraphEntity.iri_issn, '1111-2222'),
                              (GraphEntity.iri_issn, '3333-4444'),
                              (GraphEntity.iri_doi, '1111-2222')}

        self.assertSetEqual(id_list_set, non_duplicated_ids)


if __name__ == '__main__':
    unittest.main()
