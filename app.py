import streamlit as st
import pickle
import requests
import re

# -----------------------------
# CONFIG
# -----------------------------
NEWS_API_KEY = "468e3b8c85624a468fd4b862347a813f"

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

user_input = st.text_area("Enter news text or claim:")

if st.button("Analyze"):

    if not user_input.strip():
        st.warning("Please enter some text.")
        st.stop()

    word_count = len(user_input.split())

    if word_count < MIN_WORDS_REQUIRED:
        st.warning("⚠ Please enter a full claim or article. Short keywords cannot be verified reliably.")
        st.stop()

    prediction, probability = analyze_text(user_input)

    verified_articles = search_verified_news(user_input)

    # -----------------------------
    # DECISION LOGIC (Improved)
    # -----------------------------

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
        explanation.append("Language is neutral but verification is limited.")
    else:
        verdict = "🔴 Likely Unreliable"
        explanation.append("Language patterns resemble misleading or sensational content.")

    # If trusted articles exist, soften harsh verdict
    if verified_articles and verdict == "🔴 Likely Unreliable":
        verdict = "🟡 Use Caution"
        explanation.append("However, presence of trusted sources reduces risk.")

    # -----------------------------
    # OUTPUT
    # -----------------------------

    st.subheader("Verdict:")
    st.write(verdict)

    st.subheader("Confidence Score:")
    st.write(f"{round(probability * 100, 2)}%")

    st.subheader("Explanation:")
    for line in explanation:
        st.write(f"- {line}")
