from openai import OpenAI
from typing import Dict, Any
import json
from ..core.config import settings

class DocTypeDetector:
    def __init__(self):
        try:
            self.client = OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL
            )
            self.enabled = True
        except:
            self.client = None
            self.enabled = False
    
    def detect_type(self, content: str) -> Dict[str, Any]:
        if not self.enabled or not content.strip():
            return {"type": "unknown", "confidence": 0.0, "fields": []}
        
        prompt = f"""Analyze this document and identify its type and key fields.

Document content (first 1000 chars):
{content[:1000]}

Identify:
1. Document type (invoice, contract, deal, email, report, etc.)
2. Confidence level (0-1)
3. Key fields to extract

Return JSON:
{{
  "type": "document type",
  "confidence": 0.95,
  "fields": ["field1", "field2", ...]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a document classification expert. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"Doc type detection error: {e}")
            return {"type": "unknown", "confidence": 0.0, "fields": []}

doc_detector = DocTypeDetector()
