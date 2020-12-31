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
from abc import ABC, abstractmethod


class CounterHandler(ABC):
    @abstractmethod
    def set_counter(self, new_value: int, entity_short_name: str, prov_short_name: str = "",
                    identifier: int = 1) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_counter(self, entity_short_name: str, prov_short_name: str = "", identifier: int = 1) -> int:
        raise NotImplementedError

    @abstractmethod
    def increment_counter(self, entity_short_name: str, prov_short_name: str = "", identifier: int = 1) -> int:
        raise NotImplementedError

    @abstractmethod
    def set_metadata_counter(self, new_value: int, entity_short_name: str, dataset_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_metadata_counter(self, entity_short_name: str, dataset_name: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def increment_metadata_counter(self, entity_short_name: str, dataset_name: str) -> int:
        raise NotImplementedError
