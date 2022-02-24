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

        if not os.path.isfile(cls.file_path):
            with open(cls.file_path, 'wb') as file:
                first_line = cls.counter_handler._trailing_char * (cls.counter_handler._initial_line_len - 1) + '\n'
                file.write(first_line.encode('ascii'))

    def setUp(self):
        # Reset test file content:
        with open(self.file_path, 'wb') as file:
            first_line = self.counter_handler._trailing_char * (self.counter_handler._initial_line_len - 1) + '\n'
            file.write(first_line.encode('ascii'))

    def test_get_line_len(self):
        with open(self.file_path, 'rb') as test_file:
            line_len = self.counter_handler._get_line_len(test_file)
            self.assertIsNotNone(line_len)
            self.assertEqual(line_len, self.counter_handler._initial_line_len)
            self.assertEqual(test_file.tell(), 0)

    def test_increase_line_len(self):
        increment = 1
        result = self.counter_handler._increase_line_len(self.file_path,
                                                         self.counter_handler._initial_line_len + increment)
        self.assertIsNone(result)
        with open(self.file_path, 'rt', encoding='ascii') as test_file:
            for line in test_file:
                self.assertEqual(len(line), self.counter_handler._initial_line_len + increment)

        self.assertRaises(ValueError, self.counter_handler._increase_line_len, self.file_path, -1)
        self.assertRaises(ValueError, self.counter_handler._increase_line_len, self.file_path,
                          self.counter_handler._initial_line_len - 1)

    def test_is_a_valid_line(self):
        with self.subTest("line is 'abc \\n'"):
            line = 'abc \n'.encode('ascii')
            result = self.counter_handler._is_a_valid_line(line)
            self.assertIsNotNone(result)
            self.assertTrue(result)
        with self.subTest("line is 'a\\0c \\n'"):
            line = 'a\0c \n'.encode('ascii')
            result = self.counter_handler._is_a_valid_line(line)
            self.assertIsNotNone(result)
            self.assertFalse(result)
        with self.subTest("line is 'abc'"):
            line = 'abc'.encode('ascii')
            result = self.counter_handler._is_a_valid_line(line)
            self.assertIsNotNone(result)
            self.assertFalse(result)
        with self.subTest("line is 'a\\0c'"):
            line = 'a\\0c'.encode('ascii')
            result = self.counter_handler._is_a_valid_line(line)
            self.assertIsNotNone(result)
            self.assertFalse(result)

    def test_fix_previous_lines(self):
        with open(self.file_path, 'wb') as test_file:
            num_lines = 10
            for i in range(0, num_lines):
                line = '\0' * self.counter_handler._initial_line_len
                test_file.write(line.encode('ascii'))
            last_line = '1'.ljust(self.counter_handler._initial_line_len - 1, self.counter_handler._trailing_char) + '\n'
            test_file.write(last_line.encode('ascii'))

        with open(self.file_path, 'r+b') as test_file:
            test_file.seek(self.counter_handler._initial_line_len * num_lines)
            result = self.counter_handler._fix_previous_lines(test_file, self.counter_handler._initial_line_len)
            self.assertIsNone(result)

        with open(self.file_path, 'rt', encoding='ascii') as test_file:
            count = 0
            for line in test_file:
                count += 1
                if count >= num_lines:
                    break
                self.assertTrue(self.counter_handler._is_a_valid_line(line.encode('ascii')))

    def test_set_number(self):
        number = 18
        with open(self.file_path, 'r+b') as test_file:
            num_of_line = 35
            test_file.seek(self.counter_handler._initial_line_len * (num_of_line - 1))
            line = str(number).ljust(self.counter_handler._initial_line_len - 1, self.counter_handler._trailing_char) + '\n'
            test_file.write(line.encode('ascii'))

        new_number = 205
        result = self.counter_handler._set_number(new_number, self.file_path, num_of_line)
        self.assertIsNone(result)
        with open(self.file_path, 'rt', encoding='ascii') as test_file:
            count = 0
            for line in test_file:
                count += 1
                if count >= num_of_line:
                    self.assertEqual(int(line), new_number)
                    break
                self.assertTrue(self.counter_handler._is_a_valid_line(line.encode('ascii')))

        self.assertRaises(ValueError, self.counter_handler._set_number, -1, self.file_path, 1)
        self.assertRaises(ValueError, self.counter_handler._set_number, 1, self.file_path, -1)

    def test_read_number(self):
        number = 18
        with open(self.file_path, 'r+b') as test_file:
            num_of_line = 35
            test_file.seek(self.counter_handler._initial_line_len * (num_of_line - 1))
            line = str(number).ljust(self.counter_handler._initial_line_len - 1, self.counter_handler._trailing_char) + '\n'
            test_file.write(line.encode('ascii'))

        read_number, line_len = self.counter_handler._read_number(self.file_path, num_of_line)
        self.assertIsNotNone(read_number)
        self.assertIsNotNone(line_len)
        self.assertEqual(read_number, number)
        self.assertEqual(line_len, self.counter_handler._initial_line_len)

        self.assertRaises(ValueError, self.counter_handler._read_number, self.file_path, -1)

    def test_add_number(self):
        number = 18
        with open(self.file_path, 'r+b') as test_file:
            num_of_line = 35
            test_file.seek(self.counter_handler._initial_line_len * (num_of_line - 1))
            line = str(number).ljust(self.counter_handler._initial_line_len - 1, self.counter_handler._trailing_char) + '\n'
            test_file.write(line.encode('ascii'))

        read_number = self.counter_handler._add_number(self.file_path, num_of_line)
        self.assertIsNotNone(read_number)
        self.assertEqual(read_number, number + 1)
        with open(self.file_path, 'rt', encoding='ascii') as test_file:
            count = 0
            for line in test_file:
                count += 1
                if count >= num_of_line:
                    break
                self.assertTrue(self.counter_handler._is_a_valid_line(line.encode('ascii')))

        self.assertRaises(ValueError, self.counter_handler._add_number, self.file_path, -1)

    def test_read_metadata_counter(self):
        dataset_name: str = "http://dataset/"
        self.assertRaises(ValueError, self.counter_handler.read_metadata_counter, "xyz", dataset_name)
        self.assertRaises(ValueError, self.counter_handler.read_metadata_counter, "di", None)

    def test_increment_metadata_counter(self):
        dataset_name: str = "http://dataset/"
        self.assertRaises(ValueError, self.counter_handler.increment_metadata_counter, "xyz", dataset_name)
        self.assertRaises(ValueError, self.counter_handler.increment_metadata_counter, "di", None)


if __name__ == '__main__':
    unittest.main()
