
"""Compare warm-up lengths for M/M/1 simulations."""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from src.simulation import simulate_mm1
from src.theory import calculate_mm1_metrics


OUTPUT_DIR = Path("results")
OUTPUT_DIR.mkdir(exist_ok=True)

SERVICE_RATE = 10.0
TRAFFIC_LOADS = [0.50, 0.90, 0.95]
WARMUP_VALUES = [0, 1000, 5000, 10000, 20000]

REPLICATIONS = 10
TARGET_DEPARTURES = 100_000


def main():
    rows = []

    for rho in TRAFFIC_LOADS:
        lam = rho * SERVICE_RATE
        theory = calculate_mm1_metrics(lam, SERVICE_RATE)

        for warmup in WARMUP_VALUES:
            measurements = []

            for run in range(REPLICATIONS):
                result = simulate_mm1(
                    arrival_rate=lam,
                    service_rate=SERVICE_RATE,
                    target_departures=TARGET_DEPARTURES,
                    warmup_departures=warmup,
                    seed=2026 + run,
                )

                measurements.append(result.W)

            mean_w = float(np.mean(measurements))
            relative_error = (
                abs(mean_w - theory.W) / theory.W * 100
            )

            rows.append({
                "rho": rho,
                "warmup_departures": warmup,
                "mean_W": mean_w,
                "theory_W": theory.W,
                "relative_error_pct": relative_error,
            })

            print(
                f"rho={rho:.2f} | warmup={warmup:>5} | "
                f"W={mean_w:.5f} | error={relative_error:.2f}%"
            )

    with open(
        OUTPUT_DIR / "warmup_analysis.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)

    plt.figure(figsize=(9, 5.5))

    for rho in TRAFFIC_LOADS:
        selected = [
            row for row in rows if row["rho"] == rho
        ]

        plt.plot(
            [row["warmup_departures"] for row in selected],
            [row["relative_error_pct"] for row in selected],
            marker="o",
            label=f"rho = {rho:.2f}",
        )

    plt.xlabel("Warm-up departures")
    plt.ylabel("Relative error in W (%)")
    plt.title("Effect of Warm-up Length on M/M/1 Estimates")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "warmup_analysis.png",
        dpi=300,
    )
    plt.close()

    print("\nWarm-up analysis completed.")
    print("Saved: results/warmup_analysis.csv")
    print("Saved: results/warmup_analysis.png")


if __name__ == "__main__":
    main()
