"""Manual CSV input for issuers not available from SEC EDGAR.

Why this exists
---------------
EDGAR only carries SEC filers. Indian listed companies — CDSL, HDFC AMC and
their peers — do not file with the SEC, so their data has to be entered by hand
from annual reports.

Rather than building a second analysis path for them, this module loads manual
data into **the same schema** that ``normalize.normalize_companyfacts``
produces. Everything downstream — the EV bridge, multiples, peer statistics,
outlier flagging, export — is then shared. One engine, two data sources.

CSV format
----------
One row per company. A header row is required. Column names match schema field
names; unknown columns are ignored, and missing columns resolve to ``None``
rather than zero.

Blank cells mean "not available" and are preserved as ``None``, which matters:
a blank EBITDA must not become a zero that corrupts the peer median.

Values are entered in **whole currency units** (not millions), matching EDGAR
convention, so display scaling behaves identically for both sources.
"""

import csv
import os
from typing import Any, Dict, List, Optional

from .normalize import ALL_FIELDS, _derive_ebitda, _derive_tbv

# Identity columns.
TEXT_FIELDS = ("ticker", "name")

# Market data may be supplied inline, which is usually more convenient than a
# separate prices file when typing figures from annual reports.
MARKET_FIELDS = ("price", "shares_outstanding")

# Operating-base fields for sector-specific multiples. Not part of the EDGAR
# schema because XBRL does not tag them.
OPERATING_BASE_FIELDS = (
    "aum",              # assets under management (asset managers)
    "demat_accounts",   # beneficial owner accounts (depositories)
    "capacity_units",   # generic operating capacity
)

NUMERIC_FIELDS = tuple(ALL_FIELDS) + MARKET_FIELDS + OPERATING_BASE_FIELDS

# Columns a human is most likely to want when building a peer set by hand.
TEMPLATE_COLUMNS = (
    "ticker",
    "name",
    "fiscal_year",
    "price",
    "shares_outstanding",
    "revenue",
    "operating_income",
    "depreciation_amortization",
    "net_income",
    "total_equity",
    "goodwill",
    "intangibles",
    "preferred_equity",
    "minority_interest",
    "cash",
    "total_debt",
    "aum",
    "demat_accounts",
)


class CsvInputError(ValueError):
    """Raised when a manual CSV cannot be parsed."""


def _parse_number(raw: Optional[str], field: str, row_number: int) -> Optional[float]:
    """Parse a numeric cell, tolerating human formatting.

    Accepts thousands separators, currency symbols, percentage signs and
    parenthesised negatives, because the data is typed by hand from PDFs.
    """
    if raw is None:
        return None

    text = str(raw).strip()
    if text in ("", "-", "–", "—", "n/a", "N/A", "na", "NA", "nil", "NIL"):
        return None

    negative = text.startswith("(") and text.endswith(")")
    if negative:
        text = text[1:-1]

    for token in (",", "\u00a0", " ", "₹", "$", "%", "x", "X"):
        text = text.replace(token, "")

    if not text:
        return None

    try:
        value = float(text)
    except ValueError:
        raise CsvInputError(
            "Row {0}: could not parse {1!r} as a number for field {2!r}. "
            "Use blank for unavailable data, not 0.".format(row_number, raw, field)
        )

    return -value if negative else value


def load_financials_csv(path: str, fiscal_year: Optional[int] = None) -> List[Dict[str, Any]]:
    """Load manual financial records from CSV.

    Returns records in the same schema as ``normalize_companyfacts``, so they
    can be fed straight into the comps pipeline.

    ``fiscal_year`` filters rows when the CSV carries several years per company.
    """
    if not os.path.isfile(path):
        raise CsvInputError("CSV not found: {0}".format(path))

    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise CsvInputError("CSV {0} is empty — a header row is required.".format(path))

        headers = [h.strip() for h in reader.fieldnames if h]
        if "ticker" not in headers:
            raise CsvInputError(
                "CSV {0} must contain a 'ticker' column. Found: {1}".format(
                    path, ", ".join(headers)
                )
            )

        records: List[Dict[str, Any]] = []
        for row_number, raw_row in enumerate(reader, start=2):
            row = {
                (key.strip() if key else ""): value
                for key, value in raw_row.items()
                if key
            }

            ticker = (row.get("ticker") or "").strip()
            if not ticker or ticker.startswith("#"):
                continue  # blank row or comment

            record: Dict[str, Any] = {"ticker": ticker.upper()}
            record["name"] = (row.get("name") or "").strip() or None

            year = _parse_number(row.get("fiscal_year"), "fiscal_year", row_number)
            record["fiscal_year"] = int(year) if year is not None else fiscal_year

            if (
                fiscal_year is not None
                and record["fiscal_year"] is not None
                and record["fiscal_year"] != fiscal_year
            ):
                continue

            for field in NUMERIC_FIELDS:
                if field in ("ticker", "name", "fiscal_year"):
                    continue
                record[field] = _parse_number(row.get(field), field, row_number)

            # Derive the same computed fields the EDGAR path produces, but only
            # when not supplied directly — a hand-entered EBITDA wins, since the
            # analyst may have scrubbed exceptional items.
            if record.get("ebitda") is None:
                record["ebitda"] = _derive_ebitda(record)
            if record.get("tangible_book_value") is None:
                record["tangible_book_value"] = _derive_tbv(record)

            record["missing_fields"] = sorted(
                f for f in ALL_FIELDS if record.get(f) is None
            )
            record["source"] = "csv"
            records.append(record)

    if not records:
        raise CsvInputError(
            "No usable rows in {0}{1}.".format(
                path,
                " for fiscal year {0}".format(fiscal_year) if fiscal_year else "",
            )
        )
    return records


def prices_from_records(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Extract inline market data into the prices mapping shape.

    Lets a single CSV carry both financials and market data.
    """
    prices: Dict[str, Dict[str, Any]] = {}
    for record in records:
        price = record.get("price")
        shares = record.get("shares_outstanding")
        if price is None and shares is None:
            continue
        prices[record["ticker"]] = {
            "price": price,
            "shares_outstanding": shares,
        }
    return prices


def write_template(path: str) -> str:
    """Write an empty CSV template with the expected header row."""
    directory = os.path.dirname(os.path.abspath(path))
    if directory and not os.path.isdir(directory):
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(TEMPLATE_COLUMNS)
    return path
