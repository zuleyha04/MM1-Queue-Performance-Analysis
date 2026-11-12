
"""Discrete-event simulation of an M/M/1 FIFO queue."""

from collections import deque
from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class SimulationResult:
    rho: float
    L: float
    Lq: float
    W: float
    Wq: float
    completed_packets: int
    observation_time: float


def simulate_mm1(
    arrival_rate: float,
    service_rate: float,
    target_departures: int = 100_000,
    warmup_departures: int = 10_000,
    seed: int = 42,
) -> SimulationResult:
    """Run an event-driven M/M/1 queue simulation."""

    lam = float(arrival_rate)
    mu = float(service_rate)

    if not (
        math.isfinite(lam)
        and math.isfinite(mu)
        and 0 < lam < mu
    ):
        raise ValueError("Require 0 < lambda < mu.")

    if (
        not isinstance(target_departures, int)
        or not isinstance(warmup_departures, int)
        or target_departures <= 0
        or warmup_departures < 0
    ):
        raise ValueError("Invalid departure counts.")

    rng = np.random.default_rng(seed)

    clock = 0.0
    next_arrival = rng.exponential(1 / lam)
    next_departure = math.inf

    # Each queued packet stores its arrival time.
    queue = deque()

    server_busy = False
    current_arrival = None
    current_service_start = None

    completed = 0
    measured = 0

    area_system = 0.0
    area_queue = 0.0

    total_system_time = 0.0
    total_waiting_time = 0.0

    observation_start = 0.0 if warmup_departures == 0 else None
    previous_time = 0.0

    total_required = warmup_departures + target_departures

    while completed < total_required:

        event_time = min(next_arrival, next_departure)

        if observation_start is not None:
            duration = event_time - previous_time

            area_system += (
                len(queue) + int(server_busy)
            ) * duration

            area_queue += len(queue) * duration

        clock = event_time
        previous_time = clock

        if next_arrival <= next_departure:
            # Arrival event
            packet_arrival = clock

            next_arrival = (
                clock + rng.exponential(1 / lam)
            )

            if not server_busy:
                server_busy = True
                current_arrival = packet_arrival
                current_service_start = clock

                next_departure = (
                    clock + rng.exponential(1 / mu)
                )
            else:
                queue.append(packet_arrival)

        else:
            # Departure event
            completed += 1

            if completed > warmup_departures:
                measured += 1

                total_system_time += (
                    clock - current_arrival
                )

                total_waiting_time += (
                    current_service_start - current_arrival
                )

            if queue:
                current_arrival = queue.popleft()
                current_service_start = clock

                next_departure = (
                    clock + rng.exponential(1 / mu)
                )
            else:
                server_busy = False
                current_arrival = None
                current_service_start = None
                next_departure = math.inf

            if completed == warmup_departures:
                observation_start = clock

    observation_time = clock - observation_start

    return SimulationResult(
        rho=lam / mu,
        L=area_system / observation_time,
        Lq=area_queue / observation_time,
        W=total_system_time / measured,
        Wq=total_waiting_time / measured,
        completed_packets=measured,
        observation_time=observation_time,
    )


def simulate_convergence(
    arrival_rate: float,
    service_rate: float,
    total_departures: int = 100_000,
    record_every: int = 500,
    seed: int = 42,
):
    """Record cumulative mean system time during simulation."""

    if not (
        math.isfinite(arrival_rate)
        and math.isfinite(service_rate)
        and 0 < arrival_rate < service_rate
    ):
        raise ValueError("Require 0 < lambda < mu.")

    if total_departures <= 0 or record_every <= 0:
        raise ValueError("Counts must be positive.")

    rng = np.random.default_rng(seed)

    queue = deque()

    clock = 0.0
    next_arrival = rng.exponential(1 / arrival_rate)
    next_departure = math.inf

    server_busy = False
    current_arrival = None

    completed = 0
    cumulative_system_time = 0.0

    records = []

    while completed < total_departures:

        if next_arrival <= next_departure:
            clock = next_arrival

            next_arrival = (
                clock + rng.exponential(1 / arrival_rate)
            )

            if not server_busy:
                server_busy = True
                current_arrival = clock

                next_departure = (
                    clock + rng.exponential(1 / service_rate)
                )
            else:
                queue.append(clock)

        else:
            clock = next_departure

            completed += 1

            cumulative_system_time += (
                clock - current_arrival
            )

            if (
                completed % record_every == 0
                or completed == total_departures
            ):
                records.append((
                    completed,
                    cumulative_system_time / completed,
                ))

            if queue:
                current_arrival = queue.popleft()

                next_departure = (
                    clock + rng.exponential(1 / service_rate)
                )
            else:
                server_busy = False
                current_arrival = None
                next_departure = math.inf

    return records
