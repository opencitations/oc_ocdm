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
    from oc_graphlib.bibliographic_reference import BibliographicReference
    from oc_graphlib.reference_annotation import ReferenceAnnotation
from oc_graphlib.graph_entity import GraphEntity
from oc_graphlib.bibliographic_entity import BibliographicEntity

"""
Notes about RP:

    Chill down, everything seems OK here!
"""


class ReferencePointer(BibliographicEntity):
    """Reference pointer (long: in-text reference pointer; short: rp): a textual device (e.g.
       '[1]'), denoting a single bibliographic reference, that is embedded in the text of a
       document within the context of a particular sentence or text chunk. A bibliographic
       reference can be denoted in the text by one or more in-text reference pointers."""

    # HAS REFERENCE POINTER TEXT
    # <self.res> C4O:hasContent "string"
    def create_content(self, string: str) -> bool:
        return self._create_literal(GraphEntity.has_content, string)

    # HAS NEXT (ReferencePointer)
    # <self.res> OCO:hasNext <rp_res>
    def has_next_rp(self, rp_res: ReferencePointer) -> None:  # new
        self.g.add((self.res, GraphEntity.has_next, URIRef(str(rp_res))))

    # DENOTES (BibliographicReference)
    # <self.res> C4O:denotes <be_res>
    def denotes_be(self, be_res: BibliographicReference) -> None:
        self.g.add((self.res, GraphEntity.denotes, URIRef(str(be_res))))

    # new
    # HAS ANNOTATION (ReferenceAnnotation)
    # <self.res> OCO:hasAnnotation <an_res>
    def _create_annotation(self, an_res: ReferenceAnnotation) -> None:
        self.g.add((self.res, GraphEntity.has_annotation, URIRef(str(an_res))))
