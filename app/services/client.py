from app.repositories.client import ClientRepository
from app.schemas.client import ClientCreate


class ClientService:

    def __init__(self):
        self.repository = ClientRepository()

    def create_client(self, data: ClientCreate):
        return self.repository.create_client(data)
