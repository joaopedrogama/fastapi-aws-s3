import boto3
import os
import uuid
import tempfile
from datetime import datetime
from datetime import timedelta

from pydantic import BaseModel
from urllib3 import ProxyManager
from botocore.client import Config

from app.exceptions.s3 import S3ObjectDoesntExistException
from app.config.settings import settings


class S3Service:
    """
    Class that prvides a facade for application to access the underlying S3 storage.
    """

    tmp_path: str
    s3_client: None = None

    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            config=Config(
                signature_version="s3v4",
            ),
            region_name="us-east-1"
        )
        self.tmp_path: str = "./tmp"
        self.bucket_name = settings.bucket_name

    def __generate_upload_path(self) -> str:
        """
        Generate a directory path based on the current date.

        Returns:
        - str: A string representing the directory path in the format "YYYY/MM/DD".
        """
        current_yyyy_mm_dd: str = datetime.now().strftime("%Y/%m/%d")
        path: str = current_yyyy_mm_dd + "/"
        return path

    def __generate_upload_path_with_file_name(self, file_name) -> str:
        """
        Generate a unique S3 object path with a file name.

        Combines the current date directory path with a UUID as the file name.

        Returns:
        - str: A string representing the full S3 object path in the format "YYYY/MM/DD/<UUID>".
        """
        s3_object_file_name: str = file_name
        s3_object_path = f"{self.__generate_upload_path()}{s3_object_file_name}"
        return s3_object_path

    def __validate_object_existance(self, s3_object_path: str) -> None:
        """
        Validate the existence of an object in the S3 bucket.

        Checks if the object with the given path exists in the configured S3 bucket.
        If the object does not exist, raises an `S3ObjectDoesntExistException`.

        Parameters:
        - s3_object_path (str): The path of the object in the S3 bucket to validate.

        Raises:
        - S3ObjectDoesntExistException: If the object does not exist in the S3 bucket.
        - S3Error: For other S3-related errors.
        """
        try:
            self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_object_path,
            )
        except Exception as e:
            raise S3ObjectDoesntExistException(
                f"The S3 object with path='{s3_object_path}' does not exist in the bucket {self.bucket_name}."
            ) from e
            raise

    def remove_digital_object(self, s3_object_path: str) -> None:
        """
        Removes a digital object from the S3 bucket.

        Parameters:
        - s3_object_path (str): The path of the digital object to be removed in the S3 bucket.

        Raises:
        - FileNotFoundError: If the specified object does not exist in the bucket.
        - S3Error: If there is an issue with the S3-compatible storage service.
        """
        self.__validate_object_existance(s3_object_path)
        self.s3_client.delete_object(
            self.bucket_name, s3_object_path
        )

    def upload(self, file_name: str, content) -> str:
        """
        Upload file to S3 storage.

        Parameters:
        - file_name (str): relative path to file to upload
        """
        s3_object_path: str = self.__generate_upload_path_with_file_name(file_name)
        self.s3_client.put_object(
            Bucket=self.bucket_name, Key=s3_object_path, Body=content
        )
        return s3_object_path

    def download(self, s3_object_path: str, local_file_name: str | None = None) -> str:
        """
        Download a file from S3 storage to the tmp directory.

        Parameters:
        - object_name (str): The path of the object in the S3 store (including file name).
        - local_file_name (str, optional): Name of the local file to save. Defaults to the
          object's name.

        Returns:
        - str: The path to the downloaded file in the local tmp directory.
        """
        self.__validate_object_existance(s3_object_path=s3_object_path)
        file_name_to_create: str = (
            local_file_name if local_file_name else os.path.basename(s3_object_path)
        )
        local_file_path: str = os.path.join(self.tmp_path, file_name_to_create)
        try:
            self.s3_client.download_file(
                    self.bucket_name,
                    s3_object_path,
                    file_name_to_create,
                )
            return file_name_to_create
        except Exception as e:
            raise RuntimeError(
                f"Failed to download file '{s3_object_path}': {str(e)}"
            ) from e

    def generate_download_url(
        self,
        s3_object_path: str,
        desired_filename: str | None = None,
        expiration_minutes: int = 360,
    ) -> str:
        """
        Generate a pre-signed URL for downloading an object from S3 with a specific filename.

        Parameters:
        - s3_object_path (str): The path of the object in the S3 bucket.
        - desired_filename (str | None, optional): The filename the user should see when
            downloading the file.
        - expiration_minutes (int): The validity duration of the pre-signed URL in minutes.

        Returns:
        - (str): A pre-signed URL to download the object.
        """
        self.__validate_object_existance(s3_object_path=s3_object_path)
        file_name: str = (
            desired_filename if desired_filename else os.path.basename(s3_object_path)
        )
        try:
            presigned_url: str = self.s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_object_path},
                ExpiresIn=60,
            )
            return presigned_url
        except Exception as e:
            raise RuntimeError(f"Failed to generate download link: {str(e)}") from e

    def generate_presigned_upload_url(
        self, s3_object_path: str | None = None, expiration_minutes: int = 360
    ) -> tuple[str, str]:
        """
        Generate a pre-signed URL for uploading files directly from the frontend.

        Parameters:
        - s3_object_path (str, optional): The path of the object in S3 (including file name).
        - expiration_minutes (int): The number of minutes the pre-signed URL is valid for.

        Returns:
        - (tuple(str, str)): The pre-signed URL for file upload and s3_object_path
        """
        if s3_object_path is None:
            s3_object_path = self.__generate_upload_path_with_file_name()
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                bucket_name=self.bucket_name,
                object_name=s3_object_path,
                expires=timedelta(minutes=expiration_minutes),
            )
            return presigned_url, s3_object_path
        except Exception as e:
            raise RuntimeError(f"Failed to generate pre-signed URL: {str(e)}") from e
