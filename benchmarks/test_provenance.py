"""
Benchmarks for provenance generation operations.

Tests ProvSet operations for typical bibliographic data processing workflows.
"""

import pytest

from benchmarks.conftest import (
    BENCHMARK_ROUNDS,
    create_populated_graph_set,
    create_prov_set,
)


class TestProvenanceGeneration:
    """Benchmarks for generate_provenance() operation."""

    @pytest.mark.benchmark(group="provenance_generation")
    @pytest.mark.parametrize("entity_count", [50, 100, 200])
    def test_generate_provenance_creation(
        self, benchmark, redis_counter_handler, entity_count
    ):
        """
        Benchmark generate_provenance() for new entity creation.

        All entities are new (no preexisting graph), so this tests
        the creation snapshot path.
        """
        def setup():
            graph_set, _ = create_populated_graph_set(
                redis_counter_handler, entity_count
            )
            prov_set = create_prov_set(graph_set, redis_counter_handler)
            return (prov_set,), {}

        result = benchmark.pedantic(
            lambda prov_set: prov_set.generate_provenance(),
            setup=setup,
            rounds=BENCHMARK_ROUNDS
        )
        # Each record creates ~14 entities, each gets a provenance snapshot
        assert len(result) >= entity_count * 14


class TestProvenanceModification:
    """Benchmarks for provenance generation with modifications."""

    @pytest.mark.benchmark(group="provenance_modification")
    @pytest.mark.parametrize("entity_count", [50, 100, 200])
    def test_generate_provenance_modification(
        self, benchmark, redis_counter_handler, entity_count
    ):
        """
        Benchmark generate_provenance() for entity modifications.

        Creates entities, generates initial provenance, then modifies
        and generates provenance again. This tests the modification
        snapshot path with graph diff.
        """
        def setup():
            graph_set, brs = create_populated_graph_set(
                redis_counter_handler, entity_count
            )
            prov_set = create_prov_set(graph_set, redis_counter_handler)
            prov_set.generate_provenance()

            for i, br in enumerate(brs):
                br.has_title(f"Modified Title {i}")

            return (prov_set,), {}

        result = benchmark.pedantic(
            lambda prov_set: prov_set.generate_provenance(),
            setup=setup,
            rounds=BENCHMARK_ROUNDS
        )
        # All entities get new snapshots on second provenance generation
        assert len(result) >= entity_count * 14
