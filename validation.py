def validate_weights(
    cost_weight,
    quality_weight,
    lead_time_weight
):
    """
    Validate procurement criteria weights.
    """

    total = (
        cost_weight
        + quality_weight
        + lead_time_weight
    )

    if abs(total - 1.0) > 0.0001:
        return False, (
            f"Criteria weights must total 100%. "
            f"Current total: {total * 100:.1f}%"
        )

    if any(
        weight < 0 or weight > 1
        for weight in [
            cost_weight,
            quality_weight,
            lead_time_weight
        ]
    ):
        return False, (
            "Each weight must be between 0% and 100%."
        )

    return True, "Weights are valid."


def validate_requirements(
    quantity,
    maximum_cost,
    maximum_lead_time,
    minimum_quality
):
    """
    Validate buyer procurement requirements.
    """

    errors = []

    if quantity <= 0:
        errors.append(
            "Quantity must be greater than 0."
        )

    if maximum_cost <= 0:
        errors.append(
            "Maximum unit cost must be greater than 0."
        )

    if maximum_lead_time <= 0:
        errors.append(
            "Maximum lead time must be greater than 0."
        )

    if minimum_quality < 0 or minimum_quality > 100:
        errors.append(
            "Minimum quality must be between 0 and 100."
        )

    if errors:
        return False, errors

    return True, []


def validate_vendor_data(df):
    """
    Validate the vendor dataset.
    """

    required_columns = [
        "Vendor",
        "Category",
        "Unit Cost",
        "Quality Score",
        "Lead Time",
        "On-Time %",
        "Defect %",
        "Capacity"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        return False, [
            f"Missing column: {column}"
            for column in missing_columns
        ]

    numeric_columns = [
        "Unit Cost",
        "Quality Score",
        "Lead Time",
        "On-Time %",
        "Defect %",
        "Capacity"
    ]

    for column in numeric_columns:
        if df[column].isna().any():
            return False, [
                f"Missing numeric value found in: {column}"
            ]

    return True, []
