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

from rdflib import Graph, Namespace, URIRef

from oc_ocdm.abstract_entity import AbstractEntity
from oc_ocdm.graph.graph_entity import GraphEntity

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

    iri_entity: ClassVar[URIRef] = PROV.Entity
    iri_generated_at_time: ClassVar[URIRef] = PROV.generatedAtTime
    iri_invalidated_at_time: ClassVar[URIRef] = PROV.invalidatedAtTime
    iri_specialization_of: ClassVar[URIRef] = PROV.specializationOf
    iri_was_derived_from: ClassVar[URIRef] = PROV.wasDerivedFrom
    iri_had_primary_source: ClassVar[URIRef] = PROV.hadPrimarySource
    iri_was_attributed_to: ClassVar[URIRef] = PROV.wasAttributedTo
    iri_description: ClassVar[URIRef] = GraphEntity.DCTERMS.description
    iri_has_update_query: ClassVar[URIRef] = GraphEntity.OCO.hasUpdateQuery

    short_name_to_type_iri: ClassVar[Dict[str, URIRef]] = {
        'se': iri_entity
    }

    def __init__(self, prov_subject: GraphEntity, g: Graph, p_set: ProvSet,
                 res: Optional[URIRef] = None, resp_agent: Optional[str] = None, source: Optional[str] = None,
                 count: Optional[str] = None, label: Optional[str] = None,
                 short_name: str = "se") -> None:
        super(ProvEntity, self).__init__()
        self.prov_subject: GraphEntity = prov_subject

        self.g: Graph = g
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
    def _generate_new_res(g: Graph, count: str, short_name: str) -> URIRef:
        return URIRef(str(g.identifier) + short_name + "/" + count)
