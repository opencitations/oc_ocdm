"""
Plot generator for benchmark results.

Generates PNG visualizations from pytest-benchmark JSON output.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


class BenchmarkPlotGenerator:
    """
    Generates PNG visualizations from benchmark results.
    """

    COLORS = [
        "#2ecc71",
        "#3498db",
        "#e74c3c",
        "#9b59b6",
        "#f39c12",
        "#1abc9c",
        "#e67e22",
        "#34495e",
    ]

    def __init__(self, output_dir: str = "benchmarks/output/plots"):
        """
        Initialize the plot generator.

        Args:
            output_dir: Directory to save generated plots.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_benchmark_results(self, json_path: str) -> Dict[str, Any]:
        """
        Load benchmark results from pytest-benchmark JSON file.

        Args:
            json_path: Path to JSON file.

        Returns:
            Parsed benchmark data.
        """
        with open(json_path) as f:
            return json.load(f)

    def _extract_benchmarks_by_group(
        self, data: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group benchmarks by their group name.

        Args:
            data: Raw benchmark data.

        Returns:
            Dictionary mapping group names to benchmark lists.
        """
        groups = {}
        for benchmark in data["benchmarks"]:
            group = benchmark["group"]
            if group not in groups:
                groups[group] = []
            groups[group].append(benchmark)
        return groups

    def _get_benchmark_name(self, benchmark: Dict[str, Any]) -> str:
        """Extract a clean name from benchmark data."""
        name = benchmark["name"]
        if name.startswith("test_"):
            name = name[5:]
        return name

    def _get_param_value(self, benchmark: Dict[str, Any], param: str) -> Optional[Any]:
        """Extract parameter value from benchmark."""
        params = benchmark.get("params")
        if params is None:
            return None
        return params[param] if param in params else None

    def _get_group_parameters(self, benchmarks: List[Dict[str, Any]]) -> set:
        """Extract all parameter names used in a benchmark group."""
        params = set()
        for bm in benchmarks:
            bm_params = bm.get("params")
            if bm_params is not None:
                params.update(bm_params.keys())
        return params

    def plot_group_combined(
        self,
        data: Dict[str, Any],
        group: str,
        output_name: str,
    ):
        """
        Create a combined plot with comparison bar chart and scaling/throughput
        line charts for all parameters in a single PNG.

        Layout:
        - Row 1: Comparison bar chart (spans full width)
        - Row 2: For each parameter, scaling and throughput side by side

        Args:
            data: Benchmark data.
            group: Group name to plot.
            output_name: Output filename (without extension).
        """
        groups = self._extract_benchmarks_by_group(data)
        if group not in groups:
            print(f"Group '{group}' not found in benchmark data")
            return

        benchmarks = groups[group]
        group_params = list(self._get_group_parameters(benchmarks))

        # Determine layout: 1 row for comparison + 1 row for each parameter pair
        n_params = max(1, len(group_params))
        n_cols = n_params * 2  # scaling + throughput for each param

        # Create figure with GridSpec
        fig = plt.figure(figsize=(6 * n_params, 10))
        gs = fig.add_gridspec(2, n_cols, height_ratios=[1, 1])

        # Row 1: Comparison bar chart (spans all columns)
        ax_comparison = fig.add_subplot(gs[0, :])
        self._draw_comparison_subplot(ax_comparison, benchmarks, group)

        # Row 2: Scaling and throughput for each parameter
        if group_params:
            for i, param in enumerate(sorted(group_params)):
                ax_scaling = fig.add_subplot(gs[1, i * 2])
                ax_throughput = fig.add_subplot(gs[1, i * 2 + 1])
                self._draw_scaling_subplot(ax_scaling, benchmarks, param)
                self._draw_throughput_subplot(ax_throughput, benchmarks, param)

        plt.tight_layout()
        output_path = self.output_dir / f"{output_name}.png"
        plt.savefig(output_path, dpi=150)
        plt.close()
        print(f"Saved: {output_path}")

    def _draw_comparison_subplot(
        self, ax: plt.Axes, benchmarks: List[Dict[str, Any]], group: str
    ):
        """Draw comparison bar chart on given axes."""
        names = []
        means = []
        stddevs = []

        for bm in benchmarks:
            names.append(self._get_benchmark_name(bm))
            stats = bm["stats"]
            means.append(stats["mean"] * 1000)
            stddevs.append(stats["stddev"] * 1000)

        x = range(len(names))
        bars = ax.bar(x, means, yerr=stddevs, capsize=5, color=self.COLORS[0], alpha=0.8)

        ax.set_xlabel("Benchmark")
        ax.set_ylabel("Time (ms)")
        ax.set_title(f"{group} - Comparison")
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha="right")

        for bar, mean in zip(bars, means):
            height = bar.get_height()
            ax.annotate(
                f"{mean:.2f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    def _draw_scaling_subplot(
        self, ax: plt.Axes, benchmarks: List[Dict[str, Any]], param_name: str
    ):
        """Draw scaling line chart on given axes."""
        test_data = {}
        for bm in benchmarks:
            base_name = self._get_benchmark_name(bm)
            if "[" in base_name:
                base_name = base_name.split("[")[0]

            param_value = self._get_param_value(bm, param_name)
            if param_value is None:
                continue

            if base_name not in test_data:
                test_data[base_name] = {"x": [], "y": [], "err": []}

            stats = bm["stats"]
            test_data[base_name]["x"].append(param_value)
            test_data[base_name]["y"].append(stats["mean"] * 1000)
            test_data[base_name]["err"].append(stats["stddev"] * 1000)

        for i, (name, values) in enumerate(test_data.items()):
            sorted_data = sorted(zip(values["x"], values["y"], values["err"]))
            x = [d[0] for d in sorted_data]
            y = [d[1] for d in sorted_data]
            err = [d[2] for d in sorted_data]

            color = self.COLORS[i % len(self.COLORS)]
            ax.errorbar(x, y, yerr=err, marker="o", label=name, color=color, capsize=3)

        ax.set_xlabel(param_name.replace("_", " ").title())
        ax.set_ylabel("Time (ms)")
        ax.set_title(f"Scaling ({param_name})")
        ax.legend(loc="best", fontsize=7)
        ax.grid(True, alpha=0.3)

    def _draw_throughput_subplot(
        self, ax: plt.Axes, benchmarks: List[Dict[str, Any]], param_name: str
    ):
        """Draw throughput line chart on given axes."""
        test_data = {}
        for bm in benchmarks:
            base_name = self._get_benchmark_name(bm)
            if "[" in base_name:
                base_name = base_name.split("[")[0]

            param_value = self._get_param_value(bm, param_name)
            if param_value is None:
                continue

            if base_name not in test_data:
                test_data[base_name] = {"x": [], "y": []}

            stats = bm["stats"]
            mean_time = stats["mean"]
            throughput = param_value / mean_time

            test_data[base_name]["x"].append(param_value)
            test_data[base_name]["y"].append(throughput)

        for i, (name, values) in enumerate(test_data.items()):
            sorted_data = sorted(zip(values["x"], values["y"]))
            x = [d[0] for d in sorted_data]
            y = [d[1] for d in sorted_data]

            color = self.COLORS[i % len(self.COLORS)]
            ax.plot(x, y, marker="o", label=name, color=color)

        ax.set_xlabel(param_name.replace("_", " ").title())
        ax.set_ylabel("Throughput (entities/sec)")
        ax.set_title(f"Throughput ({param_name})")
        ax.legend(loc="best", fontsize=7)
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, _: format(int(x), ","))
        )

    def generate_all_plots(self, json_file: str):
        """
        Generate all standard plots from benchmark JSON file.

        Args:
            json_file: Path to benchmark JSON file.
        """
        json_path = Path(json_file)
        if not json_path.exists():
            print(f"File not found: {json_file}")
            return

        print(f"\nProcessing: {json_path.name}")
        data = self.load_benchmark_results(str(json_path))

        # Generate one combined plot per group
        groups = self._extract_benchmarks_by_group(data)

        for group_name in groups:
            safe_group_name = group_name.replace("/", "_").replace(" ", "_")
            self.plot_group_combined(data, group=group_name, output_name=safe_group_name)

    def generate_group_plot(self, json_file: str, group: str):
        """
        Generate plot for a specific benchmark group only.

        Args:
            json_file: Path to benchmark JSON file.
            group: Name of the benchmark group to plot.
        """
        json_path = Path(json_file)
        if not json_path.exists():
            print(f"File not found: {json_file}")
            return

        print(f"\nProcessing: {json_path.name} (group: {group})")
        data = self.load_benchmark_results(str(json_path))

        safe_group_name = group.replace("/", "_").replace(" ", "_")
        self.plot_group_combined(data, group=group, output_name=safe_group_name)


def main():
    """Generate plots from command line."""

    parser = argparse.ArgumentParser(description="Generate benchmark plots")
    parser.add_argument(
        "--input-file",
        default="benchmarks/output/json/benchmark.json",
        help="Path to benchmark JSON file",
    )
    parser.add_argument(
        "--output-dir",
        default="benchmarks/output/plots",
        help="Directory to save plots",
    )
    parser.add_argument(
        "--group",
        default=None,
        help="Generate plot for specific benchmark group only",
    )

    args = parser.parse_args()

    generator = BenchmarkPlotGenerator(output_dir=args.output_dir)
    if args.group:
        generator.generate_group_plot(args.input_file, args.group)
    else:
        generator.generate_all_plots(args.input_file)


if __name__ == "__main__":
    main()
