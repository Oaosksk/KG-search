from fastapi import APIRouter, Depends, HTTPException
from ..core.auth import get_current_user
from typing import Dict, Any

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/gdrive")
async def sync_google_drive(user: dict = Depends(get_current_user)):
    from ..services.file_manager import file_manager
    from ..services.token_validator import token_validator
    import requests as http_requests
    user_id = user["id"]
    access_token = user.get("access_token")
    
    print(f"[SYNC] User ID: {user_id}")
    print(f"[SYNC] Access token present: {bool(access_token)}")
    
    if not access_token:
        raise HTTPException(
            status_code=401, 
            detail="Google Drive access token not found. Please log out and log in again to grant Drive permissions."
        )
    
    # Validate token before using it
    token_info = token_validator.validate_token(access_token)
    if not token_info.get("valid"):
        raise HTTPException(
            status_code=401,
            detail=f"Google token expired or invalid. Please log out and log in again. ({token_info.get('error', 'Unknown error')})"
        )
    
    if not token_info.get("has_drive_scope"):
        raise HTTPException(
            status_code=403,
            detail="Google Drive permission not granted. Please log out and log in again to grant Drive access."
        )
    
    print(f"[SYNC] Token valid, expires in {token_info.get('expires_in')} seconds")
    
    try:
        # Fetch files from Google Drive API
        headers = {"Authorization": f"Bearer {access_token}"}
        print(f"[SYNC] Calling Google Drive API...")
        
        response = http_requests.get(
            "https://www.googleapis.com/drive/v3/files",
            headers=headers,
            params={
                "pageSize": 100,
                "fields": "files(id, name, mimeType)",
                "q": "trashed=false"
            },
            timeout=10
        )
        
        print(f"[SYNC] Google Drive API response status: {response.status_code}")
        
        if response.status_code != 200:
            error_detail = response.json() if response.text else "Unknown error"
            print(f"[SYNC] Error: {error_detail}")
            raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch Google Drive files: {error_detail}")
        
        gdrive_files = response.json().get("files", [])
        print(f"[SYNC] Found {len(gdrive_files)} files in Google Drive")
        
        # Clear old gdrive entries for this user
        keys_to_remove = [k for k, v in file_manager.hash_registry.items() 
                         if v.get("user_id") == user_id and v.get("source") == "gdrive"]
        for key in keys_to_remove:
            del file_manager.hash_registry[key]
        print(f"[SYNC] Cleared {len(keys_to_remove)} old synced files")
        
        synced_files = []
        for gdrive_file in gdrive_files:
            file_key = f"{user_id}_gdrive_{gdrive_file['id']}"
            file_manager.hash_registry[file_key] = {
                "file_id": gdrive_file['id'],
                "filename": gdrive_file['name'],
                "user_id": user_id,
                "synced": True,
                "source": "gdrive",
                "mime_type": gdrive_file.get('mimeType')
            }
            synced_files.append(gdrive_file['name'])
        
        file_manager._save_registry()
        print(f"[SYNC] Synced {len(synced_files)} files: {synced_files}")
        
        return {
            "status": "success",
            "message": "Google Drive synced successfully",
            "files_synced": len(synced_files),
            "files": synced_files,
            "total_files": len(gdrive_files)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[SYNC] Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_sync_status(user: dict = Depends(get_current_user)):
    user_id = user["id"]
    return {
        "synced": False,
        "last_sync": None
    }

@router.post("/process/{file_id}")
async def process_gdrive_file(file_id: str, user: dict = Depends(get_current_user)):
    from ..services.parser import parser
    from ..services.kg_builder import kg_builder
    from ..services.rag_engine import rag_engine
    import requests as http_requests
    import io
    
    user_id = user["id"]
    access_token = user.get("access_token")
    
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token")
    
    try:
        # Get file metadata
        headers = {"Authorization": f"Bearer {access_token}"}
        meta_response = http_requests.get(
            f"https://www.googleapis.com/drive/v3/files/{file_id}",
            headers=headers,
            params={"fields": "mimeType,name"},
            timeout=10
        )
        
        if meta_response.status_code != 200:
            raise HTTPException(status_code=meta_response.status_code, detail="Failed to get file info")
        
        file_info = meta_response.json()
        mime_type = file_info.get('mimeType', '')
        
        # Export Google Workspace files
        if 'google-apps' in mime_type:
            if 'spreadsheet' in mime_type:
                export_mime = 'text/csv'
                ext = '.csv'
            elif 'document' in mime_type:
                export_mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                ext = '.docx'
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {mime_type}")
            
            response = http_requests.get(
                f"https://www.googleapis.com/drive/v3/files/{file_id}/export",
                headers=headers,
                params={"mimeType": export_mime},
                timeout=30
            )
        else:
            # Regular file download
            response = http_requests.get(
                f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media",
                headers=headers,
                timeout=30
            )
            ext = '.tmp'
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to download file")
        
        # Save temporarily
        temp_path = f"uploads/temp_{file_id}{ext}"
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        
        # Parse
        parsed_data = parser.parse_file(temp_path)
        
        # Build KG
        kg_builder.build_graph(parsed_data, file_id, user_id, "unknown")
        
        # Store embeddings
        rag_engine.store_embeddings(parsed_data, file_id, user_id)
        
        # Clean up
        import os
        os.remove(temp_path)
        
        return {"message": "File processed successfully", "file_id": file_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
