from fastapi import APIRouter, HTTPException
from ..models.schemas import GoogleAuthRequest, AuthResponse
from ..core.auth import verify_google_token, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest):
    user_info = verify_google_token(request.token)
    
    user_data = {
        "id": user_info["sub"],
        "email": user_info["email"],
        "name": user_info.get("name", ""),
        "picture": user_info.get("picture", ""),
        "access_token": request.token
    }
    
    access_token = create_access_token(user_data)
    
    return AuthResponse(
        access_token=access_token,
        user=user_data
    )
