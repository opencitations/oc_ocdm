#!/bin/bash
# Run a single benchmark group without clearing other results.
#
# Usage: ./run_single_benchmark.sh <benchmark_group>
# Example: ./run_single_benchmark.sh context_caching
#
# Results stored in .benchmarks/<group>/
# Plots stored in benchmarks/output/plots/<group>.png

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <benchmark_group>"
    echo "Available groups:"
    echo "  - graph_diff"
    echo "  - context_caching"
    echo "  - storer"
    exit 1
fi

GROUP="$1"
TEST_FILE=""

case "$GROUP" in
    graph_diff)
        TEST_FILE="benchmarks/test_graph_diff.py"
        ;;
    context_caching)
        TEST_FILE="benchmarks/test_context_caching.py"
        ;;
    storer)
        TEST_FILE="benchmarks/test_storer.py"
        ;;
    *)
        echo "Unknown benchmark group: $GROUP"
        echo "Available groups: graph_diff, context_caching, storer"
        exit 1
        ;;
esac

echo "Running benchmark group: $GROUP"
echo "Test file: $TEST_FILE"

mkdir -p ".benchmarks/$GROUP"
rm -rf ".benchmarks/$GROUP"/*
rm -f "benchmarks/output/plots/$GROUP.png"

export BENCHMARK_GROUP="$GROUP"

poetry run pytest "$TEST_FILE" -v \
    --benchmark-autosave \
    --benchmark-save-data \
    --benchmark-columns=min,max,mean,stddev,rounds,iterations \
    --benchmark-sort=mean \
    --benchmark-warmup=on \
    --benchmark-warmup-iterations=1

BENCHMARK_FILE=$(find ".benchmarks/$GROUP" -type f -name "*.json" | head -1)

if [ -n "$BENCHMARK_FILE" ]; then
    echo "Generating plots from: $BENCHMARK_FILE"
    poetry run python -m benchmarks.reports.plot_generator \
        --input-file "$BENCHMARK_FILE" \
        --output-dir benchmarks/output/plots \
        --group "$GROUP"
else
    echo "No benchmark JSON file found in .benchmarks/$GROUP/"
fi
