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
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_has_citing_entity)
        if uri is not None:
            return self.g_set.add_br(self.resp_agent, self.source_agent, self.source, uri)

    @accepts_only('br')
    def has_citing_entity(self, citing_res: BibliographicResource) -> None:
        """The bibliographic resource which acts as the source for the citation.
        """
        self.remove_citing_entity()
        self.g.add((self.res, GraphEntity.iri_has_citing_entity, citing_res.res))

    def remove_citing_entity(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_citing_entity, None))

    # HAS CITED DOCUMENT (BibliographicResource)
    def get_cited_entity(self) -> Optional[BibliographicResource]:
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_has_cited_entity)
        if uri is not None:
            return self.g_set.add_br(self.resp_agent, self.source_agent, self.source, uri)

    @accepts_only('br')
    def has_cited_entity(self, cited_res: BibliographicResource) -> None:
        """ The bibliographic resource which acts as the target for the citation.
        """
        self.remove_cited_entity()
        self.g.add((self.res, GraphEntity.iri_has_cited_entity, cited_res.res))

    def remove_cited_entity(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_cited_entity, None))

    # HAS CITATION CREATION DATE
    def get_citation_creation_date(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_has_citation_creation_date)

    @accepts_only('literal')
    def has_citation_creation_date(self, string: str) -> None:
        """The date on which the citation was created. This has the same numerical value
        as the publication date of the citing bibliographic resource, but is a property
        of the citation itself. When combined with the citation time span, it permits
        that citation to be located in history.
        """
        cur_type, string = get_datatype_from_iso_8601(string)
        if cur_type is not None and string is not None:
            self.remove_citation_creation_date()
            self._create_literal(GraphEntity.iri_has_citation_creation_date, string, cur_type, False)

    def remove_citation_creation_date(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_citation_creation_date, None))

    # HAS CITATION TIME SPAN
    def get_citation_time_span(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_has_citation_time_span)

    @accepts_only('literal')
    def has_citation_time_span(self, string: str) -> None:
        """The date interval between the publication date of the cited bibliographic resource and
        the publication date of the citing bibliographic resource.
        """
        self.remove_citation_time_span()
        self._create_literal(GraphEntity.iri_has_citation_time_span, string, XSD.duration, False)

    def remove_citation_time_span(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_citation_time_span, None))

    # HAS CITATION CHARACTERIZATION
    def get_citation_characterization(self) -> Optional[URIRef]:
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_citation_characterisation)
        return uri

    @accepts_only('thing')
    def has_citation_characterization(self, thing_ref: URIRef) -> None:
        """The citation function characterizing the purpose of the citation.
        """
        self.remove_citation_characterization()
        self.g.add((self.res, GraphEntity.iri_citation_characterisation, thing_ref))

    def remove_citation_characterization(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_citation_characterisation, None))

    # HAS TYPE
    def create_self_citation(self) -> None:
        self._create_type(GraphEntity.iri_self_citation)

    def create_affiliation_self_citation(self) -> None:
        self._create_type(GraphEntity.iri_affiliation_self_citation)

    def create_author_network_self_citation(self) -> None:
        self._create_type(GraphEntity.iri_author_network_self_citation)

    def create_author_self_citation(self) -> None:
        self._create_type(GraphEntity.iri_author_self_citation)

    def create_funder_self_citation(self) -> None:
        self._create_type(GraphEntity.iri_funder_self_citation)

    def create_journal_self_citation(self) -> None:
        self._create_type(GraphEntity.iri_journal_self_citation)

    def create_journal_cartel_citation(self) -> None:
        self._create_type(GraphEntity.iri_journal_cartel_citation)

    def create_distant_citation(self) -> None:
        self._create_type(GraphEntity.iri_distant_citation)
