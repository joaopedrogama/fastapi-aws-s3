from pydantic import BaseModel


class ClientCreate(BaseModel):
    name: str


class ClientResponse(BaseModel):
    name: str
    api_key: str
