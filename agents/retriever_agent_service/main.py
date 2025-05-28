# retriever/main.py
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Request models
class IndexRequest(BaseModel):
    documents: List[str]

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

# Retriever implementation
class RetrieverAgent:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.text_chunks = []
        self.initialize_default_data()

    def initialize_default_data(self):
        default_docs = [
            "TSMC reported 4% earnings beat in Q2 2024",
            "Samsung Electronics lowered Q3 guidance by 2%",
            "Asian tech sector shows neutral sentiment with caution on rising bond yields",
            "Apple increases orders with Asian semiconductor suppliers",
            "Baidu announces new AI chip collaboration with Chinese foundries"
        ]
        self.build_index(default_docs)

    def build_index(self, documents: List[str]):
        self.text_chunks = documents
        embeddings = self.model.encode(documents)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(np.array(embeddings))

    def query(self, question: str, top_k=3):
        query_vec = self.model.encode([question])
        distances, indices = self.index.search(np.array(query_vec), top_k)
        return [self.text_chunks[i] for i in indices[0]]

# Initialize agent
agent = RetrieverAgent()

# API endpoints
@app.post("/index_documents")
async def index_documents(request: IndexRequest):
    """Endpoint to update the document index"""
    agent.build_index(request.documents)
    return {"status": "success", "indexed_documents": len(request.documents)}

@app.post("/query")
async def query_documents(request: QueryRequest):
    """Endpoint to query the document index"""
    results = agent.query(request.question, request.top_k)
    return {"results": results}

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "index_size": len(agent.text_chunks),
        "model": agent.model.get_sentence_embedding_dimension()
    }

# Initialize with default data on startup
@app.on_event("startup")
async def startup_event():
    agent.initialize_default_data()