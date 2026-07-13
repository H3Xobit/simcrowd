"""Van Westendorp pricing from raw responses (pandas only, never LLM math)."""

from __future__ import annotations

from typing import Any

import pandas as pd


def van_westendorp(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Expect keys cheap/bargain/expensive/too_expensive numeric strings."""
    if not rows:
        return {"ok": False, "reason": "no rows"}
    df = pd.DataFrame(rows)
    for col in ["cheap", "bargain", "expensive", "too_expensive"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna()
    if df.empty:
        return {"ok": False, "reason": "no numeric prices"}
    points = sorted({float(x) for x in df.values.ravel()})
    # Cumulative shares
    def cdf_above(series: pd.Series, x: float) -> float:
        return float((series <= x).mean())

    def cdf_below(series: pd.Series, x: float) -> float:
        return float((series >= x).mean())

    curve = []
    for x in points:
        curve.append(
            {
                "price": x,
                "too_cheap": cdf_above(df["cheap"], x),
                "bargain": cdf_above(df["bargain"], x),
                "expensive": cdf_below(df["expensive"], x),
                "too_expensive": cdf_below(df["too_expensive"], x),
            }
        )
    # Intersection approximations
    opp = min(curve, key=lambda r: abs(r["too_cheap"] - r["expensive"]))
    indifference = min(curve, key=lambda r: abs(r["bargain"] - r["expensive"]))
    return {
        "ok": True,
        "n": int(len(df)),
        "optimal_price_point": opp["price"],
        "indifference_price_point": indifference["price"],
        "curve": curve,
    }
