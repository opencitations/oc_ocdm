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

from rdflib import Graph, Namespace, URIRef

from oc_ocdm.abstract_entity import AbstractEntity

if TYPE_CHECKING:
    from typing import ClassVar, Dict, List, Optional, Tuple

    from oc_ocdm.graph.graph_set import GraphSet


class GraphEntity(AbstractEntity):
    BIRO: ClassVar[Namespace] = Namespace("http://purl.org/spar/biro/")
    C4O: ClassVar[Namespace] = Namespace("http://purl.org/spar/c4o/")
    CO: ClassVar[Namespace] = Namespace("http://purl.org/co/")
    CITO: ClassVar[Namespace] = Namespace("http://purl.org/spar/cito/")
    DATACITE: ClassVar[Namespace] = Namespace("http://purl.org/spar/datacite/")
    DCTERMS: ClassVar[Namespace] = Namespace("http://purl.org/dc/terms/")
    DEO: ClassVar[Namespace] = Namespace("http://purl.org/spar/deo/")
    DOCO: ClassVar[Namespace] = Namespace("http://purl.org/spar/doco/")
    FABIO: ClassVar[Namespace] = Namespace("http://purl.org/spar/fabio/")
    FOAF: ClassVar[Namespace] = Namespace("http://xmlns.com/foaf/0.1/")
    FR: ClassVar[Namespace] = Namespace("http://purl.org/spar/fr/")
    FRBR: ClassVar[Namespace] = Namespace("http://purl.org/vocab/frbr/core#")
    LITERAL: ClassVar[Namespace] = Namespace("http://www.essepuntato.it/2010/06/literalreification/")
    OA: ClassVar[Namespace] = Namespace("http://www.w3.org/ns/oa#")
    OCO: ClassVar[Namespace] = Namespace("https://w3id.org/oc/ontology/")
    PRISM: ClassVar[Namespace] = Namespace("http://prismstandard.org/namespaces/basic/2.0/")
    PRO: ClassVar[Namespace] = Namespace("http://purl.org/spar/pro/")

    iri_has_subtitle: ClassVar[URIRef] = FABIO.hasSubtitle
    iri_has_publication_date: ClassVar[URIRef] = PRISM.publicationDate
    iri_bibliographic_reference: ClassVar[URIRef] = BIRO.BibliographicReference
    iri_references: ClassVar[URIRef] = BIRO.references
    iri_denotes: ClassVar[URIRef] = C4O.denotes
    iri_has_content: ClassVar[URIRef] = C4O.hasContent
    iri_intextref_pointer: ClassVar[URIRef] = C4O.InTextReferencePointer
    iri_is_context_of: ClassVar[URIRef] = C4O.isContextOf
    iri_singleloc_pointer_list: ClassVar[URIRef] = C4O.SingleLocationPointerList
    iri_has_element: ClassVar[URIRef] = CO.element
    iri_citation: ClassVar[URIRef] = CITO.Citation
    iri_cites: ClassVar[URIRef] = CITO.cites
    iri_citation_characterisation: ClassVar[URIRef] = CITO.hasCitationCharacterisation
    iri_has_citing_entity: ClassVar[URIRef] = CITO.hasCitingEntity
    iri_has_cited_entity: ClassVar[URIRef] = CITO.hasCitedEntity
    iri_openalex: ClassVar[URIRef] = DATACITE.openalex
    iri_arxiv: ClassVar[URIRef] = DATACITE.arxiv
    iri_oci: ClassVar[URIRef] = DATACITE.oci
    iri_doi: ClassVar[URIRef] = DATACITE.doi
    iri_pmid: ClassVar[URIRef] = DATACITE.pmid
    iri_pmcid: ClassVar[URIRef] = DATACITE.pmcid
    iri_orcid: ClassVar[URIRef] = DATACITE.orcid
    iri_xpath: ClassVar[URIRef] = DATACITE["local-resource-identifier-scheme"]
    iri_intrepid: ClassVar[URIRef] = DATACITE.intrepid
    iri_xmlid: ClassVar[URIRef] = DATACITE["local-resource-identifier-scheme"]
    iri_has_identifier: ClassVar[URIRef] = DATACITE.hasIdentifier
    iri_identifier: ClassVar[URIRef] = DATACITE.Identifier
    iri_isbn: ClassVar[URIRef] = DATACITE.isbn
    iri_issn: ClassVar[URIRef] = DATACITE.issn
    iri_url: ClassVar[URIRef] = DATACITE.url
    iri_uses_identifier_scheme: ClassVar[URIRef] = DATACITE.usesIdentifierScheme
    iri_title: ClassVar[URIRef] = DCTERMS["title"]
    iri_caption: ClassVar[URIRef] = DEO.Caption
    iri_discourse_element: ClassVar[URIRef] = DEO.DiscourseElement
    iri_footnote: ClassVar[URIRef] = DOCO.Footnote
    iri_paragraph: ClassVar[URIRef] = DOCO.Paragraph
    iri_part: ClassVar[URIRef] = DOCO.Part
    iri_section: ClassVar[URIRef] = DOCO.Section
    iri_section_title: ClassVar[URIRef] = DOCO.SectionTitle
    iri_sentence: ClassVar[URIRef] = DOCO.Sentence
    iri_table: ClassVar[URIRef] = DOCO.Table
    iri_text_chunk: ClassVar[URIRef] = DOCO.TextChunk
    iri_abstract: ClassVar[URIRef] = DOCO.Abstract
    iri_academic_proceedings: ClassVar[URIRef] = FABIO.AcademicProceedings
    iri_audio_document: ClassVar[URIRef] = FABIO.AudioDocument
    iri_book: ClassVar[URIRef] = FABIO.Book
    iri_book_chapter: ClassVar[URIRef] = FABIO.BookChapter
    iri_book_series: ClassVar[URIRef] = FABIO.BookSeries
    iri_book_set: ClassVar[URIRef] = FABIO.BookSet
    iri_computer_program: ClassVar[URIRef] = FABIO.ComputerProgram
    iri_data_file: ClassVar[URIRef] = FABIO.DataFile
    iri_data_management_plan: ClassVar[URIRef] = FABIO.DataManagementPlan
    iri_editorial: ClassVar[URIRef] = FABIO.Editorial
    iri_expression: ClassVar[URIRef] = FABIO.Expression
    iri_expression_collection: ClassVar[URIRef] = FABIO.ExpressionCollection
    iri_has_sequence_identifier: ClassVar[URIRef] = FABIO.hasSequenceIdentifier
    iri_journal: ClassVar[URIRef] = FABIO.Journal
    iri_journal_article: ClassVar[URIRef] = FABIO.JournalArticle
    iri_journal_editorial: ClassVar[URIRef] = FABIO.JournalEditorial
    iri_journal_issue: ClassVar[URIRef] = FABIO.JournalIssue
    iri_journal_volume: ClassVar[URIRef] = FABIO.JournalVolume
    iri_manifestation: ClassVar[URIRef] = FABIO.Manifestation
    iri_newspaper: ClassVar[URIRef] = FABIO.Newspaper
    iri_newspaper_article: ClassVar[URIRef] = FABIO.NewspaperArticle
    iri_newspaper_editorial: ClassVar[URIRef] = FABIO.NewspaperEditorial
    iri_newspaper_issue: ClassVar[URIRef] = FABIO.NewspaperIssue
    iri_peer_review: ClassVar[URIRef] = FR.ReviewVersion
    iri_preprint: ClassVar[URIRef] = FABIO.Preprint
    iri_presentation: ClassVar[URIRef] = FABIO.Presentation
    iri_proceedings_paper: ClassVar[URIRef] = FABIO.ProceedingsPaper
    iri_proceedings_series: ClassVar[URIRef] = FABIO.Series
    iri_reference_book: ClassVar[URIRef] = FABIO.ReferenceBook
    iri_reference_entry: ClassVar[URIRef] = FABIO.ReferenceEntry
    iri_report_document: ClassVar[URIRef] = FABIO.ReportDocument
    iri_retraction_notice: ClassVar[URIRef] = FABIO.RetractionNotice
    iri_series: ClassVar[URIRef] = FABIO.Series
    iri_specification_document: ClassVar[URIRef] = FABIO.SpecificationDocument
    iri_thesis: ClassVar[URIRef] = FABIO.Thesis
    iri_web_content: ClassVar[URIRef] = FABIO.WebContent
    iri_agent: ClassVar[URIRef] = FOAF.Agent
    iri_family_name: ClassVar[URIRef] = FOAF.familyName
    iri_given_name: ClassVar[URIRef] = FOAF.givenName
    iri_name: ClassVar[URIRef] = FOAF.name
    iri_embodiment: ClassVar[URIRef] = FRBR.embodiment
    iri_part_of: ClassVar[URIRef] = FRBR.partOf
    iri_contains_reference: ClassVar[URIRef] = FRBR.part
    iri_contains_de: ClassVar[URIRef] = FRBR.part
    iri_has_literal_value: ClassVar[URIRef] = LITERAL.hasLiteralValue
    iri_ending_page: ClassVar[URIRef] = PRISM.endingPage
    iri_starting_page: ClassVar[URIRef] = PRISM.startingPage
    iri_author: ClassVar[URIRef] = PRO.author
    iri_editor: ClassVar[URIRef] = PRO.editor
    iri_is_held_by: ClassVar[URIRef] = PRO.isHeldBy
    iri_publisher: ClassVar[URIRef] = PRO.publisher
    iri_is_document_context_for: ClassVar[URIRef] = PRO.isDocumentContextFor
    iri_role_in_time: ClassVar[URIRef] = PRO.RoleInTime
    iri_with_role: ClassVar[URIRef] = PRO.withRole
    iri_note: ClassVar[URIRef] = OA.Annotation
    iri_has_body: ClassVar[URIRef] = OA.hasBody
    iri_has_annotation: ClassVar[URIRef] = OCO.hasAnnotation  # inverse of OA.hasTarget
    iri_has_next: ClassVar[URIRef] = OCO.hasNext
    iri_archival_document: ClassVar[URIRef] = FABIO.ArchivalDocument
    iri_viaf: ClassVar[URIRef] = DATACITE.viaf
    iri_crossref: ClassVar[URIRef] = DATACITE.crossref  # TODO: add to datacite!
    iri_datacite: ClassVar[URIRef] = DATACITE.datacite  # TODO: add to datacite!
    iri_jid: ClassVar[URIRef] = DATACITE.jid # TODO: add to datacite!
    iri_wikidata: ClassVar[URIRef] = DATACITE.wikidata  # TODO: add to datacite!
    iri_wikipedia: ClassVar[URIRef] = DATACITE.wikipedia  # TODO: add to datacite!
    iri_has_edition: ClassVar[URIRef] = PRISM.edition
    iri_relation: ClassVar[URIRef] = DCTERMS.relation
    iri_has_citation_creation_date: ClassVar[URIRef] = CITO.hasCitationCreationDate
    iri_has_citation_time_span: ClassVar[URIRef] = CITO.hasCitationTimeSpan
    iri_digital_manifestation: ClassVar[URIRef] = FABIO.DigitalManifestation
    iri_print_object: ClassVar[URIRef] = FABIO.PrintObject
    iri_has_url: ClassVar[URIRef] = FRBR.exemplar
    iri_self_citation: ClassVar[URIRef] = CITO.SelfCitation
    iri_affiliation_self_citation: ClassVar[URIRef] = CITO.AffiliationSelfCitation
    iri_author_network_self_citation: ClassVar[URIRef] = CITO.AuthorNetworkSelfCitation
    iri_author_self_citation: ClassVar[URIRef] = CITO.AuthorSelfCitation
    iri_funder_self_citation: ClassVar[URIRef] = CITO.FunderSelfCitation
    iri_journal_self_citation: ClassVar[URIRef] = CITO.JournalSelfCitation
    iri_journal_cartel_citation: ClassVar[URIRef] = CITO.JournalCartelCitation
    iri_distant_citation: ClassVar[URIRef] = CITO.DistantCitation
    iri_has_format: ClassVar[URIRef] = DCTERMS["format"]

    short_name_to_type_iri: ClassVar[Dict[str, URIRef]] = {
        'an': iri_note,
        'ar': iri_role_in_time,
        'be': iri_bibliographic_reference,
        'br': iri_expression,
        'ci': iri_citation,
        'de': iri_discourse_element,
        'id': iri_identifier,
        'pl': iri_singleloc_pointer_list,
        'ra': iri_agent,
        're': iri_manifestation,
        'rp': iri_intextref_pointer
    }

    def __init__(self, g: Graph, g_set: GraphSet, res: URIRef = None, res_type: URIRef = None,
                 resp_agent: str = None, source: str = None, count: str = None, label: str = None,
                 short_name: str = "", preexisting_graph: Graph = None) -> None:
        super(GraphEntity, self).__init__()
        self.g: Graph = g
        self.resp_agent: str = resp_agent
        self.source: str = source
        self.short_name: str = short_name
        self.g_set: GraphSet = g_set
        self.preexisting_graph: Graph = Graph(identifier=g.identifier)
        self._merge_list: Tuple[GraphEntity] = tuple()
        # FLAGS
        self._to_be_deleted: bool = False
        self._was_merged: bool = False

        # If res was not specified, create from scratch the URI reference for this entity,
        # otherwise use the provided one
        if res is None:
            self.res = self._generate_new_res(g, count)
        else:
            self.res = res

        if g_set is not None:
            # If not already done, register this GraphEntity instance inside the GraphSet
            if self.res not in g_set.res_to_entity:
                g_set.res_to_entity[self.res] = self

        if preexisting_graph is not None:
            # Triples inside self.g are entirely replaced by triples from preexisting_graph.
            # This has maximum priority with respect to every other self.g initializations.
            # It's fundamental that the preexisting graph gets passed as an argument of the constructor:
            # allowing the user to set this value later through a method would mean that the user could
            # set the preexisting graph AFTER having modified self.g (which would not make sense).
            self.remove_every_triple()
            for p, o in preexisting_graph.predicate_objects(self.res):
                self.g.add((self.res, p, o))
                self.preexisting_graph.add((self.res, p, o))
        else:
            # Add mandatory information to the entity graph
            self._create_type(res_type)
            if label is not None:
                self.create_label(label)

    @staticmethod
    def _generate_new_res(g: Graph, count: str) -> URIRef:
        return URIRef(str(g.identifier) + count)

    @property
    def to_be_deleted(self) -> bool:
        return self._to_be_deleted

    @property
    def was_merged(self) -> bool:
        return self._was_merged

    @property
    def merge_list(self) -> Tuple[GraphEntity]:
        return self._merge_list

    def mark_as_to_be_deleted(self) -> None:
        # Here we must REMOVE triples pointing
        # to 'self' [THIS CANNOT BE UNDONE]:
        for res, entity in self.g_set.res_to_entity.items():
            triples_list: List[Tuple] = list(entity.g.triples((res, None, self.res)))
            for triple in triples_list:
                entity.g.remove(triple)

        self._to_be_deleted = True

    def merge(self, other: GraphEntity) -> None:
        """
        **WARNING:** ``GraphEntity`` **is an abstract class that cannot be instantiated at runtime.
        As such, it's only possible to execute this method on entities generated from**
        ``GraphEntity``'s **subclasses. Please, refer to their documentation of the** `merge` **method.**

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: GraphEntity
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """

        # Here we must REDIRECT triples pointing
        # to 'other' to make them point to 'self':
        for res, entity in self.g_set.res_to_entity.items():
            triples_list: List[Tuple] = list(entity.g.triples((res, None, other.res)))
            for triple in triples_list:
                entity.g.remove(triple)
                new_triple = (triple[0], triple[1], self.res)
                entity.g.add(new_triple)

        types: List[URIRef] = other.get_types()
        for cur_type in types:
            self._create_type(cur_type)

        label: Optional[str] = other.get_label()
        if label is not None:
            self.create_label(label)

        self._was_merged = True
        self._merge_list = (*self._merge_list, other)

        # 'other' must be deleted AFTER the redirection of
        # triples pointing to it, since mark_as_to_be_deleted
        # also removes every triple pointing to 'other'
        other.mark_as_to_be_deleted()

    def commit_changes(self):
        self.preexisting_graph = Graph(identifier=self.g.identifier)
        if self._to_be_deleted:
            self.remove_every_triple()
        else:
            for triple in self.g.triples((self.res, None, None)):
                self.preexisting_graph.add(triple)
        self._to_be_deleted = False
        self._was_merged = False
        self._merge_list = tuple()
