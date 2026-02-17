import streamlit as st
import requests
from bs4 import BeautifulSoup

NEWS_API_KEY = st.secrets["NEWS_API_KEY"]

st.title("Fake News Detection & Verification")

user_input = st.text_input("Enter a news claim or paste a URL:")
analyze = st.button("Analyze")


def fetch_related_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&language=en&sortBy=relevancy"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "ok":
        return data["articles"]
    return []

def check_url_readability(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])

        if len(text) > 500:
            return True, text[:500]
        else:
            return False, ""
    except:
        return False, ""

if analyze and user_input:


    # Case 1: User entered a URL
    if user_input.startswith("http"):

        readable, preview = check_url_readability(user_input)

        if readable:
            st.success("The article is readable and appears properly structured.")
            st.write("It is most likely true, but always cross-check with trusted sources.")

            st.subheader("Article Preview:")
            st.write(preview + "...")

        else:
            st.error("This article appears unreliable.")
            st.write("Reasons:")
            st.write("- The content could not be properly extracted.")
            st.write("- The website may not be a trusted news source.")
            st.write("- The formatting is not ideal or lacks structured reporting.")

        st.subheader("Verified News Related To This Topic:")
        related_news = fetch_related_news(user_input)

        if related_news:
            for article in related_news[:5]:
                st.markdown(f"- [{article['title']}]({article['url']})")
        else:
            st.write("No verified coverage found in trusted outlets.")

    # Case 2: User entered a claim
    else:

        st.info("Analyzing claim and searching trusted sources...")

        related_news = fetch_related_news(user_input)

        if related_news:
            st.success("Related coverage found in trusted news sources.")
            st.write("This claim is most likely TRUE because similar reports exist in recognized media.")

            st.subheader("Trusted Sources Reporting This:")
            for article in related_news[:5]:
                st.markdown(f"- [{article['title']}]({article['url']})")

        else:
            st.error("No trusted news coverage found.")
            st.write("This claim is most likely UNRELIABLE because:")
            st.write("- No major news outlets are reporting this.")
            st.write("- It may be a rumor or unverified information.")

            st.subheader("You may prefer checking verified sources manually.")

