import streamlit as st
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="News Credibility Checker",
    page_icon="📰",
    layout="centered"
)

# ---------------- TRUSTED SOURCES ----------------
TRUSTED_SOURCES = [
    "msn.com",
    "economictimes.com",
    "ndtv.com",
    "bbc.com",
    "reuters.com",
    "cnn.com",
    "thehindu.com",
    "indiatoday.in",
    "hindustantimes.com",
    "timesofindia.indiatimes.com"
]

CLICKBAIT_PHRASES = [
    "you won’t believe",
    "shocking",
    "breaking",
    "secret",
    "exposed",
    "goes viral",
    "must read",
    "what happened next"
]

# ---------------- ARTICLE EXTRACTION ----------------
def extract_text(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    return " ".join(p.get_text() for p in paragraphs)

# ---------------- ANALYSIS ----------------
def analyze_article(text, url=None):
    reasons = []
    score = 0.5  # neutral base

    # ---- SOURCE CHECK ----
    if url:
        domain = urlparse(url).netloc.lower()
        if any(src in domain for src in TRUSTED_SOURCES):
            score += 0.35
            reasons.append("Source is a well-known and trusted news organization.")
        else:
            score -= 0.2
            reasons.append("Source is unknown or not widely trusted.")

    # ---- LANGUAGE CHECK ----
    text_lower = text.lower()

    clickbait_hits = sum(1 for p in CLICKBAIT_PHRASES if p in text_lower)
    if clickbait_hits > 0:
        score -= 0.2
        reasons.append("Article uses sensational or clickbait-style language.")

    if re.search(r"\b[A-Z]{4,}\b", text):
        score -= 0.1
        reasons.append("Excessive capitalization detected, often used in misleading content.")

    if len(text.split()) < 80:
        score -= 0.15
        reasons.append("Article text is very short, limiting credibility assessment.")

    # ---- FINAL LABEL ----
    score = max(0, min(score, 1))

    if score >= 0.7:
        label = "🟢 Likely Reliable News"
    elif score >= 0.45:
        label = "🟡 Use Caution"
    else:
        label = "🔴 Likely Unreliable"

    return label, round(score * 100, 2), reasons

# ---------------- UI ----------------
st.title("📰 News Credibility Checker")
st.caption("Checks source reliability and writing quality — not fake news guessing.")

user_input = st.text_area(
    "Paste a news article or URL",
    height=220,
    placeholder="Paste a news article or a news website link..."
)

if st.button("🔍 Analyze"):
    if not user_input.strip():
        st.warning("Please enter some text or a URL.")
    else:
        with st.spinner("Analyzing credibility..."):
            try:
                if user_input.startswith("http"):
                    text = extract_text(user_input)
                    label, score, reasons = analyze_article(text, user_input)
                else:
                    label, score, reasons = analyze_article(user_input)

                st.subheader(label)
                st.progress(score / 100)
                st.metric("Credibility Score", f"{score}%")

                st.subheader("🧠 Explanation")
                for r in reasons:
                    st.write("•", r)

            except Exception:
                st.error("Unable to analyze this content. The website may block access.")
