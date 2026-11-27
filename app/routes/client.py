from fastapi import APIRouter

from app.schemas.client import ClientCreate, ClientResponse
from app.services.client import ClientService

router = APIRouter()

@router.post("/", response_model=ClientResponse)
def create(data: ClientCreate):
    service = ClientService()
    return service.create_client(data)
