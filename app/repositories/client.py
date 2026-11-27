from sqlmodel import Session, select, exists

from app.config.database import engine
from app.models.client import Client
from app.schemas.client import ClientCreate


class ClientRepository:

    def create_client(self, client_data: ClientCreate):
        with Session(engine) as session:
            client_db = Client(
                name=client_data.name
            )
            session.add(client_db)
            session.commit()
            session.refresh(client_data)
            return client_data

    def check_api_key(self, api_key):
        with Session(engine) as session:
            return session.query(exists().where(Client.api_key == api_key))

    def get_user_from_api_key(self, api_key):
        with Session(engine) as session:
            statement = select(Client).where(Client.api_key == api_key)
            return session.exec(statement).one()
