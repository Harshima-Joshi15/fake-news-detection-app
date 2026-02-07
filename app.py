import streamlit as st
import re
import requests
from newspaper import Article
from bs4 import BeautifulSoup

st.set_page_config(page_title="Fake News Detector", layout="centered")

st.title("📰 Fake News Detection App")
st.caption("AI-powered news authenticity checker")

news_input = st.text_area(
    "📝 Paste news article OR news link",
    height=200,
    placeholder="Paste full news text or URL here..."
)

def is_url(text):
    return bool(re.search(r"https?://\S+", text))

def extract_with_newspaper(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return None

def extract_with_bs(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])

        return text
    except:
        return None

def analyze_news(text):
    reasons = []

    if len(text.split()) < 80:
        reasons.append("Article is very short")

    sensational_words = [
        "shocking", "breaking", "exposed", "secret",
        "you won't believe", "miracle", "guaranteed"
    ]

    for word in sensational_words:
        if word in text.lower():
            reasons.append(f"Uses sensational phrase: '{word}'")
            break

    if not any(word in text.lower() for word in ["said", "reported", "according to", "stated"]):
        reasons.append("Lacks formal journalistic attribution")

    if len(reasons) == 0:
        return "Likely Real", "Language, length, and structure resemble credible journalism."

    if len(reasons) >= 3:
        return "Likely Fake", "; ".join(reasons)

    return "Uncertain", "; ".join(reasons)

if st.button("🔍 Check News"):
    if news_input.strip() == "":
        st.warning("⚠️ Please paste some text or a link.")
    else:
        text_to_check = news_input

        if is_url(news_input):
            st.info("🔗 Reading article from link...")

            text = extract_with_newspaper(news_input)

            if not text or len(text.split()) < 50:
                st.warning("⚠️ Primary extraction failed. Trying alternate method...")
                text = extract_with_bs(news_input)

            if not text or len(text.split()) < 50:
                st.error("❌ This website blocks automatic reading (common for MSN, Google News).")
                st.info("👉 Please copy-paste the article text manually.")
                st.stop()

            text_to_check = text
            st.success("✅ Article content extracted successfully.")

        result, explanation = analyze_news(text_to_check)

        if result == "Likely Real":
            st.success("✅ **Likely Real News**")
        elif result == "Likely Fake":
            st.error("❌ **Likely Fake News**")
        else:
            st.warning("⚠️ **Uncertain**")

        st.subheader("🧠 Explanation")
        st.write(explanation)
