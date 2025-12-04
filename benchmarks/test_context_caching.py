"""
Benchmarks for JSON-LD context caching performance.

Compares serialization with local cached context vs remote URL fetch.
"""

import pytest
from rdflib import Dataset

from benchmarks.conftest import BENCHMARK_ROUNDS, create_populated_graph_set

CONTEXT_URL = "https://raw.githubusercontent.com/opencitations/corpus/master/context.json"

CONTEXT_DATA = {
    "@context": {
        "gocc": "https://w3id.org/oc/corpus/",
        "gprov": "https://w3id.org/oc/corpus/prov/",
        "gar": "https://w3id.org/oc/corpus/ar/",
        "gbe": "https://w3id.org/oc/corpus/be/",
        "gbr": "https://w3id.org/oc/corpus/br/",
        "datacite": "http://purl.org/spar/datacite/",
        "dcterms": "http://purl.org/dc/terms/",
        "fabio": "http://purl.org/spar/fabio/",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "frbr": "http://purl.org/vocab/frbr/core#",
        "literal": "http://www.essepuntato.it/2010/06/literalreification/",
        "prism": "http://prismstandard.org/namespaces/basic/2.0/",
        "pro": "http://purl.org/spar/pro/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
    }
}


class TestContextCaching:

    @pytest.mark.benchmark(group="context_caching")
    @pytest.mark.parametrize("entity_count", [10, 50, 100])
    def test_serialize_with_local_context(
        self, benchmark, redis_counter_handler, entity_count
    ):
        """Benchmark with local context dict (current hack approach)."""

        def setup():
            graph_set, _ = create_populated_graph_set(
                redis_counter_handler, entity_count
            )
            dataset = Dataset()
            for g in graph_set.graphs():
                dataset.addN((s, p, o, g.identifier) for s, p, o in g)
            return (dataset,), {}

        def serialize(dataset):
            return dataset.serialize(format="json-ld", context=CONTEXT_DATA)

        result = benchmark.pedantic(
            serialize, setup=setup, rounds=BENCHMARK_ROUNDS
        )
        assert len(result) > 0

    @pytest.mark.benchmark(group="context_caching")
    @pytest.mark.parametrize("entity_count", [10, 50, 100])
    def test_serialize_with_remote_context(
        self, benchmark, redis_counter_handler, entity_count
    ):
        """Benchmark with remote context URL (fetches from network)."""

        def setup():
            graph_set, _ = create_populated_graph_set(
                redis_counter_handler, entity_count
            )
            dataset = Dataset()
            for g in graph_set.graphs():
                dataset.addN((s, p, o, g.identifier) for s, p, o in g)
            return (dataset,), {}

        def serialize(dataset):
            return dataset.serialize(format="json-ld", context=CONTEXT_URL)

        result = benchmark.pedantic(
            serialize, setup=setup, rounds=BENCHMARK_ROUNDS
        )
        assert len(result) > 0
