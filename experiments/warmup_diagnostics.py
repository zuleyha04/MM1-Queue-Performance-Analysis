
"""Block-average diagnostics for M/M/1 warm-up analysis."""

from collections import deque
from pathlib import Path
import math

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from src.theory import calculate_mm1_metrics


RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

SERVICE_RATE = 10.0
TRAFFIC_LOADS = [0.50, 0.90, 0.95]

REPLICATIONS = 10
TOTAL_DEPARTURES = 100_000
BLOCK_SIZE = 1000


def simulate_block_means(lam, mu, seed):
    rng = np.random.default_rng(seed)

    queue = deque()

    clock = 0.0
    next_arrival = rng.exponential(1 / lam)
    next_departure = math.inf

    server_busy = False
    current_arrival = None

    completed = 0
    block_sum = 0.0
    block_means = []

    while completed < TOTAL_DEPARTURES:

        if next_arrival <= next_departure:
            clock = next_arrival

            next_arrival = (
                clock + rng.exponential(1 / lam)
            )

            if not server_busy:
                server_busy = True
                current_arrival = clock

                next_departure = (
                    clock + rng.exponential(1 / mu)
                )
            else:
                queue.append(clock)

        else:
            clock = next_departure

            completed += 1
            block_sum += clock - current_arrival

            if completed % BLOCK_SIZE == 0:
                block_means.append(
                    block_sum / BLOCK_SIZE
                )
                block_sum = 0.0

            if queue:
                current_arrival = queue.popleft()

                next_departure = (
                    clock + rng.exponential(1 / mu)
                )
            else:
                server_busy = False
                current_arrival = None
                next_departure = math.inf

    return np.array(block_means)


def main():
    fig, axes = plt.subplots(
        3, 1,
        figsize=(11, 11),
        sharex=True,
    )

    for ax, rho in zip(axes, TRAFFIC_LOADS):
        lam = rho * SERVICE_RATE

        theory = calculate_mm1_metrics(
            lam, SERVICE_RATE
        )

        runs = np.array([
            simulate_block_means(
                lam, SERVICE_RATE, 2026 + seed
            )
            for seed in range(REPLICATIONS)
        ])

        mean_blocks = runs.mean(axis=0)

        x = np.arange(
            1, len(mean_blocks) + 1
        ) * BLOCK_SIZE

        ax.plot(
            x,
            mean_blocks,
            linewidth=1.5,
            label="Mean block delay (10 runs)",
        )

        ax.axhline(
            theory.W,
            linestyle="--",
            label=f"Theoretical W = {theory.W:.3f}",
        )

        ax.axvline(
            10_000,
            linestyle=":",
            label="Selected warm-up",
        )

        ax.set_title(f"Traffic intensity rho = {rho:.2f}")
        ax.set_ylabel("Block mean W (seconds)")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)

    axes[-1].set_xlabel("Completed packets")

    fig.suptitle(
        "M/M/1 Warm-up Diagnostics: Block Means"
    )

    fig.tight_layout()

    output = RESULTS_DIR / "warmup_block_means.png"
    fig.savefig(output, dpi=300)
    plt.close(fig)

    print(f"Saved: {output}")
    print("Warm-up diagnostics completed.")


if __name__ == "__main__":
    main()
