import requests
from typing import Optional, Dict, Any
from datetime import datetime

class TokenValidator:
    """Validates Google OAuth tokens before API calls"""
    
    @staticmethod
    def validate_token(access_token: str) -> Dict[str, Any]:
        """
        Validate Google OAuth token and return token info
        
        Returns:
            dict with 'valid' (bool), 'expires_in' (int), 'scope' (str)
        """
        try:
            response = requests.get(
                f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "valid": True,
                    "expires_in": int(data.get("expires_in", 0)),
                    "scope": data.get("scope", ""),
                    "has_drive_scope": "drive" in data.get("scope", "")
                }
            else:
                return {"valid": False, "error": "Token invalid or expired"}
                
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    @staticmethod
    def check_drive_permission(access_token: str) -> bool:
        """Check if token has Google Drive permissions"""
        info = TokenValidator.validate_token(access_token)
        return info.get("valid", False) and info.get("has_drive_scope", False)

token_validator = TokenValidator()
