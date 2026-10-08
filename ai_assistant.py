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


def ask_procurement_assistant(question, vendor_context):
    """
    Ask Gemini 3.8 Flash a procurement-related question.

    Gemini explains the supplied vendor information
    but does not modify the official deterministic ranking.
    """

    client = get_gemini_client()

    prompt = f"""
You are ProcureIQ's procurement decision-support assistant.

Answer the user's question using ONLY the supplied
vendor context.

Do not invent information.

The official vendor ranking is calculated by deterministic
Python scoring and must not be changed by the AI.

Vendor context:

{vendor_context}

User question:

{question}

Provide a concise, professional, business-oriented answer.

If the supplied context is insufficient, explicitly say so.

Do not change or recalculate the official vendor ranking.

Focus on:
- vendor ranking
- cost
- quality
- lead time
- capacity
- on-time performance
- defect rate
- procurement trade-offs
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text