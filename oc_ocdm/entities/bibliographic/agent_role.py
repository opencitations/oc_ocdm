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
    from oc_ocdm.entities.bibliographic import ResponsibleAgent
from oc_ocdm import GraphEntity
from oc_ocdm.entities import BibliographicEntity


class AgentRole(BibliographicEntity):
    """Agent role (short: ar): a particular role held by an agent with respect to a bibliographic resource."""

    # HAS NEXT (AgentRole)
    @accepts_only('ar')
    def has_next(self, ar_res: AgentRole) -> None:
        """The previous role in a sequence of agent roles of the same type associated with the
        same bibliographic resource (so as to define, for instance, an ordered list of authors).
        """
        self.remove_next()
        self.g.add((self.res, GraphEntity.has_next, ar_res.res))

    def remove_next(self) -> None:
        self.g.remove((self.res, GraphEntity.has_next, None))

    # IS HELD BY (ResponsibleAgent)
    @accepts_only('ra')
    def is_held_by(self, ra_res: ResponsibleAgent):
        """The agent holding this role with respect to a particular bibliographic resource.
        """
        self.remove_held_by()
        self.g.add((self.res, GraphEntity.is_held_by, ra_res.res))

    def remove_held_by(self) -> None:
        self.g.remove((self.res, GraphEntity.is_held_by, None))

    # ++++++++++++++++++++++++ FACTORY METHODS ++++++++++++++++++++++++
    def create_publisher(self) -> None:
        """The specific type of role under consideration (e.g. author, editor or publisher).
        """
        self.remove_role_type()
        self.g.add((self.res, GraphEntity.with_role, GraphEntity.publisher))

    def create_author(self) -> None:
        """The specific type of role under consideration (e.g. author, editor or publisher).
        """
        self.remove_role_type()
        self.g.add((self.res, GraphEntity.with_role, GraphEntity.author))

    def create_editor(self) -> None:
        """The specific type of role under consideration (e.g. author, editor or publisher).
        """
        self.remove_role_type()
        self.g.add((self.res, GraphEntity.with_role, GraphEntity.editor))

    def remove_role_type(self) -> None:
        self.g.remove((self.res, GraphEntity.with_role, None))
