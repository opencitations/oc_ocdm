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

from rdflib import RDF

from oc_ocdm.decorators import accepts_only
from oc_ocdm.support import get_datatype_from_iso_8601

if TYPE_CHECKING:
    from rdflib import URIRef
    from oc_ocdm.entities.bibliographic import BibliographicReference, AgentRole
    from oc_ocdm.entities.bibliographic import DiscourseElement
    from oc_ocdm.entities.bibliographic import ResourceEmbodiment
from oc_ocdm import GraphEntity
from oc_ocdm.entities import BibliographicEntity


class BibliographicResource(BibliographicEntity):
    """Bibliographic resource (short: br): a published bibliographic resource that cites/is
       cited by another published bibliographic resource."""

    # HAS TITLE
    # <self.res> DCTERMS:title "string"
    @accepts_only('literal')
    def has_title(self, string: str) -> None:
        """The title of the bibliographic resource.
        """
        self.remove_title()
        self._create_literal(GraphEntity.title, string)

    def remove_title(self) -> None:
        self.g.remove((self.res, GraphEntity.title, None))

    # HAS SUBTITLE
    # <self.res> FABIO:hasSubtitle "string"
    @accepts_only('literal')
    def has_subtitle(self, string: str) -> None:
        """The subtitle of the bibliographic resource.
        """
        self.remove_subtitle()
        self._create_literal(GraphEntity.has_subtitle, string)

    def remove_subtitle(self) -> None:
        self.g.remove((self.res, GraphEntity.has_subtitle, None))

    # IS PART OF (BibliographicResource)
    # <self.res> FRBR:partOf <br_res>
    @accepts_only('br')
    def is_part_of(self, br_res: BibliographicResource) -> None:
        """The corpus identifier of the bibliographic resource (e.g. issue, volume, journal,
        conference proceedings) that contains the subject bibliographic resource.
        """
        self.remove_part_of()
        self.g.add((self.res, GraphEntity.part_of, br_res.res))

    def remove_part_of(self) -> None:
        self.g.remove((self.res, GraphEntity.part_of, None))

    # CITES (BibliographicResource)
    # <self.res> CITO:cites <br_res>
    @accepts_only('br')
    def has_citation(self, br_res: BibliographicResource) -> None:
        """The corpus identifier of the bibliographic resource cited by the subject bibliographic
        resource.
        """
        self.g.add((self.res, GraphEntity.cites, br_res.res))

    @accepts_only('br')
    def remove_citation(self, br_res: BibliographicResource = None) -> None:
        if br_res is not None:
            self.g.remove((self.res, GraphEntity.cites, br_res.res))
        else:
            self.g.remove((self.res, GraphEntity.cites, None))

    # HAS PUBLICATION DATE
    # <self.res> PRISM:publicationDate "string"
    @accepts_only('literal')
    def has_pub_date(self, string: str) -> None:
        """The date of publication of the bibliographic resource.
        """
        cur_type, string = get_datatype_from_iso_8601(string)
        if cur_type is not None and string is not None:
            self.remove_pub_date()
            self._create_literal(GraphEntity.has_publication_date, string, cur_type, False)

    def remove_pub_date(self) -> None:
        self.g.remove((self.res, GraphEntity.has_publication_date, None))

    # IS EMBODIED AS (ResourceEmbodiment)
    # <self.res> FRBR:embodiment <re_res>
    @accepts_only('re')
    def has_format(self, re_res: ResourceEmbodiment) -> None:
        """The corpus identifier of the resource embodiment defining the format in which the
        bibliographic resource has been embodied, which can be either print or digital.
        """
        self.g.add((self.res, GraphEntity.embodiment, re_res.res))

    @accepts_only('re')
    def remove_format(self, re_res: ResourceEmbodiment = None):
        if re_res is not None:
            self.g.remove((self.res, GraphEntity.embodiment, re_res.res))
        else:
            self.g.remove((self.res, GraphEntity.embodiment, None))

    # HAS NUMBER
    # <self.res> FABIO:hasSequenceIdentifier "string"
    @accepts_only('literal')
    def has_number(self, string: str) -> None:
        """A literal (for example a number or a letter) that identifies the sequence position of the
        bibliographic resource as a particular item within a larger collection (e.g. an article
        number within a journal issue, a volume number of a journal, a chapter number within
        a book).
        """
        self.remove_number()
        self._create_literal(GraphEntity.has_sequence_identifier, string)

    def remove_number(self) -> None:
        self.g.remove((self.res, GraphEntity.has_sequence_identifier, None))

    # HAS EDITION
    # <self.res> PRISM:edition "string"
    @accepts_only('literal')
    def has_edition(self, string: str) -> None:
        """An identifier for one of several alternative editions of a particular bibliographic
        resource.
        """
        self.remove_edition()
        self._create_literal(GraphEntity.has_edition, string)

    def remove_edition(self) -> None:
        self.g.remove((self.res, GraphEntity.has_edition, None))

    # HAS PART (BibliographicReference)
    # <self.res> FRBR:part <be_res>
    @accepts_only('be')
    def contains_in_reference_list(self, be_res: BibliographicReference) -> None:
        """A bibliographic reference within the bibliographic resource, or a discourse element
        wherein the text of the bibliographic resources can be organized.
        """
        self.g.add((self.res, GraphEntity.contains_reference, be_res.res))

    @accepts_only('be')
    def remove_in_reference_list(self, be_res: BibliographicReference = None) -> None:
        if be_res is not None:
            self.g.remove((self.res, GraphEntity.contains_reference, be_res.res))
        else:
            self.g.remove((self.res, GraphEntity.contains_reference, None))

    # HAS PART (DiscourseElement)
    # <self.res> FRBR:part <de_res>
    @accepts_only('de')
    def contains_discourse_element(self, de_res: DiscourseElement) -> None:
        """A bibliographic reference within the bibliographic resource, or a discourse element
        wherein the text of the bibliographic resources can be organized.
        """
        self.g.add((self.res, GraphEntity.contains_de, de_res.res))

    @accepts_only('de')
    def remove_discourse_element(self, de_res: DiscourseElement = None) -> None:
        if de_res is not None:
            self.g.remove((self.res, GraphEntity.contains_de, de_res.res))
        else:
            self.g.remove((self.res, GraphEntity.contains_de, None))

    # HAS CONTRIBUTOR (AgentRole)
    # <self.res> PRO:isDocumentContextFor <ar_res>
    @accepts_only('ar')
    def has_contributor(self, ar_res: AgentRole):
        self.g.add((self.res, GraphEntity.is_document_context_for, ar_res.res))

    @accepts_only('ar')
    def remove_contributor(self, ar_res: AgentRole = None):
        if ar_res is not None:
            self.g.remove((self.res, GraphEntity.is_document_context_for, ar_res.res))
        else:
            self.g.remove((self.res, GraphEntity.is_document_context_for, None))

    # HAS RELATED DOCUMENT
    # <self.res> DCTERMS:relation <thing_ref>
    @accepts_only('thing')
    def has_related_document(self, thing_ref: URIRef) -> None:
        """A document external to the Corpus, that is related to the bibliographic resource (such
        as a version of the bibliographic resource – for example a preprint – recorded in an
        external database).
        """
        self.g.add((self.res, GraphEntity.relation, thing_ref))

    @accepts_only('thing')
    def remove_related_document(self, thing_ref: URIRef = None) -> None:
        if thing_ref is not None:
            self.g.remove((self.res, GraphEntity.relation, thing_ref))
        else:
            self.g.remove((self.res, GraphEntity.relation, None))

    # ++++++++++++++++++++++++ FACTORY METHODS ++++++++++++++++++++++++
    # <self.res> RDF:type <type>

    def create_archival_document(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.archival_document)

    def create_book(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.book)

    def create_book_chapter(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.book_chapter)

    def create_book_part(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.part)

    def create_book_section(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.expression_collection)

    def create_book_series(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.book_series)

    def create_book_set(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.book_set)

    def create_book_track(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.expression)

    def create_component(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.expression)

    def create_dataset(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.data_file)

    def create_dissertation(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.thesis)

    def create_edited_book(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.book)

    def create_journal_article(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.journal_article)

    def create_issue(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.journal_issue)

    def create_volume(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.journal_volume)

    def create_journal(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.journal)

    def create_monograph(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.book)

    def create_proceedings_article(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.proceedings_paper)

    def create_proceedings(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.academic_proceedings)

    def create_reference_book(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.reference_book)

    def create_reference_entry(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.reference_entry)

    def create_report_series(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.series)

    def create_report(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.report_document)

    def create_standard_series(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.series)

    def create_standard(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.specification_document)

    def create_series(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.series)

    def create_expression_collection(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.expression_collection)

    def create_other(self) -> None:
        """The type of the bibliographic resource
        """
        self._create_type(GraphEntity.expression)

    @accepts_only('thing')
    def remove_type(self, type_ref: URIRef = None) -> None:
        if type_ref is not None:
            self.g.remove((self.res, RDF.type, type_ref))
        else:
            self.g.remove((self.res, RDF.type, None))
