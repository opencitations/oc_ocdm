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

from oc_ocdm.counter_handler.counter_handler import CounterHandler
from oc_ocdm.counter_handler.filesystem_counter_handler import FilesystemCounterHandler
from oc_ocdm.counter_handler.in_memory_counter_handler import InMemoryCounterHandler
from oc_ocdm.metadata.entities.dataset import Dataset
from oc_ocdm.metadata.entities.distribution import Distribution
from oc_ocdm.support.support import get_count, is_dataset, get_short_name

if TYPE_CHECKING:
    from typing import Dict, Optional, Tuple, ClassVar

from rdflib import Graph, URIRef

from oc_ocdm.metadata.metadata_entity import MetadataEntity
from oc_ocdm.abstract_set import AbstractSet


class MetadataSet(AbstractSet):
    # Labels
    labels: ClassVar[Dict[str, str]] = {
        "_dataset_": "dataset",
        "di": "distribution"
    }

    def __init__(self, base_iri: str, info_dir: str = "", wanted_label: bool = True) -> None:
        super(MetadataSet, self).__init__()
        # The following variable maps a URIRef with the related metadata entity
        self.res_to_entity: Dict[URIRef, MetadataEntity] = {}
        self.base_iri: str = base_iri
        if self.base_iri[-1] != '/':
            self.base_iri += '/'
        self.wanted_label: bool = wanted_label

        if info_dir is not None and info_dir != "":
            self.counter_handler: CounterHandler = FilesystemCounterHandler(info_dir)
        else:
            self.counter_handler: CounterHandler = InMemoryCounterHandler()

    def get_entity(self, res: URIRef) -> Optional[MetadataEntity]:
        if res in self.res_to_entity:
            return self.res_to_entity[res]

    def add_dataset(self, dataset_name: str, resp_agent: str, source: str = None, res: URIRef = None,
                    preexisting_graph: Graph = None) -> Dataset:
        if res is not None and not is_dataset(res):
            raise ValueError(f"Given res: <{res}> is inappropriate for a Dataset entity.")
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        # Here we use a fictitious short name for Dataset, since the OCDM document doesn't specify
        # any particular short name for this type of entity. It's only used internally to distinguish
        # between different metadata entities but it's meaningless outside of this scope.
        cur_g, count, label = self._add_metadata("_dataset_", dataset_name, res)
        return Dataset(cur_g, self.base_iri, dataset_name, self, res,
                       MetadataEntity.iri_dataset, resp_agent,
                       source, count, label, "_dataset_", preexisting_graph)

    def add_di(self, dataset_name: str, resp_agent: str, source: str = None,
               res: URIRef = None, preexisting_graph: Graph = None) -> Distribution:
        if res is not None and get_short_name(res) != "di":
            raise ValueError(f"Given res: <{res}> is inappropriate for a Distribution entity.")
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add_metadata("di", dataset_name, res)
        return Distribution(cur_g, self.base_iri, dataset_name, self, res,
                            MetadataEntity.iri_datafile, resp_agent,
                            source, count, label, "di", preexisting_graph)

    def _add_metadata(self, short_name: str, dataset_name: str,
                      res: URIRef = None) -> Tuple[Graph, Optional[str], Optional[str]]:
        cur_g: Graph = Graph()
        self._set_ns(cur_g)

        count: Optional[str] = None
        label: Optional[str] = None

        if res is not None:
            if short_name != '_dataset_':  # Datasets don't have a counter associated with them...
                try:
                    res_count: int = int(get_count(res))
                except ValueError:
                    res_count: int = -1
                if res_count > self.counter_handler.read_metadata_counter(short_name, dataset_name):
                    self.counter_handler.set_metadata_counter(res_count, short_name, dataset_name)
            return cur_g, count, label

        if short_name != '_dataset_':  # Datasets don't have a counter associated with them...
            count = str(self.counter_handler.increment_metadata_counter(short_name, dataset_name))

        if self.wanted_label:
            label = "%s %s [%s/%s]" % (self.labels[short_name], count, short_name, count)

        return cur_g, count, label

    def commit_changes(self):
        for res, entity in self.res_to_entity.items():
            entity.commit_changes()
            if entity.to_be_deleted:
                del self.res_to_entity[res]

    @staticmethod
    def _set_ns(g: Graph) -> None:
        g.namespace_manager.bind("dcterms", MetadataEntity.DCTERMS)
        g.namespace_manager.bind("dcat", MetadataEntity.DCAT)
        g.namespace_manager.bind("void", MetadataEntity.VOID)

    def get_dataset(self) -> Tuple[Dataset]:
        result: Tuple[Dataset] = tuple()
        for ref in self.res_to_entity:
            entity: MetadataEntity = self.res_to_entity[ref]
            if isinstance(entity, Dataset):
                result += (entity, )
        return result

    def get_di(self) -> Tuple[Distribution]:
        result: Tuple[Distribution] = tuple()
        for ref in self.res_to_entity:
            entity: MetadataEntity = self.res_to_entity[ref]
            if isinstance(entity, Distribution):
                result += (entity, )
        return result
