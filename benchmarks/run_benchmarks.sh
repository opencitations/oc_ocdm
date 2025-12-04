#!/bin/bash
# Run all benchmarks or a specific benchmark group.
#
# Usage:
#   ./run_benchmarks.sh              # Run all benchmarks
#   ./run_benchmarks.sh --group NAME # Run specific benchmark group
#
# Available groups: graph_diff, context_caching

set -e

GROUP=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --group)
            GROUP="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -n "$GROUP" ]; then
    exec "$(dirname "$0")/run_single_benchmark.sh" "$GROUP"
fi

echo "Cleaning previous benchmark results..."
rm -rf .benchmarks/*
rm -rf benchmarks/output/plots/*

poetry run pytest benchmarks/ -v \
    --benchmark-autosave \
    --benchmark-save-data \
    --benchmark-columns=min,max,mean,stddev,rounds,iterations \
    --benchmark-sort=mean \
    --benchmark-warmup=on \
    --benchmark-warmup-iterations=1

BENCHMARK_FILE=$(find .benchmarks -type f -name "*.json" | head -1)

if [ -n "$BENCHMARK_FILE" ]; then
    echo "Generating plots from: $BENCHMARK_FILE"
    poetry run python -m benchmarks.reports.plot_generator \
        --input-file "$BENCHMARK_FILE" \
        --output-dir benchmarks/output/plots
else
    echo "No benchmark JSON file found in .benchmarks/"
fi