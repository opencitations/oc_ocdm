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

from oc_ocdm import GraphEntity
from oc_ocdm import GraphSet
from oc_ocdm.counter_handler import FilesystemCounterHandler


class TestAgentRole(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.counter_handler = FilesystemCounterHandler("./info_dir/")
        cls.graph_set = GraphSet("http://test/", "context_base", cls.counter_handler, "", wanted_label=False)

    def setUp(self):
        self.graph_set.g = []
        self.ar1 = self.graph_set.add_ar(self.__class__.__name__)
        self.ar2 = self.graph_set.add_ar(self.__class__.__name__)
        self.br = self.graph_set.add_br(self.__class__.__name__)

    def test_follows(self):
        result = self.ar2.follows(self.ar1)
        self.assertIsNone(result)

        triple = self.ar1.res, GraphEntity.has_next, self.ar2.res
        self.assertIn(triple, self.ar1.g)

    def test_create_publisher(self):
        result = self.ar1.create_publisher(self.br)
        self.assertIsNone(result)

        triple1 = self.ar1.res, GraphEntity.with_role, GraphEntity.publisher
        self.assertIn(triple1, self.ar1.g)

        triple2 = self.br.res, GraphEntity.is_document_context_for, self.ar1.res
        self.assertIn(triple2, self.br.g)

    def test_create_author(self):
        result = self.ar1.create_author(self.br)
        self.assertIsNone(result)

        triple1 = self.ar1.res, GraphEntity.with_role, GraphEntity.author
        self.assertIn(triple1, self.ar1.g)

        triple2 = self.br.res, GraphEntity.is_document_context_for, self.ar1.res
        self.assertIn(triple2, self.br.g)

    def test_create_editor(self):
        result = self.ar1.create_editor(self.br)
        self.assertIsNone(result)

        triple1 = self.ar1.res, GraphEntity.with_role, GraphEntity.editor
        self.assertIn(triple1, self.ar1.g)

        triple2 = self.br.res, GraphEntity.is_document_context_for, self.ar1.res
        self.assertIn(triple2, self.br.g)


if __name__ == '__main__':
    unittest.main()