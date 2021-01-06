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
    from typing import Optional, List
    from rdflib import URIRef
from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.graph.entities.bibliographic_entity import BibliographicEntity


class ResponsibleAgent(BibliographicEntity):
    """Responsible agent (short: ra): the agent (usually a person or an organisation) having
       a certain role with respect to a bibliographic resource (e.g. an author of a paper or
       book, or an editor of a journal)."""

    @accepts_only('ra')
    def merge(self, other: ResponsibleAgent) -> None:
        super(ResponsibleAgent, self).merge(other)

        name: Optional[str] = other.get_name()
        if name is not None:
            self.has_name(name)

        given_name: Optional[str] = other.get_given_name()
        if given_name is not None:
            self.has_given_name(given_name)

        family_name: Optional[str] = other.get_family_name()
        if family_name is not None:
            self.has_family_name(family_name)

        related_agents: List[URIRef] = other.get_related_agents()
        for cur_agent in related_agents:
            self.has_related_agent(cur_agent)

    # HAS NAME STRING
    def get_name(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_name)

    @accepts_only('literal')
    def has_name(self, string: str) -> None:
        """The name of an agent (for people, usually in the format: given name followed by family
        name, separated by a space).
        """
        self.remove_name()
        self._create_literal(GraphEntity.iri_name, string)

    def remove_name(self) -> None:
        self.g.remove((self.g, GraphEntity.iri_name, None))

    # HAS GIVEN NAME
    def get_given_name(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_given_name)

    @accepts_only('literal')
    def has_given_name(self, string: str) -> None:
        """The given name of an agent, if a person.
        """
        self.remove_given_name()
        self._create_literal(GraphEntity.iri_given_name, string)

    def remove_given_name(self) -> None:
        self.g.remove((self.g, GraphEntity.iri_given_name, None))

    # HAS FAMILY NAME
    def get_family_name(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_family_name)

    @accepts_only('literal')
    def has_family_name(self, string: str) -> None:
        """The family name of an agent, if a person.
        """
        self.remove_family_name()
        self._create_literal(GraphEntity.iri_family_name, string)

    def remove_family_name(self) -> None:
        self.g.remove((self.g, GraphEntity.iri_family_name, None))

    # HAS RELATED AGENT
    def get_related_agents(self) -> List[URIRef]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_relation)
        return uri_list

    @accepts_only('thing')
    def has_related_agent(self, thing_ref: URIRef) -> None:
        """An external agent that/who is related in some relevant way with this responsible agent
        (e.g. for inter-linking purposes).
        """
        self.g.add((self.res, GraphEntity.iri_relation, thing_ref))

    @accepts_only('thing')
    def remove_related_agent(self, thing_ref: URIRef = None) -> None:
        if thing_ref is not None:
            self.g.remove((self.res, GraphEntity.iri_relation, thing_ref))
        else:
            self.g.remove((self.res, GraphEntity.iri_relation, None))
