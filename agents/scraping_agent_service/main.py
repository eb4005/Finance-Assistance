# scraper_agent/main.py
from fastapi import FastAPI
from newspaper import Article
import requests
from bs4 import BeautifulSoup
import re

app = FastAPI()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

@app.get("/scrape_news")
def scrape_news():
    scraped_data = {}
    
    try:
        # TSMC News from Yahoo Finance
        tsmc_url = "https://finance.yahoo.com/quote/TSM/news?p=TSM"
        response = requests.get(tsmc_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('li', {'class': 'js-stream-content'})[:3]
        scraped_data["TSMC"] = [{
            "title": clean_text(art.find('h3').text),
            "summary": clean_text(art.find('p').text) if art.find('p') else ""
        } for art in articles if art.find('h3')]

        # Samsung News from Yahoo Finance
        samsung_url = "https://finance.yahoo.com/quote/005930.KS/news?p=005930.KS"
        response = requests.get(samsung_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('li', {'class': 'js-stream-content'})[:3]
        scraped_data["Samsung"] = [{
            "title": clean_text(art.find('h3').text),
            "summary": clean_text(art.find('p').text) if art.find('p') else ""
        } for art in articles if art.find('h3')]

    except Exception as e:
        scraped_data = {"error": str(e)}

    return scraped_data