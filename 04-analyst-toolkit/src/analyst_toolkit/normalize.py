"""Normalisation of raw XBRL facts into a stable financial schema.

The core problem this module solves
-----------------------------------
Filers do not tag the same economic concept consistently. Revenue may appear as
``Revenues``, ``RevenueFromContractWithCustomerExcludingAssessedTax``, or
``SalesRevenueNet`` depending on the filer and the year. Some concepts are not
reported directly at all and must be assembled from components (total debt is
usually the sum of several tranche-level tags).

Each field is therefore resolved through an ordered list of candidate tags. The
first tag that yields a value for the requested fiscal year wins, so the list
order encodes preference, not just possibility.
"""

from typing import Any, Dict, List, Optional

# Ordered candidate tags per field. First match wins.
FIELD_TAGS = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
        "SalesRevenueGoodsNet",
    ],
    "operating_income": [
        "OperatingIncomeLoss",
    ],
    "pretax_income": [
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
    ],
    "net_income": [
        "NetIncomeLoss",
        "ProfitLoss",
        "NetIncomeLossAvailableToCommonStockholdersBasic",
    ],
    "depreciation_amortization": [
        "DepreciationDepletionAndAmortization",
        "DepreciationAndAmortization",
        "DepreciationAmortizationAndAccretionNet",
        "Depreciation",
    ],
    "cash": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
        "CashAndDueFromBanks",
    ],
    "total_equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "goodwill": [
        "Goodwill",
    ],
    "intangibles": [
        "IntangibleAssetsNetExcludingGoodwill",
        "FiniteLivedIntangibleAssetsNet",
    ],
    "minority_interest": [
        "MinorityInterest",
    ],
    "preferred_equity": [
        "PreferredStockValue",
        "PreferredStockLiquidationPreferenceValue",
    ],
    "shares_diluted": [
        "WeightedAverageNumberOfDilutedSharesOutstanding",
        "WeightedAverageNumberOfSharesOutstandingBasic",
    ],
    "total_assets": [
        "Assets",
    ],
    # --- Bank-specific fields (used for the Citigroup peer set) ---
    "net_interest_income": [
        "InterestIncomeExpenseNet",
        "InterestIncomeExpenseAfterProvisionForLoanLoss",
    ],
    "provision_credit_losses": [
        "ProvisionForLoanLeaseAndOtherLosses",
        "ProvisionForCreditLosses",
    ],
    "deposits": [
        "Deposits",
    ],
    "loans": [
        "LoansAndLeasesReceivableNetReportedAmount",
        "NotesReceivableNet",
        "FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss",
    ],
}

# Fields assembled by summing several tags rather than picking one.
# Used where filers report components but no consolidated total.
COMPOSITE_FIELDS = {
    "total_debt": {
        "primary": ["DebtLongtermAndShorttermCombinedAmount"],
        "components": [
            "LongTermDebtNoncurrent",
            "LongTermDebtCurrent",
            "ShortTermBorrowings",
            "CommercialPaper",
        ],
        "fallback": ["LongTermDebt", "DebtCurrent"],
    },
}

# Fields that are calculated from other fields rather than tagged.
DERIVED_FIELDS = ("ebitda", "tangible_book_value")

ALL_FIELDS = (
    tuple(FIELD_TAGS.keys()) + tuple(COMPOSITE_FIELDS.keys()) + DERIVED_FIELDS
)


def _facts_root(companyfacts: Dict[str, Any]) -> Dict[str, Any]:
    """Return the us-gaap fact namespace from a companyfacts payload."""
    return companyfacts.get("facts", {}).get("us-gaap", {})


def extract_tag_value(
    companyfacts: Dict[str, Any],
    tag: str,
    fiscal_year: int,
    prefer_forms=("10-K", "20-F", "40-F"),
) -> Optional[float]:
    """Extract a single tag's value for a fiscal year.

    Prefers annual report forms and, among duplicates, the most recently filed
    observation — restatements mean the same (tag, fy) pair can appear several
    times with different values.
    """
    tag_data = _facts_root(companyfacts).get(tag)
    if not tag_data:
        return None

    candidates: List[Dict[str, Any]] = []
    for unit_key, observations in tag_data.get("units", {}).items():
        if not unit_key.startswith("USD") and unit_key != "shares":
            continue
        for obs in observations:
            if obs.get("fy") != fiscal_year:
                continue
            if obs.get("fp") != "FY":
                continue
            if prefer_forms and obs.get("form") not in prefer_forms:
                continue
            if obs.get("val") is None:
                continue
            candidates.append(obs)

    if not candidates:
        return None

    candidates.sort(key=lambda o: o.get("filed", ""), reverse=True)
    return float(candidates[0]["val"])


def resolve_field(
    companyfacts: Dict[str, Any], field: str, fiscal_year: int
) -> Optional[float]:
    """Resolve one schema field, walking the candidate tag list in order."""
    if field in FIELD_TAGS:
        for tag in FIELD_TAGS[field]:
            value = extract_tag_value(companyfacts, tag, fiscal_year)
            if value is not None:
                return value
        return None

    if field in COMPOSITE_FIELDS:
        spec = COMPOSITE_FIELDS[field]

        for tag in spec.get("primary", []):
            value = extract_tag_value(companyfacts, tag, fiscal_year)
            if value is not None:
                return value

        parts = [
            extract_tag_value(companyfacts, tag, fiscal_year)
            for tag in spec.get("components", [])
        ]
        present = [p for p in parts if p is not None]
        if present:
            return sum(present)

        for tag in spec.get("fallback", []):
            value = extract_tag_value(companyfacts, tag, fiscal_year)
            if value is not None:
                return value
        return None

    return None


def normalize_companyfacts(
    companyfacts: Dict[str, Any], ticker: str, fiscal_year: int
) -> Dict[str, Any]:
    """Normalise a raw companyfacts payload into the common schema.

    Returns a dict with every schema field present; unresolvable fields are
    ``None`` rather than absent, so downstream code can distinguish "missing"
    from "zero" without key checks.
    """
    record: Dict[str, Any] = {
        "ticker": ticker.upper(),
        "name": companyfacts.get("entityName"),
        "cik": companyfacts.get("cik"),
        "fiscal_year": fiscal_year,
    }

    for field in FIELD_TAGS:
        record[field] = resolve_field(companyfacts, field, fiscal_year)
    for field in COMPOSITE_FIELDS:
        record[field] = resolve_field(companyfacts, field, fiscal_year)

    record["ebitda"] = _derive_ebitda(record)
    record["tangible_book_value"] = _derive_tbv(record)
    record["missing_fields"] = sorted(
        f for f in ALL_FIELDS if record.get(f) is None
    )
    return record


def _derive_ebitda(record: Dict[str, Any]) -> Optional[float]:
    """EBITDA = operating income + D&A.

    Deliberately not computed from net income, which would require unwinding
    interest, tax and non-operating items that are inconsistently tagged.
    """
    ebit = record.get("operating_income")
    da = record.get("depreciation_amortization")
    if ebit is None:
        return None
    return ebit + (da or 0.0)


def _derive_tbv(record: Dict[str, Any]) -> Optional[float]:
    """Tangible book value = equity − goodwill − intangibles − preferred."""
    equity = record.get("total_equity")
    if equity is None:
        return None
    return (
        equity
        - (record.get("goodwill") or 0.0)
        - (record.get("intangibles") or 0.0)
        - (record.get("preferred_equity") or 0.0)
    )
