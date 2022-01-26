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

from typing import TYPE_CHECKING, Tuple, List, Optional

from oc_ocdm.abstract_entity import AbstractEntity
from rdflib import URIRef, Namespace, Graph

if TYPE_CHECKING:
    from typing import ClassVar, Dict
    from oc_ocdm.metadata.metadata_set import MetadataSet


class MetadataEntity(AbstractEntity):
    DCTERMS = Namespace("http://purl.org/dc/terms/")
    DCAT = Namespace("http://www.w3.org/ns/dcat#")
    VOID = Namespace("http://rdfs.org/ns/void#")

    iri_dataset = DCAT.Dataset
    iri_datafile = DCAT.Distribution

    iri_title = DCTERMS["title"]
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

    short_name_to_type_iri: ClassVar[Dict[str, URIRef]] = {
        '_dataset_': iri_dataset,
        'di': iri_datafile
    }

    def __init__(self, g: Graph, base_iri: str, dataset_name: str, m_set: MetadataSet,
                 res: URIRef = None, res_type: URIRef = None, resp_agent: str = None,
                 source: str = None, count: str = None, label: str = None, short_name: str = "",
                 preexisting_graph: Graph = None) -> None:
        super(MetadataEntity, self).__init__()
        self.g: Graph = g
        self.base_iri: str = base_iri
        self.dataset_name: str = dataset_name
        self.resp_agent: str = resp_agent
        self.source: str = source
        self.short_name: str = short_name
        self.m_set: MetadataSet = m_set
        self.preexisting_graph: Graph = Graph(identifier=g.identifier)
        self._merge_list: Tuple[MetadataEntity] = tuple()
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
            # Triples inside self.g are entirely replaced by triples from preexisting_graph.
            # This has maximum priority with respect to every other self.g initializations.
            # It's fundamental that the preexisting graph gets passed as an argument of the constructor:
            # allowing the user to set this value later through a method would mean that the user could
            # set the preexisting graph AFTER having modified self.g (which would not make sense).
            self.remove_every_triple()
            for p, o in preexisting_graph.predicate_objects(self.res):
                self.g.add((self.res, p, o))
                self.preexisting_graph.add((self.res, p, o))
        else:
            # Add mandatory information to the entity graph
            self._create_type(res_type)
            if label is not None:
                self.create_label(label)

    @staticmethod
    def _generate_new_res(count: str, base_res: str, short_name: str) -> URIRef:
        if short_name == '_dataset_':
            return URIRef(base_res)
        else:
            return URIRef(base_res + short_name + "/" + count)

    @property
    def to_be_deleted(self) -> bool:
        return self._to_be_deleted

    @property
    def was_merged(self) -> bool:
        return self._was_merged

    @property
    def merge_list(self) -> Tuple[MetadataEntity]:
        return self._merge_list

    def mark_as_to_be_deleted(self) -> None:
        # Here we must REMOVE triples pointing
        # to 'self' [THIS CANNOT BE UNDONE]:
        for res, entity in self.m_set.res_to_entity.items():
            triples_list: List[Tuple] = list(entity.g.triples((res, None, self.res)))
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

        # Here we must REDIRECT triples pointing
        # to 'other' to make them point to 'self':
        for res, entity in self.m_set.res_to_entity.items():
            triples_list: List[Tuple] = list(entity.g.triples((res, None, other.res)))
            for triple in triples_list:
                entity.g.remove(triple)
                new_triple = (triple[0], triple[1], self.res)
                entity.g.add(new_triple)

        types: List[URIRef] = other.get_types()
        for cur_type in types:
            self._create_type(cur_type)

        label: Optional[str] = other.get_label()
        if label is not None:
            self.create_label(label)

        self._was_merged = True
        self._merge_list = (*self._merge_list, other)

        # 'other' must be deleted AFTER the redirection of
        # triples pointing to it, since mark_as_to_be_deleted
        # also removes every triple pointing to 'other'
        other.mark_as_to_be_deleted()

    def commit_changes(self):
        self.preexisting_graph = Graph(identifier=self.g.identifier)
        if self._to_be_deleted:
            self.remove_every_triple()
        else:
            for triple in self.g.triples((self.res, None, None)):
                self.preexisting_graph.add(triple)
        self._to_be_deleted = False
        self._was_merged = False
        self._merge_list = tuple()
