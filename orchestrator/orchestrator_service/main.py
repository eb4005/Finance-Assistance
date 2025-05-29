

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import requests
import logging
import re
import aiohttp
import base64

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

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

def extract_earnings_from_context(context: list) -> dict:
    earnings = {}
    for item in context:
        if '% earnings beat' in item.lower():
            try:
                company = item.split()[0]
                beat = re.search(r'(\d+)%', item).group(1)
                earnings[company] = float(beat)
            except (AttributeError, ValueError, IndexError):
                pass
        elif 'TSMC' in item and '%' in item:
            try:
                beat = re.search(r'(\d+)%', item).group(1)
                earnings['TSMC'] = float(beat)
            except (AttributeError, ValueError):
                pass
    return earnings

class UserQuery(BaseModel):
    user_query: str

@app.post("/brief")
async def generate_brief(payload: UserQuery):
    components = {}

    exposure = safe_request('get', service_url("api", "exposure")) or {"exposure": 0}
    earnings_api = safe_request('get', service_url("api", "earnings")) or {}

    news_data = safe_request('get', service_url("scraper", "news")) or {}

    retrieved = safe_request(
        'post', 
        service_url("retriever", "query"),
        {"question": payload.user_query, "top_k": 3}
    ) or {"results": ["Market context unavailable"]}

    context_items = retrieved.get("results", [])
    earnings = earnings_api if earnings_api else extract_earnings_from_context(context_items)

    components["market_data"] = {
        "exposure": exposure.get("exposure", 0),
        "earnings": earnings
    }
    components["news"] = news_data
    components["context"] = context_items

    llm_payload = {
        "query": payload.user_query,
        "market_data": components["market_data"],
        "news": components["news"],
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
async def voice_to_brief(audio: UploadFile = File(...)):
    query_text = "What's our Asia tech exposure?"  
    brief = {}
    audio_base64 = None
    errors = []

    try:
        #  STT 
        async with aiohttp.ClientSession() as session:
            audio_bytes = await audio.read()
            form = aiohttp.FormData()
            form.add_field(
                name='file',
                value=audio_bytes,
                filename=audio.filename,
                content_type=audio.content_type
            )
            async with session.post(service_url("voice", "stt"), data=form, timeout=15) as stt_resp:
                if stt_resp.status == 200:
                    stt_result = await stt_resp.json()
                    query_text = stt_result.get("transcript", query_text)
                else:
                    errors.append(f"STT failed with status {stt_resp.status}")

        # Generate Brief 
        brief = await generate_brief(UserQuery(user_query=query_text))

        #  TTS 
        async with aiohttp.ClientSession() as session:
            tts_form = aiohttp.FormData()
            tts_form.add_field("text", brief["summary"])

            async with session.post(service_url("voice", "tts"), data=tts_form, timeout=20) as tts_resp:
                if tts_resp.status == 200:
                    audio_result = await tts_resp.read()
                    audio_base64 = base64.b64encode(audio_result).decode("utf-8")
                else:
                    errors.append(f"TTS failed with status {tts_resp.status}")

    except Exception as e:
        logger.exception("Unhandled error during voice brief")
        errors.append(str(e))

    return {
        "query": query_text,
        "summary": brief.get("summary", "Briefing failed"),
        "components": brief.get("components", {}),
        "audio_base64": audio_base64,
        "errors": errors
    }

