"""Valuation multiple calculations.

Every function returns ``None`` rather than raising when a multiple is not
meaningful — a negative or zero denominator, or missing data. Silently
substituting zero would corrupt peer-set medians, which is the single most
common error in automated comps.
"""

from typing import Dict, List, Optional, Sequence


def safe_div(
    numerator: Optional[float],
    denominator: Optional[float],
    require_positive_denominator: bool = True,
) -> Optional[float]:
    """Divide, returning None where the result would be meaningless."""
    if numerator is None or denominator is None:
        return None
    if denominator == 0:
        return None
    if require_positive_denominator and denominator < 0:
        return None
    return numerator / denominator


def market_cap(price: Optional[float], shares: Optional[float]) -> Optional[float]:
    if price is None or shares is None:
        return None
    return price * shares


def enterprise_value(
    mkt_cap: Optional[float],
    total_debt: Optional[float],
    cash: Optional[float],
    minority_interest: Optional[float] = None,
    preferred_equity: Optional[float] = None,
) -> Optional[float]:
    """EV = market cap + debt − cash + minority interest + preferred.

    Minority interest is added because consolidated EBITDA includes the whole
    of the partly-owned subsidiary, so the numerator must reflect the whole
    claim on it too.
    """
    if mkt_cap is None:
        return None
    return (
        mkt_cap
        + (total_debt or 0.0)
        - (cash or 0.0)
        + (minority_interest or 0.0)
        + (preferred_equity or 0.0)
    )


def net_debt(total_debt: Optional[float], cash: Optional[float]) -> Optional[float]:
    if total_debt is None and cash is None:
        return None
    return (total_debt or 0.0) - (cash or 0.0)


# -- Multiples ------------------------------------------------------------


def ev_ebitda(ev: Optional[float], ebitda: Optional[float]) -> Optional[float]:
    return safe_div(ev, ebitda)


def ev_revenue(ev: Optional[float], revenue: Optional[float]) -> Optional[float]:
    return safe_div(ev, revenue)


def ev_ebit(ev: Optional[float], operating_income: Optional[float]) -> Optional[float]:
    return safe_div(ev, operating_income)


def price_earnings(
    mkt_cap: Optional[float], net_income: Optional[float]
) -> Optional[float]:
    """P/E. None for loss-makers — a negative P/E is not interpretable."""
    return safe_div(mkt_cap, net_income)


def price_tangible_book(
    mkt_cap: Optional[float], tangible_book_value: Optional[float]
) -> Optional[float]:
    """P/TBV — the primary multiple for financial institutions."""
    return safe_div(mkt_cap, tangible_book_value)


def return_on_tangible_equity(
    net_income: Optional[float], tangible_book_value: Optional[float]
) -> Optional[float]:
    """ROTE. Uses period-end tangible book rather than an average.

    A fuller implementation would average opening and closing tangible book;
    period-end is used here because single-period fixtures lack the prior year.
    """
    return safe_div(net_income, tangible_book_value)


def ebitda_margin(
    ebitda: Optional[float], revenue: Optional[float]
) -> Optional[float]:
    return safe_div(ebitda, revenue)


def net_debt_ebitda(
    nd: Optional[float], ebitda: Optional[float]
) -> Optional[float]:
    """Leverage. Negative net debt legitimately gives a negative ratio."""
    return safe_div(nd, ebitda)


# -- Peer statistics ------------------------------------------------------


def median(values: Sequence[Optional[float]]) -> Optional[float]:
    clean = sorted(v for v in values if v is not None)
    if not clean:
        return None
    mid = len(clean) // 2
    if len(clean) % 2 == 1:
        return clean[mid]
    return (clean[mid - 1] + clean[mid]) / 2.0


def mean(values: Sequence[Optional[float]]) -> Optional[float]:
    clean = [v for v in values if v is not None]
    if not clean:
        return None
    return sum(clean) / len(clean)


def minimum(values: Sequence[Optional[float]]) -> Optional[float]:
    clean = [v for v in values if v is not None]
    return min(clean) if clean else None


def maximum(values: Sequence[Optional[float]]) -> Optional[float]:
    clean = [v for v in values if v is not None]
    return max(clean) if clean else None


def summary_stats(values: Sequence[Optional[float]]) -> Dict[str, Optional[float]]:
    return {
        "median": median(values),
        "mean": mean(values),
        "min": minimum(values),
        "max": maximum(values),
    }


def flag_outliers(
    values: Sequence[Optional[float]], threshold: float = 2.5
) -> List[bool]:
    """Flag values more than ``threshold`` × the median away from it.

    Median-based rather than standard-deviation-based because peer sets are
    small and a single extreme value distorts the mean and sigma badly.
    """
    med = median(values)
    if med is None or med == 0:
        return [False] * len(values)
    flags = []
    for value in values:
        if value is None:
            flags.append(False)
            continue
        flags.append(abs(value / med) > threshold or abs(value / med) < (1.0 / threshold))
    return flags


def linear_regression(xs: Sequence[float], ys: Sequence[float]):
    """Ordinary least squares fit. Returns (slope, intercept, r_squared).

    Used for the P/TBV vs. ROTE bank regression. Implemented directly to keep
    the toolkit dependency-free.
    """
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 2:
        raise ValueError("Need at least two complete observations to regress.")

    n = float(len(pairs))
    mean_x = sum(p[0] for p in pairs) / n
    mean_y = sum(p[1] for p in pairs) / n

    sxx = sum((p[0] - mean_x) ** 2 for p in pairs)
    sxy = sum((p[0] - mean_x) * (p[1] - mean_y) for p in pairs)
    if sxx == 0:
        raise ValueError("Zero variance in x; cannot regress.")

    slope = sxy / sxx
    intercept = mean_y - slope * mean_x

    ss_tot = sum((p[1] - mean_y) ** 2 for p in pairs)
    ss_res = sum((p[1] - (slope * p[0] + intercept)) ** 2 for p in pairs)
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot else 1.0

    return slope, intercept, r_squared
