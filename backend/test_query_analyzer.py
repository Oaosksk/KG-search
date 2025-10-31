import sys
sys.path.insert(0, '/home/ven/KG-Search/backend')

from app.services.query_analyzer import query_analyzer

print("Testing query analyzer...")
print(f"Enabled: {query_analyzer.enabled}")

if query_analyzer.enabled:
    result = query_analyzer.analyze_query("How many customers do we have?")
    print(f"\nResult: {result}")
else:
    print("Query analyzer is disabled!")
