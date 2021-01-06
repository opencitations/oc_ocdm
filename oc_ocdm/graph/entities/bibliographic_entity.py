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

if TYPE_CHECKING:
    from typing import List
    from rdflib import URIRef
    from oc_ocdm.graph.entities.identifier import Identifier
from oc_ocdm.graph.graph_entity import GraphEntity

"""
Notes about BibliographicEntity:

    Chill down, everything seems OK here!
"""


class BibliographicEntity(GraphEntity):
    """The base class for each bibliographic entity of the OpenCitations DataModel (OCDM)."""

    def merge(self, other: BibliographicEntity) -> None:
        super(BibliographicEntity, self).merge(other)
        id_list: List[Identifier] = other.get_identifiers()
        for cur_id in id_list:
            self.has_identifier(cur_id)

    # HAS IDENTIFIER
    def get_identifiers(self) -> List[Identifier]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_has_identifier)
        result: List[Identifier] = []
        for uri in uri_list:
            result.append(self.g_set.add_id(self.resp_agent, self.source_agent, self.source, uri))
        return result

    @accepts_only('id')
    def has_identifier(self, id_res: Identifier) -> None:
        """In addition to the internal dataset identifier assigned to the entity upon initial
        curation (format: [entity short name]/[local identifier]), other external third-party
        identifiers can be specified through this attribute (e.g. DOI, ORCID, PubMedID).
        """
        self.g.add((self.res, GraphEntity.iri_has_identifier, id_res.res))

    @accepts_only('id')
    def remove_identifier(self, id_res: Identifier = None) -> None:
        if id_res is not None:
            self.g.remove((self.res, GraphEntity.iri_has_identifier, id_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_has_identifier, None))
