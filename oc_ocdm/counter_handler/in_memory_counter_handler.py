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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Dict

from oc_ocdm.counter_handler.counter_handler import CounterHandler


class InMemoryCounterHandler(CounterHandler):
    """A concrete implementation of the ``CounterHandler`` interface that temporarily stores
    the counter values in the volatile system memory."""

    def __init__(self) -> None:
        """
        Constructor of the ``InMemoryCounterHandler`` class.
        """
        self.short_names: List[str] = ["an", "ar", "be", "br", "ci", "de", "id", "pl", "ra", "re", "rp"]
        self.prov_short_names: List[str] = ["se"]
        self.metadata_short_names: List[str] = ["di"]
        self.entity_counters: Dict[str, int] = {key: 0 for key in self.short_names}
        self.prov_counters: Dict[str, Dict[str, List[int]]] = {key1: {key2: [] for key2 in self.prov_short_names}
                                                               for key1 in self.short_names}
        self.metadata_counters: Dict[str, Dict[str, int]] = {}

    def set_counter(self, new_value: int, entity_short_name: str, prov_short_name: str = "",
                    identifier: int = 1, supplier_prefix: str = "") -> None:
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
        :raises ValueError: if ``new_value`` is a negative integer, ``identifier`` is less than or equal to zero,
          ``entity_short_name`` is not a known short name or ``prov_short_name`` is not a known provenance short name.
        :return: None
        """
        if new_value < 0:
            raise ValueError("new_value must be a non negative integer!")

        if entity_short_name not in self.short_names:
            raise ValueError("entity_short_name is not a known short name!")

        if prov_short_name != "":
            if prov_short_name not in self.prov_short_names:
                raise ValueError("prov_short_name is not a known provenance short name!")
            if identifier <= 0:
                raise ValueError("identifier must be a positive non-zero integer number!")

        identifier -= 1  # Internally we use zero_indexing!
        if prov_short_name in self.prov_short_names:
            # It's a provenance entity!
            missing_counters: int = identifier - (len(self.prov_counters[entity_short_name][prov_short_name]) - 1)
            if missing_counters > 0:
                self.prov_counters[entity_short_name][prov_short_name] += [0] * missing_counters
            self.prov_counters[entity_short_name][prov_short_name][identifier] = new_value
        else:
            # It's an entity!
            self.entity_counters[entity_short_name] = new_value

    def read_counter(self, entity_short_name: str, prov_short_name: str = "", identifier: int = 1, supplier_prefix: str = "") -> int:
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
        :raises ValueError: if ``identifier`` is less than or equal to zero, ``entity_short_name``
          is not a known short name or ``prov_short_name`` is not a known provenance short name.
        :return: The requested counter value.
        """
        if entity_short_name not in self.short_names:
            raise ValueError("entity_short_name is not a known short name!")

        if prov_short_name != "":
            if prov_short_name not in self.prov_short_names:
                raise ValueError("prov_short_name is not a known provenance short name!")
            if identifier <= 0:
                raise ValueError("identifier must be a positive non-zero integer number!")

        identifier -= 1  # Internally we use zero_indexing!
        if prov_short_name in self.prov_short_names:
            # It's a provenance entity!
            missing_counters: int = identifier - (len(self.prov_counters[entity_short_name][prov_short_name]) - 1)
            if missing_counters > 0:
                self.prov_counters[entity_short_name][prov_short_name] += [0] * missing_counters
            return self.prov_counters[entity_short_name][prov_short_name][identifier]
        else:
            # It's an entity!
            return self.entity_counters[entity_short_name]

    def increment_counter(self, entity_short_name: str, prov_short_name: str = "", identifier: int = 1, supplier_prefix: str = "") -> int:
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
        :raises ValueError: if ``identifier`` is less than or equal to zero, ``entity_short_name``
          is not a known short name or ``prov_short_name`` is not a known provenance short name.
        :return: The newly-updated (already incremented) counter value.
        """
        if entity_short_name not in self.short_names:
            raise ValueError("entity_short_name is not a known short name!")

        if prov_short_name != "":
            if prov_short_name not in self.prov_short_names:
                raise ValueError("prov_short_name is not a known provenance short name!")
            if identifier <= 0:
                raise ValueError("identifier must be a positive non-zero integer number!")

        identifier -= 1  # Internally we use zero_indexing!
        if prov_short_name in self.prov_short_names:
            # It's a provenance entity!
            missing_counters: int = identifier - (len(self.prov_counters[entity_short_name][prov_short_name]) - 1)
            if missing_counters > 0:
                self.prov_counters[entity_short_name][prov_short_name] += [0]*missing_counters
            self.prov_counters[entity_short_name][prov_short_name][identifier] += 1
            return self.prov_counters[entity_short_name][prov_short_name][identifier]
        else:
            # It's an entity!
            self.entity_counters[entity_short_name] += 1
            return self.entity_counters[entity_short_name]

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

        if dataset_name not in self.metadata_counters:
            self.metadata_counters[dataset_name] = {key: 0 for key in self.metadata_short_names}

        self.metadata_counters[dataset_name][entity_short_name] = new_value

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

        if dataset_name not in self.metadata_counters:
            return 0
        else:
            if entity_short_name not in self.metadata_counters[dataset_name]:
                return 0
            else:
                return self.metadata_counters[dataset_name][entity_short_name]

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

        if dataset_name not in self.metadata_counters:
            self.metadata_counters[dataset_name] = {key: 0 for key in self.metadata_short_names}

        self.metadata_counters[dataset_name][entity_short_name] += 1
        return self.metadata_counters[dataset_name][entity_short_name]
