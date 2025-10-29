from fastapi import APIRouter, Depends, HTTPException
from ..core.auth import get_current_user
import requests as http_requests

router = APIRouter(prefix="/process", tags=["process"])

@router.post("/all-synced")
async def process_all_synced(user: dict = Depends(get_current_user)):
    """Process all synced Google Drive files that haven't been processed yet"""
    from ..services.file_manager import file_manager
    from ..services.parser import parser
    from ..services.kg_builder import kg_builder
    from ..services.rag_engine import rag_engine
    from ..services.doc_type_detector import doc_detector
    import os
    
    user_id = user["id"]
    access_token = user.get("access_token")
    
    if not access_token:
        raise HTTPException(status_code=401, detail="No access token")
    
    # Find synced files
    synced_files = []
    for key, file_info in file_manager.hash_registry.items():
        if file_info.get("user_id") == user_id and file_info.get("source") == "gdrive":
            synced_files.append(file_info)
    
    if not synced_files:
        return {"message": "No synced files found", "processed": 0}
    
    print(f"[PROCESS] Found {len(synced_files)} synced files to process")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    processed = 0
    errors = []
    
    for file_info in synced_files:
        file_id = file_info['file_id']
        filename = file_info['filename']
        mime_type = file_info.get('mime_type', '')
        
        try:
            print(f"[PROCESS] Processing: {filename} ({file_id})")
            
            # Determine export format
            if 'spreadsheet' in mime_type:
                export_mime = 'text/csv'
                ext = '.csv'
            elif 'document' in mime_type:
                export_mime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                ext = '.docx'
            else:
                print(f"[PROCESS] Skipping unsupported type: {mime_type}")
                continue
            
            # Download
            response = http_requests.get(
                f"https://www.googleapis.com/drive/v3/files/{file_id}/export",
                headers=headers,
                params={"mimeType": export_mime},
                timeout=60
            )
            
            if response.status_code != 200:
                raise Exception(f"Download failed: {response.status_code}")
            
            # Save temporarily
            temp_path = f"uploads/temp_{file_id}{ext}"
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            
            # Parse
            parsed_data = parser.parse_file(temp_path)
            
            # Detect type
            sample_content = str(parsed_data[0].get('content', ''))[:2000] if parsed_data else ""
            doc_info = doc_detector.detect_type(sample_content)
            doc_type = doc_info.get("type", "unknown")
            
            # Build KG
            kg_result = kg_builder.build_graph(parsed_data, file_id, user_id, doc_type)
            
            # Store embeddings
            rag_engine.store_embeddings(parsed_data, file_id, user_id)
            
            # Clean up
            os.remove(temp_path)
            
            processed += 1
            print(f"[PROCESS] ✓ Processed: {filename}")
            
        except Exception as e:
            error_msg = f"{filename}: {str(e)}"
            errors.append(error_msg)
            print(f"[PROCESS] ✗ Error: {error_msg}")
    
    return {
        "message": f"Processed {processed}/{len(synced_files)} files",
        "processed": processed,
        "total": len(synced_files),
        "errors": errors
    }
