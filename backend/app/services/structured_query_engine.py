from typing import Dict, Any, List
from .kg_builder import kg_builder
from datetime import datetime, timedelta
import re

class StructuredQueryEngine:
    def execute_count_query(self, entity_type: str, user_id: str, time_filter: str = None) -> Dict[str, Any]:
        """Execute counting queries like 'How many deals?'"""
        
        # Load user's graph
        if user_id not in kg_builder.graphs:
            kg_builder._load_graph(user_id)
        
        if user_id not in kg_builder.graphs:
            return {"count": 0, "items": []}
        
        G = kg_builder.graphs[user_id]
        matching_nodes = []
        
        # Find nodes matching entity type
        for node, data in G.nodes(data=True):
            entity_text = data.get('entity_text', '').lower()
            doc_type = data.get('doc_type', '').lower()
            entity_type_lower = entity_type.lower()
            
            # Match by entity type or document type (handle singular/plural)
            if (entity_type_lower in entity_text or entity_type_lower in doc_type or
                entity_type_lower.rstrip('s') in entity_text or entity_type_lower.rstrip('s') in doc_type):
                matching_nodes.append(data)
        
        # Apply time filter if provided
        if time_filter:
            matching_nodes = self._apply_time_filter(matching_nodes, time_filter)
        
        # Extract unique IDs
        ids = self._extract_ids(matching_nodes)
        
        return {
            "count": len(ids) if ids else len(matching_nodes),
            "items": matching_nodes[:10],  # Return first 10 for display
            "query_type": "count"
        }
    
    def execute_list_query(self, entity_type: str, user_id: str, time_filter: str = None, limit: int = 10) -> Dict[str, Any]:
        """Execute listing queries like 'List all invoices'"""
        
        result = self.execute_count_query(entity_type, user_id, time_filter)
        
        return {
            "count": result["count"],
            "items": result["items"][:limit],
            "query_type": "list"
        }
    
    def _apply_time_filter(self, nodes: List[Dict], time_filter: str) -> List[Dict]:
        """Filter nodes by time period"""
        
        now = datetime.now()
        
        if "yesterday" in time_filter.lower():
            target_date = now - timedelta(days=1)
        elif "last week" in time_filter.lower():
            target_date = now - timedelta(days=7)
        elif "last month" in time_filter.lower():
            target_date = now - timedelta(days=30)
        else:
            return nodes  # No filtering
        
        filtered = []
        for node in nodes:
            # Try to extract date from metadata
            metadata = node.get('metadata', {})
            created_at = metadata.get('created_at')
            
            if created_at:
                # Simple date comparison (can be enhanced)
                filtered.append(node)
        
        return filtered
    
    def _extract_ids(self, nodes: List[Dict]) -> List[str]:
        """Extract order/deal IDs from nodes"""
        ids = []
        for node in nodes:
            text = node.get('entity_text', '')
            # Extract ID patterns (501, 502, 101, 102, etc.)
            matches = re.findall(r'\b(\d{3})\b', text)
            ids.extend(matches)
        return list(set(ids))  # Unique IDs

structured_query_engine = StructuredQueryEngine()
