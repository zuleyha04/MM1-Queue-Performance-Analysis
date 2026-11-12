
"""Warm-up sensitivity and paired confidence interval analysis."""

import csv
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.simulation import simulate_mm1
from src.theory import calculate_mm1_metrics

MU = 10.0
LOADS = [0.50, 0.90, 0.95]
WARMUPS = [0, 5000, 10000, 20000, 30000, 50000]
REPLICATIONS = 20
MEASURED_PACKETS = 100000

# Two-sided 95% Student-t critical value for df = 19
T_CRITICAL = 2.093024054408263

OUTPUT = Path("results")
OUTPUT.mkdir(exist_ok=True)


def mean_ci(values):
    values = np.asarray(values, dtype=float)
    mean = float(np.mean(values))
    half_width = float(
        T_CRITICAL * np.std(values, ddof=1) / np.sqrt(len(values))
    )
    return mean, mean - half_width, mean + half_width


def main():
    rows = []
    paired_rows = []

    fig, axes = plt.subplots(
        1, len(LOADS), figsize=(16, 5), sharey=False
    )

    for ax, rho in zip(axes, LOADS):
        lam = rho * MU
        theory = calculate_mm1_metrics(lam, MU).W
        results = {}

        print(f"\nTraffic intensity rho = {rho:.2f}")

        for warmup in WARMUPS:
            delays = []

            for i in range(REPLICATIONS):
                result = simulate_mm1(
                    arrival_rate=lam,
                    service_rate=MU,
                    target_departures=MEASURED_PACKETS,
                    warmup_departures=warmup,
                    seed=5000 + i,
                )
                delays.append(result.W)

            results[warmup] = np.asarray(delays)
            mean, lower, upper = mean_ci(delays)

            rows.append({
                "rho": rho,
                "warmup": warmup,
                "mean_W": mean,
                "ci_lower": lower,
                "ci_upper": upper,
                "theoretical_W": theory,
                "relative_error_pct": 100 * abs(mean - theory) / theory,
            })

            print(
                f"Warm-up {warmup:>6}: "
                f"W={mean:.5f}, 95% CI=[{lower:.5f}, {upper:.5f}]"
            )

        reference = results[50000]

        for warmup in WARMUPS[:-1]:
            differences = results[warmup] - reference
            mean, lower, upper = mean_ci(differences)

            paired_rows.append({
                "rho": rho,
                "warmup": warmup,
                "reference_warmup": 50000,
                "mean_difference_W": mean,
                "difference_ci_lower": lower,
                "difference_ci_upper": upper,
                "relative_difference_pct": 100 * mean / theory,
                "relative_ci_lower_pct": 100 * lower / theory,
                "relative_ci_upper_pct": 100 * upper / theory,
            })

            print(
                f"Paired difference {warmup:>6} vs 50000: "
                f"{mean:+.5f}, 95% CI=[{lower:+.5f}, {upper:+.5f}]"
            )

        subset = [r for r in rows if r["rho"] == rho]
        x = np.array([r["warmup"] for r in subset])
        y = np.array([r["mean_W"] for r in subset])
        lower_err = y - np.array([r["ci_lower"] for r in subset])
        upper_err = np.array([r["ci_upper"] for r in subset]) - y

        ax.errorbar(
            x, y, yerr=[lower_err, upper_err],
            fmt="o-", capsize=4, label="Simulation (95% CI)"
        )
        ax.axhline(
            theory, linestyle="--", color="black",
            label="Theoretical W"
        )
        ax.axvline(
            10000, linestyle=":", color="gray",
            label="Current warm-up"
        )
        ax.set_title(f"rho = {rho:.2f}")
        ax.set_xlabel("Warm-up (departures)")
        ax.set_ylabel("Mean delay W (seconds)")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)

    fig.suptitle("Warm-up Sensitivity Analysis")
    fig.tight_layout()
    fig.savefig(OUTPUT / "warmup_validation.png", dpi=300)
    plt.close(fig)

    for filename, data in [
        ("warmup_validation.csv", rows),
        ("warmup_paired_differences.csv", paired_rows),
    ]:
        with (OUTPUT / filename).open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file, fieldnames=list(data[0].keys())
            )
            writer.writeheader()
            writer.writerows(data)

    print("\nAnalysis completed.")
    print("Saved: results/warmup_validation.png")
    print("Saved: results/warmup_validation.csv")
    print("Saved: results/warmup_paired_differences.csv")


if __name__ == "__main__":
    main()
