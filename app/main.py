from fastapi import FastAPI
from app.routes.bucket import router as bucket_router

app = FastAPI()

app.include_router(bucket_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
