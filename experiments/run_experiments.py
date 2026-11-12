
"""Run replicated M/M/1 traffic-load experiments."""

import csv
from pathlib import Path

import numpy as np

from src.simulation import simulate_mm1
from src.theory import calculate_mm1_metrics


SERVICE_RATE = 10.0
REPLICATIONS = 10
TARGET_DEPARTURES = 100_000
WARMUP_DEPARTURES = 10_000

OUTPUT_DIR = Path("results")
OUTPUT_DIR.mkdir(exist_ok=True)

METRICS = ("L", "Lq", "W", "Wq")



from statistics import NormalDist

def confidence_interval(values):
    """Calculate a two-sided 95% Student-t confidence interval."""
    values = np.asarray(values, dtype=float)

    n = len(values)

    if n < 2:
        raise ValueError("At least two replications are required.")

    mean = float(np.mean(values))
    std_error = float(np.std(values, ddof=1) / np.sqrt(n))

    # Student-t critical value for 95% CI with 9 degrees
    # of freedom (10 independent replications).
    if n != 10:
        raise ValueError(
            "This implementation requires exactly 10 replications."
        )

    t_critical = 2.2621571627409915
    margin = t_critical * std_error

    return mean, mean - margin, mean + margin


def run_experiments():
    summary_rows = []
    replication_rows = []

    traffic_loads = np.arange(2, 20) / 20

    for rho in traffic_loads:
        arrival_rate = float(rho * SERVICE_RATE)

        theoretical = calculate_mm1_metrics(
            arrival_rate, SERVICE_RATE
        )

        results = []

        for run in range(REPLICATIONS):
            seed = 2026 + run

            result = simulate_mm1(
                arrival_rate=arrival_rate,
                service_rate=SERVICE_RATE,
                target_departures=TARGET_DEPARTURES,
                warmup_departures=WARMUP_DEPARTURES,
                seed=seed,
            )

            results.append(result)

            replication_rows.append({
                "rho": round(float(rho), 2),
                "replication": run + 1,
                "seed": seed,
                **{
                    metric: getattr(result, metric)
                    for metric in METRICS
                },
            })

        row = {
            "rho": round(float(rho), 2),
            "lambda": arrival_rate,
            "mu": SERVICE_RATE,
        }

        for metric in METRICS:
            values = [
                getattr(result, metric)
                for result in results
            ]

            mean, ci_lower, ci_upper = confidence_interval(
                values
            )

            expected = getattr(theoretical, metric)

            row[f"{metric}_theory"] = expected
            row[f"{metric}_mean"] = mean
            row[f"{metric}_ci_lower"] = ci_lower
            row[f"{metric}_ci_upper"] = ci_upper
            row[f"{metric}_relative_error_pct"] = (
                abs(mean - expected) / expected * 100
            )

        summary_rows.append(row)

        print(
            f"rho={rho:.2f} | "
            f"W={row['W_mean']:.5f} | "
            f"Lq={row['Lq_mean']:.5f}"
        )

    def save_csv(filename, rows):
        with open(
            OUTPUT_DIR / filename,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file, fieldnames=list(rows[0].keys())
            )
            writer.writeheader()
            writer.writerows(rows)

    save_csv("experiment_summary.csv", summary_rows)
    save_csv("replication_results.csv", replication_rows)

    print("\nExperiments completed successfully.")
    print(f"Scenarios: {len(traffic_loads)}")
    print(f"Replications: {REPLICATIONS}")
    print(f"Total runs: {len(replication_rows)}")


if __name__ == "__main__":
    run_experiments()
