import streamlit as st
import pickle
from newspaper import Article
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Fake News Detection",
    page_icon="📰",
    layout="centered"
)

# ---------------- LOAD ML ASSETS ----------------
MODEL_PATH = "model/fake_news_model.pkl"
VECTORIZER_PATH = "model/vectorizer.pkl"

model = pickle.load(open(MODEL_PATH, "rb"))
vectorizer = pickle.load(open(VECTORIZER_PATH, "rb"))

TRUSTED_SOURCES = [
    "msn.com",
    "ndtv.com",
    "bbc.com",
    "reuters.com",
    "cnn.com",
    "thehindu.com",
    "indiatoday.in",
    "timesofindia.indiatimes.com",
    "hindustantimes.com"
]

# ---------------- ARTICLE EXTRACTION ----------------
def extract_article_primary(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip()
    except:
        return ""

def extract_article_fallback(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)
        return text.strip()
    except:
        return ""

# ---------------- PREDICTION LOGIC ----------------
def predict_news(text, url=None):
    reasons = []

    if len(text.split()) < 40:
        return (
            "🟡 Uncertain",
            55,
            ["Could not extract enough readable article text from the link"]
        )

    vec = vectorizer.transform([text])
    prob_real = model.predict_proba(vec)[0][1]
    final_score = prob_real

    if url:
        domain = urlparse(url).netloc.lower()
        if any(src in domain for src in TRUSTED_SOURCES):
            final_score = min(final_score + 0.25, 1.0)
            reasons.append("Published by a trusted news source")

    if final_score >= 0.75:
        label = "🟢 Likely Real"
    elif final_score >= 0.45:
        label = "🟡 Uncertain"
    else:
        label = "🔴 Likely Misleading"

    reasons.append(f"ML model confidence: {round(prob_real * 100, 2)}%")

    return label, round(final_score * 100, 2), reasons

# ---------------- UI ----------------
st.title("📰 Fake News Detection App")
st.caption("ML-powered news credibility analyzer")

user_input = st.text_area(
    "📌 Paste news article text or a news URL",
    height=220,
    placeholder="Paste a full news article OR a news link here..."
)

if st.button("🔍 Analyze News"):
    if not user_input.strip():
        st.warning("Please enter text or a URL.")
    else:
        with st.spinner("Analyzing content..."):
            try:
                if user_input.startswith("http"):
                    text = extract_article_primary(user_input)

                    if len(text.split()) < 50:
                        text = extract_article_fallback(user_input)

                    label, score, reasons = predict_news(text, user_input)
                else:
                    label, score, reasons = predict_news(user_input)

                st.subheader(label)
                st.progress(score / 100)
                st.metric("Credibility Score", f"{score}%")

                st.subheader("🧠 Explanation")
                for r in reasons:
                    st.write("•", r)

            except Exception as e:
                st.error("Unable to analyze this content.")
