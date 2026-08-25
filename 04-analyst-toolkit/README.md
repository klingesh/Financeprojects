# Analyst Toolkit — Comps Automation

A dependency-free Python package that builds comparable-company tables. It pulls XBRL data from SEC
EDGAR for US filers, accepts manual CSV input for everyone else, normalises both into a single
schema, computes valuation multiples and exports a formatted table.

**Standard library only.** `openpyxl` is optional and needed solely for Excel export.
Tested on Python 3.9+.

---

## Quick start

Runs immediately against bundled fixtures — no network, no credentials:

```bash
cd 04-analyst-toolkit

# US banks from EDGAR-shaped fixtures
PYTHONPATH=src python3 -m analyst_toolkit.cli comps --offline --bank
PYTHONPATH=src python3 -m analyst_toolkit.cli regress --offline

# Indian peer sets from manual CSV
PYTHONPATH=src python3 -m analyst_toolkit.cli comps \
    --input-csv data/sample/amc_peers_template.csv --template amc --fiscal-year 2025
PYTHONPATH=src python3 -m analyst_toolkit.cli comps \
    --input-csv data/sample/depository_peers_template.csv --template depository --fiscal-year 2025

python3 -m unittest discover -s tests
```

For live EDGAR data, the SEC requires a real contact string in the User-Agent header:

```bash
export SEC_USER_AGENT="Your Name your.email@example.com"
PYTHONPATH=src python3 -m analyst_toolkit.cli comps \
    --peers C,JPM,BAC,WFC,GS,MS --bank --cache-dir .cache --out comps.xlsx
```

Requests without a descriptive User-Agent are refused with HTTP 403.

---

## Two data sources, one analysis engine

EDGAR only carries SEC filers. **Indian listed companies — CDSL, HDFC AMC and their peers — do not
file with the SEC**, so their figures have to be entered by hand from annual reports.

Rather than maintaining a second analysis path for them, manual CSV data is loaded into *the same
schema* that the EDGAR normaliser produces. Everything downstream — the enterprise value bridge,
multiples, peer statistics, outlier flagging, export — is shared. There is exactly one
implementation of the analysis.

```
SEC EDGAR (XBRL)  ─┐
                   ├─→  common schema  ─→  multiples  ─→  statistics  ─→  export
Manual CSV        ─┘
```

### CSV format

One row per company, header row required. Column names match schema field names; unknown columns are
ignored and missing columns resolve to `None`. Generate a blank template with
`csv_input.write_template()`, or start from the bundled examples.

The parser tolerates how figures actually appear when typed from a PDF: thousands separators,
currency symbols, and parenthesised negatives. Values go in **whole currency units** (not millions),
matching EDGAR convention, so display scaling behaves identically for both sources.

**A blank cell means "not available" and is preserved as `None`.** Never enter `0` for missing data —
see below for why this matters more than it sounds.

---

## Design decisions worth explaining

**Missing data returns `None`, never `0`.** The single most important choice in the codebase.
Coercing a missing or negative denominator to zero silently corrupts peer medians, and a comps table
that is quietly wrong is far more dangerous than one that visibly fails. `safe_div` refuses negative
denominators by default, so a loss-making peer yields `None` for P/E rather than a meaningless
negative multiple dragging the median down.

**Ordered candidate tag lists.** XBRL is standardised in theory. In practice filers tag the same
concept differently — revenue appears as `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`
or `SalesRevenueNet` depending on the filer and the year, because ASC 606 adoption changed this
mid-history. **Total debt is usually not tagged at all** and must be assembled from tranche-level
tags. Duplicate observations resolve to the most recently filed value, so restatements win over
originals.

**Column templates encode sector knowledge.** Four templates: `industrial`, `bank`, `amc`,
`depository`. The bank template contains no EV-based multiple, because enterprise value is
meaningless for a bank — a test asserts this structurally rather than trusting convention. The AMC
template pairs P/AUM with blended yield, because P/AUM cannot be interpreted without knowing how
much each unit of AUM earns.

**Currency scaled at render time only.** EDGAR reports monetary values in full units. Raw values are
preserved through the pipeline and divided by 1,000,000 only for display, so no precision is lost.
Ratios and per-unit figures are never scaled — EV per demat account is a small absolute number, and
scaling it to millions would render it meaningless.

**Coverage reporting is template-aware.** Banks legitimately lack revenue and EBITDA; fee businesses
legitimately lack deposits and loans. Inapplicable fields are suppressed so genuine gaps aren't
buried in expected noise.

**One bad ticker doesn't fail the run.** Failures are collected into an `errors` list and surfaced in
the coverage report.

**Market data is supplied separately.** EDGAR carries filings, not quotes. Prices come from a JSON
file with an explicit `as_of` date, or inline in the CSV, keeping the market-data date auditable
rather than implicitly "whenever the script ran".

---

## Module map

| Module | Responsibility |
|---|---|
| `edgar.py` | HTTP client (`urllib`), ticker→CIK resolution, on-disk cache, `OfflineClient` for fixtures |
| `csv_input.py` | Manual CSV loading, tolerant number parsing, inline prices, template writer |
| `normalize.py` | Candidate tag lists, composite assembly, derived fields, schema contract |
| `multiples.py` | EV bridge, all multiples, sector metrics, peer statistics, OLS regression |
| `comps.py` | Row construction, column templates, display scaling, coverage reporting |
| `excel_export.py` | CSV, fixed-width text, optional formatted `.xlsx` |
| `cli.py` | `comps` and `regress` subcommands |
| `tools/make_fixtures.py` | Regenerates the EDGAR-shaped offline fixtures |

---

## Commands

### `comps` — build a comparables table

| Flag | Purpose |
|---|---|
| `--peers` | Comma-separated tickers (EDGAR path) |
| `--input-csv` | Load from manual CSV instead of EDGAR — required for non-SEC filers |
| `--template` | `industrial` (default), `bank`, `amc`, `depository` |
| `--bank` | Shorthand for `--template bank` |
| `--fiscal-year` | Fiscal year to pull |
| `--offline` | Run from bundled fixtures |
| `--cache-dir` | Cache EDGAR responses to avoid repeat requests |
| `--prices` | JSON file of prices and share counts |
| `--out` / `--format` | Output path and format (`csv` or `xlsx`) |
| `--raw` | Write unformatted numbers rather than display strings |

### `regress` — P/TBV vs. ROTE

Fits an OLS regression of price-to-tangible-book on return on tangible equity across a peer set,
then reports each company's fitted value and residual. The empirical backbone of bank relative
valuation: it separates "cheap because returns are poor" from "cheap for no explained reason". Works
with either data source.

---

## Sector metrics

| Metric | Used for | Note |
|---|---|---|
| `p_aum` | Asset managers | Market cap as % of AUM. **How AMC deals are actually priced**, giving a direct bridge from trading comps to precedents. |
| `aum_yield_bps` | Asset managers | Blended fee yield. Required context — a low P/AUM on a liquid-heavy book is not cheap. |
| `ev_per_account` | Depositories | Capitalised value of each account relationship |
| `revenue_per_account` | Depositories | Monetisation intensity; where fee compression appears first |
| `p_tbv`, `rote` | Banks | See the [bank primer](../docs/bank-valuation-primer.md) |

---

## About the bundled sample data

**All bundled data is synthetic.** It exists to exercise the pipeline offline and must not be
mistaken for filed figures:

- **EDGAR fixtures** (`companyfacts_*.json`) — entity names suffixed `(SYNTHETIC)`, values are round
  numbers. Calibrated to reproduce the *qualitative* Citigroup situation (lowest ROTE in the peer
  set, P/TBV below 1.0x) so the regression output is pedagogically meaningful. A test asserts this
  relationship holds. Regenerate with `python3 tools/make_fixtures.py`.
- **CSV templates** (`amc_peers_template.csv`, `depository_peers_template.csv`) — every company name
  is suffixed `(PLACEHOLDER)`, and tests assert that. **Replace every figure from annual reports
  before drawing any conclusion.**

One caveat worth stating: the regression R² against the EDGAR fixtures is ~0.97 because the synthetic
values sit almost exactly on a line by construction. **Real peer data gives a materially lower R².**
Do not quote the fixture figure as a finding.

---

## Tests

```bash
python3 -m unittest discover -s tests -v
```

155 tests, no network required. Coverage concentrates on the failure modes that matter:

- Zero, negative and missing denominators
- `None` excluded from medians rather than coerced to zero
- Restatement precedence (later filing wins)
- Quarterly observations excluded from annual comps
- Composite debt assembly, including partial components
- Currency scaling applied to absolute figures but never to ratios or per-unit metrics
- Bank template structurally cannot contain EV multiples
- CSV parsing of thousands separators, currency symbols, parenthesised negatives and n/a variants
- Blank CSV cells preserved as `None`, never `0`
- Hand-entered EBITDA takes precedence over the derived value
- Manual records satisfy the same schema contract as EDGAR records
- Sector metrics return `None` when their operating base is absent
- Bad tickers and malformed CSVs collected or reported with actionable messages

---

## Known limitations

- **ROTE uses period-end tangible book**, not an average of opening and closing. Single-period
  fixtures lack the prior year.
- **No calendarisation.** Peers with differing fiscal year ends are not adjusted to a common period
  (Week 31 in the roadmap).
- **No segment-level data.** Company-level aggregates only.
- **Multiples are unadjusted.** No normalisation for exceptional items, which a real analyst would
  scrub by hand — which is why a hand-entered EBITDA overrides the derived one.
- **CSV data is only as good as the typing.** There is no cross-check against the source filing;
  the model checklist is the control.
- The SEC rate limit is respected with a fixed delay rather than adaptive backoff.
