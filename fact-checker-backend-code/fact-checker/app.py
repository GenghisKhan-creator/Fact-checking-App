import streamlit as st
import requests
import os
from dotenv import load_dotenv
import subprocess
import PyPDF2
import re


# Load environment variables
load_dotenv()

# Get API keys from .env
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Streamlit UI
st.title("🧠 Simple AI Fact Checker - Claim Extraction & Verification")

uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_claims(text):
    prompt = f"""
Extract all claims or statements presented as facts from the text below. Claims can be true, false, or unverifiable.

Text:
{text}

List of claims:
"""
    result = subprocess.run(
        ["ollama", "run", "llama3"],
        input=prompt.encode("utf-8"),
        capture_output=True
    )
    output = result.stdout.decode("utf-8")

    # Extract bullet points or numbered list items, or fallback split by newlines
    matches = re.findall(r"(?:^|\n)[-•\d.]+\s+(.*?)(?=\n|$)", output)
    if matches:
        return [claim.strip() for claim in matches if claim.strip()]
    else:
        # fallback: split output by new lines and filter empty lines
        return [line.strip("-•0123456789. ").strip() for line in output.split("\n") if line.strip()]

def web_search(query):
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
        "num": 5,
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = []

    for result in data.get("organic_results", []):
        results.append(result.get("snippet", ""))

    return " ".join(results)

def check_with_llama3(statement, context):
    prompt = f"""
You are a fact checker. Given a statement and some web context, determine if it's true, false, or unverifiable.

Statement: {statement}
Snippets: {context}

Respond with one of: True, False, Unverifiable. Then explain briefly why.
"""
    result = subprocess.run(
        ["ollama", "run", "llama3"],
        input=prompt.encode("utf-8"),
        capture_output=True
    )
    return result.stdout.decode("utf-8")

if uploaded_file:
    with st.spinner("Reading PDF..."):
        text = extract_text_from_pdf(uploaded_file)
        st.subheader("Extracted Text (Preview)")
        st.write(text[:1000] + "...")  # Preview first 1000 chars

    with st.spinner("Extracting claims..."):
        claims = extract_claims(text)
        st.subheader(f"🧾 Claims Found ({len(claims)}):")
        for claim in claims:
            st.markdown(f"• {claim}")

    with st.spinner("Fact-checking claims..."):
        st.subheader("✅ Fact Check Results")
        for claim in claims:
            snippets = web_search(claim)
            verdict = check_with_llama3(claim, snippets)
            st.markdown(f"**Claim:** {claim}")
            st.write(verdict)
            st.markdown("---")
