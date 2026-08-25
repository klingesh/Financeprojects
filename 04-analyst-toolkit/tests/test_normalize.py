"""Tests for XBRL normalisation — the messiest part of the toolkit."""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
)

from analyst_toolkit import normalize  # noqa: E402


def make_fact(tag, value, fy=2024, fp="FY", form="10-K", filed="2025-02-20",
              unit="USD"):
    return {
        tag: {
            "units": {
                unit: [
                    {"fy": fy, "fp": fp, "form": form, "filed": filed, "val": value}
                ]
            }
        }
    }


def make_payload(facts, name="TEST CO", cik=1234):
    return {"entityName": name, "cik": cik, "facts": {"us-gaap": facts}}


class TestTagExtraction(unittest.TestCase):
    def test_extracts_matching_year(self):
        payload = make_payload(make_fact("Revenues", 500.0))
        self.assertAlmostEqual(
            normalize.extract_tag_value(payload, "Revenues", 2024), 500.0
        )

    def test_wrong_year_returns_none(self):
        payload = make_payload(make_fact("Revenues", 500.0, fy=2023))
        self.assertIsNone(normalize.extract_tag_value(payload, "Revenues", 2024))

    def test_missing_tag_returns_none(self):
        payload = make_payload({})
        self.assertIsNone(normalize.extract_tag_value(payload, "Revenues", 2024))

    def test_quarterly_observations_excluded(self):
        # Only full-year observations should be picked up for annual comps.
        payload = make_payload(make_fact("Revenues", 120.0, fp="Q3"))
        self.assertIsNone(normalize.extract_tag_value(payload, "Revenues", 2024))

    def test_prefers_most_recently_filed_on_restatement(self):
        # A restated figure filed later must win over the original.
        payload = make_payload(
            {
                "Revenues": {
                    "units": {
                        "USD": [
                            {"fy": 2024, "fp": "FY", "form": "10-K",
                             "filed": "2025-02-20", "val": 500.0},
                            {"fy": 2024, "fp": "FY", "form": "10-K",
                             "filed": "2026-02-20", "val": 480.0},
                        ]
                    }
                }
            }
        )
        self.assertAlmostEqual(
            normalize.extract_tag_value(payload, "Revenues", 2024), 480.0
        )

    def test_shares_unit_accepted(self):
        payload = make_payload(
            make_fact(
                "WeightedAverageNumberOfDilutedSharesOutstanding",
                1000.0,
                unit="shares",
            )
        )
        self.assertAlmostEqual(
            normalize.extract_tag_value(
                payload, "WeightedAverageNumberOfDilutedSharesOutstanding", 2024
            ),
            1000.0,
        )


class TestFieldResolution(unittest.TestCase):
    def test_first_candidate_wins(self):
        facts = {}
        facts.update(make_fact("RevenueFromContractWithCustomerExcludingAssessedTax", 900.0))
        facts.update(make_fact("Revenues", 500.0))
        payload = make_payload(facts)
        # The ASC 606 tag has priority over the legacy Revenues tag.
        self.assertAlmostEqual(
            normalize.resolve_field(payload, "revenue", 2024), 900.0
        )

    def test_falls_through_to_later_candidate(self):
        payload = make_payload(make_fact("SalesRevenueNet", 300.0))
        self.assertAlmostEqual(
            normalize.resolve_field(payload, "revenue", 2024), 300.0
        )

    def test_unresolvable_field_is_none(self):
        payload = make_payload({})
        self.assertIsNone(normalize.resolve_field(payload, "revenue", 2024))


class TestCompositeFields(unittest.TestCase):
    def test_sums_components(self):
        facts = {}
        facts.update(make_fact("LongTermDebtNoncurrent", 800.0))
        facts.update(make_fact("LongTermDebtCurrent", 100.0))
        facts.update(make_fact("ShortTermBorrowings", 50.0))
        payload = make_payload(facts)
        self.assertAlmostEqual(
            normalize.resolve_field(payload, "total_debt", 2024), 950.0
        )

    def test_partial_components_still_sum(self):
        payload = make_payload(make_fact("LongTermDebtNoncurrent", 800.0))
        self.assertAlmostEqual(
            normalize.resolve_field(payload, "total_debt", 2024), 800.0
        )

    def test_primary_tag_preempts_components(self):
        facts = {}
        facts.update(make_fact("DebtLongtermAndShorttermCombinedAmount", 1000.0))
        facts.update(make_fact("LongTermDebtNoncurrent", 800.0))
        payload = make_payload(facts)
        self.assertAlmostEqual(
            normalize.resolve_field(payload, "total_debt", 2024), 1000.0
        )

    def test_fallback_when_no_components(self):
        payload = make_payload(make_fact("LongTermDebt", 700.0))
        self.assertAlmostEqual(
            normalize.resolve_field(payload, "total_debt", 2024), 700.0
        )


class TestDerivedFields(unittest.TestCase):
    def test_ebitda_from_operating_income_plus_da(self):
        facts = {}
        facts.update(make_fact("OperatingIncomeLoss", 200.0))
        facts.update(make_fact("DepreciationDepletionAndAmortization", 50.0))
        record = normalize.normalize_companyfacts(make_payload(facts), "TST", 2024)
        self.assertAlmostEqual(record["ebitda"], 250.0)

    def test_ebitda_none_without_operating_income(self):
        facts = make_fact("DepreciationDepletionAndAmortization", 50.0)
        record = normalize.normalize_companyfacts(make_payload(facts), "TST", 2024)
        self.assertIsNone(record["ebitda"])

    def test_ebitda_tolerates_missing_da(self):
        facts = make_fact("OperatingIncomeLoss", 200.0)
        record = normalize.normalize_companyfacts(make_payload(facts), "TST", 2024)
        self.assertAlmostEqual(record["ebitda"], 200.0)

    def test_tangible_book_value(self):
        facts = {}
        facts.update(make_fact("StockholdersEquity", 1000.0))
        facts.update(make_fact("Goodwill", 200.0))
        facts.update(make_fact("IntangibleAssetsNetExcludingGoodwill", 50.0))
        facts.update(make_fact("PreferredStockValue", 100.0))
        record = normalize.normalize_companyfacts(make_payload(facts), "TST", 2024)
        self.assertAlmostEqual(record["tangible_book_value"], 650.0)

    def test_tbv_none_without_equity(self):
        record = normalize.normalize_companyfacts(make_payload({}), "TST", 2024)
        self.assertIsNone(record["tangible_book_value"])


class TestSchemaContract(unittest.TestCase):
    def test_all_fields_present_even_when_unresolved(self):
        # Downstream code relies on keys existing with None values rather than
        # being absent.
        record = normalize.normalize_companyfacts(make_payload({}), "TST", 2024)
        for field in normalize.ALL_FIELDS:
            self.assertIn(field, record)

    def test_missing_fields_reported(self):
        record = normalize.normalize_companyfacts(make_payload({}), "TST", 2024)
        self.assertIn("revenue", record["missing_fields"])

    def test_ticker_uppercased(self):
        record = normalize.normalize_companyfacts(make_payload({}), "tst", 2024)
        self.assertEqual(record["ticker"], "TST")


if __name__ == "__main__":
    unittest.main()
