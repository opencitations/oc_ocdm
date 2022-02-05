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
    from typing import Optional
    from rdflib import URIRef
    from oc_ocdm.graph.entities.bibliographic.citation import Citation
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.entities.bibliographic_entity import BibliographicEntity


class ReferenceAnnotation(BibliographicEntity):
    """Reference annotation (short: an): an annotation, attached either to an in-text
       reference pointer or to a bibliographic reference, describing the related citation. If an
       in-text reference pointer is annotated, the related citation may be characterized with a
       citation function (the reason for that citation) specific to the textual location of that
       in-text reference pointer within the citing entity. If a bibliographic reference is
       annotated, the related citation may be similarly characterized in a more general way
       with a citation function (the reason for that citation)."""

    @accepts_only('an')
    def merge(self, other: ReferenceAnnotation) -> None:
        """
        The merge operation allows combining two ``ReferenceAnnotation`` entities into a single one,
        by marking the second entity as to be deleted while also copying its data into the current
        ``ReferenceAnnotation``. Moreover, every triple from the containing ``GraphSet`` referring to the second
        entity gets "redirected" to the current entity: **every other reference contained inside a
        different source (e.g. a triplestore) must be manually handled by the user!**

        In case of functional properties, values from the current entity get overwritten
        by those coming from the second entity while, in all other cases, values from the
        second entity are simply appended to those of the current entity. In this context,
        ``rdfs:label`` is considered as a functional property, while ``rdf:type`` is not.

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: ReferenceAnnotation
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        super(ReferenceAnnotation, self).merge(other)

        citation: Optional[Citation] = other.get_body_annotation()
        if citation is not None:
            self.has_body_annotation(citation)

    # HAS CITATION (Citation)
    def get_body_annotation(self) -> Optional[Citation]:
        """
        Getter method corresponding to the ``oa:hasBody`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_has_body, 'ci')
        if uri is not None:
            return self.g_set.add_ci(self.resp_agent, self.source, uri)

    @accepts_only('ci')
    def has_body_annotation(self, ci_res: Citation) -> None:
        """
        Setter method corresponding to the ``oa:hasBody`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The citation to which the annotation relates, that is relevant either to a bibliographic
        reference or to an in-text reference pointer that denotes such a bibliographic reference.`

        :param ci_res: The value that will be set as the object of the property related to this method
        :type ci_res: Citation
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_body_annotation()
        self.g.add((self.res, GraphEntity.iri_has_body, ci_res.res))

    def remove_body_annotation(self) -> None:
        """
        Remover method corresponding to the ``oa:hasBody`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_body, None))
