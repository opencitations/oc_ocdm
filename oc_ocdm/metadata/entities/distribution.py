#!/usr/bin/python

# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
from __future__ import annotations

from oc_ocdm.constants import XSD_DATETIME, XSD_DECIMAL
from triplelite import RDFTerm
from oc_ocdm.metadata.metadata_entity import MetadataEntity


class Distribution(MetadataEntity):
    """Distribution (short: di): an accessible form of a dataset, for example a downloadable
       file."""

    def _merge_properties(self, other: MetadataEntity) -> None:
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
        super()._merge_properties(other)
        assert isinstance(other, Distribution)

        title: str | None = other.get_title()
        if title is not None:
            self.has_title(title)

        description: str | None = other.get_description()
        if description is not None:
            self.has_description(description)

        pub_date: str | None = other.get_publication_date()
        if pub_date is not None:
            self.has_publication_date(pub_date)

        byte_size: str | None = other.get_byte_size()
        if byte_size is not None:
            self.has_byte_size(byte_size)

        license_uri: str | None = other.get_license()
        if license_uri is not None:
            self.has_license(license_uri)

        download_url: str | None = other.get_download_url()
        if download_url is not None:
            self.has_download_url(download_url)

        media_type: str | None = other.get_media_type()
        if media_type is not None:
            self.has_media_type(media_type)

    # HAS TITLE
    def get_title(self) -> str | None:
        """
        Getter method corresponding to the ``dcterms:title`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(MetadataEntity.iri_title)

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
    def get_description(self) -> str | None:
        """
        Getter method corresponding to the ``dcterms:description`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(MetadataEntity.iri_description)

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
    def get_publication_date(self) -> str | None:
        """
        Getter method corresponding to the ``dcterms:issued`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(MetadataEntity.iri_issued)

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
        self._create_literal(MetadataEntity.iri_issued, string, XSD_DATETIME, False)

    def remove_publication_date(self) -> None:
        """
        Remover method corresponding to the ``dcterms:issued`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_issued, None))

    # HAS BYTE SIZE
    def get_byte_size(self) -> str | None:
        """
        Getter method corresponding to the ``dcat:byte_size`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(MetadataEntity.iri_byte_size)

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
        self._create_literal(MetadataEntity.iri_byte_size, string, XSD_DECIMAL)

    def remove_byte_size(self) -> None:
        """
        Remover method corresponding to the ``dcat:byte_size`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_byte_size, None))

    # HAS LICENSE
    def get_license(self) -> str | None:
        """
        Getter method corresponding to the ``dcterms:license`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_uri_reference(MetadataEntity.iri_license)

    def has_license(self, thing_res: str) -> None:
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
        self.g.add((self.res, MetadataEntity.iri_license, RDFTerm("uri", str(thing_res))))

    def remove_license(self) -> None:
        """
        Remover method corresponding to the ``dcterms:license`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_license, None))

    # HAS DOWNLOAD URL
    def get_download_url(self) -> str | None:
        """
        Getter method corresponding to the ``dcat:downloadURL`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_uri_reference(MetadataEntity.iri_download_url)

    def has_download_url(self, thing_res: str) -> None:
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
        self.g.add((self.res, MetadataEntity.iri_download_url, RDFTerm("uri", str(thing_res))))

    def remove_download_url(self) -> None:
        """
        Remover method corresponding to the ``dcat:downloadURL`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_download_url, None))

    # HAS_MEDIA_TYPE
    def get_media_type(self) -> str | None:
        """
        Getter method corresponding to the ``dcat:mediaType`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_uri_reference(MetadataEntity.iri_media_type)

    def has_media_type(self, thing_res: str) -> None:
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
        self.g.add((self.res, MetadataEntity.iri_media_type, RDFTerm("uri", str(thing_res))))

    def remove_media_type(self) -> None:
        """
        Remover method corresponding to the ``dcat:mediaType`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_media_type, None))
