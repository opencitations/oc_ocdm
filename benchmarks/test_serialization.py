"""
Benchmarks for serialization and storage operations.

Tests Storer operations for typical bibliographic data processing workflows.
"""

import os

import pytest

from oc_ocdm.storer import Storer
from oc_ocdm.support.query_utils import (
    get_update_query,
    serialize_graph_to_nquads,
)

from benchmarks.conftest import (
    BASE_IRI,
    BENCHMARK_ROUNDS,
    create_populated_graph_set,
    create_prov_set,
)


class TestStoreAll:
    """Benchmarks for store_all() file serialization."""

    @pytest.mark.benchmark(group="store_all")
    @pytest.mark.parametrize("entity_count", [50, 100, 200])
    def test_store_all_jsonld(
        self, benchmark, tmp_path, redis_counter_handler, entity_count
    ):
        """Benchmark store_all() with JSON-LD output format."""
        def setup():
            graph_set, _ = create_populated_graph_set(
                redis_counter_handler, entity_count
            )

            output_dir = tmp_path / f"jsonld_{entity_count}"
            os.makedirs(output_dir, exist_ok=True)

            storer = Storer(
                abstract_set=graph_set,
                output_format="json-ld",
                dir_split=0,
                n_file_item=1000,
                default_dir="_"
            )

            return (storer, graph_set, str(output_dir)), {}

        def store_jsonld(storer, graph_set, output_dir):
            storer.store_all(
                base_dir=output_dir + os.sep,
                base_iri=BASE_IRI
            )
            return graph_set

        result = benchmark.pedantic(store_jsonld, setup=setup, rounds=BENCHMARK_ROUNDS)
        # Each record creates ~14 entities
        assert len(result.res_to_entity) >= entity_count * 14


class TestUploadAll:
    """Benchmarks for upload_all() SPARQL query generation."""

    @pytest.mark.benchmark(group="upload_all")
    @pytest.mark.parametrize("entity_count", [50, 100, 200])
    def test_upload_all_bulk_load(
        self, benchmark, tmp_path, redis_counter_handler, entity_count
    ):
        """
        Benchmark upload_all() with prepare_bulk_load=True.

        This generates N-Quads for Virtuoso bulk loading.
        """
        def setup():
            graph_set, _ = create_populated_graph_set(
                redis_counter_handler, entity_count
            )

            prov_set = create_prov_set(graph_set, redis_counter_handler)
            modified_entities = prov_set.generate_provenance()

            storer = Storer(
                abstract_set=graph_set,
                output_format="nquads",
                dir_split=0,
                n_file_item=1000,
                default_dir="_",
                modified_entities=modified_entities
            )

            bulk_load_dir = str(tmp_path / f"nquads_{entity_count}")
            os.makedirs(bulk_load_dir, exist_ok=True)

            queries_dir = str(tmp_path / f"queries_{entity_count}")

            return (storer, modified_entities, queries_dir, bulk_load_dir), {}

        def generate_nquads(storer, modified_entities, queries_dir, bulk_load_dir):
            storer.upload_all(
                triplestore_url=None,
                base_dir=queries_dir,
                batch_size=10,
                prepare_bulk_load=True,
                bulk_load_dir=bulk_load_dir
            )
            return modified_entities

        result = benchmark.pedantic(generate_nquads, setup=setup, rounds=BENCHMARK_ROUNDS)
        # Each record creates ~14 entities, each gets a provenance snapshot
        assert len(result) >= entity_count * 14


class TestSerializationHelpers:
    """Benchmarks for serialization helper functions."""

    @pytest.mark.benchmark(group="update_query")
    @pytest.mark.parametrize("count", [50, 100, 200])
    def test_get_update_query_batch(self, benchmark, redis_counter_handler, count):
        """Benchmark get_update_query() for multiple entities."""
        def setup():
            graph_set, _ = create_populated_graph_set(redis_counter_handler, count)
            entities = list(graph_set.res_to_entity.values())
            return (entities,), {}

        def generate_queries(entities):
            queries = []
            for entity in entities:
                query = get_update_query(entity, "graph")
                queries.append(query)
            return queries

        result = benchmark.pedantic(generate_queries, setup=setup, rounds=BENCHMARK_ROUNDS)
        # Each record creates ~14 entities
        assert len(result) >= count * 14

    @pytest.mark.benchmark(group="nquads_serialization")
    @pytest.mark.parametrize("count", [50, 100, 200])
    def test_serialize_graph_to_nquads_batch(
        self, benchmark, redis_counter_handler, count
    ):
        """Benchmark serialize_graph_to_nquads() for multiple entities."""
        def setup():
            graph_set, _ = create_populated_graph_set(redis_counter_handler, count)
            entities = list(graph_set.res_to_entity.values())
            return (entities,), {}

        def serialize_graphs(entities):
            nquads = []
            for entity in entities:
                graph_iri = str(entity.g.identifier)
                nq = serialize_graph_to_nquads(entity.g, graph_iri)
                nquads.append(nq)
            return nquads

        result = benchmark.pedantic(serialize_graphs, setup=setup, rounds=BENCHMARK_ROUNDS)
        # Each record creates ~14 entities
        assert len(result) >= count * 14
