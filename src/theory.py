
"""
M/M/1 Queueing Model - Analytical Calculations.

This module implements the theoretical performance metrics
of a stable M/M/1 queueing system.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MM1Metrics:
    """Analytical performance metrics of an M/M/1 queue."""

    rho: float
    L: float
    Lq: float
    W: float
    Wq: float


def calculate_mm1_metrics(
    arrival_rate: float,
    service_rate: float,
) -> MM1Metrics:
    """
    Calculate theoretical M/M/1 performance metrics.

    Parameters
    ----------
    arrival_rate : float
        Packet arrival rate (lambda), packets/second.
    service_rate : float
        Packet service rate (mu), packets/second.

    Returns
    -------
    MM1Metrics
        Traffic intensity, mean system population,
        mean queue length, mean system time,
        and mean queue waiting time.

    Raises
    ------
    ValueError
        If the rates are invalid or the queue is unstable.
    """

    lam = float(arrival_rate)
    mu = float(service_rate)

    if not (0 <= lam < mu) or mu <= 0:
        raise ValueError(
            "Rates must satisfy 0 <= lambda < mu and mu > 0."
        )

    rho = lam / mu

    L = rho / (1 - rho)
    Lq = rho**2 / (1 - rho)

    W = 1 / (mu - lam)
    Wq = lam / (mu * (mu - lam))

    return MM1Metrics(
        rho=rho,
        L=L,
        Lq=Lq,
        W=W,
        Wq=Wq,
    )


def verify_littles_law(
    metrics: MM1Metrics,
    arrival_rate: float,
    tolerance: float = 1e-9,
) -> bool:
    """
    Verify Little's Law:
        L = lambda * W
        Lq = lambda * Wq
    """

    import math

    lam = float(arrival_rate)

    return (
        math.isclose(
            metrics.L, lam * metrics.W,
            rel_tol=tolerance,
            abs_tol=tolerance,
        )
        and math.isclose(
            metrics.Lq, lam * metrics.Wq,
            rel_tol=tolerance,
            abs_tol=tolerance,
        )
    )
