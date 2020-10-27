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
    from oc_ocdm.entities.bibliographic import ReferenceAnnotation, BibliographicResource
from oc_ocdm import GraphEntity
from oc_ocdm.entities import BibliographicEntity


class BibliographicReference(BibliographicEntity):
    """Bibliographic reference (short: be): the particular textual bibliographic reference,
    usually occurring in the reference list (and denoted by one or more in-text reference
    pointers within the text of a citing bibliographic resource), that references another
    bibliographic resource.
    """

    # HAS BIBLIOGRAPHIC REFERENCE TEXT
    # <self.res> C4O:hasContent "string"
    @accepts_only('literal')
    def has_content(self, string: str) -> None:
        """The literal text of a bibliographic reference occurring in the reference list (or
        elsewhere) within a bibliographic resource, that references another bibliographic
        resource. The reference text should be recorded “as given” in the citing bibliographic
        resource, including any errors (e.g. mis-spellings of authors’ names, or changes from
        “β” in the original published title to “beta” in the reference text) or omissions (e.g.
        omission of the title of the referenced bibliographic resource, or omission of sixth and
        subsequent authors’ names, as required by certain publishers), and in whatever format
        it has been made available. For instance, the reference text can be either as plain text
        or as a block of XML.
        """
        self.remove_content()
        self._create_literal(GraphEntity.has_content, string)

    def remove_content(self) -> None:
        self.g.remove((self.res, GraphEntity.has_content, None))

    # HAS ANNOTATION (ReferenceAnnotation)
    # <self.res> OCO:hasAnnotation <an_res>
    @accepts_only('an')
    def has_annotation(self, an_res: ReferenceAnnotation) -> None:
        """An annotation characterizing the related citation, in terms of its citation function (the
        reason for that citation).
        """
        self.g.add((self.res, GraphEntity.has_annotation, an_res.res))

    @accepts_only('an')
    def remove_annotation(self, an_res: ReferenceAnnotation = None) -> None:
        if an_res is not None:
            self.g.remove((self.res, GraphEntity.has_annotation, an_res.res))
        else:
            self.g.remove((self.res, GraphEntity.has_annotation, None))

    # REFERENCES (BibliographicResource)
    # <self.res> BIRO:references <br_res>
    @accepts_only('br')
    def references_br(self, br_res: BibliographicResource) -> None:
        """The bibliographic reference that cites this bibliographic resource.
        """
        self.remove_referenced_br()
        self.g.add((self.res, GraphEntity.references, br_res.res))

    def remove_referenced_br(self) -> None:
        self.g.remove((self.res, GraphEntity.references, None))
