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
    from oc_ocdm.entities.bibliographic import Citation
from oc_ocdm import GraphEntity
from oc_ocdm.entities import BibliographicEntity

"""
Notes about AN:

    Chill down, everything seems OK here!
"""


class ReferenceAnnotation(BibliographicEntity):
    """Reference annotation (short: an): an annotation, attached either to an in-text
       reference pointer or to a bibliographic reference, describing the related citation. If an
       in-text reference pointer is annotated, the related citation may be characterized with a
       citation function (the reason for that citation) specific to the textual location of that
       in-text reference pointer within the citing entity. If a bibliographic reference is
       annotated, the related citation may be similarly characterized in a more general way
       with a citation function (the reason for that citation)."""

    # HAS CITATION (Citation)
    # <self.res> OA:hasBody <ci_res>
    def _create_body_annotation(self, ci_res: Citation) -> None:
        """The citation to which the annotation relates, that is relevant either to a bibliographic
        reference or to an in-text reference pointer that denotes such a bibliographic reference.
        """
        self.remove_body_annotation()
        self.g.add((self.res, GraphEntity.has_body, URIRef(str(ci_res))))

    def remove_body_annotation(self) -> None:
        self.g.remove((self.res, GraphEntity.has_body, None))
