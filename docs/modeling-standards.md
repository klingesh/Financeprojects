# Modelling Standards

These are the conventions used across every model in this repository. They are not stylistic
preferences — they are the conventions used on the street, and deviating from them signals
inexperience to anyone who reviews your work.

## Cell Formatting

| Colour | Meaning |
|---|---|
| **Blue font** | Hardcoded input / assumption |
| **Black font** | Formula calculated on the current sheet |
| **Green font** | Link pulled from another sheet in the same workbook |
| **Red font** | Link to an external workbook (avoid entirely where possible) |
| Yellow fill | Temporary — must be resolved before the model is called finished |

Set these up as named Excel cell styles before you start typing. Applying them retroactively
across a finished model takes hours.

## The Cardinal Rule

**No hardcoded numbers inside formulas. Ever.**

```
WRONG:   = B12 * 1.08
RIGHT:   = B12 * (1 + $C$4)        where C4 is a labelled blue input cell
```

The exceptions are genuine mathematical constants and unit conversions: `365`, `12`, `100`,
`10000000` for crore conversions. Nothing else.

The reason is auditability. A reviewer must be able to change any assumption in one place and see
the whole model respond. A growth rate buried inside forty formulas is invisible and undefendable.

## Structure

- **One row = one line item. One column = one period.** Never break this grid.
- **Historicals and forecasts in the same rows**, separated by a visible divider column. This lets
  ratios calculate continuously across both.
- **Assumptions live on their own tab**, not scattered through the statements.
- **Left-to-right chronological.** Oldest period on the left, always.
- **No blank rows inside a calculation block.** Group with indentation and formatting instead.

## Sign Convention

Pick one and hold it absolutely consistently. The convention used here:

- **Revenue and inflows positive.**
- **Costs and outflows negative**, summed with `SUM()` rather than subtracted.

So EBITDA is `=SUM(revenue:other_expenses)` where every cost row is already negative. This is safer
than mixed addition and subtraction because a misplaced sign becomes visually obvious.

Capex is negative in the cash flow statement and positive in the PP&E roll-forward. That is
intentional — but label both clearly.

## Integrity Checks

Every model has a `Checks` tab. It contains, at minimum:

```
Balance sheet balances       = Total assets − (Total liabilities + Total equity)     → must be 0
Cash ties                    = Closing cash on BS − Closing cash on CFS              → must be 0
PP&E roll-forward ties       = Closing net block − (Opening + capex − depreciation)   → must be 0
Debt schedule ties           = Closing debt on BS − Closing debt on schedule          → must be 0
Retained earnings ties       = Closing RE − (Opening + NI − dividends)                → must be 0
Sources = Uses               (transaction models only)                                → must be 0
```

Wrap each in a tolerance test so floating point noise doesn't produce false alarms:

```
=IF(ABS(check_value) < 0.001, "OK", "ERROR")
```

Put a single master flag at the top of the `Cover` tab that aggregates all of them:

```
=IF(COUNTIF(Checks!$D$5:$D$40, "ERROR") = 0, "ALL CHECKS PASS", "MODEL HAS ERRORS")
```

Build the checks tab **before** you build the forecast, not after. It catches errors as you
introduce them, when you still remember what you just changed.

## Circular References

Interest expense on an average debt balance is genuinely circular:

```
interest → net income → cash flow → debt balance → average balance → interest
```

Do not solve this by using the opening balance and pretending the problem doesn't exist. Handle it
explicitly:

1. Enable iterative calculation (File → Options → Formulas → Enable iterative calculation, max
   iterations 100, max change 0.001).
2. Build a `Circ_Breaker` toggle input cell: when set to 1, the interest formula returns a hardcoded
   zero instead of the circular reference.
3. Document the toggle prominently on the `Cover` tab with instructions.

The breaker matters because circular models corrupt into `#VALUE!` cascades when a formula errors
mid-calculation, and the toggle is how you reset without rebuilding.

## Formulas to Avoid

| Avoid | Use instead | Why |
|---|---|---|
| `VLOOKUP` | `INDEX`/`MATCH` or `XLOOKUP` | Breaks silently when columns are inserted |
| Nested `IF` beyond 3 levels | Helper rows, or `CHOOSE` | Unauditable |
| Merged cells | Centre across selection | Breaks references, sorting and navigation |
| Volatile functions (`OFFSET`, `INDIRECT`, `NOW`) | Direct references | Force full recalculation; slow and fragile |
| Array formulas | Explicit helper rows | Opaque to reviewers |

Scenario switching should use `CHOOSE` or `INDEX` driven by one integer toggle cell — never a
stack of nested `IF`s.

## Units and Labelling

- State units in **every** row label: `Revenue (₹ crore)`, `Volume (mt)`, `Realisation (₹/tonne)`.
- Never mix units within a row.
- Note the currency and scale in the tab header. UltraTech reports in ₹ crore; Citigroup in
  US$ millions. Do not let these meet without an explicit, labelled conversion.
- Percentages formatted as percentages, not decimals.
- Negative numbers in parentheses, financial convention: `(1,234)`.

## Before You Call a Model Finished

Run [`../templates/model-checklist.md`](../templates/model-checklist.md) in full.

Then do this: press `Ctrl+~` to reveal all formulas and scan every tab. Hardcodes you forgot about
become immediately visible. It takes two minutes and catches embarrassing errors.

Finally, export to PDF. Anyone reviewing your portfolio from a phone will read the PDF, not open
the workbook.
