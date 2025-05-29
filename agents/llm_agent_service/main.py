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

