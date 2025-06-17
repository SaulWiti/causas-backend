from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from .config import config

api_key_security = APIKeyHeader(name="api-key-auth")

def validate_api_key(api_key: str = Security(api_key_security)):
    if api_key != config.api_key_auth:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return "OK"