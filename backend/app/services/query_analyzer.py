from openai import OpenAI
from typing import Dict, Any
import json
from ..core.config import settings

class QueryAnalyzer:
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
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine if it needs aggregation, filtering, or simple search"""
        
        if not self.enabled:
            return {"type": "simple_search", "intent": "search"}
        
        prompt = f"""Analyze this query and determine its type and intent.

Query: "{query}"

Classify as:
1. "count" - counting queries (how many, total number, count)
2. "filter" - filtering queries (yesterday, last week, specific dates)
3. "list" - listing queries (show all, list, display)
4. "search" - simple search queries

Also extract:
- entities (deals, invoices, orders, etc.)
- time_filter (yesterday, last month, etc.)
- aggregation_type (count, sum, average, etc.)

Return JSON:
{{
  "type": "count|filter|list|search",
  "intent": "what user wants",
  "entities": ["entity1", "entity2"],
  "time_filter": "time period or null",
  "aggregation": "count|sum|avg|null",
  "structured_query": "SQL-like query if applicable"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a query analysis expert. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"Query analysis error: {e}")
            return {"type": "simple_search", "intent": "search"}

query_analyzer = QueryAnalyzer()
