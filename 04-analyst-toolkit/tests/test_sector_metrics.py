"""Tests for sector-specific metrics and their display handling.

Two properties matter most here:
  * scaling is applied to absolute currency figures but never to ratios or
    per-unit figures;
  * each metric returns None when its operating base is absent, so it is
    harmless on templates that don't use it.
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from analyst_toolkit import comps, excel_export  # noqa: E402
from analyst_toolkit import multiples as m  # noqa: E402


class TestPriceToAum(unittest.TestCase):
    def test_basic(self):
        # 100 market cap on 2,000 AUM = 5%
        self.assertAlmostEqual(m.price_to_aum(100.0, 2000.0), 0.05)

    def test_zero_aum_is_none(self):
        self.assertIsNone(m.price_to_aum(100.0, 0.0))

    def test_negative_aum_is_none(self):
        self.assertIsNone(m.price_to_aum(100.0, -2000.0))

    def test_missing_inputs(self):
        self.assertIsNone(m.price_to_aum(None, 2000.0))
        self.assertIsNone(m.price_to_aum(100.0, None))


class TestRevenueYieldOnAum(unittest.TestCase):
    def test_basis_points_conversion(self):
        # 50 revenue on 100,000 AUM = 50 bps
        yield_fraction = m.revenue_yield_on_aum(50.0, 100_000.0)
        self.assertAlmostEqual(yield_fraction * 10_000, 5.0)

    def test_missing_aum(self):
        self.assertIsNone(m.revenue_yield_on_aum(50.0, None))


class TestPerUnitMetrics(unittest.TestCase):
    def test_ev_per_unit(self):
        self.assertAlmostEqual(m.ev_per_unit(1_000_000.0, 500.0), 2000.0)

    def test_revenue_per_unit(self):
        self.assertAlmostEqual(m.revenue_per_unit(50_000.0, 500.0), 100.0)

    def test_zero_units_is_none(self):
        self.assertIsNone(m.ev_per_unit(1_000_000.0, 0.0))

    def test_missing_units_is_none(self):
        # Peers without an account base must not silently produce a value.
        self.assertIsNone(m.ev_per_unit(1_000_000.0, None))


class TestBuildRowSectorMetrics(unittest.TestCase):
    def test_aum_metrics_populated(self):
        row = comps.build_row(
            {"revenue": 500.0, "aum": 100_000.0},
            {"price": 10.0, "shares_outstanding": 1000.0},
        )
        self.assertAlmostEqual(row["p_aum"], 10_000.0 / 100_000.0)
        self.assertAlmostEqual(row["aum_yield_bps"], 50.0)

    def test_account_metrics_populated(self):
        row = comps.build_row(
            {"revenue": 1000.0, "demat_accounts": 100.0, "cash": 0.0, "total_debt": 0.0},
            {"price": 10.0, "shares_outstanding": 1000.0},
        )
        self.assertAlmostEqual(row["ev_per_account"], 100.0)
        self.assertAlmostEqual(row["revenue_per_account"], 10.0)

    def test_capacity_units_fallback(self):
        # Generic capacity should drive the same per-unit metrics.
        row = comps.build_row(
            {"revenue": 1000.0, "capacity_units": 200.0},
            {"price": 10.0, "shares_outstanding": 1000.0},
        )
        self.assertAlmostEqual(row["revenue_per_account"], 5.0)

    def test_absent_base_yields_none(self):
        row = comps.build_row(
            {"revenue": 1000.0}, {"price": 10.0, "shares_outstanding": 1000.0}
        )
        self.assertIsNone(row["p_aum"])
        self.assertIsNone(row["aum_yield_bps"])
        self.assertIsNone(row["ev_per_account"])


class TestScalingBehaviour(unittest.TestCase):
    def setUp(self):
        self.result = {
            "fiscal_year": 2025,
            "rows": [
                comps.build_row(
                    {
                        "ticker": "AAA",
                        "name": "Alpha",
                        "revenue": 10_000_000_000.0,
                        "operating_income": 6_000_000_000.0,
                        "aum": 7_500_000_000_000.0,
                        "demat_accounts": 150_000_000.0,
                        "cash": 0.0,
                        "total_debt": 0.0,
                    },
                    {"price": 1500.0, "shares_outstanding": 209_000_000.0},
                )
            ],
            "stats": {},
            "errors": [],
        }

    def test_aum_scaled_to_millions(self):
        table = comps.to_table(self.result, comps.AMC_COLUMNS)
        col = table[0].index("AUM (m)")
        self.assertAlmostEqual(table[1][col], 7_500_000.0)

    def test_p_aum_not_scaled(self):
        unscaled = comps.to_table(self.result, comps.AMC_COLUMNS, scale=1.0)
        scaled = comps.to_table(self.result, comps.AMC_COLUMNS)
        col = unscaled[0].index("P/AUM")
        self.assertAlmostEqual(unscaled[1][col], scaled[1][col])

    def test_blended_yield_not_scaled(self):
        unscaled = comps.to_table(self.result, comps.AMC_COLUMNS, scale=1.0)
        scaled = comps.to_table(self.result, comps.AMC_COLUMNS)
        col = unscaled[0].index("Blended yield (bps)")
        self.assertAlmostEqual(unscaled[1][col], scaled[1][col])

    def test_per_account_not_scaled(self):
        # EV per account is a small absolute figure; scaling to millions would
        # render it meaningless.
        table = comps.to_table(self.result, comps.DEPOSITORY_COLUMNS)
        col = table[0].index("EV per account")
        self.assertGreater(table[1][col], 1.0)
        self.assertLess(table[1][col], 100_000.0)


class TestTemplates(unittest.TestCase):
    def test_all_templates_registered(self):
        for name in ("industrial", "bank", "amc", "depository"):
            self.assertIn(name, comps.COLUMN_TEMPLATES)

    def test_amc_template_has_no_tbv(self):
        # Tangible book is a bank metric; irrelevant for a fee franchise.
        header = [label for _, label in comps.AMC_COLUMNS]
        self.assertFalse(any("TBV" in h for h in header))

    def test_depository_template_has_per_account_metrics(self):
        header = [label for _, label in comps.DEPOSITORY_COLUMNS]
        self.assertIn("EV per account", header)

    def test_fee_ignore_covers_bank_only_fields(self):
        for field in comps.BANK_ONLY_FIELDS:
            self.assertIn(field, comps.FEE_BUSINESS_IGNORE_FIELDS)


class TestFormatting(unittest.TestCase):
    def test_p_aum_renders_as_percent(self):
        self.assertEqual(excel_export.format_value("P/AUM", 0.128), "12.8%")

    def test_blended_yield_renders_one_decimal(self):
        self.assertEqual(
            excel_export.format_value("Blended yield (bps)", 46.66), "46.7"
        )

    def test_per_account_renders_one_decimal(self):
        self.assertEqual(
            excel_export.format_value("EV per account", 2010.0), "2,010.0"
        )

    def test_none_renders_na(self):
        self.assertEqual(excel_export.format_value("P/AUM", None), "n/a")


class TestStatsIncludeSectorMetrics(unittest.TestCase):
    def test_sector_metrics_in_stat_fields(self):
        for field in ("p_aum", "aum_yield_bps", "ev_per_account", "revenue_per_account"):
            self.assertIn(field, comps.STAT_FIELDS)


if __name__ == "__main__":
    unittest.main()
