# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
# SPDX-FileCopyrightText: 2022-2024 Arcangelo Massari <arcangelo.massari@unibo.it>
# SPDX-FileCopyrightText: 2024 martasoricetti <marta.soricetti@studio.unibo.it>
#
# SPDX-License-Identifier: ISC

from __future__ import annotations

from typing import TYPE_CHECKING

from rdflib import RDF, Namespace

from oc_ocdm.abstract_entity import AbstractEntity
from triplelite import RDFTerm, TripleLite

if TYPE_CHECKING:
    from typing import ClassVar, Dict, List, Optional, Self

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

    iri_has_subtitle: ClassVar[str] = str(FABIO.hasSubtitle)
    iri_has_publication_date: ClassVar[str] = str(PRISM.publicationDate)
    iri_bibliographic_reference: ClassVar[str] = str(BIRO.BibliographicReference)
    iri_references: ClassVar[str] = str(BIRO.references)
    iri_denotes: ClassVar[str] = str(C4O.denotes)
    iri_has_content: ClassVar[str] = str(C4O.hasContent)
    iri_intextref_pointer: ClassVar[str] = str(C4O.InTextReferencePointer)
    iri_is_context_of: ClassVar[str] = str(C4O.isContextOf)
    iri_singleloc_pointer_list: ClassVar[str] = str(C4O.SingleLocationPointerList)
    iri_has_element: ClassVar[str] = str(CO.element)
    iri_citation: ClassVar[str] = str(CITO.Citation)
    iri_cites: ClassVar[str] = str(CITO.cites)
    iri_citation_characterisation: ClassVar[str] = str(CITO.hasCitationCharacterisation)
    iri_has_citing_entity: ClassVar[str] = str(CITO.hasCitingEntity)
    iri_has_cited_entity: ClassVar[str] = str(CITO.hasCitedEntity)
    iri_openalex: ClassVar[str] = str(DATACITE.openalex)
    iri_arxiv: ClassVar[str] = str(DATACITE.arxiv)
    iri_oci: ClassVar[str] = str(DATACITE.oci)
    iri_doi: ClassVar[str] = str(DATACITE.doi)
    iri_pmid: ClassVar[str] = str(DATACITE.pmid)
    iri_pmcid: ClassVar[str] = str(DATACITE.pmcid)
    iri_orcid: ClassVar[str] = str(DATACITE.orcid)
    iri_xpath: ClassVar[str] = str(DATACITE["local-resource-identifier-scheme"])
    iri_intrepid: ClassVar[str] = str(DATACITE.intrepid)
    iri_xmlid: ClassVar[str] = str(DATACITE["local-resource-identifier-scheme"])
    iri_has_identifier: ClassVar[str] = str(DATACITE.hasIdentifier)
    iri_identifier: ClassVar[str] = str(DATACITE.Identifier)
    iri_isbn: ClassVar[str] = str(DATACITE.isbn)
    iri_issn: ClassVar[str] = str(DATACITE.issn)
    iri_url: ClassVar[str] = str(DATACITE.url)
    iri_uses_identifier_scheme: ClassVar[str] = str(DATACITE.usesIdentifierScheme)
    iri_title: ClassVar[str] = str(DCTERMS["title"])
    iri_caption: ClassVar[str] = str(DEO.Caption)
    iri_discourse_element: ClassVar[str] = str(DEO.DiscourseElement)
    iri_footnote: ClassVar[str] = str(DOCO.Footnote)
    iri_paragraph: ClassVar[str] = str(DOCO.Paragraph)
    iri_part: ClassVar[str] = str(DOCO.Part)
    iri_section: ClassVar[str] = str(DOCO.Section)
    iri_introduction: ClassVar[str] = str(DEO.Introduction)
    iri_methods: ClassVar[str] = str(DEO.Methods)
    iri_materials: ClassVar[str] = str(DEO.Materials)
    iri_related_work: ClassVar[str] = str(DEO.RelatedWork)
    iri_results: ClassVar[str] = str(DEO.Results)
    iri_discussion: ClassVar[str] = str(DEO.Discussion)
    iri_conclusion: ClassVar[str] = str(DEO.Conclusion)
    iri_section_title: ClassVar[str] = str(DOCO.SectionTitle)
    iri_sentence: ClassVar[str] = str(DOCO.Sentence)
    iri_table: ClassVar[str] = str(DOCO.Table)
    iri_text_chunk: ClassVar[str] = str(DOCO.TextChunk)
    iri_abstract: ClassVar[str] = str(DOCO.Abstract)
    iri_academic_proceedings: ClassVar[str] = str(FABIO.AcademicProceedings)
    iri_audio_document: ClassVar[str] = str(FABIO.AudioDocument)
    iri_book: ClassVar[str] = str(FABIO.Book)
    iri_book_chapter: ClassVar[str] = str(FABIO.BookChapter)
    iri_book_series: ClassVar[str] = str(FABIO.BookSeries)
    iri_book_set: ClassVar[str] = str(FABIO.BookSet)
    iri_computer_program: ClassVar[str] = str(FABIO.ComputerProgram)
    iri_data_file: ClassVar[str] = str(FABIO.DataFile)
    iri_data_management_plan: ClassVar[str] = str(FABIO.DataManagementPlan)
    iri_editorial: ClassVar[str] = str(FABIO.Editorial)
    iri_expression: ClassVar[str] = str(FABIO.Expression)
    iri_expression_collection: ClassVar[str] = str(FABIO.ExpressionCollection)
    iri_has_sequence_identifier: ClassVar[str] = str(FABIO.hasSequenceIdentifier)
    iri_journal: ClassVar[str] = str(FABIO.Journal)
    iri_journal_article: ClassVar[str] = str(FABIO.JournalArticle)
    iri_journal_editorial: ClassVar[str] = str(FABIO.JournalEditorial)
    iri_journal_issue: ClassVar[str] = str(FABIO.JournalIssue)
    iri_journal_volume: ClassVar[str] = str(FABIO.JournalVolume)
    iri_manifestation: ClassVar[str] = str(FABIO.Manifestation)
    iri_newspaper: ClassVar[str] = str(FABIO.Newspaper)
    iri_newspaper_article: ClassVar[str] = str(FABIO.NewspaperArticle)
    iri_newspaper_editorial: ClassVar[str] = str(FABIO.NewspaperEditorial)
    iri_newspaper_issue: ClassVar[str] = str(FABIO.NewspaperIssue)
    iri_peer_review: ClassVar[str] = str(FR.ReviewVersion)
    iri_preprint: ClassVar[str] = str(FABIO.Preprint)
    iri_presentation: ClassVar[str] = str(FABIO.Presentation)
    iri_proceedings_paper: ClassVar[str] = str(FABIO.ProceedingsPaper)
    iri_proceedings_series: ClassVar[str] = str(FABIO.Series)
    iri_reference_book: ClassVar[str] = str(FABIO.ReferenceBook)
    iri_reference_entry: ClassVar[str] = str(FABIO.ReferenceEntry)
    iri_report_document: ClassVar[str] = str(FABIO.ReportDocument)
    iri_retraction_notice: ClassVar[str] = str(FABIO.RetractionNotice)
    iri_series: ClassVar[str] = str(FABIO.Series)
    iri_specification_document: ClassVar[str] = str(FABIO.SpecificationDocument)
    iri_thesis: ClassVar[str] = str(FABIO.Thesis)
    iri_web_content: ClassVar[str] = str(FABIO.WebContent)
    iri_agent: ClassVar[str] = str(FOAF.Agent)
    iri_family_name: ClassVar[str] = str(FOAF.familyName)
    iri_given_name: ClassVar[str] = str(FOAF.givenName)
    iri_name: ClassVar[str] = str(FOAF.name)
    iri_embodiment: ClassVar[str] = str(FRBR.embodiment)
    iri_part_of: ClassVar[str] = str(FRBR.partOf)
    iri_contains_reference: ClassVar[str] = str(FRBR.part)
    iri_contains_de: ClassVar[str] = str(FRBR.part)
    iri_has_literal_value: ClassVar[str] = str(LITERAL.hasLiteralValue)
    iri_ending_page: ClassVar[str] = str(PRISM.endingPage)
    iri_starting_page: ClassVar[str] = str(PRISM.startingPage)
    iri_author: ClassVar[str] = str(PRO.author)
    iri_editor: ClassVar[str] = str(PRO.editor)
    iri_is_held_by: ClassVar[str] = str(PRO.isHeldBy)
    iri_publisher: ClassVar[str] = str(PRO.publisher)
    iri_is_document_context_for: ClassVar[str] = str(PRO.isDocumentContextFor)
    iri_role_in_time: ClassVar[str] = str(PRO.RoleInTime)
    iri_with_role: ClassVar[str] = str(PRO.withRole)
    iri_note: ClassVar[str] = str(OA.Annotation)
    iri_has_body: ClassVar[str] = str(OA.hasBody)
    iri_has_annotation: ClassVar[str] = str(OCO.hasAnnotation)  # inverse of OA.hasTarget
    iri_has_next: ClassVar[str] = str(OCO.hasNext)
    iri_archival_document: ClassVar[str] = str(FABIO.ArchivalDocument)
    iri_viaf: ClassVar[str] = str(DATACITE.viaf)
    iri_crossref: ClassVar[str] = str(DATACITE.crossref)  # TODO: add to datacite!
    iri_datacite: ClassVar[str] = str(DATACITE.datacite)  # TODO: add to datacite!
    iri_jid: ClassVar[str] = str(DATACITE.jid)  # TODO: add to datacite!
    iri_wikidata: ClassVar[str] = str(DATACITE.wikidata)  # TODO: add to datacite!
    iri_wikipedia: ClassVar[str] = str(DATACITE.wikipedia)  # TODO: add to datacite!
    iri_has_edition: ClassVar[str] = str(PRISM.edition)
    iri_relation: ClassVar[str] = str(DCTERMS.relation)
    iri_has_citation_creation_date: ClassVar[str] = str(CITO.hasCitationCreationDate)
    iri_has_citation_time_span: ClassVar[str] = str(CITO.hasCitationTimeSpan)
    iri_digital_manifestation: ClassVar[str] = str(FABIO.DigitalManifestation)
    iri_print_object: ClassVar[str] = str(FABIO.PrintObject)
    iri_has_url: ClassVar[str] = str(FRBR.exemplar)
    iri_self_citation: ClassVar[str] = str(CITO.SelfCitation)
    iri_affiliation_self_citation: ClassVar[str] = str(CITO.AffiliationSelfCitation)
    iri_author_network_self_citation: ClassVar[str] = str(CITO.AuthorNetworkSelfCitation)
    iri_author_self_citation: ClassVar[str] = str(CITO.AuthorSelfCitation)
    iri_funder_self_citation: ClassVar[str] = str(CITO.FunderSelfCitation)
    iri_journal_self_citation: ClassVar[str] = str(CITO.JournalSelfCitation)
    iri_journal_cartel_citation: ClassVar[str] = str(CITO.JournalCartelCitation)
    iri_distant_citation: ClassVar[str] = str(CITO.DistantCitation)
    iri_has_format: ClassVar[str] = str(DCTERMS["format"])

    short_name_to_type_iri: ClassVar[Dict[str, str]] = {
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

    def __init__(self, g: TripleLite, g_set: GraphSet, res_type: str, res: str | None = None,
                 resp_agent: str | None = None, source: str | None = None, count: str | None = None, label: str | None = None,
                 short_name: str = "", preexisting_graph: TripleLite | None = None) -> None:
        super(GraphEntity, self).__init__()
        self.g: TripleLite = g
        self.resp_agent: str | None = resp_agent
        self.source: str | None = source
        self.short_name: str = short_name
        self.g_set: GraphSet = g_set
        self._preexisting_triples: frozenset = frozenset()
        self._merge_list: tuple[GraphEntity, ...] = ()
        # FLAGS
        self._to_be_deleted: bool = False
        self._was_merged: bool = False
        self._is_restored: bool = False

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
            self.g.add_many((self.res, p, o) for p, o in preexisting_graph.predicate_objects(self.res))
            self._preexisting_triples = frozenset(self.g)
        else:
            # Add mandatory information to the entity graph
            self._create_type(res_type)
            if label is not None:
                self.create_label(label)

    @staticmethod
    def _generate_new_res(g: TripleLite, count: str | None) -> str:
        assert count is not None
        return str(g.identifier) + count

    @property
    def to_be_deleted(self) -> bool:
        return self._to_be_deleted

    @property
    def was_merged(self) -> bool:
        return self._was_merged

    @property
    def merge_list(self) -> tuple[GraphEntity, ...]:
        return self._merge_list

    @property 
    def is_restored(self) -> bool:
        """Indicates if this entity was restored after being deleted."""
        return self._is_restored

    def mark_as_restored(self) -> None:
        """
        Marks an entity as being restored after deletion.
                
        This state signals to the provenance system that:
        - No new invalidation time should be generated for the previous snapshot
        - The original deletion snapshot's invalidation time should be preserved
        - The entity should be treated as restored rather than newly created
        """
        self._to_be_deleted = False
        self._is_restored = True
            
    def mark_as_to_be_deleted(self) -> None:
        # Here we must REMOVE triples pointing
        # to 'self' [THIS CANNOT BE UNDONE]:
        for res, entity in self.g_set.res_to_entity.items():
            triples_list: List[tuple] = list(entity.g.triples((res, None, RDFTerm("uri", str(self.res)))))
            for triple in triples_list:
                entity.g.remove(triple)

        self._to_be_deleted = True

    def _get_specific_type(self) -> Optional[str]:
        base_type_str = str(self.short_name_to_type_iri[self.short_name])
        for _, _, type_uri in self.g.triples((self.res, RDF.type, None)):
            if type_uri.type == "uri" and type_uri.value != base_type_str:
                return type_uri.value
        return None

    def merge(self, other: Self, prefer_self: bool = False) -> None:
        """
        **WARNING:** ``GraphEntity`` **is an abstract class that cannot be instantiated at runtime.
        As such, it's only possible to execute this method on entities generated from**
        ``GraphEntity``'s **subclasses. Please, refer to their documentation of the** `merge` **method.**

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: GraphEntity
        :param prefer_self: If True, prefer values from the current entity for non-functional properties
        :type prefer_self: bool
        :raises TypeError: if the parameter is not of the same entity type
        :return: None
        """
        if not isinstance(other, GraphEntity) or other.short_name != self.short_name:
            raise TypeError(
                f"[{self.__class__.__name__}.merge] Expected entity type: {self.short_name}. "
                f"Provided: {type(other).__name__}."
            )

        # Redirect triples pointing to 'other' to point to 'self'
        for res, entity in self.g_set.res_to_entity.items():
            triples_list: List[tuple] = list(entity.g.triples((res, None, RDFTerm("uri", str(other.res)))))
            for triple in triples_list:
                entity.g.remove(triple)
                new_triple = (triple[0], triple[1], RDFTerm("uri", str(self.res)))
                entity.g.add(new_triple)

        self_specific_type = self._get_specific_type()
        other_specific_type = other._get_specific_type()

        final_specific_type = None
        if prefer_self and self_specific_type:
            final_specific_type = self_specific_type
        elif other_specific_type:
            final_specific_type = other_specific_type
        elif self_specific_type:
            final_specific_type = self_specific_type

        self.g.remove((self.res, RDF.type, None))
        base_type = self.short_name_to_type_iri[self.short_name]
        self.g.add((self.res, RDF.type, RDFTerm("uri", str(base_type))))
        if final_specific_type:
            self.g.add((self.res, RDF.type, RDFTerm("uri", str(final_specific_type))))

        label: Optional[str] = other.get_label()
        if label is not None:
            self.create_label(label)

        self._was_merged = True
        self._merge_list = (*self._merge_list, other)

        # 'other' must be deleted AFTER the redirection of
        # triples pointing to it, since mark_as_to_be_deleted
        # also removes every triple pointing to 'other'
        other.mark_as_to_be_deleted()

        self._merge_properties(other, prefer_self)

    def _merge_properties(self, other: GraphEntity, prefer_self: bool) -> None:
        pass

    def commit_changes(self):
        if self._to_be_deleted:
            self._preexisting_triples = frozenset()
            self.remove_every_triple()
        else:
            self._preexisting_triples = frozenset(self.g.triples((self.res, None, None)))
        self._is_restored = False
        self._to_be_deleted = False
        self._was_merged = False
        self._merge_list = tuple()