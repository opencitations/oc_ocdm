#!/bin/bash
# Simple entry point for running benchmarks in Docker.
#
# Usage:
#   ./benchmarks/benchmark.sh                    # Run all benchmarks
#   ./benchmarks/benchmark.sh context_caching    # Run specific group
#   ./benchmarks/benchmark.sh graph_diff         # Run specific group

cd "$(dirname "$0")"

if [ -z "$1" ]; then
    docker-compose -f docker-compose.yml run --rm benchmark
else
    docker-compose -f docker-compose.yml run --rm benchmark \
        bash /app/benchmarks/run_single_benchmark.sh "$1"
fi
