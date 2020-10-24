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
    from rdflib import URIRef
    from oc_ocdm.entities.bibliographic import AgentRole
from oc_ocdm import GraphEntity
from oc_ocdm.entities import BibliographicEntity

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
    @accepts_only('literal')
    def has_name(self, string: str) -> None:
        """The name of an agent (for people, usually in the format: given name followed by family
        name, separated by a space).
        """
        self.remove_name()
        self._create_literal(GraphEntity.name, string)

    def remove_name(self) -> None:
        self.g.remove((self.g, GraphEntity.name, None))

    # HAS GIVEN NAME
    # <self.res> FOAF:givenName "string"
    @accepts_only('literal')
    def has_given_name(self, string: str) -> None:
        """The given name of an agent, if a person.
        """
        self.remove_given_name()
        self._create_literal(GraphEntity.given_name, string)

    def remove_given_name(self) -> None:
        self.g.remove((self.g, GraphEntity.given_name, None))

    # HAS FAMILY NAME
    # <self.res> FOAF:familyName "string"
    @accepts_only('literal')
    def has_family_name(self, string: str) -> None:
        """The family name of an agent, if a person.
        """
        self.remove_family_name()
        self._create_literal(GraphEntity.family_name, string)

    def remove_family_name(self) -> None:
        self.g.remove((self.g, GraphEntity.family_name, None))

    """
    AAA: this should have inverse logic and it should belong to AgentRole class!!!
    See below:
    
    class AgentRole:
        # IS HELD BY (ResponsibleAgent)
        def is_held_by(self, ra_res: URIRef):
            self.g.add((self.res, GraphEntity.is_held_by, ar_res.res))
    """
    @accepts_only('ar')
    def has_role(self, ar_res: AgentRole):
        """[AgentRole] The agent holding this role with respect to a particular bibliographic resource.
        """
        ar_res.g.add((ar_res.res, GraphEntity.is_held_by, self.res))

    @accepts_only('ar')
    def remove_role(self, ar_res: AgentRole = None) -> None:
        if ar_res is not None:
            if (ar_res.res, GraphEntity.is_held_by, self.res) in ar_res.g:
                ar_res.g.remove((ar_res.res, GraphEntity.is_held_by, None))
        else:
            if self.g_set is not None:
                for ar_res in self.g_set.get_ar():
                    if (ar_res.res, GraphEntity.is_held_by, self.res) in ar_res.g:
                        ar_res.g.remove((ar_res.res, GraphEntity.is_held_by, None))

    # HAS RELATED AGENT
    # <self.res> DCTERMS:relation <thing_ref>
    @accepts_only('thing')
    def has_related_agent(self, thing_ref: URIRef) -> None:
        """An external agent that/who is related in some relevant way with this responsible agent
        (e.g. for inter-linking purposes).
        """
        self.g.add((self.res, GraphEntity.relation, thing_ref))

    @accepts_only('thing')
    def remove_related_agent(self, thing_ref: URIRef = None) -> None:
        if thing_ref is not None:
            self.g.remove((self.res, GraphEntity.relation, thing_ref))
        else:
            self.g.remove((self.res, GraphEntity.relation, None))
