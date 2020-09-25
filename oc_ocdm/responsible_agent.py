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
from rdflib import URIRef

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from oc_ocdm.agent_role import AgentRole
from oc_ocdm.graph_entity import GraphEntity
from oc_ocdm.bibliographic_entity import BibliographicEntity

"""
Notes about RA:

    Chill down, everything seems OK here!
"""


class ResponsibleAgent(BibliographicEntity):
    """Responsible agent (short: ra): the agent (usually a person or an organisation) having
       a certain role with respect to a bibliographic resource (e.g. an author of a paper or
       book, or an editor of a journal)."""

    # HAS NAME STRING
    # <self.res> FOAF:name "string"
    def create_name(self, string: str) -> bool:
        """The name of an agent (for people, usually in the format: given name followed by family
        name, separated by a space).
        """
        return self._create_literal(GraphEntity.name, string)

    # HAS GIVEN NAME
    # <self.res> FOAF:givenName "string"
    def create_given_name(self, string: str) -> bool:
        """The given name of an agent, if a person.
        """
        return self._create_literal(GraphEntity.given_name, string)

    # HAS FAMILY NAME
    # <self.res> FOAF:familyName "string"
    def create_family_name(self, string: str) -> bool:
        """The family name of an agent, if a person.
        """
        return self._create_literal(GraphEntity.family_name, string)

    """
    AAA: this should have inverse logic and it should belong to AgentRole class!!!
    See below:
    
    class AgentRole:
        # IS HELD BY (ResponsibleAgent)
        def is_held_by(self, ra_res: URIRef):
            self.g.add((self.res, GraphEntity.is_held_by, URIRef(str(ar_res))))
    """
    def has_role(self, ar_res: AgentRole):
        """[AgentRole] The agent holding this role with respect to a particular bibliographic resource.
        """
        ar_res.g.add((URIRef(str(ar_res)), GraphEntity.is_held_by, self.res))

    # HAS RELATED AGENT
    # <self.res> DCTERMS:relation <thing_ref>
    def has_related_agent(self, thing_ref: URIRef) -> None:
        """An external agent that/who is related in some relevant way with this responsible agent
        (e.g. for inter-linking purposes).
        """
        self.g.add((self.res, GraphEntity.relation, thing_ref))
