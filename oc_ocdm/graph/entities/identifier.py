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

from oc_ocdm.decorators import accepts_only
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.support.support import encode_url, is_string_empty


class Identifier(GraphEntity):
    """Identifier (short: id): an external identifier (e.g. DOI, ORCID, PubMedID, Open
       Citation Identifier) associated with the bibliographic entity. Members of this class of
       metadata are themselves given unique corpus identifiers e.g. 'id/0420129'."""

    @accepts_only('id')
    def merge(self, other: Identifier):
        """
        The merge operation allows combining two ``Identifier`` entities into a single one,
        by marking the second entity as to be deleted while also copying its data into the current
        ``Identifier``. Moreover, every triple from the containing ``GraphSet`` referring to the second
        entity gets "redirected" to the current entity: **every other reference contained inside a
        different source (e.g. a triplestore) must be manually handled by the user!**

        In case of functional properties, values from the current entity get overwritten
        by those coming from the second entity while, in all other cases, values from the
        second entity are simply appended to those of the current entity. In this context,
        ``rdfs:label`` is considered as a functional property, while ``rdf:type`` is not.

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: Identifier
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        super(Identifier, self).merge(other)

        literal_value: Optional[str] = other.get_literal_value()
        scheme: Optional[URIRef] = other.get_scheme()
        if literal_value is not None and scheme is not None:
            self._associate_identifier_with_scheme(literal_value, scheme)

    # HAS LITERAL VALUE and HAS SCHEME
    def get_literal_value(self) -> Optional[str]:
        """
        Getter method corresponding to the ``literal:hasLiteralValue`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_has_literal_value)

    def get_scheme(self) -> Optional[URIRef]:
        """
        Getter method corresponding to the ``datacite:usesIdentifierScheme`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_uses_identifier_scheme)
        return uri

    @accepts_only('literal')
    def create_oci(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:oci`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_oci)

    @accepts_only('literal')
    def create_orcid(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:orcid`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_orcid)

    @accepts_only('literal')
    def create_openalex(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:openalex`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_openalex)

    @accepts_only('literal')
    def create_doi(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:doi`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        The string gets internally preprocessed by converting it to lowercase
        (e.g. 'DOI:10.1111/HEX.12487' becomes 'doi:10.1111/hex.12487').

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string.lower(), GraphEntity.iri_doi)

    @accepts_only('literal')
    def create_jid(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:jid`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_jid)

    @accepts_only('literal')
    def create_pmid(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:pmid`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_pmid)

    @accepts_only('literal')
    def create_pmcid(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:pmcid`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_pmcid)

    @accepts_only('literal')
    def create_issn(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:issn`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        The string gets internally preprocessed by eventually replacing long dashes with short ones
        (e.g. '1522–4501' becomes '1522-4501').

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method. **It
          must be a string different from '0000-0000'.**
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        cur_string = re.sub("–", "-", string)
        if cur_string != "0000-0000":
            self._associate_identifier_with_scheme(string, GraphEntity.iri_issn)

    @accepts_only('literal')
    def create_isbn(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:isbn`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        The string gets internally preprocessed by eventually replacing long dashes with short ones
        (e.g. '817525766–0' becomes '817525766-0').

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(re.sub("–", "-", string), GraphEntity.iri_isbn)

    @accepts_only('literal')
    def create_url(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:url`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        The string gets internally preprocessed both by converting it to lowercase
        (e.g. 'https://OPENCITATIONS.NET/' becomes 'https://opencitations.net/') and by
        applying `URL encoding` on it (e.g. 'https://opencitations.net/file name.txt'
        becomes 'https://opencitations.net/file%20name.txt').

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(encode_url(string.lower()), GraphEntity.iri_url)

    @accepts_only('literal')
    def create_xpath(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value `datacite:local-resource-identifier-scheme` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_xpath)

    @accepts_only('literal')
    def create_intrepid(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:intrepid`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_intrepid)

    @accepts_only('literal')
    def create_xmlid(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value `datacite:local-resource-identifier-scheme` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_xmlid)

    @accepts_only('literal')
    def create_wikidata(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:wikidata`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_wikidata)

    @accepts_only('literal')
    def create_wikipedia(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:wikipedia`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_wikipedia)

    @accepts_only('literal')
    def create_arxiv(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:crossref`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_arxiv)

    @accepts_only('literal')
    def create_crossref(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:crossref`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_crossref)

    @accepts_only('literal')
    def create_datacite(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:datacite`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_datacite)

    @accepts_only('literal')
    def create_viaf(self, string: str) -> None:
        """
        Setter method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.
        It implicitly sets the object value ``datacite:viaf`` for the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._associate_identifier_with_scheme(string, GraphEntity.iri_viaf)

    def _associate_identifier_with_scheme(self, string: str, id_type: URIRef) -> None:
        if not is_string_empty(string):
            self.remove_identifier_with_scheme()
            self._create_literal(GraphEntity.iri_has_literal_value, string)
            self.g.add((self.res, GraphEntity.iri_uses_identifier_scheme, id_type))

    def remove_identifier_with_scheme(self) -> None:
        """
        Remover method corresponding to both the ``literal:hasLiteralValue`` and the
        ``datacite:usesIdentifierScheme`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_literal_value, None))
        self.g.remove((self.res, GraphEntity.iri_uses_identifier_scheme, None))
