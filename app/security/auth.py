from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.repositories.client import ClientRepository

api_key_header = APIKeyHeader(name="X-API-Key")

def get_user(api_key_header: str = Security(api_key_header)):
    repository = ClientRepository()

    if repository.check_api_key(api_key_header):
        return repository.get_user_from_api_key(api_key_header)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid API key"
    )
