import re
from typing import List, Dict, Any

class PatternExtractor:
    """Extract entities from structured text using patterns"""
    
    def extract_entities_and_relations(self, text: str) -> Dict[str, Any]:
        """Extract entities and relations from structured text"""
        entities = []
        relations = []
        
        # Pattern: "Label: Value"
        pattern = r'([A-Za-z\s]+):\s*([^\n]+)'
        matches = re.findall(pattern, text)
        
        deal_id = None
        
        for label, value in matches:
            label = label.strip()
            value = value.strip()
            
            if not value or value.lower() in ['', 'none', 'null']:
                continue
            
            # Determine entity type
            if 'id' in label.lower():
                entity_type = 'ID'
                deal_id = value
            elif 'client' in label.lower() or 'company' in label.lower():
                entity_type = 'ORG'
            elif 'name' in label.lower() and 'deal' in label.lower():
                entity_type = 'PRODUCT'
            elif 'amount' in label.lower() or 'price' in label.lower() or '$' in value:
                entity_type = 'MONEY'
            elif 'status' in label.lower():
                entity_type = 'STATUS'
            elif 'date' in label.lower() or 'on' in label.lower():
                entity_type = 'DATE'
            else:
                entity_type = 'VALUE'
            
            entities.append({
                'text': value,
                'type': entity_type,
                'value': value
            })
            
            # Create relation to deal_id if exists
            if deal_id and value != deal_id:
                relation_name = label.lower().replace(' ', '_')
                relations.append({
                    'source': deal_id,
                    'target': value,
                    'relation': f'has_{relation_name}'
                })
        
        return {
            'entities': entities,
            'relations': relations,
            'doc_type': 'structured'
        }

pattern_extractor = PatternExtractor()
