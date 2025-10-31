import sys
sys.path.insert(0, '/home/ven/KG-Search/backend')

from app.services.kg_builder import kg_builder
import pickle
from pathlib import Path

user_id = "test_user"
graph_path = Path("data/graphs") / f"{user_id}.pkl"

if graph_path.exists():
    with open(graph_path, 'rb') as f:
        G = pickle.load(f)
    
    print(f"Total nodes: {len(G.nodes())}")
    
    # Count by doc_type
    doc_types = {}
    for node, data in G.nodes(data=True):
        dt = data.get('doc_type', 'None')
        doc_types[dt] = doc_types.get(dt, 0) + 1
    
    print(f"\nNodes by doc_type:")
    for dt, count in sorted(doc_types.items()):
        print(f"  {dt}: {count}")
    
    # Show sample nodes
    print(f"\nSample nodes (first 10):")
    for i, (node, data) in enumerate(list(G.nodes(data=True))[:10]):
        print(f"  {i+1}. {data.get('entity_text')} ({data.get('entity_type')}) - doc_type={data.get('doc_type')}")
else:
    print(f"Graph file not found: {graph_path}")
