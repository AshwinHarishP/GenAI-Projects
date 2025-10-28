import streamlit as st
import requests
from bs4 import BeautifulSoup

from chain import Chain
from portfolio import Portfolio
from utils import clean_text


def get_page_text(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=15)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch page (Status: {res.status_code})")
    soup = BeautifulSoup(res.text, "html.parser")
    return soup.get_text(" ", strip=True)


def create_streamlit_app(llm, portfolio, clean_text):
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    st.title("📧 Cold Mail Generator")

    url_input = st.text_input(
        "Enter a URL:",
        value="https://careers.salesforce.com/en/jobs/jr302924/senior-backend-software-engineer/",
        placeholder="https://careers.company.com/job/software-engineer"
    )
    submit_button = st.button("Submit")

    if submit_button:
        try:
            st.write("Loading page content...")
            # Fetch page text using requests and BeautifulSoup
            page_text = get_page_text(url_input)
            data = clean_text(page_text)

            st.text_area("Cleaned Page Text (First 2000 chars):", data[:2000], height=200)

            if not data or len(data) < 100:
                st.error("Page content is too short. The site may be JavaScript-rendered.")
                st.stop()

            st.write("Page content loaded. Length:", len(data))

            portfolio.load_portfolio()
            st.write("Portfolio loaded.")

            st.write("Extracting jobs using LLM...")
            jobs = llm.extract_jobs(data)
            st.write("Extracted Jobs:", jobs)

            if not jobs:
                st.warning("No jobs extracted from the given URL.")
                st.stop()

            for job in jobs:
                skills = job.get('skills', [])
                st.write("Extracted Skills:", skills)

                links = portfolio.query_links(skills)
                st.write("Matching Portfolio Links:", links)

                email = llm.write_mail(job, links)
                st.code(email, language='markdown')

        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)
