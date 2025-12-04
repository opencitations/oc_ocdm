import pytest
from rdflib import Graph

from oc_ocdm.support.query_utils import _compute_graph_changes

from benchmarks.conftest import BENCHMARK_ROUNDS, create_populated_graph_set


class MockEntity:
    def __init__(self, current_graph, preexisting_graph):
        self.g = current_graph
        self.preexisting_graph = preexisting_graph
        self.to_be_deleted = False


class TestGraphDiff:

    @pytest.mark.benchmark(group="graph_diff")
    @pytest.mark.parametrize("entity_count", [50, 100, 150])
    def test_compute_graph_changes_modified(
        self, benchmark, redis_counter_handler, entity_count
    ):
        def setup():
            graph_set, brs = create_populated_graph_set(
                redis_counter_handler, entity_count
            )
            entities = []
            for entity in graph_set.res_to_entity.values():
                preexisting = Graph()
                for triple in entity.g:
                    preexisting.add(triple)
                mock = MockEntity(entity.g, preexisting)
                entities.append(mock)
            for i, br in enumerate(brs):
                br.has_title(f"Modified Title {i}")
            return (entities,), {}

        def compute_changes(entities):
            results = []
            for entity in entities:
                result = _compute_graph_changes(entity, "graph")
                results.append(result)
            return results

        result = benchmark.pedantic(
            compute_changes, setup=setup, rounds=BENCHMARK_ROUNDS
        )
        assert len(result) >= entity_count * 14
        entities_with_changes = sum(
            1 for to_insert, to_delete, n_added, n_removed in result
            if n_added > 0 or n_removed > 0
        )
        assert entities_with_changes == entity_count, (
            f"Expected {entity_count} entities with changes, "
            f"got {entities_with_changes}"
        )
