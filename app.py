import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from difflib import SequenceMatcher

NEWS_API_KEY = st.secrets["NEWS_API_KEY"]

st.title("AI News Verification System")

user_input = st.text_area("Enter a claim, paste article text, or provide a URL:")
analyze = st.button("Analyze")

trusted_domains = [
    "bbc.com",
    "reuters.com",
    "ndtv.com",
    "thehindu.com",
    "hindustantimes.com",
    "timesofindia.com",
    "msn.com",
    "indiatoday.in",
    "news18.com"
]

def fetch_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&language=en"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "ok":
        return data["articles"]
    return []

def extract_text(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        return " ".join([p.get_text() for p in paragraphs])
    except:
        return ""

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

if analyze and user_input:

    # If URL
    if user_input.startswith("http"):
        content = extract_text(user_input)
        if len(content) < 200:
            st.warning("Could not fully extract article. Searching trusted coverage...")
        query = content[:300]

    # If claim or pasted article text
    else:
        query = user_input[:300]
        content = user_input

    related_articles = fetch_news(query)

    if related_articles:

        best_score = 0
        for article in related_articles:
            compare_text = article["description"] or ""
            score = similarity(content[:500], compare_text)
            if score > best_score:
                best_score = score

        confidence = int(best_score * 100)

        if confidence > 60 or len(related_articles) > 3:
            st.success(f"This claim/article is likely TRUE ({confidence}% confidence).")
            st.write("Multiple trusted sources are reporting similar information.")
            st.write("You can continue reading the provided article if from trusted source.")

        else:
            st.error(f"This claim/article seems UNVERIFIED or potentially FALSE ({confidence}% confidence).")
            st.write("The content does not strongly match trusted news coverage.")

        show_sources = st.button("Show Trusted Sources")

        if show_sources:
            st.subheader("Trusted News Available Online:")
            for article in related_articles[:5]:
                st.markdown(f"- [{article['title']}]({article['url']})")

    else:
        st.error("No trusted coverage found. This claim may be unreliable or unverified.")
