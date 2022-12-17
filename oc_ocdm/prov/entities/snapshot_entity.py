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
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.prov.prov_entity import ProvEntity

if TYPE_CHECKING:
    from typing import List, Optional

    from rdflib import URIRef


class SnapshotEntity(ProvEntity):
    """Snapshot of entity metadata (short: se): a particular snapshot recording the
    metadata associated with an individual entity (either a bibliographic entity or an
    identifier) at a particular date and time, including the agent, such as a person,
    organisation or automated process that created or modified the entity metadata."""

    # HAS CREATION DATE
    def get_generation_time(self) -> Optional[str]:
        """
        Getter method corresponding to the ``prov:generatedAtTime`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(ProvEntity.iri_generated_at_time)

    @accepts_only('literal')
    def has_generation_time(self, string: str) -> None:
        """
        Setter method corresponding to the ``prov:generatedAtTime`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The date on which a particular snapshot of a bibliographic entity's metadata was
        created.`

        :param string: The value that will be set as the object of the property related to this method. **It must
          be a string compliant with the** ``xsd:dateTime`` **datatype.**
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_generation_time()
        self._create_literal(ProvEntity.iri_generated_at_time, string, XSD.dateTime)

    def remove_generation_time(self) -> None:
        """
        Remover method corresponding to the ``prov:generatedAtTime`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, ProvEntity.iri_generated_at_time, None))

    # HAS INVALIDATION DATE
    def get_invalidation_time(self) -> Optional[str]:
        """
        Getter method corresponding to the ``prov:invalidatedAtTime`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(ProvEntity.iri_invalidated_at_time)

    @accepts_only('literal')
    def has_invalidation_time(self, string: str) -> None:
        """
        Setter method corresponding to the ``prov:invalidatedAtTime`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The date on which a snapshot of a bibliographic entity's metadata was invalidated due
        to an update (e.g. a correction, or the addition of some metadata that was not specified
        in the previous snapshot), or due to a merger of the entity with another one.`

        :param string: The value that will be set as the object of the property related to this method. **It must
          be a string compliant with the** ``xsd:dateTime`` **datatype.**
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_invalidation_time()
        self._create_literal(ProvEntity.iri_invalidated_at_time, string, XSD.dateTime)

    def remove_invalidation_time(self) -> None:
        """
        Remover method corresponding to the ``prov:invalidatedAtTime`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, ProvEntity.iri_invalidated_at_time, None))

    # IS SNAPSHOT OF
    def get_is_snapshot_of(self) -> Optional[URIRef]:
        """
        Getter method corresponding to the ``prov:specializationOf`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[URIRef] = self._get_uri_reference(ProvEntity.iri_specialization_of)
        return uri

    def is_snapshot_of(self, en_res: GraphEntity) -> None:
        """
        Setter method corresponding to the ``prov:specializationOf`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `This property is used to link a snapshot of entity metadata to the bibliographic entity
        to which the snapshot refers.`

        :param en_res: The value that will be set as the object of the property related to this method
        :type en_res: GraphEntity
        :return: None
        """
        self.remove_is_snapshot_of()
        self.g.add((self.res, ProvEntity.iri_specialization_of, en_res.res))

    def remove_is_snapshot_of(self) -> None:
        """
        Remover method corresponding to the ``prov:specializationOf`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, ProvEntity.iri_specialization_of, None))

    # IS DERIVED FROM
    def get_derives_from(self) -> List[ProvEntity]:
        """
        Getter method corresponding to the ``prov:wasDerivedFrom`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(ProvEntity.iri_was_derived_from, 'se')
        result: List[ProvEntity] = []
        for uri in uri_list:
            # TODO: what is the prov_subject of these snapshots?
            result.append(self.p_set.add_se(None, uri))
        return result

    @accepts_only('se')
    def derives_from(self, se_res: ProvEntity) -> None:
        """
        Setter method corresponding to the ``prov:wasDerivedFrom`` RDF predicate.

        `This property is used to identify the immediately previous snapshot of entity metadata
        associated with the same bibliographic entity.`

        :param se_res: The value that will be set as the object of the property related to this method
        :type se_res: ProvEntity
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, ProvEntity.iri_was_derived_from, se_res.res))

    @accepts_only('se')
    def remove_derives_from(self, se_res: ProvEntity = None) -> None:
        """
        Remover method corresponding to the ``prov:wasDerivedFrom`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param se_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type se_res: SnapshotEntity
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if se_res is not None:
            self.g.remove((self.res, ProvEntity.iri_was_derived_from, se_res.res))
        else:
            self.g.remove((self.res, ProvEntity.iri_was_derived_from, None))

    # HAS PRIMARY SOURCE
    def get_primary_source(self) -> Optional[URIRef]:
        """
        Getter method corresponding to the ``prov:hadPrimarySource`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[URIRef] = self._get_uri_reference(ProvEntity.iri_had_primary_source)
        return uri

    @accepts_only('thing')
    def has_primary_source(self, any_res: URIRef) -> None:
        """
        Setter method corresponding to the ``prov:hadPrimarySource`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `This property is used to identify the primary source from which the metadata
        described in the snapshot are derived (e.g. Crossref, as the result of querying the
        CrossRef API).`

        :param any_res: The value that will be set as the object of the property related to this method
        :type any_res: URIRef
        :return: None
        """
        self.remove_primary_source()
        self.g.add((self.res, ProvEntity.iri_had_primary_source, any_res))

    def remove_primary_source(self) -> None:
        """
        Remover method corresponding to the ``prov:hadPrimarySource`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, ProvEntity.iri_had_primary_source, None))

    # HAS UPDATE ACTION
    def get_update_action(self) -> Optional[str]:
        """
        Getter method corresponding to the ``oco:hasUpdateQuery`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(ProvEntity.iri_has_update_query)

    @accepts_only('literal')
    def has_update_action(self, string: str) -> None:
        """
        Setter method corresponding to the ``oco:hasUpdateQuery`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The UPDATE SPARQL query that specifies which data, associated to the bibliographic
        entity in consideration, have been modified (e.g. for correcting a mistake) in the
        current snapshot starting from those associated to the previous snapshot of the entity.`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :return: None
        """
        self.remove_update_action()
        self._create_literal(ProvEntity.iri_has_update_query, string)

    def remove_update_action(self) -> None:
        """
        Remover method corresponding to the ``oco:hasUpdateQuery`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, ProvEntity.iri_has_update_query, None))

    # HAS DESCRIPTION
    def get_description(self) -> Optional[str]:
        """
        Getter method corresponding to the ``dcterms:description`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(ProvEntity.iri_description)

    @accepts_only('literal')
    def has_description(self, string: str) -> None:
        """
        Setter method corresponding to the ``dcterms:description`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `A textual description of the events that have resulted in the current snapshot (e.g. the
        creation of the initial snapshot, the creation of a new snapshot following the
        modification of the entity to which the metadata relate, or the creation of a new
        snapshot following the merger with another entity of the entity to which the previous
        snapshot related).`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :return: None
        """
        self.remove_description()
        self._create_literal(ProvEntity.iri_description, string)

    def remove_description(self) -> None:
        """
        Remover method corresponding to the ``dcterms:description`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, ProvEntity.iri_description, None))

    # IS ATTRIBUTED TO
    def get_resp_agent(self) -> Optional[URIRef]:
        """
        Getter method corresponding to the ``prov:wasAttributedTo`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[URIRef] = self._get_uri_reference(ProvEntity.iri_was_attributed_to)
        return uri

    @accepts_only('thing')
    def has_resp_agent(self, se_agent: URIRef) -> None:
        """
        Setter method corresponding to the ``prov:wasAttributedTo`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The agent responsible for the creation of the current entity snapshot.`

        :param se_agent: The value that will be set as the object of the property related to this method
        :type se_agent: URIRef
        :return: None
        """
        self.remove_resp_agent()
        self.g.add((self.res, ProvEntity.iri_was_attributed_to, se_agent))

    def remove_resp_agent(self) -> None:
        """
        Remover method corresponding to the ``prov:wasAttributedTo`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, ProvEntity.iri_was_attributed_to, None))
