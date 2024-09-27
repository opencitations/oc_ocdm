#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2024, Arcangelo Massari <arcangelo.massari@unibo.it>
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
from unittest.mock import MagicMock, patch

from oc_ocdm.counter_handler.redis_counter_handler import RedisCounterHandler


class TestRedisCounterHandler(unittest.TestCase):

    def setUp(self):
        self.mock_redis = MagicMock()
        with patch('redis.Redis', return_value=self.mock_redis):
            self.counter_handler = RedisCounterHandler(host='localhost', port=6379, db=0)

    def test_set_counter(self):
        with self.subTest("Set counter for bibliographic resource"):
            self.counter_handler.set_counter(1, "br", supplier_prefix="060")
            self.mock_redis.set.assert_called_with("br:060", 1)

        with self.subTest("Set counter for identifier"):
            self.counter_handler.set_counter(5, "id", supplier_prefix="060")
            self.mock_redis.set.assert_called_with("id:060", 5)

        with self.subTest("Set counter for agent role"):
            self.counter_handler.set_counter(10, "ar", supplier_prefix="060")
            self.mock_redis.set.assert_called_with("ar:060", 10)

        with self.subTest("Set counter for responsible agent"):
            self.counter_handler.set_counter(15, "ra", supplier_prefix="060")
            self.mock_redis.set.assert_called_with("ra:060", 15)

        with self.subTest("Set counter for resource embodiment"):
            self.counter_handler.set_counter(20, "re", supplier_prefix="060")
            self.mock_redis.set.assert_called_with("re:060", 20)

        with self.subTest("Set provenance counter"):
            self.counter_handler.set_counter(2, "br", "se", "1", "060")
            self.mock_redis.set.assert_called_with("br:060:1:se", 2)

        with self.subTest("Wrong inputs"):
            with self.assertRaises(ValueError):
                self.counter_handler.set_counter(-1, "br", supplier_prefix="060")

    def test_read_counter(self):
        with self.subTest("Read counter for bibliographic resource"):
            self.mock_redis.get.return_value = "1"
            result = self.counter_handler.read_counter("br", supplier_prefix="060")
            self.assertEqual(result, 1)
            self.mock_redis.get.assert_called_with("br:060")

        with self.subTest("Read provenance counter"):
            self.mock_redis.get.return_value = "2"
            result = self.counter_handler.read_counter("br", "se", "1", "060")
            self.assertEqual(result, 2)
            self.mock_redis.get.assert_called_with("br:060:1:se")

        with self.subTest("Read non-existent counter"):
            self.mock_redis.get.return_value = None
            result = self.counter_handler.read_counter("br", supplier_prefix="060")
            self.assertEqual(result, 0)

    def test_increment_counter(self):
        with self.subTest("Increment counter for bibliographic resource"):
            self.mock_redis.incr.return_value = 2
            result = self.counter_handler.increment_counter("br", supplier_prefix="060")
            self.assertEqual(result, 2)
            self.mock_redis.incr.assert_called_with("br:060")

        with self.subTest("Increment provenance counter"):
            self.mock_redis.incr.return_value = 3
            result = self.counter_handler.increment_counter("br", "se", "1", "060")
            self.assertEqual(result, 3)
            self.mock_redis.incr.assert_called_with("br:060:1:se")

    def test_set_metadata_counter(self):
        with self.subTest("Set metadata counter"):
            self.counter_handler.set_metadata_counter(5, "di", "http://dataset/")
            self.mock_redis.set.assert_called_with("metadata:http://dataset/:di", 5)

        with self.subTest("Wrong inputs"):
            with self.assertRaises(ValueError):
                self.counter_handler.set_metadata_counter(-1, "di", "http://dataset/")
            with self.assertRaises(ValueError):
                self.counter_handler.set_metadata_counter(1, "di", None)

    def test_read_metadata_counter(self):
        with self.subTest("Read metadata counter"):
            self.mock_redis.get.return_value = "5"
            result = self.counter_handler.read_metadata_counter("di", "http://dataset/")
            self.assertEqual(result, 5)
            self.mock_redis.get.assert_called_with("metadata:http://dataset/:di")

        with self.subTest("Read non-existent metadata counter"):
            self.mock_redis.get.return_value = None
            result = self.counter_handler.read_metadata_counter("di", "http://dataset/")
            self.assertEqual(result, 0)

        with self.subTest("Wrong inputs"):
            with self.assertRaises(ValueError):
                self.counter_handler.read_metadata_counter("di", None)

    def test_increment_metadata_counter(self):
        with self.subTest("Increment metadata counter"):
            self.mock_redis.incr.return_value = 6
            result = self.counter_handler.increment_metadata_counter("di", "http://dataset/")
            self.assertEqual(result, 6)
            self.mock_redis.incr.assert_called_with("metadata:http://dataset/:di")

        with self.subTest("Wrong inputs"):
            with self.assertRaises(ValueError):
                self.counter_handler.increment_metadata_counter("di", None)

if __name__ == '__main__':
    unittest.main()
