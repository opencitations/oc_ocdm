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
from rdflib import URIRef

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from oc_graphlib.reference_pointer import ReferencePointer
from oc_graphlib.prov_entity import GraphEntity
from oc_graphlib.bibliographic_entity import BibliographicEntity

"""
Notes about PL:

    Chill down, everything seems OK here!
"""


class PointerList(BibliographicEntity):
    # HAS POINTER LIST TEXT
    # <self.res> C4O:hasContent "string"
    def create_content(self, string: str) -> bool:
        return self._create_literal(GraphEntity.has_content, string)

    # HAS ELEMENT (ReferencePointer)
    # <self.res> CO:element <rp_res>
    def contains_element(self, rp_res: ReferencePointer) -> None:  #  new
        self.g.add((self.res, GraphEntity.has_element, URIRef(str(rp_res))))