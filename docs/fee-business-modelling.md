# Modelling Capital-Light Fee Businesses

CDSL and HDFC AMC are both **capital-light fee businesses**. They earn a fee on someone else's
assets or activity, hold almost no fixed assets, carry no debt, and sit on net cash.

This changes the model structurally. It is not a capital-intensive model with smaller numbers — the drivers,
the balance sheet, and the WACC all behave differently. This document explains how.

Read this alongside [`bank-valuation-primer.md`](bank-valuation-primer.md). Together they cover the
three architectures in this portfolio:

| Architecture | Revenue driver | Valuation |
|---|---|---|
| **Capital-light fee** (CDSL, HDFC AMC) | Fee × someone else's base | Standard DCF works fully |
| **Balance sheet spread** (Citigroup) | Spread × own balance sheet | DDM, residual income |
| Capital-intensive industrial | Capacity × utilisation × price | Standard DCF |

---

## 1. Revenue is a fee on a base you don't own

The universal form:

```
Revenue = Base × Rate
```

Where the **base** belongs to customers and the **rate** is usually regulated or competitively
compressed. Two variants appear in this portfolio:

### Asset-based (HDFC AMC)

```
Average AUM by category × Yield (basis points) by category = Management fee revenue
```

The essential subtlety: **yield differs enormously by asset category.** Equity funds earn
multiples of what liquid funds earn. So a shift in AUM *mix* changes blended yield even when no
individual fee rate moves.

This means you must model AUM **by category**, never as a single blended number. A model that
forecasts total AUM × blended yield will miss the single most important dynamic in the business.

```
Equity AUM      × equity yield (bps)      ─┐
Debt AUM        × debt yield (bps)         ├─→ Total revenue
Liquid AUM      × liquid yield (bps)       │
Other/passive   × passive yield (bps)     ─┘
```

Then decompose AUM growth into its two sources, which behave completely differently:

- **Net flows** — the business winning or losing mandates. Management's actual performance.
- **Market appreciation** — the market moving. Nothing to do with management.

A year of strong AUM growth driven entirely by a market rally is not evidence of a good business.
Separating these two is the core analytical skill in asset management.

### Activity- and account-based (CDSL)

```
Number of accounts × annual fee          = recurring revenue
Transaction volumes × charge per debit   = cyclical revenue
Number of issuers × slab-based fee       = recurring revenue
KYC/other volumes × unit rate            = ancillary revenue
```

The key distinction here is **recurring versus cyclical**. Annual issuer fees and account-linked
charges recur regardless of market conditions. Transaction charges track market activity and fall
sharply in a bear market. Model them separately — the recurring share is what supports the
valuation floor, and the cyclical share is what creates the earnings volatility.

---

## 2. Operating leverage runs the other way

In a capital-intensive industrial, operating leverage comes from spreading heavy fixed costs over more
units of output.

In a fee business, leverage comes from the fact that **the cost base barely responds to the
revenue base**. Doubling AUM does not double headcount. Doubling demat accounts does not double
the cost of running the depository.

So forecast costs **bottom-up as their own drivers**, not as a percentage of revenue:

- **Employee cost** — headcount × average cost, growing with inflation and modest additions
- **Technology and operations** — largely fixed, stepping up with capacity investments
- **Regulatory and compliance** — fixed
- **Distribution/commission** — the exception; this one genuinely does scale with the asset base

If you forecast every cost as a percentage of revenue, margins stay flat forever and the model
demonstrates nothing. **The whole point is that margins expand as the base grows.**

The metric that captures this cleanly:

```
Operating profit as a percentage of average AUM     (asset managers)
Operating cost per demat account                    (depositories)
```

Both should trend favourably as scale builds. If your forecast shows otherwise, either you have a
view about competition and fee compression — state it — or your cost build is wrong.

---

## 3. The balance sheet is mostly cash

Consequences that trip people up:

**PP&E and capex are immaterial.** Build the schedule anyway for the practice, but it will be small
and will not drive value. Do not spend forecast effort here.

**Working capital is minor.** Fees are typically collected promptly and there is no inventory.
Model receivables off revenue and move on.

**There is no debt**, so:

```
WACC = Cost of equity
```

The WACC build collapses to CAPM. Say so explicitly in the model rather than constructing an
elaborate weighted calculation where the debt weight is zero.

**Net cash means enterprise value is *below* market capitalisation:**

```
EV = Market cap + Debt − Cash
   = Market cap + 0 − (large cash balance)
   = Market cap − net cash
```

This surprises people the first time. It also means EV/EBITDA understates the apparent richness of
a net-cash company relative to a levered peer, so be careful comparing across different balance
sheet structures.

**Returns on equity are structurally high** because the equity base is small relative to earnings.
Do not read a 30%+ ROE as evidence of exceptional performance — it is a feature of the business
model. Compare against peers, not against industrials.

---

## 4. Sum-of-parts, when there is a treasury book

Some fee businesses accumulate a large investment portfolio from retained profits, and it can
generate material "other income". HDFC AMC is a case in point.

**Do not discount other income inside the operating DCF.** It is not operating cash flow, and
capitalising it at an operating multiple double-counts. Instead:

```
Value of core fee business        (DCF of operating cash flows only)
+ Net investments at market value  (the treasury book, marked)
= Total equity value
```

This matters because the two components deserve different multiples. A fee franchise compounding
at 15% is worth far more per rupee of earnings than a bond portfolio yielding 7%. Blending them
into a single P/E obscures exactly the thing you are trying to value.

Handling this correctly is a genuine differentiator. Most people quietly leave other income in the
operating forecast and never notice.

---

## 5. Sector-specific multiples

Every sector has a multiple that reveals whether you understand it — a cement producer has EV per
tonne of capacity, a hotel has EV per key. The equivalents for the businesses in this portfolio:

### Asset managers: Market cap as a percentage of AUM

```
P/AUM (%) = Market capitalisation / Assets under management
```

The dominant metric in asset management, and the basis on which **AMC acquisitions are actually
priced** — deals are announced and discussed as a percentage of AUM. This gives you a direct
bridge between trading comps and precedent transactions, which is unusually clean.

Interpretation requires care: a manager with a high equity mix should trade at a higher P/AUM
because each rupee of AUM earns more. So always read P/AUM alongside blended yield and asset mix.
A low P/AUM on a liquid-fund-heavy book is not cheap.

### Depositories and exchanges

```
EV per demat account            (capitalised value of each account relationship)
Revenue per account             (monetisation intensity)
P/E                             (dominant, given the asset-light structure)
EV/EBITDA                       (cross-check; remember net cash reduces EV)
```

---

## 6. What actually drives the valuation

For both companies, value is overwhelmingly determined by three things:

1. **Growth in the base** — AUM, accounts, issuers, volumes
2. **The rate** — whether fees hold, and this is usually a *regulatory* question
3. **Incremental margin** — how much of each new rupee of revenue reaches operating profit

Item 2 is where most of the risk sits. Both businesses operate under SEBI-regulated or
SEBI-influenced pricing. A regulator can compress your fee rate with a circular, and no amount of
base growth offsets a structural rate cut. **The regulatory section of your memo is not
boilerplate — it is the core risk.**

This is also why the terminal value assumption deserves real scrutiny. A capital-light business
with a high ROE and a long runway can support a healthy terminal multiple. But if fee compression
is structural rather than cyclical, terminal margins should be *below* current margins. Decide
which you believe and say so.

---

## 7. Common mistakes

| Mistake | Why it's wrong |
|---|---|
| Forecasting total AUM × blended yield | Misses mix shift, the dominant driver of yield |
| Not splitting AUM growth into flows vs. market | Attributes a market rally to management skill |
| Costs as a % of revenue | Destroys the operating leverage you are trying to show |
| Other income inside the operating DCF | Double-counts the treasury book; wrong multiple |
| Building an elaborate WACC with zero debt weight | WACC is simply Ke; the complexity is theatre |
| Expecting EV > market cap | Net cash inverts this |
| Treating high ROE as outperformance | It is a structural feature of capital-light models |
| Ignoring regulated pricing risk | It is the single largest risk to the thesis |
| Flat forecast margins | Either your cost build is wrong or you have an unstated view |

---

## Interview questions this prepares you for

- *How would you value an asset manager?*
- *Why do asset managers trade on a percentage of AUM?*
- *An AMC's AUM grew 20% — is that good?* (Depends entirely on flows versus market appreciation.)
- *What happens to an AMC's revenue if equity markets fall 20%?* (More than 20%, because mix
  shifts toward lower-yielding debt and liquid funds as well.)
- *Why might a company have an enterprise value below its market cap?*
- *This company has 40% ROE — is it a great business?* (Probably capital-light; compare to peers.)
- *How do you value a business with a large investment portfolio?* (Sum-of-parts.)
- *What's the biggest risk to a regulated fee business?* (Regulated rate compression.)
