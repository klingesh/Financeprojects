# UltraTech Cement — Valuation Suite & Deal Models

Full-stack valuation and transaction analysis of UltraTech Cement Ltd (NSE: ULTRACEMCO),
India's largest cement producer and the cement arm of the Aditya Birla Group.

**Reporting basis:** Ind AS · consolidated · fiscal year ends **31 March** · figures in **₹ crore**

---

## Why this company

Chosen deliberately as the core modelling subject:

- **Single segment.** Grey cement dominates the business, so there's no segment-level complexity
  diluting the modelling work.
- **Capital intensive and cyclical.** This makes PP&E schedules, capex forecasting and operating
  leverage genuinely meaningful rather than rounding errors.
- **Excellent disclosure.** Management reports per-tonne operating metrics quarterly, which lets you
  build a real driver-based model instead of guessing at percentage growth.
- **Deep comparable set.** Six-plus listed peers of meaningful scale.
- **Active M&A sector.** Indian cement has consolidated heavily, giving real precedent transactions
  to work with.

---

## Deliverables

| # | File | Status |
|---|---|---|
| 1 | `models/ultratech_operating_model.xlsx` — three-statement model | Not started |
| 2 | `models/ultratech_dcf.xlsx` (or DCF tab) — DCF and WACC | Not started |
| 3 | `models/ultratech_comps.xlsx` — trading comps and precedents | Not started |
| 4 | `outputs/football_field.png` — valuation triangulation | Not started |
| 5 | `models/ultratech_lbo.xlsx` — leveraged buyout | Not started |
| 6 | `models/cement_merger_model.xlsx` — accretion/dilution | Not started |
| 7 | `outputs/*.pdf` — PDF export of each model | Not started |

Update this table as you go. It's the first thing a reviewer looks at.

---

## Workbook Structure

Build the operating model with these tabs, in this order:

```
Cover        Model purpose, author, date, units, master check flag, circularity toggle instructions
Assumptions  Every input in the model. Blue font only. Scenario toggle lives here.
IS           Income statement — 8 years historical + 5 years forecast
BS           Balance sheet — same periods
CFS          Cash flow statement — same periods
WC           Working capital schedule (DSO / DIO / DPO)
PPE          PP&E roll-forward and depreciation waterfall
Debt         Debt schedule by facility, interest on average balance
DCF          UFCF bridge, WACC, terminal value, sensitivity tables
Comps        Trading comparables and precedent transactions
Checks       Integrity tests — build this BEFORE the forecast
```

Follow [`../docs/modeling-standards.md`](../docs/modeling-standards.md) without exception.

---

## The Revenue Driver Chain

This is what distinguishes a real cement model from a generic one. Do not forecast revenue as
"grows 8% a year."

```
Capacity (MTPA)                    ← from announced expansion pipeline, with commissioning dates
  × Utilisation (%)                ← your cyclical view; the key judgement call
  = Sales volume (mt)
  × Realisation (₹ / tonne)        ← pricing; regionally driven
  = Revenue (₹ crore)
```

Then build costs **per tonne**, not as a percentage of revenue:

| Cost line | Driver | Notes |
|---|---|---|
| Power & fuel | Fuel price × consumption/tonne | Most volatile line. Petcoke and coal linked. |
| Freight & forwarding | Lead distance × volume | Huge in cement — heavy, low value-to-weight. Scales with volume, not revenue. |
| Raw materials | ₹/tonne | Limestone, fly ash, slag. Blending ratio affects this. |
| Employee cost | Inflation | Largely **fixed** — do not scale with volume. |
| Other expenses | Inflation + volume mix | Partly fixed. |

Forecasting fixed costs as fixed is what produces realistic operating leverage. If you grow every
cost line with revenue, your margins will be flat forever and the model will teach you nothing.

**The critical validation:** compute implied **EBITDA per tonne** for every forecast year and plot it
against 8 years of history. EBITDA/tonne is how the entire sector is discussed. If your forecast sits
outside the historical range, you must either justify it explicitly or revise it.

---

## Comparable Companies

Justify each inclusion in writing on the `Comps` tab.

**Core peers**
- Shree Cement (NSE: SHREECEM)
- Ambuja Cements (NSE: AMBUJACEM)
- ACC (NSE: ACC)
- Dalmia Bharat (NSE: DALBHARAT)
- JK Cement (NSE: JKCEMENT)
- The Ramco Cements (NSE: RAMCOCEM)

**Consider also**
- Birla Corporation, Nuvoco Vistas, JK Lakshmi Cement, Star Cement

**Analytical note:** Ambuja and ACC came under Adani Group control following Holcim's exit from
India in 2022. Ownership change can affect capital allocation, growth ambition and therefore the
multiple. Note this rather than treating all peers as homogeneous.

**Multiples to compute**

| Multiple | Why |
|---|---|
| EV / EBITDA | Primary multiple for the sector |
| EV / Revenue | Secondary cross-check |
| P / E | Affected by differing leverage and depreciation policy |
| **EV / tonne of capacity** | **Cement-specific.** Values the asset base directly and is how deals in the sector are actually priced. Including it signals real sector knowledge. |

Handle **calendarisation** — UltraTech's year ends 31 March, and not every peer matches. Adjust to a
common period or your comparison is spurious.

---

## Precedent Transactions

Research these from **primary announcement documents**. Verify every figure — secondary summaries
are frequently wrong, and undisclosed terms should be marked undisclosed rather than estimated.

Candidates to investigate:

- **Adani / Holcim** — acquisition of Holcim's Ambuja + ACC stakes (2022). The largest in the sector.
- **UltraTech / Jaiprakash Associates** — cement asset acquisition (2017)
- **UltraTech / Binani Cement** — acquired through the insolvency process (2018)
- **UltraTech / Kesoram Industries** — cement business (2024)
- **Ambuja / Sanghi Industries** (2023) and **Ambuja / Penna Cement** (2024)
- **Dalmia Bharat / Murli Industries** and other distressed acquisitions

For each: announced enterprise value, acquired capacity in MTPA, implied **EV per tonne**, and the
implied EV/EBITDA where EBITDA was disclosed. Then compare the transaction multiple range against
trading comps to quantify the **control premium**.

---

## Data Sources

| Source | Use |
|---|---|
| UltraTech investor relations — annual reports | Primary financials. Download FY2016 onward. |
| Quarterly investor presentations | Per-tonne metrics and capacity pipeline. Annual reports bury these. |
| Quarterly results filings | Latest interim data |
| BSE / NSE announcements | Deal announcements, capacity commissioning |
| Cement Manufacturers' Association | Industry volume and capacity data |

Store everything in `data/`. Screener-type aggregator sites are acceptable for a quick history but
**verify every figure against the annual report** before it enters the model. Aggregators
misclassify exceptional items routinely.

> **Note:** Indian companies do not file with SEC EDGAR, so the Python toolkit in
> `03-analyst-toolkit/` cannot automate this data. UltraTech comps are assembled manually from
> annual reports; the toolkit handles the Citigroup peer set. This asymmetry is worth understanding —
> data availability shapes what can be automated.

---

## Assumptions Log

Record your key assumptions here as you set them, with justification. This becomes your interview
script — you must be able to defend every number.

| Assumption | Base | Bull | Bear | Basis |
|---|---|---|---|---|
| Utilisation % | | | | |
| Realisation growth % | | | | |
| Fuel cost/tonne growth | | | | |
| Maintenance capex % of revenue | | | | |
| Growth capex (₹ cr) | | | | |
| Effective tax rate | | | | |
| WACC | | | | |
| Terminal growth | | | | |
| Exit EV/EBITDA | | | | |

---

## Valuation Summary

Complete after Phase 2.

| Method | Low | High | Implied ₹/share |
|---|---|---|---|
| 52-week trading range | | | |
| Trading comparables | | | |
| Precedent transactions | | | |
| DCF | | | |
| **Conclusion** | | | |

**Current share price:** _as of date_
**Recommendation:** _to be written_

---

## Limitations

- Forecasts are the author's own estimates, not company guidance. Not investment advice.
- The LBO is an academic exercise. UltraTech is promoter-controlled with a market capitalisation far
  beyond realistic buyout scale, and Indian leveraged finance markets would not support this
  structure. It exists to demonstrate mechanics.
- The merger model uses a constructed acquirer/target pair for illustrative purposes.
- Precedent transaction data is limited by disclosure; undisclosed terms are marked as such.
