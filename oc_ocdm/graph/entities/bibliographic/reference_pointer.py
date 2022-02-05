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
        """
        The merge operation allows combining two ``ReferencePointer`` entities into a single one,
        by marking the second entity as to be deleted while also copying its data into the current
        ``ReferencePointer``. Moreover, every triple from the containing ``GraphSet`` referring to the second
        entity gets "redirected" to the current entity: **every other reference contained inside a
        different source (e.g. a triplestore) must be manually handled by the user!**

        In case of functional properties, values from the current entity get overwritten
        by those coming from the second entity while, in all other cases, values from the
        second entity are simply appended to those of the current entity. In this context,
        ``rdfs:label`` is considered as a functional property, while ``rdf:type`` is not.

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: ReferencePointer
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
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
        """
        Getter method corresponding to the ``c4o:hasContent`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_has_content)

    @accepts_only('literal')
    def has_content(self, string: str) -> None:
        """
        Setter method corresponding to the ``c4o:hasContent`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The literal text of the textual device forming an in-text reference pointer and denoting
        a single bibliographic reference (e.g. “[1]”).`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_content()
        self._create_literal(GraphEntity.iri_has_content, string)

    def remove_content(self) -> None:
        """
        Remover method corresponding to the ``c4o:hasContent`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_content, None))

    # HAS NEXT (ReferencePointer)
    def get_next_rp(self) -> Optional[ReferencePointer]:
        """
        Getter method corresponding to the ``oco:hasNext`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_has_next, 'rp')
        if uri is not None:
            return self.g_set.add_rp(self.resp_agent, self.source, uri)

    @accepts_only('rp')
    def has_next_rp(self, rp_res: ReferencePointer) -> None:
        """
        Setter method corresponding to the ``oco:hasNext`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The following in-text reference pointer, when included within a single in-text reference
        pointer list.`

        :param rp_res: The value that will be set as the object of the property related to this method
        :type rp_res: ReferencePointer
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_next_rp()
        self.g.add((self.res, GraphEntity.iri_has_next, rp_res.res))

    def remove_next_rp(self) -> None:
        """
        Remover method corresponding to the ``oco:hasNext`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_next, None))

    # DENOTES (BibliographicReference)
    def get_denoted_be(self) -> Optional[BibliographicReference]:
        """
        Getter method corresponding to the ``c4o:denotes`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_denotes, 'be')
        if uri is not None:
            return self.g_set.add_be(self.resp_agent, self.source, uri)

    @accepts_only('be')
    def denotes_be(self, be_res: BibliographicReference) -> None:
        """
        Setter method corresponding to the ``c4o:denotes`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The bibliographic reference included in the list of bibliographic references, denoted by
        the in-text reference pointer.`

        :param be_res: The value that will be set as the object of the property related to this method
        :type be_res: BibliographicReference
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_denoted_be()
        self.g.add((self.res, GraphEntity.iri_denotes, be_res.res))

    def remove_denoted_be(self) -> None:
        """
        Remover method corresponding to the ``c4o:denotes`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_denotes, None))

    # HAS ANNOTATION (ReferenceAnnotation)
    def get_annotations(self) -> List[ReferenceAnnotation]:
        """
        Getter method corresponding to the ``oco:hasAnnotation`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_has_annotation, 'an')
        result: List[ReferenceAnnotation] = []
        for uri in uri_list:
            result.append(self.g_set.add_an(self.resp_agent, self.source, uri))
        return result

    @accepts_only('an')
    def has_annotation(self, an_res: ReferenceAnnotation) -> None:
        """
        Setter method corresponding to the ``oco:hasAnnotation`` RDF predicate.

        `An annotation characterizing the citation to which the in-text reference pointer relates
        in terms of its citation function (the reason for that citation) specific to the textual
        location of that in-text reference pointer within the citing entity.`

        :param an_res: The value that will be set as the object of the property related to this method
        :type an_res: ReferenceAnnotation
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, GraphEntity.iri_has_annotation, an_res.res))

    @accepts_only('an')
    def remove_annotation(self, an_res: ReferenceAnnotation = None) -> None:
        """
        Remover method corresponding to the ``oco:hasAnnotation`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param an_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type an_res: ReferenceAnnotation
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if an_res is not None:
            self.g.remove((self.res, GraphEntity.iri_has_annotation, an_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_has_annotation, None))
