import streamlit as st
from newspaper import Article
import re
from urllib.parse import urlparse

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Fake News Detection App",
    page_icon="📰",
    layout="centered"
)

TRUSTED_SOURCES = [
    "ndtv.com", "bbc.com", "reuters.com", "thehindu.com",
    "cnn.com", "timesofindia.indiatimes.com", "hindustantimes.com"
]

SENSATIONAL_WORDS = [
    "guaranteed", "shocking", "breaking", "exposed",
    "unbelievable", "secret", "viral", "click here"
]

# ---------------- FUNCTIONS ----------------
def extract_article(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text

def get_domain(url):
    return urlparse(url).netloc.lower()

def analyze_text(text, source_domain=None):
    score = 50
    reasons = []

    word_count = len(text.split())

    if word_count > 300:
        score += 20
        reasons.append("Article has sufficient length.")
    elif word_count < 80:
        score -= 20
        reasons.append("Article is very short.")

    sensational_hits = [
        word for word in SENSATIONAL_WORDS
        if re.search(rf"\b{word}\b", text.lower())
    ]

    if sensational_hits:
        score -= 25
        reasons.append(f"Sensational words detected: {', '.join(sensational_hits)}")

    if source_domain:
        for trusted in TRUSTED_SOURCES:
            if trusted in source_domain:
                score += 30
                reasons.append(f"Trusted news source detected ({trusted}).")
                break

    score = max(0, min(score, 100))

    if score >= 70:
        verdict = "✅ Likely Real News"
    elif score >= 40:
        verdict = "⚠️ Suspicious"
    else:
        verdict = "❌ Likely Fake News"

    return verdict, score, reasons

# ---------------- UI ----------------
st.title("📰 Fake News Detection App")
st.caption("AI-powered news credibility analyzer")

input_text = st.text_area(
    "📌 Paste news article text or news URL",
    height=220,
    placeholder="Paste full article text or URL here..."
)

if st.button("🔍 Check News"):
    if not input_text.strip():
        st.warning("Please enter text or a URL.")
    else:
        with st.spinner("Analyzing content..."):
            try:
                if input_text.startswith("http"):
                    st.info("Reading article from link...")
                    text = extract_article(input_text)
                    domain = get_domain(input_text)
                else:
                    text = input_text
                    domain = None

                verdict, score, reasons = analyze_text(text, domain)

                st.subheader(verdict)
                st.metric("Credibility Score", f"{score}%")

                st.subheader("🧠 Explanation")
                for r in reasons:
                    st.write("•", r)

            except Exception as e:
                st.error("Could not analyze this content.")
