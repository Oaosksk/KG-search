import sys
sys.path.insert(0, '/home/ven/KG-Search/backend')

from app.services.parser import parser
from app.services.kg_builder import kg_builder
from pathlib import Path

user_id = "112944693963105753678"
file_id = "3680541d459db7fc7fab32633e08b8e4290ab4ac5b5fc6558b823dc8306e4e29"
file_path = f"uploads/{user_id}_{file_id}.xlsx"

print(f"Re-processing customer file with correct doc_type...")
print(f"File: {file_path}")

# Parse the file
parsed_data = parser.parse_file(file_path)
print(f"Parsed {len(parsed_data)} items")

# Show sample
if parsed_data:
    print(f"\nSample data:")
    print(parsed_data[0])

# Rebuild KG with correct doc_type
print(f"\nRebuilding KG with doc_type='customers'...")
kg_result = kg_builder.build_graph(parsed_data, file_id, user_id, doc_type="customers")
print(f"Result: {kg_result}")

# Verify
import pickle
graph_path = Path("storage/graphs") / f"{user_id}.pkl"
with open(graph_path, 'rb') as f:
    G = pickle.load(f)

# Count by doc_type
doc_types = {}
for node, data in G.nodes(data=True):
    dt = data.get('doc_type', 'None')
    doc_types[dt] = doc_types.get(dt, 0) + 1

print(f"\nUpdated graph stats:")
for dt, count in sorted(doc_types.items()):
    print(f"  {dt}: {count} nodes")
