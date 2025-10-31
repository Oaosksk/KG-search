import pickle
from pathlib import Path

user_id = "112944693963105753678"
graph_path = Path(f"storage/graphs/{user_id}.pkl")

if graph_path.exists():
    with open(graph_path, 'rb') as f:
        G = pickle.load(f)
    
    print(f"Total nodes: {len(G.nodes())}")
    print(f"Total edges: {len(G.edges())}")
    print("\n" + "="*80)
    
    # Group nodes by doc_type
    doc_types = {}
    for node_id, data in G.nodes(data=True):
        dt = data.get('doc_type', 'unknown')
        if dt not in doc_types:
            doc_types[dt] = []
        doc_types[dt].append((node_id, data))
    
    print(f"\nDoc types found: {list(doc_types.keys())}")
    print("="*80)
    
    # Show sample nodes from each doc_type
    for doc_type, nodes in doc_types.items():
        print(f"\n{doc_type.upper()} ({len(nodes)} nodes):")
        print("-"*80)
        for node_id, data in nodes[:5]:
            print(f"  Node: {node_id}")
            print(f"    entity_text: {data.get('entity_text')}")
            print(f"    entity_type: {data.get('entity_type')}")
            print(f"    entity_value: {data.get('entity_value')}")
            print(f"    file_id: {data.get('file_id')[:20]}...")
            print()
else:
    print(f"Graph file not found: {graph_path}")
