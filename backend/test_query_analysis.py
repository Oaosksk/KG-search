#!/usr/bin/env python3
"""Test query analysis"""

from app.services.query_analyzer import query_analyzer

test_queries = [
    "How many customers do we have?",
    "Show me all customers",
    "How many deals do we have?",
    "Show deals closed between Oct 12 and Oct 20"
]

print("Testing Query Analysis")
print("=" * 80)

for query in test_queries:
    print(f"\nQuery: '{query}'")
    print("-" * 80)
    
    result = query_analyzer.analyze_query(query)
    
    print(f"Type: {result.get('type')}")
    print(f"Doc Type: {result.get('doc_type')}")
    print(f"Entities: {result.get('entities')}")
    print(f"Date Filter: {result.get('date_filter')}")
    print(f"Intent: {result.get('intent')}")
    
    # Check if it will route correctly
    if result.get('type') in ['count', 'list']:
        print("✅ Will use Structured Query Engine")
    else:
        print("⚠️ Will use Hybrid Search (might be wrong for count queries)")

print("\n" + "=" * 80)
