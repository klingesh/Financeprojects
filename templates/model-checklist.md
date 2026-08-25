# Model QA Checklist

Run this in full before any model is called finished. Copy it into each project and tick items off.

Attention to detail is the skill being assessed. A model with one broken link reads as careless
regardless of how sophisticated the rest of it is.

---

## 1. Integrity — every one of these must pass

- [ ] Balance sheet balances in **every** historical year
- [ ] Balance sheet balances in **every** forecast year
- [ ] Balance sheet balances under **every** scenario (Base, Bull, Bear)
- [ ] Closing cash on the balance sheet equals closing cash on the cash flow statement
- [ ] PP&E roll-forward ties: closing = opening + capex − depreciation − disposals
- [ ] Debt on the balance sheet equals closing debt on the debt schedule
- [ ] Retained earnings ties: closing = opening + net income − dividends
- [ ] Sources equal Uses (transaction models)
- [ ] Master check flag on the `Cover` tab reads PASS
- [ ] No `#REF!`, `#VALUE!`, `#DIV/0!`, `#N/A` or `#NAME?` anywhere — use Ctrl+G → Special → Formulas → Errors

## 2. Formulas

- [ ] Press **Ctrl+~** and scan every tab for hardcoded numbers inside formulas
- [ ] No hardcodes except genuine constants (365, 12, 100, crore conversions)
- [ ] Every formula in a row is consistent across all columns — check by copying the leftmost
      forecast cell rightwards and confirming nothing changes
- [ ] No `VLOOKUP` (use `INDEX`/`MATCH`)
- [ ] No merged cells
- [ ] No external workbook links
- [ ] No volatile functions (`OFFSET`, `INDIRECT`, `NOW`, `TODAY`) in calculation paths
- [ ] Circularity handled with a documented breaker toggle, not by using opening balances
- [ ] Iterative calculation enabled if the model is intentionally circular
- [ ] Scenario toggle switches cleanly with no residual hardcoded values

## 3. Formatting

- [ ] Blue font on all inputs
- [ ] Black font on all same-sheet formulas
- [ ] Green font on all cross-sheet links
- [ ] **No yellow fill remaining** — every temporary cell resolved
- [ ] Units stated in every row label
- [ ] No mixed units within a row
- [ ] Percentages formatted as percentages
- [ ] Negatives in parentheses
- [ ] Consistent decimal places within each row
- [ ] Column widths sized so nothing shows as `####`
- [ ] Print area set and each tab fits sensibly on a page
- [ ] Gridlines off, freeze panes set on every statement tab

## 4. Sanity — does it make economic sense?

This section catches the errors that formulas cannot.

- [ ] Forecast margins sit within, or defensibly outside, the historical range
- [ ] EBITDA per tonne is comparable to history (cement) — flag and justify any deviation
- [ ] Revenue growth is achievable given the capacity you have modelled
- [ ] Capex is sufficient to support the volume growth you have assumed
- [ ] Depreciation is broadly consistent with the asset base and its useful life
- [ ] Working capital days are stable or the change is deliberate and explained
- [ ] Tax rate is plausible against the statutory rate
- [ ] Net debt / EBITDA stays within a range a lender would actually accept
- [ ] Terminal growth rate does not exceed long-run nominal GDP
- [ ] Exit multiple implies a sane perpetuity growth rate — cross-check it
- [ ] WACC exceeds the risk-free rate and cost of equity exceeds cost of debt
- [ ] Implied valuation is in the same universe as the current market price; if not, you can explain why

## 5. Stress tests

- [ ] Set revenue growth to 0% — does the model still balance?
- [ ] Set revenue growth to −20% — does anything break or go nonsensical?
- [ ] Double the largest cost input — does EBITDA respond proportionately?
- [ ] Set capex to zero — does depreciation eventually decline as it should?
- [ ] Push leverage until the coverage covenant breaches (LBO) — does the sweep behave?
- [ ] Set synergies to zero (merger model) — is the deal still defensible?

## 6. Documentation

- [ ] `Cover` tab states purpose, author, date, currency and units
- [ ] Every key assumption is logged with its basis in the project README
- [ ] Data sources cited, with the date each figure was pulled
- [ ] Circularity toggle instructions written on the `Cover` tab
- [ ] Limitations section written and honest
- [ ] Valuation conclusion stated as a range, not a false-precision point estimate

## 7. Delivery

- [ ] Exported to PDF into `outputs/`
- [ ] PDF opens correctly and is legible without the workbook
- [ ] Project README deliverables table updated
- [ ] Committed and pushed
- [ ] All README links resolve

---

## The final test

Close the model. Come back the next day. Open it and ask:

1. Can I explain every assumption on the `Assumptions` tab out loud, without notes?
2. Could a stranger follow my logic from revenue driver to valuation conclusion?
3. If someone changed one input, would the whole model respond correctly?

If the answer to any of these is no, the model is not finished.
