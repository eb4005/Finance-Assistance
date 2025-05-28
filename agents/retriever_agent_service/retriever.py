from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RetrieverAgent:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.text_chunks = []

    def build_index(self, documents: list[str]):
        self.text_chunks = documents
        embeddings = self.model.encode(documents)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(np.array(embeddings))

    def query(self, question: str, top_k=3):
        query_vec = self.model.encode([question])
        distances, indices = self.index.search(np.array(query_vec), top_k)
        return [self.text_chunks[i] for i in indices[0]]
