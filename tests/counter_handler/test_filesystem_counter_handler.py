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

from oc_ocdm.counter_handler.filesystem_counter_handler import FilesystemCounterHandler


class TestFilesystemCounterHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.info_dir = './info_dir/'
        cls.counter_handler = FilesystemCounterHandler(cls.info_dir)

        cls.file_path = cls.info_dir + 'test_file.txt'
        if not os.path.exists(os.path.dirname(cls.file_path)):
            os.makedirs(os.path.dirname(cls.file_path))

    def setUp(self):
        # Reset test file content:
        with open(self.file_path, 'w') as file:
            file.write("\n")

    def test_set_number(self):
        number = 18
        num_of_line = 35
        self.counter_handler._set_number(number, self.file_path, num_of_line)
        read_number = self.counter_handler._read_number(self.file_path, num_of_line)
        self.assertEqual(read_number, number)
        self.assertRaises(ValueError, self.counter_handler._set_number, -1, self.file_path, 1)
        self.assertRaises(ValueError, self.counter_handler._set_number, 1, self.file_path, -1)

    def test_read_number(self):
        number = 18
        num_of_line = 35
        self.counter_handler._set_number(number, self.file_path, num_of_line)
        
        read_number = self.counter_handler._read_number(self.file_path, num_of_line)
        self.assertEqual(read_number, number)

        self.assertRaises(ValueError, self.counter_handler._read_number, self.file_path, -1)

    def test_add_number(self):
        number = 18
        num_of_line = 35
        self.counter_handler._set_number(number, self.file_path, num_of_line)

        read_number = self.counter_handler._add_number(self.file_path, num_of_line)
        self.assertEqual(read_number, number + 1)

        self.assertRaises(ValueError, self.counter_handler._add_number, self.file_path, -1)

    def test_set_counters_batch(self):
        updates = {("br", "se"): {1: 10, 2: 20, 3: 30}}
        self.counter_handler.set_counters_batch(updates, "")
        
        for line_number, expected_value in updates[("br", "se")].items():
            read_value = self.counter_handler.read_counter("br", "se", line_number)
            self.assertEqual(read_value, expected_value)

    def test_read_metadata_counter(self):
        dataset_name: str = "http://dataset/"
        self.assertRaises(ValueError, self.counter_handler.read_metadata_counter, "xyz", dataset_name)
        self.assertRaises(ValueError, self.counter_handler.read_metadata_counter, "di", None)

    def test_increment_metadata_counter(self):
        dataset_name: str = "http://dataset/"
        self.assertRaises(ValueError, self.counter_handler.increment_metadata_counter, "xyz", dataset_name)
        self.assertRaises(ValueError, self.counter_handler.increment_metadata_counter, "di", None)

    def test_set_metadata_counter(self):
        dataset_name = "http://dataset/"
        entity_short_name = "di"
        value = 42
        
        self.counter_handler.set_metadata_counter(value, entity_short_name, dataset_name)
        read_value = self.counter_handler.read_metadata_counter(entity_short_name, dataset_name)
        self.assertEqual(read_value, value)


if __name__ == '__main__':
    unittest.main()
