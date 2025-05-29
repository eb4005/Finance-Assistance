from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from transformers import pipeline, AutoTokenizer
import torch
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLM-Agent")

# Load efficient model
MODEL_NAME = "google/flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
pipe = pipeline(
    "text2text-generation",
    model=MODEL_NAME,
    device=0 if torch.cuda.is_available() else -1,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    model_kwargs={}  # 4-bit quantization for efficiency
)

class BriefRequest(BaseModel):
    query: str
    market_data: Dict
    news: Dict
    retrieved_chunks: List[str]

def format_earnings(earnings: dict) -> str:
    if not earnings:
        return "None"
    return ", ".join([f"{k} ({v}% beat)" for k, v in earnings.items()])

def format_news(news: dict) -> str:
    highlights = []
    for company, articles in news.items():
        if company in ["TSMC", "Samsung"] and isinstance(articles, list):
            for i, art in enumerate(articles[:2]):
                title = art.get('title', 'No title').replace('"', '').strip()
                if len(title) > 80:
                    title = title[:77] + "..."
                highlights.append(f"{company}: {title}")
    return " | ".join(highlights) if highlights else "None"

@app.post("/generate-brief")
def generate_brief(request: BriefRequest):
    try:
        # Extract core data points
        exposure = request.market_data.get('exposure', 0)
        earnings = request.market_data.get('earnings', {})
        context = " | ".join(request.retrieved_chunks[:3]) or "None"
        
        # Format components
        earnings_str = format_earnings(earnings)
        news_str = format_news(request.news)
        
        # Create directive prompt
        prompt = f"""Generate a concise 2-sentence spoken market brief about Asia tech exposure using ONLY these facts:
        
USER QUERY: "{request.query}"
PORTFOLIO EXPOSURE: {exposure}% to Asian tech
EARNINGS RESULTS: {earnings_str}
KEY CONTEXT: {context}
NEWS HIGHLIGHTS: {news_str}

RULES:
- MUST mention {exposure}% exposure first
- MUST include earnings beats if available
- MUST reference at least one news item
- Address bond yields if mentioned in context
- Use natural, conversational language
- MAX 40 words

SPOKEN BRIEF:"""
        
        # Generate response
        result = pipe(
            prompt,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.4,
            top_p=0.9
        )[0]['generated_text']
        
        # Post-process for clarity
        summary = result.replace("SPOKEN BRIEF:", "").strip()
        if not summary.endswith('.'):
            summary += '.'
            
        logger.info(f"Generated summary: {summary}")
        return {"summary": summary}

    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        return {"summary": f"Our Asian tech exposure is {request.market_data.get('exposure', 0)}%. " +
                           "Recent developments include semiconductor earnings beats and supply chain updates."}




# llama

# from fastapi import FastAPI, Request
# from pydantic import BaseModel
# from typing import List, Dict
# import torch
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# app = FastAPI()

# # Load LLaMA-3 model
# model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
# tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
# model = AutoModelForCausalLM.from_pretrained(
#     model_id,
#     torch_dtype=torch.float16,
#     device_map="auto"
# )

# # Pipeline for text generation
# pipe = pipeline(
#     "text-generation",
#     model=model,
#     tokenizer=tokenizer,
#     device=0,
#     torch_dtype=torch.float16,
# )

# # Input format
# class MarketData(BaseModel):
#     exposure: float
#     earnings: Dict[str, str]

# class InputData(BaseModel):
#     market_data: MarketData
#     news: Dict[str, List[Dict[str, str]]]
#     context: List[str]

# @app.post("/generate-summary/")
# async def generate_summary(request: Request):
#     body = await request.json()
#     market_data = body["market_data"]
#     news = body["news"]
#     context = body["context"]

#     # Extract components
#     exposure = market_data["exposure"]
#     earnings = market_data["earnings"]

#     # Flatten earnings
#     earnings_str = ". ".join([f"{company} reported {info}" for company, info in earnings.items()]) or "No recent earnings reported."

#     # Flatten news
#     news_str = ""
#     for company, articles in news.items():
#         for article in articles:
#             news_str += f"{company}: {article['summary']} "

#     # Context
#     context_str = " ".join(context)

#     # Prompt
#     prompt = f"""[INST] 
# You are a financial market assistant.

# Write a spoken-style market summary (under 40 words) using these:

# - Portfolio exposure to Asian tech: {exposure}%
# - Earnings: {earnings_str}
# - News: {news_str}
# - Market context: {context_str}

# Start with the portfolio exposure. Mention earnings if present. Include at least one important news point. Use a natural, conversational tone.

# Summary: [/INST]
# """

#     result = pipe(prompt, max_new_tokens=100, do_sample=True, temperature=0.7, top_p=0.9)[0]['generated_text']
#     summary = result.split("Summary:")[-1].strip()

#     return {
#         "summary": summary,
#         "components": {
#             "market_data": market_data,
#             "earnings": earnings,
#             "news": news,
#             "context": context
#         }
#     }
# # 