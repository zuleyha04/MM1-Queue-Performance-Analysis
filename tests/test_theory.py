
"""Unit tests for the analytical M/M/1 model."""

import math
import unittest

from src.theory import (
    calculate_mm1_metrics,
    verify_littles_law,
)


class TestMM1Theory(unittest.TestCase):

    def test_known_values(self):
        """Check analytical results for lambda=5, mu=10."""
        metrics = calculate_mm1_metrics(5, 10)

        self.assertAlmostEqual(metrics.rho, 0.5)
        self.assertAlmostEqual(metrics.L, 1.0)
        self.assertAlmostEqual(metrics.Lq, 0.5)
        self.assertAlmostEqual(metrics.W, 0.2)
        self.assertAlmostEqual(metrics.Wq, 0.1)

    def test_littles_law(self):
        """Verify both forms of Little's Law."""
        metrics = calculate_mm1_metrics(5, 10)

        self.assertTrue(
            verify_littles_law(metrics, 5)
        )

    def test_zero_arrivals(self):
        """Check the model when no packets arrive."""
        metrics = calculate_mm1_metrics(0, 10)

        self.assertEqual(metrics.rho, 0)
        self.assertEqual(metrics.L, 0)
        self.assertEqual(metrics.Lq, 0)
        self.assertEqual(metrics.Wq, 0)
        self.assertAlmostEqual(metrics.W, 0.1)

    def test_invalid_rates(self):
        """Reject invalid or unstable queue parameters."""
        invalid_cases = [
            (10, 10),
            (12, 10),
            (-1, 10),
            (5, 0),
        ]

        for lam, mu in invalid_cases:
            with self.subTest(lam=lam, mu=mu):
                with self.assertRaises(ValueError):
                    calculate_mm1_metrics(lam, mu)

    def test_multiple_traffic_loads(self):
        """Check Little's Law for several traffic loads."""
        mu = 10

        for rho in [0.1, 0.3, 0.5, 0.7, 0.9, 0.95]:
            lam = rho * mu
            metrics = calculate_mm1_metrics(lam, mu)

            self.assertTrue(
                math.isclose(metrics.rho, rho)
            )
            self.assertTrue(
                verify_littles_law(metrics, lam)
            )


if __name__ == "__main__":
    unittest.main()
