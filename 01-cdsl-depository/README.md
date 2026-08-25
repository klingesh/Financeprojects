# CDSL — Central Depository Services (India) Ltd

Full-stack valuation of CDSL (NSE: CDSL), one of two securities depositories in India.

**Reporting basis:** Ind AS · consolidated · fiscal year ends **31 March** · figures in **₹ crore**

> Read [`../docs/fee-business-modelling.md`](../docs/fee-business-modelling.md) before starting.
> This is a capital-light fee business — the model architecture differs structurally from a
> capital-intensive industrial, not just in scale.

---

## Why this company

The core modelling subject for the portfolio:

- **Regulated duopoly.** CDSL and NSDL are the only two depositories in India. Market structure is
  unusually clean to analyse.
- **A direct listed peer now exists.** NSDL listed in August 2025, giving you a true like-for-like
  comparable rather than a stretch to loosely related names. Before that, CDSL had no listed
  depository peer anywhere in India.
- **Transparent drivers.** Demat account counts, issuer counts and transaction volumes are all
  disclosed and independently verifiable.
- **Recurring plus cyclical revenue in one business.** Annual fees recur; transaction charges swing
  with market activity. Modelling both teaches you to separate the valuation floor from the
  earnings volatility.
- **Genuinely contested thesis.** SEBI sets or influences pricing, so a regulatory circular can
  compress fees regardless of volume growth. That makes for a real risk section.

---

## Deliverables

| # | File | Status |
|---|---|---|
| 1 | `models/cdsl_operating_model.xlsx` — three-statement model | Not started |
| 2 | `models/cdsl_dcf.xlsx` (or DCF tab) — DCF and cost of equity | Not started |
| 3 | `models/cdsl_comps.xlsx` — trading comps and precedents | Not started |
| 4 | `outputs/football_field.png` — valuation triangulation | Not started |
| 5 | `outputs/*.pdf` — PDF exports | Not started |

The LBO and merger model live in [`../02-hdfc-amc/`](../02-hdfc-amc/) and the CAMS sub-project —
see the roadmap. **CDSL itself cannot be used for an LBO**; the reason is explained below and is
worth understanding.

---

## Workbook Structure

```
Cover        Purpose, units (₹ crore), date, master check flag
Assumptions  All inputs. Blue font only. Scenario toggle here.
Drivers      Demat accounts, issuers, transaction volumes, KYC volumes
IS           Income statement — 8 years historical + 5 years forecast
BS           Balance sheet — same periods
CFS          Cash flow statement — same periods
Segments     Revenue by line (issuer fees, transaction, KYC, other)
DCF          FCF bridge, cost of equity, terminal value, sensitivities
Comps        Trading comparables and precedent transactions
Checks       Integrity tests — build BEFORE the forecast
```

Follow [`../docs/modeling-standards.md`](../docs/modeling-standards.md) without exception.

---

## The Revenue Build

CDSL earns fees on activity and accounts it does not own. Model each line on its own driver —
this is the core of the project.

| Revenue line | Driver | Character |
|---|---|---|
| **Annual issuer charges** | Number of issuer companies × slab-based fee (folio/market-cap linked) | **Recurring** — sticky, largely market-independent |
| **Transaction charges** | Debit transaction volumes × charge per debit | **Cyclical** — tracks market activity closely |
| **IPO / corporate action charges** | Corporate action volumes, new issuances | Cyclical, lumpy |
| **Online data charges (KYC)** | KYC volumes via CDSL Ventures (CVL, a KYC Registration Agency) | Growth-linked, tied to new investor onboarding |
| **e-CAS, e-voting, other** | Account counts, event volumes | Mostly recurring |

The single most important structural decision:

```
Recurring revenue  →  supports the valuation floor
Cyclical revenue   →  creates the earnings volatility
```

Forecast them separately. A model that grows total revenue at one blended rate cannot show what
happens to CDSL in a bear market, which is precisely the question a valuation needs to answer.

### Driver chain

```
Demat (BO) accounts     ← new investor onboarding; the structural growth story
Number of issuers       ← listed + unlisted companies using the depository
Transaction volumes     ← market turnover and investor churn
KYC volumes             ← new account openings across the market
```

Back-test your driver logic against the last three reported years before forecasting. If it does
not reproduce actual revenue within a few percent, your fee-per-unit assumption is wrong.

### Cost build

Forecast bottom-up, **not** as a percentage of revenue:

- **Employee cost** — headcount × average cost, inflation-linked
- **Technology and connectivity** — largely fixed, stepping up with capacity investment
- **Regulatory, compliance, audit** — fixed
- **Other operating expenses** — partly fixed

Because costs barely respond to volumes, margins should expand as the base grows. Track
**operating cost per demat account** across the forecast — it should trend down. If margins are
flat in your forecast, either your cost build is wrong or you hold an unstated view on fee
compression. State it either way.

---

## Why CDSL Cannot Be LBO'd

Worth understanding, because it is a genuine insight and an interview-worthy observation.

CDSL is a **Market Infrastructure Institution** under SEBI regulation. MIIs are subject to strict
shareholding caps — no single investor may hold more than a small prescribed percentage, with
narrow exceptions for sponsors. A financial sponsor cannot acquire control, so a leveraged buyout
is not merely unattractive, it is **regulatorily impossible**.

This is why the portfolio's LBO uses **CAMS** instead. CAMS is a registrar and transfer agent, not
an MII, so it is not subject to the same ownership caps — and it has a genuine private equity
ownership history. See the roadmap.

Recognising which businesses can and cannot be bought is exactly the judgement an IB analyst is
expected to have.

---

## Comparable Companies

Justify each inclusion in writing on the `Comps` tab.

**Direct peer**
- **NSDL** — National Securities Depository Ltd. Listed August 2025 on BSE (note: not listed on
  NSE). The only true like-for-like comparable. Read its IPO prospectus — it is the single best
  source of Indian depository industry data in existence.

**Market infrastructure / adjacent**
- BSE Ltd (NSE: BSEL) — exchange; note it has historically held a stake in CDSL
- Multi Commodity Exchange of India (NSE: MCX) — commodity exchange
- CAMS — Computer Age Management Services (NSE: CAMS) — mutual fund RTA
- KFin Technologies (NSE: KFINTECH) — RTA, CAMS's competitor

**Notes on peer selection**
- NSE is unlisted, though a listing has been anticipated for some time — verify its current status
  before treating it as a comp.
- Global depositories (DTCC, Euroclear, Clearstream) are unlisted or embedded in larger groups, so
  international comps are of limited use. Say so rather than forcing a bad comparison.
- Exchanges and RTAs share the capital-light regulated-fee profile but have different growth and
  regulatory exposure. Note the differences rather than treating all five as homogeneous.

**Multiples to compute**

| Multiple | Why |
|---|---|
| **P/E** | Dominant multiple for this asset-light, net-cash profile |
| EV/EBITDA | Cross-check — remember net cash makes **EV lower than market cap** |
| **EV per demat account** | Sector-specific. Capitalises the value of each account relationship. |
| Revenue per demat account | Monetisation intensity; reveals pricing power directly |
| ROE | Structurally high in capital-light models — compare to peers, not to industrials |

---

## Precedent Transactions

Depository M&A in India is effectively absent because of the MII ownership caps, so genuine
precedents are scarce. Handle this honestly: **state that transaction comps are not meaningfully
available for this asset class** rather than padding the section.

What you *can* research:

- **Regulatory-driven stake divestments** — BSE's reduction of its CDSL holding to comply with
  ownership limits, and NSE's divestment of its CAMS stake. These are forced sales, not control
  transactions, so they establish minority valuation reference points only. Label them as such.
- **Global exchange and infrastructure deals for context** — LSEG/Refinitiv, ICE/Black Knight,
  Nasdaq/Adenza, Deutsche Börse/ISS. Different markets and regulatory regimes, so use these to
  frame multiple ranges rather than as direct precedents.

Verify every figure from primary announcements. Mark undisclosed terms as undisclosed.

---

## Data Sources

| Source | Use |
|---|---|
| CDSL investor relations — annual reports | Primary financials. Download FY2018 onward (post-IPO). |
| Quarterly results and investor presentations | Operating metrics: accounts, volumes, revenue split |
| **NSDL IPO prospectus (DRHP/RHP)** | **Best available industry dataset.** Market share, industry volumes, competitive detail. |
| SEBI bulletins and circulars | Fee regulations, MII ownership rules, market activity data |
| BSE / NSE announcements | Filings, shareholding patterns |
| CDSL monthly business updates | Account and volume trends between quarters |

Store filings in `data/`. Aggregator sites are fine for a quick history but verify every figure
against the annual report before it enters the model.

> **Note:** Indian companies do not file with SEC EDGAR, so the toolkit's EDGAR path cannot pull
> this data. Use the toolkit's **CSV input mode** to run CDSL and peer comps through the same
> multiples and statistics engine — see [`../04-analyst-toolkit/`](../04-analyst-toolkit/).

---

## Assumptions Log

| Assumption | Base | Bull | Bear | Basis |
|---|---|---|---|---|
| Demat account growth % | | | | |
| Issuer count growth % | | | | |
| Transaction volume growth % | | | | |
| Fee per debit (₹) | | | | regulated — flag change risk |
| Annual issuer fee growth % | | | | |
| KYC volume growth % | | | | |
| Employee cost growth % | | | | |
| Effective tax rate | | | | |
| Risk-free rate | | | | as-of date |
| Equity risk premium | | | | |
| Beta | | | | high — volumes are market-linked |
| **Cost of equity (= WACC, no debt)** | | | | |
| Terminal growth | | | | |

Note the WACC line explicitly: **CDSL carries no debt, so WACC collapses to cost of equity.** Do
not build an elaborate weighted calculation with a zero debt weight.

---

## Valuation Summary

| Method | Low | High | Implied ₹/share |
|---|---|---|---|
| 52-week trading range | | | |
| Trading comparables (vs. NSDL, BSE, MCX) | | | |
| DCF | | | |
| **Conclusion** | | | |

**Current share price:** _as of date_
**Recommendation:** _to be written_

**The central question:** does the structural growth in demat accounts and market participation
outweigh the risk that SEBI compresses fee rates?

---

## Limitations

- Forecasts are the author's own estimates, not company guidance. Not investment advice.
- **Transaction precedents are not meaningfully available** for Indian depositories because MII
  ownership caps preclude control transactions. The football field therefore has one fewer
  methodology than a standard valuation, by necessity rather than omission.
- Regulated fee rates can change by circular with limited notice; the forecast assumes the current
  fee structure persists unless explicitly flexed in a scenario.
- NSDL's listed history is short, so its trading multiple may not yet reflect a settled market view.
- Transaction volume forecasting is inherently tied to market activity, which is not forecastable
  with confidence. The scenario range is wide for this reason.
