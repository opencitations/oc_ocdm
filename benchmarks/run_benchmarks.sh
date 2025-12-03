#!/bin/bash
set -e

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