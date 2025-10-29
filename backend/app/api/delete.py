from fastapi import APIRouter, HTTPException, Depends
from ..core.auth import get_current_user
from ..services.supabase_client import supabase_client
import os
import json

router = APIRouter()

@router.delete("/file/{file_id}")
async def delete_file(file_id: str, user: dict = Depends(get_current_user)):
    user_id = user["id"]
    print(f"\n🗑️ DELETE REQUEST: file_id={file_id}, user_id={user_id}")
    
    try:
        # Delete from Supabase
        if supabase_client.enabled:
            try:
                supabase_client.client.table('kg_nodes').delete().eq('file_id', file_id).execute()
                supabase_client.client.table('kg_edges').delete().eq('file_id', file_id).execute()
                supabase_client.client.table('embeddings').delete().eq('file_id', file_id).execute()
            except:
                pass
        
        # Remove from file registry
        from ..services.file_manager import file_manager
        registry_path = "uploads/file_registry.json"
        
        if os.path.exists(registry_path):
            with open(registry_path, 'r') as f:
                registry = json.load(f)
            
            # Find and remove file
            file_to_delete = None
            key_to_delete = None
            
            print(f"  Registry has {len(registry)} entries")
            
            for key, file_info in registry.items():
                print(f"  Checking: {key} -> file_id={file_info.get('file_id')}")
                if file_info.get('file_id') == file_id and file_info.get('user_id') == user_id:
                    file_to_delete = file_info
                    key_to_delete = key
                    print(f"  ✓ Found match: {key}")
                    break
            
            if key_to_delete:
                print(f"  Deleting key: {key_to_delete}")
                del registry[key_to_delete]
                
                with open(registry_path, 'w') as f:
                    json.dump(registry, f, indent=2)
                
                # Reload registry in file_manager
                file_manager.hash_registry = file_manager._load_registry()
                print(f"  ✓ Reloaded registry, now has {len(file_manager.hash_registry)} entries")
                
                # Delete physical file
                if file_to_delete and file_to_delete.get('source') != 'gdrive':
                    file_path = file_to_delete.get('path')
                    print(f"  File path: {file_path}")
                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"  ✓ Deleted physical file: {file_path}")
                    else:
                        print(f"  ⚠️ File not found: {file_path}")
            else:
                print(f"  ⚠️ No matching file found in registry")
        
        # Reload graphs from storage
        from ..services.kg_builder import kg_builder
        from ..services.rag_engine import rag_engine
        
        if user_id in kg_builder.graphs:
            del kg_builder.graphs[user_id]
        
        if user_id in rag_engine.indices:
            del rag_engine.indices[user_id]
            del rag_engine.documents[user_id]
        
        return {"message": "File deleted successfully", "file_id": file_id}
    
    except Exception as e:
        print(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
