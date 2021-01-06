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
        return self._get_literal(GraphEntity.iri_title)

    @accepts_only('literal')
    def has_title(self, string: str) -> None:
        """The title of the bibliographic resource.
        """
        self.remove_title()
        self._create_literal(GraphEntity.iri_title, string)

    def remove_title(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_title, None))

    # HAS SUBTITLE
    def get_subtitle(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_has_subtitle)

    @accepts_only('literal')
    def has_subtitle(self, string: str) -> None:
        """The subtitle of the bibliographic resource.
        """
        self.remove_subtitle()
        self._create_literal(GraphEntity.iri_has_subtitle, string)

    def remove_subtitle(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_subtitle, None))

    # IS PART OF (BibliographicResource)
    def get_is_part_of(self) -> Optional[BibliographicResource]:
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_part_of)
        if uri is not None:
            return self.g_set.add_br(self.resp_agent, self.source_agent, self.source, uri)

    @accepts_only('br')
    def is_part_of(self, br_res: BibliographicResource) -> None:
        """The corpus identifier of the bibliographic resource (e.g. issue, volume, journal,
        conference proceedings) that contains the subject bibliographic resource.
        """
        self.remove_is_part_of()
        self.g.add((self.res, GraphEntity.iri_part_of, br_res.res))

    def remove_is_part_of(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_part_of, None))

    # CITES (BibliographicResource)
    def get_citations(self) -> List[BibliographicResource]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_cites)
        result: List[BibliographicResource] = []
        for uri in uri_list:
            result.append(self.g_set.add_br(self.resp_agent, self.source_agent, self.source, uri))
        return result

    @accepts_only('br')
    def has_citation(self, br_res: BibliographicResource) -> None:
        """The corpus identifier of the bibliographic resource cited by the subject bibliographic
        resource.
        """
        self.g.add((self.res, GraphEntity.iri_cites, br_res.res))

    @accepts_only('br')
    def remove_citation(self, br_res: BibliographicResource = None) -> None:
        if br_res is not None:
            self.g.remove((self.res, GraphEntity.iri_cites, br_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_cites, None))

    # HAS PUBLICATION DATE
    def get_pub_date(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_has_publication_date)

    @accepts_only('literal')
    def has_pub_date(self, string: str) -> None:
        """The date of publication of the bibliographic resource.
        """
        cur_type, string = get_datatype_from_iso_8601(string)
        if cur_type is not None and string is not None:
            self.remove_pub_date()
            self._create_literal(GraphEntity.iri_has_publication_date, string, cur_type, False)

    def remove_pub_date(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_publication_date, None))

    # IS EMBODIED AS (ResourceEmbodiment)
    def get_formats(self) -> List[ResourceEmbodiment]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_embodiment)
        result: List[ResourceEmbodiment] = []
        for uri in uri_list:
            result.append(self.g_set.add_re(self.resp_agent, self.source_agent, self.source, uri))
        return result

    @accepts_only('re')
    def has_format(self, re_res: ResourceEmbodiment) -> None:
        """The corpus identifier of the resource embodiment defining the format in which the
        bibliographic resource has been embodied, which can be either print or digital.
        """
        self.g.add((self.res, GraphEntity.iri_embodiment, re_res.res))

    @accepts_only('re')
    def remove_format(self, re_res: ResourceEmbodiment = None):
        if re_res is not None:
            self.g.remove((self.res, GraphEntity.iri_embodiment, re_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_embodiment, None))

    # HAS NUMBER
    def get_number(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_has_sequence_identifier)

    @accepts_only('literal')
    def has_number(self, string: str) -> None:
        """A literal (for example a number or a letter) that identifies the sequence position of the
        bibliographic resource as a particular item within a larger collection (e.g. an article
        number within a journal issue, a volume number of a journal, a chapter number within
        a book).
        """
        self.remove_number()
        self._create_literal(GraphEntity.iri_has_sequence_identifier, string)

    def remove_number(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_sequence_identifier, None))

    # HAS EDITION
    def get_edition(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_has_edition)

    @accepts_only('literal')
    def has_edition(self, string: str) -> None:
        """An identifier for one of several alternative editions of a particular bibliographic
        resource.
        """
        self.remove_edition()
        self._create_literal(GraphEntity.iri_has_edition, string)

    def remove_edition(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_edition, None))

    # HAS PART (BibliographicReference)
    def get_contained_in_reference_lists(self) -> List[BibliographicReference]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_contains_reference)
        result: List[BibliographicReference] = []
        for uri in uri_list:
            result.append(self.g_set.add_be(self.resp_agent, self.source_agent, self.source, uri))
        return result

    @accepts_only('be')
    def contains_in_reference_list(self, be_res: BibliographicReference) -> None:
        """A bibliographic reference within the bibliographic resource, or a discourse element
        wherein the text of the bibliographic resources can be organized.
        """
        self.g.add((self.res, GraphEntity.iri_contains_reference, be_res.res))

    @accepts_only('be')
    def remove_contained_in_reference_list(self, be_res: BibliographicReference = None) -> None:
        if be_res is not None:
            self.g.remove((self.res, GraphEntity.iri_contains_reference, be_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_contains_reference, None))

    # HAS PART (DiscourseElement)
    def get_contained_discourse_elements(self) -> List[DiscourseElement]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_contains_de)
        result: List[DiscourseElement] = []
        for uri in uri_list:
            result.append(self.g_set.add_de(self.resp_agent, self.source_agent, self.source, uri))
        return result

    @accepts_only('de')
    def contains_discourse_element(self, de_res: DiscourseElement) -> None:
        """A bibliographic reference within the bibliographic resource, or a discourse element
        wherein the text of the bibliographic resources can be organized.
        """
        self.g.add((self.res, GraphEntity.iri_contains_de, de_res.res))

    @accepts_only('de')
    def remove_contained_discourse_element(self, de_res: DiscourseElement = None) -> None:
        if de_res is not None:
            self.g.remove((self.res, GraphEntity.iri_contains_de, de_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_contains_de, None))

    # HAS CONTRIBUTOR (AgentRole)
    def get_contributors(self) -> List[AgentRole]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_is_document_context_for)
        result: List[AgentRole] = []
        for uri in uri_list:
            result.append(self.g_set.add_ar(self.resp_agent, self.source_agent, self.source, uri))
        return result

    @accepts_only('ar')
    def has_contributor(self, ar_res: AgentRole):
        self.g.add((self.res, GraphEntity.iri_is_document_context_for, ar_res.res))

    @accepts_only('ar')
    def remove_contributor(self, ar_res: AgentRole = None):
        if ar_res is not None:
            self.g.remove((self.res, GraphEntity.iri_is_document_context_for, ar_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_is_document_context_for, None))

    # HAS RELATED DOCUMENT
    def get_related_documents(self) -> List[URIRef]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_relation)
        return uri_list

    @accepts_only('thing')
    def has_related_document(self, thing_ref: URIRef) -> None:
        """A document external to the Corpus, that is related to the bibliographic resource (such
        as a version of the bibliographic resource – for example a preprint – recorded in an
        external database).
        """
        self.g.add((self.res, GraphEntity.iri_relation, thing_ref))

    @accepts_only('thing')
    def remove_related_document(self, thing_ref: URIRef = None) -> None:
        if thing_ref is not None:
            self.g.remove((self.res, GraphEntity.iri_relation, thing_ref))
        else:
            self.g.remove((self.res, GraphEntity.iri_relation, None))

    # HAS TYPE
    def create_archival_document(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_archival_document)

    def create_book(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_book)

    def create_book_chapter(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_book_chapter)

    def create_book_part(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_part)

    def create_book_section(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_expression_collection)

    def create_book_series(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_book_series)

    def create_book_set(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_book_set)

    def create_book_track(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_expression)

    def create_component(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_expression)

    def create_dataset(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_data_file)

    def create_dissertation(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_thesis)

    def create_edited_book(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_book)

    def create_journal_article(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_journal_article)

    def create_issue(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_journal_issue)

    def create_volume(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_journal_volume)

    def create_journal(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_journal)

    def create_monograph(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_book)

    def create_proceedings_article(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_proceedings_paper)

    def create_proceedings(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_academic_proceedings)

    def create_reference_book(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_reference_book)

    def create_reference_entry(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_reference_entry)

    def create_report_series(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_series)

    def create_report(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_report_document)

    def create_standard_series(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_series)

    def create_standard(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_specification_document)

    def create_series(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_series)

    def create_expression_collection(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_expression_collection)

    def create_other(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.iri_expression)
