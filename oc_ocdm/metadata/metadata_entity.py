#!/usr/bin/python

# SPDX-FileCopyrightText: 2020-2022 Simone Persiani <iosonopersia@gmail.com>
#
# SPDX-License-Identifier: ISC

# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING, List

from oc_ocdm.abstract_entity import AbstractEntity
from oc_ocdm.constants import Namespace
from triplelite import RDFTerm, SubgraphView, TripleLite, rdflib_to_rdfterm

if TYPE_CHECKING:
    from typing import ClassVar, Dict

    from oc_ocdm.metadata.metadata_set import MetadataSet


class MetadataEntity(AbstractEntity):
    DCTERMS = Namespace("http://purl.org/dc/terms/")
    DCAT = Namespace("http://www.w3.org/ns/dcat#")
    VOID = Namespace("http://rdfs.org/ns/void#")

    iri_dataset = DCAT.Dataset
    iri_datafile = DCAT.Distribution

    iri_title = DCTERMS.title
    iri_description = DCTERMS.description
    iri_issued = DCTERMS.issued
    iri_modified = DCTERMS.modified
    iri_keyword = DCAT.keyword
    iri_subject = DCAT.theme
    iri_landing_page = DCAT.landingPage
    iri_subset = VOID.subset
    iri_sparql_endpoint = VOID.sparqlEndpoint
    iri_distribution = DCAT.distribution
    iri_license = DCTERMS.license
    iri_download_url = DCAT.downloadURL
    iri_media_type = DCAT.mediaType
    iri_byte_size = DCAT.byte_size

    short_name_to_type_iri: ClassVar[Dict[str, str]] = {
        '_dataset_': iri_dataset,
        'di': iri_datafile
    }

    def __init__(self, g: TripleLite, base_iri: str, dataset_name: str, m_set: MetadataSet,
                 res_type: str, res: str | None = None, resp_agent: str | None = None,
                 source: str | None = None, count: str | None = None, label: str | None = None, short_name: str = "",
                 preexisting_graph: SubgraphView | None = None) -> None:
        super(MetadataEntity, self).__init__()
        self.g: TripleLite = g
        self.base_iri: str = base_iri
        self.dataset_name: str = dataset_name
        self.resp_agent: str | None = resp_agent
        self.source: str | None = source
        self.short_name: str = short_name
        self.m_set: MetadataSet = m_set
        self._preexisting_triples: frozenset | SubgraphView = frozenset()
        self._merge_list: tuple[MetadataEntity, ...] = ()
        # FLAGS
        self._to_be_deleted: bool = False
        self._was_merged: bool = False

        # If res was not specified, create from scratch the URI reference for this entity,
        # otherwise use the provided one
        if res is None:
            base_res: str = self.base_iri + self.dataset_name
            if base_res[-1] != '/':
                base_res += '/'
            self.res = self._generate_new_res(count, base_res, short_name)
        else:
            self.res = res

        if m_set is not None:
            # If not already done, register this MetadataEntity instance inside the MetadataSet
            if self.res not in m_set.res_to_entity:
                m_set.res_to_entity[self.res] = self

        if preexisting_graph is not None:
            self.remove_every_triple()
            self.g.add_many((self.res, p, rdflib_to_rdfterm(o)) for p, o in preexisting_graph.predicate_objects(self.res))
            self._preexisting_triples = preexisting_graph
        else:
            # Add mandatory information to the entity graph
            self._create_type(res_type)
            if label is not None:
                self.create_label(label)

    @staticmethod
    def _generate_new_res(count: str | None, base_res: str, short_name: str) -> str:
        if short_name == '_dataset_':
            return base_res
        else:
            assert count is not None
            return base_res + short_name + "/" + count

    @property
    def to_be_deleted(self) -> bool:
        return self._to_be_deleted

    @property
    def was_merged(self) -> bool:
        return self._was_merged

    @property
    def merge_list(self) -> tuple[MetadataEntity, ...]:
        return self._merge_list

    def mark_as_to_be_deleted(self) -> None:
        # Here we must REMOVE triples pointing
        # to 'self' [THIS CANNOT BE UNDONE]:
        for res, entity in self.m_set.res_to_entity.items():
            triples_list: List[tuple] = list(entity.g.triples((res, None, RDFTerm("uri", str(self.res)))))
            for triple in triples_list:
                entity.g.remove(triple)

        self._to_be_deleted = True

    def merge(self, other: MetadataEntity) -> None:
        """
        **WARNING:** ``MetadataEntity`` **is an abstract class that cannot be instantiated at runtime.
        As such, it's only possible to execute this method on entities generated from**
        ``MetadataEntity``'s **subclasses. Please, refer to their documentation of the** `merge` **method.**

        :param other: The entity which will be marked as to be deleted and whose properties will
         be merged into the current entity.
        :type other: MetadataEntity
        :raises TypeError: if the parameter is of the wrong type
        :return: None
        """
        if not isinstance(other, MetadataEntity) or other.short_name != self.short_name:
            raise TypeError(
                f"[{self.__class__.__name__}.merge] Expected entity type: {self.short_name}. "
                f"Provided: {type(other).__name__}."
            )

        # Here we must REDIRECT triples pointing
        # to 'other' to make them point to 'self':
        for res, entity in self.m_set.res_to_entity.items():
            triples_list: List[tuple] = list(entity.g.triples((res, None, RDFTerm("uri", str(other.res)))))
            for triple in triples_list:
                entity.g.remove(triple)
                new_triple = (triple[0], triple[1], RDFTerm("uri", str(self.res)))
                entity.g.add(new_triple)

        types: List[str] = other.get_types()
        for cur_type in types:
            self._create_type(cur_type)

        label: str | None = other.get_label()
        if label is not None:
            self.create_label(label)

        self._was_merged = True
        self._merge_list = (*self._merge_list, other)

        # 'other' must be deleted AFTER the redirection of
        # triples pointing to it, since mark_as_to_be_deleted
        # also removes every triple pointing to 'other'
        other.mark_as_to_be_deleted()

        self._merge_properties(other)

    def _merge_properties(self, other: MetadataEntity) -> None:
        pass

    def commit_changes(self):
        if self._to_be_deleted:
            self._preexisting_triples = frozenset()
            self.remove_every_triple()
        else:
            self._preexisting_triples = frozenset(self.g.triples((self.res, None, None)))
        self._to_be_deleted = False
        self._was_merged = False
        self._merge_list = ()
