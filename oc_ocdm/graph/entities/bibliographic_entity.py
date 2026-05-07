#!/usr/bin/python

# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
# SPDX-FileCopyrightText: 2024 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

from triplelite import RDFTerm

from oc_ocdm.decorators import accepts_only

if TYPE_CHECKING:
    from typing import Dict, List, Optional

    from oc_ocdm.graph.entities.identifier import Identifier
from oc_ocdm.graph.graph_entity import GraphEntity


class BibliographicEntity(GraphEntity):
    """The base class for each bibliographic entity of the OpenCitations DataModel (OCDM)."""

    def _merge_properties(self, other: GraphEntity, prefer_self: bool) -> None:
        """
        Hook method called by ``merge`` to copy properties specific to bibliographic entities.
        Merges identifiers from the other entity and removes duplicates.

        :param other: The entity whose properties will be merged into the current entity.
        :type other: BibliographicEntity
        :param prefer_self: If True, prefer values from the current entity for non-functional properties
        :type prefer_self: bool
        :return: None
        """
        super()._merge_properties(other, prefer_self)
        assert isinstance(other, BibliographicEntity)

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
        uri_list: List[str] = self._get_multiple_uri_references(GraphEntity.iri_has_identifier, 'id')
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
        self.g.add((self.res, GraphEntity.iri_has_identifier, RDFTerm("uri", str(id_res.res))))

    @accepts_only('id')
    def remove_identifier(self, id_res: Identifier | None = None) -> None:
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
            self.g.remove((self.res, GraphEntity.iri_has_identifier, RDFTerm("uri", str(id_res.res))))
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
        id_dict: Dict[str, Dict[str, Identifier]] = {}
        for identifier in id_list:
            schema: Optional[str] = identifier.get_scheme()
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
