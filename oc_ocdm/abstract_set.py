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

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from oc_ocdm.abstract_entity import AbstractEntity

if TYPE_CHECKING:
    from typing import List, ClassVar, Dict, Optional
    from rdflib import URIRef, Graph


class AbstractSet(ABC):

    short_name_to_type_iri: ClassVar[Dict[str, URIRef]] = {}

    def __init__(self) -> None:
        self.res_to_entity: Dict[URIRef, AbstractEntity] = {}

    def graphs(self) -> List[Graph]:
        result: List[Graph] = []
        for entity in self.res_to_entity.values():
            if len(entity.g) > 0:
                result.append(entity.g)
        return result

    @abstractmethod
    def get_entity(self, res: URIRef) -> Optional[AbstractEntity]:
        pass

    @staticmethod
    def get_graph_iri(g: Graph) -> str:
        return str(g.identifier)
