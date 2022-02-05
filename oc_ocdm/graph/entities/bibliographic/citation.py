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

from rdflib import XSD

from oc_ocdm.decorators import accepts_only
from oc_ocdm.support.support import get_datatype_from_iso_8601

if TYPE_CHECKING:
    from typing import Optional
    from rdflib import URIRef
    from oc_ocdm.graph.entities.bibliographic.bibliographic_resource import BibliographicResource
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.entities.bibliographic_entity import BibliographicEntity


class Citation(BibliographicEntity):
    """Citation (short: ci): a permanent conceptual directional link from the citing
       bibliographic resource to a cited bibliographic resource. A citation is created by the
       performative act of an author citing a published work that is relevant to the current
       work by using a particular textual device. Typically, citations are made by including a
       bibliographic reference in the reference list of the citing work and by denoting such a
       bibliographic reference using one or more in-text reference pointers (e.g. '[1]'), or by
       the inclusion within the citing work of a link, in the form of an HTTP Uniform Resource
       Locator (URL), to the cited bibliographic resource on the World Wide Web."""

    @accepts_only('ci')
    def merge(self, other: Citation) -> None:
        """
        The merge operation allows combining two ``Citation`` entities into a single one,
        by marking the second entity as to be deleted while also copying its data into the current
        ``Citation``. Moreover, every triple from the containing ``GraphSet`` referring to the second
        entity gets "redirected" to the current entity: **every other reference contained inside a
        different source (e.g. a triplestore) must be manually handled by the user!**

        In case of functional properties, values from the current entity get overwritten
        by those coming from the second entity while, in all other cases, values from the
        second entity are simply appended to those of the current entity. In this context,
        ``rdfs:label`` is considered as a functional property, while ``rdf:type`` is not.

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: Citation
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        super(Citation, self).merge(other)

        citing_br: Optional[BibliographicResource] = other.get_citing_entity()
        if citing_br is not None:
            self.has_citing_entity(citing_br)

        cited_br: Optional[BibliographicResource] = other.get_cited_entity()
        if cited_br is not None:
            self.has_cited_entity(cited_br)

        creation_date: Optional[str] = other.get_citation_creation_date()
        if creation_date is not None:
            self.has_citation_creation_date(creation_date)

        time_span: Optional[str] = other.get_citation_time_span()
        if time_span is not None:
            self.has_citation_time_span(time_span)

        characterization: Optional[URIRef] = other.get_citation_characterization()
        if characterization is not None:
            self.has_citation_characterization(characterization)

    # HAS CITING DOCUMENT (BibliographicResource)
    def get_citing_entity(self) -> Optional[BibliographicResource]:
        """
        Getter method corresponding to the ``cito:hasCitingEntity`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_has_citing_entity, 'br')
        if uri is not None:
            return self.g_set.add_br(self.resp_agent, self.source, uri)

    @accepts_only('br')
    def has_citing_entity(self, citing_res: BibliographicResource) -> None:
        """
        Setter method corresponding to the ``cito:hasCitingEntity`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The bibliographic resource which acts as the source for the citation.`

        :param citing_res: The value that will be set as the object of the property related to this method
        :type citing_res: BibliographicResource
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_citing_entity()
        self.g.add((self.res, GraphEntity.iri_has_citing_entity, citing_res.res))

    def remove_citing_entity(self) -> None:
        """
        Remover method corresponding to the ``cito:hasCitingEntity`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_citing_entity, None))

    # HAS CITED DOCUMENT (BibliographicResource)
    def get_cited_entity(self) -> Optional[BibliographicResource]:
        """
        Getter method corresponding to the ``cito:hasCitedEntity`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_has_cited_entity, 'br')
        if uri is not None:
            return self.g_set.add_br(self.resp_agent, self.source, uri)

    @accepts_only('br')
    def has_cited_entity(self, cited_res: BibliographicResource) -> None:
        """
        Setter method corresponding to the ``cito:hasCitedEntity`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The bibliographic resource which acts as the target for the citation.`

        :param cited_res: The value that will be set as the object of the property related to this method
        :type cited_res: BibliographicResource
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_cited_entity()
        self.g.add((self.res, GraphEntity.iri_has_cited_entity, cited_res.res))

    def remove_cited_entity(self) -> None:
        """
        Remover method corresponding to the ``c4o:hasCitedEntity`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_cited_entity, None))

    # HAS CITATION CREATION DATE
    def get_citation_creation_date(self) -> Optional[str]:
        """
        Getter method corresponding to the ``cito:hasCitationCreationDate`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_has_citation_creation_date)

    @accepts_only('literal')
    def has_citation_creation_date(self, string: str) -> None:
        """
        Setter method corresponding to the ``cito:hasCitationCreationDate`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The date on which the citation was created. This has the same numerical value
        as the publication date of the citing bibliographic resource, but is a property
        of the citation itself. When combined with the citation time span, it permits
        that citation to be located in history.`

        :param string: The value that will be set as the object of the property related to this method. **It must
          be a string compliant with the** ``ISO 8601`` **standard.**
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        cur_type, string = get_datatype_from_iso_8601(string)
        if cur_type is not None and string is not None:
            self.remove_citation_creation_date()
            self._create_literal(GraphEntity.iri_has_citation_creation_date, string, cur_type, False)

    def remove_citation_creation_date(self) -> None:
        """
        Remover method corresponding to the ``c4o:hasCitationCreationDate`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_citation_creation_date, None))

    # HAS CITATION TIME SPAN
    def get_citation_time_span(self) -> Optional[str]:
        """
        Getter method corresponding to the ``cito:hasCitationTimeSpan`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_has_citation_time_span)

    @accepts_only('literal')
    def has_citation_time_span(self, string: str) -> None:
        """
        Setter method corresponding to the ``cito:hasCitationTimeSpan`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The date interval between the publication date of the cited bibliographic resource and
        the publication date of the citing bibliographic resource.`

        :param string: The value that will be set as the object of the property related to this method. **It must
          be a string compliant with the** ``xsd:duration`` **datatype.**
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_citation_time_span()
        self._create_literal(GraphEntity.iri_has_citation_time_span, string, XSD.duration, False)

    def remove_citation_time_span(self) -> None:
        """
        Remover method corresponding to the ``c4o:hasCitationTimeSpan`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_citation_time_span, None))

    # HAS CITATION CHARACTERIZATION
    def get_citation_characterization(self) -> Optional[URIRef]:
        """
        Getter method corresponding to the ``cito:hasCitationCharacterisation`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_citation_characterisation)
        return uri

    @accepts_only('thing')
    def has_citation_characterization(self, thing_res: URIRef) -> None:
        """
        Setter method corresponding to the ``cito:hasCitationCharacterisation`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The citation function characterizing the purpose of the citation.`

        :param thing_res: The value that will be set as the object of the property related to this method
        :type thing_res: URIRef
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_citation_characterization()
        self.g.add((self.res, GraphEntity.iri_citation_characterisation, thing_res))

    def remove_citation_characterization(self) -> None:
        """
        Remover method corresponding to the ``c4o:hasCitationCharacterisation`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_citation_characterisation, None))

    # HAS TYPE
    def create_self_citation(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``cito:SelfCitation``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        :return: None
        """
        self._create_type(GraphEntity.iri_self_citation)

    def create_affiliation_self_citation(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``cito:AffiliationSelfCitation``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        :return: None
        """
        self._create_type(GraphEntity.iri_affiliation_self_citation)

    def create_author_network_self_citation(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``cito:AuthorNetworkSelfCitation``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        :return: None
        """
        self._create_type(GraphEntity.iri_author_network_self_citation)

    def create_author_self_citation(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``cito:AuthorSelfCitation``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        :return: None
        """
        self._create_type(GraphEntity.iri_author_self_citation)

    def create_funder_self_citation(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``cito:FunderSelfCitation``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        :return: None
        """
        self._create_type(GraphEntity.iri_funder_self_citation)

    def create_journal_self_citation(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``cito:JournalSelfCitation``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        :return: None
        """
        self._create_type(GraphEntity.iri_journal_self_citation)

    def create_journal_cartel_citation(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``cito:JournalCartelCitation``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        :return: None
        """
        self._create_type(GraphEntity.iri_journal_cartel_citation)

    def create_distant_citation(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``cito:DistantCitation``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        :return: None
        """
        self._create_type(GraphEntity.iri_distant_citation)
