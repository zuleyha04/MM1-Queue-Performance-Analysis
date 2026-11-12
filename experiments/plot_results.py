
"""Plot theoretical and simulated M/M/1 performance."""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from src.theory import calculate_mm1_metrics


RESULTS_DIR = Path("results")
SUMMARY_FILE = RESULTS_DIR / "experiment_summary.csv"


def load_results():
    with open(
        SUMMARY_FILE,
        newline="",
        encoding="utf-8",
    ) as file:
        return list(csv.DictReader(file))


def plot_metric(rows, metric, ylabel, filename):
    rho = np.array([
        float(row["rho"]) for row in rows
    ])

    simulated = np.array([
        float(row[f"{metric}_mean"]) for row in rows
    ])

    ci_lower = np.array([
        float(row[f"{metric}_ci_lower"]) for row in rows
    ])

    ci_upper = np.array([
        float(row[f"{metric}_ci_upper"]) for row in rows
    ])

    # Smooth analytical curve.
    rho_curve = np.linspace(0.10, 0.95, 400)

    theory_curve = np.array([
        getattr(
            calculate_mm1_metrics(r * 10, 10),
            metric,
        )
        for r in rho_curve
    ])

    yerr = np.vstack([
        simulated - ci_lower,
        ci_upper - simulated,
    ])

    plt.figure(figsize=(9, 5.5))

    plt.plot(
        rho_curve,
        theory_curve,
        label="Theoretical M/M/1",
        linewidth=2,
    )

    plt.errorbar(
        rho,
        simulated,
        yerr=yerr,
        fmt="o",
        markersize=4,
        capsize=3,
        label="Simulation mean (95% CI)",
    )

    plt.xlabel("Traffic intensity (rho)")
    plt.ylabel(ylabel)
    plt.title(f"M/M/1 Queue Performance: {metric}")

    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    output = RESULTS_DIR / filename

    plt.savefig(output, dpi=300)
    plt.close()

    print(f"Saved: {output}")


def main():
    rows = load_results()

    plot_metric(
        rows,
        metric="W",
        ylabel="Mean system time (seconds)",
        filename="W_comparison.png",
    )

    plot_metric(
        rows,
        metric="Lq",
        ylabel="Mean queue length (packets)",
        filename="Lq_comparison.png",
    )


if __name__ == "__main__":
    main()
