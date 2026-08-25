# 32-Week Build Roadmap

**Commitment:** 1 hour/day, 6 days/week. Day 7 is deliberate buffer — use it to catch up or rest.
**Total:** ~192 hours across ~7.5 months.

> **Compressing to 5–6 months:** do 1.5 hours/day and treat each "week" below as 4 days.
> Do not compress by skipping Phase 1. The CDSL three-statement model is the foundation everything
> else sits on, and rushing it produces a model that looks finished but cannot be defended.

## Phase Overview

| Phase | Weeks | Deliverable |
|---|---|---|
| 0 — Foundations | 1–2 | Filings gathered, standards internalised, historicals spread |
| 1 — CDSL Three-Statement | 3–8 | Integrated operating model |
| 2 — CDSL Valuation | 9–13 | DCF, comps, football field |
| 3 — HDFC AMC | 14–18 | Full model, sum-of-parts DCF, AMC comps |
| 4 — CAMS LBO | 19–22 | Buyout model with returns attribution |
| 5 — Merger Model | 23–25 | HDFC AMC / UTI AMC accretion-dilution |
| 6 — Citigroup FIG | 26–28 | DDM, residual income, P/TBV–ROTE regression |
| 7 — Analyst Toolkit | 29–31 | Python comps automation, extended for Indian data |
| 8 — Capstone | 32 | Investment memo, comparative analysis, packaging |

**Commit at the end of every session.** Even a half-finished tab. Your commit history becomes proof
of sustained effort, and it protects you from losing work.

### Why three companies works

The three subjects deliberately span the financial sector's three revenue architectures:

| Company | Architecture | Toolkit |
|---|---|---|
| **CDSL** | Fee × activity and accounts | Standard DCF |
| **HDFC AMC** | Fee × assets under management | Standard DCF + sum-of-parts |
| **Citigroup** | Spread × own balance sheet | DDM, residual income |

HDFC AMC costs far less than CDSL despite similar depth, because the workbook architecture,
cost-of-equity method and comps process all carry over. The second model is where you find out
whether you learned the first one.

The comparative insight — that each architecture demands a different valuation approach — is the
strongest thing you will be able to say in an interview.

---

# PHASE 0 — FOUNDATIONS (Weeks 1–2)

## Week 1 — CDSL and depository mechanics

Resist opening Excel this week. Analysts who model before understanding the business produce
confident nonsense.

- **Day 1** — Download CDSL annual reports FY2018→latest into `01-cdsl-depository/data/`. Note the fiscal year ends **31 March**, figures are in **₹ crore**, under **Ind AS**.
- **Day 2** — Read the latest annual report's Management Discussion & Analysis end to end. Note what management says drives each revenue line.
- **Day 3** — Download the **NSDL IPO prospectus (DRHP/RHP)**. This is the single best dataset on the Indian depository industry that exists — market share, industry volumes, competitive structure. Read the industry section.
- **Day 4** — Learn the mechanics: dematerialisation, beneficial owner (BO) accounts, depository participants, issuers, settlement. Write down how a trade actually settles through a depository.
- **Day 5** — Map CDSL's revenue lines and classify each as **recurring** or **cyclical**: annual issuer charges, transaction charges, IPO/corporate action, KYC (via CDSL Ventures), e-CAS and e-voting.
- **Day 6** — Read [`docs/fee-business-modelling.md`](docs/fee-business-modelling.md). Then write a one-page summary of how CDSL makes money, in your own words.

## Week 2 — Standards and historical spreading

- **Day 1** — Read [`docs/modeling-standards.md`](docs/modeling-standards.md) and [`templates/model-checklist.md`](templates/model-checklist.md). Set up Excel cell styles before typing a single number.
- **Day 2** — Create `models/cdsl_operating_model.xlsx` with tabs: `Cover`, `Assumptions`, `Drivers`, `IS`, `BS`, `CFS`, `Segments`, `DCF`, `Comps`, `Checks`.
- **Day 3** — Spread historical **income statement** into `IS`, consolidated only. Type from the PDF; do not paste. The typing is how you notice things.
- **Day 4** — Spread historical **balance sheet** into `BS`. Note the large cash and investments balance and the absence of debt.
- **Day 5** — Spread historical **cash flow statement** into `CFS`.
- **Day 6** — Build the `Checks` tab **now**, before forecasting: assets − (liabilities + equity) = 0 for every historical year, and closing cash ties to `CFS`. Fix every discrepancy. If historicals don't tie, the forecast never will.

---

# PHASE 1 — CDSL THREE-STATEMENT MODEL (Weeks 3–8)

## Week 3 — Historical analysis and driver extraction

- **Day 1** — Build the demat (BO) account history on `Drivers` from annual reports and CDSL's monthly business updates.
- **Day 2** — Add issuer count and transaction volume history.
- **Day 3** — Split historical revenue by line on `Segments`. Calculate the **recurring share of total revenue** by year — this number is central to the whole valuation.
- **Day 4** — **Back-solve the implied fee per unit** for each line: issuer revenue ÷ issuers, transaction revenue ÷ volumes, KYC revenue ÷ volumes. This tells you the actual realised pricing, which is more useful than the published tariff.
- **Day 5** — Cost analysis: classify each cost line as fixed or variable, then compute **operating cost per demat account** by year.
- **Day 6** — Margin history: EBITDA, EBIT, net. Write a half-page conclusion on which ratios are stable enough to hold constant and which need a genuine view.

## Week 4 — Revenue forecast

- **Day 1** — Forecast demat account growth. This is the structural growth story — ground it in investor penetration data, not a guess.
- **Day 2** — Forecast issuer count growth.
- **Day 3** — Forecast **transaction volumes**. The hardest and most uncertain input, because it tracks market activity. Make it an explicit scenario driver, not a single point estimate.
- **Day 4** — Forecast KYC volumes, linked to new account openings across the market.
- **Day 5** — Apply fee rates to build forecast revenue by line. **Back-test the driver logic on the last 3 historical years** — if it doesn't reproduce reported revenue within a few percent, your fee assumption is wrong.
- **Day 6** — Build the scenario toggle (Base / Bull / Bear) driving volumes and fee rates via `CHOOSE` or `INDEX`. One switch cell, three input columns.

## Week 5 — Cost forecast and operating leverage

- **Day 1** — Forecast employee cost bottom-up: headcount × average cost, inflation-linked. Do **not** use a percentage of revenue.
- **Day 2** — Forecast technology and connectivity costs. Largely fixed, stepping up with capacity investment.
- **Day 3** — Forecast regulatory, compliance, audit and other operating expenses. Mostly fixed.
- **Day 4** — Assemble forecast EBITDA. Chart **operating cost per demat account** across the forecast — it should trend down as scale builds.
- **Day 5** — Chart forecast EBITDA margin against history. Write two sentences into the tab defending the trajectory. Flat margins mean either a cost-build error or an unstated view on fee compression.
- **Day 6** — Isolate **other income** (treasury/investment returns) on its own line. Do not bury it in operating revenue — you will need it separated for the sum-of-parts later.

## Week 6 — Balance sheet schedules

Capital-light means these are small. Build them anyway for the reps, but don't over-invest.

- **Day 1** — Build the PP&E roll-forward: opening + capex − depreciation = closing.
- **Day 2** — Build the depreciation schedule on existing net block plus new capex.
- **Day 3** — Working capital: forecast receivables off revenue, payables off costs. Minor here, but model it.
- **Day 4** — Tax: effective rate from historicals. Note current versus deferred and don't conflate them.
- **Day 5** — **No debt, so no debt schedule.** Write a note on the `Cover` tab explaining that WACC therefore collapses to cost of equity. Understanding why this is legitimate matters.
- **Day 6** — Forecast dividends. Capital-light businesses with no reinvestment need typically pay out heavily — check the historical payout ratio and carry it forward.

## Week 7 — Integration

The hardest week. Expect it to break repeatedly.

- **Day 1** — Complete forecast `IS` down to net income, including other income and tax.
- **Day 2** — Build forecast `CFS`: net income + depreciation ± ΔWC − capex ± investments ± dividends.
- **Day 3** — Build forecast `BS` assets: cash, investments, receivables, net block.
- **Day 4** — Build forecast `BS` liabilities and equity. Retained earnings = prior RE + net income − dividends.
- **Day 5** — **Make the balance sheet balance.** It won't on the first attempt. Work the discrepancy line by line — a failure means a real cash item is missing, so the error is always informative.
- **Day 6** — Run every item on [`templates/model-checklist.md`](templates/model-checklist.md).

## Week 8 — Stress and finish

- **Day 1** — Flex transaction volumes **down 30%** (bear market). Does the recurring revenue base hold the floor? This is the key structural question about CDSL.
- **Day 2** — Flex fee per debit **down 20%** (a SEBI fee cut). This is the central risk to the thesis — quantify it.
- **Day 3** — Test all three scenarios end to end. Confirm the balance sheet balances in every one.
- **Day 4** — Formatting pass: blue inputs, black formulas, green links, units on every label, no stray hardcodes.
- **Day 5** — Export to PDF into `outputs/`. Write the assumption summary into the project README.
- **Day 6** — **Commit and push.** Deliverable #1 done.

---

# PHASE 2 — CDSL VALUATION (Weeks 9–13)

## Week 9 — Cost of equity

- **Day 1** — Pull the risk-free rate: 10-year Indian government security yield. Record the date.
- **Day 2** — Estimate the India equity risk premium. Document your source — this number is contestable and you should know why.
- **Day 3** — Calculate beta by regressing 2 years of weekly CDSL returns against the Nifty 50. **Expect a high beta** — transaction volumes are market-linked. Explain the economic reason, don't just report the number.
- **Day 4** — Compute cost of equity via CAPM. Sanity check against the earnings yield.
- **Day 5** — Document that **WACC = Ke** because there is no debt. Do not build a weighted calculation with a zero debt weight — that's theatre.
- **Day 6** — Cross-check your Ke against what peers would imply. If it's far off, revisit beta.

## Week 10 — DCF core

- **Day 1** — Build the free cash flow bridge: EBIT × (1 − tax) + D&A − capex − ΔWC. Note that capex is immaterial here, so FCF tracks close to post-tax EBIT.
- **Day 2** — Build discounting with a mid-year convention. Be explicit about the valuation date.
- **Day 3** — Terminal value via **Gordon growth**. Cap perpetuity growth at long-run nominal GDP.
- **Day 4** — Terminal value via **exit multiple** (P/E or EV/EBITDA). Cross-check: what perpetuity growth does your multiple imply?
- **Day 5** — Bridge EV to equity value. **Add back net cash and investments** — remember net cash means EV is *below* market cap. Divide by diluted shares.
- **Day 6** — Compare implied value per share to market price. Write your explanation for the gap — this is your thesis forming.

## Week 11 — Sensitivities

- **Day 1** — Two-way data table: cost of equity vs. terminal growth.
- **Day 2** — Two-way table: **fee per debit vs. transaction volume growth.** These are the real risk axes for CDSL, far more informative than the generic pair.
- **Day 3** — Note what % of total value sits in terminal value. Above ~75% means your DCF is largely a multiple in disguise — say so openly.
- **Day 4** — Run the DCF under all three operating scenarios.
- **Day 5** — Formatting and audit pass on the `DCF` tab.
- **Day 6** — Commit. Write the DCF conclusion into the project README.

## Week 12 — Trading comps

- **Day 1** — Select peers and **justify each in writing**: NSDL (the direct peer), BSE, MCX, CAMS, KFin Technologies. Note NSE is unlisted — verify its current status.
- **Day 2** — Pull market data for each: price, shares outstanding, market cap.
- **Day 3** — Build the EV bridge for each peer. Most are net cash, so **EV will be below market cap** — make sure your formula handles this correctly.
- **Day 4** — Pull revenue, EBITDA and net income for each peer.
- **Day 5** — Calculate multiples: **P/E** (dominant), EV/EBITDA, and **EV per demat account** plus **revenue per account** — the sector-specific metrics that show you understand the business.
- **Day 6** — Handle **calendarisation** for differing fiscal year ends. Add a caveat that NSDL's listed history is short, so its multiple may not yet reflect a settled market view.

## Week 13 — Precedents and football field

- **Day 1** — Research depository M&A and establish the honest finding: **control transactions do not exist in this asset class** because SEBI's Market Infrastructure Institution ownership caps preclude them. Document *why* — this is an insight, not a gap.
- **Day 2** — Research the regulatory-driven stake divestments (BSE reducing its CDSL holding; NSE divesting CAMS). Treat these as **minority** valuation reference points and label them as such — they are forced sales, not control deals.
- **Day 3** — Research global infrastructure deals for context only: LSEG/Refinitiv, ICE/Black Knight, Nasdaq/Adenza, Deutsche Börse/ISS. Different regulatory regimes — use to frame ranges, not as direct precedents.
- **Day 4** — Build the **football field**: 52-week range, trading comps, DCF, with current price marked. State plainly that it carries one fewer methodology than standard, by necessity.
- **Day 5** — Write the valuation conclusion: a defensible range and where in it you land.
- **Day 6** — PDF, commit. **Deliverable #2 done.**

---

# PHASE 3 — HDFC AMC (Weeks 14–18)

Accelerated, because the architecture carries over. This is where you find out whether you learned
Phase 1 or merely followed it.

**Read the AUM mix-shift and sum-of-parts sections of
[`docs/fee-business-modelling.md`](docs/fee-business-modelling.md) again before Day 1.**

## Week 14 — Setup and AUM history

- **Day 1** — Download HDFC AMC annual reports FY2019→latest and the last 8 quarterly investor presentations into `02-hdfc-amc/data/`.
- **Day 2** — Copy the CDSL workbook as a structural template. Rebuild the tab set for an AMC: replace `Drivers` with `AUM`, add `SOTP`.
- **Day 3** — Spread historical `IS`, `BS`, `CFS`. Faster now — you know the process.
- **Day 4** — Build **AUM by category** history from the quarterly presentations and AMFI monthly data: equity, debt, liquid, passive.
- **Day 5** — **Decompose historical AUM growth into net flows vs. market appreciation.** The single most important analytical step in asset management — it separates franchise performance from market beta.
- **Day 6** — **Back-solve implied yield by category**: segment revenue ÷ segment AAUM × 10,000 = bps. Chart the trend. This is where you see fee compression directly.

## Week 15 — Revenue forecast

- **Day 1** — Forecast equity AUM, splitting net flows and assumed market return as separate inputs.
- **Day 2** — Forecast debt and liquid AUM.
- **Day 3** — Forecast passive/ETF AUM. This is the mix shift — passive grows faster but earns a fraction of the yield.
- **Day 4** — Set yield assumptions by category. State your view on TER-driven compression explicitly in the assumptions log.
- **Day 5** — Compute **average** AUM (AAUM) — revenue accrues on the average, not the closing balance. Then build revenue by category.
- **Day 6** — Chart implied **blended yield** across the forecast. Mix shift should visibly move it even where individual rates are flat. If it doesn't, your category split isn't working.

## Week 16 — Costs and operating leverage

- **Day 1** — Forecast employee cost bottom-up — the largest line.
- **Day 2** — Forecast fees and commission. The one line that partly scales with the asset base.
- **Day 3** — Forecast advertising, business promotion and other operating expenses.
- **Day 4** — Chart **operating profit as a percentage of AAUM (bps)** against history. The standard AMC efficiency measure.
- **Day 5** — Isolate **other income** from the treasury book on its own line, entirely outside operating profit. You will value it separately.
- **Day 6** — Complete the forecast income statement.

## Week 17 — Integration and sum-of-parts DCF

- **Day 1** — Build forecast `CFS` and `BS`. Make the balance sheet balance.
- **Day 2** — Cost of equity: reuse your Week 9 method. Note that beta is high because AUM tracks markets directly.
- **Day 3** — DCF the **core franchise only** — operating cash flows, excluding all treasury income.
- **Day 4** — Value the **treasury book separately** at marked value.
- **Day 5** — Assemble the **sum-of-parts**: core franchise DCF + net investments = equity value. Divide by diluted shares.
- **Day 6** — Sensitivity on the two-sided thesis: **yield compression vs. AUM growth.** This grid *is* the investment debate.

## Week 18 — AMC comps and finish

- **Day 1** — Peer set with written justification: Nippon Life India AMC, Aditya Birla Sun Life AMC, UTI AMC. Note the large unlisted competitors (SBI, ICICI Prudential, Kotak) matter for market share even though they can't be comps.
- **Day 2** — Compute **market cap / AUM (%)** for each peer — the dominant AMC multiple.
- **Day 3** — Compute blended yield and asset mix for each peer. **You cannot interpret P/AUM without these** — a low P/AUM on a liquid-heavy book is not cheap.
- **Day 4** — Compute P/E and EV/EBITDA as cross-checks.
- **Day 5** — Research precedents as **% of AUM**: HSBC/L&T Investment Management, Bandhan consortium/IDFC AMC, Nippon/Reliance Nippon Life AMC, Sundaram/Principal. Verify every figure from primary announcements and record the acquired book's asset mix.
- **Day 6** — Valuation conclusion, football field, PDF, commit. **Deliverable #3 done.**

---

# PHASE 4 — CAMS LBO (Weeks 19–22)

## Week 19 — Why CAMS, and a lean model

- **Day 1** — Write down **why CAMS is the realistic LBO target** and CDSL and HDFC AMC are not: CAMS is a registrar and transfer agent, not a Market Infrastructure Institution, so it isn't subject to SEBI's MII ownership caps — and it has a genuine private equity ownership history. Recognising which businesses can actually be bought is exactly the judgement an IB analyst needs.
- **Day 2** — Download CAMS annual reports. Understand RTA economics: fees on the AUM it services, duopoly with KFin Technologies.
- **Day 3** — Build a **lean** three-statement model. Simplified — you have the muscle memory now, and the LBO only needs credible cash flows.
- **Day 4** — Forecast revenue: AAUM serviced × yield in bps, plus non-MF service lines.
- **Day 5** — Forecast costs and EBITDA.
- **Day 6** — Derive free cash flow before financing — the input the LBO consumes.

## Week 20 — Transaction structure

- **Day 1** — Set entry assumptions: offer price per share, premium to market, entry EV/EBITDA.
- **Day 2** — Build **Sources & Uses**. Uses: equity purchase price, refinanced debt, fees. Sources: revolver, term loans, mezzanine, sponsor equity. They must foot exactly.
- **Day 3** — Set the capital structure: leverage in turns of EBITDA, tranche sizing, pricing spreads, tenors. Note that Indian leveraged finance markets support less leverage than US markets — reflect that rather than importing US assumptions.
- **Day 4** — Build purchase price allocation and goodwill.
- **Day 5** — Construct the pro forma opening balance sheet at close.
- **Day 6** — Verify the pro forma balance sheet balances. Add to `Checks`.

## Week 21 — Debt schedule and cash sweep

- **Day 1** — Lay out the debt schedule grid: one row block per tranche, columns by forecast year.
- **Day 2** — Add mandatory amortisation on the term loans.
- **Day 3** — Build cash flow available for debt service: EBITDA − cash interest − taxes − capex − ΔWC.
- **Day 4** — Build the **cash sweep waterfall**: revolver first, then term loans in priority order, subject to a minimum cash balance. The mechanical heart of an LBO.
- **Day 5** — Calculate interest on average balances and resolve the circularity with your documented breaker toggle.
- **Day 6** — Build credit statistics by year: total and net leverage, interest coverage, FCCR.

## Week 22 — Returns

- **Day 1** — Set exit assumptions. **Default exit multiple = entry multiple** — assuming expansion is how amateurs manufacture returns.
- **Day 2** — Compute exit EV, subtract net debt at exit, derive exit equity value.
- **Day 3** — Compute **IRR** and **MoIC** across 3/4/5-year horizons.
- **Day 4** — Sensitivity grids: entry vs. exit multiple, and leverage vs. EBITDA growth.
- **Day 5** — Build the **returns attribution**: decompose IRR into EBITDA growth, multiple change, and debt paydown. Exactly how sponsors discuss a deal.
- **Day 6** — Solve for maximum supportable price at a 20% IRR hurdle. PDF, commit. **Deliverable #4 done.**

---

# PHASE 5 — MERGER MODEL (Weeks 23–25)

HDFC AMC acquiring **UTI AMC**. Both listed with full disclosure, and the strategic logic is real:
AUM scale, distribution reach, operational cost synergies, and UTI's historically under-monetised
franchise.

## Week 23 — Setup

- **Day 1** — Write the strategic rationale. Why would HDFC AMC want UTI, and what does UTI's operating profit as a share of AAUM suggest about the opportunity?
- **Day 2** — Standalone acquirer forecast — reuse your HDFC AMC model.
- **Day 3** — Standalone target forecast. Pull UTI AMC financials and AUM by category.
- **Day 4** — Set offer price and premium. Compute the implied **% of AUM** and compare against your Week 18 precedents.
- **Day 5** — Set consideration mix (cash / stock / debt) as adjustable input percentages.
- **Day 6** — Build sources & uses, including financing and advisory fees.

## Week 24 — Pro forma

- **Day 1** — Compute goodwill and intangibles. Note that acquired **AMC contracts** may be recognised as intangibles with associated amortisation.
- **Day 2** — Combine the income statements line by line.
- **Day 3** — Layer in cost synergies phased over 3 years, with one-time integration costs. Keep revenue synergies separate and conservative.
- **Day 4** — Model **AUM attrition on change of manager.** Some assets leave when the manager changes. Assuming zero attrition is not credible, and this assumption is what separates a real AMC merger model from a generic one.
- **Day 5** — Add financing effects: new interest expense, and forgone interest income on cash used.
- **Day 6** — Compute pro forma net income and pro forma diluted shares including new stock issued.

## Week 25 — Analysis

- **Day 1** — Compute **EPS accretion/dilution** in ₹ and %, by year.
- **Day 2** — Solve for **breakeven synergies** — where EPS is exactly neutral. Goal seek, then hardcode the logic.
- **Day 3** — Sensitivity: offer premium vs. synergy level, and **AUM attrition vs. synergies** — the sector-specific grid.
- **Day 4** — Sensitivity on consideration mix: how does accretion shift from all-cash to all-stock, and why?
- **Day 5** — Write the recommendation: do the deal, at what price, with what structure?
- **Day 6** — PDF, checklist, commit. **Deliverable #5 done.**

---

# PHASE 6 — CITIGROUP FIG (Weeks 26–28)

**Read [`docs/bank-valuation-primer.md`](docs/bank-valuation-primer.md) before Day 1.** Everything
from Phases 1–5 about unlevered FCF, EV multiples and LBOs is **inapplicable here**, and
understanding why is the point of this project.

## Week 26 — Understanding the bank

- **Day 1** — Download Citigroup's latest 10-K and last four 10-Qs into `03-citigroup-fig/data/`. Note the **calendar** fiscal year and **US$ millions**.
- **Day 2** — Map the segments: Services, Markets, Banking, Wealth, US Personal Banking, All Other. Record revenue and net income for each.
- **Day 3** — Build the bank balance sheet view: earning assets, loans by category, deposits by type, funding mix.
- **Day 4** — Decompose **net interest margin**: yield on earning assets − cost of funds, across 8 quarters.
- **Day 5** — Analyse credit: provisions, net charge-off rate, allowance for credit losses as % of loans, non-performing loans.
- **Day 6** — Pull the capital stack: **CET1 ratio**, RWA, RWA density, supplementary leverage ratio, GSIB surcharge.

## Week 27 — Building the valuation

- **Day 1** — Compute **tangible book value**: equity − goodwill − intangibles − preferred. Then TBV per share.
- **Day 2** — Compute **ROTCE** by quarter and year. Compare against management's medium-term target.
- **Day 3** — Build a simplified 5-year forecast, **balance sheet first**: NII from loan growth and NIM, fee revenue, expenses via efficiency ratio, credit costs.
- **Day 4** — Build the **Dividend Discount Model**, with dividends constrained by the CET1 requirement rather than a flat payout assumption.
- **Day 5** — Build the **Residual Income model**: RI = (ROTE − Ke) × tangible book. Note that when ROTE < Ke the model returns a value *below* book — mathematically, not as an error. That is the entire Citi debate.
- **Day 6** — Reconcile the two models. If they diverge sharply, find your inconsistent assumption.

## Week 28 — Peer regression and conclusion

- **Day 1** — Peer set: JPMorgan, Bank of America, Wells Fargo, Goldman Sachs, Morgan Stanley. Pull P/TBV and ROTE for each. Note GS and MS have very different business mixes — flag it rather than ignoring it.
- **Day 2** — Run the **regression of P/TBV on ROTE**. The empirical backbone of bank relative valuation.
- **Day 3** — Plot Citi against the fitted line. Is the discount explained by low ROTE, or is there unexplained residual?
- **Day 4** — Compute the value uplift if Citi closed its ROTE gap to the peer median. This quantifies the restructuring thesis.
- **Day 5** — Write the conclusion: is the discount to tangible book an opportunity, or a fair reflection of sub-cost-of-equity returns?
- **Day 6** — PDF, commit. **Deliverable #6 done.**

---

# PHASE 7 — ANALYST TOOLKIT (Weeks 29–31)

The package in `04-analyst-toolkit/` already runs offline against bundled fixtures. Your job is to
make it work against live EDGAR data and extend it to serve the Indian projects.

## Week 29 — Get it running live

- **Day 1** — Read through the package: `edgar.py`, `normalize.py`, `multiples.py`, `comps.py`, `excel_export.py`, `cli.py`. Run the test suite.
- **Day 2** — Run `comps --offline` and trace how data flows from fixture to output table.
- **Day 3** — Set `SEC_USER_AGENT` (the SEC requires a real contact string) and make one live call for a single ticker.
- **Day 4** — Run the full Citi peer set live. Expect gaps and failures — that's the real problem to solve.
- **Day 5** — Debug the tag failures. Extend the candidate tag lists in `normalize.py` until coverage is complete.
- **Day 6** — Add caching so you aren't re-hitting EDGAR on every run.

## Week 30 — Extend for the Indian projects

Indian companies don't file with EDGAR, so this is where the CSV input path earns its keep.

- **Day 1** — Run `comps --input-csv` using the bundled template. Trace how manual data flows through the same multiples engine.
- **Day 2** — Build the CDSL peer CSV from annual reports: NSDL, BSE, MCX, CAMS, KFin.
- **Day 3** — Build the AMC peer CSV and add **P/AUM** as a computed metric in `multiples.py`.
- **Day 4** — Add **EV per demat account** as a computed metric.
- **Day 5** — Wire outlier flagging and summary statistics into your own comps outputs.
- **Day 6** — Write tests for every new calculation. Cover zero denominators, missing data, negative values.

## Week 31 — Polish

- **Day 1** — Improve the Excel exporter: number formats, column widths, header styling.
- **Day 2** — Add `--as-of` so you can pull historical comps rather than only current.
- **Day 3** — Update the toolkit README: what it does, how to run it, and what the XBRL normalisation problem actually is.
- **Day 4** — Add clear error handling for rate limits, missing tickers and malformed CSVs.
- **Day 5** — Final cleanup. Run the full test suite.
- **Day 6** — Commit. **Deliverable #7 done.**

---

# PHASE 8 — CAPSTONE (Week 32)

Draft incrementally rather than all at once — you have been forming these views since Week 10.

- **Day 1** — Choose your primary pitch subject (CDSL or HDFC AMC). Write the executive summary and thesis: 3 bullets, recommendation, target price. Use [`templates/investment-memo-template.md`](templates/investment-memo-template.md).
- **Day 2** — Write the business overview and industry/competitive positioning.
- **Day 3** — Write the valuation section, pulling in your football field and DCF.
- **Day 4** — Write catalysts and **risks — including what would prove you wrong.** For both Indian names the core risk is regulated fee compression. Interviewers probe this hardest.
- **Day 5** — Write the **comparative section**: three companies, three revenue architectures, two valuation toolkits, and why the differences are structural rather than cosmetic. This is the most distinctive thing in your portfolio — most candidates have one model and no comparative view.
- **Day 6** — Rehearse the pitch aloud at 90 seconds, then 30. Final portfolio pass: update the top-level README, verify every PDF renders and every link resolves, push everything.

---

## Interview Readiness Checkpoints

Test yourself at these milestones. If you can't answer from memory, revisit.

| After | You should be able to answer |
|---|---|
| Week 8 | Walk me through how ₹10 of depreciation flows through all three statements. |
| Week 8 | This company's revenue is half recurring — why does that matter for valuation? |
| Week 11 | Walk me through a DCF. Why unlevered cash flow? Why is the discount rate just Ke here? |
| Week 12 | Why is this company's enterprise value below its market cap? |
| Week 13 | Which valuation methodology gives the highest value, and why? |
| Week 16 | An AMC's AUM grew 20% — is that good? (Flows or market?) |
| Week 17 | How do you value a company with a large investment portfolio? |
| Week 18 | Why do asset managers trade on a percentage of AUM? |
| Week 22 | Walk me through an LBO. What drives returns? Why can't you LBO CDSL? |
| Week 25 | An all-stock deal — when is it accretive? |
| Week 28 | Why can't you use EV/EBITDA on a bank? Why do banks trade below book? |
| Week 32 | Pitch me a stock. (90 seconds, no notes.) |

## A Note on Priorities

This portfolio gets you interviews at valuation, equity research, FP&A, credit and corporate
development roles, and gives you substantive material for IB conversations.

But for investment banking specifically, **networking converts better than any portfolio.** Alumni
coffee chats and informational calls get you the interview; this work makes those conversations
credible and closes the technical screen once you're in the room. Spend time on both from week one.

Do not let building become a way to postpone reaching out to people.
