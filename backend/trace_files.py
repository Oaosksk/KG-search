import sys
sys.path.insert(0, '/home/ven/KG-Search/backend')

import json
import pickle
from pathlib import Path

user_id = "112944693963105753678"

# Load file registry
registry_file = Path("uploads/file_registry.json")
if registry_file.exists():
    with open(registry_file, 'r') as f:
        registry = json.load(f)
    
    print("=== Uploaded Files ===")
    user_files = {k: v for k, v in registry.items() if k.startswith(user_id)}
    for key, info in user_files.items():
        print(f"\nFile: {info['filename']}")
        print(f"  ID: {info['file_id']}")
        print(f"  Path: {info['path']}")
        print(f"  Size: {info['size']} bytes")

# Load graph
graph_path = Path("storage/graphs") / f"{user_id}.pkl"
if graph_path.exists():
    with open(graph_path, 'rb') as f:
        G = pickle.load(f)
    
    print(f"\n=== Graph Analysis ===")
    print(f"Total nodes: {len(G.nodes())}")
    
    # Group by file_id and doc_type
    by_file = {}
    for node, data in G.nodes(data=True):
        fid = data.get('file_id', 'unknown')
        dt = data.get('doc_type', 'unknown')
        key = f"{fid}_{dt}"
        if key not in by_file:
            by_file[key] = []
        by_file[key].append(data)
    
    print(f"\nNodes by file_id and doc_type:")
    for key, nodes in sorted(by_file.items()):
        fid, dt = key.rsplit('_', 1)
        print(f"  file_id={fid[:12]}..., doc_type='{dt}': {len(nodes)} nodes")
        # Show sample entities
        sample = nodes[:3]
        for n in sample:
            print(f"    - {n.get('entity_text')} ({n.get('entity_type')})")
else:
    print("No graph found")
