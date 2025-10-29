import hashlib
from pathlib import Path
from fastapi import UploadFile, HTTPException
from typing import Dict, Any, Optional
import json

ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.docx', '.pdf', '.json', '.txt'}
MAX_FILE_SIZE = 50 * 1024 * 1024

class FileManager:
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        self.hash_registry_file = self.upload_dir / "file_registry.json"
        self.hash_registry = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        if self.hash_registry_file.exists():
            with open(self.hash_registry_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_registry(self):
        with open(self.hash_registry_file, 'w') as f:
            json.dump(self.hash_registry, f, indent=2)
    
    def validate_file(self, file: UploadFile) -> Dict[str, Any]:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"File type {ext} not allowed")
        return {"valid": True, "extension": ext}
    
    def get_file_hash(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()
    
    def check_duplicate(self, file_hash: str, user_id: str) -> Optional[Dict[str, Any]]:
        key = f"{user_id}_{file_hash}"
        if key in self.hash_registry:
            return self.hash_registry[key]
        return None
    
    async def save_file(self, file: UploadFile, user_id: str) -> Dict[str, Any]:
        self.validate_file(file)
        content = await file.read()
        
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(400, "File too large")
        
        file_hash = self.get_file_hash(content)
        
        # Check for duplicate
        existing = self.check_duplicate(file_hash, user_id)
        if existing:
            raise HTTPException(409, f"File already uploaded: {existing['filename']}")
        
        file_path = self.upload_dir / f"{user_id}_{file_hash}{Path(file.filename).suffix}"
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        file_info = {
            "file_id": file_hash,
            "filename": file.filename,
            "path": str(file_path),
            "size": len(content),
            "hash": file_hash,
            "user_id": user_id
        }
        
        # Register file
        self.hash_registry[f"{user_id}_{file_hash}"] = file_info
        self._save_registry()
        
        return file_info

file_manager = FileManager()
