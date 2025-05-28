# orchestrator/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

SERVICES = {
    "api": {"port": 8001, "endpoints": {
        "exposure": "/exposure",
        "earnings": "/earnings_surprises"
    }},
    "scraper": {"port": 8003, "endpoints": {
        "news": "/scrape_news"
    }},
    "retriever": {"port": 8002, "endpoints": {
        "query": "/query"
    }},
    "llm": {"port": 8004, "endpoints": {
        "brief": "/generate-brief"
    }}
}

def service_url(service: str, endpoint: str) -> str:
    return f"http://localhost:{SERVICES[service]['port']}{SERVICES[service]['endpoints'][endpoint]}"

class UserQuery(BaseModel):
    user_query: str

@app.post("/brief")
async def generate_brief(payload: UserQuery):
    components = {}
    
    try:
        # Get market data
        exposure = requests.get(service_url("api", "exposure")).json()
        earnings = requests.get(service_url("api", "earnings")).json()
        components["market_data"] = {
            "exposure": exposure.get("exposure"),
            "earnings": earnings
        }

        # Get news
        news = requests.get(service_url("scraper", "news")).json()
        components["news"] = news

        # Get context
        retrieved = requests.post(
            service_url("retriever", "query"),
            json={"question": payload.user_query, "top_k": 3}
        ).json()
        components["context"] = retrieved.get("results", [])

        # Generate summary
        llm_response = requests.post(
            service_url("llm", "brief"),
            json={
                "query": payload.user_query,
                "market_data": components["market_data"],
                "earnings": components["market_data"]["earnings"],
                "retrieved_chunks": components["context"]
            }
        ).json()

        return {
            "summary": llm_response.get("summary"),
            "components": components
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Service error: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")