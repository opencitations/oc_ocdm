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

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from rdflib import URIRef

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.decorators import accepts_only
from oc_ocdm.support.support import is_string_empty, encode_url

"""
Notes about ID:

    HAS LITERAL VALUE and HAS SCHEME are generated by factory methods!
    Chill down, everything seems OK here!
"""


class Identifier(GraphEntity):
    """Identifier (short: id): an external identifier (e.g. DOI, ORCID, PubMedID, Open
       Citation Identifier) associated with the bibliographic entity. Members of this class of
       metadata are themselves given unique corpus identifiers e.g. 'id/0420129'."""

    @accepts_only('id')
    def merge(self, other: Identifier):
        super(Identifier, self).merge(other)

        literal_value: Optional[str] = other.get_literal_value()
        scheme: Optional[URIRef] = other.get_scheme()
        if literal_value is not None and scheme is not None:
            self._associate_identifier_with_scheme(literal_value, scheme)

    # HAS LITERAL VALUE and HAS SCHEME
    def get_literal_value(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_has_literal_value)

    def get_scheme(self) -> Optional[URIRef]:
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_uses_identifier_scheme)
        return uri

    @accepts_only('literal')
    def create_oci(self, string: str) -> None:
        self._associate_identifier_with_scheme(string, GraphEntity.iri_oci)

    @accepts_only('literal')
    def create_orcid(self, string: str) -> None:
        self._associate_identifier_with_scheme(string, GraphEntity.iri_orcid)

    @accepts_only('literal')
    def create_doi(self, string: str) -> None:
        self._associate_identifier_with_scheme(string.lower(), GraphEntity.iri_doi)

    @accepts_only('literal')
    def create_pmid(self, string: str) -> None:
        self._associate_identifier_with_scheme(string, GraphEntity.iri_pmid)

    @accepts_only('literal')
    def create_pmcid(self, string: str) -> None:
        self._associate_identifier_with_scheme(string, GraphEntity.iri_pmcid)

    @accepts_only('literal')
    def create_issn(self, string: str) -> None:
        cur_string = re.sub("–", "-", string)
        if cur_string != "0000-0000":
            self._associate_identifier_with_scheme(string, GraphEntity.iri_issn)

    @accepts_only('literal')
    def create_isbn(self, string: str) -> None:
        self._associate_identifier_with_scheme(re.sub("–", "-", string), GraphEntity.iri_isbn)

    @accepts_only('literal')
    def create_url(self, string: str) -> None:
        self._associate_identifier_with_scheme(encode_url(string.lower()), GraphEntity.iri_url)

    @accepts_only('literal')
    def create_xpath(self, string: str) -> None:
        self._associate_identifier_with_scheme(string, GraphEntity.iri_xpath)

    @accepts_only('literal')
    def create_intrepid(self, string: str) -> None:
        self._associate_identifier_with_scheme(string, GraphEntity.iri_intrepid)

    @accepts_only('literal')
    def create_xmlid(self, string: str) -> None:
        self._associate_identifier_with_scheme(string, GraphEntity.iri_xmlid)

    @accepts_only('literal')
    def create_wikidata(self, string: str) -> None:
        self._associate_identifier_with_scheme(string, GraphEntity.iri_wikidata)

    @accepts_only('literal')
    def create_wikipedia(self, string: str) -> None:
        self._associate_identifier_with_scheme(string, GraphEntity.iri_wikipedia)

    @accepts_only('literal')
    def create_crossref(self, string: str) -> None:
        self._associate_identifier_with_scheme(string, GraphEntity.iri_crossref)

    @accepts_only('literal')
    def create_viaf(self, string: str) -> None:
        self._associate_identifier_with_scheme(string, GraphEntity.iri_viaf)

    def _associate_identifier_with_scheme(self, string: str, id_type: URIRef) -> None:
        if not is_string_empty(string):
            self.remove_identifier_with_scheme()
            self._create_literal(GraphEntity.iri_has_literal_value, string)
            self.g.add((self.res, GraphEntity.iri_uses_identifier_scheme, id_type))

    def remove_identifier_with_scheme(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_literal_value, None))
        self.g.remove((self.res, GraphEntity.iri_uses_identifier_scheme, None))
