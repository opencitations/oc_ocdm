#!/usr/bin/python

# SPDX-FileCopyrightText: 2023-2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-

import sqlite3

from oc_ocdm.counter_handler.counter_handler import CounterHandler


class SqliteCounterHandler(CounterHandler):
    """A concrete implementation of the ``CounterHandler`` interface that persistently stores
    the counter values within a SQLite database."""

    def __init__(self, database: str) -> None:
        """
        Constructor of the ``SqliteCounterHandler`` class.

        :param database: The name of the database
        :type info_dir: str
        """
        sqlite3.threadsafety = 3
        self.database = database
        self.con = sqlite3.connect(database)
        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS info(
            entity TEXT PRIMARY KEY,
            count INTEGER)""")

    def set_counter(self, new_value: int, entity_short_name: str, prov_short_name: str = "",  # type: ignore[override]
                    identifier: int = 1, supplier_prefix: str = "") -> None:
        """
        It allows to set the counter value of provenance entities.

        In this implementation, ``entity_short_name`` is used as a generic entity key
        (which may be a URI string when called from ProvSet with a GraphEntity).

        :param new_value: The new counter value to be set
        :type new_value: int
        :param entity_short_name: The entity name (used as lookup key)
        :type entity_short_name: str
        :raises ValueError: if ``new_value`` is a negative integer.
        :return: None
        """
        if new_value < 0:
            raise ValueError("new_value must be a non negative integer!")
        self.cur.execute(f"INSERT OR REPLACE INTO info (entity, count) VALUES ('{entity_short_name}', {new_value})")
        self.con.commit()

    def read_counter(self, entity_short_name: str, prov_short_name: str = "",  # type: ignore[override]
                     identifier: int = 1, supplier_prefix: str = "") -> int:
        """
        It allows to read the counter value of provenance entities.

        :param entity_short_name: The entity name (used as lookup key)
        :type entity_short_name: str
        :return: The requested counter value.
        """
        rows = self.cur.execute(f"SELECT count FROM info WHERE entity='{entity_short_name}'").fetchall()
        if len(rows) == 1:
            return rows[0][0]
        elif len(rows) == 0:
            return 0
        else:
            raise(Exception("There is more than one counter for this entity. The databse id broken"))

    def increment_counter(self, entity_short_name: str, prov_short_name: str = "",  # type: ignore[override]
                          identifier: int = 1, supplier_prefix: str = "") -> int:
        """
        It allows to increment the counter value of graph and provenance entities by one unit.

        :param entity_short_name: The entity name (used as lookup key)
        :type entity_short_name: str
        :return: The newly-updated (already incremented) counter value.
        """
        count = self.read_counter(entity_short_name) + 1
        self.set_counter(count, entity_short_name)
        return count

    def increment_metadata_counter(self, entity_short_name: str = "", dataset_name: str = "") -> int:  # type: ignore[override]
        return 0

    def read_metadata_counter(self, entity_short_name: str = "", dataset_name: str = "") -> int:  # type: ignore[override]
        return 0

    def set_metadata_counter(self, new_value: int = 0, entity_short_name: str = "", dataset_name: str = "") -> None:  # type: ignore[override]
        pass

    def __getstate__(self):
        """
        Support for pickle serialization.

        Exclude the SQLite connection and cursor objects, which are not picklable.
        The database path is preserved and the connection will be recreated upon unpickling.
        """
        state = self.__dict__.copy()
        del state['con']
        del state['cur']
        return state

    def __setstate__(self, state: dict[str, object]) -> None:
        """
        Support for pickle deserialization.

        Recreates the SQLite connection and cursor after unpickling.
        """
        vars(self).update(state)
        sqlite3.threadsafety = 3
        self.con = sqlite3.connect(self.database)
        self.cur = self.con.cursor()
