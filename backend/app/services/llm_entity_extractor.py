import requests
from typing import List, Dict, Any
import json
from ..core.config import settings

class LLMEntityExtractor:
    def __init__(self):
        if settings.OPENROUTER_API_KEY:
            self.api_key = settings.OPENROUTER_API_KEY
            self.base_url = settings.OPENROUTER_BASE_URL
            self.model = settings.LLM_MODEL
            self.enabled = True
            print("✅ LLM Entity Extractor enabled")
        else:
            self.api_key = None
            self.enabled = False
            print("⚠️ LLM Entity Extractor disabled (no API key)")
    
    def extract_entities_and_relations(self, text: str, doc_type: str = "unknown") -> Dict[str, Any]:
        if not self.enabled or not text.strip():
            return {"entities": [], "relations": [], "doc_type": doc_type}
        
        prompt = f"""You are a Knowledge Graph expert. Analyze this {doc_type} document and extract a complete knowledge graph.

Document:
{text[:2000]}

Your task:
1. Identify ALL entities (IDs, names, organizations, amounts, dates, statuses, etc.)
2. Understand the document structure and how entities relate to each other
3. Create meaningful relationships that capture the business logic

For a deal/transaction document:
- Deal ID is the central entity
- Connect Deal ID to: client (has_client), amount (has_amount), status (has_status), date (closed_on), product/service name (has_name)
- Think about what information belongs to what

Return ONLY valid JSON:
{{
  "doc_type": "deals|invoice|contract|etc",
  "entities": [
    {{"text": "101", "type": "ID", "value": "101"}},
    {{"text": "Alpha Co", "type": "ORG", "value": "Alpha Co"}},
    {{"text": "5000", "type": "MONEY", "value": "5000.00"}}
  ],
  "relations": [
    {{"source": "101", "target": "Alpha Co", "relation": "has_client"}},
    {{"source": "101", "target": "5000", "relation": "has_amount"}},
    {{"source": "101", "target": "Closed", "relation": "has_status"}}
  ]
}}

IMPORTANT: Create relations that show HOW entities connect, not just that they exist together."""
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are an expert at extracting structured information from documents. Return ONLY valid JSON, no explanations."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1
                },
                timeout=30
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            
            # Extract JSON from response (handle reasoning text)
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            elif '{' in content:
                start = content.find('{')
                end = content.rfind('}') + 1
                content = content[start:end]
            
            result = json.loads(content)
            return result
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return {"entities": [], "relations": [], "doc_type": doc_type}

llm_extractor = LLMEntityExtractor()
