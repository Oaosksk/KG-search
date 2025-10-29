from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class GoogleAuthRequest(BaseModel):
    token: str

class AuthResponse(BaseModel):
    access_token: str
    user: Dict[str, Any]

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    status: str

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10

class SearchResult(BaseModel):
    content: str
    score: float
    source: str
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    answer: str
    results: List[SearchResult]
    kg_entities: List[Dict[str, Any]]
    kg_data: Optional[Dict[str, Any]] = None
    citations: List[str]

class FeedbackRequest(BaseModel):
    query: str
    answer: str
    rating: int
    comment: Optional[str] = None
