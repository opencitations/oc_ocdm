"""
Shared configuration and fixtures for oc_ocdm benchmarks.
"""

import os
from pathlib import Path

import pytest

from oc_ocdm.counter_handler.redis_counter_handler import RedisCounterHandler
from oc_ocdm.graph.graph_set import GraphSet
from oc_ocdm.prov.prov_set import ProvSet

from benchmarks.generators.data_factory import DataFactory

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ["REDIS_PORT"])
REDIS_DB = int(os.environ["REDIS_DB"])

BASE_IRI = "https://w3id.org/oc/meta/"
RESP_AGENT = "https://orcid.org/0000-0002-8420-0696"
SUPPLIER_PREFIX = "060"

BENCHMARK_ROUNDS = 5


@pytest.fixture(scope="session")
def redis_counter_handler():
    """Session-scoped RedisCounterHandler instance."""
    return RedisCounterHandler(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


def create_populated_graph_set(handler, entity_count):
    """
    Create a fresh GraphSet populated with test entities.

    Args:
        handler: RedisCounterHandler instance
        entity_count: Number of bibliographic records to create

    Returns:
        Tuple of (GraphSet, list of created BibliographicResource entities)
    """
    graph_set = GraphSet(
        base_iri=BASE_IRI,
        wanted_label=False,
        custom_counter_handler=handler,
        supplier_prefix=SUPPLIER_PREFIX
    )
    factory = DataFactory(seed=42)
    entities = factory.populate_graph_set(graph_set, RESP_AGENT, entity_count)
    return graph_set, entities


def create_prov_set(graph_set, handler):
    """
    Create a ProvSet linked to a GraphSet.

    Args:
        graph_set: GraphSet instance to track provenance for
        handler: RedisCounterHandler instance

    Returns:
        ProvSet instance
    """
    return ProvSet(
        prov_subj_graph_set=graph_set,
        base_iri=BASE_IRI,
        wanted_label=False,
        custom_counter_handler=handler,
        supplier_prefix=SUPPLIER_PREFIX
    )


def pytest_configure(config):
    """Configure pytest-benchmark storage directory based on benchmark group."""
    benchmark_group = os.environ.get("BENCHMARK_GROUP")
    if benchmark_group:
        storage_dir = Path(".benchmarks") / benchmark_group
        storage_dir.mkdir(parents=True, exist_ok=True)
        config.option.benchmark_storage = str(storage_dir)
