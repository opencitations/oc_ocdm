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
        """
        The merge operation allows combining two ``BibliographicReference`` entities into a single one,
        by marking the second entity as to be deleted while also copying its data into the current
        ``BibliographicReference``. Moreover, every triple from the containing ``GraphSet`` referring to the second
        entity gets "redirected" to the current entity: **every other reference contained inside a
        different source (e.g. a triplestore) must be manually handled by the user!**

        In case of functional properties, values from the current entity get overwritten
        by those coming from the second entity while, in all other cases, values from the
        second entity are simply appended to those of the current entity. In this context,
        ``rdfs:label`` is considered as a functional property, while ``rdf:type`` is not.

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: BibliographicReference
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
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

        `The literal text of a bibliographic reference occurring in the reference list (or
        elsewhere) within a bibliographic resource, that references another bibliographic
        resource. The reference text should be recorded “as given” in the citing bibliographic
        resource, including any errors (e.g. mis-spellings of authors’ names, or changes from
        “β” in the original published title to “beta” in the reference text) or omissions (e.g.
        omission of the title of the referenced bibliographic resource, or omission of sixth and
        subsequent authors’ names, as required by certain publishers), and in whatever format
        it has been made available. For instance, the reference text can be either as plain text
        or as a block of XML.`

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

        `An annotation characterizing the related citation, in terms of its citation function (the
        reason for that citation).`

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

    # REFERENCES (BibliographicResource)
    def get_referenced_br(self) -> Optional[BibliographicResource]:
        """
        Getter method corresponding to the ``biro:references`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_references, 'br')
        if uri is not None:
            return self.g_set.add_br(self.resp_agent, self.source, uri)

    @accepts_only('br')
    def references_br(self, br_res: BibliographicResource) -> None:
        """
        Setter method corresponding to the ``biro:references`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The bibliographic reference that cites this bibliographic resource.`

        :param br_res: The value that will be set as the object of the property related to this method
        :type br_res: BibliographicResource
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_referenced_br()
        self.g.add((self.res, GraphEntity.iri_references, br_res.res))

    def remove_referenced_br(self) -> None:
        """
        Remover method corresponding to the ``biro:references`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_references, None))
