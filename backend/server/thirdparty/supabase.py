import os
from flask import Flask
from supabase import create_client
import time

class SupabaseAdapter:
    def __init__(self):
        self.client = None
        self.bucket = None

    def init_app(self, app: Flask):
        self.bucket = app.config["SUPABASE_BUCKET"]
        # Use service role key for backend storage operations (bypasses RLS)
        key = app.config.get("SUPABASE_SERVICE_KEY") or app.config["SUPABASE_API_KEY"]
        self.client = create_client(app.config["SUPABASE_URL"], key)

    def upload_file(self, file_data: bytes, file_name: str, content_type: str) -> str:
        import logging
        logger = logging.getLogger(__name__)
        unique_name = f"{int(time.time())}_{file_name}"
        try:
            response = self.client.storage.from_(self.bucket).upload(unique_name, file_data, {"content-type": content_type})
            logger.info("Supabase upload response: %s", response)
        except Exception as upload_err:
            logger.error("Supabase upload error (bucket=%s, file=%s): %s | %r", self.bucket, unique_name, upload_err, upload_err)
            raise
        public_url = self.client.storage.from_(self.bucket).get_public_url(unique_name)
        return public_url

    def delete_file(self, file_path: str) -> bool:
        key = file_path.split("/")[-1]
        res = self.client.storage.from_(self.bucket).remove([key])
        return len(res) == 0  # Empty list on success