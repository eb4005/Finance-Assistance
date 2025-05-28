from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from transformers import pipeline, AutoTokenizer
import torch
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLM-Agent")

# Load efficient model (7B parameters might be too heavy - using smaller model)
MODEL_NAME = "google/flan-t5-large"  # More efficient alternative
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
pipe = pipeline(
    "text2text-generation",
    model=MODEL_NAME,
    device=0 if torch.cuda.is_available() else -1,
    torch_dtype=torch.float16
)

class BriefRequest(BaseModel):
    query: str
    market_data: Dict
    earnings: Dict
    retrieved_chunks: List[str]

def extract_summary(generated_text: str) -> str:
    """Extract only the generated summary without prompt"""
    # Split on the last occurrence of the instruction marker
    parts = generated_text.split("Brief Summary:", 1)
    return parts[-1].strip() if len(parts) > 1 else generated_text

@app.post("/generate-brief")
def generate_brief(request: BriefRequest):
    try:
        exposure = request.market_data.get('exposure', 'N/A')
        earnings_items = [f"{k}: {v}%" for k, v in request.earnings.items()] if request.earnings else []
        context_items = request.retrieved_chunks[:3]

        # Create optimized prompt
        prompt = f"""Generate a concise spoken market brief using this information:
        
Query: {request.query}
Asia Tech Exposure: {exposure}% of AUM
Earnings Highlights: {', '.join(earnings_items) or 'None'}
Context: {'; '.join(context_items) or 'None'}

Brief Summary:"""
        
        logger.info(f"Prompt length: {len(prompt)} characters")
        
        # Generate response
        result = pipe(
            prompt,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.7
        )[0]['generated_text']
        
        # Extract only the summary
        summary = extract_summary(result)
        logger.info(f"Generated summary: {summary}")
        
        return {"summary": summary}

    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        return {"summary": f"Error: {str(e)}"}