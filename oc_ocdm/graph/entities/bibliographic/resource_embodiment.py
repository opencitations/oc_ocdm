#!/usr/bin/python

# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

from oc_ocdm.graph.entities.bibliographic_entity import BibliographicEntity
from oc_ocdm.graph.graph_entity import GraphEntity
from triplelite import RDFTerm


class ResourceEmbodiment(BibliographicEntity):
    """Resource embodiment (short: re): the particular physical or digital format in which a
       bibliographic resource was made available by its publisher."""

    def _merge_properties(self, other: GraphEntity, prefer_self: bool) -> None:
        """
        The merge operation allows combining two ``ResourceEmbodiment`` entities into a single one,
        by marking the second entity as to be deleted while also copying its data into the current
        ``ResourceEmbodiment``. Moreover, every triple from the containing ``GraphSet`` referring to the second
        entity gets "redirected" to the current entity: **every other reference contained inside a
        different source (e.g. a triplestore) must be manually handled by the user!**

        In case of functional properties, values from the current entity get overwritten
        by those coming from the second entity while, in all other cases, values from the
        second entity are simply appended to those of the current entity. In this context,
        ``rdfs:label`` is considered as a functional property, while ``rdf:type`` is not.

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: ResourceEmbodiment
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        super()._merge_properties(other, prefer_self)
        assert isinstance(other, ResourceEmbodiment)

        media_type: Optional[str] = other.get_media_type()
        if media_type is not None:
            self.has_media_type(media_type)

        starting_page: Optional[str] = other.get_starting_page()
        if starting_page is not None:
            self.has_starting_page(starting_page)

        ending_page: Optional[str] = other.get_ending_page()
        if ending_page is not None:
            self.has_ending_page(ending_page)

        url: Optional[str] = other.get_url()
        if url is not None:
            self.has_url(url)

    # HAS FORMAT
    def get_media_type(self) -> Optional[str]:
        """
        Getter method corresponding to the ``dcterms:format`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[str] = self._get_uri_reference(GraphEntity.iri_has_format)
        return uri

    def has_media_type(self, thing_res: str) -> None:
        """
        Setter method corresponding to the ``dcterms:format`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `It allows one to specify the IANA media type of the embodiment.`

        :param thing_res: The value that will be set as the object of the property related to this method
        :type thing_res: URIRef
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_media_type()
        self.g.add((self.res, GraphEntity.iri_has_format, RDFTerm("uri", str(thing_res))))

    def remove_media_type(self) -> None:
        """
        Remover method corresponding to the ``dcterms:format`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_format, None))

    # HAS FIRST PAGE
    def get_starting_page(self) -> Optional[str]:
        """
        Getter method corresponding to the ``prism:startingPage`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_starting_page)

    def has_starting_page(self, string: str) -> None:
        """
        Setter method corresponding to the ``prism:startingPage`` RDF predicate.

        The string gets internally preprocessed by eventually removing dashes and everything
        that follows them (e.g. '22-45' becomes '22').

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The first page of the bibliographic resource according to the current embodiment.`

        :param string: The value that will be set as the object of the property related to this method. **It must
          be a string that starts with an integer number.**
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_starting_page()
        if re.search("[-–]+", string) is None:
            page_number = string
        else:
            page_number = re.sub("[-–]+.*$", "", string)
        self._create_literal(GraphEntity.iri_starting_page, page_number)

    def remove_starting_page(self) -> None:
        """
        Remover method corresponding to the ``prism:startingPage`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_starting_page, None))

    # HAS LAST PAGE
    def get_ending_page(self) -> Optional[str]:
        """
        Getter method corresponding to the ``prism:endingPage`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(GraphEntity.iri_ending_page)

    def has_ending_page(self, string: str) -> None:
        """
        Setter method corresponding to the ``prism:endingPage`` RDF predicate.

        The string gets internally preprocessed by eventually removing dashes and everything
        that comes before them (e.g. '22-45' becomes '45').

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The last page of the bibliographic resource according to the current embodiment.`

        :param string: The value that will be set as the object of the property related to this method. **It must
          be a string that ends with an integer number.**
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_ending_page()
        if re.search("[-–]+", string) is None:
            page_number = string
        else:
            page_number = re.sub("^.*[-–]+", "", string)
        self._create_literal(GraphEntity.iri_ending_page, page_number)

    def remove_ending_page(self) -> None:
        """
        Remover method corresponding to the ``prism:endingPage`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_ending_page, None))

    # HAS URL
    def get_url(self) -> Optional[str]:
        """
        Getter method corresponding to the ``frbr:exemplar`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[str] = self._get_uri_reference(GraphEntity.iri_has_url)
        return uri

    def has_url(self, thing_res: str) -> None:
        """
        Setter method corresponding to the ``frbr:exemplar`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The URL at which the embodiment of the bibliographic resource is available.`

        :param thing_res: The value that will be set as the object of the property related to this method
        :type thing_res: URIRef
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_url()
        self.g.add((self.res, GraphEntity.iri_has_url, RDFTerm("uri", str(thing_res))))

    def remove_url(self) -> None:
        """
        Remover method corresponding to the ``frbr:exemplar`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, GraphEntity.iri_has_url, None))

    # HAS TYPE
    def create_digital_embodiment(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:DigitalManifestation``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `It identifies the particular type of the embodiment, either digital or print.`

        :return: None
        """
        self._create_type(GraphEntity.iri_digital_manifestation)

    def create_print_embodiment(self) -> None:
        """
        Setter method corresponding to the ``rdf:type`` RDF predicate.
        It implicitly sets the object value ``fabio:PrintObject``.

        **WARNING: the OCDM specification admits at most two types for an entity.
        The main type cannot be edited or removed. Any existing secondary type
        will be overwritten!**

        `It identifies the particular type of the embodiment, either digital or print.`

        :return: None
        """
        self._create_type(GraphEntity.iri_print_object)
