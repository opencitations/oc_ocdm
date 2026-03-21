#!/usr/bin/python

# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
# SPDX-FileCopyrightText: 2024 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod


class CounterHandler(ABC):
    """Abstract class representing the interface for every concrete counter handler."""

    @abstractmethod
    def set_counter(self, new_value: int, entity_short_name: str, prov_short_name: str = "",
                    identifier: int = 1, supplier_prefix: str = "") -> None:
        """
        Method signature for concrete implementations that allow setting the counter value
        of graph and provenance entities.

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
        :raises NotImplementedError: always
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def read_counter(self, entity_short_name: str, prov_short_name: str = "", identifier: int = 1, supplier_prefix: str = "") -> int:
        """
        Method signature for concrete implementations that allow reading the counter value
        of graph and provenance entities.

        :param entity_short_name: The short name associated either to the type of the entity itself
         or, in case of a provenance entity, to the type of the relative graph entity.
        :type entity_short_name: str
        :param prov_short_name: In case of a provenance entity, the short name associated to the type
         of the entity itself. An empty string otherwise.
        :type prov_short_name: str
        :param identifier: In case of a provenance entity, the counter value that identifies the relative
          graph entity. The integer value '1' otherwise.
        :type identifier: int
        :raises NotImplementedError: always
        :return: The requested counter value.
        """
        raise NotImplementedError

    @abstractmethod
    def increment_counter(self, entity_short_name: str, prov_short_name: str = "", identifier: int = 1, supplier_prefix: str = "") -> int:
        """
        Method signature for concrete implementations that allow incrementing by one unit
        the counter value of graph and provenance entities.

        :param entity_short_name: The short name associated either to the type of the entity itself
         or, in case of a provenance entity, to the type of the relative graph entity.
        :type entity_short_name: str
        :param prov_short_name: In case of a provenance entity, the short name associated to the type
         of the entity itself. An empty string otherwise.
        :type prov_short_name: str
        :param identifier: In case of a provenance entity, the counter value that identifies the relative
          graph entity. The integer value '1' otherwise.
        :type identifier: int
        :raises NotImplementedError: always
        :return: The newly-updated (already incremented) counter value.
        """
        raise NotImplementedError

    @abstractmethod
    def set_metadata_counter(self, new_value: int, entity_short_name: str, dataset_name: str) -> None:
        """
        Method signature for concrete implementations that allow setting the counter value
        of metadata entities.

        :param new_value: The new counter value to be set
        :type new_value: int
        :param entity_short_name: The short name associated either to the type of the entity itself.
        :type entity_short_name: str
        :param dataset_name: In case of a ``Dataset``, its name. Otherwise, the name of the relative dataset.
        :type dataset_name: str
        :raises NotImplementedError: always
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def read_metadata_counter(self, entity_short_name: str, dataset_name: str) -> int:
        """
        Method signature for concrete implementations that allow reading the counter value
        of metadata entities.

        :param entity_short_name: The short name associated either to the type of the entity itself.
        :type entity_short_name: str
        :param dataset_name: In case of a ``Dataset``, its name. Otherwise, the name of the relative dataset.
        :type dataset_name: str
        :raises NotImplementedError: always
        :return: The requested counter value.
        """
        raise NotImplementedError

    @abstractmethod
    def increment_metadata_counter(self, entity_short_name: str, dataset_name: str) -> int:
        """
        Method signature for concrete implementations that allow incrementing by one unit
        the counter value of metadata entities.

        :param entity_short_name: The short name associated either to the type of the entity itself.
        :type entity_short_name: str
        :param dataset_name: In case of a ``Dataset``, its name. Otherwise, the name of the relative dataset.
        :type dataset_name: str
        :raises NotImplementedError: always
        :return: The newly-updated (already incremented) counter value.
        """
        raise NotImplementedError
