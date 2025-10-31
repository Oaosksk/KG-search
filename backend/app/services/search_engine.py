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
    
    def hybrid_search(self, query: str, user_id: str, top_k: int = 10, doc_type_filter: str = None) -> List[Dict[str, Any]]:
        # Filter documents by doc_type before searching
        dense_results = rag_engine.search_similar(query, user_id, top_k, doc_type_filter)
        kg_results = kg_builder.query_graph(query, user_id, doc_type_filter)
        
        combined = []
        
        # BM25 keyword search
        if user_id not in self.bm25_indices:
            self._update_bm25(user_id)
        
        if user_id in self.bm25_indices:
            # Filter corpus by doc_type if specified
            if doc_type_filter:
                filtered_corpus = [(i, doc) for i, doc in enumerate(self.bm25_corpus[user_id])
                                  if doc.get('metadata', {}).get('doc_type') == doc_type_filter]
                if filtered_corpus:
                    filtered_indices, filtered_docs = zip(*filtered_corpus)
                    bm25_scores = self.bm25_indices[user_id].get_scores(query.split())
                    filtered_scores = [bm25_scores[i] for i in filtered_indices]
                    top_bm25_idx = np.argsort(filtered_scores)[-top_k:][::-1]
                    
                    for idx in top_bm25_idx:
                        if idx < len(filtered_docs):
                            doc = filtered_docs[idx]
                            combined.append({
                                "content": doc.get('chunk', ''),
                                "score": self.bm25_weight * float(filtered_scores[idx]),
                                "source": "bm25",
                                "metadata": doc
                            })
            else:
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
        
        # Dense vector search (already filtered by doc_type)
        for idx, result in enumerate(dense_results):
            score = self.dense_weight * result.get("score", 0.5)
            combined.append({
                "content": result.get("content", ""),
                "score": score,
                "source": "vector",
                "metadata": result.get("metadata", {})
            })
        
        # Knowledge graph expansion
        kg_nodes = kg_results.get('nodes', [])
        for idx, result in enumerate(kg_nodes[:top_k]):
            score = self.kg_weight * (1 - idx / max(len(kg_nodes), 1))
            combined.append({
                "content": str(result),
                "score": score,
                "source": "kg",
                "metadata": result
            })
        
        combined.sort(key=lambda x: x["score"], reverse=True)
        return combined[:top_k]

search_engine = HybridSearchEngine()
