# HDFC Asset Management Company Ltd

Valuation of HDFC AMC (NSE: HDFCAMC), one of India's largest mutual fund managers, plus the
portfolio's **merger model** (AMC consolidation).

**Reporting basis:** Ind AS · fiscal year ends **31 March** · figures in **₹ crore**

> Read [`../docs/fee-business-modelling.md`](../docs/fee-business-modelling.md) first, particularly
> the sections on **AUM mix shift** and **sum-of-parts for treasury books**. Both are essential here
> and both are where most people get an AMC model wrong.

---

## Important: this is the AMC, not the bank

HDFC **Bank** and HDFC **Asset Management Company** are entirely different valuation problems.

| | HDFC Bank | HDFC AMC |
|---|---|---|
| Business | Spread on own balance sheet | Fee on customers' assets |
| Capital | Regulatory capital constrained | Capital-light, net cash |
| DCF | Not applicable | **Works fully** |
| EV multiples | Meaningless | Meaningful |
| Primary multiple | P/TBV | **P/AUM**, P/E |

HDFC Bank is the promoter of HDFC AMC, which is why the names are similar. Only the AMC is
modelable with the standard toolkit — the bank belongs to the toolkit in
[`../docs/bank-valuation-primer.md`](../docs/bank-valuation-primer.md), which
[`../03-citigroup-fig/`](../03-citigroup-fig/) covers.

---

## Why this company

- **The cleanest possible fee-driver model.** Revenue is almost literally AUM × basis points. There
  is nowhere to hide a vague growth assumption.
- **Architecture reuse.** Having built CDSL, the workbook structure, cost-of-equity approach and
  comps methodology all carry across, so this project moves considerably faster.
- **Excellent listed comps.** Three directly comparable listed AMCs, unusual for an Indian sector.
- **A genuinely two-sided thesis.** Structural growth in Indian mutual fund penetration and SIP
  flows, against structural fee compression from TER regulation and the passive shift. Both
  arguments are strong, which makes for a real investment debate rather than a foregone conclusion.
- **Teaches sum-of-parts.** The company holds a substantial investment book, so a naive DCF or P/E
  double-counts. Handling this correctly is a differentiator.

---

## Deliverables

| # | File | Status |
|---|---|---|
| 1 | `models/hdfcamc_operating_model.xlsx` — three-statement model | Not started |
| 2 | `models/hdfcamc_dcf.xlsx` — DCF with sum-of-parts | Not started |
| 3 | `models/amc_comps.xlsx` — AMC trading comps and precedents | Not started |
| 4 | `models/amc_merger_model.xlsx` — accretion/dilution | Not started |
| 5 | `outputs/*.pdf` — PDF exports | Not started |

---

## The Revenue Build — AUM by category, never blended

This is the whole project. Get it right and everything follows.

```
Equity & growth AUM   × equity yield (bps)    ─┐
Debt / income AUM     × debt yield (bps)       ├─→ Investment management fee revenue
Liquid / overnight    × liquid yield (bps)     │
Passive / index / ETF × passive yield (bps)   ─┘
```

**Why category-level matters:** yields differ by a wide margin across categories. Equity funds earn
substantially more per rupee than debt funds, which in turn earn more than liquid funds, and passive
products earn a small fraction of active equity. So the **blended yield moves purely on mix**, even
when no individual fee rate changes.

A model that forecasts total AUM × a single blended yield cannot express the most important thing
happening in Indian asset management. Do not build one.

### Decompose AUM growth into its two sources

```
Opening AUM
  + Net flows          ← the business winning or losing money. Management performance.
  + Market appreciation ← the market moving. Nothing to do with management.
  = Closing AUM

Average AUM (AAUM)     ← revenue is earned on the average, not the closing balance
```

Keeping these separate is the core analytical discipline in asset management. A year of 25% AUM
growth in a market that rose 25% means the franchise won nothing. Conversely, positive net flows in
a falling market is a genuinely strong signal.

Note also that revenue accrues on **average** AUM — quarterly average (QAAUM) is the disclosed
figure. Using closing AUM overstates revenue in a rising market.

### Where the yield assumption comes from

Do not guess. Back-solve historical yield by category:

```
Implied yield (bps) = Segment revenue / Segment AAUM × 10,000
```

Then form a view on the trajectory. Yields have been under structural pressure from TER regulation
and competition. Your forecast should reflect a considered view, stated explicitly in the
assumptions log.

### Cost build

Forecast bottom-up. Costs do **not** scale with AUM:

- **Employee cost** — the largest line; headcount × average cost, inflation and increments
- **Fees and commission** — the one line that does partly scale with the asset base and distribution
- **Advertisement and business promotion** — discretionary, competitively driven
- **Other operating expenses** — largely fixed

The metric that shows whether you have modelled this correctly:

```
Operating profit as a percentage of average AUM  (in basis points)
```

Chart it across history and forecast. This is the standard AMC efficiency measure. If it is flat in
your forecast, you have either mis-built costs or you hold an unstated view on fee compression.

---

## Sum-of-Parts — do not skip this

HDFC AMC holds a meaningful investment portfolio built from retained earnings, generating material
"other income". This is **not operating cash flow** and must not be capitalised at an operating
multiple.

```
Value of the core asset management franchise    ← DCF of operating cash flows only
+ Net investments at market value                ← the treasury book, marked to market
= Total equity value
```

The reason this matters: a fee franchise compounding at a high rate deserves a very different
multiple from a bond portfolio yielding single digits. Blending them into one P/E obscures the
thing you are trying to value.

Most people quietly leave other income inside the operating forecast and never notice. Handling it
properly, and saying so in the memo, is a real differentiator.

---

## Comparable Companies

**Listed AMC peers**
- Nippon Life India Asset Management (NSE: NAM-INDIA)
- Aditya Birla Sun Life AMC (NSE: ABSLAMC)
- UTI Asset Management (NSE: UTIAMC)

**Adjacent capital-light financials** (for cross-sector context, clearly labelled as such)
- CAMS and KFin Technologies — the RTAs that service the AMC industry
- CDSL and BSE — market infrastructure

**Unlisted context** — SBI Funds Management, ICICI Prudential AMC and Kotak Mahindra AMC are major
competitors but unlisted. They matter for market-share analysis even though they cannot be comps.

**Global reference** — BlackRock, T. Rowe Price, Amundi, Schroders. Different markets and fee
structures; use only to frame how the market values fee compression versus growth, and label the
comparison as indicative.

### Multiples

| Multiple | Why |
|---|---|
| **Market cap / AUM (%)** | **The dominant AMC multiple**, and the basis on which AMC acquisitions are actually priced. Gives you a direct bridge from trading comps to precedent transactions. |
| P/E | Standard; note it blends the fee franchise with the treasury book |
| EV/EBITDA | Cross-check; net cash means **EV is below market cap** |
| Blended yield (bps) | Not a valuation multiple, but essential context for reading P/AUM |
| Operating profit / AAUM (bps) | Operating efficiency |

**Reading P/AUM correctly:** a manager with a higher equity mix should trade at a higher P/AUM,
because each rupee of its AUM earns more. Never compare P/AUM across peers without also comparing
asset mix and blended yield. A low P/AUM on a liquid-heavy book is not cheap.

---

## Precedent Transactions

Indian AMC M&A is genuinely active, and deals are announced and discussed as a **percentage of
AUM** — which maps directly onto your trading comp metric. This makes the precedent analysis
unusually clean.

Candidates to research from **primary announcements** (verify every figure; mark undisclosed terms
as undisclosed):

- **HSBC AMC / L&T Investment Management** — HSBC's acquisition of L&T Mutual Fund
- **Bandhan consortium / IDFC AMC** — Bandhan Financial Holdings with GIC and ChrysCapital
- **Nippon Life / Reliance Nippon Life AMC** — Nippon's buyout of Reliance Capital's stake
- **Sundaram AMC / Principal AMC** — Principal's India exit
- **Baroda BNP Paribas** — AMC merger
- Global for context: Franklin/Legg Mason, Invesco/Oppenheimer, Morgan Stanley/Eaton Vance,
  Amundi/Lyxor

For each: announced deal value, AUM acquired, implied **% of AUM**, and the acquired book's asset
mix. The mix matters — a deal at 4% of AUM for an equity-heavy book is not comparable to 4% for a
liquid-heavy book.

---

## Merger Model — AMC Consolidation

The portfolio's accretion/dilution model lives here, because AMC consolidation is real and
frequent, so the exercise is grounded rather than hypothetical.

**Suggested pairing:** HDFC AMC acquiring **UTI AMC**. Both are listed with full disclosure, and
the strategic logic is genuine — AUM scale, distribution reach, cost synergies in operations, and
UTI's historically under-monetised franchise (its operating profit as a share of AAUM has lagged).

Build:

1. Standalone forecasts for acquirer and target
2. Offer price, premium, and implied **% of AUM** against the precedents above
3. Consideration mix (cash / stock / debt) as adjustable inputs
4. Goodwill and intangible creation — note that acquired **AMC contracts** may be recognised as
   intangibles with associated amortisation
5. Cost synergies phased over three years, with integration costs, and revenue synergies kept
   separate and conservative
6. **AUM attrition assumption** — critical and specific to this sector: some AUM leaves on a change
   of manager. Assuming zero attrition is not credible.
7. Pro forma EPS accretion/dilution, and **breakeven synergies**

The AUM attrition assumption is what separates a real AMC merger model from a generic one.

---

## Data Sources

| Source | Use |
|---|---|
| HDFC AMC investor relations — annual reports | Primary financials, FY2019 onward (post-IPO) |
| Quarterly investor presentations | **AUM by category, QAAUM, market share, yields.** Essential. |
| **AMFI monthly data** | Industry AUM by category, net flows, SIP data, AMC-wise market share |
| Scheme information documents | TER by scheme — the actual fee rates |
| SEBI circulars | TER regulation, the primary fee-compression risk |
| Peer annual reports and presentations | Comps |

Store filings in `data/`.

> Indian companies do not file with SEC EDGAR. Use the toolkit's **CSV input mode** to run AMC comps
> through the same multiples and statistics engine — see
> [`../04-analyst-toolkit/`](../04-analyst-toolkit/).

---

## Assumptions Log

| Assumption | Base | Bull | Bear | Basis |
|---|---|---|---|---|
| Equity AUM growth — net flows % | | | | |
| Equity AUM growth — market return % | | | | |
| Debt AUM growth % | | | | |
| Liquid AUM growth % | | | | |
| Passive AUM growth % | | | | shifting mix |
| Equity yield (bps) | | | | TER-constrained |
| Debt yield (bps) | | | | |
| Liquid yield (bps) | | | | |
| Passive yield (bps) | | | | structurally low |
| Employee cost growth % | | | | |
| Effective tax rate | | | | |
| **Cost of equity (= WACC, no debt)** | | | | |
| Terminal growth | | | | |
| Treasury book value | | | | marked, for sum-of-parts |
| AUM attrition on merger % | | | | merger model only |

---

## Valuation Summary

| Method | Low | High | Implied ₹/share |
|---|---|---|---|
| 52-week trading range | | | |
| Trading comps — P/AUM | | | |
| Trading comps — P/E | | | |
| Precedent transactions — % of AUM | | | |
| DCF (core franchise) + net investments | | | |
| **Conclusion** | | | |

**Current share price:** _as of date_
**Recommendation:** _to be written_

**The central question:** does growth in Indian mutual fund penetration and SIP flows outrun
structural fee compression from TER regulation and the shift toward passive products?

---

## Limitations

- Forecasts are the author's own estimates, not company guidance. Not investment advice.
- **HDFC AMC cannot realistically be LBO'd** — it is promoter-controlled, and a change of control
  in a regulated AMC requires SEBI approval. The portfolio's LBO therefore uses CAMS instead; see
  the roadmap.
- AUM forecasts embed an implicit equity market return assumption, which is not forecastable with
  confidence. The scenario range is wide for this reason and should be read as such.
- Yields are modelled at category level; actual TER varies scheme by scheme and by direct versus
  regular plan, which is not fully replicated.
- The merger model uses a plausible but hypothetical transaction. AUM attrition on a change of
  manager is an assumption, not an observation.
- Treasury book marked at reported values; a full analysis would look through to the underlying
  security-level portfolio.
