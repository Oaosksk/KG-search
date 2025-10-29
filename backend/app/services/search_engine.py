from rank_bm25 import BM25Okapi
from typing import List, Dict, Any
import numpy as np
from .rag_engine import rag_engine
from .kg_builder import kg_builder

class HybridSearchEngine:
    def __init__(self):
        self.bm25_weight = 0.3
        self.dense_weight = 0.5
        self.kg_weight = 0.2
        self.bm25_corpus = {}
        self.bm25_indices = {}
    
    def _update_bm25(self, user_id: str):
        if user_id in rag_engine.documents and rag_engine.documents[user_id]:
            corpus = [doc.get('chunk', '').split() for doc in rag_engine.documents[user_id]]
            self.bm25_indices[user_id] = BM25Okapi(corpus)
            self.bm25_corpus[user_id] = rag_engine.documents[user_id]
    
    def hybrid_search(self, query: str, user_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        dense_results = rag_engine.search_similar(query, user_id, top_k)
        kg_results = kg_builder.query_graph(query, user_id)
        
        combined = []
        
        # BM25 keyword search
        if user_id not in self.bm25_indices:
            self._update_bm25(user_id)
        
        if user_id in self.bm25_indices:
            bm25_scores = self.bm25_indices[user_id].get_scores(query.split())
            top_bm25_idx = np.argsort(bm25_scores)[-top_k:][::-1]
            
            for idx in top_bm25_idx:
                if idx < len(self.bm25_corpus[user_id]):
                    doc = self.bm25_corpus[user_id][idx]
                    combined.append({
                        "content": doc.get('chunk', ''),
                        "score": self.bm25_weight * float(bm25_scores[idx]),
                        "source": "bm25",
                        "metadata": doc
                    })
        
        # Dense vector search
        for idx, result in enumerate(dense_results):
            score = self.dense_weight * result.get("score", 0.5)
            combined.append({
                "content": result.get("content", ""),
                "score": score,
                "source": "vector",
                "metadata": result.get("metadata", {})
            })
        
        # Knowledge graph expansion
        for idx, result in enumerate(kg_results[:top_k]):
            score = self.kg_weight * (1 - idx / max(len(kg_results), 1))
            combined.append({
                "content": str(result.get("metadata", {})),
                "score": score,
                "source": "kg",
                "metadata": result
            })
        
        combined.sort(key=lambda x: x["score"], reverse=True)
        return combined[:top_k]

search_engine = HybridSearchEngine()
