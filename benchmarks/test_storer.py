import os
import shutil
import tempfile

import pytest

from oc_ocdm.prov.prov_set import ProvSet
from oc_ocdm.storer import Storer

from benchmarks.conftest import BASE_IRI, BENCHMARK_ROUNDS, create_populated_graph_set


class TestStorer:

    @pytest.mark.benchmark(group="storer")
    @pytest.mark.parametrize("entity_count", [50, 100, 200])
    def test_store_all(self, benchmark, redis_counter_handler, entity_count):
        def setup():
            graph_set, _ = create_populated_graph_set(redis_counter_handler, entity_count)
            prov_set = ProvSet(prov_subj_graph_set=graph_set, base_iri=BASE_IRI, wanted_label=False)
            prov_set.generate_provenance()
            temp_dir = tempfile.mkdtemp()
            storer = Storer(graph_set, output_format="json-ld", zip_output=True, dir_split=10000, n_file_item=1000)
            prov_storer = Storer(prov_set, output_format="json-ld", zip_output=True, dir_split=10000, n_file_item=1000)
            return (storer, prov_storer, temp_dir), {}

        def store_operation(storer, prov_storer, temp_dir):
            base_dir = temp_dir + os.sep
            paths = storer.store_all(base_dir, BASE_IRI)
            prov_paths = prov_storer.store_all(base_dir, BASE_IRI)
            return paths + prov_paths

        result = benchmark.pedantic(store_operation, setup=setup, rounds=BENCHMARK_ROUNDS)
        assert len(result) > 0
        shutil.rmtree(os.path.dirname(os.path.dirname(result[0])), ignore_errors=True)
