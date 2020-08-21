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

from datetime import datetime

from rdflib import URIRef, XSD

from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from oc_graphlib.bibliographic_resource import BibliographicResource
from oc_graphlib.graph_entity import GraphEntity
from oc_graphlib.bibliographic_entity import BibliographicEntity

"""
Notes about CI:
    
    Chill down, everything seems OK here!
"""


class Citation(BibliographicEntity):

    # HAS CITING DOCUMENT (BibliographicResource)
    # HAS CITED DOCUMENT (BibliographicResource)
    # <self.res> CITO:hasCitingEntity <citing_res>
    # <self.res> CITO:hasCitedEntity <cited_res>
    def _create_citation(self, citing_res: BibliographicResource, cited_res: BibliographicResource) -> None:
        self.g.add((self.res, GraphEntity.has_citing_entity, URIRef(str(citing_res))))
        self.g.add((self.res, GraphEntity.has_cited_entity, URIRef(str(cited_res))))

    # HAS CITATION CREATION DATE
    # <self.res> CITO:hasCitationCreationDate "string"
    def has_citation_creation_date(self, date_list: List[Optional[int]] = None) -> bool:
        if date_list is not None:
            l_date_list = len(date_list)
            if l_date_list != 0 and date_list[0] is not None:
                if l_date_list == 3 and \
                        ((date_list[1] is not None and date_list[1] != 1) or
                         (date_list[2] is not None and date_list[2] != 1)):
                    cur_type = XSD.date
                    string = datetime(
                        date_list[0], date_list[1], date_list[2], 0, 0).strftime('%Y-%m-%d')
                elif l_date_list == 2 and date_list[1] is not None:
                    cur_type = XSD.gYearMonth
                    string = datetime(
                        date_list[0], date_list[1], 1, 0, 0).strftime('%Y-%m')
                else:
                    cur_type = XSD.gYear
                    string = datetime(date_list[0], 1, 1, 0, 0).strftime('%Y')
                return self._create_literal(GraphEntity.has_citation_creation_date, string, cur_type, False)
        return False  # Added by @iosonopersia

    # HAS CITATION TIME SPAN
    # <self.res> CITO:hasCitationTimeSpan "string"
    def has_citation_time_span(self, string: str) -> bool:
        return self._create_literal(GraphEntity.has_citation_time_span, string, XSD.duration, False)

    # HAS CITATION CHARACTERIZATION
    # <self.res> CITO:hasCitationCharacterization <thing_ref>
    def has_citation_characterization(self, thing_ref: URIRef) -> None:
        self.g.add((self.res, GraphEntity.citation_characterisation, thing_ref))

    # ++++++++++++++++++++++++ FACTORY METHODS ++++++++++++++++++++++++
    # <self.res> RDF:type <type>

    def create_self_citation(self) -> None:  # new
        self._create_type(GraphEntity.self_citation)

