"""End-to-end tests for the comps pipeline, run against bundled fixtures."""

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from analyst_toolkit import comps, excel_export  # noqa: E402
from analyst_toolkit.edgar import EdgarError, OfflineClient  # noqa: E402

FIXTURE_DIR = os.path.join(ROOT, "data", "sample")
PRICES_PATH = os.path.join(FIXTURE_DIR, "prices_sample.json")


class TestOfflineClient(unittest.TestCase):
    def setUp(self):
        self.client = OfflineClient(FIXTURE_DIR)

    def test_fixtures_exist(self):
        self.assertTrue(
            self.client.available(),
            "No fixtures found. Run: python tools/make_fixtures.py",
        )

    def test_loads_known_ticker(self):
        payload = self.client.fetch_companyfacts("C")
        self.assertIn("facts", payload)
        self.assertIn("us-gaap", payload["facts"])

    def test_case_insensitive(self):
        self.assertIsNotNone(self.client.fetch_companyfacts("c"))

    def test_unknown_ticker_raises_with_guidance(self):
        with self.assertRaises(EdgarError) as ctx:
            self.client.fetch_companyfacts("NOSUCHTICKER")
        self.assertIn("No offline fixture", str(ctx.exception))


class TestBuildRow(unittest.TestCase):
    def test_uses_market_shares_over_filed_shares(self):
        financials = {"shares_diluted": 100.0, "total_equity": 1000.0}
        row = comps.build_row(
            financials, {"price": 10.0, "shares_outstanding": 200.0}
        )
        self.assertAlmostEqual(row["shares_outstanding"], 200.0)
        self.assertAlmostEqual(row["market_cap"], 2000.0)

    def test_falls_back_to_filed_diluted_shares(self):
        financials = {"shares_diluted": 100.0}
        row = comps.build_row(financials, {"price": 10.0})
        self.assertAlmostEqual(row["market_cap"], 1000.0)

    def test_no_market_data_yields_none_multiples(self):
        row = comps.build_row({"revenue": 500.0, "ebitda": 100.0}, None)
        self.assertIsNone(row["market_cap"])
        self.assertIsNone(row["ev_ebitda"])

    def test_ebitda_margin(self):
        row = comps.build_row({"revenue": 1000.0, "ebitda": 250.0}, None)
        self.assertAlmostEqual(row["ebitda_margin"], 0.25)


class TestBuildComps(unittest.TestCase):
    def setUp(self):
        self.client = OfflineClient(FIXTURE_DIR)
        self.prices = comps.load_prices(PRICES_PATH)

    def test_builds_all_rows(self):
        result = comps.build_comps(
            self.client, ["C", "JPM", "BAC"], 2024, self.prices
        )
        self.assertEqual(len(result["rows"]), 3)
        self.assertEqual(result["errors"], [])

    def test_bad_ticker_collected_not_raised(self):
        # One bad ticker must not cost the whole run.
        result = comps.build_comps(
            self.client, ["C", "NOPE", "JPM"], 2024, self.prices
        )
        self.assertEqual(len(result["rows"]), 2)
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["ticker"], "NOPE")

    def test_blank_tickers_ignored(self):
        result = comps.build_comps(self.client, ["C", "", "  "], 2024, self.prices)
        self.assertEqual(len(result["rows"]), 1)

    def test_citi_trades_below_tangible_book_in_fixtures(self):
        # The fixtures are built to reproduce the real Citi situation: the
        # lowest ROTE in the peer set and a P/TBV below 1.0x.
        result = comps.build_comps(self.client, ["C", "JPM"], 2024, self.prices)
        citi = next(r for r in result["rows"] if r["ticker"] == "C")
        jpm = next(r for r in result["rows"] if r["ticker"] == "JPM")
        self.assertLess(citi["p_tbv"], 1.0)
        self.assertLess(citi["rote"], jpm["rote"])

    def test_stats_computed(self):
        result = comps.build_comps(
            self.client, ["C", "JPM", "BAC", "WFC"], 2024, self.prices
        )
        self.assertIsNotNone(result["stats"]["p_tbv"]["median"])
        self.assertIsNotNone(result["stats"]["rote"]["median"])

    def test_unknown_fiscal_year_gives_empty_fields(self):
        result = comps.build_comps(self.client, ["C"], 1999, self.prices)
        self.assertEqual(len(result["rows"]), 1)
        self.assertIsNone(result["rows"][0]["total_equity"])


class TestTableRendering(unittest.TestCase):
    def setUp(self):
        self.client = OfflineClient(FIXTURE_DIR)
        self.prices = comps.load_prices(PRICES_PATH)
        self.result = comps.build_comps(
            self.client, ["C", "JPM", "BAC"], 2024, self.prices
        )

    def test_bank_table_has_header_and_stats(self):
        table = comps.to_table(self.result, comps.BANK_COLUMNS)
        # header + 3 peers + spacer + 4 stat rows
        self.assertEqual(len(table), 9)
        self.assertEqual(table[0][0], "Ticker")
        self.assertEqual(table[5][0], "MEDIAN")

    def test_bank_table_excludes_ev_multiples(self):
        # EV-based multiples are meaningless for banks and must not appear.
        header = comps.to_table(self.result, comps.BANK_COLUMNS)[0]
        joined = " ".join(header)
        self.assertNotIn("EV", joined)

    def test_currency_scaled_to_millions(self):
        table = comps.to_table(self.result, comps.BANK_COLUMNS, scale=1_000_000.0)
        header = table[0]
        col = header.index("Total equity ($m)")
        # Synthetic Citi equity is 209,000m; must not render as 2.09e11.
        self.assertLess(table[1][col], 1_000_000)

    def test_ratios_never_scaled(self):
        unscaled = comps.to_table(self.result, comps.BANK_COLUMNS, scale=1.0)
        scaled = comps.to_table(self.result, comps.BANK_COLUMNS, scale=1_000_000.0)
        col = unscaled[0].index("P/TBV")
        self.assertAlmostEqual(unscaled[1][col], scaled[1][col])

    def test_empty_result_gives_header_only(self):
        empty = {"fiscal_year": 2024, "rows": [], "stats": {}, "errors": []}
        self.assertEqual(len(comps.to_table(empty, comps.BANK_COLUMNS)), 1)

    def test_render_text_runs(self):
        table = comps.to_table(self.result, comps.BANK_COLUMNS)
        text = excel_export.render_text(table)
        self.assertIn("Ticker", text)
        self.assertIn("MEDIAN", text)


class TestCoverageReport(unittest.TestCase):
    def setUp(self):
        self.client = OfflineClient(FIXTURE_DIR)
        self.result = comps.build_comps(self.client, ["C"], 2024, {})

    def test_reports_unresolved_fields(self):
        lines = comps.coverage_report(self.result)
        self.assertTrue(any("unresolved" in line for line in lines))

    def test_ignore_suppresses_inapplicable_fields(self):
        # Banks legitimately lack revenue/EBITDA; suppressing them should
        # shorten the report.
        full = comps.coverage_report(self.result)
        filtered = comps.coverage_report(
            self.result, ignore=comps.INDUSTRIAL_ONLY_FIELDS
        )
        self.assertLessEqual(len(" ".join(filtered)), len(" ".join(full)))

    def test_failed_tickers_reported(self):
        result = comps.build_comps(self.client, ["NOPE"], 2024, {})
        lines = comps.coverage_report(result)
        self.assertTrue(any("FAILED" in line for line in lines))


class TestExport(unittest.TestCase):
    def setUp(self):
        self.client = OfflineClient(FIXTURE_DIR)
        self.prices = comps.load_prices(PRICES_PATH)
        result = comps.build_comps(self.client, ["C", "JPM"], 2024, self.prices)
        self.table = comps.to_table(result, comps.BANK_COLUMNS)

    def test_csv_formatted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "out.csv")
            excel_export.write_csv(self.table, path)
            with open(path, encoding="utf-8") as handle:
                content = handle.read()
        self.assertIn("Ticker", content)
        self.assertIn("x", content)  # multiples carry an x suffix

    def test_csv_raw_writes_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "raw.csv")
            excel_export.write_csv(self.table, path, raw=True)
            with open(path, encoding="utf-8") as handle:
                lines = handle.read().strip().split("\n")
        self.assertNotIn("x", lines[1].split(",")[-1])

    def test_write_infers_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "inferred.csv")
            self.assertTrue(os.path.isfile(excel_export.write(self.table, path)))

    def test_unsupported_format_raises(self):
        with self.assertRaises(ValueError):
            excel_export.write(self.table, "x.txt", fmt="pdf")


class TestFormatValue(unittest.TestCase):
    def test_none_renders_na(self):
        self.assertEqual(excel_export.format_value("P/E", None), "n/a")

    def test_percent(self):
        self.assertEqual(excel_export.format_value("ROTE", 0.152), "15.2%")

    def test_multiple(self):
        self.assertEqual(excel_export.format_value("EV/EBITDA", 12.34), "12.3x")

    def test_large_number_has_thousands_separators(self):
        self.assertEqual(excel_export.format_value("EV ($m)", 1234567.0), "1,234,567")

    def test_string_passthrough(self):
        self.assertEqual(excel_export.format_value("Ticker", "MEDIAN"), "MEDIAN")


class TestPrices(unittest.TestCase):
    def test_loads_and_uppercases(self):
        prices = comps.load_prices(PRICES_PATH)
        self.assertIn("C", prices)
        self.assertIn("price", prices["C"])

    def test_as_of_present(self):
        # The market-data date must be explicit for the comps to be auditable.
        self.assertIsNotNone(comps.prices_as_of(PRICES_PATH))


if __name__ == "__main__":
    unittest.main()
