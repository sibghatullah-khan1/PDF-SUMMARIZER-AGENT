import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

# Streamlit secrets ya local .env se API key fetch karein
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

st.set_page_config(page_title="PDF Summarizer Agent", page_icon="📄", layout="centered")

st.title("📄 PDF Summarizer AI Agent")
st.write("Please upload your PDF file below. The agent will read it and provide a detailed summary.")

# API Key validation
if not api_key:
    st.error("⚠️ GEMINI_API_KEY environment variable ya Streamlit Secrets mein missing hai!")
    st.stop()

genai.configure(api_key=api_key)

# PDF Upload
uploaded_file = st.file_uploader("Upload your PDF document", type=["pdf"])

if uploaded_file is not None:
    st.success("PDF uploaded successfully!")
    
    with st.spinner("Extracting text from PDF..."):
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    
    if text.strip():
        if st.button("Generate Summary"):
            with st.spinner("Analyzing document and generating summary..."):
                try:
                    model = genai.GenerativeModel("gemini-3.6-flash")
                    
                    # Strict prompt to force English output
                    prompt = f"""
                    You are an expert document summarizer AI agent.
                    Read the following extracted document text carefully and provide a comprehensive, well-structured, clear summary.

                    STRICT REQUIREMENT: Provide the entire summary ALWAYS in English, regardless of the input document language.

                    Document Text:
                    {text[:30000]}  # Limiting character count for token limits if needed
                    """
                    
                    response = model.generate_content(prompt)
                    
                    st.subheader("📌 Key Insights & Summary")
                    st.write(response.text)
                    
                except Exception as e:
                    st.error(f"An error occurred while generating summary: {e}")
    else:
        st.warning("Could not extract any readable text from this PDF. It might be scanned or image-based.")