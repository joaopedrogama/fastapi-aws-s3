import os

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks

from app.services.s3_service import S3Service

router = APIRouter()


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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
def delete_file(filename: str = Query(..., examples=["2024/12/27/123.txt"])):
    try:
        service = S3Service()
        service.remove_digital_object(filename)
        return {"filename": filename, "message": "Deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
