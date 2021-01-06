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
    from oc_ocdm.graph.entities.bibliographic.reference_annotation import ReferenceAnnotation
    from oc_ocdm.graph.entities.bibliographic.bibliographic_resource import BibliographicResource
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.entities.bibliographic_entity import BibliographicEntity


class BibliographicReference(BibliographicEntity):
    """Bibliographic reference (short: be): the particular textual bibliographic reference,
    usually occurring in the reference list (and denoted by one or more in-text reference
    pointers within the text of a citing bibliographic resource), that references another
    bibliographic resource.
    """

    @accepts_only('be')
    def merge(self, other: BibliographicReference) -> None:
        super(BibliographicReference, self).merge(other)

        content: Optional[str] = other.get_content()
        if content is not None:
            self.has_content(content)

        annotations_list: List[ReferenceAnnotation] = other.get_annotations()
        for cur_annotation in annotations_list:
            self.has_annotation(cur_annotation)

        referenced_br: Optional[BibliographicResource] = other.get_referenced_br()
        if referenced_br is not None:
            self.references_br(referenced_br)

    # HAS BIBLIOGRAPHIC REFERENCE TEXT
    def get_content(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_has_content)

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
        self._create_literal(GraphEntity.iri_has_content, string)

    def remove_content(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_content, None))

    # HAS ANNOTATION (ReferenceAnnotation)
    def get_annotations(self) -> List[ReferenceAnnotation]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_has_annotation)
        result: List[ReferenceAnnotation] = []
        for uri in uri_list:
            result.append(self.g_set.add_an(self.resp_agent, self.source_agent, self.source, uri))
        return result

    @accepts_only('an')
    def has_annotation(self, an_res: ReferenceAnnotation) -> None:
        """An annotation characterizing the related citation, in terms of its citation function (the
        reason for that citation).
        """
        self.g.add((self.res, GraphEntity.iri_has_annotation, an_res.res))

    @accepts_only('an')
    def remove_annotation(self, an_res: ReferenceAnnotation = None) -> None:
        if an_res is not None:
            self.g.remove((self.res, GraphEntity.iri_has_annotation, an_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_has_annotation, None))

    # REFERENCES (BibliographicResource)
    def get_referenced_br(self) -> Optional[BibliographicResource]:
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_references)
        if uri is not None:
            return self.g_set.add_br(self.resp_agent, self.source_agent, self.source, uri)

    @accepts_only('br')
    def references_br(self, br_res: BibliographicResource) -> None:
        """The bibliographic reference that cites this bibliographic resource.
        """
        self.remove_referenced_br()
        self.g.add((self.res, GraphEntity.iri_references, br_res.res))

    def remove_referenced_br(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_references, None))
