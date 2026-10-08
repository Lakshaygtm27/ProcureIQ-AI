import pandas as pd


def normalize_cost(series):
    """
    Lower cost is better.
    """
    minimum = series.min()

    if minimum <= 0:
        return pd.Series(0.0, index=series.index)

    return (minimum / series) * 100


def normalize_benefit(series):
    """
    Higher value is better.
    """
    maximum = series.max()

    if maximum <= 0:
        return pd.Series(0.0, index=series.index)

    return (series / maximum) * 100


def calculate_scores(
    df,
    cost_weight=0.40,
    quality_weight=0.35,
    lead_time_weight=0.25
):
    """
    Calculate deterministic vendor scores.

    Gemini is NOT involved in this calculation.
    """

    weights_total = (
        cost_weight +
        quality_weight +
        lead_time_weight
    )

    if abs(weights_total - 1.0) > 0.0001:
        raise ValueError("Weights must total 100%.")

    result = df.copy()

    # Normalize criteria
    result["Cost Score"] = normalize_cost(result["Unit Cost"])

    result["Quality Score Normalized"] = normalize_benefit(
        result["Quality Score"]
    )

    result["Lead Time Score"] = normalize_cost(
        result["Lead Time"]
    )

    # Weighted contributions
    result["Cost Contribution"] = (
        result["Cost Score"] * cost_weight
    )

    result["Quality Contribution"] = (
        result["Quality Score Normalized"] * quality_weight
    )

    result["Lead Time Contribution"] = (
        result["Lead Time Score"] * lead_time_weight
    )

    # Final deterministic score
    result["Final Score"] = (
        result["Cost Contribution"]
        + result["Quality Contribution"]
        + result["Lead Time Contribution"]
    )

    # Ranking
    result = result.sort_values(
        by="Final Score",
        ascending=False
    ).reset_index(drop=True)

    result["Rank"] = result.index + 1

    return result