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

from rdflib import URIRef, XSD

from typing import TYPE_CHECKING, Optional, List

from oc_ocdm.support.support import create_date

if TYPE_CHECKING:
    from oc_ocdm.bibliographic_resource import BibliographicResource
from oc_ocdm.graph_entity import GraphEntity
from oc_ocdm.bibliographic_entity import BibliographicEntity

"""
Notes about CI:
    
    Chill down, everything seems OK here!
"""


class Citation(BibliographicEntity):
    """Citation (short: ci): a permanent conceptual directional link from the citing
       bibliographic resource to a cited bibliographic resource. A citation is created by the
       performative act of an author citing a published work that is relevant to the current
       work by using a particular textual device. Typically, citations are made by including a
       bibliographic reference in the reference list of the citing work and by denoting such a
       bibliographic reference using one or more in-text reference pointers (e.g. '[1]'), or by
       the inclusion within the citing work of a link, in the form of an HTTP Uniform Resource
       Locator (URL), to the cited bibliographic resource on the World Wide Web."""

    # HAS CITING DOCUMENT (BibliographicResource)
    # HAS CITED DOCUMENT (BibliographicResource)
    # <self.res> CITO:hasCitingEntity <citing_res>
    # <self.res> CITO:hasCitedEntity <cited_res>
    def _create_citation(self, citing_res: BibliographicResource, cited_res: BibliographicResource) -> None:
        """The bibliographic resource which acts as the source for the citation and the
        bibliographic resource which acts as the target for the citation.
        """
        self.g.add((self.res, GraphEntity.has_citing_entity, URIRef(str(citing_res))))
        self.g.add((self.res, GraphEntity.has_cited_entity, URIRef(str(cited_res))))

    # HAS CITATION CREATION DATE
    # <self.res> CITO:hasCitationCreationDate "string"
    def has_citation_creation_date(self, date_list: List[Optional[int]] = None) -> bool:
        """The date on which the citation was created. This has the same numerical value
        as the publication date of the citing bibliographic resource, but is a property
        of the citation itself. When combined with the citation time span, it permits
        that citation to be located in history.
        """
        cur_type, string = create_date(date_list)
        if cur_type is not None and string is not None:
            return self._create_literal(GraphEntity.has_citation_creation_date, string, cur_type, False)
        return False  # Added by @iosonopersia

    # HAS CITATION TIME SPAN
    # <self.res> CITO:hasCitationTimeSpan "string"
    def has_citation_time_span(self, string: str) -> bool:
        """The date interval between the publication date of the cited bibliographic resource and
        the publication date of the citing bibliographic resource.
        """
        return self._create_literal(GraphEntity.has_citation_time_span, string, XSD.duration, False)

    # HAS CITATION CHARACTERIZATION
    # <self.res> CITO:hasCitationCharacterization <thing_ref>
    def has_citation_characterization(self, thing_ref: URIRef) -> None:
        """The citation function characterizing the purpose of the citation.
        """
        self.g.add((self.res, GraphEntity.citation_characterisation, thing_ref))

    # ++++++++++++++++++++++++ FACTORY METHODS ++++++++++++++++++++++++
    # <self.res> RDF:type <type>

    def create_self_citation(self) -> None:  # new
        self._create_type(GraphEntity.self_citation)

    def create_affiliation_self_citation(self) -> None:
        self._create_type(GraphEntity.affiliation_self_citation)

    def create_author_network_self_citation(self) -> None:
        self._create_type(GraphEntity.author_network_self_citation)

    def create_author_self_citation(self) -> None:
        self._create_type(GraphEntity.author_self_citation)

    def create_funder_self_citation(self) -> None:
        self._create_type(GraphEntity.funder_self_citation)

    def create_journal_self_citation(self) -> None:
        self._create_type(GraphEntity.journal_self_citation)

    def create_journal_cartel_citation(self) -> None:
        self._create_type(GraphEntity.journal_cartel_citation)

    def create_distant_citation(self) -> None:
        self._create_type(GraphEntity.distant_citation)
