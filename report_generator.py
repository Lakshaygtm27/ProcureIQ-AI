from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def generate_procurement_report(
    scored_df,
    evaluated_df,
    quantity,
    maximum_cost,
    maximum_lead_time,
    minimum_quality,
    cost_weight,
    quality_weight,
    lead_time_weight
):
    """
    Generate a downloadable PDF procurement report.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "ProcureIQ - Procurement Recommendation Report",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 8))

    story.append(
        Paragraph(
            "AI-Assisted Vendor Selection & Procurement "
            "Decision Support",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "<b>Purchase Requirements</b>",
            styles["Heading2"]
        )
    )

    requirements = [
        ["Required Quantity", str(quantity)],
        ["Maximum Unit Cost", f"{maximum_cost:.2f}"],
        ["Maximum Lead Time", f"{maximum_lead_time} days"],
        ["Minimum Quality", str(minimum_quality)],
    ]

    table = Table(
        requirements,
        colWidths=[70 * mm, 70 * mm]
    )

    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "<b>Scoring Weights</b>",
            styles["Heading2"]
        )
    )

    weights = [
        ["Cost", f"{cost_weight * 100:.0f}%"],
        ["Quality", f"{quality_weight * 100:.0f}%"],
        ["Lead Time", f"{lead_time_weight * 100:.0f}%"],
    ]

    weight_table = Table(
        weights,
        colWidths=[70 * mm, 70 * mm]
    )

    weight_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(weight_table)
    story.append(Spacer(1, 15))

    if len(scored_df) > 0:

        top_vendor = scored_df.iloc[0]

        story.append(
            Paragraph(
                "<b>Recommended Vendor</b>",
                styles["Heading2"]
            )
        )

        story.append(
            Paragraph(
                f"<b>{top_vendor['Vendor']}</b> "
                f"with a final score of "
                f"<b>{top_vendor['Final Score']:.2f}/100</b>.",
                styles["Normal"]
            )
        )

        story.append(Spacer(1, 10))

        columns = [
            "Rank",
            "Vendor",
            "Unit Cost",
            "Quality Score",
            "Lead Time",
            "Final Score"
        ]

        report_data = [columns]

        for _, row in scored_df.head(10).iterrows():

            report_data.append(
                [
                    str(row["Rank"]),
                    str(row["Vendor"]),
                    f"{row['Unit Cost']:.2f}",
                    f"{row['Quality Score']:.1f}",
                    str(row["Lead Time"]),
                    f"{row['Final Score']:.2f}",
                ]
            )

        ranking_table = Table(
            report_data,
            repeatRows=1
        )

        ranking_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkgrey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("PADDING", (0, 0), (-1, -1), 5),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]
            )
        )

        story.append(ranking_table)

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "<b>Methodology</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            "Vendor eligibility is determined using capacity, "
            "cost, lead-time and quality requirements. Eligible "
            "vendors are ranked using deterministic weighted "
            "scoring. Gemini AI is used only for explanations "
            "and procurement Q&A and does not modify the official "
            "ranking.",
            styles["Normal"]
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()