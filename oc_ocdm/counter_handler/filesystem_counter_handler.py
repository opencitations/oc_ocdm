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
from __future__ import annotations

import os
from shutil import copymode, move
from tempfile import mkstemp
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import BinaryIO, Tuple, List, Dict

from oc_ocdm.counter_handler.counter_handler import CounterHandler


class FilesystemCounterHandler(CounterHandler):
    initial_line_len: int = 3
    trailing_char: str = " "

    def __init__(self, info_dir: str) -> None:
        if info_dir is None or len(info_dir) <= 0:
            raise ValueError("info_dir parameter is required!")

        if info_dir[-1] != os.sep:
            info_dir += os.sep

        self.info_dir: str = info_dir
        self.datasets_dir: str = info_dir + 'datasets' + os.sep
        self.short_names: List[str] = ["an", "ar", "be", "br", "ci", "de", "id", "pl", "ra", "re", "rp"]
        self.metadata_short_names: List[str] = ["di"]
        self.info_files: Dict[str, str] = {key: ("info_file_" + key + ".txt")
                                           for key in self.short_names}
        self.prov_files: Dict[str, str] = {key: ("prov_file_" + key + ".txt")
                                           for key in self.short_names}

    def set_counter(self, new_value: int, entity_short_name: str, prov_short_name: str = "",
                    identifier: int = 1) -> None:
        if new_value < 0:
            raise ValueError("new_value must be a non negative integer!")

        if prov_short_name == "se":
            file_path: str = self.get_prov_path(entity_short_name)
        else:
            file_path: str = self.get_info_path(entity_short_name)
        self._set_number(new_value, file_path, identifier)

    def read_counter(self, entity_short_name: str, prov_short_name: str = "", identifier: int = 1) -> int:
        if prov_short_name == "se":
            file_path: str = self.get_prov_path(entity_short_name)
        else:
            file_path: str = self.get_info_path(entity_short_name)
        return self._read_number(file_path, identifier)[0]

    def increment_counter(self, entity_short_name: str, prov_short_name: str = "", identifier: int = 1) -> int:
        if prov_short_name == "se":
            file_path: str = self.get_prov_path(entity_short_name)
        else:
            file_path: str = self.get_info_path(entity_short_name)
        return self._add_number(file_path, identifier)

    def get_info_path(self, short_name: str) -> str:
        return self.info_dir + self.info_files[short_name]

    def get_prov_path(self, short_name: str) -> str:
        return self.info_dir + self.prov_files[short_name]

    def get_metadata_path(self, short_name: str, dataset_name: str) -> str:
        return self.datasets_dir + dataset_name + os.sep + 'metadata_' + short_name + '.txt'

    def _read_number(self, file_path: str, line_number: int) -> Tuple[int, int]:
        if line_number <= 0:
            raise ValueError("line_number must be a positive non-zero integer number!")

        cur_number: int = 0
        cur_line_len: int = 0
        try:
            with open(file_path, "rb") as file:
                cur_line_len = self._get_line_len(file)
                line_offset = (line_number - 1) * cur_line_len
                file.seek(line_offset)
                line = file.readline(cur_line_len).decode("ascii")
                cur_number = int(line.rstrip(self.trailing_char + "\n"))
        except ValueError:
            cur_number = 0
        except Exception as e:
            print(e)

        return cur_number, cur_line_len

    def _add_number(self, file_path: str, line_number: int = 1) -> int:
        if line_number <= 0:
            raise ValueError("line_number must be a positive non-zero integer number!")

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        if not os.path.isfile(file_path):
            with open(file_path, "wb") as file:
                first_line: str = self.trailing_char * (self.initial_line_len - 1) + "\n"
                file.write(first_line.encode("ascii"))

        cur_number, cur_line_len = self._read_number(file_path, line_number)
        cur_number += 1

        cur_number_len: int = len(str(cur_number)) + 1
        if cur_number_len > cur_line_len:
            self._increase_line_len(file_path, new_length=cur_number_len)
            cur_line_len = cur_number_len

        with open(file_path, "r+b") as file:
            line_offset: int = (line_number - 1) * cur_line_len
            file.seek(line_offset)
            line: str = str(cur_number).ljust(cur_line_len - 1, self.trailing_char) + "\n"
            file.write(line.encode("ascii"))
            file.seek(-cur_line_len, os.SEEK_CUR)
            self._fix_previous_lines(file, cur_line_len)
        return cur_number

    def _set_number(self, new_value: int, file_path: str, line_number: int = 1) -> None:
        if new_value < 0:
            raise ValueError("new_value must be a non negative integer!")

        if line_number <= 0:
            raise ValueError("line_number must be a positive non-zero integer number!")

        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        if not os.path.isfile(file_path):
            with open(file_path, "wb") as file:
                first_line: str = self.trailing_char * (self.initial_line_len - 1) + "\n"
                file.write(first_line.encode("ascii"))

        cur_line_len = self._read_number(file_path, line_number)[1]

        cur_number_len: int = len(str(new_value)) + 1
        if cur_number_len > cur_line_len:
            self._increase_line_len(file_path, new_length=cur_number_len)
            cur_line_len = cur_number_len

        with open(file_path, "r+b") as file:
            line_offset: int = (line_number - 1) * cur_line_len
            file.seek(line_offset)
            line: str = str(new_value).ljust(cur_line_len - 1, self.trailing_char) + "\n"
            file.write(line.encode("ascii"))
            file.seek(-cur_line_len, os.SEEK_CUR)
            self._fix_previous_lines(file, cur_line_len)

    @staticmethod
    def _get_line_len(file: BinaryIO) -> int:
        cur_char: str = file.read(1).decode("ascii")
        count: int = 1
        while cur_char is not None and len(cur_char) == 1 and cur_char != "\0":
            cur_char = file.read(1).decode("ascii")
            count += 1
            if cur_char == "\n":
                break

        # Undo I/O pointer updates
        file.seek(0)

        if cur_char is None:
            raise EOFError("Reached end-of-file without encountering a line separator!")
        elif cur_char == "\0":
            raise ValueError("Encountered a NULL byte!")
        else:
            return count

    def _increase_line_len(self, file_path: str, new_length: int = 0) -> None:
        if new_length <= 0:
            raise ValueError("new_length must be a positive non-zero integer number!")

        with open(file_path, "rb") as cur_file:
            if self._get_line_len(cur_file) >= new_length:
                raise ValueError("Current line length is greater than new_length!")

        fh, abs_path = mkstemp()
        with os.fdopen(fh, "wb") as new_file:
            with open(file_path, "rt", encoding="ascii") as old_file:
                for line in old_file:
                    number: str = line.rstrip(self.trailing_char + "\n")
                    new_line: str = str(number).ljust(new_length - 1, self.trailing_char) + "\n"
                    new_file.write(new_line.encode("ascii"))

        # Copy the file permissions from the old file to the new file
        copymode(file_path, abs_path)

        # Replace original file
        os.remove(file_path)
        move(abs_path, file_path)

    @staticmethod
    def _is_a_valid_line(buf: bytes) -> bool:
        string: str = buf.decode("ascii")
        return (string[-1] == "\n") and ("\0" not in string[:-1])

    def _fix_previous_lines(self, file: BinaryIO, line_len: int) -> None:
        if line_len < self.initial_line_len:
            raise ValueError("line_len should be at least %d!" % self.initial_line_len)

        while file.tell() >= line_len:
            file.seek(-line_len, os.SEEK_CUR)
            buf: bytes = file.read(line_len)
            if self._is_a_valid_line(buf) or len(buf) < line_len:
                break
            else:
                file.seek(-line_len, os.SEEK_CUR)
                fixed_line: str = (self.trailing_char * (line_len - 1)) + "\n"
                file.write(fixed_line.encode("ascii"))
                file.seek(-line_len, os.SEEK_CUR)

    def set_metadata_counter(self, new_value: int, entity_short_name: str, dataset_name: str) -> None:
        if new_value < 0:
            raise ValueError("new_value must be a non negative integer!")

        if dataset_name is None:
            raise ValueError("dataset_name must be provided!")

        if entity_short_name not in self.metadata_short_names:
            raise ValueError("entity_short_name is not a known metadata short name!")

        file_path: str = self.get_metadata_path(entity_short_name, dataset_name)
        return self._set_number(new_value, file_path, 1)

    def read_metadata_counter(self, entity_short_name: str, dataset_name: str) -> int:
        if dataset_name is None:
            raise ValueError("dataset_name must be provided!")

        if entity_short_name not in self.metadata_short_names:
            raise ValueError("entity_short_name is not a known metadata short name!")

        file_path: str = self.get_metadata_path(entity_short_name, dataset_name)
        return self._read_number(file_path, 1)[0]

    def increment_metadata_counter(self, entity_short_name: str, dataset_name: str) -> int:
        if dataset_name is None:
            raise ValueError("dataset_name must be provided!")

        if entity_short_name not in self.metadata_short_names:
            raise ValueError("entity_short_name is not a known metadata short name!")

        file_path: str = self.get_metadata_path(entity_short_name, dataset_name)
        return self._add_number(file_path, 1)
