
"""Final validation of M/M/1 simulation results."""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from src.simulation import simulate_convergence
from src.theory import calculate_mm1_metrics


RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

TRAFFIC_LOADS = [0.50, 0.90, 0.95]
SEEDS = range(2026, 2036)


def validate_confidence_intervals():
    """Check theoretical values against reported 95% CIs."""

    with open(
        RESULTS_DIR / "experiment_summary.csv",
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(csv.DictReader(file))

    print("\nCONFIDENCE INTERVAL VALIDATION")
    print("-" * 60)

    for metric in ("W", "Lq"):
        covered = 0

        for row in rows:
            theoretical = float(row[f"{metric}_theory"])
            lower = float(row[f"{metric}_ci_lower"])
            upper = float(row[f"{metric}_ci_upper"])

            if lower <= theoretical <= upper:
                covered += 1

        print(
            f"{metric}: {covered}/{len(rows)} theoretical "
            "values inside 95% confidence intervals"
        )


def analyze_convergence():
    """Plot cumulative mean W for different traffic loads."""

    fig, axes = plt.subplots(
        3, 1,
        figsize=(10, 11),
        sharex=True,
    )

    for ax, rho in zip(axes, TRAFFIC_LOADS):
        lam = rho * 10
        mu = 10

        theoretical = calculate_mm1_metrics(lam, mu)

        trajectories = []

        for seed in SEEDS:
            records = simulate_convergence(
                arrival_rate=lam,
                service_rate=mu,
                total_departures=100_000,
                record_every=500,
                seed=seed,
            )

            trajectories.append([
                mean_w for _, mean_w in records
            ])

        x = np.array([
            departures for departures, _ in records
        ])

        values = np.asarray(trajectories)

        mean_curve = values.mean(axis=0)

        for curve in values:
            ax.plot(
                x,
                curve,
                alpha=0.12,
                linewidth=0.8,
            )

        ax.plot(
            x,
            mean_curve,
            linewidth=2,
            label="Mean of 10 replications",
        )

        ax.axhline(
            theoretical.W,
            linestyle="--",
            label=f"Theoretical W = {theoretical.W:.3f}",
        )

        ax.axvline(
            10_000,
            linestyle=":",
            label="Selected warm-up = 10,000",
        )

        ax.set_title(f"Traffic intensity rho = {rho:.2f}")
        ax.set_ylabel("Cumulative mean W (seconds)")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)

    axes[-1].set_xlabel("Completed packets")

    fig.suptitle(
        "M/M/1 Warm-up and Convergence Analysis",
        fontsize=14,
    )

    fig.tight_layout()

    output = RESULTS_DIR / "convergence_analysis.png"
    fig.savefig(output, dpi=300)
    plt.close(fig)

    print(f"\nSaved: {output}")


def main():
    validate_confidence_intervals()
    analyze_convergence()
    print("\nFinal validation completed.")


if __name__ == "__main__":
    main()
