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
from oc_ocdm.support.support import get_datatype_from_iso_8601

if TYPE_CHECKING:
    from typing import Optional, List
    from rdflib import URIRef
    from oc_ocdm.graph.entities.bibliographic.bibliographic_reference import BibliographicReference
    from oc_ocdm.graph.entities.bibliographic.agent_role import AgentRole
    from oc_ocdm.graph.entities.bibliographic.discourse_element import DiscourseElement
    from oc_ocdm.graph.entities.bibliographic.resource_embodiment import ResourceEmbodiment
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.entities.bibliographic_entity import BibliographicEntity


class BibliographicResource(BibliographicEntity):
    """Bibliographic resource (short: br): a published bibliographic resource that cites/is
       cited by another published bibliographic resource."""

    @accepts_only('br')
    def merge(self, other: BibliographicResource) -> None:
        """
        The merge operation allows combining two ``BibliographicResource`` entities into a single one,
        by marking the second entity as to be deleted while also copying its data into the current
        ``BibliographicResource``. Moreover, every triple from the containing ``GraphSet`` referring to the second
        entity gets "redirected" to the current entity: **every other reference contained inside a
        different source (e.g. a triplestore) must be manually handled by the user!**

        In case of functional properties, values from the current entity get overwritten
        by those coming from the second entity while, in all other cases, values from the
        second entity are simply appended to those of the current entity. In this context,
        ``rdfs:label`` is considered as a functional property, while ``rdf:type`` is not.

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: BibliographicResource
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        super(BibliographicResource, self).merge(other)

        title: Optional[str] = other.get_title()
        if title is not None:
            self.has_title(title)

        subtitle: Optional[str] = other.get_subtitle()
        if subtitle is not None:
            self.has_subtitle(subtitle)

        container: Optional[BibliographicResource] = other.get_is_part_of()
        if container is not None:
            self.is_part_of(container)

        citations_list: List[BibliographicResource] = other.get_citations()
        for cur_citation in citations_list:
            self.has_citation(cur_citation)

        pub_date: Optional[str] = other.get_pub_date()
        if pub_date is not None:
            self.has_pub_date(pub_date)

        re_list: List[ResourceEmbodiment] = other.get_formats()
        for cur_format in re_list:
            self.has_format(cur_format)

        number: Optional[str] = other.get_number()
        if number is not None:
            self.has_number(number)

        edition: Optional[str] = other.get_edition()
        if edition is not None:
            self.has_edition(edition)

        be_list: List[BibliographicReference] = other.get_contained_in_reference_lists()
        for reference in be_list:
            self.contains_in_reference_list(reference)

        de_list: List[DiscourseElement] = other.get_contained_discourse_elements()
        for discourse_element in de_list:
            self.contains_discourse_element(discourse_element)

        ar_list: List[AgentRole] = other.get_contributors()
        for agent_role in ar_list:
            self.has_contributor(agent_role)

        related_doc_list: List[URIRef] = other.get_related_documents()
        for doc in related_doc_list:
            self.has_related_document(doc)

    # HAS TITLE
    def get_title(self) -> Optional[str]:
        """
        Getter method corresponding to the ``dcterms:title`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_title)

    @accepts_only('literal')
    def has_title(self, string: str) -> None:
        """
        Setter method corresponding to the ``dcterms:title`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The title of the bibliographic resource.`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_title()
        self._create_literal(GraphEntity.iri_title, string)

    def remove_title(self) -> None:
        """
        Remover method corresponding to the ``dcterms:title`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_title, None))

    # HAS SUBTITLE
    def get_subtitle(self) -> Optional[str]:
        """
        Getter method corresponding to the ``fabio:hasSubtitle`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_has_subtitle)

    @accepts_only('literal')
    def has_subtitle(self, string: str) -> None:
        """
        Setter method corresponding to the ``fabio:hasSubtitle`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The subtitle of the bibliographic resource.`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_subtitle()
        self._create_literal(GraphEntity.iri_has_subtitle, string)

    def remove_subtitle(self) -> None:
        """
        Remover method corresponding to the ``fabio:hasSubtitle`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_subtitle, None))

    # IS PART OF (BibliographicResource)
    def get_is_part_of(self) -> Optional[BibliographicResource]:
        """
        Getter method corresponding to the ``frbr:partOf`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_part_of, 'br')
        if uri is not None:
            return self.g_set.add_br(self.resp_agent, self.source, uri)

    @accepts_only('br')
    def is_part_of(self, br_res: BibliographicResource) -> None:
        """
        Setter method corresponding to the ``frbr:partOf`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The corpus identifier of the bibliographic resource (e.g. issue, volume, journal,
        conference proceedings) that contains the subject bibliographic resource.`

        :param br_res: The value that will be set as the object of the property related to this method
        :type br_res: BibliographicResource
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_is_part_of()
        self.g.add((self.res, GraphEntity.iri_part_of, br_res.res))

    def remove_is_part_of(self) -> None:
        """
        Remover method corresponding to the ``frbr:partOf`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_part_of, None))

    # CITES (BibliographicResource)
    def get_citations(self) -> List[BibliographicResource]:
        """
        Getter method corresponding to the ``cito:cites`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_cites, 'br')
        result: List[BibliographicResource] = []
        for uri in uri_list:
            result.append(self.g_set.add_br(self.resp_agent, self.source, uri))
        return result

    @accepts_only('br')
    def has_citation(self, br_res: BibliographicResource) -> None:
        """
        Setter method corresponding to the ``cito:cites`` RDF predicate.

        `The corpus identifier of the bibliographic resource cited by the subject bibliographic
        resource.`

        :param br_res: The value that will be set as the object of the property related to this method
        :type br_res: BibliographicResource
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, GraphEntity.iri_cites, br_res.res))

    @accepts_only('br')
    def remove_citation(self, br_res: BibliographicResource = None) -> None:
        """
        Remover method corresponding to the ``cito:cites`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param br_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type br_res: BibliographicResource
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if br_res is not None:
            self.g.remove((self.res, GraphEntity.iri_cites, br_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_cites, None))

    # HAS PUBLICATION DATE
    def get_pub_date(self) -> Optional[str]:
        """
        Getter method corresponding to the ``prism:publicationDate`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_has_publication_date)

    @accepts_only('literal')
    def has_pub_date(self, string: str) -> None:
        """
        Setter method corresponding to the ``prism:publicationDate`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The date of publication of the bibliographic resource.`

        :param string: The value that will be set as the object of the property related to this method. **It must
          be a string compliant with the** ``ISO 8601`` **standard.**
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        cur_type, string = get_datatype_from_iso_8601(string)
        if cur_type is not None and string is not None:
            self.remove_pub_date()
            self._create_literal(GraphEntity.iri_has_publication_date, string, cur_type, False)

    def remove_pub_date(self) -> None:
        """
        Remover method corresponding to the ``prism:publicationDate`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_publication_date, None))

    # IS EMBODIED AS (ResourceEmbodiment)
    def get_formats(self) -> List[ResourceEmbodiment]:
        """
        Getter method corresponding to the ``frbr:embodiment`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_embodiment, 're')
        result: List[ResourceEmbodiment] = []
        for uri in uri_list:
            result.append(self.g_set.add_re(self.resp_agent, self.source, uri))
        return result

    @accepts_only('re')
    def has_format(self, re_res: ResourceEmbodiment) -> None:
        """
        Setter method corresponding to the ``frbr:embodiment`` RDF predicate.

        `The corpus identifier of the resource embodiment defining the format in which the
        bibliographic resource has been embodied, which can be either print or digital.`

        :param re_res: The value that will be set as the object of the property related to this method
        :type re_res: ResourceEmbodiment
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, GraphEntity.iri_embodiment, re_res.res))

    @accepts_only('re')
    def remove_format(self, re_res: ResourceEmbodiment = None) -> None:
        """
        Remover method corresponding to the ``frbr:embodiment`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param re_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type re_res: ResourceEmbodiment
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if re_res is not None:
            self.g.remove((self.res, GraphEntity.iri_embodiment, re_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_embodiment, None))

    # HAS NUMBER
    def get_number(self) -> Optional[str]:
        """
        Getter method corresponding to the ``fabio:hasSequenceIdentifier`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_has_sequence_identifier)

    @accepts_only('literal')
    def has_number(self, string: str) -> None:
        """
        Setter method corresponding to the ``fabio:hasSequenceIdentifier`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `A literal (for example a number or a letter) that identifies the sequence position of the
        bibliographic resource as a particular item within a larger collection (e.g. an article
        number within a journal issue, a volume number of a journal, a chapter number within
        a book).`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_number()
        self._create_literal(GraphEntity.iri_has_sequence_identifier, string)

    def remove_number(self) -> None:
        """
        Remover method corresponding to the ``fabio:hasSequenceIdentifier`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_sequence_identifier, None))

    # HAS EDITION
    def get_edition(self) -> Optional[str]:
        """
        Getter method corresponding to the ``prism:edition`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_has_edition)

    @accepts_only('literal')
    def has_edition(self, string: str) -> None:
        """
        Setter method corresponding to the ``prism:edition`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `An identifier for one of several alternative editions of a particular bibliographic
        resource.`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_edition()
        self._create_literal(GraphEntity.iri_has_edition, string)

    def remove_edition(self) -> None:
        """
        Remover method corresponding to the ``prism:edition`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_edition, None))

    # HAS PART (BibliographicReference)
    def get_contained_in_reference_lists(self) -> List[BibliographicReference]:
        """
        Getter method corresponding to the ``frbr:part`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_contains_reference, 'be')
        result: List[BibliographicReference] = []
        for uri in uri_list:
            result.append(self.g_set.add_be(self.resp_agent, self.source, uri))
        return result

    @accepts_only('be')
    def contains_in_reference_list(self, be_res: BibliographicReference) -> None:
        """
        Setter method corresponding to the ``frbr:part`` RDF predicate.

        `A bibliographic reference within the bibliographic resource, or a discourse element
        wherein the text of the bibliographic resources can be organized.`

        :param be_res: The value that will be set as the object of the property related to this method
        :type be_res: BibliographicReference
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, GraphEntity.iri_contains_reference, be_res.res))

    @accepts_only('be')
    def remove_contained_in_reference_list(self, be_res: BibliographicReference = None) -> None:
        """
        Remover method corresponding to the ``frbr:part`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param be_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type be_res: BibliographicReference
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if be_res is not None:
            self.g.remove((self.res, GraphEntity.iri_contains_reference, be_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_contains_reference, None))

    # HAS PART (DiscourseElement)
    def get_contained_discourse_elements(self) -> List[DiscourseElement]:
        """
        Getter method corresponding to the ``frbr:part`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_contains_de, 'de')
        result: List[DiscourseElement] = []
        for uri in uri_list:
            result.append(self.g_set.add_de(self.resp_agent, self.source, uri))
        return result

    @accepts_only('de')
    def contains_discourse_element(self, de_res: DiscourseElement) -> None:
        """
        Setter method corresponding to the ``frbr:part`` RDF predicate.

        `A bibliographic reference within the bibliographic resource, or a discourse element
        wherein the text of the bibliographic resources can be organized.`

        :param de_res: The value that will be set as the object of the property related to this method
        :type de_res: DiscourseElement
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, GraphEntity.iri_contains_de, de_res.res))

    @accepts_only('de')
    def remove_contained_discourse_element(self, de_res: DiscourseElement = None) -> None:
        """
        Remover method corresponding to the ``frbr:part`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param de_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type de_res: DiscourseElement
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if de_res is not None:
            self.g.remove((self.res, GraphEntity.iri_contains_de, de_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_contains_de, None))

    # HAS CONTRIBUTOR (AgentRole)
    def get_contributors(self) -> List[AgentRole]:
        """
        Getter method corresponding to the ``pro:isDocumentContextFor`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_is_document_context_for, 'ar')
        result: List[AgentRole] = []
        for uri in uri_list:
            result.append(self.g_set.add_ar(self.resp_agent, self.source, uri))
        return result

    @accepts_only('ar')
    def has_contributor(self, ar_res: AgentRole):
        """
        Setter method corresponding to the ``pro:isDocumentContextFor`` RDF predicate.

        :param ar_res: The value that will be set as the object of the property related to this method
        :type ar_res: AgentRole
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, GraphEntity.iri_is_document_context_for, ar_res.res))

    @accepts_only('ar')
    def remove_contributor(self, ar_res: AgentRole = None):
        """
        Remover method corresponding to the ``frbr:part`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param ar_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type ar_res: AgentRole
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if ar_res is not None:
            self.g.remove((self.res, GraphEntity.iri_is_document_context_for, ar_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_is_document_context_for, None))

    # HAS RELATED DOCUMENT
    def get_related_documents(self) -> List[URIRef]:
        """
        Getter method corresponding to the ``dcterms:relation`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_relation)
        return uri_list

    @accepts_only('thing')
    def has_related_document(self, thing_res: URIRef) -> None:
        """
        Setter method corresponding to the ``dcterms:relation`` RDF predicate.

        `A document external to the Corpus, that is related to the bibliographic resource (such
        as a version of the bibliographic resource – for example a preprint – recorded in an
        external database).`

        :param thing_res: The value that will be set as the object of the property related to this method
        :type thing_res: URIRef
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, GraphEntity.iri_relation, thing_res))

    @accepts_only('thing')
    def remove_related_document(self, thing_res: URIRef = None) -> None:
        """
        Remover method corresponding to the ``dcterms:relation`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param thing_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type thing_res: URIRef
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if thing_res is not None:
            self.g.remove((self.res, GraphEntity.iri_relation, thing_res))
        else:
            self.g.remove((self.res, GraphEntity.iri_relation, None))
    
    def create_abstract(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``doco:Abstract``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_abstract)

    # HAS TYPE
    def create_archival_document(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:ArchivalDocument``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_archival_document)

    def create_audio_document(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:AudioDocument``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_audio_document)

    def create_book(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Book``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_book)

    def create_book_chapter(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:BookChapter``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_book_chapter)

    def create_book_part(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``doco:Part``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_part)

    def create_book_section(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:ExpressionCollection``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_expression_collection)

    def create_book_series(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:BookSeries``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_book_series)

    def create_book_set(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:BookSet``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_book_set)

    def create_book_track(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Expression``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_expression)

    def create_component(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Expression``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_expression)

    def create_computer_program(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:ComputerProgram``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_computer_program)

    def create_data_management_plan(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:DataManagementPlan``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_data_management_plan)

    def create_dataset(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:DataFile``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_data_file)

    def create_dissertation(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Thesis``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_thesis)

    def create_edited_book(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Book``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_book)

    def create_editorial(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Editorial``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_editorial)

    def create_journal_article(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:JournalArticle``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_journal_article)

    def create_journal_editorial(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:JournalEditorial``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_journal_editorial)

    def create_issue(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:JournalIssue``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_journal_issue)

    def create_volume(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:JournalVolume``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_journal_volume)

    def create_journal(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Journal``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_journal)

    def create_monograph(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Book``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_book)

    def create_newspaper(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Newspaper``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_newspaper)

    def create_newspaper_article(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:NewspaperArticle``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_newspaper_article)

    def create_newspaper_editorial(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:NewspaperEditorial``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_newspaper_editorial)
    
    def create_newspaper_issue(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:NewspaperIssue``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_newspaper_issue)

    def create_peer_review(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fr:ReviewVersion``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_peer_review)

    def create_preprint(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Preprint``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_preprint)

    def create_presentation(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Presentation``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_presentation)

    def create_proceedings_article(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:ProceedingsPaper``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_proceedings_paper)

    def create_proceedings(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:AcademicProceedings``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_academic_proceedings)

    def create_proceedings_series(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Series``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_proceedings_series)

    def create_reference_book(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:ReferenceBook``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_reference_book)

    def create_reference_entry(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:ReferenceEntry``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_reference_entry)

    def create_report_series(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Series``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_series)

    def create_report(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:ReportDocument``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_report_document)

    def create_retraction_notice(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:RetractionNotice``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_retraction_notice)

    def create_standard_series(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Series``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_series)

    def create_standard(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:SpecificationDocument``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_specification_document)

    def create_series(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Series``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_series)

    def create_expression_collection(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:ExpressionCollection``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_expression_collection)

    def create_web_content(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:WebContent``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_web_content)

    def create_other(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:Expression``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `The type of the bibliographic resource`

        :return: None
        """
        self._create_type(GraphEntity.iri_expression)
