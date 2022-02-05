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
from oc_ocdm.metadata.metadata_entity import MetadataEntity
from rdflib import XSD

if TYPE_CHECKING:
    from typing import Optional, List
    from rdflib import URIRef
    from oc_ocdm.metadata.entities.distribution import Distribution


class Dataset(MetadataEntity):
    """Dataset (short: not applicable and strictly dependent on the implementation of the
       dataset infrastructure): a set of collected information about something."""

    @accepts_only('_dataset_')
    def merge(self, other: Dataset) -> None:
        """
        The merge operation allows combining two ``Dataset`` entities into a single one,
        by marking the second entity as to be deleted while also copying its data into the current
        ``Dataset``. Moreover, every triple from the containing ``MetadataSet`` referring to the second
        entity gets "redirected" to the current entity: **every other reference contained inside a
        different source (e.g. a triplestore) must be manually handled by the user!**

        In case of functional properties, values from the current entity get overwritten
        by those coming from the second entity while, in all other cases, values from the
        second entity are simply appended to those of the current entity. In this context,
        ``rdfs:label`` is considered as a functional property, while ``rdf:type`` is not.

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: Dataset
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        super(Dataset, self).merge(other)

        title: Optional[str] = other.get_title()
        if title is not None:
            self.has_title(title)

        description: Optional[str] = other.get_description()
        if description is not None:
            self.has_description(description)

        pub_date: Optional[str] = other.get_publication_date()
        if pub_date is not None:
            self.has_publication_date(pub_date)

        mod_date: Optional[str] = other.get_modification_date()
        if mod_date is not None:
            self.has_modification_date(mod_date)

        keywords_list: List[str] = other.get_keywords()
        for cur_keyword in keywords_list:
            self.has_keyword(cur_keyword)

        subjects_list: List[URIRef] = other.get_subjects()
        for cur_subject in subjects_list:
            self.has_subject(cur_subject)

        landing_page: Optional[URIRef] = other.get_landing_page()
        if landing_page is not None:
            self.has_landing_page(landing_page)

        sub_datasets_list: List[Dataset] = other.get_sub_datasets()
        for cur_sub_dataset in sub_datasets_list:
            self.has_sub_dataset(cur_sub_dataset)

        sparql_endpoint: Optional[URIRef] = other.get_sparql_endpoint()
        if sparql_endpoint is not None:
            self.has_sparql_endpoint(sparql_endpoint)

        distributions_list: List[Distribution] = other.get_distributions()
        for cur_distribution in distributions_list:
            self.has_distribution(cur_distribution)

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

        `The title of the dataset.`

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

        `A short textual description of the content of the dataset.`

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

        `The date of first publication of the dataset.`

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

    # HAS MODIFICATION DATE
    def get_modification_date(self) -> Optional[str]:
        """
        Getter method corresponding to the ``dcterms:modified`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(MetadataEntity.iri_modified)

    @accepts_only('literal')
    def has_modification_date(self, string: str) -> None:
        """
        Setter method corresponding to the ``dcterms:modified`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The date on which the dataset has been modified.`

        :param string: The value that will be set as the object of the property related to this method. **It must
          be a string compliant with the** ``xsd:dateTime`` **datatype.**
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_modification_date()
        self._create_literal(MetadataEntity.iri_modified, string, XSD.dateTime, False)

    def remove_modification_date(self) -> None:
        """
        Remover method corresponding to the ``dcterms:modified`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_modified, None))

    # HAS KEYWORD
    def get_keywords(self) -> List[str]:
        """
        Getter method corresponding to the ``dcat:keyword`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        return self._get_multiple_literals(MetadataEntity.iri_keyword)

    @accepts_only('literal')
    def has_keyword(self, string: str) -> None:
        """
        Setter method corresponding to the ``dcat:keyword`` RDF predicate.

        `A keyword or phrase describing the content of the dataset.`

        :param string: The value that will be set as the object of the property related to this method
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self._create_literal(MetadataEntity.iri_keyword, string)

    @accepts_only('literal')
    def remove_keyword(self, string: str = None) -> None:
        """
        Remover method corresponding to the ``dcat:keyword`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param string: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type string: str
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if string is not None:
            self.g.remove((self.res, MetadataEntity.iri_keyword, string))
        else:
            self.g.remove((self.res, MetadataEntity.iri_keyword, None))

    # HAS SUBJECT
    def get_subjects(self) -> List[URIRef]:
        """
        Getter method corresponding to the ``dcat:theme`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(MetadataEntity.iri_subject)
        return uri_list

    @accepts_only('thing')
    def has_subject(self, thing_res: URIRef) -> None:
        """
        Setter method corresponding to the ``dcat:theme`` RDF predicate.

        `A concept describing the primary subject of the dataset.`

        :param thing_res: The value that will be set as the object of the property related to this method
        :type thing_res: URIRef
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, MetadataEntity.iri_subject, thing_res))

    @accepts_only('thing')
    def remove_subject(self, thing_res: URIRef = None) -> None:
        """
        Remover method corresponding to the ``dcat:theme`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param thing_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type thing_res: URIRef
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if thing_res is not None:
            self.g.remove((self.res, MetadataEntity.iri_subject, thing_res))
        else:
            self.g.remove((self.res, MetadataEntity.iri_subject, None))

    # HAS LANDING PAGE
    def get_landing_page(self) -> Optional[URIRef]:
        """
        Getter method corresponding to the ``dcat:landingPage`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        return self._get_literal(MetadataEntity.iri_landing_page)

    @accepts_only('thing')
    def has_landing_page(self, thing_res: URIRef) -> None:
        """
        Setter method corresponding to the ``dcat:landingPage`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `An HTML page (indicated by its URL) representing a browsable page for the dataset.`

        :param thing_res: The value that will be set as the object of the property related to this method
        :type thing_res: URIRef
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_landing_page()
        self.g.add((self.res, MetadataEntity.iri_landing_page, thing_res))

    def remove_landing_page(self) -> None:
        """
        Remover method corresponding to the ``dcat:landingPage`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_landing_page, None))

    # HAS SUB-DATASET
    def get_sub_datasets(self) -> List[Dataset]:
        """
        Getter method corresponding to the ``void:subset`` RDF predicate.

        :return: A list containing the requested values if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(MetadataEntity.iri_subset, '_dataset_')
        result: List[Dataset] = []
        for uri in uri_list:
            result.append(self.m_set.add_dataset(self.resp_agent, self.source, uri))
        return result

    @accepts_only('_dataset_')
    def has_sub_dataset(self, obj: Dataset) -> None:
        """
        Setter method corresponding to the ``void:subset`` RDF predicate.

        `A link to a subset of the present dataset.`

        :param obj: The value that will be set as the object of the property related to this method
        :type obj: Dataset
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, MetadataEntity.iri_subset, obj.res))

    @accepts_only('_dataset_')
    def remove_sub_dataset(self, dataset_res: Dataset = None) -> None:
        """
        Remover method corresponding to the ``void:subset`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param dataset_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type dataset_res: Dataset
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if dataset_res is not None:
            self.g.remove((self.res, MetadataEntity.iri_subset, dataset_res.res))
        else:
            self.g.remove((self.res, MetadataEntity.iri_subset, None))

    # HAS SPARQL ENDPOINT
    def get_sparql_endpoint(self) -> Optional[URIRef]:
        """
        Getter method corresponding to the ``void:sparqlEndpoint`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri: Optional[URIRef] = self._get_uri_reference(MetadataEntity.iri_sparql_endpoint)
        return uri

    @accepts_only('thing')
    def has_sparql_endpoint(self, thing_res: URIRef) -> None:
        """
        Setter method corresponding to the ``void:sparqlEndpoint`` RDF predicate.

        **WARNING: this is a functional property, hence any existing value will be overwritten!**

        `The link to the SPARQL endpoint for querying the dataset.`

        :param thing_res: The value that will be set as the object of the property related to this method
        :type thing_res: URIRef
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.remove_sparql_endpoint()
        self.g.add((self.res, MetadataEntity.iri_sparql_endpoint, thing_res))

    def remove_sparql_endpoint(self) -> None:
        """
        Remover method corresponding to the ``void:sparqlEndpoint`` RDF predicate.

        :return: None
        """
        self.g.remove((self.res, MetadataEntity.iri_sparql_endpoint, None))

    # HAS DISTRIBUTION (Distribution)
    def get_distributions(self) -> List[Distribution]:
        """
        Getter method corresponding to the ``dcat:distribution`` RDF predicate.

        :return: The requested value if found, None otherwise
        """
        uri_list: List[URIRef] = self._get_multiple_uri_references(MetadataEntity.iri_distribution, 'di')
        result: List[Distribution] = []
        for uri in uri_list:
            result.append(self.m_set.add_di(self.resp_agent, self.source, uri))
        return result

    @accepts_only('di')
    def has_distribution(self, obj: Distribution) -> None:
        """
        Setter method corresponding to the ``dcat:distribution`` RDF predicate.

        `A distribution of the dataset.`

        :param obj: The value that will be set as the object of the property related to this method
        :type obj: Distribution
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        self.g.add((self.res, MetadataEntity.iri_distribution, obj.res))

    @accepts_only('di')
    def remove_distribution(self, di_res: Distribution = None) -> None:
        """
        Remover method corresponding to the ``dcat:distribution`` RDF predicate.

        **WARNING: this is a non-functional property, hence, if the parameter
        is None, any existing value will be removed!**

        :param di_res: If not None, the specific object value that will be removed from the property
         related to this method (defaults to None)
        :type di_res: Distribution
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if di_res is not None:
            self.g.remove((self.res, MetadataEntity.iri_distribution, di_res.res))
        else:
            self.g.remove((self.res, MetadataEntity.iri_distribution, None))
