import statistics
from collections import defaultdict

import click

from gitkit.util.cli import croak
from gitkit.util.shell import get_output

common_lengths = [72, 79, 80, 88, 100, 120, 132]


def get_line_lengths(filepath: str) -> list[int]:
    line_lengths = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                line_lengths.append(len(line.rstrip("\n")))
    return line_lengths


def analyze_repository(pattern):
    result = get_output(["git", "ls-files", pattern])
    files = [file.strip() for file in result.splitlines() if file.strip()]
    if not files:
        return croak("Nothing to do with the given pattern.")

    all_line_lengths = []
    for file_path in files:
        all_line_lengths.extend(get_line_lengths(file_path))

    if not all_line_lengths:
        croak("No lines to analyze.")

    return all_line_lengths


def calculate_statistics(line_lengths: list[int]):
    """Calculate statistics about line lengths."""
    stats = {
        "count": len(line_lengths),
        "min": min(line_lengths),
        "max": max(line_lengths),
        "mean": statistics.mean(line_lengths),
        "median": statistics.median(line_lengths),
        "mode": statistics.mode(line_lengths) if line_lengths else None,
    }

    # Calculate percentile distribution for specific lengths
    percentiles = {}

    for length in common_lengths:
        lines_shorter = sum(1 for line_length in line_lengths if line_length <= length)
        percentage = (lines_shorter / len(line_lengths)) * 100
        percentiles[length] = percentage

    return stats, percentiles


def find_optimal_length(line_lengths, target_percentile: float = 95.0):
    """Find the length that encompasses target_percentile% of all lines."""
    if not line_lengths:
        return None

    line_lengths.sort()
    index = int((target_percentile / 100) * len(line_lengths))
    return line_lengths[min(index, len(line_lengths) - 1)]


def print_results(stats, percentiles, optimal_length, target_percentile):
    """Print the analysis results."""
    print(f"Total lines analyzed: {stats['count']}")
    print(f"Length range: {stats['min']} to {stats['max']} characters")
    print(f"Mean length: {stats['mean']:.2f} characters")
    print(f"Median length: {stats['median']} characters")
    if stats["mode"] is not None:
        print(f"Most common length: {stats['mode']} characters")

    for length, percentage in sorted(percentiles.items()):
        print(f"* {percentage:.1f}% of lines are ≤ {length} characters")

    print(
        f"\nOptimal wrap length (covers {target_percentile}% of lines): "
        f"{optimal_length} characters",
    )

    # Find closest common standard
    common_standards = [72, 79, 80, 88, 100, 120, 132]
    closest = min(common_standards, key=lambda x: abs(x - optimal_length))

    if closest < optimal_length:
        coverage = percentiles.get(closest, 0)
        print(f"Closest standard below: {closest} characters (covers {coverage:.1f}% of lines)")
    else:
        standard_above = closest
        standards_below = [s for s in common_standards if s < optimal_length]
        if standards_below:
            closest_below = max(standards_below)
            coverage = percentiles.get(closest_below, 0)
            print(
                f"Closest standard below: {closest_below} characters (covers {coverage:.1f}% of lines)",
            )

        coverage = percentiles.get(standard_above, 0)
        print(
            f"Closest standard above: {standard_above} characters (covers {coverage:.1f}% of lines)",
        )


def create_histogram(line_lengths: list[int], bins: int = 20, max_length: int = 200):
    """Create a simple ASCII histogram of line lengths."""
    filtered_lengths = [line_length for line_length in line_lengths if line_length <= max_length]
    histogram = defaultdict(int)

    for length in filtered_lengths:
        histogram[length] += 1

    # Calculate bin size
    min_length = min(filtered_lengths) if filtered_lengths else 0
    bin_size = max(1, (max_length - min_length) // bins)

    # Create binned histogram
    binned_histogram = defaultdict(int)
    for length, count in histogram.items():
        bin_index = (length - min_length) // bin_size
        bin_value = min_length + (bin_index * bin_size)
        binned_histogram[bin_value] += count

    # Find the maximum count for scaling
    max_count = max(binned_histogram.values()) if binned_histogram else 0
    scale_factor = 40  # Maximum width of the histogram bar

    print("\n=== Line Length Histogram ===")
    print(f"Each * represents approximately {max(1, max_count // scale_factor)} lines")
    print(f"Displaying lengths up to {max_length} characters (binned by {bin_size})")

    for bin_start in sorted(binned_histogram.keys()):
        bin_end = bin_start + bin_size - 1
        count = binned_histogram[bin_start]
        bar_length = int((count / max_count) * scale_factor) if max_count > 0 else 0
        bar = "*" * bar_length
        print(f"{bin_start:3d}-{bin_end:<3d} ({count:6d}) {bar}")


@click.command(help="Analyze line lengths in the repository.")
@click.argument("pattern", required=True)
@click.option(
    "--percentile",
    type=float,
    default=95,
    help="Target percentile for optimal line length",
)
@click.option(
    "--max-histogram",
    type=int,
    default=200,
    help="Maximum line length to include in histogram",
)
def line_lengths(pattern: str, percentile: float, max_histogram: int):
    lengths = analyze_repository(pattern)
    stats, percentiles = calculate_statistics(lengths)
    optimal_length = find_optimal_length(lengths, target_percentile=percentile)
    print_results(stats, percentiles, optimal_length, target_percentile=percentile)
    create_histogram(lengths, max_length=max_histogram)
