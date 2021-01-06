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

from oc_ocdm.decorators import accepts_only

if TYPE_CHECKING:
    from typing import Optional, List
    from rdflib import URIRef
    from oc_ocdm.graph.entities.bibliographic.reference_pointer import ReferencePointer
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.entities.bibliographic_entity import BibliographicEntity


class PointerList(BibliographicEntity):
    """Pointer list (short: pl): a textual device (e.g. '[1, 2, 3]' or '[4-9]') which includes a
       number of reference pointers denoting the specific bibliographic references to which
       the list pertains."""

    @accepts_only('pl')
    def merge(self, other: PointerList) -> None:
        super(PointerList, self).merge(other)

        content: Optional[str] = self.get_content()
        if content is not None:
            self.has_content(content)

        rp_list: List[ReferencePointer] = other.get_contained_elements()
        for cur_rp in rp_list:
            self.contains_element(cur_rp)

    # HAS POINTER LIST TEXT
    def get_content(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_has_content)

    @accepts_only('literal')
    def has_content(self, string: str) -> None:
        self.remove_content()
        self._create_literal(GraphEntity.iri_has_content, string)

    def remove_content(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_content, None))

    # HAS ELEMENT (ReferencePointer)
    def get_contained_elements(self) -> List[ReferencePointer]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_has_element)
        result: List[ReferencePointer] = []
        for uri in uri_list:
            result.append(self.g_set.add_rp(self.resp_agent, self.source_agent, self.source, uri))
        return result

    @accepts_only('rp')
    def contains_element(self, rp_res: ReferencePointer) -> None:
        """The in-text reference pointer that is part of the in-text reference pointer list present at
        a particular location within the body of the citing work.
        """
        self.g.add((self.res, GraphEntity.iri_has_element, rp_res.res))

    @accepts_only('rp')
    def remove_contained_element(self, rp_res: ReferencePointer = None) -> None:
        if rp_res is not None:
            self.g.remove((self.res, GraphEntity.iri_has_element, rp_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_has_element, None))
