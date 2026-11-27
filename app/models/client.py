import uuid

from sqlmodel import Field, SQLModel


class Client(SQLModel, table=True):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
    )
    name: str
    api_key: str = Field(
        default_factory=uuid.uuid4,
        nullable=False,
        unique=True,
    )


