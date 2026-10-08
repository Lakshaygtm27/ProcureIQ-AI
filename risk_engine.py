def evaluate_vendor_eligibility(
    df,
    quantity,
    maximum_cost,
    maximum_lead_time,
    minimum_quality
):
    """
    Evaluate whether each vendor satisfies
    the buyer's procurement requirements.
    """

    result = df.copy()

    result["Capacity OK"] = (
        result["Capacity"] >= quantity
    )

    result["Cost OK"] = (
        result["Unit Cost"] <= maximum_cost
    )

    result["Lead Time OK"] = (
        result["Lead Time"] <= maximum_lead_time
    )

    result["Quality OK"] = (
        result["Quality Score"] >= minimum_quality
    )

    result["Eligible"] = (
        result["Capacity OK"]
        & result["Cost OK"]
        & result["Lead Time OK"]
        & result["Quality OK"]
    )

    def status(row):

        problems = []

        if not row["Capacity OK"]:
            problems.append("Insufficient capacity")

        if not row["Cost OK"]:
            problems.append("Cost exceeds limit")

        if not row["Lead Time OK"]:
            problems.append("Lead time exceeds limit")

        if not row["Quality OK"]:
            problems.append("Quality below minimum")

        if not problems:
            return "Eligible"

        return "⚠ " + "; ".join(problems)

    result["Status"] = result.apply(
        status,
        axis=1
    )

    return result