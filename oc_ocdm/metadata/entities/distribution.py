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

from rdflib import XSD

from oc_ocdm.decorators import accepts_only
from oc_ocdm.metadata.metadata_entity import MetadataEntity

if TYPE_CHECKING:
    from typing import Optional
    from rdflib import URIRef


class Distribution(MetadataEntity):
    """Distribution (short: di): an accessible form of a dataset, for example a downloadable
       file."""

    @accepts_only('di')
    def merge(self, other: Distribution) -> None:
        super(Distribution, self).merge(other)

        title: Optional[str] = other.get_title()
        if title is not None:
            self.has_title(title)

        description: Optional[str] = other.get_description()
        if description is not None:
            self.has_description(description)

        pub_date: Optional[str] = other.get_publication_date()
        if pub_date is not None:
            self.has_publication_date(pub_date)

        byte_size: Optional[str] = other.get_byte_size()
        if byte_size is not None:
            self.has_byte_size(byte_size)

        license_uri: Optional[URIRef] = other.get_license()
        if license_uri is not None:
            self.has_license(license_uri)

        download_url: Optional[URIRef] = other.get_download_url()
        if download_url is not None:
            self.has_download_url(download_url)

        media_type: Optional[URIRef] = other.get_media_type()
        if media_type is not None:
            self.has_media_type(media_type)

    # HAS TITLE
    def get_title(self) -> Optional[str]:
        return self._get_literal(MetadataEntity.iri_title)

    @accepts_only('literal')
    def has_title(self, string: str) -> None:
        """The title of the distribution."""
        self.remove_title()
        self._create_literal(MetadataEntity.iri_title, string)

    def remove_title(self) -> None:
        self.g.remove((self.res, MetadataEntity.iri_title, None))

    # HAS DESCRIPTION
    def get_description(self) -> Optional[str]:
        return self._get_literal(MetadataEntity.iri_description)

    @accepts_only('literal')
    def has_description(self, string: str) -> None:
        """A short textual description of the content of the distribution."""
        self.remove_description()
        self._create_literal(MetadataEntity.iri_description, string)

    def remove_description(self) -> None:
        self.g.remove((self.res, MetadataEntity.iri_description, None))

    # HAS PUBLICATION DATE
    def get_publication_date(self) -> Optional[str]:
        return self._get_literal(MetadataEntity.iri_issued)

    @accepts_only('literal')
    def has_publication_date(self, string: str) -> None:
        """The date of first publication of the distribution."""
        self.remove_publication_date()
        self._create_literal(MetadataEntity.iri_issued, string, XSD.dateTime, False)

    def remove_publication_date(self) -> None:
        self.g.remove((self.res, MetadataEntity.iri_issued, None))

    # HAS BYTE SIZE
    def get_byte_size(self) -> Optional[str]:
        return self._get_literal(MetadataEntity.iri_byte_size)

    @accepts_only('literal')
    def has_byte_size(self, string: str) -> None:
        """The size in bytes of the distribution."""
        self.remove_byte_size()
        self._create_literal(MetadataEntity.iri_byte_size, string, XSD.decimal)

    def remove_byte_size(self) -> None:
        self.g.remove((self.res, MetadataEntity.iri_byte_size, None))

    # HAS LICENSE
    def get_license(self) -> Optional[URIRef]:
        return self._get_literal(MetadataEntity.iri_license)

    @accepts_only('thing')
    def has_license(self, thing_res: URIRef) -> None:
        """The resource describing the license associated with the data in the distribution."""
        self.remove_license()
        self.g.add((self.res, MetadataEntity.iri_license, thing_res))

    def remove_license(self) -> None:
        self.g.remove((self.res, MetadataEntity.iri_license, None))

    # HAS DOWNLOAD URL
    def get_download_url(self) -> Optional[URIRef]:
        return self._get_literal(MetadataEntity.iri_download_url)

    @accepts_only('thing')
    def has_download_url(self, thing_res: URIRef) -> None:
        """The URL of the document where the distribution is stored."""
        self.remove_download_url()
        self.g.add((self.res, MetadataEntity.iri_download_url, thing_res))

    def remove_download_url(self) -> None:
        self.g.remove((self.res, MetadataEntity.iri_download_url, None))

    # HAS_MEDIA_TYPE
    def get_media_type(self) -> Optional[URIRef]:
        return self._get_literal(MetadataEntity.iri_media_type)

    @accepts_only('thing')
    def has_media_type(self, thing_res: URIRef) -> None:
        """The file type of the representation of the distribution (according to IANA media types)."""
        self.remove_media_type()
        self.g.add((self.res, MetadataEntity.iri_media_type, thing_res))

    def remove_media_type(self) -> None:
        self.g.remove((self.res, MetadataEntity.iri_media_type, None))
