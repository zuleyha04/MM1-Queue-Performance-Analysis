# M/M/1 Queue Performance Analysis

Analytical modeling and discrete-event simulation of an M/M/1 queueing system using Python.

## Overview

This project analyzes the performance of a single-server M/M/1 queue representing packet processing in a network router. Analytical queueing results are compared with a custom event-driven simulation.

The study evaluates system delay, queue length, transient-state behavior, and statistical confidence intervals under different traffic loads.

## Features

- Analytical calculation of L, Lq, W, and Wq
- Verification of Little's Law
- Event-driven simulation with Arrival and Departure events
- FIFO queue management
- Exponential interarrival and service times
- 18 traffic intensity scenarios (ρ = 0.10–0.95)
- 10 independent simulation replications per scenario
- Warm-up analysis using Welch's method
- 95% confidence intervals
- Comparison of analytical and simulation results
- Unit tests

## Experimental Setup

| Parameter | Value |
|---|---|
| Service rate (μ) | 10 packets/second |
| Traffic intensity (ρ) | 0.10–0.95 |
| Step size | 0.05 |
| Independent replications | 10 |
| Warm-up period | 10,000 completed packets |
| Measurement period | 100,000 completed packets |
| Confidence level | 95% |

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the main program:

```bash
python main.py
```

Run the experiments:

```bash
python -m experiments.run_experiments
```

Generate comparison plots:

```bash
python -m experiments.plot_results
```

Run unit tests:

```bash
python -m unittest discover -s tests -v
```

## Results

The analytical values of average system delay (W) and average queue length (Lq) were within the calculated 95% confidence intervals for all 18 traffic intensity scenarios.

As traffic intensity approaches 1, system delay and queue length increase significantly.

## Technologies

Python, NumPy, Matplotlib

## Academic Context

Graduate coursework project for **Computer Network Performance Analysis (BM508)**, Düzce University, 2026–2027 Fall Semester.