import sys
sys.path.insert(0, '/home/ven/KG-Search/backend')

from app.services.kg_builder import kg_builder
import pickle
from pathlib import Path

user_id = "112944693963105753678"

# Check what files were uploaded
from app.services.file_manager import file_manager
file_manager._load_registry()

print("=== Uploaded Files ===")
if user_id in file_manager.file_registry:
    for file_id, file_info in file_manager.file_registry[user_id].items():
        print(f"  {file_id}: {file_info.get('filename')} (uploaded: {file_info.get('uploaded_at')})")
else:
    print("  No files found for user")

# Check graph
graph_path = Path("storage/graphs") / f"{user_id}.pkl"
if graph_path.exists():
    with open(graph_path, 'rb') as f:
        G = pickle.load(f)
    
    print(f"\n=== Graph Stats ===")
    print(f"Total nodes: {len(G.nodes())}")
    
    # Group by file_id
    by_file = {}
    for node, data in G.nodes(data=True):
        fid = data.get('file_id', 'unknown')
        if fid not in by_file:
            by_file[fid] = []
        by_file[fid].append(data)
    
    print(f"\nNodes by file_id:")
    for fid, nodes in by_file.items():
        doc_types = set(n.get('doc_type', 'None') for n in nodes)
        print(f"  {fid}: {len(nodes)} nodes, doc_types={doc_types}")
