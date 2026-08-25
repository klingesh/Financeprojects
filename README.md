# Finance Portfolio — Valuation, Deal Modelling & Analyst Tooling

A working portfolio of financial models and analytical tooling, built to demonstrate
accounting fluency, valuation judgement and deal mechanics.

Every model is built from primary sources (annual reports and regulatory filings),
follows a documented set of [modelling standards](docs/modeling-standards.md), and ships
with a PDF export so it can be reviewed without opening Excel.

---

## Projects

### 1. UltraTech Cement — Valuation Suite & Deal Models
**[→ 01-ultratech-cement/](01-ultratech-cement/)**

Full-stack valuation of India's largest cement producer (Aditya Birla Group).

| Deliverable | What it demonstrates |
|---|---|
| Three-statement operating model | Driver-based forecasting, working capital, PP&E and debt schedules, integrated statements |
| DCF valuation | Unlevered FCF, WACC build-up, dual terminal value, sensitivity analysis |
| Trading comps & precedent transactions | Peer selection, multiple calculation, calendarisation |
| Football field | Triangulation of value across methodologies |
| LBO model | Sources & uses, cash sweep across tranches, IRR / MoIC returns attribution |
| Merger model | Consideration mix, goodwill creation, EPS accretion/dilution, breakeven synergies |

Revenue is built bottom-up as **capacity × utilisation × realisation per tonne**, which makes
the operating leverage in a capital-intensive cyclical business explicit rather than assumed.

### 2. Citigroup — Financial Institutions Valuation
**[→ 02-citigroup-fig/](02-citigroup-fig/)**

Banks cannot be valued with the standard toolkit. This project builds the alternative:

- **Dividend Discount Model** and **Residual Income / Excess Returns** valuation
- **P/TBV vs. ROTE** regression across US money-centre and universal bank peers
- Net interest margin decomposition, provisioning and credit cost analysis
- CET1 capital adequacy, RWA density and capital return capacity

See the [bank valuation primer](docs/bank-valuation-primer.md) for why unlevered FCF, EV/EBITDA
and LBO analysis are all inapplicable to a bank.

### 3. Analyst Toolkit — Comps Automation
**[→ 03-analyst-toolkit/](03-analyst-toolkit/)**

A dependency-free Python package that pulls XBRL financial data from the SEC EDGAR API,
normalises inconsistent filer tagging into a common schema, computes trading multiples and
exports a formatted comparable-companies table.

```bash
cd 03-analyst-toolkit
python -m analyst_toolkit.cli comps --peers C,JPM,BAC,WFC,GS,MS --out comps.csv
python -m analyst_toolkit.cli comps --offline --out comps.csv   # runs from bundled fixtures
```

Standard library only. The interesting problem is XBRL tag inconsistency — filers report the
same concept under different us-gaap tags across years, so the normalisation layer resolves
each field through a prioritised candidate list.

---

## Repository Map

```
├── docs/
│   ├── modeling-standards.md      Excel conventions and integrity checks
│   ├── bank-valuation-primer.md   Why financials need a different toolkit
│   └── interview-prep-map.md      Which project answers which interview question
├── templates/
│   ├── investment-memo-template.md
│   └── model-checklist.md         Pre-flight QA before any model is called done
├── 01-ultratech-cement/
├── 02-citigroup-fig/
└── 03-analyst-toolkit/
```

## Build Plan

The portfolio is built over 28 weeks at roughly one hour per day.
The full day-by-day schedule is in **[ROADMAP.md](ROADMAP.md)**.

## Limitations

Stated plainly, because every model has them:

- Forecasts are the author's own estimates, not company guidance, and are not investment advice.
- Precedent transaction data is assembled from public deal announcements; undisclosed terms are
  marked as such rather than estimated.
- The UltraTech LBO is an academic exercise — a promoter-controlled Indian listed company with
  this profile is not a realistic buyout candidate. It exists to demonstrate the mechanics.
- Comps use unadjusted reported figures unless a normalisation is explicitly documented.
