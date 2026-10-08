import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import load_vendor_data
from ai_explanation import generate_vendor_explanation
from ai_assistant import ask_procurement_assistant
from report_generator import generate_procurement_report

from scoring import calculate_scores
from validation import (
    validate_requirements,
    validate_vendor_data,
    validate_weights
)
from risk_engine import evaluate_vendor_eligibility


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="ProcureIQ",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .procure-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .procure-subtitle {
        font-size: 17px;
        color: #6b7280;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 650;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD VENDOR DATA
# =========================================================

try:
    df = load_vendor_data()

except Exception as e:
    st.error(f"Unable to load vendor data: {e}")
    st.stop()


# =========================================================
# DATA VALIDATION
# =========================================================

data_valid, data_errors = validate_vendor_data(df)

if not data_valid:

    st.error("Vendor dataset validation failed.")

    for error in data_errors:
        st.error(error)

    st.stop()


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="procure-title">📊 ProcureIQ</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="procure-subtitle">'
    'AI-Powered Vendor Selection & Procurement Recommender'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    "ProcureIQ uses deterministic Python scoring for vendor ranking. "
    "Gemini AI is used only for explanations and procurement Q&A."
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ Procurement Settings")

st.sidebar.subheader("Purchase Requirements")


quantity = st.sidebar.number_input(
    "Required Quantity",
    min_value=1,
    value=3000,
    step=100
)


maximum_cost = st.sidebar.number_input(
    "Maximum Unit Cost (₹)",
    min_value=1.0,
    value=900.0,
    step=10.0
)


maximum_lead_time = st.sidebar.number_input(
    "Maximum Lead Time (days)",
    min_value=1,
    value=10,
    step=1
)


minimum_quality = st.sidebar.slider(
    "Minimum Quality Score",
    min_value=0,
    max_value=100,
    value=85
)


st.sidebar.divider()

st.sidebar.subheader("Criteria Weights")


cost_weight = st.sidebar.slider(
    "Cost Weight",
    min_value=0,
    max_value=100,
    value=40
)


quality_weight = st.sidebar.slider(
    "Quality Weight",
    min_value=0,
    max_value=100,
    value=35
)


lead_time_weight = st.sidebar.slider(
    "Lead Time Weight",
    min_value=0,
    max_value=100,
    value=25
)


total_weight = (
    cost_weight
    + quality_weight
    + lead_time_weight
)


st.sidebar.metric(
    "Total Weight",
    f"{total_weight}%"
)


# =========================================================
# VALIDATE REQUIREMENTS
# =========================================================

requirements_valid, requirement_errors = validate_requirements(
    quantity,
    maximum_cost,
    maximum_lead_time,
    minimum_quality
)


if not requirements_valid:

    for error in requirement_errors:
        st.error(error)

    st.stop()


# =========================================================
# VALIDATE WEIGHTS
# =========================================================

weights_valid, weight_message = validate_weights(
    cost_weight / 100,
    quality_weight / 100,
    lead_time_weight / 100
)


if not weights_valid:

    st.error(weight_message)

    st.warning(
        "Adjust the sidebar weights so that they total exactly 100%."
    )

    st.stop()


# =========================================================
# VENDOR ELIGIBILITY
# =========================================================

evaluated_df = evaluate_vendor_eligibility(
    df,
    quantity,
    maximum_cost,
    maximum_lead_time,
    minimum_quality
)


eligible_df = evaluated_df[
    evaluated_df["Eligible"]
].copy()


# =========================================================
# DETERMINISTIC SCORING
# =========================================================

scored_df = calculate_scores(
    eligible_df,
    cost_weight / 100,
    quality_weight / 100,
    lead_time_weight / 100
)


# =========================================================
# PROCUREMENT OVERVIEW
# =========================================================

st.markdown(
    '<div class="section-title">Procurement Overview</div>',
    unsafe_allow_html=True
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Vendors Evaluated",
        len(df)
    )


with col2:

    st.metric(
        "Eligible Vendors",
        len(scored_df)
    )


with col3:

    if len(scored_df) > 0:

        st.metric(
            "Average Score",
            f"{scored_df['Final Score'].mean():.2f}"
        )

    else:

        st.metric(
            "Average Score",
            "N/A"
        )


with col4:

    if len(scored_df) > 0:

        st.metric(
            "Top Vendor",
            scored_df.iloc[0]["Vendor"]
        )

    else:

        st.metric(
            "Top Vendor",
            "None"
        )


# =========================================================
# NO ELIGIBLE VENDORS
# =========================================================

if len(scored_df) == 0:

    st.error(
        "No vendors satisfy the current procurement requirements."
    )

    st.subheader("Vendor Requirement Status")

    st.dataframe(
        evaluated_df[
            [
                "Vendor",
                "Unit Cost",
                "Quality Score",
                "Lead Time",
                "Capacity",
                "Status"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.stop()


# =========================================================
# TOP VENDOR
# =========================================================

top_vendor = scored_df.iloc[0]


st.markdown(
    '<div class="section-title">Recommended Shortlist</div>',
    unsafe_allow_html=True
)


st.success(
    f"Top-ranked vendor based on your selected criteria: "
    f"**{top_vendor['Vendor']}** "
    f"with a score of **{top_vendor['Final Score']:.2f}/100**."
)


# =========================================================
# AI PROCUREMENT EXPLANATION
# =========================================================

st.markdown(
    '<div class="section-title">🤖 AI Procurement Explanation</div>',
    unsafe_allow_html=True
)


st.caption(
    "Gemini explains the deterministic recommendation. "
    "It does not calculate or change the official ranking."
)


if st.button(
    "Explain Recommendation with Gemini",
    key="explain_button"
):

    try:

        with st.spinner(
            "Generating procurement explanation..."
        ):

            explanation = generate_vendor_explanation(
                vendor=top_vendor["Vendor"],
                score=top_vendor["Final Score"],
                cost=top_vendor["Unit Cost"],
                quality=top_vendor["Quality Score"],
                lead_time=top_vendor["Lead Time"],
                cost_contribution=top_vendor["Cost Contribution"],
                quality_contribution=top_vendor["Quality Contribution"],
                lead_time_contribution=top_vendor["Lead Time Contribution"]
            )

        st.markdown(explanation)

    except Exception as e:

        st.error(
            f"AI explanation unavailable: {e}"
        )


# =========================================================
# VENDOR RANKING
# =========================================================

st.markdown(
    '<div class="section-title">Vendor Ranking</div>',
    unsafe_allow_html=True
)


display_columns = [
    "Rank",
    "Vendor",
    "Category",
    "Unit Cost",
    "Quality Score",
    "Lead Time",
    "On-Time %",
    "Defect %",
    "Capacity",
    "Final Score"
]


st.dataframe(
    scored_df[display_columns],
    use_container_width=True,
    hide_index=True
)


# =========================================================
# VENDOR ANALYTICS
# =========================================================

st.markdown(
    '<div class="section-title">Vendor Analytics</div>',
    unsafe_allow_html=True
)


chart_col1, chart_col2 = st.columns(2)


# ---------------------------------------------------------
# SCORE CHART
# ---------------------------------------------------------

with chart_col1:

    score_chart = px.bar(
        scored_df.head(10),
        x="Final Score",
        y="Vendor",
        orientation="h",
        title="Top 10 Vendors by Final Score",
        text_auto=".2f"
    )

    score_chart.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(
        score_chart,
        use_container_width=True
    )


# ---------------------------------------------------------
# COST VS QUALITY
# ---------------------------------------------------------

with chart_col2:

    scatter_chart = px.scatter(
        scored_df,
        x="Unit Cost",
        y="Quality Score",
        size="Capacity",
        color="Final Score",
        hover_name="Vendor",
        title="Cost vs Quality",
        color_continuous_scale="Viridis"
    )

    st.plotly_chart(
        scatter_chart,
        use_container_width=True
    )


chart_col3, chart_col4 = st.columns(2)


# ---------------------------------------------------------
# LEAD TIME CHART
# ---------------------------------------------------------

with chart_col3:

    lead_chart = px.bar(
        scored_df.head(10),
        x="Vendor",
        y="Lead Time",
        title="Lead Time Comparison",
        text_auto=True
    )

    st.plotly_chart(
        lead_chart,
        use_container_width=True
    )


# ---------------------------------------------------------
# SCORE CONTRIBUTION
# ---------------------------------------------------------

with chart_col4:

    contribution_df = pd.DataFrame(
        {
            "Criterion": [
                "Cost",
                "Quality",
                "Lead Time"
            ],
            "Contribution": [
                top_vendor["Cost Contribution"],
                top_vendor["Quality Contribution"],
                top_vendor["Lead Time Contribution"]
            ]
        }
    )

    contribution_chart = px.bar(
        contribution_df,
        x="Criterion",
        y="Contribution",
        title=f"Score Contribution — {top_vendor['Vendor']}",
        text_auto=".2f"
    )

    st.plotly_chart(
        contribution_chart,
        use_container_width=True
    )


# =========================================================
# REQUIREMENT STATUS
# =========================================================

st.markdown(
    '<div class="section-title">Vendor Requirement Status</div>',
    unsafe_allow_html=True
)


status_df = evaluated_df[
    [
        "Vendor",
        "Unit Cost",
        "Quality Score",
        "Lead Time",
        "Capacity",
        "Status"
    ]
].copy()


st.dataframe(
    status_df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# PDF PROCUREMENT REPORT
# =========================================================

st.markdown(
    '<div class="section-title">📄 Procurement Report</div>',
    unsafe_allow_html=True
)


st.caption(
    "Generate a professional PDF containing the procurement "
    "requirements, scoring weights and vendor ranking."
)


try:

    pdf_data = generate_procurement_report(
        scored_df=scored_df,
        evaluated_df=evaluated_df,
        quantity=quantity,
        maximum_cost=maximum_cost,
        maximum_lead_time=maximum_lead_time,
        minimum_quality=minimum_quality,
        cost_weight=cost_weight / 100,
        quality_weight=quality_weight / 100,
        lead_time_weight=lead_time_weight / 100
    )

    st.download_button(
        label="📥 Download Procurement Report (PDF)",
        data=pdf_data,
        file_name="ProcureIQ_Procurement_Report.pdf",
        mime="application/pdf",
        key="pdf_download"
    )

except Exception as e:

    st.error(
        f"Unable to generate procurement report: {e}"
    )


# =========================================================
# AI PROCUREMENT ASSISTANT
# =========================================================

st.markdown(
    '<div class="section-title">🤖 ProcureIQ AI Assistant</div>',
    unsafe_allow_html=True
)


st.caption(
    "Ask questions about the current vendor shortlist. "
    "The AI uses the ranked vendor context and does not "
    "modify the official ranking."
)


question = st.text_input(
    "Ask a procurement question",
    placeholder="Example: Why was the top vendor selected?",
    key="procurement_question"
)


if question.strip():

    context_columns = [
        "Rank",
        "Vendor",
        "Category",
        "Unit Cost",
        "Quality Score",
        "Lead Time",
        "On-Time %",
        "Defect %",
        "Capacity",
        "Final Score"
    ]

    vendor_context = scored_df[
        context_columns
    ].head(10).to_string(index=False)

    try:

        with st.spinner(
            "Analyzing procurement data..."
        ):

            answer = ask_procurement_assistant(
                question,
                vendor_context
            )

        st.markdown("### AI Answer")

        st.markdown(answer)

    except Exception as e:

        st.error(
            f"AI assistant unavailable: {e}"
        )


# =========================================================
# METHODOLOGY
# =========================================================

with st.expander(
    "📘 How ProcureIQ Calculates the Ranking"
):

    st.markdown(
        """
        ### Step 1 — Requirement Validation

        The application validates quantity, maximum cost,
        maximum lead time and minimum quality.

        ### Step 2 — Eligibility

        Vendors are checked against the buyer's requirements.

        ### Step 3 — Normalization

        **Cost and Lead Time**

        Lower values receive higher normalized scores.

        **Quality**

        Higher quality receives a higher normalized score.

        ### Step 4 — Weighted Scoring

        The final score is calculated as:

        **Final Score =**

        `Cost Score × Cost Weight`

        `+ Quality Score × Quality Weight`

        `+ Lead Time Score × Lead Time Weight`

        ### Step 5 — Ranking

        Vendors are sorted by their deterministic final score.

        ### Step 6 — AI Explanation

        Gemini explains the recommendation and answers
        procurement questions.

        **Important:** Gemini does not calculate or modify
        the official vendor ranking.
        """
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()


st.caption(
    "ProcureIQ | AI-Assisted Procurement Decision Support | "
    "Deterministic scoring + Gemini explanations"
)