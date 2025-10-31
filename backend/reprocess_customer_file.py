#!/usr/bin/env python3
"""Re-process customer file to extract entities"""

from app.services.parser import parser
from app.services.kg_builder import kg_builder
from app.services.rag_engine import rag_engine
from app.services.doc_type_detector import doc_detector

user_id = "112944693963105753678"
file_path = "uploads/112944693963105753678_3680541d459db7fc7fab32633e08b8e4290ab4ac5b5fc6558b823dc8306e4e29.xlsx"
file_id = "3680541d459db7fc7fab32633e08b8e4290ab4ac5b5fc6558b823dc8306e4e29"

print("Re-processing CustomerData.xlsx")
print("=" * 80)

# Parse file
print("\n1. Parsing file...")
parsed_data = parser.parse_file(file_path)
print(f"   Parsed {len(parsed_data)} records")

# Show sample
if parsed_data:
    print(f"\n   Sample record:")
    print(f"   {str(parsed_data[0])[:200]}...")

# Detect document type
print("\n2. Detecting document type...")
sample_content = str(parsed_data[0].get('content', ''))[:2000] if parsed_data else ""
doc_info = doc_detector.detect_type(sample_content)
doc_type = doc_info.get("type", "unknown")
print(f"   Detected: {doc_type}")

# Build KG
print("\n3. Building Knowledge Graph...")
kg_result = kg_builder.build_graph(parsed_data, file_id, user_id, doc_type)
print(f"   Created {kg_result['nodes']} nodes")
print(f"   Doc type: {kg_result.get('doc_type', 'unknown')}")

# Store embeddings
print("\n4. Storing embeddings...")
rag_engine.store_embeddings(parsed_data, file_id, user_id)
print(f"   Stored embeddings for {len(parsed_data)} records")

print("\n" + "=" * 80)
print("✅ Re-processing complete!")
print("\nNow try: 'How many customers do we have?'")
