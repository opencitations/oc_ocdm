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
        """
        The merge operation allows combining two ``ResponsibleAgent`` entities into a single one,
        by marking the second entity as to be deleted while also copying its data into the current
        ``ResponsibleAgent``. Moreover, every triple from the containing ``GraphSet`` referring to the second
        entity gets "redirected" to the current entity: **every other reference contained inside a
        different source (e.g. a triplestore) must be manually handled by the user!**

        In case of functional properties, values from the current entity get overwritten
        by those coming from the second entity while, in all other cases, values from the
        second entity are simply appended to those of the current entity. In this context,
        ``rdfs:label`` is considered as a functional property, while ``rdf:type`` is not.

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: ResponsibleAgent
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
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

    # HAS NAME
    def get_name(self) -> Optional[str]:
        """
        Getter method corresponding to the ``foaf:name`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_name)

    @accepts_only('literal')
    def has_name(self, string: str) -> None:
        """
        Setter method corresponding to the ``foaf:name`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The name of an agent (for people, usually in the format: given name followed by family
        name, separated by a space).`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_name()
        self._create_literal(GraphEntity.iri_name, string)

    def remove_name(self) -> None:
        """
        Remover method corresponding to the ``foaf:name`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_name, None))

    # HAS GIVEN NAME
    def get_given_name(self) -> Optional[str]:
        """
        Getter method corresponding to the ``foaf:givenName`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_given_name)

    @accepts_only('literal')
    def has_given_name(self, string: str) -> None:
        """
        Setter method corresponding to the ``foaf:givenName`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The given name of an agent, if a person.`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_given_name()
        self._create_literal(GraphEntity.iri_given_name, string)

    def remove_given_name(self) -> None:
        """
        Remover method corresponding to the ``foaf:givenName`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_given_name, None))

    # HAS FAMILY NAME
    def get_family_name(self) -> Optional[str]:
        """
        Getter method corresponding to the ``foaf:familyName`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_family_name)

    @accepts_only('literal')
    def has_family_name(self, string: str) -> None:
        """
        Setter method corresponding to the ``foaf:familyName`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The family name of an agent, if a person.`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_family_name()
        self._create_literal(GraphEntity.iri_family_name, string)

    def remove_family_name(self) -> None:
        """
        Remover method corresponding to the ``foaf:familyName`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_family_name, None))

    # HAS RELATED AGENT
    def get_related_agents(self) -> List[URIRef]:
        """
        Getter method corresponding to the ``dcterms:relation`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(GraphEntity.iri_relation)
        return uri_list

    @accepts_only('thing')
    def has_related_agent(self, thing_res: URIRef) -> None:
        """
        Setter method corresponding to the ``dcterms:relation`` RDF predicate.

        `An external agent that/who is related in some relevant way with this responsible agent
        (e.g. for inter-linking purposes).`

        :param thing_res: The value that will be set as the object of the property related to this method
        :type thing_res: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, GraphEntity.iri_relation, thing_res))

    @accepts_only('thing')
    def remove_related_agent(self, thing_res: URIRef = None) -> None:
        """
        Remover method corresponding to the ``dcterms:relation`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param thing_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type thing_res: URIRef
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if thing_res is not None:
            self.g.remove((self.res, GraphEntity.iri_relation, thing_res))
        else:
            self.g.remove((self.res, GraphEntity.iri_relation, None))
