# Analyst Toolkit — Comps Automation from SEC EDGAR

A dependency-free Python package that pulls XBRL financial data from SEC EDGAR, normalises
inconsistent filer tagging into a common schema, computes valuation multiples, and exports a
comparable-companies table.

**Standard library only.** `openpyxl` is optional and needed solely for Excel export.
Tested on Python 3.9+.

---

## Quick start

Runs immediately against bundled fixtures, no network or credentials needed:

```bash
cd 03-analyst-toolkit
PYTHONPATH=src python3 -m analyst_toolkit.cli comps --offline --bank
PYTHONPATH=src python3 -m analyst_toolkit.cli regress --offline
python3 -m unittest discover -s tests
```

For live data, the SEC requires a real contact string in the User-Agent header:

```bash
export SEC_USER_AGENT="Your Name your.email@example.com"
PYTHONPATH=src python3 -m analyst_toolkit.cli comps \
    --peers C,JPM,BAC,WFC,GS,MS --bank \
    --cache-dir .cache --out comps.xlsx
```

Requests without a descriptive User-Agent are refused with HTTP 403.

---

## The actual problem this solves

XBRL is standardised in theory. In practice, filers tag the same economic concept differently:

- Revenue appears as `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, or
  `SalesRevenueNet` depending on the filer and the year — ASC 606 adoption changed this mid-history.
- **Total debt is usually not tagged at all.** It has to be assembled from tranche-level tags
  (`LongTermDebtNoncurrent` + `LongTermDebtCurrent` + `ShortTermBorrowings` + `CommercialPaper`).
- Restatements mean the same `(tag, fiscal year)` pair appears multiple times with different values.
- Banks don't report `Revenues` or `OperatingIncomeLoss` in any comparable way, so EBITDA is
  genuinely unresolvable for them — correctly so.

Each schema field is therefore resolved through an **ordered list of candidate tags** in
`normalize.py`, where list order encodes preference rather than mere possibility. Composite fields
sum components when no consolidated total is tagged. Duplicate observations resolve to the most
recently filed value, so restatements win over originals.

---

## Design decisions worth explaining

**Missing data returns `None`, never `0`.** This is the single most important choice in the codebase.
Coercing a missing or negative denominator to zero silently corrupts peer medians — and a comps table
that is quietly wrong is far more dangerous than one that visibly fails. `safe_div` refuses negative
denominators by default, so a loss-making peer yields `None` for P/E rather than a meaningless
negative multiple that would drag the median down.

**Market data is supplied separately.** EDGAR carries filings, not quotes. Prices and share counts
come from a JSON file with an explicit `as_of` date, which keeps the market-data date auditable
instead of implicitly "whenever the script happened to run".

**Currency is scaled at render time, not at parse time.** EDGAR reports monetary values in full
units. The raw values are preserved through the pipeline and divided by 1,000,000 only for display,
so no precision is lost and ratios are never accidentally scaled.

**One bad ticker doesn't fail the run.** Failures are collected into an `errors` list and surfaced in
the coverage report.

**Bank and industrial templates are separate.** The bank column set contains no EV-based multiple,
because enterprise value is meaningless for a bank — see
[`../docs/bank-valuation-primer.md`](../docs/bank-valuation-primer.md). A test asserts that no
EV column can appear in the bank template.

---

## Module map

| Module | Responsibility |
|---|---|
| `edgar.py` | HTTP client (`urllib`), ticker→CIK resolution, on-disk cache, `OfflineClient` for fixtures |
| `normalize.py` | Candidate tag lists, composite assembly, derived fields, schema contract |
| `multiples.py` | EV bridge, all multiples, peer statistics, OLS regression |
| `comps.py` | Row construction, table assembly, display scaling, coverage reporting |
| `excel_export.py` | CSV, fixed-width text, optional formatted `.xlsx` |
| `cli.py` | `comps` and `regress` subcommands |
| `tools/make_fixtures.py` | Regenerates the offline fixtures |

---

## Commands

### `comps` — build a comparables table

| Flag | Purpose |
|---|---|
| `--peers` | Comma-separated tickers |
| `--fiscal-year` | Fiscal year to pull (default 2024) |
| `--bank` | Use the bank template (P/TBV, ROTE; no EV multiples) |
| `--offline` | Run from bundled fixtures |
| `--cache-dir` | Cache EDGAR responses to avoid repeat requests |
| `--prices` | JSON file of prices and share counts |
| `--out` / `--format` | Output path and format (`csv` or `xlsx`) |
| `--raw` | Write unformatted numbers rather than display strings |

### `regress` — P/TBV vs. ROTE

Fits an OLS regression of price-to-tangible-book on return on tangible equity across a bank peer
set, then reports each bank's fitted value and residual. This is the empirical backbone of bank
relative valuation: it separates "cheap because returns are poor" from "cheap for no explained
reason".

---

## About the bundled fixtures

The fixtures in `data/sample/` are **synthetic**. Entity names are suffixed `(SYNTHETIC)` and the
values are round numbers, deliberately, so they cannot be mistaken for filed data. They exist to
exercise the pipeline offline.

They are calibrated to reproduce the *qualitative* Citigroup situation — lowest ROTE in the peer set
and P/TBV below 1.0x — because that makes the regression output pedagogically meaningful. A test
asserts this relationship holds.

Two caveats:

- The regression R² against fixture data is ~0.97 because the synthetic values sit almost exactly on
  a line by construction. **Real peer data gives a materially lower R².** Do not quote the fixture
  figure as a finding.
- Regenerate with `python3 tools/make_fixtures.py`.

---

## Tests

```bash
python3 -m unittest discover -s tests -v
```

91 tests, no network required. Coverage concentrates on the failure modes that matter:

- Zero, negative and missing denominators
- `None` excluded from medians rather than coerced to zero
- Restatement precedence (later filing wins)
- Quarterly observations excluded from annual comps
- Composite debt assembly, including partial components
- Currency scaling applied to absolute figures but never to ratios
- Bank template structurally cannot contain EV multiples
- Bad tickers collected rather than raised

---

## Known limitations

- **US filers only.** Indian companies (including UltraTech and its peers) do not file with the SEC,
  so `01-ultratech-cement/` comps are assembled manually from annual reports. This asymmetry is a
  real constraint on what can be automated, not an oversight.
- **ROTE uses period-end tangible book**, not an average of opening and closing. Single-period
  fixtures lack the prior year.
- **No calendarisation.** Peers with differing fiscal year ends are not adjusted to a common period
  (Week 26 Day 4 in the roadmap).
- **No segment-level data.** Company-level aggregates only.
- **Multiples are unadjusted.** No normalisation for exceptional items, which a real analyst would
  scrub by hand.
- The SEC rate limit is respected with a fixed delay rather than adaptive backoff.
