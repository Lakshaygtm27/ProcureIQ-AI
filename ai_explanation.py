import os
import streamlit as st
from google import genai


def get_gemini_client():
    """
    Create Gemini client using Streamlit secrets
    or environment variables.
    """

    api_key = None

    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass

    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "Gemini API key is not configured."
        )

    return genai.Client(api_key=api_key)


def generate_vendor_explanation(
    vendor,
    score,
    cost,
    quality,
    lead_time,
    cost_contribution,
    quality_contribution,
    lead_time_contribution
):
    """
    Generate an AI explanation for the deterministic
    vendor recommendation.

    Gemini explains the decision but does NOT
    calculate or change the official ranking.
    """

    client = get_gemini_client()

    prompt = f"""
You are ProcureIQ's procurement decision-support assistant.

Explain why the following vendor was selected by a
deterministic procurement scoring system.

Vendor: {vendor}

Final Score: {score:.2f}/100

Unit Cost: {cost}

Quality Score: {quality}

Lead Time: {lead_time} days

Cost Contribution: {cost_contribution:.2f}

Quality Contribution: {quality_contribution:.2f}

Lead Time Contribution: {lead_time_contribution:.2f}

Important rules:

1. Do not change the final score.
2. Do not recalculate or change the ranking.
3. Do not invent vendor information.
4. Explain the decision using only the information provided.
5. Clearly explain the trade-offs.
6. Mention any potential procurement risk.
7. Suggest a practical next action.
8. Keep the response professional and concise.

Structure your response using these sections:

### Recommendation Rationale

Explain why this vendor ranked first.

### Key Strengths

List the most important strengths.

### Key Trade-off

Explain the main trade-off in the decision.

### Procurement Risk

Mention any relevant risk based only on the supplied data.

### Suggested Next Action

Give one practical procurement action.
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text