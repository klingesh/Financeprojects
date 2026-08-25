# Finance Portfolio — Valuation, Deal Modelling & Analyst Tooling

A working portfolio of financial models and analytical tooling, built to demonstrate accounting
fluency, valuation judgement and deal mechanics across the financial services sector.

Every model is built from primary sources (annual reports and regulatory filings), follows a
documented set of [modelling standards](docs/modeling-standards.md), and ships with a PDF export so
it can be reviewed without opening Excel.

---

## The organising idea

The three subjects were chosen deliberately: they span the **three revenue architectures** of
financial services, and each demands a different valuation approach.

| Company | Architecture | Revenue driver | Valuation toolkit |
|---|---|---|---|
| **CDSL** | Fee on activity | Accounts × fee, volumes × rate | Standard DCF |
| **HDFC AMC** | Fee on assets | AUM × basis points | DCF + sum-of-parts |
| **Citigroup** | Spread on own balance sheet | Earning assets × NIM | DDM, residual income |

The reason this matters: a bank cannot be valued with a DCF, and an asset manager cannot be valued
on tangible book. Understanding *why* the toolkit changes — and being able to say so — is the point
of building all three rather than one.

---

## Projects

### 1. CDSL — Central Depository Services
**[→ 01-cdsl-depository/](01-cdsl-depository/)**

Valuation of one of India's two securities depositories. A regulated duopoly with unusually
transparent drivers.

| Deliverable | What it demonstrates |
|---|---|
| Three-statement operating model | Driver-based forecasting, recurring vs. cyclical revenue split, integrated statements |
| DCF valuation | Free cash flow bridge, cost of equity, dual terminal value, sensitivities |
| Trading comps | Peer selection, EV bridge with net cash, sector-specific multiples |
| Football field | Triangulation across available methodologies |

Revenue is built line by line on its own driver, separating **recurring** fee income (annual issuer
charges) from **cyclical** transaction income. That split is what determines the valuation floor
versus the earnings volatility.

Includes a genuine analytical finding: **CDSL cannot be LBO'd.** As a Market Infrastructure
Institution it is subject to SEBI shareholding caps that make sponsor control impossible. The
portfolio's LBO uses CAMS instead — a registrar, not an MII, with a real private equity ownership
history.

### 2. HDFC AMC — Asset Management
**[→ 02-hdfc-amc/](02-hdfc-amc/)**

Valuation of one of India's largest mutual fund managers, plus the portfolio's merger model.

> This is HDFC **Asset Management Company**, not HDFC **Bank**. They are entirely different
> valuation problems — see the project README for the comparison.

| Deliverable | What it demonstrates |
|---|---|
| Three-statement operating model | AUM-by-category revenue build, operating leverage |
| Sum-of-parts DCF | Separating a fee franchise from a treasury book |
| AMC trading comps and precedents | P/AUM analysis, deals priced as % of AUM |
| Merger model | Accretion/dilution, breakeven synergies, AUM attrition |

Revenue is built as **AUM by category × yield in basis points**, never as a blended average —
because equity, debt, liquid and passive products earn very different fees, so the blended yield
moves on mix alone. AUM growth is decomposed into **net flows** (management performance) versus
**market appreciation** (market beta), which is the core analytical discipline in asset management.

### 3. Citigroup — Financial Institutions Valuation
**[→ 03-citigroup-fig/](03-citigroup-fig/)**

Banks cannot be valued with the standard toolkit. This project builds the alternative:

- **Dividend Discount Model** with dividends constrained by CET1 capital adequacy
- **Residual Income / Excess Returns** — value = tangible book + PV of (ROTE − Ke) × TBV
- **P/TBV vs. ROTE regression** across US money-centre and universal bank peers
- Net interest margin decomposition, credit cost analysis, CET1 and RWA density

See the [bank valuation primer](docs/bank-valuation-primer.md) for why unlevered FCF, EV/EBITDA and
LBO analysis are all inapplicable to a bank.

### 4. Analyst Toolkit — Comps Automation
**[→ 04-analyst-toolkit/](04-analyst-toolkit/)**

A dependency-free Python package that pulls XBRL financial data from the SEC EDGAR API, normalises
inconsistent filer tagging into a common schema, computes trading multiples and exports a
comparable-companies table.

```bash
cd 04-analyst-toolkit
python -m analyst_toolkit.cli comps --offline --bank        # runs from bundled fixtures
python -m analyst_toolkit.cli regress --offline             # P/TBV vs. ROTE regression
python -m analyst_toolkit.cli comps --peers C,JPM,BAC,WFC,GS,MS --bank --out comps.xlsx
```

Standard library only. The interesting problem is XBRL tag inconsistency — filers report the same
concept under different `us-gaap` tags across years, so the normalisation layer resolves each field
through a prioritised candidate list.

Indian issuers do not file with the SEC, so the toolkit also accepts **manual CSV input**, letting
the CDSL and HDFC AMC peer sets run through the same multiples and statistics engine.

---

## Repository Map

```
├── docs/
│   ├── modeling-standards.md        Excel conventions and integrity checks
│   ├── fee-business-modelling.md    Capital-light fee businesses (CDSL, HDFC AMC)
│   ├── bank-valuation-primer.md     Why financials need a different toolkit
│   └── interview-prep-map.md        Which project answers which question
├── templates/
│   ├── investment-memo-template.md
│   └── model-checklist.md           Pre-flight QA before any model is called done
├── 01-cdsl-depository/
├── 02-hdfc-amc/
├── 03-citigroup-fig/
└── 04-analyst-toolkit/
```

## Build Plan

Built over 32 weeks at roughly one hour per day. The full day-by-day schedule is in
**[ROADMAP.md](ROADMAP.md)**.

## Limitations

Stated plainly, because every model has them:

- Forecasts are the author's own estimates, not company guidance, and are not investment advice.
- **No capital-intensive industrial model.** All three subjects are capital-light or financial, so
  heavy PP&E roll-forwards, capex-driven growth and inventory-based working capital are not
  exercised here. A deliberate trade-off in favour of sector depth.
- **Depository transaction precedents do not exist.** SEBI's MII ownership caps preclude control
  transactions, so the CDSL football field carries one fewer methodology — by necessity, not
  omission.
- The CAMS LBO and the HDFC AMC / UTI AMC merger are academic exercises using plausible but
  hypothetical transaction terms.
- Comps use unadjusted reported figures unless a normalisation is explicitly documented.
- Precedent transaction data is assembled from public announcements; undisclosed terms are marked as
  such rather than estimated.
