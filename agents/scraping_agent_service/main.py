from fastapi import FastAPI
import feedparser

app = FastAPI()

@app.get("/scrape_news")
def scrape_news():
    scraped_data = {}

    # Use Yahoo Finance RSS feeds instead of scraping HTML
    feeds = {
        "TSMC": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=TSM&region=US&lang=en-US",
        "Samsung": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=005930.KS&region=US&lang=en-US"
    }

    for company, url in feeds.items():
        feed = feedparser.parse(url)
        scraped_data[company] = [{
            "title": entry.title,
            "summary": entry.summary
        } for entry in feed.entries[:3]]  # Return top 3 news items

    return scraped_data
