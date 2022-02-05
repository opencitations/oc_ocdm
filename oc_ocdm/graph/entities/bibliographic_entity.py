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
    from typing import List, Dict, Optional
    from rdflib import URIRef
    from oc_ocdm.graph.entities.identifier import Identifier
from oc_ocdm.graph.graph_entity import GraphEntity


class BibliographicEntity(GraphEntity):
    """The base class for each bibliographic entity of the OpenCitations DataModel (OCDM)."""

    def merge(self, other: BibliographicEntity) -> None:
        """
        **WARNING:** ``BibliographicEntity`` **is an abstract class that cannot be instantiated at runtime.
        As such, it's only possible to execute this method on entities generated from**
        ``BibliographicEntity``'s **subclasses. Please, refer to their documentation of the** `merge` **method.**

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: BibliographicEntity
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        super(BibliographicEntity, self).merge(other)

        id_list: List[Identifier] = other.get_identifiers()
        for cur_id in id_list:
            self.has_identifier(cur_id)

        # The special semantics associated to the identifiers
        # of a bibliographic entity requires them to be uniquely
        # defined based on their scheme and literal value:
        self.remove_duplicated_identifiers()

    # HAS IDENTIFIER
    def get_identifiers(self) -> List[Identifier]:
        """
        Getter method corresponding to the ``datacite:hasIdentifier`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_has_identifier, 'id')
        result: List[Identifier] = []
        for uri in uri_list:
            result.append(self.g_set.add_id(self.resp_agent, self.source, uri))
        return result

    @accepts_only('id')
    def has_identifier(self, id_res: Identifier) -> None:
        """
        Setter method corresponding to the ``datacite:hasIdentifier`` RDF predicate.

        `In addition to the internal dataset identifier assigned to the entity upon initial
        curation (format: [entity short name]/[local identifier]), other external third-party
        identifiers can be specified through this attribute (e.g. DOI, ORCID, PubMedID).`

        :param id_res: The value that will be set as the object of the property related to this method
        :type id_res: Identifier
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, GraphEntity.iri_has_identifier, id_res.res))

    @accepts_only('id')
    def remove_identifier(self, id_res: Identifier = None) -> None:
        """
        Remover method corresponding to the ``datacite:hasIdentifier`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param id_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type id_res: Identifier
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if id_res is not None:
            self.g.remove((self.res, GraphEntity.iri_has_identifier, id_res.res))
        else:
            self.g.remove((self.res, GraphEntity.iri_has_identifier, None))

    def remove_duplicated_identifiers(self) -> None:
        """
        Utility function that automatically scans the list of Identifier entities associated to the
        current bibliographic entity (through the ``datacite:hasIdentifier`` RDF predicate) and it removes
        duplicated entries.

        Two distinct ``Identifier`` entities are considered the same if they share both
        the scheme (``datacite:usesIdentifierScheme``) and the literal value (``literal:hasLiteralValue``).

        :return: None
        """

        # Identifiers should be merged based on the
        # correspondence between both their scheme and literal value!
        id_list: List[Identifier] = self.get_identifiers()
        # We remove every identifier from 'self': only unique ones
        # will be re-associated with 'self'.
        self.remove_identifier()

        # We use a nested dictionary which associates the 'schema-literal_value'
        # pair to the corresponding identifier object
        # (ex. id_dict[ISSN][1234-5678] <- base_iri:id/34).
        id_dict: Dict[URIRef, Dict[str, Identifier]] = {}
        for identifier in id_list:
            schema: Optional[URIRef] = identifier.get_scheme()
            literal_value: Optional[str] = identifier.get_literal_value()
            if schema is not None and literal_value is not None:
                if schema not in id_dict:
                    id_dict[schema] = {literal_value: identifier}
                    self.has_identifier(identifier)  # the Identifier is kept!
                else:
                    if literal_value not in id_dict[schema]:
                        id_dict[schema][literal_value] = identifier
                        self.has_identifier(identifier)  # the Identifier is kept!
                    else:
                        id_to_be_kept: Identifier = id_dict[schema][literal_value]
                        id_to_be_kept.merge(identifier)  # the Identifier is dropped!
