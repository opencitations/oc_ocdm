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

from rdflib import URIRef

if TYPE_CHECKING:
    from oc_ocdm.entities.bibliographic import BibliographicReference
    from oc_ocdm.entities.bibliographic import ReferenceAnnotation
from oc_ocdm import GraphEntity
from oc_ocdm.entities import BibliographicEntity

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
    def create_content(self, string: str) -> None:
        """The literal text of the textual device forming an in-text reference pointer and denoting
        a single bibliographic reference (e.g. “[1]”).
        """
        self.remove_content()
        self._create_literal(GraphEntity.has_content, string)

    def remove_content(self) -> None:
        self.g.remove((self.res, GraphEntity.has_content, None))

    # HAS NEXT (ReferencePointer)
    # <self.res> OCO:hasNext <rp_res>
    def has_next_rp(self, rp_res: ReferencePointer) -> None:
        """The following in-text reference pointer, when included within a single in-text reference
        pointer list.
        """
        self.remove_next_rp()
        self.g.add((self.res, GraphEntity.has_next, rp_res.res))

    def remove_next_rp(self) -> None:
        self.g.remove((self.res, GraphEntity.has_next, None))

    # DENOTES (BibliographicReference)
    # <self.res> C4O:denotes <be_res>
    def denotes_be(self, be_res: BibliographicReference) -> None:
        """The bibliographic reference included in the list of bibliographic references, denoted by
        the in-text reference pointer.
        """
        self.remove_be()
        self.g.add((self.res, GraphEntity.denotes, be_res.res))

    def remove_be(self) -> None:
        self.g.remove((self.res, GraphEntity.denotes, None))

    # HAS ANNOTATION (ReferenceAnnotation)
    # <self.res> OCO:hasAnnotation <an_res>
    def create_annotation(self, an_res: ReferenceAnnotation) -> None:
        """An annotation characterizing the citation to which the in-text reference pointer relates
        in terms of its citation function (the reason for that citation) specific to the textual
        location of that in-text reference pointer within the citing entity.
        """
        self.g.add((self.res, GraphEntity.has_annotation, an_res.res))

    def remove_annotation(self, an_res: ReferenceAnnotation = None) -> None:
        if an_res is not None:
            self.g.remove((self.res, GraphEntity.has_annotation, an_res.res))
        else:
            self.g.remove((self.res, GraphEntity.has_annotation, None))
