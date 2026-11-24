import os

import boto3
from botocore.client import Config
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks

from app.config.settings import settings
from app.services.s3_service import S3Service

router = APIRouter()

s3 = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint_url,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_key,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)

BUCKET_NAME = settings.bucket_name


@router.post("/upload/")
async def upload_file(file: UploadFile):
    if file is None:
        file = File(...)

    try:
        service = S3Service()
        content = await file.read()
        service.upload(file.filename, content)
        return {"filename": file.filename, "message": "Uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/")
def list_files():
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        files = [obj for obj in response.get("Contents", [])]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download", response_class=FileResponse)
def download_file(
    background_tasks: BackgroundTasks,
    filename: str = Query(..., examples=["2024/12/27/123.txt"]),
):
    def remove_file(path: str) -> None:
        os.unlink(path)

    try:
        service = S3Service()
        obj = service.download(filename)
        background_tasks.add_task(remove_file, obj)
        return obj
    except s3.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{filename}")
def delete_file(filename: str):
    try:
        service = S3Service()
        service.remove_digital_object(filename)
        return {"filename": filename, "message": "Deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
