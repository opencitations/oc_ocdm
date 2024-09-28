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

from typing import Optional, Union

import redis
from oc_ocdm.counter_handler.counter_handler import CounterHandler


class RedisCounterHandler(CounterHandler):
    """A concrete implementation of the ``CounterHandler`` interface that persistently stores
    the counter values within a Redis database."""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: Optional[str] = None) -> None:
        """
        Constructor of the ``RedisCounterHandler`` class.

        :param host: Redis server host
        :type host: str
        :param port: Redis server port
        :type port: int
        :param db: Redis database number
        :type db: int
        :param password: Redis password (if required)
        :type password: Optional[str]
        """
        self.redis = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)

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
        :param supplier_prefix: The supplier prefix
        :type supplier_prefix: str
        :raises ValueError: if ``new_value`` is a negative integer
        :return: None
        """
        if new_value < 0:
            raise ValueError("new_value must be a non negative integer!")

        key = self._get_key(entity_short_name, prov_short_name, identifier, supplier_prefix)
        self.redis.set(key, new_value)

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
        :param supplier_prefix: The supplier prefix
        :type supplier_prefix: str
        :return: The requested counter value.
        """
        key = self._get_key(entity_short_name, prov_short_name, identifier, supplier_prefix)
        value = self.redis.get(key)
        return int(value) if value is not None else 0

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
        :param supplier_prefix: The supplier prefix
        :type supplier_prefix: str
        :return: The newly-updated (already incremented) counter value.
        """
        key = self._get_key(entity_short_name, prov_short_name, identifier, supplier_prefix)
        return self.redis.incr(key)

    def set_metadata_counter(self, new_value: int, entity_short_name: str, dataset_name: str) -> None:
        """
        It allows to set the counter value of metadata entities.

        :param new_value: The new counter value to be set
        :type new_value: int
        :param entity_short_name: The short name associated either to the type of the entity itself.
        :type entity_short_name: str
        :param dataset_name: In case of a ``Dataset``, its name. Otherwise, the name of the relative dataset.
        :type dataset_name: str
        :raises ValueError: if ``new_value`` is a negative integer or ``dataset_name`` is None
        :return: None
        """
        if new_value < 0:
            raise ValueError("new_value must be a non negative integer!")

        if dataset_name is None:
            raise ValueError("dataset_name must be provided!")

        key = f"metadata:{dataset_name}:{entity_short_name}"
        self.redis.set(key, new_value)

    def read_metadata_counter(self, entity_short_name: str, dataset_name: str) -> int:
        """
        It allows to read the counter value of metadata entities.

        :param entity_short_name: The short name associated either to the type of the entity itself.
        :type entity_short_name: str
        :param dataset_name: In case of a ``Dataset``, its name. Otherwise, the name of the relative dataset.
        :type dataset_name: str
        :raises ValueError: if ``dataset_name`` is None
        :return: The requested counter value.
        """
        if dataset_name is None:
            raise ValueError("dataset_name must be provided!")

        key = f"metadata:{dataset_name}:{entity_short_name}"
        value = self.redis.get(key)
        return int(value) if value is not None else 0

    def increment_metadata_counter(self, entity_short_name: str, dataset_name: str) -> int:
        """
        It allows to increment the counter value of metadata entities by one unit.

        :param entity_short_name: The short name associated either to the type of the entity itself.
        :type entity_short_name: str
        :param dataset_name: In case of a ``Dataset``, its name. Otherwise, the name of the relative dataset.
        :type dataset_name: str
        :raises ValueError: if ``dataset_name`` is None
        :return: The newly-updated (already incremented) counter value.
        """
        if dataset_name is None:
            raise ValueError("dataset_name must be provided!")

        key = f"metadata:{dataset_name}:{entity_short_name}"
        return self.redis.incr(key)

    def _get_key(self, entity_short_name: str, prov_short_name: str = "", identifier: Union[str, int, None] = None, supplier_prefix: str = "") -> str:
        """
        Generate a Redis key for the given parameters.

        :param entity_short_name: The short name associated either to the type of the entity itself
         or, in case of a provenance entity, to the type of the relative graph entity.
        :type entity_short_name: str
        :param prov_short_name: In case of a provenance entity, the short name associated to the type
         of the entity itself. An empty string otherwise.
        :type prov_short_name: str
        :param identifier: In case of a provenance entity, the identifier of the relative graph entity.
        :type identifier: Union[str, int, None]
        :param supplier_prefix: The supplier prefix
        :type supplier_prefix: str
        :return: The generated Redis key
        :rtype: str
        """
        key_parts = [entity_short_name, supplier_prefix]
        if prov_short_name:
            key_parts.append(str(identifier))
            key_parts.append(prov_short_name)
        return ':'.join(filter(None, key_parts))