import streamlit as st
import urllib.parse
import feedparser

st.set_page_config(page_title="AI News Verification System", layout="centered")

st.title("🔍 AI News Verification System")

user_input = st.text_area("Paste a URL, claim, or full article:")
analyze = st.button("Analyze")

trusted_domains = [
    "bbc.com",
    "reuters.com",
    "ndtv.com",
    "thehindu.com",
    "hindustantimes.com",
    "timesofindia.com",
    "indiatoday.in",
    "news18.com",
    "aljazeera.com",
    "cnn.com"
]

# ---------------------------
# Extract headline from URL
# ---------------------------
def extract_headline_from_url(url):
    try:
        path = urllib.parse.urlparse(url).path
        parts = path.split("/")

        # Handle MSN-style URLs
        if len(parts) >= 3:
            headline_part = parts[-2]
        else:
            headline_part = parts[-1]

        headline = headline_part.replace("-", " ")
        headline = ''.join([i for i in headline if not i.isdigit()])
        return headline.strip()

    except:
        return ""

# ---------------------------
# Prepare search query
# ---------------------------
def prepare_query(text):
    words = text.split()
    return " ".join(words[:20])

# ---------------------------
# Fetch Google News RSS
# ---------------------------
def fetch_news(query):
    url = f"https://news.google.com/rss/search?q={query}"
    feed = feedparser.parse(url)

    articles = []
    for entry in feed.entries:
        articles.append({
            "title": entry.title,
            "url": entry.link
        })

    return articles

# ---------------------------
# MAIN LOGIC
# ---------------------------
if analyze and user_input:

    # URL case
    if user_input.startswith("http"):
        query = extract_headline_from_url(user_input)
        st.info(f"Searching coverage for: {query}")

    # Claim or article case
    else:
        query = prepare_query(user_input)
        st.info("Analyzing claim/article against trusted sources...")

    related_articles = fetch_news(query)

    if related_articles:

        trusted_matches = [
            article for article in related_articles
            if any(domain in article["url"] for domain in trusted_domains)
        ]

        total_matches = len(trusted_matches)

        confidence = min(total_matches * 15, 95)

        if confidence >= 45:
            st.success(f"✅ YES — This appears to be REAL news ({confidence}% confidence).")
            st.write("The claim/article matches multiple trusted news sources.")
            st.write("You may continue reading. Verified sources are listed below.")

        elif confidence > 0:
            st.warning(f"⚠️ Limited coverage found ({confidence}% confidence).")
            st.write("This may be new or not widely reported yet.")

        else:
            st.error("❌ No trusted coverage found.")
            st.write("This claim/article may be false, misleading, or very new.")

        if trusted_matches:
            st.subheader("📰 Trusted Sources Reporting This:")
            for article in trusted_matches[:5]:
                st.markdown(f"- [{article['title']}]({article['url']})")

    else:
        st.error("No results found in Google News.")
        st.write("This claim/article may not exist or is extremely new.")
