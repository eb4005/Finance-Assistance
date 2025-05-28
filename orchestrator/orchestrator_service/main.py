from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import logging
import time

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

# Service configuration with timeouts
SERVICE_CONFIG = {
    "api": {
        "port": 8001,
        "timeout": 5,
        "endpoints": {
            "exposure": "/exposure",
            "earnings": "/earnings_surprises"
        }
    },
    "scraper": {
        "port": 8003,
        "timeout": 10,
        "endpoints": {
            "news": "/scrape_news"
        }
    },
    "retriever": {
        "port": 8002,
        "timeout": 5,
        "endpoints": {
            "query": "/query"
        }
    },
    "llm": {
        "port": 8400,
        "timeout": 30,
        "endpoints": {
            "brief": "/generate-brief"
        }
    },
    "voice": {
        "port": 8500,
        "timeout": 15,
        "endpoints": {
            "stt": "/stt",
            "tts": "/tts"
        }
    }
}

def service_url(service: str, endpoint: str) -> str:
    return f"http://localhost:{SERVICE_CONFIG[service]['port']}{SERVICE_CONFIG[service]['endpoints'][endpoint]}"

def safe_request(method: str, url: str, json_data: dict = None, timeout: int = 5):
    try:
        if method.lower() == 'get':
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.post(url, json=json_data, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Service call failed: {url} - {str(e)}")
        return None

class UserQuery(BaseModel):
    user_query: str

@app.post("/brief")
async def generate_brief(payload: UserQuery):
    components = {}
    
    # Market Data
    exposure = safe_request('get', service_url("api", "exposure")) or {"exposure": 0}
    earnings = safe_request('get', service_url("api", "earnings")) or {}
    components["market_data"] = {
        "exposure": exposure.get("exposure", 0),
        "earnings": earnings
    }

    # News Data
    components["news"] = safe_request('get', service_url("scraper", "news")) or {
        "error": "News service unavailable"
    }

    # Context Retrieval
    retrieved = safe_request(
        'post', 
        service_url("retriever", "query"),
        {"question": payload.user_query, "top_k": 3}
    ) or {"results": ["Market context unavailable"]}
    components["context"] = retrieved.get("results", [])

    # LLM Summary
    llm_payload = {
        "query": payload.user_query,
        "market_data": components["market_data"],
        "earnings": components["market_data"].get("earnings", {}),
        "retrieved_chunks": components["context"]
    }
    
    llm_response = safe_request(
        'post', 
        service_url("llm", "brief"),
        llm_payload,
        timeout=30
    ) or {"summary": "Summary service unavailable"}

    return {
        "summary": llm_response.get("summary", "Summary generation failed"),
        "components": components
    }

@app.post("/voice-brief")
async def voice_to_brief(audio: bytes):
    try:
        # STT
        stt_response = safe_request(
            'post',
            service_url("voice", "stt"),
            {"file": audio},  # Adjust based on your voice agent's expected format
            timeout=15
        ) or {"text": ""}
        
        query_text = stt_response.get("text", "") or "What's our Asia tech exposure?"
        
        # Generate brief
        brief = await generate_brief(UserQuery(user_query=query_text))
        
        # TTS
        tts_response = safe_request(
            'post',
            service_url("voice", "tts"),
            {"text": brief["summary"]},
            timeout=20
        )
        
        return {
            "query": query_text,
            "summary": brief["summary"],
            "audio": tts_response.get("audio", b"") if tts_response else b"",
            "components": brief.get("components", {})
        }

    except Exception as e:
        logger.error(f"Voice brief failed: {str(e)}")
        raise HTTPException(500, detail="Voice processing error")