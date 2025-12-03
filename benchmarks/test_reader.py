"""
Benchmarks for Reader operations.

Tests Reader.import_entities_from_graph() methods.
"""

import pytest
from rdflib import Dataset

from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.reader import Reader

from benchmarks.conftest import (
    BASE_IRI,
    BENCHMARK_ROUNDS,
    RESP_AGENT,
    create_populated_graph_set,
)


class TestReaderImport:
    """Benchmarks for Reader.import_entities_from_graph() operations."""

    @pytest.mark.benchmark(group="reader_import")
    @pytest.mark.parametrize("entity_count", [50, 100, 200])
    def test_import_entities_from_graph(
        self, benchmark, redis_counter_handler, entity_count
    ):
        """Benchmark Reader.import_entities_from_graph()."""
        def setup():
            source_graph_set, _ = create_populated_graph_set(
                redis_counter_handler, entity_count
            )

            dataset = Dataset()
            for graph in source_graph_set.graphs():
                for triple in graph:
                    dataset.add((*triple, graph.identifier))

            target_graph_set = GraphSet(
                base_iri=BASE_IRI,
                wanted_label=False,
                custom_counter_handler=redis_counter_handler
            )

            return (target_graph_set, dataset), {}

        def import_entities(target_graph_set, dataset):
            Reader.import_entities_from_graph(
                g_set=target_graph_set,
                results=dataset,
                resp_agent=RESP_AGENT,
                enable_validation=False
            )
            return target_graph_set

        result = benchmark.pedantic(import_entities, setup=setup, rounds=BENCHMARK_ROUNDS)
        # Each record creates ~14 entities (4 BR, 3 AR, 3 RA, 3 ID, 1 RE)
        assert len(result.res_to_entity) >= entity_count * 14
