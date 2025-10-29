from fastapi import APIRouter, Depends
from ..core.auth import get_current_user
from typing import List, Dict, Any

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/list")
async def list_files(user: dict = Depends(get_current_user)):
    from ..services.file_manager import file_manager
    user_id = user["id"]
    
    uploaded = []
    synced = []
    
    for key, file_info in file_manager.hash_registry.items():
        if file_info.get("user_id") == user_id:
            file_data = {
                "file_id": file_info["file_id"],
                "filename": file_info["filename"]
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
    
    # Load user's graph
    if user_id not in kg_builder.graphs:
        kg_builder._load_graph(user_id)
    
    if user_id not in kg_builder.graphs:
        return {"nodes": [], "edges": []}
    
    G = kg_builder.graphs[user_id]
    
    # Filter nodes by file_id
    file_nodes = [(node, data) for node, data in G.nodes(data=True) 
                  if data.get('file_id') == file_id]
    
    if not file_nodes:
        return {"nodes": [], "edges": []}
    
    # Build node map
    node_map = {node: idx for idx, (node, _) in enumerate(file_nodes)}
    
    # Extract nodes
    nodes = [{"entity_text": data.get('entity_text', 'Unknown'),
             "entity_type": data.get('entity_type', 'UNKNOWN'),
             "entity_value": data.get('entity_value', '')} 
            for node, data in file_nodes]
    
    # Extract edges within this file
    edges = []
    for node, _ in file_nodes:
        for neighbor in G.neighbors(node):
            if neighbor in node_map:
                edge_data = G.get_edge_data(node, neighbor)
                edges.append({
                    "source": node_map[node],
                    "target": node_map[neighbor],
                    "relation": edge_data.get('relation', 'related')
                })
    
    return {"nodes": nodes, "edges": edges}
