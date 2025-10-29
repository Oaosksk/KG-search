from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, upload, search, sync, files, delete
from app.core.config import settings

app = FastAPI(title="KG-Search API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(search.router)
app.include_router(sync.router)
app.include_router(files.router)
app.include_router(delete.router, prefix="/delete", tags=["delete"])

@app.get("/")
async def root():
    return {"message": "KG-Search API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
