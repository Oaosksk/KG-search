from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
import numpy as np
from typing import List, Dict, Any
import pickle
from pathlib import Path
from .supabase_client import supabase_client

class RAGEngine:
    def __init__(self):
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.chunk_size = 500
        self.storage_dir = Path("storage")
        self.storage_dir.mkdir(exist_ok=True)
        self.indices = {}
        self.documents = {}
    
    def chunk_text(self, text: str) -> List[str]:
        words = text.split()
        return [" ".join(words[i:i + self.chunk_size]) for i in range(0, len(words), self.chunk_size)]
    
    def generate_embedding(self, text: str) -> np.ndarray:
        return self.encoder.encode(text, convert_to_numpy=True)
    
    def store_embeddings(self, data: List[Dict[str, Any]], file_id: str, user_id: str):
        chunks = []
        metadata = []
        
        for item in data:
            content = str(item.get('content', ''))
            
            # If content is short (< 1000 chars), keep as single chunk
            if len(content) < 1000:
                chunks.append(content)
                metadata.append({**item, "chunk": content})
            else:
                # Only chunk long content
                text_chunks = self.chunk_text(content)
                chunks.extend(text_chunks)
                metadata.extend([{**item, "chunk": chunk} for chunk in text_chunks])
        
        embeddings = self.encoder.encode(chunks, convert_to_numpy=True)
        
        if user_id not in self.indices:
            dimension = embeddings.shape[1]
            self.indices[user_id] = faiss.IndexFlatL2(dimension)
            self.documents[user_id] = []
        
        self.indices[user_id].add(embeddings)
        self.documents[user_id].extend(metadata)
        
        self._save_index(user_id)
    
    def search_similar(self, query: str, user_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        if user_id not in self.indices:
            self._load_index(user_id)
        
        if user_id not in self.indices or self.indices[user_id].ntotal == 0:
            return []
        
        query_embedding = self.generate_embedding(query).reshape(1, -1)
        distances, indices = self.indices[user_id].search(query_embedding, min(top_k * 2, self.indices[user_id].ntotal))
        
        candidates = [(self.documents[user_id][idx], 1 / (1 + distances[0][i])) 
                     for i, idx in enumerate(indices[0]) if idx < len(self.documents[user_id])]
        
        pairs = [[query, doc.get('chunk', '')] for doc, _ in candidates]
        scores = self.reranker.predict(pairs)
        
        reranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)[:top_k]
        
        return [{"content": doc.get('chunk', ''), "score": float(score), "metadata": doc} 
                for (doc, _), score in reranked]
    
    def _save_index(self, user_id: str):
        faiss.write_index(self.indices[user_id], str(self.storage_dir / f"{user_id}.index"))
        with open(self.storage_dir / f"{user_id}.pkl", 'wb') as f:
            pickle.dump(self.documents[user_id], f)
        
        if supabase_client.enabled:
            try:
                for doc in self.documents[user_id]:
                    embedding = self.encoder.encode(doc['chunk']).tolist()
                    supabase_client.client.table('embeddings').upsert({
                        'user_id': user_id,
                        'content': doc.get('content', ''),
                        'chunk': doc['chunk'],
                        'embedding': embedding
                    }).execute()
                print(f"✅ Saved {len(self.documents[user_id])} embeddings to Supabase")
            except Exception as e:
                print(f"⚠️ Supabase save failed: {e}")
    
    def _load_index(self, user_id: str):
        index_path = self.storage_dir / f"{user_id}.index"
        docs_path = self.storage_dir / f"{user_id}.pkl"
        
        if index_path.exists() and docs_path.exists():
            self.indices[user_id] = faiss.read_index(str(index_path))
            with open(docs_path, 'rb') as f:
                self.documents[user_id] = pickle.load(f)

rag_engine = RAGEngine()
