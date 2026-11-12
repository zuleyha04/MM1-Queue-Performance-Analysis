
"""Welch graphical warm-up analysis for the M/M/1 queue."""

import csv
import math
from collections import deque
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from src.theory import calculate_mm1_metrics


OUTPUT = Path("results")
OUTPUT.mkdir(exist_ok=True)

MU = 10.0
LOADS = [0.50, 0.90, 0.95]
REPLICATIONS = 20
TOTAL_DEPARTURES = 150_000
BLOCK_SIZE = 1000
SMOOTHING_WINDOW = 5


def simulate_blocks(lam, mu, seed):
    """Record successive non-overlapping block mean delays."""
    rng = np.random.default_rng(seed)
    queue = deque()

    clock = 0.0
    next_arrival = rng.exponential(1.0 / lam)
    next_departure = math.inf
    current_arrival = None

    completed = 0
    block_total = 0.0
    block_means = []

    while completed < TOTAL_DEPARTURES:
        if next_arrival <= next_departure:
            clock = next_arrival
            next_arrival = clock + rng.exponential(1.0 / lam)

            if current_arrival is None:
                current_arrival = clock
                next_departure = clock + rng.exponential(1.0 / mu)
            else:
                queue.append(clock)

        else:
            clock = next_departure
            completed += 1
            block_total += clock - current_arrival

            if completed % BLOCK_SIZE == 0:
                block_means.append(block_total / BLOCK_SIZE)
                block_total = 0.0

            if queue:
                current_arrival = queue.popleft()
                next_departure = clock + rng.exponential(1.0 / mu)
            else:
                current_arrival = None
                next_departure = math.inf

    return np.asarray(block_means)


def smooth(values, window):
    """Centered moving average, excluding incomplete edge windows."""
    kernel = np.ones(window) / window
    return np.convolve(values, kernel, mode="valid")


def main():
    fig, axes = plt.subplots(
        len(LOADS), 1, figsize=(11, 11), sharex=True
    )
    output_rows = []

    for ax, rho in zip(axes, LOADS):
        lam = rho * MU
        theory = calculate_mm1_metrics(lam, MU).W

        runs = np.asarray([
            simulate_blocks(lam, MU, seed=3000 + i)
            for i in range(REPLICATIONS)
        ])

        average_blocks = runs.mean(axis=0)
        smoothed = smooth(average_blocks, SMOOTHING_WINDOW)

        block_positions = (
            np.arange(1, len(average_blocks) + 1) * BLOCK_SIZE
        )
        half = SMOOTHING_WINDOW // 2
        smooth_positions = block_positions[
            half:len(block_positions) - half
        ]

        for position, raw, filtered in zip(
            smooth_positions,
            average_blocks[half:-half],
            smoothed,
        ):
            output_rows.append({
                "rho": rho,
                "departures": int(position),
                "raw_block_mean_W": float(raw),
                "welch_smoothed_W": float(filtered),
                "theoretical_W": theory,
            })

        ax.plot(
            block_positions,
            average_blocks,
            alpha=0.30,
            label="Average block W (20 runs)",
        )
        ax.plot(
            smooth_positions,
            smoothed,
            linewidth=2,
            label="Welch smoothed W",
        )
        ax.axhline(
            theory,
            linestyle="--",
            label=f"Theoretical W = {theory:.3f}",
        )
        ax.axvline(
            10_000,
            linestyle=":",
            label="Current warm-up = 10,000",
        )
        ax.set_title(f"Traffic intensity rho = {rho:.2f}")
        ax.set_ylabel("Mean W (seconds)")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)

        print(
            f"rho={rho:.2f} | theory W={theory:.4f} | "
            f"smoothed W at ~10,000="
            f"{smoothed[np.argmin(abs(smooth_positions - 10000))]:.4f}"
        )

    axes[-1].set_xlabel("Completed packets")
    fig.suptitle(
        "Welch Warm-up Analysis (20 Independent Replications)"
    )
    fig.tight_layout()

    figure_path = OUTPUT / "welch_warmup.png"
    fig.savefig(figure_path, dpi=300)
    plt.close(fig)

    csv_path = OUTPUT / "welch_warmup.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(output_rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"\nSaved: {figure_path}")
    print(f"Saved: {csv_path}")
    print("Welch analysis completed.")


if __name__ == "__main__":
    main()
