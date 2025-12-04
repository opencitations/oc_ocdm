import pytest
from rdflib import URIRef

from oc_ocdm.support.support import find_paths

from benchmarks.conftest import BASE_IRI, BENCHMARK_ROUNDS


class TestFindPaths:

    @pytest.mark.benchmark(group="find_paths")
    @pytest.mark.parametrize("uri_count", [100, 500, 1000])
    def test_find_paths(self, benchmark, uri_count):
        uris = [URIRef(f"{BASE_IRI}br/060{i}") for i in range(1, uri_count + 1)]
        prov_uris = [URIRef(f"{BASE_IRI}br/060{i}/prov/se/1") for i in range(1, uri_count + 1)]
        all_uris = uris + prov_uris

        def find_all_paths():
            results = []
            for uri in all_uris:
                results.append(find_paths(uri, "/tmp/", BASE_IRI, "_", 10000, 1000))
            return results

        result = benchmark.pedantic(find_all_paths, rounds=BENCHMARK_ROUNDS)
        assert len(result) == uri_count * 2
