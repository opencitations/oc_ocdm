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

from oc_ocdm.graph import GraphEntity
from oc_ocdm.graph import GraphSet
from oc_ocdm.counter_handler import FilesystemCounterHandler


class TestAgentRole(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.counter_handler = FilesystemCounterHandler("./info_dir/")
        cls.graph_set = GraphSet("http://test/", cls.counter_handler, "", False)

    def setUp(self):
        self.ar1 = self.graph_set.add_ar(self.__class__.__name__)
        self.ar2 = self.graph_set.add_ar(self.__class__.__name__)
        self.ra = self.graph_set.add_ra(self.__class__.__name__)
        self.br = self.graph_set.add_br(self.__class__.__name__)

    def test_has_next(self):
        result = self.ar1.has_next(self.ar2)
        self.assertIsNone(result)

        triple = self.ar1.res, GraphEntity.iri_has_next, self.ar2.res
        self.assertIn(triple, self.ar1.g)

    def test_is_held_by(self):
        result = self.ar1.is_held_by(self.ra)
        self.assertIsNone(result)

        triple = self.ar1.res, GraphEntity.iri_is_held_by, self.ra.res
        self.assertIn(triple, self.ar1.g)

    def test_create_publisher(self):
        result = self.ar1.create_publisher()
        self.assertIsNone(result)

        triple = self.ar1.res, GraphEntity.iri_with_role, GraphEntity.iri_publisher
        self.assertIn(triple, self.ar1.g)

    def test_create_author(self):
        result = self.ar1.create_author()
        self.assertIsNone(result)

        triple = self.ar1.res, GraphEntity.iri_with_role, GraphEntity.iri_author
        self.assertIn(triple, self.ar1.g)

    def test_create_editor(self):
        result = self.ar1.create_editor()
        self.assertIsNone(result)

        triple = self.ar1.res, GraphEntity.iri_with_role, GraphEntity.iri_editor
        self.assertIn(triple, self.ar1.g)


if __name__ == '__main__':
    unittest.main()