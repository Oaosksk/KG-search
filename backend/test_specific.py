#!/usr/bin/env python3
"""Quick test for specific failing queries"""

import requests
import json

API_URL = "http://localhost:8000"
JWT_TOKEN = input("Paste JWT token: ").strip()

# Test specific failing queries
TESTS = [
    ("Show me Stellar Retail's orders", "Should return 2: 601, 602"),
    ("What did Nova Mart order?", "Should return 1: 502"),
    ("List closed deals from Gamma LLC", "Should return 1: 102"),
    ("Show me orders over 4000", "Should return 2: 502, 602"),
    ("Show open deals worth more than 10000", "Should return 1: 103"),
    ("List all products", "Should return 6 products"),
]

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

for query, expected in TESTS:
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"Expected: {expected}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{API_URL}/search/",
            headers=headers,
            json={"query": query, "top_k": 10},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            entities = data.get('kg_entities', [])
            print(f"✅ Got {len(entities)} results")
            
            # Extract IDs
            ids = [e.get('entity_text') for e in entities if e.get('entity_text', '').isdigit()]
            if ids:
                print(f"   IDs: {ids}")
            
            # Show first result details
            if entities:
                print(f"   First result: {entities[0].get('entity_text')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text[:200]}")
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT (>15s)")
    except Exception as e:
        print(f"❌ Error: {e}")

print(f"\n{'='*60}")
print("Test complete!")
