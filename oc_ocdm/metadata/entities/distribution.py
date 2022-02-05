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
        """
        The merge operation allows combining two ``Distribution`` entities into a single one,
        by marking the second entity as to be deleted while also copying its data into the current
        ``Distribution``. Moreover, every triple from the containing ``MetadataSet`` referring to the second
        entity gets "redirected" to the current entity: **every other reference contained inside a
        different source (e.g. a triplestore) must be manually handled by the user!**

        In case of functional properties, values from the current entity get overwritten
        by those coming from the second entity while, in all other cases, values from the
        second entity are simply appended to those of the current entity. In this context,
        ``rdfs:label`` is considered as a functional property, while ``rdf:type`` is not.

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: Distribution
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
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
        """
        Getter method corresponding to the ``dcterms:title`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(MetadataEntity.iri_title)

    @accepts_only('literal')
    def has_title(self, string: str) -> None:
        """
        Setter method corresponding to the ``dcterms:title`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The title of the distribution.`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_title()
        self._create_literal(MetadataEntity.iri_title, string)

    def remove_title(self) -> None:
        """
        Remover method corresponding to the ``dcterms:title`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_title, None))

    # HAS DESCRIPTION
    def get_description(self) -> Optional[str]:
        """
        Getter method corresponding to the ``dcterms:description`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(MetadataEntity.iri_description)

    @accepts_only('literal')
    def has_description(self, string: str) -> None:
        """
        Setter method corresponding to the ``dcterms:description`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `A short textual description of the content of the distribution.`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_description()
        self._create_literal(MetadataEntity.iri_description, string)

    def remove_description(self) -> None:
        """
        Remover method corresponding to the ``dcterms:description`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_description, None))

    # HAS PUBLICATION DATE
    def get_publication_date(self) -> Optional[str]:
        """
        Getter method corresponding to the ``dcterms:issued`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(MetadataEntity.iri_issued)

    @accepts_only('literal')
    def has_publication_date(self, string: str) -> None:
        """
        Setter method corresponding to the ``dcterms:issued`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The date of first publication of the distribution.`

        :param string: The value that will be set as the object of the property related to this method. **It must
          be a string compliant with the** ``xsd:dateTime`` **datatype.**
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_publication_date()
        self._create_literal(MetadataEntity.iri_issued, string, XSD.dateTime, False)

    def remove_publication_date(self) -> None:
        """
        Remover method corresponding to the ``dcterms:issued`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_issued, None))

    # HAS BYTE SIZE
    def get_byte_size(self) -> Optional[str]:
        """
        Getter method corresponding to the ``dcat:byte_size`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(MetadataEntity.iri_byte_size)

    @accepts_only('literal')
    def has_byte_size(self, string: str) -> None:
        """
        Setter method corresponding to the ``dcat:byte_size`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The size in bytes of the distribution.`

        :param string: The value that will be set as the object of the property related to this method. **It must
          be a string compliant with the** ``xsd:decimal`` **datatype.**
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_byte_size()
        self._create_literal(MetadataEntity.iri_byte_size, string, XSD.decimal)

    def remove_byte_size(self) -> None:
        """
        Remover method corresponding to the ``dcat:byte_size`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_byte_size, None))

    # HAS LICENSE
    def get_license(self) -> Optional[URIRef]:
        """
        Getter method corresponding to the ``dcterms:license`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(MetadataEntity.iri_license)

    @accepts_only('thing')
    def has_license(self, thing_res: URIRef) -> None:
        """
        Setter method corresponding to the ``dcterms:license`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The resource describing the license associated with the data in the distribution.`

        :param thing_res: The value that will be set as the object of the property related to this method
        :type thing_res: URIRef
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_license()
        self.g.add((self.res, MetadataEntity.iri_license, thing_res))

    def remove_license(self) -> None:
        """
        Remover method corresponding to the ``dcterms:license`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_license, None))

    # HAS DOWNLOAD URL
    def get_download_url(self) -> Optional[URIRef]:
        """
        Getter method corresponding to the ``dcat:downloadURL`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(MetadataEntity.iri_download_url)

    @accepts_only('thing')
    def has_download_url(self, thing_res: URIRef) -> None:
        """
        Setter method corresponding to the ``dcat:downloadURL`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The URL of the document where the distribution is stored.`

        :param thing_res: The value that will be set as the object of the property related to this method
        :type thing_res: URIRef
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_download_url()
        self.g.add((self.res, MetadataEntity.iri_download_url, thing_res))

    def remove_download_url(self) -> None:
        """
        Remover method corresponding to the ``dcat:downloadURL`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_download_url, None))

    # HAS_MEDIA_TYPE
    def get_media_type(self) -> Optional[URIRef]:
        """
        Getter method corresponding to the ``dcat:mediaType`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(MetadataEntity.iri_media_type)

    @accepts_only('thing')
    def has_media_type(self, thing_res: URIRef) -> None:
        """
        Setter method corresponding to the ``dcat:mediaType`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The file type of the representation of the distribution (according to IANA media types).`

        :param thing_res: The value that will be set as the object of the property related to this method
        :type thing_res: URIRef
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_media_type()
        self.g.add((self.res, MetadataEntity.iri_media_type, thing_res))

    def remove_media_type(self) -> None:
        """
        Remover method corresponding to the ``dcat:mediaType`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_media_type, None))
