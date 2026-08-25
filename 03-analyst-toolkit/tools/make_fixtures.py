"""Generate offline test fixtures in EDGAR companyfacts shape.

The values here are SYNTHETIC and illustrative. They are deliberately round
numbers so nobody mistakes them for real filed data. Their purpose is to
exercise the pipeline offline, not to be accurate.

Real figures come from live EDGAR calls:

    export SEC_USER_AGENT="Your Name you@example.com"
    python -m analyst_toolkit.cli comps --peers C,JPM,BAC,WFC,GS,MS --bank

Run this script to regenerate the fixtures:

    python tools/make_fixtures.py
"""

import json
import os

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample")
FY = 2024

# EDGAR XBRL reports monetary values in FULL UNITS (dollars), not millions.
# The tables below are written in millions for legibility and scaled up on
# write, so the fixtures match real EDGAR behaviour.
MILLION = 1_000_000

# Synthetic bank data, US$ millions except share counts.
# Fields: name, cik, net income, equity, goodwill, intangibles, preferred,
#         cash, total debt, net interest income, deposits, diluted shares (m)
BANKS = {
    "C": dict(
        name="CITIGROUP INC (SYNTHETIC)", cik=831001,
        net_income=12_700, equity=209_000, goodwill=19_700, intangibles=4_200,
        preferred=18_200, cash=25_000, debt=310_000,
        nii=53_000, deposits=1_310_000, loans=700000, provision=8500,
        shares=1_910,
    ),
    "JPM": dict(
        name="JPMORGAN CHASE & CO (SYNTHETIC)", cik=19617,
        net_income=54_000, equity=344_000, goodwill=53_000, intangibles=3_500,
        preferred=27_000, cash=27_000, debt=390_000,
        nii=92_000, deposits=2_400_000, loans=1320000, provision=9200,
        shares=2_870,
    ),
    "BAC": dict(
        name="BANK OF AMERICA CORP (SYNTHETIC)", cik=70858,
        net_income=27_100, equity=295_000, goodwill=69_000, intangibles=2_100,
        preferred=28_400, cash=33_000, debt=300_000,
        nii=56_000, deposits=1_960_000, loans=1100000, provision=5500,
        shares=7_900,
    ),
    "WFC": dict(
        name="WELLS FARGO & CO (SYNTHETIC)", cik=72971,
        net_income=19_700, equity=185_000, goodwill=25_200, intangibles=1_400,
        preferred=19_400, cash=32_000, debt=205_000,
        nii=47_700, deposits=1_370_000, loans=910000, provision=3300,
        shares=3_440,
    ),
    "GS": dict(
        name="GOLDMAN SACHS GROUP INC (SYNTHETIC)", cik=886982,
        net_income=14_100, equity=121_000, goodwill=6_000, intangibles=900,
        preferred=10_700, cash=182_000, debt=290_000,
        nii=7_600, deposits=433_000, loans=185000, provision=1500,
        shares=320,
    ),
    "MS": dict(
        name="MORGAN STANLEY (SYNTHETIC)", cik=895421,
        net_income=13_400, equity=104_000, goodwill=17_100, intangibles=3_600,
        preferred=8_800, cash=91_000, debt=270_000,
        nii=8_100, deposits=376_000, loans=240000, provision=700,
        shares=1_650,
    ),
}

# Synthetic market data.
PRICES = {
    "C": 70.00, "JPM": 280.00, "BAC": 47.00,
    "WFC": 78.00, "GS": 620.00, "MS": 135.00,
}


def usd_fact(tag, value, unit="USD"):
    return {
        "label": tag,
        "units": {
            unit: [
                {
                    "fy": FY,
                    "fp": "FY",
                    "form": "10-K",
                    "end": "{0}-12-31".format(FY),
                    "filed": "{0}-02-20".format(FY + 1),
                    "val": value,
                }
            ]
        },
    }


def build_companyfacts(ticker, data):
    facts = {
        "NetIncomeLoss": usd_fact("NetIncomeLoss", data["net_income"] * MILLION),
        "StockholdersEquity": usd_fact(
            "StockholdersEquity", data["equity"] * MILLION
        ),
        "Goodwill": usd_fact("Goodwill", data["goodwill"] * MILLION),
        "IntangibleAssetsNetExcludingGoodwill": usd_fact(
            "IntangibleAssetsNetExcludingGoodwill", data["intangibles"] * MILLION
        ),
        "PreferredStockValue": usd_fact(
            "PreferredStockValue", data["preferred"] * MILLION
        ),
        "CashAndDueFromBanks": usd_fact(
            "CashAndDueFromBanks", data["cash"] * MILLION
        ),
        "LongTermDebtNoncurrent": usd_fact(
            "LongTermDebtNoncurrent", data["debt"] * MILLION
        ),
        "InterestIncomeExpenseNet": usd_fact(
            "InterestIncomeExpenseNet", data["nii"] * MILLION
        ),
        "Deposits": usd_fact("Deposits", data["deposits"] * MILLION),
        "LoansAndLeasesReceivableNetReportedAmount": usd_fact(
            "LoansAndLeasesReceivableNetReportedAmount", data["loans"] * MILLION
        ),
        "ProvisionForCreditLosses": usd_fact(
            "ProvisionForCreditLosses", data["provision"] * MILLION
        ),
        "Assets": usd_fact(
            "Assets", (data["deposits"] + data["debt"] + 200_000) * MILLION
        ),
        "WeightedAverageNumberOfDilutedSharesOutstanding": usd_fact(
            "WeightedAverageNumberOfDilutedSharesOutstanding",
            data["shares"] * MILLION,
            unit="shares",
        ),
    }
    return {
        "cik": data["cik"],
        "entityName": data["name"],
        "facts": {"us-gaap": facts},
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    for ticker, data in BANKS.items():
        path = os.path.join(OUT_DIR, "companyfacts_{0}.json".format(ticker))
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(build_companyfacts(ticker, data), handle, indent=2)
        print("wrote", path)

    prices_payload = {
        "_note": "SYNTHETIC illustrative data for offline testing. Not real market data.",
        "as_of": "{0}-12-31".format(FY),
        "prices": {
            ticker: {
                "price": PRICES[ticker],
                "shares_outstanding": BANKS[ticker]["shares"] * 1_000_000,
            }
            for ticker in BANKS
        },
    }
    prices_path = os.path.join(OUT_DIR, "prices_sample.json")
    with open(prices_path, "w", encoding="utf-8") as handle:
        json.dump(prices_payload, handle, indent=2)
    print("wrote", prices_path)


if __name__ == "__main__":
    main()
