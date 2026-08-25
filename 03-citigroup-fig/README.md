# Citigroup — Financial Institutions Valuation

Valuation of Citigroup Inc. (NYSE: C) using the financial-institutions toolkit.

**Reporting basis:** US GAAP · **calendar** fiscal year · figures in **US$ millions**

> **Read [`../docs/bank-valuation-primer.md`](../docs/bank-valuation-primer.md) before starting.**
> Everything from the CDSL and HDFC AMC projects about EV/EBITDA, unlevered free cash flow and LBO
> analysis is **inapplicable to a bank.** Understanding why is the purpose of this project.

---

## Why this company

- **The canonical valuation debate.** Citi has persistently traded at a discount to tangible book
  value. Whether that discount reflects structurally poor returns or a genuine mispricing is a real,
  contested question — not a textbook exercise with a known answer.
- **Forces the alternative toolkit.** You cannot fake your way through this with a DCF.
- **A live restructuring story.** The ongoing simplification programme, business exits and
  divestitures give the analysis genuine catalysts.
- **Files with SEC EDGAR**, so the Python toolkit can automate the peer data.
- **Recognisable name** on a resume, in a coverage area (FIG) that is a real IB group.

---

## Deliverables

| # | File | Status |
|---|---|---|
| 1 | `models/citi_financial_summary.xlsx` — historicals, segments, NIM, credit, capital | Not started |
| 2 | `models/citi_ddm.xlsx` — dividend discount model | Not started |
| 3 | `models/citi_residual_income.xlsx` — excess returns valuation | Not started |
| 4 | `models/bank_peer_regression.xlsx` — P/TBV vs. ROTE | Not started |
| 5 | `outputs/ptbv_rote_regression.png` — the chart | Not started |
| 6 | `outputs/*.pdf` — PDF exports | Not started |

---

## Workbook Structure

```
Cover        Purpose, units (US$m), date, check flags
Segments     Revenue and net income by reported segment
BS_Analysis  Earning assets, loans by category, deposits by type, funding mix
NIM          Yield on earning assets, cost of funds, margin decomposition by quarter
Credit       Provisions, NCO rate, ACL/loans, NPLs
Capital      CET1, RWA, RWA density, SLR, GSIB surcharge
Forecast     5-year projection — balance sheet first, then income statement
DDM          Dividend discount model
RI           Residual income model
Peers        P/TBV and ROTE across peer set, with regression
Checks       Integrity tests
```

---

## Segment Structure

Citigroup reports through five core businesses plus a residual. Map current-period revenue and net
income to each from the latest 10-K:

| Segment | Contains |
|---|---|
| **Services** | Treasury & Trade Solutions, Securities Services |
| **Markets** | Fixed income and equity trading |
| **Banking** | Investment banking, corporate lending |
| **Wealth** | Private bank, wealth management |
| **US Personal Banking** | Cards, retail banking |
| **All Other** | Legacy franchises and divestiture-related items |

Note which segments earn returns above cost of equity and which dilute group ROTE. That distinction
drives the restructuring thesis — the argument for Citi is essentially that exiting low-return
businesses lifts group returns toward the peer group.

---

## The Modelling Order (balance sheet first)

This is structurally different from an industrial model. Do not start with revenue.

```
1. Average earning assets     ← loan growth by category + securities portfolio
2. × Yield on earning assets  = Interest income
3. Funding base               ← deposits by type + wholesale borrowings
4. × Cost of funds            = Interest expense
5. Net interest income        = (2) − (4)
6. + Fee & trading revenue    ← large for Citi: Services and Markets
7. − Non-interest expense     ← driven by target efficiency ratio
8. − Provision for credit losses  ← loan growth × assumed loss rate
9. − Tax                      = Net income
10. Roll RWA forward → check CET1 ratio
11. Distributable capital = what remains after funding RWA growth and holding required CET1
```

**Step 11 is what makes this a bank model.** Shareholder returns are constrained by regulatory
capital, not by cash generation. Model that constraint explicitly rather than assuming a flat payout
ratio — the constraint *is* the analysis.

---

## Valuation Methods

### 1. Dividend Discount Model

```
Value/share = Σ [ DPS_t / (1 + Ke)^t ] + Terminal value
```

Dividends must be constrained by CET1 adequacy — a bank cannot distribute capital it needs to hold
against risk-weighted assets. Discount at **cost of equity** (CAPM), never WACC.

### 2. Residual Income / Excess Returns

```
RI_t   = (ROTE_t − Ke) × TBV_(t−1)
Value  = TBV_0 + Σ [ RI_t / (1 + Ke)^t ]
```

If ROTE < Ke, this model returns a value **below** tangible book — mathematically, not as an error.
That is precisely the Citi situation and the reason for the discount. Make sure you understand this
before you conclude the model is broken.

### 3. P/TBV vs. ROTE Regression

Peer set: **JPMorgan (JPM), Bank of America (BAC), Wells Fargo (WFC), Goldman Sachs (GS),
Morgan Stanley (MS)**. Consider adding US Bancorp and PNC for a broader regression, and note that GS
and MS have very different business mixes — flag that rather than ignoring it.

Regress P/TBV on ROTE, plot Citi against the fitted line, and interpret:

- **On the line** → the discount is fully explained by returns. No mispricing.
- **Below the line** → unexplained discount. Either the market doubts reported returns or there is
  opportunity.
- **Above the line** → improvement already priced in.

Then quantify the thesis: **what is Citi worth if it closes its ROTE gap to the peer median?** That
single number is the investment case, and it's the output a research analyst would actually publish.

---

## Metrics to Track

**Profitability** — ROTCE/ROTE, NIM, efficiency ratio, operating leverage
**Credit** — NCO rate, ACL/loans, NPL ratio, provision expense
**Capital** — CET1 ratio, RWA, RWA density, SLR, GSIB surcharge, TBV per share
**Funding** — deposit mix, share of non-interest-bearing deposits, deposit beta

Pull all values from the filings and record the reporting date. Do not carry forward stale figures —
bank capital and credit metrics move quarter to quarter.

---

## Data Sources

| Source | Use |
|---|---|
| SEC EDGAR — Citigroup 10-K and 10-Q | Primary financials |
| Citigroup investor relations — quarterly financial supplement | **Most useful single document.** Segment detail, per-share metrics, capital ratios in one place. |
| Quarterly earnings presentations | Management framing, targets |
| Federal Reserve stress test disclosures | Capital requirements, stress capital buffer |
| [`../04-analyst-toolkit/`](../04-analyst-toolkit/) | Automated peer data pull from EDGAR |

Store filings in `data/`.

---

## Assumptions Log

| Assumption | Value | Basis |
|---|---|---|
| Risk-free rate (10Y UST) | | as of date |
| Equity risk premium | | |
| Beta | | |
| Cost of equity (Ke) | | |
| Sustainable ROTE | | vs. management target |
| Required CET1 ratio | | regulatory minimum + management buffer |
| Loan growth | | |
| NIM trajectory | | |
| Normalised credit cost | | through-cycle, not current |
| Terminal growth | | |

---

## Valuation Summary

| Method | Value/share |
|---|---|
| Dividend discount model | |
| Residual income | |
| P/TBV regression implied | |
| P/TBV at peer-median ROTE | |
| **Conclusion** | |

**Current price / TBV per share:** _as of date_
**Recommendation:** _to be written_

**The central question to answer:** is the discount to tangible book a value opportunity, or a fair
reflection of returns that sit below the cost of equity?

---

## Limitations

- A simplified five-year forecast. A full bank model would project the loan book by portfolio segment
  with separate loss curves for each.
- Trading revenue in Markets is inherently difficult to forecast and is modelled as a normalised
  run-rate rather than driven by market activity.
- CECL provisioning depends on management's macroeconomic scenario weighting, which is not fully
  disclosed and cannot be exactly replicated.
- Regulatory capital requirements are subject to change; Basel III Endgame implementation remains a
  material uncertainty for RWA calculation.
- Not investment advice.
