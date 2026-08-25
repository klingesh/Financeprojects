# Interview Prep Map

Which project answers which interview question. Use this to convert build work into interview
answers — and to identify gaps before someone else does.

The advantage of learning technicals by building is that your answers come with a concrete example
attached. *"Yes — and when I built this for CDSL, the thing that surprised me was..."* is a far
stronger answer than a recited definition.

Week references map to [`../ROADMAP.md`](../ROADMAP.md).

---

## Accounting

| Question | Covered by | Where |
|---|---|---|
| Walk me through the three statements. | CDSL three-statement model | Phase 1 |
| ₹10 of depreciation — walk it through all three statements. | PP&E and depreciation schedules | W6 D1–2 |
| How does an increase in receivables affect the statements? | Working capital build | W6 D3 |
| What's the difference between cash and accrual accounting? | CFS construction | W7 D2 |
| Why can net income be positive while cash falls? | CFS integration | W7 D2–5 |
| What's deferred tax and why does it arise? | Tax line forecasting | W6 D4 |
| Where does goodwill come from? | LBO purchase price allocation; merger model | W20 D4, W24 D1 |
| Which statement would you pick if you could only have one? | — | Cash flow statement. Cash is fact; earnings are opinion. |

## Valuation — general

| Question | Covered by | Where |
|---|---|---|
| Walk me through a DCF. | CDSL DCF | Phase 2 |
| Why unlevered free cash flow, not levered? | FCF bridge | W10 D1 |
| Two ways to calculate terminal value? Which do you prefer? | Both built | W10 D3–4 |
| How do you get from enterprise value to equity value? | EV-to-equity bridge | W10 D5 |
| How do you calculate beta? | Beta regression vs. Nifty | W9 D3 |
| What % of your DCF value is terminal value? Is that a problem? | Terminal value contribution | W11 D3 |
| How do you select comparable companies? | Peer selection with written justification | W12 D1, W18 D1 |
| What if two comps have different fiscal year ends? | Calendarisation | W12 D6 |
| Which methodology gives the highest valuation? | Football field | W13 D4 |
| Why do precedent transactions usually exceed trading comps? | Control premium | W13 D2, W18 D5 |

## Capital-light fee businesses

The distinctive section of this portfolio — see
[`fee-business-modelling.md`](fee-business-modelling.md).

| Question | Covered by | Where |
|---|---|---|
| **Why is this company's enterprise value below its market cap?** | Net cash EV bridge | W12 D3 |
| **Why is the discount rate just cost of equity here?** | No debt, so WACC = Ke | W6 D5, W9 D5 |
| This company's revenue is half recurring — why does that matter? | Recurring vs. cyclical split | W3 D3 |
| **An AMC's AUM grew 20% — is that good?** | Flows vs. market decomposition | W14 D5 |
| **Why do asset managers trade on a percentage of AUM?** | P/AUM analysis | W18 D2 |
| Two AMCs have the same P/AUM — are they equally valued? | Asset mix and blended yield | W18 D3 |
| What happens to AMC revenue if equity markets fall 20%? | Mix shift plus AUM decline | W15 D6 |
| **How do you value a company with a large investment portfolio?** | Sum-of-parts | W17 D3–5 |
| Where does operating leverage come from in a fee business? | Bottom-up cost build | W5 D4, W16 D4 |
| This company has 40% ROE — is it a great business? | Capital-light structure | W3 D6 |
| What's the biggest risk to a regulated fee business? | Regulated rate compression | W8 D2 |
| Give me a sector-specific multiple. | EV per demat account; P/AUM | W12 D5, W18 D2 |

## LBO and deal mechanics

| Question | Covered by | Where |
|---|---|---|
| Walk me through an LBO. | CAMS LBO | Phase 4 |
| **What makes a good LBO candidate — and why can't you LBO CDSL?** | MII ownership caps | W19 D1 |
| Sources & uses — what goes where? | S&U table | W20 D2 |
| What's a cash flow sweep and how does the waterfall work? | Cash sweep build | W21 D4 |
| What are the three drivers of LBO returns? | Returns attribution | W22 D5 |
| Why does leverage amplify returns? | Debt paydown component | W22 D5 |
| What's the difference between IRR and MoIC? | Returns calculation | W22 D3 |
| How do you decide the maximum purchase price? | IRR-hurdle solve | W22 D6 |
| Walk me through accretion/dilution. | Merger model | Phase 5 |
| When is an all-stock acquisition accretive? | Consideration mix sensitivity | W25 D4 |
| What synergies are needed to break even? | Breakeven solve | W25 D2 |
| Why do most acquisitions destroy value? | Synergy phasing, integration costs | W24 D3 |
| What's specific to acquiring an asset manager? | AUM attrition on manager change | W24 D4 |

## Financial institutions

| Question | Covered by | Where |
|---|---|---|
| **Why can't you use EV/EBITDA on a bank?** | [Bank primer](bank-valuation-primer.md) | Phase 6 |
| How would you value a bank? | DDM + residual income | W27 D4–5 |
| **Why do banks trade below book value?** | Residual income logic | W27 D5 |
| Book value vs. tangible book value? | TBV calculation | W27 D1 |
| What is the CET1 ratio and what does it constrain? | Capital analysis | W26 D6 |
| How do rising rates affect a bank? | NIM decomposition | W26 D4 |
| Explain deposit beta. | Cost of funds analysis | W26 D4 |
| What's the efficiency ratio? | Expense forecasting | W27 D3 |
| Why is P/TBV related to ROTE? | Peer regression | W28 D2 |

## The comparative question

The strongest thing this portfolio lets you say, and nobody else will have it:

> *"I valued a depository, an asset manager and a bank. The depository and the asset manager both
> take a DCF, but the asset manager needs sum-of-parts because its treasury book shouldn't carry an
> operating multiple. The bank takes neither — no enterprise value, no unlevered cash flow — so it
> needs a dividend discount or residual income approach, and the reason it trades below book is
> simply that its return on tangible equity sits under its cost of equity."*

Built in Week 32 Day 5. Rehearse it — it demonstrates range that a single model cannot.

## The stock pitch

Asked in essentially every finance interview. Your capstone memo is the preparation.

1. **Recommendation and target** — one sentence, lead with the conclusion.
2. **Three reasons** — the thesis, ordered by importance.
3. **Why the market is wrong** — what do you see that consensus doesn't? Without this you have a
   description, not a thesis.
4. **Catalyst** — what makes it play out, and when.
5. **Risks and what disproves you** — the two things that would change your mind.

Practise at **30 seconds**, **90 seconds** and **5 minutes**. Interviewers cut you off at different
points and you need to survive all of them.

Bring a printed copy of the memo. Almost nobody does, and it changes the tenor of the conversation.

## Behavioural — "Why this project?"

> "I wanted to learn modelling by building rather than reading, so I valued CDSL from the annual
> reports — three-statement model, DCF, comps. Then HDFC AMC, which is a fee-on-AUM business rather
> than fee-on-activity, and needs sum-of-parts because of its treasury book. Then Citigroup, because
> a bank breaks the standard toolkit entirely and I wanted to understand why. The thing that
> surprised me most was [specific, genuine observation]."

Fill that bracket with something you actually discovered. Interviewers can tell instantly whether
you built the model or downloaded it, and the tell is always whether you have a real observation
about the business.

Good candidates for that observation, if they hold when you do the work: how much of CDSL's revenue
survives a bear market; how much of an AMC's AUM growth is just the market; how far Citi's ROTE gap
explains its discount to book.

## Known gaps in this portfolio

Be honest about these rather than being caught out:

- **No capital-intensive industrial model.** All three subjects are capital-light or financial, so
  heavy PP&E roll-forwards, capex-driven growth, inventory working capital and cyclical operating
  leverage are not exercised. If you're interviewing for industrials or infrastructure coverage,
  acknowledge this directly — and consider building a fourth model later.
- **No restructuring or distressed work** — no recovery waterfalls or fulcrum security analysis.
- **No insurance modelling** — embedded value and VNB for life insurers, combined ratio for general
  insurers, are all untouched. Worth knowing this is a *fourth* toolkit beyond the three here.
- **No real estate NAV or oil & gas reserve models.**
- **India-weighted** — CDSL, HDFC AMC, the CAMS LBO and the merger model are all Indian; only Citi
  is US. Adjust emphasis depending on which market you're recruiting in.
- **Limited live market context** — you've built models, not tracked markets. Read a financial daily
  and be able to discuss the current rate and deal environment.
