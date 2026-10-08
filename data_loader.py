import os
import pandas as pd


REQUIRED_COLUMNS = [
    "Vendor",
    "Category",
    "Unit Cost",
    "Quality Score",
    "Lead Time",
    "On-Time %",
    "Defect %",
    "Capacity"
]


def get_data_path():
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "vendors.csv"
    )


def load_vendor_data():
    """
    Load the ProcureIQ vendor dataset.
    """

    data_path = get_data_path()

    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"Vendor dataset not found: {data_path}"
        )

    df = pd.read_csv(data_path)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    return df