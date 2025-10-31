import sys
sys.path.insert(0, '/home/ven/KG-Search/backend')

from app.services.parser import parser
from app.services.kg_builder import kg_builder

user_id = "112944693963105753678"

# Process customers file
print("=== Processing CustomerData.xlsx ===")
file_id1 = "3680541d459db7fc7fab32633e08b8e4290ab4ac5b5fc6558b823dc8306e4e29"
file_path1 = f"uploads/{user_id}_{file_id1}.xlsx"
parsed1 = parser.parse_file(file_path1)
result1 = kg_builder.build_graph(parsed1, file_id1, user_id, doc_type="customers")
print(f"Result: {result1}\n")

# Process deals file
print("=== Processing Deals.docx ===")
file_id2 = "b2ed46f9635e41ffbb02582c90db545c21215c8177316c97a6b88eab0e57c4a4"
file_path2 = f"uploads/{user_id}_{file_id2}.docx"
parsed2 = parser.parse_file(file_path2)
result2 = kg_builder.build_graph(parsed2, file_id2, user_id, doc_type="deals")
print(f"Result: {result2}\n")

# Verify
import pickle
from pathlib import Path
graph_path = Path("storage/graphs") / f"{user_id}.pkl"
with open(graph_path, 'rb') as f:
    G = pickle.load(f)

doc_types = {}
for node, data in G.nodes(data=True):
    dt = data.get('doc_type', 'None')
    doc_types[dt] = doc_types.get(dt, 0) + 1

print("=== Final Graph Stats ===")
print(f"Total nodes: {len(G.nodes())}")
for dt, count in sorted(doc_types.items()):
    print(f"  {dt}: {count} nodes")
