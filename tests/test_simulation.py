
"""Tests for the M/M/1 discrete-event simulator."""

import unittest

from src.simulation import simulate_mm1
from src.theory import calculate_mm1_metrics


class TestMM1Simulation(unittest.TestCase):

    def test_reproducibility(self):
        """Same seed must produce identical results."""
        a = simulate_mm1(5, 10, 10000, 1000, 42)
        b = simulate_mm1(5, 10, 10000, 1000, 42)

        self.assertEqual(a, b)

    def test_completed_packets(self):
        result = simulate_mm1(5, 10, 10000, 1000)

        self.assertEqual(result.completed_packets, 10000)
        self.assertGreater(result.observation_time, 0)

    def test_theoretical_agreement(self):
        """Simulation should approximate analytical values."""
        theory = calculate_mm1_metrics(5, 10)
        result = simulate_mm1(5, 10, 100000, 10000)

        for metric in ("L", "Lq", "W", "Wq"):
            expected = getattr(theory, metric)
            actual = getattr(result, metric)

            relative_error = abs(actual - expected) / expected

            self.assertLess(
                relative_error,
                0.05,
                f"{metric}: relative error exceeds 5%",
            )

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            simulate_mm1(10, 10)

        with self.assertRaises(ValueError):
            simulate_mm1(12, 10)

        with self.assertRaises(ValueError):
            simulate_mm1(-1, 10)

    def test_littles_law_approximation(self):
        """Check empirical Little's Law approximately."""
        lam = 5
        result = simulate_mm1(lam, 10, 100000, 10000)

        self.assertAlmostEqual(
            result.L,
            lam * result.W,
            delta=0.05,
        )

        self.assertAlmostEqual(
            result.Lq,
            lam * result.Wq,
            delta=0.05,
        )


if __name__ == "__main__":
    unittest.main()
