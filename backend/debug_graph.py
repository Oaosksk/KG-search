#!/usr/bin/env python3
"""Debug graph to see what's stored"""

import pickle
from pathlib import Path

user_id = "112944693963105753678"  # Your user ID from uploads
graph_path = Path(f"storage/graphs/{user_id}.pkl")

if graph_path.exists():
    with open(graph_path, 'rb') as f:
        G = pickle.load(f)
    
    print(f"Total nodes in graph: {len(G.nodes())}")
    print("=" * 80)
    
    # Count by doc_type
    doc_types = {}
    for node, data in G.nodes(data=True):
        doc_type = data.get('doc_type', 'unknown')
        if doc_type not in doc_types:
            doc_types[doc_type] = []
        doc_types[doc_type].append((node, data))
    
    print("\nNodes by doc_type:")
    print("-" * 80)
    for doc_type, nodes in doc_types.items():
        print(f"\n{doc_type}: {len(nodes)} nodes")
        # Show first 5 nodes
        for node, data in nodes[:5]:
            entity_text = data.get('entity_text', 'N/A')
            entity_type = data.get('entity_type', 'N/A')
            print(f"  - {entity_text} ({entity_type})")
        if len(nodes) > 5:
            print(f"  ... and {len(nodes) - 5} more")
    
    print("\n" + "=" * 80)
    print("Summary:")
    for doc_type, nodes in doc_types.items():
        print(f"  {doc_type}: {len(nodes)} nodes")
    
else:
    print(f"Graph file not found: {graph_path}")
    print("Available graph files:")
    for f in Path("storage/graphs").glob("*.pkl"):
        print(f"  - {f.name}")
