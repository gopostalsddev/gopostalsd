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
        self.client = create_client(app.config["SUPABASE_URL"], app.config["SUPABASE_API_KEY"])

    def upload_file(self, file_data: bytes, filename: str, content_type: str) -> str:
        unique_name = f"{int(time.time())}_{filename}"
        self.client.storage.from_(self.bucket).upload(unique_name, file_data, {"content-type": content_type})
        public_url = self.client.storage.from_(self.bucket).get_public_url(unique_name)
        return public_url

    def delete_file(self, file_path: str) -> bool:
        key = file_path.split("/")[-1]
        res = self.client.storage.from_(self.bucket).remove([key])
        return len(res) == 0  # Empty list on success