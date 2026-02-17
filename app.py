import streamlit as st
import pickle
import requests
from bs4 import BeautifulSoup
import re

# -----------------------------
# CONFIG
# -----------------------------
NEWS_API_KEY = st.secrets["468e3b8c85624a468fd4b862347a813f"]

TRUSTED_SOURCES = [
    "bbc-news",
    "reuters",
    "cnn",
    "the-hindu",
    "the-times-of-india",
    "ndtv"
]

MIN_WORDS_REQUIRED = 8

# -----------------------------
# LOAD MODEL
# -----------------------------
model = pickle.load(open("fake_news_model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# -----------------------------
# FUNCTIONS
# -----------------------------

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, "html.parser")

        paragraphs = soup.find_all("p")
        article_text = " ".join([p.get_text() for p in paragraphs])

        return article_text
    except:
        return None


def search_verified_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()

    verified_articles = []

    if data.get("articles"):
        for article in data["articles"]:
            if article["source"]["id"] in TRUSTED_SOURCES:
                verified_articles.append({
                    "title": article["title"],
                    "url": article["url"]
                })

    return verified_articles[:3]


def analyze_text(text):
    text_vec = vectorizer.transform([text])
    prediction = model.predict(text_vec)[0]
    probability = model.predict_proba(text_vec)[0][1]  # Probability of real

    return prediction, probability


# -----------------------------
# STREAMLIT UI
# -----------------------------

st.title("📰 AI News Credibility & Verification System")

user_input = st.text_area("Enter news text, claim, or article URL:")

if st.button("Analyze"):

    if not user_input.strip():
        st.warning("Please enter some text or URL.")
        st.stop()

    # Detect URL
    if user_input.startswith("http"):
        st.info("🔍 Extracting article content from URL...")
        extracted_text = extract_text_from_url(user_input)

        if not extracted_text or len(extracted_text.split()) < MIN_WORDS_REQUIRED:
            st.error("Could not extract sufficient article content.")
            st.stop()

        text_to_analyze = extracted_text
    else:
        text_to_analyze = user_input

        if len(text_to_analyze.split()) < MIN_WORDS_REQUIRED:
            st.warning("⚠ Please enter a more detailed claim or article.")
            st.stop()

    # Analyze using ML
    prediction, probability = analyze_text(text_to_analyze)

    # Search trusted news
    verified_articles = search_verified_news(user_input)

    explanation = []

    if verified_articles:
        st.success("🟢 Related articles found from trusted sources.")
        for article in verified_articles:
            st.markdown(f"- [{article['title']}]({article['url']})")
        explanation.append("Trusted news sources are reporting related information.")
    else:
        explanation.append("No trusted sources reporting this claim were found.")

    # ML score interpretation
    if probability > 0.70:
        verdict = "🟢 Likely Reliable"
        explanation.append("Language patterns align with credible reporting.")
    elif probability > 0.45:
        verdict = "🟡 Use Caution"
        explanation.append("Language appears neutral but verification is limited.")
    else:
        verdict = "🔴 Likely Unreliable"
        explanation.append("Language resembles misleading or sensational content.")

    # Soften verdict if trusted articles exist
    if verified_articles and verdict == "🔴 Likely Unreliable":
        verdict = "🟡 Use Caution"
        explanation.append("Presence of trusted reporting reduces risk.")

    # Output
    st.subheader("Verdict:")
    st.write(verdict)

    st.subheader("Confidence Score:")
    st.write(f"{round(probability * 100, 2)}%")

    st.subheader("Explanation:")
    for line in explanation:
        st.write(f"- {line}")
