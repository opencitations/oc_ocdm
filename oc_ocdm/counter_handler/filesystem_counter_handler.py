#!/usr/bin/python

# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
# SPDX-FileCopyrightText: 2024-2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

from oc_ocdm.counter_handler.counter_handler import CounterHandler
from oc_ocdm.support.support import is_string_empty


class FilesystemCounterHandler(CounterHandler):
    """A concrete implementation of the ``CounterHandler`` interface that persistently stores the counter values within the filesystem.

    Counter data is loaded into RAM on first access per supplier prefix (lazy loading) and written back to disk only when ``flush()`` is called."""

    def __init__(self, info_dir: str, supplier_prefix: str = "") -> None:
        """
        Constructor of the ``FilesystemCounterHandler`` class.

        :param info_dir: The path to the folder that does/will contain the counter values.
        :type info_dir: str
        :raises ValueError: if ``info_dir`` is None or an empty string.
        """
        if info_dir is None or is_string_empty(info_dir):
            raise ValueError("info_dir parameter is required!")

        if info_dir[-1] != os.sep:
            info_dir += os.sep

        self.info_dir: str = info_dir
        self.supplier_prefix: str = supplier_prefix
        self.datasets_dir: str = info_dir + "datasets" + os.sep
        self.short_names: List[str] = ["an", "ar", "be", "br", "ci", "de", "id", "pl", "ra", "re", "rp"]
        self.metadata_short_names: List[str] = ["di"]
        self.info_files: Dict[str, str] = {key: ("info_file_" + key + ".txt") for key in self.short_names}
        self.prov_files: Dict[str, str] = {key: ("prov_file_" + key + ".txt") for key in self.short_names}

        self._cache: Dict[str, List[int]] = {}
        self._dirty: set[str] = set()
        self._loaded_dirs: set[str] = set()

        self._ensure_loaded(supplier_prefix)

    def __del__(self):
        try:
            self.flush()
        except Exception:
            pass

    def _get_prefix_dir(self, supplier_prefix: str) -> str:
        sp = "" if supplier_prefix is None else supplier_prefix
        if sp == self.supplier_prefix or not self.supplier_prefix:
            return self.info_dir
        return self.info_dir.replace(self.supplier_prefix, sp, 1)

    def _ensure_loaded(self, supplier_prefix: str) -> None:
        prefix_dir = self._get_prefix_dir(supplier_prefix)
        if prefix_dir in self._loaded_dirs:
            return
        if not os.path.isdir(prefix_dir):
            self._loaded_dirs.add(prefix_dir)
            return
        for filename in os.listdir(prefix_dir):
            if not filename.endswith(".txt"):
                continue
            if not (filename.startswith("info_file_") or filename.startswith("prov_file_")):
                continue
            filepath = prefix_dir + filename
            with open(filepath, "r") as f:
                self._cache[filepath] = [int(line.rstrip("\n")) if line.rstrip("\n") else 0 for line in f]
        self._loaded_dirs.add(prefix_dir)

    def flush(self) -> None:
        for file_path in self._dirty:
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            cache_list = self._cache[file_path]
            with open(file_path, "w") as f:
                f.writelines(f"{v}\n" if v else "\n" for v in cache_list)
        self._dirty.clear()

    def set_counter(
        self,
        new_value: int,
        entity_short_name: str,
        prov_short_name: str = "",
        identifier: int = 1,
        supplier_prefix: str = "",
    ) -> None:
        """
        It allows to set the counter value of graph and provenance entities.

        :param new_value: The new counter value to be set
        :type new_value: int
        :param entity_short_name: The short name associated either to the type of the entity itself
         or, in case of a provenance entity, to the type of the relative graph entity.
        :type entity_short_name: str
        :param prov_short_name: In case of a provenance entity, the short name associated to the type
         of the entity itself. An empty string otherwise.
        :type prov_short_name: str
        :param identifier: In case of a provenance entity, the counter value that identifies the relative
          graph entity. The integer value '1' otherwise.
        :type identifier: int
        :raises ValueError: if ``new_value`` is a negative integer or ``identifier`` is less than or equal to zero.
        :return: None
        """
        if new_value < 0:
            raise ValueError("new_value must be a non negative integer!")
        self._ensure_loaded(supplier_prefix)
        if prov_short_name == "se":
            file_path: str = self._get_prov_path(entity_short_name, supplier_prefix)
        else:
            file_path: str = self._get_info_path(entity_short_name, supplier_prefix)
        self._set_number(new_value, file_path, identifier)

    def set_counters_batch(self, updates: Dict[Tuple[str, str], Dict[int, int]], supplier_prefix: str) -> None:
        """
        Updates counters in batch for multiple files.
        `updates` is a dictionary where the key is a tuple (entity_short_name, prov_short_name)
        and the value is a dictionary of line numbers to new counter values.
        """
        self._ensure_loaded(supplier_prefix)
        for (entity_short_name, prov_short_name), file_updates in updates.items():
            file_path = (
                self._get_prov_path(entity_short_name, supplier_prefix)
                if prov_short_name == "se"
                else self._get_info_path(entity_short_name, supplier_prefix)
            )
            self._set_numbers(file_path, file_updates)

    def _set_numbers(self, file_path: str, updates: Dict[int, int]) -> None:
        """
        Apply multiple counter updates to a single file.
        `updates` is a dictionary where the key is the line number (identifier)
        and the value is the new counter value.
        """
        if file_path not in self._cache:
            self._cache[file_path] = [0]
        cache_list = self._cache[file_path]
        needed = max(updates.keys()) + 1 - len(cache_list)
        if needed > 0:
            cache_list.extend([0] * needed)
        for line_number, new_value in updates.items():
            cache_list[line_number - 1] = new_value
        self._dirty.add(file_path)

    def read_counter(
        self, entity_short_name: str, prov_short_name: str = "", identifier: int = 1, supplier_prefix: str = ""
    ) -> int:
        """
        It allows to read the counter value of graph and provenance entities.

        :param entity_short_name: The short name associated either to the type of the entity itself
         or, in case of a provenance entity, to the type of the relative graph entity.
        :type entity_short_name: str
        :param prov_short_name: In case of a provenance entity, the short name associated to the type
         of the entity itself. An empty string otherwise.
        :type prov_short_name: str
        :param identifier: In case of a provenance entity, the counter value that identifies the relative
          graph entity. The integer value '1' otherwise.
        :type identifier: int
        :raises ValueError: if ``identifier`` is less than or equal to zero.
        :return: The requested counter value.
        """
        self._ensure_loaded(supplier_prefix)
        if prov_short_name == "se":
            file_path: str = self._get_prov_path(entity_short_name, supplier_prefix)
        else:
            file_path: str = self._get_info_path(entity_short_name, supplier_prefix)
        return self._read_number(file_path, identifier)

    def increment_counter(
        self, entity_short_name: str, prov_short_name: str = "", identifier: int = 1, supplier_prefix: str = ""
    ) -> int:
        """
        It allows to increment the counter value of graph and provenance entities by one unit.

        :param entity_short_name: The short name associated either to the type of the entity itself
         or, in case of a provenance entity, to the type of the relative graph entity.
        :type entity_short_name: str
        :param prov_short_name: In case of a provenance entity, the short name associated to the type
         of the entity itself. An empty string otherwise.
        :type prov_short_name: str
        :param identifier: In case of a provenance entity, the counter value that identifies the relative
          graph entity. The integer value '1' otherwise.
        :type identifier: int
        :raises ValueError: if ``identifier`` is less than or equal to zero.
        :return: The newly-updated (already incremented) counter value.
        """
        self._ensure_loaded(supplier_prefix)
        if prov_short_name == "se":
            file_path: str = self._get_prov_path(entity_short_name, supplier_prefix)
        else:
            file_path: str = self._get_info_path(entity_short_name, supplier_prefix)
        return self._add_number(file_path, identifier)

    def _get_info_path(self, short_name: str, supplier_prefix: str) -> str:
        return self._get_prefix_dir(supplier_prefix) + self.info_files[short_name]

    def _get_prov_path(self, short_name: str, supplier_prefix: str) -> str:
        return self._get_prefix_dir(supplier_prefix) + self.prov_files[short_name]

    def _get_metadata_path(self, short_name: str, dataset_name: str) -> str:
        return self.datasets_dir + dataset_name + os.sep + "metadata_" + short_name + ".txt"

    def _read_number(self, file_path: str, line_number: int) -> int:
        if line_number <= 0:
            raise ValueError("line_number must be a positive non-zero integer number!")
        if file_path in self._cache:
            idx = line_number - 1
            cache_list = self._cache[file_path]
            if idx < len(cache_list):
                return cache_list[idx]
            return 0
        self._cache[file_path] = [0]
        return 0

    def _add_number(self, file_path: str, line_number: int = 1) -> int:
        if line_number <= 0:
            raise ValueError("line_number must be a positive non-zero integer number!")
        current_value = self._read_number(file_path, line_number)
        new_value = current_value + 1
        self._set_number(new_value, file_path, line_number)
        return new_value

    def _set_number(self, new_value: int, file_path: str, line_number: int = 1) -> None:
        if new_value < 0:
            raise ValueError("new_value must be a non negative integer!")
        if line_number <= 0:
            raise ValueError("line_number must be a positive non-zero integer number!")
        if file_path not in self._cache:
            self._cache[file_path] = [0]
        cache_list = self._cache[file_path]
        needed = line_number - len(cache_list)
        if needed > 0:
            cache_list.extend([0] * needed)
        cache_list[line_number - 1] = new_value
        self._dirty.add(file_path)

    def set_metadata_counter(self, new_value: int, entity_short_name: str, dataset_name: str) -> None:
        """
        It allows to set the counter value of metadata entities.

        :param new_value: The new counter value to be set
        :type new_value: int
        :param entity_short_name: The short name associated either to the type of the entity itself.
        :type entity_short_name: str
        :param dataset_name: In case of a ``Dataset``, its name. Otherwise, the name of the relative dataset.
        :type dataset_name: str
        :raises ValueError: if ``new_value`` is a negative integer, ``dataset_name`` is None or
          ``entity_short_name`` is not a known metadata short name.
        :return: None
        """
        if new_value < 0:
            raise ValueError("new_value must be a non negative integer!")
        if dataset_name is None:
            raise ValueError("dataset_name must be provided!")
        if entity_short_name not in self.metadata_short_names:
            raise ValueError("entity_short_name is not a known metadata short name!")
        file_path: str = self._get_metadata_path(entity_short_name, dataset_name)
        return self._set_number(new_value, file_path, 1)

    def read_metadata_counter(self, entity_short_name: str, dataset_name: str) -> int:
        """
        It allows to read the counter value of metadata entities.

        :param entity_short_name: The short name associated either to the type of the entity itself.
        :type entity_short_name: str
        :param dataset_name: In case of a ``Dataset``, its name. Otherwise, the name of the relative dataset.
        :type dataset_name: str
        :raises ValueError: if ``dataset_name`` is None or ``entity_short_name`` is not a known metadata short name.
        :return: The requested counter value.
        """
        if dataset_name is None:
            raise ValueError("dataset_name must be provided!")
        if entity_short_name not in self.metadata_short_names:
            raise ValueError("entity_short_name is not a known metadata short name!")
        file_path: str = self._get_metadata_path(entity_short_name, dataset_name)
        return self._read_number(file_path, 1)

    def increment_metadata_counter(self, entity_short_name: str, dataset_name: str) -> int:
        """
        It allows to increment the counter value of metadata entities by one unit.

        :param entity_short_name: The short name associated either to the type of the entity itself.
        :type entity_short_name: str
        :param dataset_name: In case of a ``Dataset``, its name. Otherwise, the name of the relative dataset.
        :type dataset_name: str
        :raises ValueError: if ``dataset_name`` is None or ``entity_short_name`` is not a known metadata short name.
        :return: The newly-updated (already incremented) counter value.
        """
        if dataset_name is None:
            raise ValueError("dataset_name must be provided!")
        if entity_short_name not in self.metadata_short_names:
            raise ValueError("entity_short_name is not a known metadata short name!")
        file_path: str = self._get_metadata_path(entity_short_name, dataset_name)
        return self._add_number(file_path, 1)
