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
        return self._get_literal(MetadataEntity.iri_title)

    @accepts_only('literal')
    def has_title(self, string: str) -> None:
        """The title of the dataset."""
        self.remove_title()
        self._create_literal(MetadataEntity.iri_title, string)

    def remove_title(self) -> None:
        self.g.remove((self.res, MetadataEntity.iri_title, None))

    # HAS DESCRIPTION
    def get_description(self) -> Optional[str]:
        return self._get_literal(MetadataEntity.iri_description)

    @accepts_only('literal')
    def has_description(self, string: str) -> None:
        """A short textual description of the content of the dataset."""
        self.remove_description()
        self._create_literal(MetadataEntity.iri_description, string)

    def remove_description(self) -> None:
        self.g.remove((self.res, MetadataEntity.iri_description, None))

    # HAS PUBLICATION DATE
    def get_publication_date(self) -> Optional[str]:
        return self._get_literal(MetadataEntity.iri_issued)

    @accepts_only('literal')
    def has_publication_date(self, string: str) -> None:
        """The date of first publication of the dataset."""
        self.remove_publication_date()
        self._create_literal(MetadataEntity.iri_issued, string, XSD.dateTime, False)

    def remove_publication_date(self) -> None:
        self.g.remove((self.res, MetadataEntity.iri_issued, None))

    # HAS MODIFICATION DATE
    def get_modification_date(self) -> Optional[str]:
        return self._get_literal(MetadataEntity.iri_modified)

    @accepts_only('literal')
    def has_modification_date(self, string: str) -> None:
        """The date on which the dataset has been modified."""
        self.remove_modification_date()
        self._create_literal(MetadataEntity.iri_modified, string, XSD.dateTime, False)

    def remove_modification_date(self) -> None:
        self.g.remove((self.res, MetadataEntity.iri_modified, None))

    # HAS KEYWORD
    def get_keywords(self) -> List[str]:
        return self._get_multiple_literals(MetadataEntity.iri_keyword)

    @accepts_only('literal')
    def has_keyword(self, string: str) -> None:
        """A keyword or phrase describing the content of the dataset."""
        self._create_literal(MetadataEntity.iri_keyword, string)

    @accepts_only('literal')
    def remove_keyword(self, string: str = None) -> None:
        if string is not None:
            self.g.remove((self.res, MetadataEntity.iri_keyword, string))
        else:
            self.g.remove((self.res, MetadataEntity.iri_keyword, None))

    # HAS SUBJECT
    def get_subjects(self) -> List[URIRef]:
        return self._get_multiple_uri_references(MetadataEntity.iri_subject)

    @accepts_only('thing')
    def has_subject(self, thing_res: URIRef) -> None:
        """A concept describing the primary subject of the dataset."""
        self.g.add((self.res, MetadataEntity.iri_subject, thing_res))

    @accepts_only('thing')
    def remove_subject(self, thing_res: URIRef = None) -> None:
        if thing_res is not None:
            self.g.remove((self.res, MetadataEntity.iri_subject, thing_res))
        else:
            self.g.remove((self.res, MetadataEntity.iri_subject, None))

    # HAS LANDING PAGE
    def get_landing_page(self) -> Optional[URIRef]:
        return self._get_literal(MetadataEntity.iri_landing_page)

    @accepts_only('thing')
    def has_landing_page(self, thing_res: URIRef) -> None:
        """An HTML page (indicated by its URL) representing a browsable page for the dataset."""
        self.remove_landing_page()
        self.g.add((self.res, MetadataEntity.iri_landing_page, thing_res))

    def remove_landing_page(self) -> None:
        self.g.remove((self.res, MetadataEntity.iri_landing_page, None))

    # HAS SUB-DATASET
    def get_sub_datasets(self) -> List[Dataset]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(MetadataEntity.iri_subset)
        result: List[Dataset] = []
        for uri in uri_list:
            result.append(self.m_set.add_dataset(self.resp_agent, self.source_agent, self.source, uri))
        return result

    @accepts_only('_dataset_')
    def has_sub_dataset(self, obj: Dataset) -> None:
        """A link to a subset of the present dataset."""
        self.g.add((self.res, MetadataEntity.iri_subset, obj.res))

    @accepts_only('_dataset_')
    def remove_sub_dataset(self, dataset_res: Dataset = None) -> None:
        if dataset_res is not None:
            self.g.remove((self.res, MetadataEntity.iri_subset, dataset_res.res))
        else:
            self.g.remove((self.res, MetadataEntity.iri_subset, None))

    # HAS SPARQL ENDPOINT
    def get_sparql_endpoint(self) -> Optional[URIRef]:
        return self._get_uri_reference(MetadataEntity.iri_sparql_endpoint)

    @accepts_only('thing')
    def has_sparql_endpoint(self, thing_res: URIRef) -> None:
        """The link to the SPARQL endpoint for querying the dataset."""
        self.remove_sparql_endpoint()
        self.g.add((self.res, MetadataEntity.iri_sparql_endpoint, thing_res))

    def remove_sparql_endpoint(self) -> None:
        self.g.remove((self.res, MetadataEntity.iri_sparql_endpoint, None))

    # HAS DISTRIBUTION (Distribution)
    def get_distributions(self) -> List[Distribution]:
        uri_list: List[URIRef] = self._get_multiple_uri_references(MetadataEntity.iri_distribution)
        result: List[Distribution] = []
        for uri in uri_list:
            result.append(self.m_set.add_di(self.resp_agent, self.source_agent, self.source, uri))
        return result

    @accepts_only('di')
    def has_distribution(self, obj: Distribution) -> None:
        """A distribution of the dataset."""
        self.g.add((self.res, MetadataEntity.iri_distribution, obj.res))

    @accepts_only('di')
    def remove_distribution(self, di_res: Distribution = None) -> None:
        if di_res is not None:
            self.g.remove((self.res, MetadataEntity.iri_distribution, di_res.res))
        else:
            self.g.remove((self.res, MetadataEntity.iri_distribution, None))
