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
from rdflib.namespace import XSD, RDF

from oc_ocdm.decorators import accepts_only

if TYPE_CHECKING:
    from typing import Optional, List
    from oc_ocdm import ProvSet
    from oc_ocdm.entities.bibliographic import ResponsibleAgent
from oc_ocdm import GraphEntity

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
    was_attributed_to: ClassVar[URIRef] = PROV.wasAttributedTo
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
        super(ProvEntity, self).__init__(
            g, res, res_type, resp_agent, source_agent, source, count, label, short_name, g_set)
        self.prov_subject: GraphEntity = prov_subject

    @staticmethod
    def _generate_new_res(g: Graph, count: str, short_name: str = "") -> URIRef:
        return URIRef(str(g.identifier) + (short_name + "/" if short_name != "" else "") + count)

    # HAS CREATION DATE
    def get_generation_date(self) -> Optional[str]:
        return self._get_literal(ProvEntity.generated_at_time)

    @accepts_only('literal')
    def has_generation_time(self, string: str) -> None:
        """The date on which a particular snapshot of a bibliographic entity's metadata was
        created.
        """
        self.remove_generation_time()
        self._create_literal(ProvEntity.generated_at_time, string, XSD.dateTime)

    def remove_generation_time(self) -> None:
        self.g.remove((self.res, ProvEntity.generated_at_time, None))

    # HAS INVALIDATION DATE
    def get_invalidation_date(self) -> Optional[str]:
        return self._get_literal(ProvEntity.invalidated_at_time)

    @accepts_only('literal')
    def has_invalidation_time(self, string: str) -> None:
        """The date on which a snapshot of a bibliographic entity's metadata was invalidated due
        to an update (e.g. a correction, or the addition of some metadata that was not specified
        in the previous snapshot), or due to a merger of the entity with another one.
        """
        self.remove_invalidation_time()
        self._create_literal(ProvEntity.invalidated_at_time, string, XSD.dateTime)

    def remove_invalidation_time(self) -> None:
        self.g.remove((self.res, ProvEntity.invalidated_at_time, None))

    # IS SNAPSHOT OF
    def get_snapshot_of(self) -> Optional[URIRef]:
        uri: Optional[URIRef] = self._get_uri_reference(ProvEntity.specialization_of)
        return uri

    def snapshot_of(self, en_res: GraphEntity) -> None:
        """This property is used to link a snapshot of entity metadata to the bibliographic entity
        to which the snapshot refers.
        """
        self.remove_snapshot_of()
        self.g.add((self.res, ProvEntity.specialization_of, en_res.res))

    def remove_snapshot_of(self) -> None:
        self.g.remove((self.res, ProvEntity.specialization_of, None))

    # IS DERIVED FROM
    def get_derives_from(self) -> List[ProvEntity]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(ProvEntity.was_derived_from)
        result: List[ProvEntity] = []
        for uri in uri_list:
            result.append(self.g_set.add_se(self.resp_agent, self.source_agent, self.source, uri))
        return result

    @accepts_only('se')
    def derives_from(self, se_res: ProvEntity) -> None:
        """This property is used to identify the immediately previous snapshot of entity metadata
        associated with the same bibliographic entity.
        """
        self.g.add((self.res, ProvEntity.was_derived_from, se_res.res))

    @accepts_only('se')
    def remove_derives_from(self, se_res: ProvEntity = None) -> None:
        if se_res is not None:
            self.g.remove((self.res, ProvEntity.was_derived_from, se_res.res))
        else:
            self.g.remove((self.res, ProvEntity.was_derived_from, None))

    # HAS PRIMARY SOURCE
    def get_primary_source(self) -> Optional[URIRef]:
        uri: Optional[URIRef] = self._get_uri_reference(ProvEntity.had_primary_source)
        return uri

    @accepts_only('thing')
    def has_primary_source(self, any_res: URIRef) -> None:
        """This property is used to identify the primary source from which the metadata
        described in the snapshot are derived (e.g. Crossref, as the result of querying the
        CrossRef API).
        """
        self.remove_primary_source()
        self.g.add((self.res, ProvEntity.had_primary_source, any_res))

    def remove_primary_source(self) -> None:
        self.g.remove((self.res, ProvEntity.had_primary_source, None))

    # HAS UPDATE ACTION
    def get_update_action(self) -> Optional[str]:
        return self._get_literal(ProvEntity.has_update_query)

    @accepts_only('literal')
    def has_update_action(self, string: str) -> None:
        """The UPDATE SPARQL query that specifies which data, associated to the bibliographic
        entity in consideration, have been modified (e.g. for correcting a mistake) in the
        current snapshot starting from those associated to the previous snapshot of the entity.
        """
        self.remove_update_action()
        self._create_literal(ProvEntity.has_update_query, string)

    def remove_update_action(self) -> None:
        self.g.remove((self.res, ProvEntity.has_update_query, None))

    # HAS DESCRIPTION
    def get_description(self) -> Optional[str]:
        return self._get_literal(ProvEntity.description)

    @accepts_only('literal')
    def has_description(self, string: str) -> None:
        """A textual description of the events that have resulted in the current snapshot (e.g. the
        creation of the initial snapshot, the creation of a new snapshot following the
        modification of the entity to which the metadata relate, or the creation of a new
        snapshot following the merger with another entity of the entity to which the previous
        snapshot related).
        """
        self.remove_description()
        self._create_literal(ProvEntity.description, string)

    def remove_description(self) -> None:
        self.g.remove((self.res, ProvEntity.description, None))

    # IS ATTRIBUTED TO
    def get_resp_agent(self) -> Optional[URIRef]:
        uri: Optional[URIRef] = self._get_uri_reference(ProvEntity.was_attributed_to)
        return uri

    @accepts_only('thing')
    def has_resp_agent(self, se_agent: URIRef) -> None:
        """The agent responsible for the creation of the current entity snapshot.
        """
        self.remove_resp_agent()
        self.g.add((self.res, ProvEntity.was_attributed_to, se_agent))

    def remove_resp_agent(self) -> None:
        self.g.remove((self.res, ProvEntity.was_attributed_to, None))

    # HAS TYPE
    def get_types(self) -> List[URIRef]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(RDF.type)
        return uri_list

    def create_creation_activity(self) -> None:
        self._create_type(ProvEntity.create)

    def create_update_activity(self) -> None:
        self._create_type(ProvEntity.modify)

    def create_merging_activity(self) -> None:
        self._create_type(ProvEntity.replace)

    @accepts_only('thing')
    def remove_type(self, type_ref: URIRef = None) -> None:
        if type_ref is not None:
            self.g.remove((self.res, RDF.type, type_ref))
        else:
            self.g.remove((self.res, RDF.type, None))
    # +++++++++++++++++++++++++ UNDOCUMENTED ++++++++++++++++++++++++++

    @accepts_only('se')
    def generates(self, se_res: ProvEntity) -> None:
        se_res.g.add((se_res.res, ProvEntity.was_generated_by, self.res))

    @accepts_only('se')
    def invalidates(self, se_res: ProvEntity) -> None:
        se_res.g.add((se_res.res, ProvEntity.was_invalidated_by, self.res))

    @accepts_only('thing')
    def involves_agent_with_role(self, cr_res: URIRef) -> None:
        self.g.add((self.res, ProvEntity.qualified_association, cr_res))

    @accepts_only('thing')
    def has_role_type(self, any_res: URIRef) -> None:
        self.g.add((self.res, ProvEntity.had_role, any_res))

    @accepts_only('ra')
    def has_role_in(self, ca_res: ResponsibleAgent) -> None:
        ca_res.g.add((ca_res.res, ProvEntity.associated_agent, self.res))
