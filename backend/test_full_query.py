#!/usr/bin/env python3
"""Test full query flow"""

from app.services.query_analyzer import query_analyzer
from app.services.structured_query_engine import structured_query_engine

user_id = "112944693963105753678"
query = "How many customers do we have?"

print("=" * 80)
print(f"Testing Query: '{query}'")
print("=" * 80)

# Step 1: Analyze query
print("\n1. Query Analysis:")
analysis = query_analyzer.analyze_query(query)
print(f"   Type: {analysis.get('type')}")
print(f"   Doc Type: {analysis.get('doc_type')}")
print(f"   Entities: {analysis.get('entities')}")

# Step 2: Check routing
print("\n2. Routing Decision:")
if analysis.get('type') in ['count', 'list']:
    print("   ✅ Will use Structured Query Engine")
    
    # Step 3: Execute structured query
    print("\n3. Executing Structured Query:")
    entity_type = analysis.get('entities', ['customers'])[0] if analysis.get('entities') else 'customers'
    doc_type = analysis.get('doc_type')
    
    print(f"   Entity Type: {entity_type}")
    print(f"   Doc Type Filter: {doc_type}")
    
    result = structured_query_engine.execute_count_query(
        entity_type=entity_type,
        user_id=user_id,
        doc_type=doc_type
    )
    
    print(f"\n4. Result:")
    print(f"   Count: {result['count']}")
    print(f"   Sample Items: {result['items'][:3]}")
    
    if result['count'] == 0:
        print("\n   ⚠️ No results found!")
        print("   Possible reasons:")
        print("   - No customer data uploaded")
        print("   - Doc type mismatch")
        print("   - Graph not loaded")
else:
    print("   ⚠️ Will use Hybrid Search (wrong for count queries)")

print("\n" + "=" * 80)
