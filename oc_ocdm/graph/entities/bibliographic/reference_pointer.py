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
    from oc_ocdm.graph.entities.bibliographic.bibliographic_reference import BibliographicReference
    from oc_ocdm.graph.entities.bibliographic.reference_annotation import ReferenceAnnotation
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.entities.bibliographic_entity import BibliographicEntity


class ReferencePointer(BibliographicEntity):
    """Reference pointer (long: in-text reference pointer; short: rp): a textual device (e.g.
       '[1]'), denoting a single bibliographic reference, that is embedded in the text of a
       document within the context of a particular sentence or text chunk. A bibliographic
       reference can be denoted in the text by one or more in-text reference pointers."""

    @accepts_only('rp')
    def merge(self, other: ReferencePointer) -> None:
        super(ReferencePointer, self).merge(other)

        content: Optional[str] = other.get_content()
        if content is not None:
            self.has_content(content)

        next_rp: Optional[ReferencePointer] = other.get_next_rp()
        if next_rp is not None:
            self.has_next_rp(next_rp)

        denoted_be: Optional[BibliographicReference] = other.get_denoted_be()
        if denoted_be is not None:
            self.denotes_be(denoted_be)

        an_list: List[ReferenceAnnotation] = other.get_annotations()
        for cur_an in an_list:
            self.has_annotation(cur_an)

    # HAS REFERENCE POINTER TEXT
    def get_content(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_has_content)

    @accepts_only('literal')
    def has_content(self, string: str) -> None:
        """The literal text of the textual device forming an in-text reference pointer and denoting
        a single bibliographic reference (e.g. “[1]”).
        """
        self.remove_content()
        self._create_literal(GraphEntity.iri_has_content, string)

    def remove_content(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_content, None))

    # HAS NEXT (ReferencePointer)
    def get_next_rp(self) -> Optional[ReferencePointer]:
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_has_next)
        if uri is not None:
            return self.g_set.add_rp(self.resp_agent, self.source_agent, self.source, uri)

    @accepts_only('rp')
    def has_next_rp(self, rp_res: ReferencePointer) -> None:
        """The following in-text reference pointer, when included within a single in-text reference
        pointer list.
        """
        self.remove_next_rp()
        self.g.add((self.res, GraphEntity.iri_has_next, rp_res.res))

    def remove_next_rp(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_next, None))

    # DENOTES (BibliographicReference)
    def get_denoted_be(self) -> Optional[BibliographicReference]:
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_denotes)
        if uri is not None:
            return self.g_set.add_be(self.resp_agent, self.source_agent, self.source, uri)

    @accepts_only('be')
    def denotes_be(self, be_res: BibliographicReference) -> None:
        """The bibliographic reference included in the list of bibliographic references, denoted by
        the in-text reference pointer.
        """
        self.remove_denoted_be()
        self.g.add((self.res, GraphEntity.iri_denotes, be_res.res))

    def remove_denoted_be(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_denotes, None))

    # HAS ANNOTATION (ReferenceAnnotation)
    def get_annotations(self) -> List[ReferenceAnnotation]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_has_annotation)
        result: List[ReferenceAnnotation] = []
        for uri in uri_list:
            result.append(self.g_set.add_an(self.resp_agent, self.source_agent, self.source, uri))
        return result

    @accepts_only('an')
    def has_annotation(self, an_res: ReferenceAnnotation) -> None:
        """An annotation characterizing the citation to which the in-text reference pointer relates
        in terms of its citation function (the reason for that citation) specific to the textual
        location of that in-text reference pointer within the citing entity.
        """
        self.g.add((self.res, GraphEntity.iri_has_annotation, an_res.res))

    @accepts_only('an')
    def remove_annotation(self, an_res: ReferenceAnnotation = None) -> None:
        if an_res is not None:
            self.g.remove((self.res, GraphEntity.iri_has_annotation, an_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_has_annotation, None))
