from fastapi import APIRouter, Depends
from ..core.auth import get_current_user
from typing import List, Dict, Any

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/list")
async def list_files(user: dict = Depends(get_current_user)):
    from ..services.file_manager import file_manager
    from ..services.kg_builder import kg_builder
    user_id = user["id"]
    
    # Load graph to check which files have been processed
    if user_id not in kg_builder.graphs:
        kg_builder._load_graph(user_id)
    
    processed_files = set()
    if user_id in kg_builder.graphs:
        G = kg_builder.graphs[user_id]
        processed_files = set(d.get('file_id') for _, d in G.nodes(data=True) if d.get('file_id'))
    
    uploaded = []
    synced = []
    
    for key, file_info in file_manager.hash_registry.items():
        if file_info.get("user_id") == user_id:
            file_data = {
                "file_id": file_info["file_id"],
                "filename": file_info["filename"],
                "processed": file_info["file_id"] in processed_files
            }
            
            if file_info.get("source") == "gdrive":
                synced.append(file_data)
            else:
                uploaded.append(file_data)
    
    return {
        "uploaded": uploaded,
        "synced": synced
    }

@router.get("/kg/{file_id}")
async def get_file_kg(file_id: str, user: dict = Depends(get_current_user)):
    from ..services.kg_builder import kg_builder
    user_id = user["id"]
    
    print(f"[KG] Fetching KG for file_id: {file_id}, user_id: {user_id}")
    
    # Load user's graph
    if user_id not in kg_builder.graphs:
        kg_builder._load_graph(user_id)
    
    if user_id not in kg_builder.graphs:
        print(f"[KG] No graph found for user {user_id}")
        return {"nodes": [], "edges": [], "error": "No graph found for user"}
    
    G = kg_builder.graphs[user_id]
    print(f"[KG] Graph has {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    # Get all file_ids in graph for debugging
    all_file_ids = set(data.get('file_id') for _, data in G.nodes(data=True) if data.get('file_id'))
    print(f"[KG] File IDs in graph: {all_file_ids}")
    
    # Filter nodes by file_id
    file_nodes = [(node, data) for node, data in G.nodes(data=True) 
                  if data.get('file_id') == file_id]
    
    print(f"[KG] Found {len(file_nodes)} nodes for file_id {file_id}")
    
    if not file_nodes:
        return {
            "nodes": [], 
            "edges": [], 
            "error": f"No nodes found for file {file_id}. File may not be processed yet.",
            "available_files": list(all_file_ids)
        }
    
    # Build node map
    node_map = {node: idx for idx, (node, _) in enumerate(file_nodes)}
    
    # Extract nodes
    nodes = [{"entity_text": data.get('entity_text', 'Unknown'),
             "entity_type": data.get('entity_type', 'UNKNOWN'),
             "entity_value": data.get('entity_value', '')} 
            for node, data in file_nodes]
    
    # Extract edges within this file
    edges = []
    seen_edges = set()
    for node, _ in file_nodes:
        for neighbor in G.neighbors(node):
            if neighbor in node_map:
                edge_key = (min(node_map[node], node_map[neighbor]), max(node_map[node], node_map[neighbor]))
                if edge_key not in seen_edges:
                    edge_data = G.get_edge_data(node, neighbor)
                    edges.append({
                        "source": node_map[node],
                        "target": node_map[neighbor],
                        "relation": edge_data.get('relation', 'related')
                    })
                    seen_edges.add(edge_key)
    
    print(f"[KG] Returning {len(nodes)} nodes, {len(edges)} edges")
    return {"nodes": nodes, "edges": edges}
