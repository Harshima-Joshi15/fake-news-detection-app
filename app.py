import streamlit as st
import requests
import urllib.parse

NEWS_API_KEY = st.secrets["NEWS_API_KEY"]

st.title("AI News Verification System")

user_input = st.text_area("Paste a URL, claim, or article:")
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
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "ok":
        return data["articles"]
    return []

def extract_headline_from_url(url):
    try:
        path = urllib.parse.urlparse(url).path
        parts = path.split("/")
        
        # MSN format: headline is second last part
        if len(parts) >= 3:
            headline_part = parts[-2]
        else:
            headline_part = parts[-1]

        headline = headline_part.replace("-", " ")
        headline = ''.join([i for i in headline if not i.isdigit()])
        return headline.strip()
    except:
        return ""


def prepare_query(text):
    words = text.split()
    return " ".join(words[:20])  # use first 20 words only

if analyze and user_input:

    # If URL
    if user_input.startswith("http"):
        query = extract_headline_from_url(user_input)
        st.info(f"Searching trusted coverage for: {query}")

    # If claim or article
    else:
        query = prepare_query(user_input)
        st.info("Analyzing claim/article against trusted sources...")

    related_articles = fetch_news(query)

    if related_articles:

        trusted_matches = [
            article for article in related_articles
            if any(domain in article["url"] for domain in trusted_domains)
        ]

        confidence = min(len(trusted_matches) * 20, 95)

        if confidence > 40:
            st.success(f"YES — This appears to be REAL news ({confidence}% confidence).")
            st.write("The claim/article matches trusted news coverage.")
            st.write("You may continue reading. Trusted sources are listed below.")

        else:
            st.warning(f"This seems UNVERIFIED or potentially unreliable ({confidence}% confidence).")
            st.write("Limited trusted coverage found. Please verify using sources below.")

        st.subheader("Trusted Sources Reporting This:")
        for article in trusted_matches[:5]:
            st.markdown(f"- [{article['title']}]({article['url']})")

    else:
        st.error("No trusted coverage found. This claim/article may be false or very new.")
