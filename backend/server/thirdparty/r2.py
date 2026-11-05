import os
import time
import boto3
from botocore.config import Config
from flask import Flask


class R2Adapter:
    def __init__(self):
        self.client = None
        self.bucket = None
        self.public_url = None

    def init_app(self, app: Flask):
        self.bucket = app.config["R2_BUCKET"]
        self.public_url = app.config["R2_PUBLIC_URL"].rstrip("/")
        self.client = boto3.client(
            "s3",
            endpoint_url=app.config["R2_ENDPOINT_URL"],
            aws_access_key_id=app.config["R2_ACCESS_KEY_ID"],
            aws_secret_access_key=app.config["R2_SECRET_ACCESS_KEY"],
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )

    def upload_file(self, file_data: bytes, file_name: str, content_type: str) -> str:
        import logging
        logger = logging.getLogger(__name__)
        unique_name = f"{int(time.time())}_{file_name}"
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=unique_name,
                Body=file_data,
                ContentType=content_type,
            )
            logger.info("R2 upload completed: %s", unique_name)
        except Exception:
            logger.error("R2 upload failed: %s", unique_name)
            raise
        return f"{self.public_url}/{unique_name}"

    def delete_file(self, file_path: str) -> bool:
        import logging
        logger = logging.getLogger(__name__)
        key = file_path.split("/")[-1]
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            logger.error("R2 delete failed: %s", key)
            return False
