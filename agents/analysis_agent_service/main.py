from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from textblob import TextBlob
import pandas as pd
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("analysis-agent")

class ExposureRequest(BaseModel):
    portfolio: dict
    region: str
    sectors: list

class SentimentRequest(BaseModel):
    news: dict
    filings: dict
    market_data: dict

class RiskRequest(BaseModel):
    prices: dict
    exposure: dict

def calculate_exposure(portfolio: pd.DataFrame, region: str, sectors: list) -> float:
    """Calculate portfolio exposure for specific region and sectors"""
    filtered = portfolio[
        (portfolio['region'].str.contains(region, case=False)) &
        (portfolio['sector'].isin(sectors))
    ]
    return filtered['weight'].sum() * 100

def calculate_sentiment(texts: list) -> dict:
    """Calculate sentiment scores from text inputs"""
    sentiment_scores = []
    for text in texts:
        analysis = TextBlob(text)
        sentiment_scores.append(analysis.sentiment.polarity)
    
    avg_score = np.mean(sentiment_scores) if sentiment_scores else 0
    return {
        "score": avg_score,
        "sentiment": "positive" if avg_score > 0.1 else 
                     "negative" if avg_score < -0.1 else "neutral"
    }

@app.post("/analyze_exposure")
async def analyze_exposure(request: ExposureRequest):
    try:
        # Convert to DataFrame
        portfolio = pd.DataFrame(request.portfolio.get("holdings", []))
        
        # Calculate exposure
        exposure = calculate_exposure(portfolio, request.region, request.sectors)
        
        # Calculate change from previous day
        prev_exposure = request.portfolio.get("previous_exposure", exposure)
        change = exposure - prev_exposure
        
        return {
            "current_exposure": round(exposure, 2),
            "previous_exposure": round(prev_exposure, 2),
            "change": round(change, 2),
            "change_pct": round((change / prev_exposure * 100) if prev_exposure else 0, 2)
        }
    except Exception as e:
        logger.error(f"Exposure analysis failed: {str(e)}")
        return {"error": str(e)}

@app.post("/analyze_sentiment")
async def analyze_sentiment(request: SentimentRequest):
    try:
        # Combine all text sources
        texts = []
        texts.extend(request.news.get("headlines", []))
        texts.extend(request.filings.get("summaries", []))
        texts.extend([n["title"] for n in request.market_data.get("news", [])])
        
        # Calculate sentiment
        sentiment = calculate_sentiment(texts)
        
        # Add keyword extraction
        combined_text = " ".join(texts)
        blob = TextBlob(combined_text)
        top_nouns = [np for np in blob.noun_phrases][:10]
        
        return {
            "sentiment": sentiment["sentiment"],
            "score": round(sentiment["score"], 4),
            "keywords": top_nouns
        }
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}")
        return {"error": str(e)}

@app.post("/analyze_risk")
async def analyze_risk(request: RiskRequest):
    try:
        # Simplified risk analysis
        exposure = request.exposure.get("current_exposure", 0)
        volatility = request.prices.get("avg_volatility", 0)
        
        # Risk score calculation
        risk_score = min(100, exposure * volatility * 10)
        
        return {
            "risk_score": round(risk_score, 1),
            "risk_level": "high" if risk_score > 70 else 
                         "medium" if risk_score > 30 else "low",
            "key_risks": [
                "sector_concentration",
                "earnings_volatility"
            ]
        }
    except Exception as e:
        logger.error(f"Risk analysis failed: {str(e)}")
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "analysis-agent"}