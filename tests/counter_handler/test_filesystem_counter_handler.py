#!/usr/bin/python

# SPDX-FileCopyrightText: 2025 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
import os
import shutil
import tempfile
import unittest

from oc_ocdm.counter_handler.filesystem_counter_handler import FilesystemCounterHandler


class TestFilesystemCounterHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.info_dir = "./info_dir/"
        cls.counter_handler = FilesystemCounterHandler(cls.info_dir)

        cls.file_path = cls.info_dir + "test_file.txt"
        if not os.path.exists(os.path.dirname(cls.file_path)):
            os.makedirs(os.path.dirname(cls.file_path))

    def setUp(self):
        with open(self.file_path, "w") as file:
            file.write("\n")
        self.counter_handler._cache[self.file_path] = [0]
        self.counter_handler._dirty.discard(self.file_path)

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

    def test_flush_persists_to_disk(self):
        self.counter_handler._set_number(99, self.file_path, 1)
        self.assertIn(self.file_path, self.counter_handler._dirty)
        self.counter_handler.flush()
        self.assertEqual(len(self.counter_handler._dirty), 0)
        with open(self.file_path, "r") as f:
            lines = f.readlines()
        self.assertEqual(lines[0].strip(), "99")

    def test_flush_writes_empty_lines_for_zero(self):
        self.counter_handler._set_number(5, self.file_path, 3)
        self.counter_handler.flush()
        with open(self.file_path, "r") as f:
            lines = f.readlines()
        self.assertEqual(lines[0], "\n")
        self.assertEqual(lines[1], "\n")
        self.assertEqual(lines[2].strip(), "5")

    def test_lazy_loading_reads_existing_files(self):
        tmp_dir = tempfile.mkdtemp() + os.sep
        info_path = tmp_dir + "info_file_br.txt"
        with open(info_path, "w") as f:
            f.write("42\n")
        handler = FilesystemCounterHandler(tmp_dir)
        self.assertEqual(handler.read_counter("br"), 42)
        shutil.rmtree(tmp_dir)

    def test_read_number_beyond_cache_returns_zero(self):
        self.counter_handler._set_number(5, self.file_path, 1)
        result = self.counter_handler._read_number(self.file_path, 100)
        self.assertEqual(result, 0)

    def test_del_triggers_flush(self):
        tmp_dir = tempfile.mkdtemp() + os.sep
        handler = FilesystemCounterHandler(tmp_dir)
        handler.set_counter(77, "br")
        info_path = tmp_dir + "info_file_br.txt"
        del handler
        with open(info_path, "r") as f:
            self.assertEqual(f.readline().strip(), "77")
        shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
