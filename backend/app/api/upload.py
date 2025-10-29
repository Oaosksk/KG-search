from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from ..models.schemas import FileUploadResponse
from ..core.auth import get_current_user
from ..services.file_manager import file_manager
from ..services.parser import parser
from ..services.kg_builder import kg_builder
from ..services.rag_engine import rag_engine
from ..services.doc_type_detector import doc_detector

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/file", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    user_id = user["id"]
    
    try:
        # Save file with deduplication check
        file_info = await file_manager.save_file(file, user_id)
    except HTTPException as e:
        if e.status_code == 409:
            return FileUploadResponse(
                file_id="duplicate",
                filename=file.filename,
                status="already_exists"
            )
        raise
    
    # Parse file
    parsed_data = parser.parse_file(file_info["path"])
    
    # Detect document type
    sample_content = str(parsed_data[0].get('content', ''))[:2000] if parsed_data else ""
    doc_info = doc_detector.detect_type(sample_content)
    doc_type = doc_info.get("type", "unknown")
    
    # Build KG with document type awareness
    kg_result = kg_builder.build_graph(parsed_data, file_info["file_id"], user_id, doc_type)
    
    # Store embeddings
    rag_engine.store_embeddings(parsed_data, file_info["file_id"], user_id)
    
    return FileUploadResponse(
        file_id=file_info["file_id"],
        filename=file_info["filename"],
        status=f"processed_{doc_type}"
    )

@router.post("/google-drive")
async def upload_from_drive(file_id: str, user: dict = Depends(get_current_user)):
    return {"message": "Google Drive integration", "file_id": file_id}
