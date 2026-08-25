# 28-Week Build Roadmap

**Commitment:** 1 hour/day, 6 days/week. Day 7 is deliberate buffer — use it to catch up or rest.
**Total:** ~168 hours across ~7 months.

> **Compressing to 5 months:** do 1.5 hours/day and treat each "week" below as 4 days instead of 6.
> Do not compress by skipping Phase 1. The three-statement model is the foundation everything
> else sits on, and rushing it produces a model that looks finished but cannot be defended.

## Phase Overview

| Phase | Weeks | Deliverable |
|---|---|---|
| 0 — Foundations | 1–2 | Data gathered, standards internalised, historicals spread |
| 1 — Three-Statement Model | 3–9 | Integrated operating model, UltraTech |
| 2 — Valuation | 10–14 | DCF, WACC, comps, precedents, football field |
| 3 — LBO | 15–18 | Full buyout model with returns attribution |
| 4 — Merger Model | 19–21 | Accretion/dilution with breakeven synergies |
| 5 — Citigroup FIG | 22–24 | DDM, residual income, P/TBV–ROTE regression |
| 6 — Analyst Toolkit | 25–27 | Python comps automation |
| 7 — Capstone | 28 | Investment memo, portfolio packaging |

**Commit at the end of every single session.** Even a half-finished tab. Your commit history becomes
proof of sustained effort, which is itself a signal — and it protects you from losing work.

---

# PHASE 0 — FOUNDATIONS (Weeks 1–2)

## Week 1 — Source documents and industry mechanics

Resist the urge to open Excel this week. Analysts who model before they understand the business
produce confident nonsense.

- **Day 1** — Download UltraTech annual reports FY2016→latest from the investor relations site into `01-ultratech-cement/data/`. Note the fiscal year ends **31 March** and figures are in **₹ crore** under **Ind AS**.
- **Day 2** — Read the latest annual report's Management Discussion & Analysis end to end. Take notes on what management says drives volume and pricing. Don't skim.
- **Day 3** — Download the last 8 quarterly investor presentations. These contain per-tonne operating metrics that the annual report buries.
- **Day 4** — Learn the cement cost stack: **power & fuel** (petcoke/coal), **freight** (cement is heavy and low value-to-weight, so lead distance dominates), **raw materials** (limestone, fly ash, slag), employee, and other overheads. Write down each as a % of revenue from the latest filing.
- **Day 5** — Learn the industry KPIs: **capacity (MTPA)**, **utilisation %**, **realisation per tonne**, **EBITDA per tonne**. EBITDA/tonne is how the entire sector is discussed — internalise it.
- **Day 6** — Understand blended vs. OPC cement mix, and integrated plants vs. standalone grinding units. Write a one-page summary of how UltraTech makes money, in your own words.

## Week 2 — Standards and historical spreading

- **Day 1** — Read [`docs/modeling-standards.md`](docs/modeling-standards.md) and [`templates/model-checklist.md`](templates/model-checklist.md). Set up your Excel with the cell styles defined there before typing a single number.
- **Day 2** — Create `models/ultratech_operating_model.xlsx` with empty tabs: `Cover`, `Assumptions`, `IS`, `BS`, `CFS`, `WC`, `PPE`, `Debt`, `DCF`, `Comps`, `Checks`.
- **Day 3** — Spread 8 years of historical **income statement** into `IS`, consolidated figures only. Type from the PDF; do not paste. The typing is how you notice things.
- **Day 4** — Spread 8 years of historical **balance sheet** into `BS`.
- **Day 5** — Spread 8 years of historical **cash flow statement** into `CFS`.
- **Day 6** — Build the `Checks` tab now, before forecasting: assets − (liabilities + equity) = 0 for every historical year, and closing cash on `BS` ties to `CFS`. Fix every discrepancy. If historicals don't tie, your forecast never will.

---

# PHASE 1 — THREE-STATEMENT MODEL (Weeks 3–9)

## Week 3 — Historical ratio analysis

- **Day 1** — Calculate historical growth: revenue, volume, realisation/tonne, year over year.
- **Day 2** — Calculate margin history: gross, EBITDA, EBIT, net. Chart them.
- **Day 3** — Calculate **EBITDA per tonne** by year. Overlay against petcoke prices if you can find a series. This is the single most revealing chart in cement.
- **Day 4** — Calculate working capital ratios: **DSO** (receivables/revenue × 365), **DIO** (inventory/COGS × 365), **DPO** (payables/COGS × 365).
- **Day 5** — Calculate returns and leverage: ROE, ROCE, net debt/EBITDA, interest coverage.
- **Day 6** — Write a half-page conclusion: which of these ratios are stable enough to forecast by holding constant, and which are genuinely cyclical and need a view? This decision *is* the forecast.

## Week 4 — Revenue build

- **Day 1** — On `Assumptions`, lay out the capacity schedule: current grey cement capacity in MTPA plus announced expansions with commissioning dates from the investor presentations.
- **Day 2** — Build the forecast driver chain: **Capacity × Utilisation % = Volume (mt)**.
- **Day 3** — Add **Volume × Realisation per tonne = Revenue**. Make realisation growth an explicit input cell, not a formula.
- **Day 4** — Sanity check: back-test your driver logic on the last 3 historical years. Does it reproduce actual reported revenue within ~2%? If not, your capacity or realisation basis is wrong.
- **Day 5** — Build 5-year forecast revenue. Set utilisation and realisation assumptions you can *defend out loud*.
- **Day 6** — Add a scenario toggle (Base / Bull / Bear) driving utilisation and realisation via `CHOOSE` or `INDEX`. One switch cell, three columns of inputs.

## Week 5 — Cost build and EBITDA

- **Day 1** — Forecast power & fuel cost per tonne. This is your most volatile line — link it to a fuel price assumption.
- **Day 2** — Forecast freight cost per tonne. Note it scales with volume and lead distance, not revenue.
- **Day 3** — Forecast raw material cost per tonne.
- **Day 4** — Forecast employee costs and other expenses. These are largely fixed — grow with inflation, not volume. Getting this right is what creates realistic operating leverage.
- **Day 5** — Assemble forecast EBITDA. Calculate implied **EBITDA per tonne** and compare against history. If it's outside the historical range, justify why or revise.
- **Day 6** — Chart forecast EBITDA margin against 8 years of history. Defend the trajectory in two sentences written into the tab.

## Week 6 — PP&E and depreciation schedule

- **Day 1** — Build the `PPE` roll-forward skeleton: opening gross block + capex − disposals = closing gross block.
- **Day 2** — Forecast maintenance capex as a % of revenue, from historical average.
- **Day 3** — Forecast growth capex explicitly, tied to the capacity expansions from Week 4 Day 1. Use an approximate ₹ crore per MTPA cost from management commentary.
- **Day 4** — Build the depreciation waterfall: depreciate existing net block over remaining useful life, and each year's new capex over its own asset life.
- **Day 5** — Link depreciation into `IS` and accumulated depreciation into `BS`.
- **Day 6** — Verify: closing net block = opening net block + capex − depreciation. Add this as a row on `Checks`.

## Week 7 — Working capital and debt schedules

- **Day 1** — Build the `WC` tab: forecast receivables, inventory and payables from your DSO/DIO/DPO assumptions.
- **Day 2** — Calculate change in working capital and link it into `CFS`.
- **Day 3** — Build the `Debt` tab: opening balance, drawdowns, scheduled repayments, closing balance for each facility.
- **Day 4** — Calculate interest expense on **average** balance, not closing. Understand that this creates a circular reference (interest → net income → cash → debt → interest).
- **Day 5** — Resolve the circularity properly: add a documented `Circ_Breaker` toggle cell that switches interest to a hardcoded prior-iteration value, and enable iterative calculation. Document the toggle on the `Cover` tab.
- **Day 6** — Forecast the tax line using an effective tax rate from historicals. Note current vs. deferred tax and don't conflate them.

## Week 8 — Integration

This is the hardest week. Expect it to break repeatedly.

- **Day 1** — Complete the forecast `IS` down to net income.
- **Day 2** — Build forecast `CFS`: net income + depreciation ± ΔWC − capex ± financing = net change in cash.
- **Day 3** — Build forecast `BS` assets, linking cash from `CFS` and net block from `PPE`.
- **Day 4** — Build forecast `BS` liabilities and equity. Retained earnings = prior RE + net income − dividends.
- **Day 5** — **Make the balance sheet balance.** It will not, on the first attempt. Work through the discrepancy line by line — a balance sheet that fails to balance means a real cash flow item is missing, so the error is always informative.
- **Day 6** — Run every item on `templates/model-checklist.md`. Fix everything it surfaces.

## Week 9 — Stress and finish

- **Day 1** — Flex utilisation down 10 percentage points. Does the model behave sensibly, or does something break?
- **Day 2** — Flex fuel cost up 30%. Check that EBITDA/tonne compresses realistically.
- **Day 3** — Test all three scenario toggles end to end. Confirm the balance sheet balances in every one.
- **Day 4** — Formatting pass: blue inputs, black formulas, consistent units, labelled headers, no stray hardcodes.
- **Day 5** — Export to PDF into `01-ultratech-cement/outputs/`. Write the model's assumption summary into the project README.
- **Day 6** — **Commit and push.** Flagship deliverable #1 is done.

---

# PHASE 2 — VALUATION (Weeks 10–14)

## Week 10 — WACC

- **Day 1** — Pull the risk-free rate: 10-year Indian government security yield. Record the date you pulled it.
- **Day 2** — Estimate equity risk premium for India. Document your source and reasoning — this number is contestable and you should know why.
- **Day 3** — Calculate beta by regressing 2 years of weekly UltraTech returns against the Nifty 50. Then compare to peer betas and decide whether to use raw, adjusted, or peer-median.
- **Day 4** — Compute cost of equity via CAPM. Sanity check it against the earnings yield — if Ke is below the earnings yield, question your inputs.
- **Day 5** — Compute after-tax cost of debt from actual interest expense over average debt, times (1 − tax rate).
- **Day 6** — Build WACC using **market-value** weights, not book. Market cap for equity, book as a proxy for debt.

## Week 11 — DCF core

- **Day 1** — Bridge from EBIT to **unlevered free cash flow**: EBIT × (1 − tax) + D&A − capex − ΔWC. Note that interest is deliberately excluded.
- **Day 2** — Build the discounting: mid-year convention discount factors, and be explicit about your valuation date.
- **Day 3** — Terminal value via **Gordon growth**. Cap perpetuity growth at long-run nominal GDP — anything higher implies the company eventually becomes the whole economy.
- **Day 4** — Terminal value via **exit multiple** (EV/EBITDA). Cross-check: what perpetuity growth rate does your exit multiple imply? If it's 8%, your multiple is too high.
- **Day 5** — Sum to enterprise value, then bridge to equity value: − net debt, − minority interest, + investments in associates. Divide by diluted shares.
- **Day 6** — Compare implied value per share to the current market price. Write down your explanation for the gap — this is your thesis forming.

## Week 12 — Sensitivity and DCF finish

- **Day 1** — Build a two-way data table: WACC vs. terminal growth.
- **Day 2** — Build a second: EBITDA margin vs. realisation growth.
- **Day 3** — Note what % of your total DCF value sits in the terminal value. If it's above ~75%, say so openly — it's normal but it means your DCF is mostly a multiple in disguise.
- **Day 4** — Run the DCF under all three operating scenarios.
- **Day 5** — Formatting and audit pass on the `DCF` tab.
- **Day 6** — Commit. Write your DCF conclusion into the project README.

## Week 13 — Trading comps

- **Day 1** — Select the peer set and *justify each inclusion in writing*: Shree Cement, Ambuja Cements, ACC, Dalmia Bharat, JK Cement, Ramco Cements, and consider Birla Corp, Nuvoco Vistas, JK Lakshmi.
- **Day 2** — Pull market data for each: share price, shares outstanding, market cap.
- **Day 3** — Build the enterprise value bridge for each peer: market cap + total debt − cash + minority interest + preferred.
- **Day 4** — Pull each peer's revenue, EBITDA, EBIT, net income and **capacity in MTPA**.
- **Day 5** — Calculate multiples: EV/EBITDA, EV/Revenue, P/E, and the cement-specific **EV per tonne of capacity** — a valuation metric unique to the sector and a strong signal you understand it.
- **Day 6** — Handle **calendarisation**. UltraTech's year ends 31 March; some peers differ. Adjust to a common period or your comps are comparing different economic years.

## Week 14 — Precedents and football field

- **Day 1** — Identify Indian cement M&A precedents. Strong candidates to research and verify from primary announcements: Adani/Holcim (Ambuja + ACC, 2022), UltraTech/Jaiprakash cement assets (2017), UltraTech/Binani (2018, via insolvency), UltraTech/Kesoram (2024), Ambuja/Sanghi (2023), Ambuja/Penna (2024), Dalmia/Murli. **Verify every figure against the announcement — do not trust secondary summaries.**
- **Day 2** — For each deal, record announced EV, target capacity, and compute **EV per tonne**. Mark undisclosed terms as undisclosed rather than estimating.
- **Day 3** — Calculate the transaction multiple range and note the control premium versus trading comps.
- **Day 4** — Build the **football field chart**: horizontal bars for 52-week range, trading comps range, precedent transactions range, and DCF range, with the current share price as a vertical line.
- **Day 5** — Write your valuation conclusion: a defensible value *range*, and where in it you land and why.
- **Day 6** — Export all outputs to PDF. Commit. **Flagship deliverable #2 done.**

---

# PHASE 3 — LBO (Weeks 15–18)

## Week 15 — Transaction structure

- **Day 1** — Set the entry assumptions: offer price per share, premium to market, entry EV/EBITDA.
- **Day 2** — Build the **Sources & Uses** table. Uses: equity purchase price, refinanced debt, fees. Sources: revolver, term loans, mezzanine, sponsor equity. They must foot to each other exactly.
- **Day 3** — Set the capital structure: leverage as a turn of EBITDA, tranche sizing, pricing spreads, tenors.
- **Day 4** — Build purchase price allocation and **goodwill**: purchase equity value − book equity + write-ups.
- **Day 5** — Construct the pro forma opening balance sheet at close.
- **Day 6** — Verify the pro forma balance sheet balances. Add to `Checks`.

## Week 16 — Debt schedule and cash sweep

- **Day 1** — Lay out the debt schedule grid: one row block per tranche, columns for each forecast year.
- **Day 2** — Add mandatory amortisation on the term loans.
- **Day 3** — Build **cash flow available for debt service**: EBITDA − cash interest − taxes − capex − ΔWC.
- **Day 4** — Build the **cash sweep** waterfall: repay revolver first, then term loans in priority order, subject to a minimum cash balance. This is the mechanical heart of an LBO.
- **Day 5** — Calculate interest on average balances and resolve the resulting circularity with your documented toggle.
- **Day 6** — Build the credit statistics block by year: total leverage, net leverage, interest coverage, FCCR.

## Week 17 — Returns

- **Day 1** — Set exit assumptions. **Default to exit multiple = entry multiple** — assuming expansion is how amateurs manufacture returns.
- **Day 2** — Calculate exit EV, subtract net debt at exit, derive exit equity value.
- **Day 3** — Compute **IRR** and **MoIC** across a 3/4/5-year exit horizon.
- **Day 4** — Build a returns sensitivity grid: entry multiple vs. exit multiple, and leverage vs. EBITDA growth.
- **Day 5** — Build the **returns attribution**: decompose total IRR into EBITDA growth, multiple expansion/contraction, and debt paydown. This decomposition is exactly how sponsors discuss a deal.
- **Day 6** — Solve for the maximum price supportable at a 20% IRR hurdle — the "how high can we go" question.

## Week 18 — LBO finish

- **Day 1** — Add a management equity incentive pool and see how it dilutes sponsor returns.
- **Day 2** — Stress test: what EBITDA decline breaches your interest coverage covenant?
- **Day 3** — Run the downside case. Does the capital structure survive it?
- **Day 4** — Full checklist and formatting pass.
- **Day 5** — Write the limitations note: UltraTech is promoter-controlled and this buyout is not realistic. State that plainly — it demonstrates judgement, not weakness.
- **Day 6** — Export PDF, commit. **Flagship deliverable #3 done.**

---

# PHASE 4 — MERGER MODEL (Weeks 19–21)

## Week 19 — Setup

- **Day 1** — Choose an acquirer/target pair with strategic logic. A regional consolidation play works well — a large player acquiring a sub-scale regional producer for freight-radius synergies.
- **Day 2** — Build a simplified standalone forecast for the acquirer.
- **Day 3** — Build a simplified standalone forecast for the target.
- **Day 4** — Set offer price and premium; compute the transaction multiples.
- **Day 5** — Set the consideration mix: cash / stock / new debt, as adjustable input percentages.
- **Day 6** — Build sources & uses, including financing fees.

## Week 20 — Pro forma

- **Day 1** — Compute goodwill and the intangible write-up; note incremental amortisation.
- **Day 2** — Combine the income statements line by line.
- **Day 3** — Layer in synergies: cost synergies phased over 3 years, with one-time integration costs. Be conservative and separate revenue synergies out — most acquirers overpromise them.
- **Day 4** — Add financing effects: new interest expense, and forgone interest income on cash used.
- **Day 5** — Compute pro forma net income and pro forma diluted shares (including new shares issued).
- **Day 6** — Compute **EPS accretion/dilution** in ₹ and %, per year.

## Week 21 — Analysis

- **Day 1** — Solve for **breakeven synergies** — the synergy level at which EPS is exactly neutral. Use goal seek, then hardcode the logic.
- **Day 2** — Build a sensitivity table: offer premium vs. synergy level, output = year-1 accretion.
- **Day 3** — Sensitivity on consideration mix: how does accretion shift from all-cash to all-stock, and why?
- **Day 4** — Compute the pro forma credit profile: combined leverage and coverage. Would the acquirer keep its rating?
- **Day 5** — Write the recommendation: should they do this deal, at what price, with what structure?
- **Day 6** — PDF, checklist, commit. **Flagship deliverable #4 done.**

---

# PHASE 5 — CITIGROUP FIG VALUATION (Weeks 22–24)

Read [`docs/bank-valuation-primer.md`](docs/bank-valuation-primer.md) before Day 1. Everything you
learned in Phases 1–4 about EV/EBITDA, unlevered FCF and LBOs is **inapplicable here**, and
understanding *why* is the point of this project.

## Week 22 — Understanding the bank

- **Day 1** — Download Citigroup's latest 10-K and last four 10-Qs into `02-citigroup-fig/data/`. Note the fiscal year is **calendar**, and figures are in **US$ millions**.
- **Day 2** — Map the segment structure: Services, Markets, Banking, Wealth, US Personal Banking, and All Other. Record revenue and net income by segment.
- **Day 3** — Build the balance sheet view a bank analyst actually uses: earning assets, loans by category, deposits by type, and the funding mix.
- **Day 4** — Decompose **net interest margin**: yield on earning assets − cost of funds. Track it over 8 quarters.
- **Day 5** — Analyse credit: provisions, net charge-off rate, allowance for credit losses as a % of loans, and non-performing loans.
- **Day 6** — Pull the capital stack: **CET1 ratio**, risk-weighted assets, RWA density (RWA/total assets), supplementary leverage ratio, and the GSIB surcharge.

## Week 23 — Building the valuation

- **Day 1** — Compute **tangible book value**: total equity − goodwill − intangibles − preferred. Then TBV per share.
- **Day 2** — Compute **ROTCE** by quarter and full year. Compare against management's stated medium-term target.
- **Day 3** — Forecast a simplified 5-year path: NII from loan growth and NIM, fee revenue, expenses via the efficiency ratio, and credit costs.
- **Day 4** — Build the **Dividend Discount Model**: forecast dividends constrained by the CET1 requirement, discount at cost of equity, add terminal value.
- **Day 5** — Build the **Residual Income model**: RI = (ROTE − Ke) × tangible book. Value = TBV + PV of residual income. Note that when ROTE < Ke, the bank is mathematically worth *less* than book — which is the entire Citi debate.
- **Day 6** — Reconcile the two. They should be directionally consistent; if they aren't, find your inconsistent assumption.

## Week 24 — Peer regression and conclusion

- **Day 1** — Build the peer set: JPMorgan, Bank of America, Wells Fargo, Goldman Sachs, Morgan Stanley. Pull P/TBV and ROTE for each.
- **Day 2** — Run a **regression of P/TBV against ROTE** across the peer set. This relationship is the core of bank relative valuation.
- **Day 3** — Plot Citi against the regression line. Is the discount explained by low ROTE, or is there unexplained residual discount?
- **Day 4** — Compute the value uplift if Citi closed its ROTE gap to the peer median. This quantifies the restructuring thesis.
- **Day 5** — Write the conclusion: value range, and whether the discount is a value opportunity or a fair reflection of returns.
- **Day 6** — PDF, commit. **Flagship deliverable #5 done.**

---

# PHASE 6 — ANALYST TOOLKIT (Weeks 25–27)

The scaffold in `03-analyst-toolkit/` already runs offline against bundled fixtures. Your job is
to make it work against live EDGAR data and extend it.

## Week 25 — Get it running

- **Day 1** — Read through the existing package: `edgar.py`, `normalize.py`, `multiples.py`, `comps.py`, `excel_export.py`, `cli.py`. Run the test suite.
- **Day 2** — Run `python -m analyst_toolkit.cli comps --offline` and trace how data flows from fixture to output table.
- **Day 3** — Set your `SEC_USER_AGENT` (SEC requires a real contact string) and make one live call for a single ticker. Confirm you get real data.
- **Day 4** — Run the full peer set live. It will fail or return gaps for some tags — that's the actual problem to solve.
- **Day 5** — Debug the tag failures. Extend the candidate tag lists in `normalize.py` until coverage is complete.
- **Day 6** — Add caching so you aren't re-hitting EDGAR on every run.

## Week 26 — Extend

- **Day 1** — Add a bank-specific field set: net interest income, tangible book value, CET1 where tagged.
- **Day 2** — Add the P/TBV and ROTE calculations from Week 24 as computed metrics.
- **Day 3** — Add median, mean, high and low summary rows to the comps output.
- **Day 4** — Add calendarisation handling for differing fiscal year ends.
- **Day 5** — Add outlier flagging so a negative-EBITDA peer doesn't silently corrupt the median.
- **Day 6** — Write tests for every new calculation. Cover the edge cases: zero denominators, missing data, negative EBITDA.

## Week 27 — Polish

- **Day 1** — Improve the Excel exporter: number formats, column widths, header styling.
- **Day 2** — Add `--as-of` so you can pull historical comps rather than only current.
- **Day 3** — Write the toolkit README: what it does, how to run it, and what the XBRL normalisation problem actually is.
- **Day 4** — Add clear error handling and helpful messages for rate limits and missing tickers.
- **Day 5** — Final code cleanup. Run the full test suite.
- **Day 6** — Commit. **Flagship deliverable #6 done.**

---

# PHASE 7 — CAPSTONE (Week 28)

Draft this incrementally as you go rather than all at once — you have been forming the thesis
since Week 11.

- **Day 1** — Write the executive summary and investment thesis: 3 bullets, recommendation, target price. Use `templates/investment-memo-template.md`.
- **Day 2** — Write the business overview and industry/competitive positioning sections.
- **Day 3** — Write the valuation section, pulling in your football field and DCF output.
- **Day 4** — Write catalysts and, critically, **risks — including what would prove you wrong.** Interviewers probe this hardest.
- **Day 5** — Rehearse the pitch out loud. Compress to 90 seconds, then to 30. If you can't do 30 seconds, your thesis isn't sharp yet.
- **Day 6** — Final portfolio pass: update the top-level README, verify every PDF renders, confirm every link works, push everything.

---

## Interview Readiness Checkpoints

Test yourself at these milestones. If you can't answer from memory, revisit.

| After | You should be able to answer |
|---|---|
| Week 9 | Walk me through how $10 of depreciation flows through all three statements. |
| Week 12 | Walk me through a DCF. Why unlevered cash flow? Why is WACC the discount rate? |
| Week 14 | Which valuation methodology gives the highest value, and why? |
| Week 18 | Walk me through an LBO. What drives returns? Why does leverage amplify them? |
| Week 21 | An all-stock deal — when is it accretive? What determines that? |
| Week 24 | Why can't you use EV/EBITDA on a bank? |
| Week 28 | Pitch me a stock. (90 seconds, no notes.) |

## A Note on Priorities

This portfolio gets you interviews at valuation, equity research, FP&A, credit and corp-dev roles,
and gives you substantive material for IB conversations.

But for investment banking specifically, **networking converts better than any portfolio**. Alumni
coffee chats and informational calls get you the interview; this work makes those conversations
credible and closes the technical screen once you're in the room. Spend time on both from week one.
Do not let building become a way to postpone reaching out to people.
