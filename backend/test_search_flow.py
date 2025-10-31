import sys
sys.path.insert(0, '/home/ven/KG-Search/backend')

from app.services.query_analyzer import query_analyzer
from app.services.structured_query_engine import structured_query_engine

# Test user ID (replace with actual)
user_id = "test_user"

print("=== Testing Search Flow ===\n")

query = "How many customers do we have?"
print(f"Query: {query}")

# Step 1: Analyze
analysis = query_analyzer.analyze_query(query)
print(f"\n1. Analysis: {analysis}")

# Step 2: Execute structured query
if analysis['type'] == 'count':
    entity_type = analysis.get('doc_type', 'customers')
    doc_type = analysis.get('doc_type')
    
    print(f"\n2. Executing count query for entity_type='{entity_type}', doc_type='{doc_type}'")
    
    result = structured_query_engine.execute_count_query(
        entity_type=entity_type,
        user_id=user_id,
        doc_type=doc_type,
        date_filter=None,
        other_filters={}
    )
    
    print(f"\n3. Result: {result}")
    print(f"\n4. Count: {result['count']}")
