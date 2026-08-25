"""Tests for multiple calculations.

The emphasis is on edge cases, because that is where automated comps corrupt
silently: a loss-making peer, a net-cash balance sheet, a missing field. Any of
these can poison a peer median without raising an error.
"""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)

from analyst_toolkit import multiples as m  # noqa: E402


class TestSafeDiv(unittest.TestCase):
    def test_normal(self):
        self.assertAlmostEqual(m.safe_div(10.0, 2.0), 5.0)

    def test_zero_denominator_returns_none(self):
        self.assertIsNone(m.safe_div(10.0, 0.0))

    def test_negative_denominator_returns_none_by_default(self):
        # A negative EBITDA must not produce a negative EV/EBITDA that then
        # drags down the peer median.
        self.assertIsNone(m.safe_div(100.0, -20.0))

    def test_negative_denominator_allowed_when_requested(self):
        # Net debt / EBITDA legitimately goes negative for net-cash companies.
        self.assertAlmostEqual(
            m.safe_div(-50.0, 25.0, require_positive_denominator=False), -2.0
        )

    def test_none_inputs(self):
        self.assertIsNone(m.safe_div(None, 5.0))
        self.assertIsNone(m.safe_div(5.0, None))


class TestEnterpriseValue(unittest.TestCase):
    def test_standard_bridge(self):
        ev = m.enterprise_value(
            mkt_cap=1000.0, total_debt=300.0, cash=100.0,
            minority_interest=50.0, preferred_equity=25.0,
        )
        self.assertAlmostEqual(ev, 1275.0)

    def test_missing_components_treated_as_zero(self):
        self.assertAlmostEqual(
            m.enterprise_value(1000.0, None, None, None, None), 1000.0
        )

    def test_no_market_cap_gives_none(self):
        self.assertIsNone(m.enterprise_value(None, 300.0, 100.0))

    def test_net_cash_company(self):
        # More cash than debt should reduce EV below market cap.
        ev = m.enterprise_value(1000.0, 50.0, 400.0)
        self.assertAlmostEqual(ev, 650.0)


class TestMultiples(unittest.TestCase):
    def test_ev_ebitda(self):
        self.assertAlmostEqual(m.ev_ebitda(1200.0, 100.0), 12.0)

    def test_ev_ebitda_negative_ebitda(self):
        self.assertIsNone(m.ev_ebitda(1200.0, -100.0))

    def test_pe_lossmaker_is_none(self):
        self.assertIsNone(m.price_earnings(1000.0, -50.0))

    def test_p_tbv(self):
        self.assertAlmostEqual(m.price_tangible_book(200.0, 100.0), 2.0)

    def test_p_tbv_negative_book_is_none(self):
        # Negative tangible book (goodwill exceeding equity) is not a
        # meaningful denominator.
        self.assertIsNone(m.price_tangible_book(200.0, -100.0))

    def test_rote(self):
        self.assertAlmostEqual(m.return_on_tangible_equity(15.0, 100.0), 0.15)

    def test_net_debt_ebitda_allows_negative(self):
        self.assertAlmostEqual(m.net_debt_ebitda(-200.0, 100.0), -2.0)


class TestNetDebt(unittest.TestCase):
    def test_positive(self):
        self.assertAlmostEqual(m.net_debt(500.0, 200.0), 300.0)

    def test_net_cash(self):
        self.assertAlmostEqual(m.net_debt(100.0, 400.0), -300.0)

    def test_both_none(self):
        self.assertIsNone(m.net_debt(None, None))

    def test_one_none_treated_as_zero(self):
        self.assertAlmostEqual(m.net_debt(500.0, None), 500.0)


class TestPeerStatistics(unittest.TestCase):
    def test_median_odd(self):
        self.assertAlmostEqual(m.median([3.0, 1.0, 2.0]), 2.0)

    def test_median_even(self):
        self.assertAlmostEqual(m.median([1.0, 2.0, 3.0, 4.0]), 2.5)

    def test_median_ignores_none(self):
        # The critical behaviour: None must be excluded, not coerced to zero.
        self.assertAlmostEqual(m.median([1.0, None, 3.0]), 2.0)

    def test_median_all_none(self):
        self.assertIsNone(m.median([None, None]))

    def test_median_empty(self):
        self.assertIsNone(m.median([]))

    def test_mean_ignores_none(self):
        self.assertAlmostEqual(m.mean([2.0, None, 4.0]), 3.0)

    def test_summary_stats(self):
        stats = m.summary_stats([1.0, 2.0, 3.0, None])
        self.assertAlmostEqual(stats["median"], 2.0)
        self.assertAlmostEqual(stats["mean"], 2.0)
        self.assertAlmostEqual(stats["min"], 1.0)
        self.assertAlmostEqual(stats["max"], 3.0)


class TestOutlierFlagging(unittest.TestCase):
    def test_flags_extreme_high(self):
        flags = m.flag_outliers([10.0, 11.0, 10.5, 100.0])
        self.assertTrue(flags[3])
        self.assertFalse(flags[0])

    def test_flags_extreme_low(self):
        flags = m.flag_outliers([10.0, 11.0, 10.5, 0.5])
        self.assertTrue(flags[3])

    def test_none_never_flagged(self):
        flags = m.flag_outliers([10.0, None, 11.0])
        self.assertFalse(flags[1])

    def test_zero_median_returns_all_false(self):
        self.assertEqual(m.flag_outliers([0.0, 0.0]), [False, False])


class TestLinearRegression(unittest.TestCase):
    def test_perfect_fit(self):
        slope, intercept, r2 = m.linear_regression([1.0, 2.0, 3.0], [2.0, 4.0, 6.0])
        self.assertAlmostEqual(slope, 2.0)
        self.assertAlmostEqual(intercept, 0.0)
        self.assertAlmostEqual(r2, 1.0)

    def test_intercept(self):
        slope, intercept, _ = m.linear_regression([0.0, 1.0], [1.0, 3.0])
        self.assertAlmostEqual(slope, 2.0)
        self.assertAlmostEqual(intercept, 1.0)

    def test_ignores_incomplete_pairs(self):
        slope, _, _ = m.linear_regression([1.0, None, 3.0], [2.0, 99.0, 6.0])
        self.assertAlmostEqual(slope, 2.0)

    def test_insufficient_observations_raises(self):
        with self.assertRaises(ValueError):
            m.linear_regression([1.0], [2.0])

    def test_zero_variance_raises(self):
        with self.assertRaises(ValueError):
            m.linear_regression([5.0, 5.0], [1.0, 2.0])


if __name__ == "__main__":
    unittest.main()
