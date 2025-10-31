#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Query Testing Script
Tests queries against the KG-Search system and validates results
"""

import requests
import json
import sys
from typing import Dict, List, Tuple

# Configuration
API_URL = "http://localhost:8000"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjExMjk0NDY5Mzk2MzEwNTc1MzY3OCIsImVtYWlsIjoiZGRldjkzMTA3QGdtYWlsLmNvbSIsIm5hbWUiOiJEZXYgRGV2IiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0w3WWo0UUYtTXA1UjdtODhxcXpodkhUU2NvdlloMnVGc1ltSnhkMm9KWEF1RU1EZz1zOTYtYyIsImFjY2Vzc190b2tlbiI6InlhMjkuQTBBVGk2SzJzN3p1QXZMMmFGa2VOZHVVUkpnVXNYdHdfTUFaRF9MLTZMc2VoOHpzcG5EX2Rrbkg0eDR3ZnBnUi01dnpCWmoxYUpneE9YLVBvcTRqV3JjYUZvN3NyQmZLRVdqSUFRdVEzLXZYemJUZFRkQ01FU1JsNE1vRHBMclFvMllJdEgtWURlN0luSTB2SEN3UHBWRnRaVWFzenFIUndYOS1nUEdDUndqYmg4dDBQdkROX1dzelNsWVZGY05TQ3dxbmQ3UXQ2R0pnZGlGWURKVlMxellTekM1cWxQbEJiQ1JGQWk2UkpVdi1ob3dvaHNvYXVGUG41c2l6dzlfcUxBLUV6VHUxSi1OZDFzQ041eGZvaVhUSE9RVXVJYUNnWUtBWlVTQVJRU0ZRSEdYMk1pTkk2ZDNxM2pYeG5rczlMcHVnYmRyZzAyOTAiLCJleHAiOjE3NjI0MjI5MTl9.rpi_QVuNruTW7k8qYX8VUQE5uc5bBA1jB7WmO2hCz70"  # Replace with actual token

# Test queries with expected results
TEST_QUERIES = [
    # ========== BASIC RETRIEVAL ==========
    {"query": "How many orders do we have?", "expected_count": 6, "level": "simple", "category": "basic"},
    {"query": "Show me all orders.", "expected_count": 6, "level": "simple", "category": "basic"},
    {"query": "Show me all deals.", "expected_count": 3, "level": "simple", "category": "basic"},
    {"query": "How many deals are there?", "expected_count": 3, "level": "simple", "category": "basic"},
    {"query": "List all orders and deals together.", "expected_count": 9, "level": "medium", "category": "basic"},
    
    # ========== STATUS-BASED UNDERSTANDING ==========
    {"query": "Show me delivered orders.", "expected_count": 4, "expected_ids": ["501", "502", "601", "602"], "level": "simple", "category": "status"},
    {"query": "List pending orders.", "expected_count": 2, "expected_ids": ["503", "603"], "level": "simple", "category": "status"},
    {"query": "Show me closed deals.", "expected_count": 2, "expected_ids": ["101", "102"], "level": "simple", "category": "status"},
    {"query": "What deals are still open?", "expected_count": 1, "expected_ids": ["103"], "level": "simple", "category": "status"},
    {"query": "Delivered orders over 4000.", "expected_count": 2, "expected_ids": ["502", "602"], "level": "medium", "category": "status"},
    
    # ========== CUSTOMER / CLIENT CONTEXT ==========
    {"query": "Show me orders from Orion Traders.", "expected_count": 1, "expected_ids": ["501"], "level": "medium", "category": "customer"},
    {"query": "What deals do we have with Alpha Co?", "expected_count": 1, "expected_ids": ["101"], "level": "medium", "category": "customer"},
    {"query": "Show me Stellar Retail's orders.", "expected_count": 2, "expected_ids": ["601", "602"], "level": "medium", "category": "customer"},
    {"query": "List closed deals from Gamma LLC.", "expected_count": 1, "expected_ids": ["102"], "level": "medium", "category": "customer"},
    {"query": "What did Nova Mart order?", "expected_count": 1, "expected_ids": ["502"], "level": "medium", "category": "customer"},
    
    # ========== PRODUCT / DEAL CONTEXT ==========
    {"query": "Show me orders for Wireless Headphones.", "expected_count": 1, "expected_ids": ["501"], "level": "medium", "category": "product"},
    {"query": "What orders include Smartwatch X2?", "expected_count": 1, "expected_ids": ["502"], "level": "medium", "category": "product"},
    {"query": "Tell me about the Alpha Product deal.", "expected_count": 1, "expected_ids": ["101"], "level": "medium", "category": "product"},
    {"query": "List deals related to software.", "expected_count": 1, "expected_ids": ["103"], "level": "medium", "category": "product"},
    {"query": "List all products", "expected_count": 6, "level": "simple", "category": "product"},
    
    # ========== DATE-BASED UNDERSTANDING ==========
    {"query": "Show me orders between Oct 21 and Oct 23.", "expected_count": 4, "level": "critical", "category": "date"},
    {"query": "List deals closed on October 22, 2025.", "expected_count": 1, "expected_ids": ["101"], "level": "critical", "category": "date"},
    {"query": "What deals were finalized in October 2025?", "expected_count": 2, "expected_ids": ["101", "102"], "level": "critical", "category": "date"},
    {"query": "Show me orders from October 22, 2025", "expected_count": 2, "expected_ids": ["501", "602"], "level": "critical", "category": "date"},
    
    # ========== COMBINED / COMPLEX FILTERS ==========
    {"query": "Show me delivered orders over 4000.", "expected_count": 2, "expected_ids": ["502", "602"], "level": "critical", "category": "combined"},
    {"query": "List pending orders from Horizon Outlet.", "expected_count": 1, "expected_ids": ["503"], "level": "critical", "category": "combined"},
    {"query": "Show me closed deals with Alpha Co.", "expected_count": 1, "expected_ids": ["101"], "level": "critical", "category": "combined"},
    {"query": "Show open deals worth more than 10000.", "expected_count": 1, "expected_ids": ["103"], "level": "critical", "category": "combined"},
    {"query": "Show me orders over 4000", "expected_count": 2, "expected_ids": ["502", "602"], "level": "medium", "category": "combined"},
    
    # ========== NATURAL LANGUAGE VARIATION ==========
    {"query": "Can you show me the deals?", "expected_count": 3, "level": "simple", "category": "natural"},
    {"query": "I want to see pending orders.", "expected_count": 2, "expected_ids": ["503", "603"], "level": "simple", "category": "natural"},
    {"query": "Give me a list of all orders we've got.", "expected_count": 6, "level": "simple", "category": "natural"},
    {"query": "Find orders worth more than five thousand.", "expected_count": 1, "expected_ids": ["602"], "level": "medium", "category": "natural"},
    
    # ========== BUSINESS ANALYTICAL QUERIES ==========
    {"query": "What is the total value of all orders?", "expected_type": "analytical", "level": "critical", "category": "analytical"},
    {"query": "What is the total value of all deals?", "expected_type": "analytical", "level": "critical", "category": "analytical"},
    {"query": "What is the average deal size?", "expected_type": "analytical", "level": "critical", "category": "analytical"},
    {"query": "What is the average order amount?", "expected_type": "analytical", "level": "critical", "category": "analytical"},
    {"query": "Which customer has the most orders?", "expected_type": "analytical", "level": "critical", "category": "analytical"},
    {"query": "Which client has the most deals?", "expected_type": "analytical", "level": "critical", "category": "analytical"},
    {"query": "What is the largest order?", "expected_type": "analytical", "level": "critical", "category": "analytical"},
    {"query": "What is the highest value deal?", "expected_type": "analytical", "level": "critical", "category": "analytical"},
    
    # ========== BUSINESS INSIGHTS ==========
    {"query": "Summarize all delivered orders.", "expected_type": "insight", "level": "critical", "category": "insight"},
    {"query": "Give me an overview of closed deals.", "expected_type": "insight", "level": "critical", "category": "insight"},
    {"query": "Which products are most popular?", "expected_type": "insight", "level": "critical", "category": "insight"},
    {"query": "Who are our biggest clients?", "expected_type": "insight", "level": "critical", "category": "insight"},
    {"query": "What is the total value across orders and deals combined?", "expected_type": "insight", "level": "critical", "category": "insight"},
    
    # ========== CROSS-DOMAIN ANALYTICAL ==========
    {"query": "Show me customers who have both orders and deals.", "expected_type": "cross_domain", "level": "critical", "category": "cross_domain"},
    {"query": "What clients have pending orders and open deals?", "expected_type": "cross_domain", "level": "critical", "category": "cross_domain"},
    {"query": "Compare the average order amount vs average deal size.", "expected_type": "cross_domain", "level": "critical", "category": "cross_domain"},
]


class TestResult:
    def __init__(self, query: str, level: str, category: str = "other"):
        self.query = query
        self.level = level
        self.category = category
        self.passed = False
        self.actual_count = 0
        self.expected_count = 0
        self.actual_ids = []
        self.expected_ids = []
        self.error = None
        self.response = None


def run_query(query: str, token: str) -> Dict:
    """Execute a search query against the API"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": query,
        "top_k": 10
    }
    
    try:
        response = requests.post(
            f"{API_URL}/search/",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return {"error": "Authentication failed. Please check your JWT token."}
        return {"error": f"HTTP {e.response.status_code}: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}


def extract_ids_from_response(response: Dict) -> List[str]:
    """Extract entity IDs from response"""
    ids = []
    
    # Check kg_entities
    if "kg_entities" in response:
        for entity in response["kg_entities"]:
            entity_text = entity.get("entity_text", "")
            if entity_text.isdigit():
                ids.append(entity_text)
    
    # Check answer text
    if "answer" in response:
        import re
        answer = response["answer"]
        # Extract numbers that look like IDs (501, 502, etc.)
        found_ids = re.findall(r'\b\d{3}\b', answer)
        ids.extend(found_ids)
    
    return list(set(ids))  # Remove duplicates


def validate_result(test: Dict, response: Dict) -> TestResult:
    """Validate test result against expected values"""
    result = TestResult(test["query"], test["level"], test.get("category", "other"))
    result.response = response
    
    if "error" in response:
        result.error = response["error"]
        return result
    
    # For analytical/insight queries, just check if answer exists
    if test.get("expected_type") in ["analytical", "insight", "cross_domain"]:
        result.passed = bool(response.get("answer"))
        return result
    
    # Extract actual results
    result.actual_count = len(response.get("kg_entities", []))
    result.actual_ids = extract_ids_from_response(response)
    
    # Expected values
    result.expected_count = test.get("expected_count", 0)
    result.expected_ids = test.get("expected_ids", [])
    
    # Validation
    if result.expected_count > 0:
        count_match = result.actual_count == result.expected_count
    else:
        count_match = True
    
    if result.expected_ids:
        ids_match = set(result.actual_ids) == set(result.expected_ids)
    else:
        ids_match = True
    
    result.passed = count_match and ids_match
    
    return result


def print_results(results: List[TestResult]):
    """Print test results in a formatted way"""
    
    print("\n" + "="*80)
    print("AUTOMATED QUERY TEST RESULTS")
    print("="*80 + "\n")
    
    # Group by category
    categories = {}
    for result in results:
        cat = getattr(result, 'category', 'other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(result)
    
    # Print by category
    for category, tests in sorted(categories.items()):
        passed = sum(1 for t in tests if t.passed)
        total = len(tests)
        
        print(f"\n📁 {category.upper()}: {passed}/{total} passed")
        print("-" * 80)
        
        for result in tests:
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.query[:70]}")
            
            if result.error:
                print(f"   ERROR: {result.error}")
            elif not result.passed:
                print(f"   Expected: {result.expected_count}, Got: {result.actual_count}")
                if result.expected_ids:
                    print(f"   Expected IDs: {result.expected_ids}")
                    print(f"   Actual IDs:   {result.actual_ids}")
    
    # Summary by level
    print("\n" + "="*80)
    print("SUMMARY BY DIFFICULTY LEVEL")
    print("="*80)
    
    levels = {"simple": [], "medium": [], "critical": []}
    for result in results:
        levels[result.level].append(result)
    
    for level in ["simple", "medium", "critical"]:
        tests = levels[level]
        if tests:
            passed = sum(1 for t in tests if t.passed)
            total = len(tests)
            print(f"{level.upper()}: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    # Overall summary
    total_passed = sum(1 for r in results if r.passed)
    total_tests = len(results)
    pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print("\n" + "="*80)
    print(f"OVERALL: {total_passed}/{total_tests} tests passed ({pass_rate:.1f}%)")
    print("="*80 + "\n")


def main():
    """Run all tests"""
    print("Starting automated query testing...")
    print(f"API URL: {API_URL}")
    print(f"Total tests: {len(TEST_QUERIES)}\n")
    
    # Check if token is set
    if JWT_TOKEN == "YOUR_JWT_TOKEN_HERE" or "…" in JWT_TOKEN or len(JWT_TOKEN) < 50:
        print("⚠️  WARNING: JWT_TOKEN not set or incomplete!")
        print("\nTo get your token:")
        print("1. Open http://localhost:3000 in browser")
        print("2. Login with Google OAuth")
        print("3. Press F12 → Console tab")
        print("4. Type: localStorage.getItem('token')")
        print("5. Copy the FULL token (should be ~200+ characters)")
        print("6. Paste it in this script replacing JWT_TOKEN value")
        print("\nNote: Make sure to copy the COMPLETE token without truncation!\n")
        return
    
    results = []
    
    for i, test in enumerate(TEST_QUERIES, 1):
        print(f"[{i}/{len(TEST_QUERIES)}] Testing: {test['query'][:50]}...")
        
        response = run_query(test["query"], JWT_TOKEN)
        result = validate_result(test, response)
        results.append(result)
    
    print_results(results)
    
    # Save detailed results to file
    with open("test_results.json", "w") as f:
        json.dump([{
            "query": r.query,
            "level": r.level,
            "category": r.category,
            "passed": r.passed,
            "expected_count": r.expected_count,
            "actual_count": r.actual_count,
            "expected_ids": r.expected_ids,
            "actual_ids": r.actual_ids,
            "error": r.error
        } for r in results], f, indent=2)
    
    print("Detailed results saved to: test_results.json")


if __name__ == "__main__":
    main()
