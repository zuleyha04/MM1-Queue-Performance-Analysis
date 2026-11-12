
"""Entry point for the M/M/1 queue project."""

from src.theory import calculate_mm1_metrics
from src.simulation import simulate_mm1


def main():
    arrival_rate = 5.0
    service_rate = 10.0

    theoretical = calculate_mm1_metrics(
        arrival_rate, service_rate
    )

    simulated = simulate_mm1(
        arrival_rate, service_rate
    )

    print("\nM/M/1 QUEUE PERFORMANCE COMPARISON")
    print("-" * 48)
    print(f"Lambda: {arrival_rate} packets/sec")
    print(f"Mu:     {service_rate} packets/sec")
    print(f"Rho:    {theoretical.rho:.2f}\n")

    print(f"{'Metric':<10}{'Theory':>14}{'Simulation':>14}")
    print("-" * 38)

    for name in ("L", "Lq", "W", "Wq"):
        print(
            f"{name:<10}"
            f"{getattr(theoretical, name):>14.5f}"
            f"{getattr(simulated, name):>14.5f}"
        )


if __name__ == "__main__":
    main()
