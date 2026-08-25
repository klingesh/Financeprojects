"""Tests for the manual CSV input path.

This path exists because Indian issuers (CDSL, HDFC AMC and peers) do not file
with the SEC. The critical property is that manual data lands in the *same*
schema as EDGAR data, so all downstream analysis is shared.
"""

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from analyst_toolkit import comps, csv_input  # noqa: E402
from analyst_toolkit.csv_input import CsvInputError  # noqa: E402
from analyst_toolkit.normalize import ALL_FIELDS  # noqa: E402

SAMPLE_DIR = os.path.join(ROOT, "data", "sample")
AMC_CSV = os.path.join(SAMPLE_DIR, "amc_peers_template.csv")
DEPOSITORY_CSV = os.path.join(SAMPLE_DIR, "depository_peers_template.csv")

HEADER = "ticker,name,fiscal_year,price,shares_outstanding,revenue,operating_income,net_income,total_equity,cash,total_debt,aum,demat_accounts"


def write_csv(tmpdir, body, header=HEADER, name="peers.csv"):
    path = os.path.join(tmpdir, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(header + "\n" + body)
    return path


class TestNumberParsing(unittest.TestCase):
    def test_plain_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(tmp, "AAA,Alpha,2025,100,1000,5000,,,,,,,\n")
            record = csv_input.load_financials_csv(path)[0]
        self.assertAlmostEqual(record["revenue"], 5000.0)

    def test_thousands_separators(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(tmp, '"AAA",Alpha,2025,100,1000,"1,234,567",,,,,,,\n')
            record = csv_input.load_financials_csv(path)[0]
        self.assertAlmostEqual(record["revenue"], 1234567.0)

    def test_currency_symbols_stripped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(tmp, "AAA,Alpha,2025,₹100,1000,$5000,,,,,,,\n")
            record = csv_input.load_financials_csv(path)[0]
        self.assertAlmostEqual(record["price"], 100.0)
        self.assertAlmostEqual(record["revenue"], 5000.0)

    def test_parenthesised_negative(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(tmp, "AAA,Alpha,2025,100,1000,5000,,(250),,,,,\n")
            record = csv_input.load_financials_csv(path)[0]
        self.assertAlmostEqual(record["net_income"], -250.0)

    def test_blank_stays_none_not_zero(self):
        # The single most important behaviour: a blank must never become 0,
        # because 0 would corrupt peer medians.
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(tmp, "AAA,Alpha,2025,100,1000,,,,,,,,\n")
            record = csv_input.load_financials_csv(path)[0]
        self.assertIsNone(record["revenue"])

    def test_na_variants_are_none(self):
        for token in ("n/a", "N/A", "NA", "-", "nil", "NIL"):
            with tempfile.TemporaryDirectory() as tmp:
                path = write_csv(
                    tmp, "AAA,Alpha,2025,100,1000,{0},,,,,,,\n".format(token)
                )
                record = csv_input.load_financials_csv(path)[0]
            self.assertIsNone(record["revenue"], "token {0!r}".format(token))

    def test_unparseable_raises_with_guidance(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(tmp, "AAA,Alpha,2025,100,1000,abc,,,,,,,\n")
            with self.assertRaises(CsvInputError) as ctx:
                csv_input.load_financials_csv(path)
        message = str(ctx.exception)
        self.assertIn("Row 2", message)
        self.assertIn("not 0", message)


class TestStructure(unittest.TestCase):
    def test_missing_file_raises(self):
        with self.assertRaises(CsvInputError):
            csv_input.load_financials_csv("/tmp/definitely-not-here.csv")

    def test_missing_ticker_column_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(tmp, "Alpha,100\n", header="name,revenue")
            with self.assertRaises(CsvInputError) as ctx:
                csv_input.load_financials_csv(path)
        self.assertIn("ticker", str(ctx.exception))

    def test_empty_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "empty.csv")
            open(path, "w").close()
            with self.assertRaises(CsvInputError):
                csv_input.load_financials_csv(path)

    def test_comment_and_blank_rows_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(
                tmp,
                "# a comment row,,,,,,,,,,,,\n"
                "AAA,Alpha,2025,100,1000,5000,,,,,,,\n"
                ",,,,,,,,,,,,\n",
            )
            records = csv_input.load_financials_csv(path)
        self.assertEqual(len(records), 1)

    def test_ticker_uppercased(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(tmp, "aaa,Alpha,2025,100,1000,5000,,,,,,,\n")
            record = csv_input.load_financials_csv(path)[0]
        self.assertEqual(record["ticker"], "AAA")

    def test_unknown_columns_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(
                tmp,
                "AAA,Alpha,5000,banana\n",
                header="ticker,name,revenue,some_unknown_column",
            )
            record = csv_input.load_financials_csv(path)[0]
        self.assertAlmostEqual(record["revenue"], 5000.0)

    def test_no_usable_rows_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(tmp, "# only a comment,,,,,,,,,,,,\n")
            with self.assertRaises(CsvInputError):
                csv_input.load_financials_csv(path)


class TestFiscalYearFiltering(unittest.TestCase):
    def test_filters_to_requested_year(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(
                tmp,
                "AAA,Alpha,2024,100,1000,4000,,,,,,,\n"
                "AAA,Alpha,2025,110,1000,5000,,,,,,,\n",
            )
            records = csv_input.load_financials_csv(path, fiscal_year=2025)
        self.assertEqual(len(records), 1)
        self.assertAlmostEqual(records[0]["revenue"], 5000.0)

    def test_no_filter_returns_all(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(
                tmp,
                "AAA,Alpha,2024,100,1000,4000,,,,,,,\n"
                "AAA,Alpha,2025,110,1000,5000,,,,,,,\n",
            )
            records = csv_input.load_financials_csv(path)
        self.assertEqual(len(records), 2)

    def test_year_absent_in_csv_inherits_argument(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(
                tmp, "AAA,Alpha,,100,1000,5000,,,,,,,\n"
            )
            records = csv_input.load_financials_csv(path, fiscal_year=2025)
        self.assertEqual(records[0]["fiscal_year"], 2025)

    def test_mismatched_year_yields_no_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(tmp, "AAA,Alpha,2020,100,1000,5000,,,,,,,\n")
            with self.assertRaises(CsvInputError):
                csv_input.load_financials_csv(path, fiscal_year=2025)


class TestSchemaCompatibility(unittest.TestCase):
    """Manual records must be interchangeable with EDGAR records."""

    def test_all_schema_fields_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(tmp, "AAA,Alpha,2025,100,1000,5000,,,,,,,\n")
            record = csv_input.load_financials_csv(path)[0]
        for field in ALL_FIELDS:
            self.assertIn(field, record)

    def test_derives_ebitda(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(
                tmp,
                "AAA,Alpha,2025,100,1000,5000,1200,,,,,,\n",
                header="ticker,name,fiscal_year,price,shares_outstanding,revenue,operating_income,depreciation_amortization,net_income,total_equity,cash,total_debt,aum",
            )
            record = csv_input.load_financials_csv(path)[0]
        self.assertAlmostEqual(record["ebitda"], 1200.0)

    def test_supplied_ebitda_wins_over_derived(self):
        # A hand-entered EBITDA may reflect scrubbed exceptional items, so it
        # must take precedence over the derived value.
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(
                tmp,
                "AAA,Alpha,2025,1000,300,9999\n",
                header="ticker,name,fiscal_year,operating_income,depreciation_amortization,ebitda",
            )
            record = csv_input.load_financials_csv(path)[0]
        self.assertAlmostEqual(record["ebitda"], 9999.0)

    def test_derives_tangible_book_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(
                tmp,
                "AAA,Alpha,2025,1000,200,50\n",
                header="ticker,name,fiscal_year,total_equity,goodwill,intangibles",
            )
            record = csv_input.load_financials_csv(path)[0]
        self.assertAlmostEqual(record["tangible_book_value"], 750.0)

    def test_source_tagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(tmp, "AAA,Alpha,2025,100,1000,5000,,,,,,,\n")
            record = csv_input.load_financials_csv(path)[0]
        self.assertEqual(record["source"], "csv")


class TestInlinePrices(unittest.TestCase):
    def test_extracts_inline_market_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(tmp, "AAA,Alpha,2025,250,4000,5000,,,,,,,\n")
            records = csv_input.load_financials_csv(path)
        prices = csv_input.prices_from_records(records)
        self.assertAlmostEqual(prices["AAA"]["price"], 250.0)
        self.assertAlmostEqual(prices["AAA"]["shares_outstanding"], 4000.0)

    def test_rows_without_market_data_omitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_csv(tmp, "AAA,Alpha,2025,,,5000,,,,,,,\n")
            records = csv_input.load_financials_csv(path)
        self.assertEqual(csv_input.prices_from_records(records), {})


class TestTemplateWriter(unittest.TestCase):
    def test_writes_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = csv_input.write_template(os.path.join(tmp, "t.csv"))
            with open(path, encoding="utf-8") as handle:
                header = handle.readline().strip()
        self.assertIn("ticker", header)
        self.assertIn("aum", header)

    def test_template_is_loadable_shape(self):
        # The written template must satisfy the loader's own requirements.
        with tempfile.TemporaryDirectory() as tmp:
            path = csv_input.write_template(os.path.join(tmp, "t.csv"))
            with open(path, "a", encoding="utf-8") as handle:
                handle.write("AAA,Alpha,2025" + "," * 15 + "\n")
            records = csv_input.load_financials_csv(path)
        self.assertEqual(records[0]["ticker"], "AAA")


class TestBundledTemplates(unittest.TestCase):
    def test_amc_template_loads(self):
        records = csv_input.load_financials_csv(AMC_CSV, fiscal_year=2025)
        self.assertGreaterEqual(len(records), 4)

    def test_depository_template_loads(self):
        records = csv_input.load_financials_csv(DEPOSITORY_CSV, fiscal_year=2025)
        self.assertGreaterEqual(len(records), 6)

    def test_amc_template_marked_placeholder(self):
        # Guard against the placeholder data being mistaken for real figures.
        records = csv_input.load_financials_csv(AMC_CSV, fiscal_year=2025)
        self.assertTrue(all("PLACEHOLDER" in r["name"] for r in records))

    def test_depository_template_marked_placeholder(self):
        records = csv_input.load_financials_csv(DEPOSITORY_CSV, fiscal_year=2025)
        self.assertTrue(all("PLACEHOLDER" in r["name"] for r in records))


class TestEndToEndFromCsv(unittest.TestCase):
    def test_amc_pipeline(self):
        records = csv_input.load_financials_csv(AMC_CSV, fiscal_year=2025)
        prices = csv_input.prices_from_records(records)
        result = comps.build_comps_from_records(records, 2025, prices)

        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["rows"]), len(records))
        for row in result["rows"]:
            self.assertIsNotNone(row["p_aum"], row["ticker"])
            self.assertIsNotNone(row["aum_yield_bps"], row["ticker"])

    def test_depository_pipeline_per_account_metrics(self):
        records = csv_input.load_financials_csv(DEPOSITORY_CSV, fiscal_year=2025)
        prices = csv_input.prices_from_records(records)
        result = comps.build_comps_from_records(records, 2025, prices)

        by_ticker = {r["ticker"]: r for r in result["rows"]}
        self.assertIsNotNone(by_ticker["CDSL"]["ev_per_account"])
        # Peers without an account base must yield None, not zero.
        self.assertIsNone(by_ticker["BSE"]["ev_per_account"])

    def test_net_cash_gives_ev_below_market_cap(self):
        # Characteristic of capital-light fee businesses.
        records = csv_input.load_financials_csv(DEPOSITORY_CSV, fiscal_year=2025)
        prices = csv_input.prices_from_records(records)
        result = comps.build_comps_from_records(records, 2025, prices)
        cdsl = next(r for r in result["rows"] if r["ticker"] == "CDSL")
        self.assertLess(cdsl["enterprise_value"], cdsl["market_cap"])
        self.assertLess(cdsl["net_debt"], 0)

    def test_amc_table_renders(self):
        records = csv_input.load_financials_csv(AMC_CSV, fiscal_year=2025)
        prices = csv_input.prices_from_records(records)
        result = comps.build_comps_from_records(records, 2025, prices)
        table = comps.to_table(result, comps.AMC_COLUMNS)
        self.assertIn("P/AUM", table[0])
        self.assertIn("Blended yield (bps)", table[0])

    def test_fiscal_year_inferred_when_not_passed(self):
        records = csv_input.load_financials_csv(AMC_CSV, fiscal_year=2025)
        result = comps.build_comps_from_records(records)
        self.assertEqual(result["fiscal_year"], 2025)

    def test_coverage_clean_under_fee_ignore_set(self):
        records = csv_input.load_financials_csv(DEPOSITORY_CSV, fiscal_year=2025)
        result = comps.build_comps_from_records(records, 2025)
        report = comps.coverage_report(
            result, ignore=comps.FEE_BUSINESS_IGNORE_FIELDS
        )
        self.assertEqual(report, [])


if __name__ == "__main__":
    unittest.main()
