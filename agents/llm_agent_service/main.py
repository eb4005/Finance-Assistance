# llm_agent/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

class BriefRequest(BaseModel):
    query: str
    market_data: Dict
    earnings: Dict
    retrieved_chunks: List[str]

@app.post("/generate-brief")
def generate_brief(request: BriefRequest):
    try:
        exposure = request.market_data.get('exposure', 'N/A')
        earnings_items = [f"{k}: {v}%" for k, v in request.earnings.items()]
        context_items = request.retrieved_chunks[:3]  # Take top 3 relevant chunks
        
        summary = f"""Today's Asia tech allocation: {exposure}% of AUM.
        
Earnings Highlights:
- {', '.join(earnings_items)}

Key Context:
- {'; '.join(context_items)}"""

        return {"summary": summary}
    
    except Exception as e:
        return {"summary": f"Error generating summary: {str(e)}"}