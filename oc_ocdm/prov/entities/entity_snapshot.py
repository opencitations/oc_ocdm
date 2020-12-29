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
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.prov.prov_entity import ProvEntity
from rdflib import XSD

if TYPE_CHECKING:
    from typing import Optional, List
    from rdflib import URIRef


class EntitySnapshot(ProvEntity):
    # HAS CREATION DATE
    def get_generation_time(self) -> Optional[str]:
        return self._get_literal(ProvEntity.iri_generated_at_time)

    @accepts_only('literal')
    def has_generation_time(self, string: str) -> None:
        """The date on which a particular snapshot of a bibliographic entity's metadata was
        created.
        """
        self.remove_generation_time()
        self._create_literal(ProvEntity.iri_generated_at_time, string, XSD.dateTime)

    def remove_generation_time(self) -> None:
        self.g.remove((self.res, ProvEntity.iri_generated_at_time, None))

    # HAS INVALIDATION DATE
    def get_invalidation_time(self) -> Optional[str]:
        return self._get_literal(ProvEntity.iri_invalidated_at_time)

    @accepts_only('literal')
    def has_invalidation_time(self, string: str) -> None:
        """The date on which a snapshot of a bibliographic entity's metadata was invalidated due
        to an update (e.g. a correction, or the addition of some metadata that was not specified
        in the previous snapshot), or due to a merger of the entity with another one.
        """
        self.remove_invalidation_time()
        self._create_literal(ProvEntity.iri_invalidated_at_time, string, XSD.dateTime)

    def remove_invalidation_time(self) -> None:
        self.g.remove((self.res, ProvEntity.iri_invalidated_at_time, None))

    # IS SNAPSHOT OF
    def get_is_snapshot_of(self) -> Optional[URIRef]:
        uri: Optional[URIRef] = self._get_uri_reference(ProvEntity.iri_specialization_of)
        return uri

    def is_snapshot_of(self, en_res: GraphEntity) -> None:
        """This property is used to link a snapshot of entity metadata to the bibliographic entity
        to which the snapshot refers.
        """
        self.remove_is_snapshot_of()
        self.g.add((self.res, ProvEntity.iri_specialization_of, en_res.res))

    def remove_is_snapshot_of(self) -> None:
        self.g.remove((self.res, ProvEntity.iri_specialization_of, None))

    # IS DERIVED FROM
    def get_derives_from(self) -> List[ProvEntity]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(ProvEntity.iri_was_derived_from)
        result: List[ProvEntity] = []
        for uri in uri_list:
            # TODO: what is the prov_subject of these snapshots?
            result.append(self.p_set.add_se(None, uri))
        return result

    @accepts_only('se')
    def derives_from(self, se_res: ProvEntity) -> None:
        """This property is used to identify the immediately previous snapshot of entity metadata
        associated with the same bibliographic entity.
        """
        self.g.add((self.res, ProvEntity.iri_was_derived_from, se_res.res))

    @accepts_only('se')
    def remove_derives_from(self, se_res: ProvEntity = None) -> None:
        if se_res is not None:
            self.g.remove((self.res, ProvEntity.iri_was_derived_from, se_res.res))
        else:
            self.g.remove((self.res, ProvEntity.iri_was_derived_from, None))

    # HAS PRIMARY SOURCE
    def get_primary_source(self) -> Optional[URIRef]:
        uri: Optional[URIRef] = self._get_uri_reference(ProvEntity.iri_had_primary_source)
        return uri

    @accepts_only('thing')
    def has_primary_source(self, any_res: URIRef) -> None:
        """This property is used to identify the primary source from which the metadata
        described in the snapshot are derived (e.g. Crossref, as the result of querying the
        CrossRef API).
        """
        self.remove_primary_source()
        self.g.add((self.res, ProvEntity.iri_had_primary_source, any_res))

    def remove_primary_source(self) -> None:
        self.g.remove((self.res, ProvEntity.iri_had_primary_source, None))

    # HAS UPDATE ACTION
    def get_update_action(self) -> Optional[str]:
        return self._get_literal(ProvEntity.iri_has_update_query)

    @accepts_only('literal')
    def has_update_action(self, string: str) -> None:
        """The UPDATE SPARQL query that specifies which data, associated to the bibliographic
        entity in consideration, have been modified (e.g. for correcting a mistake) in the
        current snapshot starting from those associated to the previous snapshot of the entity.
        """
        self.remove_update_action()
        self._create_literal(ProvEntity.iri_has_update_query, string)

    def remove_update_action(self) -> None:
        self.g.remove((self.res, ProvEntity.iri_has_update_query, None))

    # HAS DESCRIPTION
    def get_description(self) -> Optional[str]:
        return self._get_literal(ProvEntity.iri_description)

    @accepts_only('literal')
    def has_description(self, string: str) -> None:
        """A textual description of the events that have resulted in the current snapshot (e.g. the
        creation of the initial snapshot, the creation of a new snapshot following the
        modification of the entity to which the metadata relate, or the creation of a new
        snapshot following the merger with another entity of the entity to which the previous
        snapshot related).
        """
        self.remove_description()
        self._create_literal(ProvEntity.iri_description, string)

    def remove_description(self) -> None:
        self.g.remove((self.res, ProvEntity.iri_description, None))

    # IS ATTRIBUTED TO
    def get_resp_agent(self) -> Optional[URIRef]:
        uri: Optional[URIRef] = self._get_uri_reference(ProvEntity.iri_was_attributed_to)
        return uri

    @accepts_only('thing')
    def has_resp_agent(self, se_agent: URIRef) -> None:
        """The agent responsible for the creation of the current entity snapshot.
        """
        self.remove_resp_agent()
        self.g.add((self.res, ProvEntity.iri_was_attributed_to, se_agent))

    def remove_resp_agent(self) -> None:
        self.g.remove((self.res, ProvEntity.iri_was_attributed_to, None))
