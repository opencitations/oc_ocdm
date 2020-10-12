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

__author__ = 'essepuntato'

from typing import ClassVar
from typing import TYPE_CHECKING

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDFS

if TYPE_CHECKING:
    from oc_ocdm import GraphSet
from oc_ocdm.support import create_literal,\
                                    create_type


class GraphEntity(object):
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
    FRBR: ClassVar[Namespace] = Namespace("http://purl.org/vocab/frbr/core#")
    LITERAL: ClassVar[Namespace] = Namespace("http://www.essepuntato.it/2010/06/literalreification/")
    OA: ClassVar[Namespace] = Namespace("http://www.w3.org/ns/oa#")
    OCO: ClassVar[Namespace] = Namespace("https://w3id.org/oc/ontology/")
    PRISM: ClassVar[Namespace] = Namespace("http://prismstandard.org/namespaces/basic/2.0/")
    PRO: ClassVar[Namespace] = Namespace("http://purl.org/spar/pro/")

    # Bibliographic entities
    has_subtitle: ClassVar[URIRef] = FABIO.hasSubtitle
    has_publication_date: ClassVar[URIRef] = PRISM.publicationDate
    bibliographic_reference: ClassVar[URIRef] = BIRO.BibliographicReference
    references: ClassVar[URIRef] = BIRO.references
    denotes: ClassVar[URIRef] = C4O.denotes
    has_content: ClassVar[URIRef] = C4O.hasContent
    intextref_pointer: ClassVar[URIRef] = C4O.InTextReferencePointer
    is_context_of: ClassVar[URIRef] = C4O.isContextOf
    singleloc_pointer_list: ClassVar[URIRef] = C4O.SingleLocationPointerList
    has_element: ClassVar[URIRef] = CO.element
    citation: ClassVar[URIRef] = CITO.Citation
    cites: ClassVar[URIRef] = CITO.cites
    citation_characterisation: ClassVar[URIRef] = CITO.hasCitationCharacterisation
    has_citing_entity: ClassVar[URIRef] = CITO.hasCitingEntity
    has_cited_entity: ClassVar[URIRef] = CITO.hasCitedEntity
    oci: ClassVar[URIRef] = DATACITE.oci
    doi: ClassVar[URIRef] = DATACITE.doi
    occ: ClassVar[URIRef] = DATACITE.occ
    pmid: ClassVar[URIRef] = DATACITE.pmid
    pmcid: ClassVar[URIRef] = DATACITE.pmcid
    orcid: ClassVar[URIRef] = DATACITE.orcid
    xpath: ClassVar[URIRef] = DATACITE["local-resource-identifier-scheme"]
    intrepid: ClassVar[URIRef] = DATACITE["intrepid"]
    xmlid: ClassVar[URIRef] = DATACITE["local-resource-identifier-scheme"]
    has_identifier: ClassVar[URIRef] = DATACITE.hasIdentifier
    identifier: ClassVar[URIRef] = DATACITE.Identifier
    isbn: ClassVar[URIRef] = DATACITE.isbn
    issn: ClassVar[URIRef] = DATACITE.issn
    url: ClassVar[URIRef] = DATACITE.url
    uses_identifier_scheme: ClassVar[URIRef] = DATACITE.usesIdentifierScheme
    title: ClassVar[URIRef] = DCTERMS["title"]
    caption: ClassVar[URIRef] = DEO.Caption
    discourse_element: ClassVar[URIRef] = DEO.DiscourseElement
    footnote: ClassVar[URIRef] = DOCO.Footnote
    paragraph: ClassVar[URIRef] = DOCO.Paragraph
    part: ClassVar[URIRef] = DOCO.Part
    section: ClassVar[URIRef] = DOCO.Section
    section_title: ClassVar[URIRef] = DOCO.SectionTitle
    sentence: ClassVar[URIRef] = DOCO.Sentence
    table: ClassVar[URIRef] = DOCO.Table
    text_chunk: ClassVar[URIRef] = DOCO.TextChunk
    academic_proceedings: ClassVar[URIRef] = FABIO.AcademicProceedings
    book: ClassVar[URIRef] = FABIO.Book
    book_chapter: ClassVar[URIRef] = FABIO.BookChapter
    book_series: ClassVar[URIRef] = FABIO.BookSeries
    book_set: ClassVar[URIRef] = FABIO.BookSet
    data_file: ClassVar[URIRef] = FABIO.DataFile
    expression: ClassVar[URIRef] = FABIO.Expression
    expression_collection: ClassVar[URIRef] = FABIO.ExpressionCollection
    has_sequence_identifier: ClassVar[URIRef] = FABIO.hasSequenceIdentifier
    journal: ClassVar[URIRef] = FABIO.Journal
    journal_article: ClassVar[URIRef] = FABIO.JournalArticle
    journal_issue: ClassVar[URIRef] = FABIO.JournalIssue
    journal_volume: ClassVar[URIRef] = FABIO.JournalVolume
    manifestation: ClassVar[URIRef] = FABIO.Manifestation
    proceedings_paper: ClassVar[URIRef] = FABIO.ProceedingsPaper
    reference_book: ClassVar[URIRef] = FABIO.ReferenceBook
    reference_entry: ClassVar[URIRef] = FABIO.ReferenceEntry
    report_document: ClassVar[URIRef] = FABIO.ReportDocument
    series: ClassVar[URIRef] = FABIO.Series
    specification_document: ClassVar[URIRef] = FABIO.SpecificationDocument
    thesis: ClassVar[URIRef] = FABIO.Thesis
    agent: ClassVar[URIRef] = FOAF.Agent
    family_name: ClassVar[URIRef] = FOAF.familyName
    given_name: ClassVar[URIRef] = FOAF.givenName
    name: ClassVar[URIRef] = FOAF.name
    embodiment: ClassVar[URIRef] = FRBR.embodiment
    part_of: ClassVar[URIRef] = FRBR.partOf
    contains_reference: ClassVar[URIRef] = FRBR.part
    contains_de: ClassVar[URIRef] = FRBR.part
    has_literal_value: ClassVar[URIRef] = LITERAL.hasLiteralValue
    ending_page: ClassVar[URIRef] = PRISM.endingPage
    starting_page: ClassVar[URIRef] = PRISM.startingPage
    author: ClassVar[URIRef] = PRO.author
    editor: ClassVar[URIRef] = PRO.editor
    is_held_by: ClassVar[URIRef] = PRO.isHeldBy
    publisher: ClassVar[URIRef] = PRO.publisher
    is_document_context_for: ClassVar[URIRef] = PRO.isDocumentContextFor
    role_in_time: ClassVar[URIRef] = PRO.RoleInTime
    with_role: ClassVar[URIRef] = PRO.withRole
    note: ClassVar[URIRef] = OA.Annotation
    has_body: ClassVar[URIRef] = OA.hasBody
    has_annotation: ClassVar[URIRef] = OCO.hasAnnotation  # inverse of OA.hasTarget
    has_next: ClassVar[URIRef] = OCO.hasNext
    archival_document: ClassVar[URIRef] = FABIO.ArchivalDocument
    viaf: ClassVar[URIRef] = DATACITE.viaf
    crossref: ClassVar[URIRef] = DATACITE.crossref  # TODO: add to datacite!
    wikidata: ClassVar[URIRef] = DATACITE.wikidata  # TODO: add to datacite!
    has_edition: ClassVar[URIRef] = PRISM.edition
    relation: ClassVar[URIRef] = DCTERMS.relation
    has_citation_creation_date: ClassVar[URIRef] = CITO.hasCitationCreationDate
    has_citation_time_span: ClassVar[URIRef] = CITO.hasCitationTimeSpan
    digital_manifestation: ClassVar[URIRef] = FABIO.DigitalManifestation
    print_object: ClassVar[URIRef] = FABIO.PrintObject
    has_url: ClassVar[URIRef] = FRBR.exemplar
    self_citation: ClassVar[URIRef] = CITO.SelfCitation
    affiliation_self_citation: ClassVar[URIRef] = CITO.AffiliationSelfCitation
    author_network_self_citation: ClassVar[URIRef] = CITO.AuthorNetworkSelfCitation
    author_self_citation: ClassVar[URIRef] = CITO.AuthorSelfCitation
    funder_self_citation: ClassVar[URIRef] = CITO.FunderSelfCitation
    journal_self_citation: ClassVar[URIRef] = CITO.JournalSelfCitation
    journal_cartel_citation: ClassVar[URIRef] = CITO.JournalCartelCitation
    distant_citation: ClassVar[URIRef] = CITO.DistantCitation
    has_format: ClassVar[URIRef] = DCTERMS["format"]

    def __init__(self, g: Graph, res: URIRef = None, res_type: URIRef = None, resp_agent: str = None,
                 source_agent: str = None, source: str = None, count: str = None, label: str = None,
                 short_name: str = "", g_set: GraphSet = None, forced_type: bool = False) -> None:
        self.cur_name: str = "SPACIN " + self.__class__.__name__
        self.resp_agent: str = resp_agent
        self.source_agent: str = source_agent
        self.source: str = source
        self.short_name: str = short_name

        existing_ref: bool = False

        # If res was not specified, create from scratch the URI reference for this entity,
        # otherwise use the provided one
        if res is None:
            self.res = self._generate_new_res(g, count, short_name)
        else:
            self.res = res
            existing_ref = True

        if g_set is not None:
            if self.res in g_set.entity_g:
                # Use the rdflib.Graph already registered inside the GraphSet
                self.g = g_set.entity_g[self.res]
            else:
                # Use the provided rdflib.Graph and register it inside the GraphSet
                self.g = g
                g_set.entity_g[self.res] = self.g

            # If not already done, register this GraphEntity instance inside the GraphSet
            if self.res not in g_set.res_to_entity:
                g_set.res_to_entity[self.res] = self

        # If this object represents a new entity in the dataset,
        # add all the additional information to it
        if not existing_ref or forced_type:
            self._create_type(res_type)

            # It creates the label
            if label is not None:
                self.create_label(label)

    @staticmethod
    def _generate_new_res(g: Graph, count: str, short_name: str = "") -> URIRef:
        return URIRef(str(g.identifier) + count)

    def remove_entity(self):
        self.g.remove((None, None, None))

    def create_label(self, string: str) -> bool:
        """Creates the RDF triple <self.res> rdfs:label <string>
        inside the graph self.g

        :param string: The string to be added as a label for this entity
        :type string: str
        :return: The outcome of the operation
        :rtype: bool
        """
        return self._create_literal(RDFS.label, string)

    def _create_literal(self, p: URIRef, s: str, dt: URIRef = None, nor: bool = True) -> bool:
        """Creates an RDF triple with a literal object inside the graph self.g

        :param p: The predicate
        :type p: URIRef
        :param s: The string to add as a literal value
        :type s: str
        :param dt: The object's datatype, if present
        :type dt: URIRef, optional
        :param nor: Whether to normalize the graph or not
        :type nor: bool, optional
        :return: The outcome of the operation
        :rtype: bool
        """
        return create_literal(self.g, self.res, p, s, dt, nor)

    def _create_type(self, res_type: URIRef) -> None:
        """Creates the RDF triple <self.res> rdf:type <res_type>
        inside the graph self.g

        :param res_type: The RDF class to be associated with this entity
        :type res_type: URIRef
        :rtype: None
        """
        create_type(self.g, self.res, res_type)

    # Overrides __str__ method
    def __str__(self) -> str:
        return str(self.res)

    def add_triples(self, iterable_of_triples) -> None:
        for s, p, o in iterable_of_triples:
            if s == self.res:  # This guarantees that only triples belonging to the resource will be added
                self.g.add((s, p, o))
