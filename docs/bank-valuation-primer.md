# Why Banks Need a Different Toolkit

The standard valuation toolkit — unlevered free cash flow, EV/EBITDA, LBO analysis — **does not
work on banks**. This document explains why, and what replaces it.

Understanding this distinction is a genuine differentiator. Many candidates try to run a DCF on a
bank and don't realise it's conceptually incoherent.

---

## Why the standard toolkit breaks

### 1. Debt is raw material, not financing

For an industrial company, debt is how you fund operations. Enterprise value deliberately strips out
financing to isolate operating performance — that's the entire logic of EV/EBITDA.

For a bank, **debt is the product.** Deposits and wholesale funding are the inputs a bank buys and
transforms into loans. Net interest income — the spread between them — *is* the revenue line.

So "enterprise value" is meaningless for a bank. You cannot separate financing from operations
because financing *is* operations. Every EV-based multiple is therefore inapplicable.

### 2. There is no meaningful EBITDA

Interest expense is a **cost of goods sold** for a bank, not a financing item. Adding it back
produces a number with no economic interpretation.

Depreciation and amortisation are also immaterial for a business whose assets are financial
instruments rather than plant and equipment.

### 3. Free cash flow is not definable

For a normal company, free cash flow is cash available to all capital providers after reinvestment.

For a bank, cash *is* inventory. An increase in cash isn't free cash flow — it's an unlent asset
earning a lower spread. And reinvestment isn't capex: to grow the loan book, a bank must retain
earnings to satisfy **regulatory capital requirements**. Growth is constrained by CET1, not by
capital expenditure.

### 4. Banks cannot be LBO'd

Setting aside mechanics entirely — it's illegal in practice. Bank holding company acquisitions
require Federal Reserve approval, acquirers must meet capital adequacy standards, and adding
acquisition leverage to a regulated deposit-taking institution defeats the purpose of capital
regulation. There is no cash sweep, because a bank's cash is its regulatory buffer.

---

## What to use instead

### Dividend Discount Model

Because a bank's distributable cash *is* its dividend capacity, and that capacity is set by
regulatory capital.

```
Value per share = Σ [ Dividend_t / (1 + Ke)^t ] + Terminal value
```

Forecast dividends as: net income × payout ratio, where the payout ratio is constrained by what the
bank can distribute while maintaining its required CET1 ratio and funding RWA growth. That
constraint is the analytical core — model it explicitly rather than assuming a flat payout.

Discount at **cost of equity**, never WACC. WACC is meaningless here for the reasons above.

### Residual Income / Excess Returns

The most theoretically sound bank valuation method, and the one that explains why banks trade
where they do.

```
Residual income_t = (ROTE_t − Ke) × Tangible book value_(t−1)

Value = Tangible book value + Σ [ Residual income_t / (1 + Ke)^t ]
```

The insight this delivers:

- If **ROTE > Ke**, the bank creates value and should trade **above** tangible book.
- If **ROTE = Ke**, it should trade **at** tangible book.
- If **ROTE < Ke**, it destroys value and should trade **below** tangible book.

This is the whole Citigroup debate in one equation. Citi has persistently traded at a discount to
tangible book because its returns have sat below its cost of equity. The investment question is
whether restructuring closes that gap.

### P/TBV vs. ROTE regression

The empirical counterpart to the above. Plot P/TBV on the y-axis against ROTE on the x-axis across
a peer set and fit a line. The relationship is reliably strong.

Then locate your bank relative to the fitted line:

- **On the line** — the valuation is explained by returns. No mispricing.
- **Below the line** — an unexplained discount. Either the market doubts the reported returns, or
  there is genuine opportunity.
- **Above the line** — the market is pricing in return improvement not yet delivered.

This separates "cheap because it earns poor returns" from "cheap for no good reason" — a distinction
that matters enormously and that most people collapse.

---

## Multiples that do work

| Multiple | Notes |
|---|---|
| **P/TBV** | The primary bank multiple. Use *tangible* book — goodwill from past acquisitions has no bearing on future earning power. |
| **P/E** | Works, but volatile because provisioning swings earnings across the credit cycle. |
| **P/B** | Acceptable, but P/TBV is preferred. |

Never use EV/EBITDA, EV/Revenue, or EV/EBIT.

---

## Metrics you must track

**Profitability**
- **ROTCE / ROTE** — return on tangible common equity. The headline metric for a bank.
- **NIM** — net interest margin: yield on earning assets − cost of funds.
- **Efficiency ratio** — non-interest expense / revenue. Lower is better; this is a bank's
  operating leverage.

**Credit quality**
- **NCO rate** — net charge-offs / average loans.
- **ACL / loans** — allowance for credit losses as a share of the book; the provisioning cushion.
- **NPL ratio** — non-performing loans.
- **Provision expense** — the P&L hit, which swings violently with the cycle and with CECL
  accounting estimates.

**Capital and funding**
- **CET1 ratio** — common equity tier 1 / risk-weighted assets. The binding growth constraint.
- **RWA density** — RWA / total assets. Reveals genuine balance sheet risk intensity.
- **SLR** — supplementary leverage ratio.
- **GSIB surcharge** — the extra capital required of globally systemically important banks. Citi
  carries one, and it directly reduces distributable capital.
- **Deposit mix** — non-interest-bearing deposits are cheap, sticky funding and a real competitive
  advantage.

---

## Modelling a bank: the structural difference

You do not build revenue then subtract costs. You **build the balance sheet first, then derive the
income statement from it**:

1. Forecast **average earning assets** — loan growth by category, plus securities.
2. Apply a **yield** to get interest income.
3. Forecast **funding** — deposits and borrowings — and apply a **cost of funds** to get interest expense.
4. Interest income − interest expense = **net interest income**.
5. Add **fee and trading revenue** (for Citi, a large share, especially in Markets and Services).
6. Subtract **non-interest expense**, driven by an efficiency ratio target.
7. Subtract **provision for credit losses**, driven by loan growth and an assumed loss rate.
8. Tax, then net income.
9. Roll **RWA** forward; check the resulting **CET1 ratio**.
10. Distributable capital is whatever remains after funding RWA growth and holding required CET1.

Step 10 is the one that makes it a bank model rather than a generic one. Capital adequacy — not
cash — governs what shareholders receive.

---

## Interview questions this prepares you for

- *Why can't you use EV/EBITDA to value a bank?*
- *Why do some banks trade below book value?*
- *What's the difference between book value and tangible book value, and why does it matter here?*
- *How does a rising rate environment affect a bank's earnings?* (NIM expansion, but watch deposit
  beta, unrealised securities losses, and credit deterioration.)
- *Walk me through how you'd value a bank.*
- *What does the CET1 ratio constrain?*
