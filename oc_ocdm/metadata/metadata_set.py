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
__author__ = 'essepuntato'

from typing import TYPE_CHECKING, Tuple, ClassVar

from oc_ocdm.counter_handler import CounterHandler
from oc_ocdm.metadata.entities import Dataset, Distribution

if TYPE_CHECKING:
    from typing import Dict, Optional

from rdflib import Graph, URIRef

from oc_ocdm.metadata import MetadataEntity
from oc_ocdm.abstract_set import AbstractSet


class MetadataSet(AbstractSet):
    # Labels
    labels: ClassVar[Dict[str, str]] = {
        "_dataset_": "dataset",
        "di": "distribution"
    }

    def __init__(self, base_iri: str, counter_handler: CounterHandler, dataset_home: str,
                 wanted_label: bool = True) -> None:
        super(MetadataSet, self).__init__()
        # The following variable maps a URIRef with the related metadata entity
        self.res_to_entity: Dict[URIRef, MetadataEntity] = {}
        self.base_iri: str = base_iri
        self.dataset_home: URIRef = URIRef(dataset_home)
        self.wanted_label: bool = wanted_label

        self.counter_handler: CounterHandler = counter_handler

    def get_entity(self, res: URIRef) -> Optional[MetadataEntity]:
        if res in self.res_to_entity:
            return self.res_to_entity[res]

    def add_dataset(self, resp_agent: str, source_agent: str = None, source: str = None,
                    res: URIRef = None, preexisting_graph: Graph = None) -> Dataset:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add_metadata(graph_url=str(self.dataset_home), res=res, short_name="_dataset_")
        return Dataset(cur_g, res=res, res_type=MetadataEntity.iri_dataset, short_name="_dataset_",
                       resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                       label=label, m_set=self, preexisting_graph=preexisting_graph)

    def add_di(self, resp_agent: str, source_agent: str = None, source: str = None,
               res: URIRef = None, preexisting_graph: Graph = None) -> Distribution:
        if res is not None and res in self.res_to_entity:
            return self.res_to_entity[res]
        cur_g, count, label = self._add_metadata(graph_url=str(self.dataset_home), res=res, short_name="di")
        return Distribution(cur_g, res=res, res_type=MetadataEntity.iri_distribution, short_name="di",
                            resp_agent=resp_agent, source_agent=source_agent, source=source, count=count,
                            label=label, m_set=self, preexisting_graph=preexisting_graph)

    def _add_metadata(self, graph_url: str, res: URIRef, short_name: str,
                      dataset_name: str) -> Tuple[Graph, Optional[str], Optional[str]]:
        cur_g: Graph = Graph(identifier=graph_url + '/' + dataset_name)
        self._set_ns(cur_g)

        count: Optional[str] = None
        label: Optional[str] = None

        if res is not None:
            return cur_g, count, label

        if short_name != '_dataset_':
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
        g.namespace_manager.bind("mtt", MetadataEntity.MTT)
        g.namespace_manager.bind("dbr", MetadataEntity.DBR)

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

    """
    def update_dataset_info(self, graph_set):
        cur_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        subgraphs_to_update = set()
        all_graphs = []

        for g in graph_set.graphs():
            cur_id = g.identifier
            if cur_id not in subgraphs_to_update:
                subgraphs_to_update.add(cur_id)
                cur_dataset_res = URIRef(cur_id)
                cur_dataset = self.get_dataset_graph(cur_dataset_res, cur_time)
                self.update_modification_date(cur_dataset, cur_dataset_res, cur_time)
                all_graphs += [cur_dataset]

        if subgraphs_to_update:
            cur_occ_res = URIRef(self.base_iri)
            cur_occ = self.get_dataset_graph(cur_occ_res, cur_time)
            self.update_modification_date(cur_occ, cur_occ_res, cur_time)

            for subgraph_id in subgraphs_to_update:
                self.has_subset(cur_occ, cur_occ_res, URIRef(subgraph_id))
            all_graphs += [cur_occ]

        if all_graphs:  # Store everything and upload to triplestore
            if self.tp_url is None:
                self.st.store_all(
                    self.base_dir, self.base_iri, self.context_path,
                    self.tmp_dir, all_graphs, True)
            else:
                self.st.upload_and_store(
                    self.base_dir, self.tp_url, self.base_iri, self.context_path,
                    self.tmp_dir, all_graphs, True)

    def get_dataset_graph(self, res, cur_time):
        dataset_path = self.get_metadata_path_from_resource(res)
        if os.path.exists(dataset_path):
            return list(self.st.load(dataset_path, tmp_dir=self.tmp_dir).contexts())[0]
        else:
            dataset_label = "ccc"
            dataset_title = "The Citations in Context Corpus"
            dataset_description = "The Citations in Context Corpus is an open repository of scholarly " \
                                  "citation data made available under a Creative Commons public " \
                                  "domain dedication, which provides in RDF accurate citation " \
                                  "information (bibliographic references) harvested from the " \
                                  "scholarly literature (described using the SPAR Ontologies) " \
                                  "that others may freely build upon, enhance and reuse for any " \
                                  "purpose, without restriction under copyright or database law."
            if re.search("/../$", str(res)) is not None:
                g = Graph(identifier=str(res))
                dataset_short_name = str(res)[-3:-1]
                dataset_name = GraphSet.labels[dataset_short_name]
                dataset_title += ": %s dataset" % dataset_name.title()
                dataset_description += " This sub-dataset contains all the '%s' resources." % \
                                       dataset_name
                dataset_label += " / %s" % dataset_short_name
                self.create_keyword(g, res, dataset_name)
            else:
                g = Graph()
                self.has_landing_page(g, res, self.dataset_home)
                self.has_sparql_endpoint(g, res, self.tp_res)
            self.dataset_type(g, res)
            self.create_label(g, res, dataset_label)
            self.create_title(g, res, dataset_title)
            self.create_description(g, res, dataset_description)
            self.create_publication_date(g, res, cur_time)
            self.create_keyword(g, res, "OCC")
            self.create_keyword(g, res, "ccc")
            self.create_keyword(g, res, "OpenCitations")
            self.create_keyword(g, res, "Citations in Context Corpus")
            self.create_keyword(g, res, "SPAR Ontologies")
            self.create_keyword(g, res, "bibliographic references")
            self.create_keyword(g, res, "citations")
            self.has_subject(g, res, self.bibliographic_database)
            self.has_subject(g, res, self.scholary_communication)
            self.has_subject(g, res, self.open_access)
            self.has_subject(g, res, self.citations)

            return g

    def get_metadata_path_from_resource(self, dataset_res):
        return self.get_metadata_path_from_iri(str(dataset_res))

    def get_metadata_path_from_iri(self, dataset_iri):
        return re.sub("^%s" % self.base_iri, self.base_dir, dataset_iri) + "index.json"
    """