"""Comparable-company table construction.

Market data (share price, shares outstanding) is **not** available from EDGAR —
EDGAR carries filings, not quotes. Prices are therefore supplied through a
separate JSON file so that the market-data date is explicit and auditable
rather than implicitly "whenever the script ran".
"""

import json
import os
from typing import Any, Dict, List, Optional, Sequence

from . import multiples as m
from .normalize import normalize_companyfacts

# Column order for the standard industrial comps table.
INDUSTRIAL_COLUMNS = [
    ("ticker", "Ticker"),
    ("name", "Company"),
    ("price", "Price"),
    ("market_cap", "Market cap ($m)"),
    ("net_debt", "Net debt ($m)"),
    ("enterprise_value", "EV ($m)"),
    ("revenue", "Revenue ($m)"),
    ("ebitda", "EBITDA ($m)"),
    ("ebitda_margin", "EBITDA margin"),
    ("ev_revenue", "EV/Revenue"),
    ("ev_ebitda", "EV/EBITDA"),
    ("pe", "P/E"),
    ("net_debt_ebitda", "Net debt/EBITDA"),
]

# Column order for banks. Note the absence of every EV-based multiple —
# see docs/bank-valuation-primer.md for why they are meaningless here.
BANK_COLUMNS = [
    ("ticker", "Ticker"),
    ("name", "Company"),
    ("price", "Price"),
    ("market_cap", "Market cap ($m)"),
    ("net_income", "Net income ($m)"),
    ("total_equity", "Total equity ($m)"),
    ("tangible_book_value", "Tangible book ($m)"),
    ("pe", "P/E"),
    ("p_tbv", "P/TBV"),
    ("rote", "ROTE"),
]

# Fields denominated in currency. EDGAR reports these in full units, so they
# are divided by the display scale before rendering. Ratios and per-share
# figures are deliberately excluded.
ABSOLUTE_CURRENCY_FIELDS = frozenset(
    {
        "market_cap",
        "net_debt",
        "enterprise_value",
        "revenue",
        "ebitda",
        "operating_income",
        "pretax_income",
        "net_income",
        "depreciation_amortization",
        "cash",
        "total_debt",
        "total_equity",
        "tangible_book_value",
        "goodwill",
        "intangibles",
        "minority_interest",
        "preferred_equity",
        "total_assets",
        "net_interest_income",
        "provision_credit_losses",
        "deposits",
        "loans",
        "aum",
    }
)

# Deliberately NOT scaled: per-unit currency figures (EV per account is a small
# absolute number and scaling it to millions would render it meaningless), and
# all ratios.

DISPLAY_SCALE_MILLIONS = 1_000_000.0

# Fields that only apply to non-financial issuers. Banks do not report
# revenue, operating income or D&A in a comparable way, so their absence is
# expected rather than a data-quality failure.
INDUSTRIAL_ONLY_FIELDS = frozenset(
    {
        "revenue",
        "operating_income",
        "ebitda",
        "depreciation_amortization",
        "pretax_income",
    }
)

BANK_ONLY_FIELDS = frozenset(
    {"net_interest_income", "provision_credit_losses", "deposits", "loans"}
)

# Capital-light fee businesses have no interest spread, no deposits and no loan
# book, so those fields are legitimately absent rather than missing.
FEE_BUSINESS_IGNORE_FIELDS = BANK_ONLY_FIELDS | frozenset(
    {"pretax_income", "shares_diluted", "total_assets"}
)

STAT_ROWS = ("median", "mean", "min", "max")

# Fields for which peer statistics are computed. Absolute figures such as
# revenue are excluded — the median revenue of a peer set is not informative.
STAT_FIELDS = (
    "ebitda_margin",
    "ev_revenue",
    "ev_ebitda",
    "pe",
    "net_debt_ebitda",
    "p_tbv",
    "rote",
    "p_aum",
    "aum_yield_bps",
    "ev_per_account",
    "revenue_per_account",
)

# Column template for asset managers. P/AUM is the dominant multiple; blended
# yield sits beside it because P/AUM cannot be interpreted without knowing how
# much each unit of AUM actually earns.
AMC_COLUMNS = [
    ("ticker", "Ticker"),
    ("name", "Company"),
    ("price", "Price"),
    ("market_cap", "Market cap (m)"),
    ("aum", "AUM (m)"),
    ("p_aum", "P/AUM"),
    ("aum_yield_bps", "Blended yield (bps)"),
    ("revenue", "Revenue (m)"),
    ("ebitda", "EBITDA (m)"),
    ("ebitda_margin", "EBITDA margin"),
    ("pe", "P/E"),
    ("ev_ebitda", "EV/EBITDA"),
]

# Column template for depositories and other account-based fee businesses.
DEPOSITORY_COLUMNS = [
    ("ticker", "Ticker"),
    ("name", "Company"),
    ("price", "Price"),
    ("market_cap", "Market cap (m)"),
    ("net_debt", "Net debt (m)"),
    ("enterprise_value", "EV (m)"),
    ("revenue", "Revenue (m)"),
    ("ebitda", "EBITDA (m)"),
    ("ebitda_margin", "EBITDA margin"),
    ("ev_ebitda", "EV/EBITDA"),
    ("pe", "P/E"),
    ("ev_per_account", "EV per account"),
    ("revenue_per_account", "Revenue per account"),
]

COLUMN_TEMPLATES = {
    "industrial": INDUSTRIAL_COLUMNS,
    "bank": BANK_COLUMNS,
    "amc": AMC_COLUMNS,
    "depository": DEPOSITORY_COLUMNS,
}


def load_prices(path: str) -> Dict[str, Dict[str, Any]]:
    """Load market data keyed by ticker.

    Expected shape::

        {
          "as_of": "2026-08-25",
          "prices": {
            "C":   {"price": 70.00, "shares_outstanding": 1890000000},
            "JPM": {"price": 280.00, "shares_outstanding": 2780000000}
          }
        }
    """
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    prices = payload.get("prices", payload)
    return {ticker.upper(): data for ticker, data in prices.items()}


def prices_as_of(path: str) -> Optional[str]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get("as_of")


def build_row(
    financials: Dict[str, Any], market: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Compute one comps row from normalised financials plus market data."""
    price = (market or {}).get("price")
    shares_out = (market or {}).get("shares_outstanding")

    # Prefer actual shares outstanding; fall back to the weighted-average
    # diluted count from the filing when market data is incomplete.
    shares = shares_out if shares_out is not None else financials.get("shares_diluted")

    mkt_cap = m.market_cap(price, shares)
    nd = m.net_debt(financials.get("total_debt"), financials.get("cash"))
    ev = m.enterprise_value(
        mkt_cap,
        financials.get("total_debt"),
        financials.get("cash"),
        financials.get("minority_interest"),
        financials.get("preferred_equity"),
    )

    row = dict(financials)
    row.update(
        {
            "price": price,
            "shares_outstanding": shares,
            "market_cap": mkt_cap,
            "net_debt": nd,
            "enterprise_value": ev,
            "ebitda_margin": m.ebitda_margin(
                financials.get("ebitda"), financials.get("revenue")
            ),
            "ev_revenue": m.ev_revenue(ev, financials.get("revenue")),
            "ev_ebitda": m.ev_ebitda(ev, financials.get("ebitda")),
            "ev_ebit": m.ev_ebit(ev, financials.get("operating_income")),
            "pe": m.price_earnings(mkt_cap, financials.get("net_income")),
            "p_tbv": m.price_tangible_book(
                mkt_cap, financials.get("tangible_book_value")
            ),
            "rote": m.return_on_tangible_equity(
                financials.get("net_income"), financials.get("tangible_book_value")
            ),
            "net_debt_ebitda": m.net_debt_ebitda(nd, financials.get("ebitda")),
        }
    )

    # Sector-specific metrics. Each resolves to None unless the relevant
    # operating base was supplied, so they are harmless on templates that
    # don't use them.
    aum = financials.get("aum")
    accounts = financials.get("demat_accounts") or financials.get("capacity_units")

    row["p_aum"] = m.price_to_aum(mkt_cap, aum)
    aum_yield = m.revenue_yield_on_aum(financials.get("revenue"), aum)
    row["aum_yield_bps"] = aum_yield * 10_000 if aum_yield is not None else None
    row["ev_per_account"] = m.ev_per_unit(ev, accounts)
    row["revenue_per_account"] = m.revenue_per_unit(financials.get("revenue"), accounts)

    return row


def build_comps(
    client,
    tickers: Sequence[str],
    fiscal_year: int,
    prices: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Build a full comps table.

    Tickers that fail are recorded in ``errors`` rather than aborting the run —
    one bad ticker should not cost you the other nine.
    """
    prices = prices or {}
    rows: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []

    for ticker in tickers:
        ticker = ticker.strip().upper()
        if not ticker:
            continue
        try:
            payload = client.fetch_companyfacts(ticker)
            financials = normalize_companyfacts(payload, ticker, fiscal_year)
            rows.append(build_row(financials, prices.get(ticker)))
        except Exception as exc:  # noqa: BLE001 - collected and reported
            errors.append({"ticker": ticker, "error": str(exc)})

    stats = {
        field: m.summary_stats([row.get(field) for row in rows])
        for field in STAT_FIELDS
    }

    return {
        "fiscal_year": fiscal_year,
        "rows": rows,
        "stats": stats,
        "errors": errors,
    }


def build_comps_from_records(
    records: Sequence[Dict[str, Any]],
    fiscal_year: Optional[int] = None,
    prices: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Build a comps table from already-normalised records.

    Used by the manual CSV path for issuers not on EDGAR. Shares all downstream
    logic — EV bridge, multiples, statistics, export — with the EDGAR path, so
    there is exactly one implementation of the analysis.
    """
    prices = prices or {}
    rows: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []

    for record in records:
        ticker = record.get("ticker")
        if not ticker:
            continue
        try:
            rows.append(build_row(record, prices.get(ticker)))
        except Exception as exc:  # noqa: BLE001 - collected and reported
            errors.append({"ticker": ticker, "error": str(exc)})

    stats = {
        field: m.summary_stats([row.get(field) for row in rows])
        for field in STAT_FIELDS
    }

    if fiscal_year is None and rows:
        fiscal_year = rows[0].get("fiscal_year")

    return {
        "fiscal_year": fiscal_year,
        "rows": rows,
        "stats": stats,
        "errors": errors,
    }


def _scaled(key: str, value: Any, scale: float) -> Any:
    if value is None or scale in (0, 1):
        return value
    if key in ABSOLUTE_CURRENCY_FIELDS and isinstance(value, (int, float)):
        return value / scale
    return value


def to_table(
    comps: Dict[str, Any],
    columns: Optional[Sequence] = None,
    scale: float = DISPLAY_SCALE_MILLIONS,
) -> List[List[Any]]:
    """Flatten a comps result into a 2D table with header and statistic rows.

    Currency fields are divided by ``scale`` (default: millions) because EDGAR
    reports monetary values in full units, which are unreadable at bank scale.
    Ratios are never scaled.
    """
    columns = list(columns or INDUSTRIAL_COLUMNS)
    header = [label for _, label in columns]
    table: List[List[Any]] = [header]

    for row in comps["rows"]:
        table.append([_scaled(key, row.get(key), scale) for key, _ in columns])

    if comps["rows"]:
        table.append([None] * len(columns))
        for stat in STAT_ROWS:
            line = []
            for key, _ in columns:
                if key == "ticker":
                    line.append(stat.upper())
                elif key in comps["stats"]:
                    line.append(_scaled(key, comps["stats"][key][stat], scale))
                else:
                    line.append(None)
            table.append(line)

    return table


def coverage_report(
    comps: Dict[str, Any], ignore: Optional[frozenset] = None
) -> List[str]:
    """Report which fields failed to resolve, per ticker.

    This is the practical output you work from when extending the tag lists in
    normalize.py — it tells you exactly what is unresolved.

    ``ignore`` suppresses fields that are legitimately inapplicable to the
    issuer type, so genuine gaps aren't buried in expected noise.
    """
    ignore = ignore or frozenset()
    lines = []
    for row in comps["rows"]:
        missing = [f for f in (row.get("missing_fields") or []) if f not in ignore]
        if missing:
            lines.append(
                "{0}: {1} unresolved -> {2}".format(
                    row["ticker"], len(missing), ", ".join(missing)
                )
            )
    for error in comps["errors"]:
        lines.append("{0}: FAILED -> {1}".format(error["ticker"], error["error"]))
    return lines


def default_fixture_dir() -> str:
    """Path to the bundled offline fixtures."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(here, "..", "..", "data", "sample"))
