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

from rdflib import Namespace, URIRef
from rdflib.namespace import XSD

from oc_graphlib.graph_entity import GraphEntity


class ProvEntity(GraphEntity):
    PROV = Namespace("http://www.w3.org/ns/prov#")

    # Exclusive provenance entities
    prov_agent = PROV.Agent
    entity = PROV.Entity
    activity = PROV.Activity
    create = PROV.Create
    modify = PROV.Modify
    replace = PROV.Replace
    association = PROV.Association
    generated_at_time = PROV.generatedAtTime
    invalidated_at_time = PROV.invalidatedAtTime
    specialization_of = PROV.specializationOf
    was_derived_from = PROV.wasDerivedFrom
    had_primary_source = PROV.hadPrimarySource
    was_generated_by = PROV.wasGeneratedBy
    was_attributed_to = PROV.wasAttributedTo # new
    was_invalidated_by = PROV.wasInvalidatedBy
    qualified_association = PROV.qualifiedAssociation
    description = GraphEntity.DCTERMS.description
    has_update_query = GraphEntity.OCO.hasUpdateQuery
    had_role = PROV.hadRole
    associated_agent = PROV.agent
    curator = GraphEntity.OCO["occ-curator"]
    source_provider = GraphEntity.OCO["source-metadata-provider"]

    def __init__(self, prov_subject, g, res=None, res_type=None,
                 resp_agent=None, source_agent=None, source=None, count=None, label=None,
                 short_name="", g_set=None):
        self.prov_subject = prov_subject
        super(ProvEntity, self).__init__(
            g, res, res_type, resp_agent, source_agent, source, count, label, short_name, g_set)

    # /START Literal Attributes
    def create_generation_time(self, string):
        return self._create_literal(ProvEntity.generated_at_time, string, XSD.dateTime)

    def create_invalidation_time(self, string):
        return self._create_literal(ProvEntity.invalidated_at_time, string, XSD.dateTime)

    def create_description(self, string):
        return self._create_literal(ProvEntity.description, string)

    def create_update_query(self, string):
        return self._create_literal(ProvEntity.has_update_query, string)
        # /END Literal Attributes

    # /START Composite Attributes
    def create_creation_activity(self):
        self._create_type(ProvEntity.create)

    def create_update_activity(self):
        self._create_type(ProvEntity.modify)

    def create_merging_activity(self):
        self._create_type(ProvEntity.replace)

    def snapshot_of(self, se_res):
        self.g.add((self.res, ProvEntity.specialization_of, URIRef(str(se_res))))

    def derives_from(self, se_res):
        self.g.add((self.res, ProvEntity.was_derived_from, URIRef(str(se_res))))

    def has_primary_source(self, any_res):
        self.g.add((self.res, ProvEntity.had_primary_source, URIRef(str(any_res))))

    def generates(self, se_res):
        se_res.g.add((URIRef(str(se_res)), ProvEntity.was_generated_by, self.res))

    def invalidates(self, se_res):
        se_res.g.add((URIRef(str(se_res)), ProvEntity.was_invalidated_by, self.res))

    def involves_agent_with_role(self, cr_res):
        self.g.add((self.res, ProvEntity.qualified_association, URIRef(str(cr_res))))

    def has_role_type(self, any_res):
        self.g.add((self.res, ProvEntity.had_role, URIRef(str(any_res))))

    def has_role_in(self, ca_res):
        ca_res.g.add((URIRef(str(ca_res)), ProvEntity.associated_agent, self.res))

    # new
    def has_resp_agent(self, se_agent):
        self.g.add((self.res, ProvEntity.was_attributed_to, URIRef(str(se_agent))))
    # /END Composite Attributes
