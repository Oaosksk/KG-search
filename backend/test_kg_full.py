#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from app.services.parser import parser
from app.services.kg_builder import kg_builder
from app.services.llm_entity_extractor import llm_extractor

# Test with actual file
file_path = "uploads/112944693963105753678_b2ed46f9635e41ffbb02582c90db545c21215c8177316c97a6b88eab0e57c4a4.docx"
user_id = "test_debug_final"
file_id = "test_file"

print("=" * 70)
print("STEP 1: PARSING FILE")
print("=" * 70)
parsed_data = parser.parse_file(file_path)
print(f"Parsed {len(parsed_data)} records\n")

for i, record in enumerate(parsed_data):
    print(f"Record {i+1}:")
    print(record.get('content', '')[:200])
    print()

print("=" * 70)
print("STEP 2: LLM EXTRACTION TEST (First Record)")
print("=" * 70)
test_content = parsed_data[0].get('content', '')
llm_result = llm_extractor.extract_entities_and_relations(test_content, "deals")

print(f"Entities extracted: {len(llm_result.get('entities', []))}")
for e in llm_result.get('entities', []):
    print(f"  - {e['text']} ({e['type']})")

print(f"\nRelations extracted: {len(llm_result.get('relations', []))}")
for r in llm_result.get('relations', []):
    print(f"  - {r['source']} --[{r['relation']}]--> {r['target']}")

print("\n" + "=" * 70)
print("STEP 3: BUILDING KNOWLEDGE GRAPH")
print("=" * 70)

# Clear existing graph
if user_id in kg_builder.graphs:
    del kg_builder.graphs[user_id]

result = kg_builder.build_graph(parsed_data, file_id, user_id, "deals")

G = kg_builder.graphs[user_id]
print(f"\n✅ Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

print("\n" + "=" * 70)
print("FINAL GRAPH STRUCTURE")
print("=" * 70)

print("\nNODES:")
for i, (node, data) in enumerate(G.nodes(data=True)):
    print(f"{i+1}. {data.get('entity_text')} ({data.get('entity_type')})")

print("\nEDGES:")
if G.number_of_edges() > 0:
    for i, (source, target, data) in enumerate(G.edges(data=True)):
        src_text = G.nodes[source].get('entity_text')
        tgt_text = G.nodes[target].get('entity_text')
        print(f"{i+1}. {src_text} --[{data.get('relation')}]--> {tgt_text}")
else:
    print("❌ NO EDGES CREATED!")

print("\n" + "=" * 70)
print("DIAGNOSIS")
print("=" * 70)

if G.number_of_edges() == 0:
    print("❌ PROBLEM: No edges in graph - relations not being added")
    print("\nPossible causes:")
    print("1. LLM not returning relations")
    print("2. Entity text matching failing")
    print("3. Nodes not being found when adding edges")
elif G.number_of_edges() < 5:
    print("⚠️ WARNING: Very few edges - graph is sparse")
else:
    print("✅ SUCCESS: Graph has good connectivity")
