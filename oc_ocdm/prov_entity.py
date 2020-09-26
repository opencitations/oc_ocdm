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

__author__ = 'essepuntato'

from typing import TYPE_CHECKING, ClassVar

from rdflib import Namespace, URIRef, Graph
from rdflib.namespace import XSD

if TYPE_CHECKING:
    from oc_ocdm.prov_set import ProvSet
    from oc_ocdm.entities.bibliographic.responsible_agent import ResponsibleAgent
from oc_ocdm.graph_entity import GraphEntity

"""
Notes about SE:

    Chill down, everything seems OK here!
"""


class ProvEntity(GraphEntity):
    """Snapshot of entity metadata (short: se): a particular snapshot recording the
    metadata associated with an individual entity (either a bibliographic entity or an
    identifier) at a particular date and time, including the agent, such as a person,
    organisation or automated process that created or modified the entity metadata.
    """

    PROV: ClassVar[Namespace] = Namespace("http://www.w3.org/ns/prov#")

    # Exclusive provenance entities
    prov_agent: ClassVar[URIRef] = PROV.Agent
    entity: ClassVar[URIRef] = PROV.Entity
    activity: ClassVar[URIRef] = PROV.Activity
    create: ClassVar[URIRef] = PROV.Create
    modify: ClassVar[URIRef] = PROV.Modify
    replace: ClassVar[URIRef] = PROV.Replace
    association: ClassVar[URIRef] = PROV.Association
    generated_at_time: ClassVar[URIRef] = PROV.generatedAtTime
    invalidated_at_time: ClassVar[URIRef] = PROV.invalidatedAtTime
    specialization_of: ClassVar[URIRef] = PROV.specializationOf
    was_derived_from: ClassVar[URIRef] = PROV.wasDerivedFrom
    had_primary_source: ClassVar[URIRef] = PROV.hadPrimarySource
    was_generated_by: ClassVar[URIRef] = PROV.wasGeneratedBy
    was_attributed_to: ClassVar[URIRef] = PROV.wasAttributedTo  #  new
    was_invalidated_by: ClassVar[URIRef] = PROV.wasInvalidatedBy
    qualified_association: ClassVar[URIRef] = PROV.qualifiedAssociation
    description: ClassVar[URIRef] = GraphEntity.DCTERMS.description
    has_update_query: ClassVar[URIRef] = GraphEntity.OCO.hasUpdateQuery
    had_role: ClassVar[URIRef] = PROV.hadRole
    associated_agent: ClassVar[URIRef] = PROV.agent
    curator: ClassVar[URIRef] = GraphEntity.OCO["occ-curator"]
    source_provider: ClassVar[URIRef] = GraphEntity.OCO["source-metadata-provider"]

    def __init__(self, prov_subject: GraphEntity, g: Graph, res: URIRef = None, res_type: URIRef = None,
                 resp_agent: str = None, source_agent: str = None, source: str = None, count: str = None,
                 label: str = None, short_name: str = "", g_set: ProvSet = None) -> None:
        self.prov_subject: GraphEntity = prov_subject
        super(ProvEntity, self).__init__(
            g, res, res_type, resp_agent, source_agent, source, count, label, short_name, g_set)

    # HAS CREATION DATE
    # <self.res> PROV:generatedAtTime "string"
    def create_generation_time(self, string: str) -> bool:
        """The date on which a particular snapshot of a bibliographic entity's metadata was
        created.
        """
        return self._create_literal(ProvEntity.generated_at_time, string, XSD.dateTime)

    # HAS INVALIDATION DATE
    # <self.res> PROV:invalidatedAtTime "string"
    def create_invalidation_time(self, string: str) -> bool:
        """The date on which a snapshot of a bibliographic entity's metadata was invalidated due
        to an update (e.g. a correction, or the addition of some metadata that was not specified
        in the previous snapshot), or due to a merger of the entity with another one.
        """
        return self._create_literal(ProvEntity.invalidated_at_time, string, XSD.dateTime)

    # IS SNAPSHOT OF
    # <self.res> PROV:specializationOf <en_res>
    def snapshot_of(self, en_res: GraphEntity) -> None:
        """This property is used to link a snapshot of entity metadata to the bibliographic entity
        to which the snapshot refers.
        """
        self.g.add((self.res, ProvEntity.specialization_of, URIRef(str(en_res))))

    # IS DERIVED FROM
    # <self.res> PROV:wasDerivedFrom <se_res>
    def derives_from(self, se_res: ProvEntity) -> None:
        """This property is used to identify the immediately previous snapshot of entity metadata
        associated with the same bibliographic entity.
        """
        self.g.add((self.res, ProvEntity.was_derived_from, URIRef(str(se_res))))

    # HAS PRIMARY SOURCE
    # <self.res> PROV:hadPrimarySource <any_res>
    def has_primary_source(self, any_res: str) -> None:
        """This property is used to identify the primary source from which the metadata
        described in the snapshot are derived (e.g. Crossref, as the result of querying the
        CrossRef API).
        """
        self.g.add((self.res, ProvEntity.had_primary_source, URIRef(str(any_res))))

    # HAS UPDATE ACTION
    # <self.res> OCO:hasUpdateQuery "string"
    def create_update_query(self, string: str) -> bool:
        """The UPDATE SPARQL query that specifies which data, associated to the bibliographic
        entity in consideration, have been modified (e.g. for correcting a mistake) in the
        current snapshot starting from those associated to the previous snapshot of the entity.
        """
        return self._create_literal(ProvEntity.has_update_query, string)

    # HAS DESCRIPTION
    # <self.res> DCTERM:description "string"
    def create_description(self, string: str) -> bool:
        """A textual description of the events that have resulted in the current snapshot (e.g. the
        creation of the initial snapshot, the creation of a new snapshot following the
        modification of the entity to which the metadata relate, or the creation of a new
        snapshot following the merger with another entity of the entity to which the previous
        snapshot related).
        """
        return self._create_literal(ProvEntity.description, string)

    # IS ATTRIBUTED TO
    # <self.res> PROV:wasAttributedTo <se_agent>
    # new
    def has_resp_agent(self, se_agent: str) -> None:
        """The agent responsible for the creation of the current entity snapshot.
        """
        self.g.add((self.res, ProvEntity.was_attributed_to, URIRef(str(se_agent))))

    # ++++++++++++++++++++++++ FACTORY METHODS ++++++++++++++++++++++++
    # <self.res> RDF:type <type>

    def create_creation_activity(self) -> None:
        self._create_type(ProvEntity.create)

    def create_update_activity(self) -> None:
        self._create_type(ProvEntity.modify)

    def create_merging_activity(self) -> None:
        self._create_type(ProvEntity.replace)

    # +++++++++++++++++++++++++ UNDOCUMENTED ++++++++++++++++++++++++++

    def generates(self, se_res: ProvEntity) -> None:
        se_res.g.add((URIRef(str(se_res)), ProvEntity.was_generated_by, self.res))

    def invalidates(self, se_res: ProvEntity) -> None:
        se_res.g.add((URIRef(str(se_res)), ProvEntity.was_invalidated_by, self.res))

    def involves_agent_with_role(self, cr_res: URIRef) -> None:
        self.g.add((self.res, ProvEntity.qualified_association, URIRef(str(cr_res))))

    def has_role_type(self, any_res: URIRef) -> None:
        self.g.add((self.res, ProvEntity.had_role, URIRef(str(any_res))))

    def has_role_in(self, ca_res: ResponsibleAgent) -> None:
        ca_res.g.add((URIRef(str(ca_res)), ProvEntity.associated_agent, self.res))
