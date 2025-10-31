import sys
sys.path.insert(0, '/home/ven/KG-Search/backend')

import pickle
from pathlib import Path

user_id = "112944693963105753678"
graph_path = Path("storage/graphs") / f"{user_id}.pkl"

if graph_path.exists():
    with open(graph_path, 'rb') as f:
        G = pickle.load(f)
    
    print(f"Total nodes: {len(G.nodes())}")
    
    # Count by doc_type
    doc_types = {}
    entity_types = {}
    for node, data in G.nodes(data=True):
        dt = data.get('doc_type', 'None')
        et = data.get('entity_type', 'None')
        doc_types[dt] = doc_types.get(dt, 0) + 1
        entity_types[et] = entity_types.get(et, 0) + 1
    
    print(f"\nNodes by doc_type:")
    for dt, count in sorted(doc_types.items()):
        print(f"  '{dt}': {count}")
    
    print(f"\nNodes by entity_type:")
    for et, count in sorted(entity_types.items()):
        print(f"  {et}: {count}")
    
    # Show sample nodes
    print(f"\nSample nodes (first 15):")
    for i, (node, data) in enumerate(list(G.nodes(data=True))[:15]):
        print(f"  {i+1}. '{data.get('entity_text')}' (type={data.get('entity_type')}, doc_type='{data.get('doc_type')}')")
else:
    print(f"Graph file not found: {graph_path}")
