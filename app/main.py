from fastapi import Depends, FastAPI

from app.config.database import create_db_and_tables
from app.routes import bucket, client
from app.security.auth import get_user

app = FastAPI()

app.include_router(
    bucket.router,
    prefix="/api/buckets",
    dependencies=[Depends(get_user)],
)

app.include_router(
    client.router,
    prefix="/api/clients",
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Hello World"}
