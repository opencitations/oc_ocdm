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
    from typing import Optional
    from rdflib import URIRef
    from oc_ocdm.graph.entities.bibliographic.responsible_agent import ResponsibleAgent
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.entities.bibliographic_entity import BibliographicEntity


class AgentRole(BibliographicEntity):
    """Agent role (short: ar): a particular role held by an agent with respect to a bibliographic resource."""

    @accepts_only('ar')
    def merge(self, other: AgentRole) -> None:
        super(AgentRole, self).merge(other)

        next_ar: Optional[AgentRole] = other.get_next()
        if next_ar is not None:
            self.has_next(next_ar)

        resp_agent: Optional[ResponsibleAgent] = other.get_is_held_by()
        if resp_agent is not None:
            self.is_held_by(resp_agent)

        role_type: Optional[URIRef] = other.get_role_type()
        if role_type is not None:
            if role_type == GraphEntity.iri_publisher:
                self.create_publisher()
            elif role_type == GraphEntity.iri_author:
                self.create_author()
            elif role_type == GraphEntity.iri_editor:
                self.create_editor()

    # HAS NEXT (AgentRole)
    def get_next(self) -> Optional[AgentRole]:
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_has_next)
        if uri is not None:
            return self.g_set.add_ar(self.resp_agent, self.source_agent, self.source, uri)

    @accepts_only('ar')
    def has_next(self, ar_res: AgentRole) -> None:
        """The previous role in a sequence of agent roles of the same type associated with the
        same bibliographic resource (so as to define, for instance, an ordered list of authors).
        """
        self.remove_next()
        self.g.add((self.res, GraphEntity.iri_has_next, ar_res.res))

    def remove_next(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_next, None))

    # IS HELD BY (ResponsibleAgent)
    def get_is_held_by(self) -> Optional[ResponsibleAgent]:
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_is_held_by)
        if uri is not None:
            return self.g_set.add_ra(self.resp_agent, self.source_agent, self.source, uri)

    @accepts_only('ra')
    def is_held_by(self, ra_res: ResponsibleAgent):
        """The agent holding this role with respect to a particular bibliographic resource.
        """
        self.remove_is_held_by()
        self.g.add((self.res, GraphEntity.iri_is_held_by, ra_res.res))

    def remove_is_held_by(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_is_held_by, None))

    # HAS ROLE TYPE
    def get_role_type(self) -> Optional[URIRef]:
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_with_role)
        return uri

    def create_publisher(self) -> None:
        """The specific type of role under consideration (e.g. author, editor or publisher).
        """
        self.remove_role_type()
        self.g.add((self.res, GraphEntity.iri_with_role, GraphEntity.iri_publisher))

    def create_author(self) -> None:
        """The specific type of role under consideration (e.g. author, editor or publisher).
        """
        self.remove_role_type()
        self.g.add((self.res, GraphEntity.iri_with_role, GraphEntity.iri_author))

    def create_editor(self) -> None:
        """The specific type of role under consideration (e.g. author, editor or publisher).
        """
        self.remove_role_type()
        self.g.add((self.res, GraphEntity.iri_with_role, GraphEntity.iri_editor))

    def remove_role_type(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_with_role, None))
