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

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from rdflib import URIRef

from oc_ocdm.graph.graph_entity import GraphEntity
from oc_ocdm.decorators import accepts_only
from oc_ocdm.graph.entities.bibliographic_entity import BibliographicEntity


class ResourceEmbodiment(BibliographicEntity):
    """Resource embodiment (short: re): the particular physical or digital format in which a
       bibliographic resource was made available by its publisher."""

    @accepts_only('re')
    def merge(self, other: ResourceEmbodiment) -> None:
        super(ResourceEmbodiment, self).merge(other)

        media_type: Optional[URIRef] = other.get_media_type()
        if media_type is not None:
            self.has_media_type(media_type)

        starting_page: Optional[str] = other.get_starting_page()
        if starting_page is not None:
            self.has_starting_page(starting_page)

        ending_page: Optional[str] = other.get_ending_page()
        if ending_page is not None:
            self.has_ending_page(ending_page)

        url: Optional[URIRef] = other.get_url()
        if url is not None:
            self.has_url(url)

    # HAS FORMAT
    def get_media_type(self) -> Optional[URIRef]:
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_has_format)
        return uri

    @accepts_only('thing')
    def has_media_type(self, thing_ref: URIRef) -> None:
        """It allows one to specify the IANA media type of the embodiment.
        """
        self.remove_media_type()
        self.g.add((self.res, GraphEntity.iri_has_format, thing_ref))

    def remove_media_type(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_format, None))

    # HAS FIRST PAGE
    def get_starting_page(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_starting_page)

    @accepts_only('literal')
    def has_starting_page(self, string: str) -> None:
        """The first page of the bibliographic resource according to the current embodiment.
        """
        self.remove_starting_page()
        if re.search("[-–]+", string) is None:
            page_number = string
        else:
            page_number = re.sub("[-–]+.*$", "", string)
        self._create_literal(GraphEntity.iri_starting_page, page_number)

    def remove_starting_page(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_starting_page, None))

    # HAS LAST PAGE
    def get_ending_page(self) -> Optional[str]:
        return self._get_literal(GraphEntity.iri_ending_page)

    @accepts_only('literal')
    def has_ending_page(self, string: str) -> None:
        """The last page of the bibliographic resource according to the current embodiment.
        """
        self.remove_ending_page()
        if re.search("[-–]+", string) is None:
            page_number = string
        else:
            page_number = re.sub("^.*[-–]+", "", string)
        self._create_literal(GraphEntity.iri_ending_page, page_number)

    def remove_ending_page(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_ending_page, None))

    # HAS URL
    def get_url(self) -> Optional[URIRef]:
        uri: Optional[URIRef] = self._get_uri_reference(GraphEntity.iri_has_url)
        return uri

    @accepts_only('thing')
    def has_url(self, thing_ref: URIRef) -> None:
        """The URL at which the embodiment of the bibliographic resource is available.
        """
        self.remove_url()
        self.g.add((self.res, GraphEntity.iri_has_url, thing_ref))

    def remove_url(self) -> None:
        self.g.remove((self.res, GraphEntity.iri_has_url, None))

    # HAS TYPE
    def create_digital_embodiment(self) -> None:
        """It identifies the particular type of the embodiment, either digital or print.
        """
        self._create_type(GraphEntity.iri_digital_manifestation)

    def create_print_embodiment(self) -> None:
        """It identifies the particular type of the embodiment, either digital or print.
        """
        self._create_type(GraphEntity.iri_print_object)
