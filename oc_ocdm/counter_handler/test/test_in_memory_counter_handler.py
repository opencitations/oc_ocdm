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

from oc_ocdm.counter_handler.in_memory_counter_handler import InMemoryCounterHandler


class TestFilesystemCounterHandler(unittest.TestCase):

    def setUp(self) -> None:
        self.counter_handler = InMemoryCounterHandler()

    def test_set_counter(self):
        with self.subTest("Set BR counter"):
            count = 99
            self.counter_handler.entity_counters["br"] = count

            new_count = 205
            result = self.counter_handler.set_counter(new_count, "br")
            self.assertIsNone(result)
            self.assertEqual(self.counter_handler.entity_counters["br"], new_count)
        with self.subTest("Set BR counter, long number"):
            long_count = 2**256
            self.counter_handler.entity_counters["br"] = long_count

            new_count = 2**512
            result = self.counter_handler.set_counter(new_count, "br")
            self.assertIsNone(result)
            self.assertEqual(self.counter_handler.entity_counters["br"], new_count)
        with self.subTest("Set SE counter"):
            count = 99
            identifier = 1234
            counter_list = [0]*identifier
            counter_list[-1] = count
            self.counter_handler.prov_counters["br"]["se"] = counter_list

            new_count = 205
            result = self.counter_handler.set_counter(new_count, "br", "se", identifier)
            self.assertIsNone(result)
            self.assertEqual(self.counter_handler.prov_counters["br"]["se"][identifier - 1], new_count)
        with self.subTest("Set SE counter, long number"):
            long_count = 2**256
            identifier = 1234
            counter_list = [0]*identifier
            counter_list[-1] = long_count
            self.counter_handler.prov_counters["br"]["se"] = counter_list

            new_count = 2**512
            result = self.counter_handler.set_counter(new_count, "br", "se", identifier)
            self.assertIsNone(result)
            self.assertEqual(self.counter_handler.prov_counters["br"]["se"][identifier - 1], new_count)
        with self.subTest("Wrong inputs"):
            self.assertRaises(ValueError, self.counter_handler.set_counter, -1, "xyz")
            self.assertRaises(ValueError, self.counter_handler.set_counter, 1, "xyz")
            self.assertRaises(ValueError, self.counter_handler.set_counter, 1, "br", "xyz")
            self.assertRaises(ValueError, self.counter_handler.set_counter, 1, "br", "se", -1)

    def test_read_counter(self):
        with self.subTest("Read BR counter"):
            count = 99
            self.counter_handler.entity_counters["br"] = count

            result = self.counter_handler.read_counter("br")
            self.assertIsNotNone(result)
            self.assertEqual(result, count)
        with self.subTest("Read BR counter, long number"):
            long_count = 2**256
            self.counter_handler.entity_counters["br"] = long_count

            result = self.counter_handler.read_counter("br")
            self.assertIsNotNone(result)
            self.assertEqual(result, long_count)
        with self.subTest("Read SE counter"):
            count = 99
            identifier = 1234
            counter_list = [0]*identifier
            counter_list[-1] = count
            self.counter_handler.prov_counters["br"]["se"] = counter_list

            result = self.counter_handler.read_counter("br", "se", identifier)
            self.assertIsNotNone(result)
            self.assertEqual(result, count)
        with self.subTest("Read SE counter, long number"):
            long_count = 2**256
            identifier = 1234
            counter_list = [0]*identifier
            counter_list[-1] = long_count
            self.counter_handler.prov_counters["br"]["se"] = counter_list

            result = self.counter_handler.read_counter("br", "se", identifier)
            self.assertIsNotNone(result)
            self.assertEqual(result, long_count)
        with self.subTest("Wrong inputs"):
            self.assertRaises(ValueError, self.counter_handler.read_counter, "xyz")
            self.assertRaises(ValueError, self.counter_handler.read_counter, "br", "xyz")
            self.assertRaises(ValueError, self.counter_handler.read_counter, "br", "se", -1)

    def test_increment_counter(self):
        with self.subTest("Increment BR counter"):
            count = 99
            self.counter_handler.entity_counters["br"] = count

            result = self.counter_handler.increment_counter("br")
            self.assertIsNotNone(result)
            self.assertEqual(result, count + 1)
            self.assertEqual(self.counter_handler.entity_counters["br"], count + 1)
        with self.subTest("Increment BR counter, long number"):
            long_count = 2**256
            self.counter_handler.entity_counters["br"] = long_count

            result = self.counter_handler.increment_counter("br")
            self.assertIsNotNone(result)
            self.assertEqual(result, long_count + 1)
            self.assertEqual(self.counter_handler.entity_counters["br"], long_count + 1)
        with self.subTest("Increment SE counter"):
            count = 99
            identifier = 1234
            counter_list = [0]*identifier
            counter_list[-1] = count
            self.counter_handler.prov_counters["br"]["se"] = counter_list

            result = self.counter_handler.increment_counter("br", "se", identifier)
            self.assertIsNotNone(result)
            self.assertEqual(result, count + 1)
            self.assertEqual(self.counter_handler.prov_counters["br"]["se"][identifier - 1], count + 1)
        with self.subTest("Increment SE counter, long number"):
            long_count = 2**256
            identifier = 1234
            counter_list = [0]*identifier
            counter_list[-1] = long_count
            self.counter_handler.prov_counters["br"]["se"] = counter_list

            result = self.counter_handler.increment_counter("br", "se", identifier)
            self.assertIsNotNone(result)
            self.assertEqual(result, long_count + 1)
            self.assertEqual(self.counter_handler.prov_counters["br"]["se"][identifier - 1], long_count + 1)
        with self.subTest("Wrong inputs"):
            self.assertRaises(ValueError, self.counter_handler.increment_counter, "xyz")
            self.assertRaises(ValueError, self.counter_handler.increment_counter, "br", "xyz")
            self.assertRaises(ValueError, self.counter_handler.increment_counter, "br", "se", -1)

    def test_set_metadata_counter(self):
        dataset_name: str = "http://dataset/"
        with self.subTest("Set DI counter"):
            count = 99
            self.counter_handler.metadata_counters[dataset_name] = {"di": count}

            new_count = 205
            result = self.counter_handler.set_metadata_counter(new_count, "di", dataset_name)
            self.assertIsNone(result)
            self.assertEqual(self.counter_handler.metadata_counters[dataset_name]["di"], new_count)
        with self.subTest("Set DI counter, long number"):
            long_count = 2 ** 256
            self.counter_handler.metadata_counters[dataset_name] = {"di": long_count}

            new_count = 2**512
            result = self.counter_handler.set_metadata_counter(new_count, "di", dataset_name)
            self.assertIsNone(result)
            self.assertEqual(self.counter_handler.metadata_counters[dataset_name]["di"], new_count)
        with self.subTest("Wrong inputs"):
            self.assertRaises(ValueError, self.counter_handler.set_metadata_counter, -1, "xyz", dataset_name)
            self.assertRaises(ValueError, self.counter_handler.set_metadata_counter, 1, "xyz", dataset_name)
            self.assertRaises(ValueError, self.counter_handler.set_metadata_counter, 1, "di", None)

    def test_read_metadata_counter(self):
        dataset_name: str = "http://dataset/"
        with self.subTest("Read DI counter"):
            count = 99
            self.counter_handler.metadata_counters[dataset_name] = {"di": count}

            result = self.counter_handler.read_metadata_counter("di", dataset_name)
            self.assertIsNotNone(result)
            self.assertEqual(result, count)
        with self.subTest("Read DI counter, long number"):
            long_count = 2**256
            self.counter_handler.metadata_counters[dataset_name] = {"di": long_count}

            result = self.counter_handler.read_metadata_counter("di", dataset_name)
            self.assertIsNotNone(result)
            self.assertEqual(result, long_count)
        with self.subTest("Wrong inputs"):
            self.assertRaises(ValueError, self.counter_handler.read_metadata_counter, "xyz", dataset_name)
            self.assertRaises(ValueError, self.counter_handler.read_metadata_counter, "di", None)

    def test_increment_metadata_counter(self):
        dataset_name: str = "http://dataset/"
        with self.subTest("Increment DI counter"):
            count = 99
            self.counter_handler.metadata_counters[dataset_name] = {"di": count}

            result = self.counter_handler.increment_metadata_counter("di", dataset_name)
            self.assertIsNotNone(result)
            self.assertEqual(result, count + 1)
            self.assertEqual(self.counter_handler.metadata_counters[dataset_name]["di"], count + 1)
        with self.subTest("Increment DI counter, long number"):
            long_count = 2**256
            self.counter_handler.metadata_counters[dataset_name] = {"di": long_count}

            result = self.counter_handler.increment_metadata_counter("di", dataset_name)
            self.assertIsNotNone(result)
            self.assertEqual(result, long_count + 1)
            self.assertEqual(self.counter_handler.metadata_counters[dataset_name]["di"], long_count + 1)
        with self.subTest("Wrong inputs"):
            self.assertRaises(ValueError, self.counter_handler.increment_metadata_counter, "xyz", dataset_name)
            self.assertRaises(ValueError, self.counter_handler.increment_metadata_counter, "di", None)


if __name__ == '__main__':
    unittest.main()
