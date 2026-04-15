#!/usr/bin/python

# SPDX-FileCopyrightText: 2023-2026 Arcangelo Massari <arcangelo.massari@unibo.it>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

from oc_ocdm.abstract_entity import AbstractEntity
from oc_ocdm.constants import Namespace
from oc_ocdm.graph.graph_entity import GraphEntity
from triplelite import TripleLite

if TYPE_CHECKING:
    from typing import ClassVar, Dict, Optional

    from oc_ocdm.prov.prov_set import ProvSet


class ProvEntity(AbstractEntity):
    """Snapshot of entity metadata (short: se): a particular snapshot recording the
    metadata associated with an individual entity (either a bibliographic entity or an
    identifier) at a particular date and time, including the agent, such as a person,
    organisation or automated process that created or modified the entity metadata.
    """

    PROV: ClassVar[Namespace] = Namespace("http://www.w3.org/ns/prov#")

    iri_entity: ClassVar[str] = PROV.Entity
    iri_generated_at_time: ClassVar[str] = PROV.generatedAtTime
    iri_invalidated_at_time: ClassVar[str] = PROV.invalidatedAtTime
    iri_specialization_of: ClassVar[str] = PROV.specializationOf
    iri_was_derived_from: ClassVar[str] = PROV.wasDerivedFrom
    iri_had_primary_source: ClassVar[str] = PROV.hadPrimarySource
    iri_was_attributed_to: ClassVar[str] = PROV.wasAttributedTo
    iri_description: ClassVar[str] = GraphEntity.DCTERMS.description
    iri_has_update_query: ClassVar[str] = GraphEntity.OCO.hasUpdateQuery

    short_name_to_type_iri: ClassVar[Dict[str, str]] = {
        'se': iri_entity
    }

    def __init__(self, prov_subject: GraphEntity, g: TripleLite, p_set: ProvSet,
                 res: Optional[str] = None, resp_agent: Optional[str] = None, source: Optional[str] = None,
                 count: Optional[str] = None, label: Optional[str] = None,
                 short_name: str = "se") -> None:
        super(ProvEntity, self).__init__()
        self.prov_subject: GraphEntity = prov_subject

        self.g: TripleLite = g
        self.resp_agent: Optional[str] = resp_agent
        self.source: Optional[str] = source
        self.short_name: str = short_name
        self.p_set: ProvSet = p_set

        if res is not None and count is not None:
            raise ValueError("'res' and 'count' are mutually exclusive: provide one or the other")
        if res is not None:
            self.res = res
        elif count is not None:
            self.res = self._generate_new_res(g, count, short_name)
        else:
            raise ValueError("Either 'res' or 'count' must be provided")

        if p_set is not None:
            if self.res not in p_set.res_to_entity:
                p_set.res_to_entity[self.res] = self

        self._create_type(self.short_name_to_type_iri[short_name])
        if label is not None:
            self.create_label(label)

    @staticmethod
    def _generate_new_res(g: TripleLite, count: str, short_name: str) -> str:
        return str(g.identifier) + short_name + "/" + count
