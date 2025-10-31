from openai import OpenAI
from typing import List, Dict, Any
from ..core.config import settings

class AnswerGenerator:
    def __init__(self):
        if settings.OPENROUTER_API_KEY:
            try:
                import httpx
                http_client = httpx.Client(timeout=120.0)
                self.client = OpenAI(
                    api_key=settings.OPENROUTER_API_KEY,
                    base_url=settings.OPENROUTER_BASE_URL,
                    http_client=http_client
                )
                self.enabled = True
                self.model = settings.LLM_MODEL
                print(f"✅ Answer Generator enabled: {self.model}")
            except Exception as e:
                print(f"❌ Answer Generator failed: {e}")
                self.client = None
                self.enabled = False
                self.model = settings.LLM_MODEL
        else:
            print("⚠️ Answer Generator disabled: No API key")
            self.client = None
            self.enabled = False
            self.model = settings.LLM_MODEL
    
    def generate_answer(self, query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        context_text = "\n\n".join([f"[{i+1}] {item['content']}" for i, item in enumerate(context)])
        
        prompt = f"""You are a precise data analyst. Answer based ONLY on the context provided.

RULES:
- Count ALL items carefully
- Include specific details (IDs, names, amounts, dates)
- Cite sources with [1], [2]
- Be accurate with numbers

Context:
{context_text}

Question: {query}

Answer:"""
        
        if self.enabled and self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a precise data analyst. Count carefully and provide accurate answers with citations."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                answer = response.choices[0].message.content
            except Exception as e:
                print(f"LLM Error: {e}")
                answer = f"Based on the provided context: {context[0]['content'][:300]}..." if context else "No relevant information found."
        else:
            answer = f"Based on the provided context: {context[0]['content'][:300]}..." if context else "No relevant information found."
        
        citations = [item.get("source", f"Document {i+1}") for i, item in enumerate(context)]
        
        return {
            "answer": answer,
            "citations": citations
        }

answer_generator = AnswerGenerator()
