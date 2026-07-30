"""
PDF Summarizer AI Agent using Google Gemini API & Streamlit.
Layout: Title -> Summary (Middle) -> File Uploader & Compact Button (Bottom).
"""

import os
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

# Fetch API Key from environment or Streamlit Secrets
api_key = os.getenv("GEMINI_API_KEY") or (
    st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
)

# Page Setup
st.set_page_config(
    page_title="PDF Summarizer Agent", page_icon="📄", layout="centered"
)

# 1. TOP: Title Section
st.title("📄 PDF Summarizer AI Agent")
st.write("Upload your PDF document below to generate detailed insights.")

# API Key Validation
if not api_key:
    st.error(
        "⚠️ GEMINI_API_KEY is missing! Please set it in your .env file or Streamlit Secrets."
    )
    st.stop()

# Configure Gemini Client
genai.configure(api_key=api_key)


def extract_pdf_text(uploaded_file) -> str:
    """Extracts text content page-by-page from the uploaded PDF."""
    try:
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return ""


# 2. MIDDLE: Placeholder container for Summary (To display between Title & Uploader)
summary_container = st.container()

st.markdown("---")

# 3. BOTTOM: PDF Upload Option & Compact Button
uploaded_file = st.file_uploader("Upload your PDF document", type=["pdf"])

if uploaded_file is not None:
    # Use columns to make the button compact/smaller
    col1, col2, _ = st.columns([2, 1, 1])
    
    with col1:
        st.caption(f"Selected: **{uploaded_file.name}**")
        
    with col2:
        generate_btn = st.button("✨ Generate Summary", use_container_width=False)

    if generate_btn:
        with st.spinner("Extracting text and analyzing document with Gemini..."):
            extracted_text = extract_pdf_text(uploaded_file)

            if not extracted_text:
                summary_container.warning(
                    "Could not extract any readable text from this PDF. It might be scanned or image-based."
                )
            else:
                try:
                    # Using recommended latest Gemini flash model endpoint
                    model = genai.GenerativeModel("gemini-3.6-flash")

                    prompt = f"""
                    You are an expert document summarizer AI agent.
                    Read the following extracted document text carefully and provide a comprehensive, well-structured executive summary.
                    Use section headings, bullet points, and key takeaways.

                    STRICT REQUIREMENT: Provide the entire summary ALWAYS in clear English.

                    Document Text:
                    {extracted_text[:40000]}
                    """

                    response = model.generate_content(prompt)

                    # Display Summary inside Middle Container
                    with summary_container:
                        st.subheader("📌 Key Insights & Summary")
                        st.markdown(response.text)

                except Exception as e:
                    summary_container.error(f"An error occurred while generating summary: {e}")