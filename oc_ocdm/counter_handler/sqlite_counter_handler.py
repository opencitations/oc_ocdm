#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2023, Arcangelo Massari <arcangelo.massari@unibo.it>
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
        self.con = sqlite3.connect(database)
        self.cur = self.con.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS info(
            entity TEXT PRIMARY KEY, 
            count INTEGER)""")

    def set_counter(self, new_value: int, entity_name: str) -> None:
        """
        It allows to set the counter value of provenance entities.

        :param new_value: The new counter value to be set
        :type new_value: int
        :param entity_name: The entity name
        :type entity_name: str
        :raises ValueError: if ``new_value`` is a negative integer.
        :return: None
        """
        entity_name = str(entity_name)
        if new_value < 0:
            raise ValueError("new_value must be a non negative integer!")
        self.cur.execute(f"INSERT OR REPLACE INTO info (entity, count) VALUES ('{entity_name}', {new_value})")
        self.con.commit()

    def read_counter(self, entity_name: str) -> int:
        """
        It allows to read the counter value of provenance entities.

        :param entity_name: The entity name
        :type entity_name: str
        :return: The requested counter value.
        """
        entity_name = str(entity_name)
        result = self.cur.execute(f"SELECT count FROM info WHERE entity='{entity_name}'")
        rows = result.fetchall()
        if len(rows) == 1:
            return rows[0][0]
        elif len(rows) == 0:
            return 0
        else:
            raise(Exception("There is more than one counter for this entity. The databse id broken"))

    def increment_counter(self, entity_name: str) -> int:
        """
        It allows to increment the counter value of graph and provenance entities by one unit.

        :param entity_name: The entity name
        :type entity_name: str
        :return: The newly-updated (already incremented) counter value.
        """
        entity_name = str(entity_name)
        cur_count = self.read_counter(entity_name)
        count = cur_count + 1
        self.set_counter(count, entity_name)
        return count

    def increment_metadata_counter(self):
        pass
    
    def read_metadata_counter(self):
        pass
    
    def set_metadata_counter(self):
        pass