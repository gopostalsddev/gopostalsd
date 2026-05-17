import os
from abc import ABC, abstractmethod
from flask import Flask, request
from werkzeug.utils import secure_filename
from server.thirdparty.supabase import SupabaseAdapter

class BaseFileStorage(ABC):
    @abstractmethod
    def upload_file(self, file_data: bytes, file_name: str, content_type: str) -> str:
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        pass

class LocalFileStorage(BaseFileStorage):
    def __init__(self):
        self.upload_dir = None

    def init_app(self, app: Flask):
        self.upload_dir = os.path.join(app.root_path, 'uploads')
        os.makedirs(self.upload_dir, exist_ok=True)

    def upload_file(self, file_data: bytes, file_name: str, content_type: str) -> str:
        file_name = secure_filename(file_name)
        file_path = os.path.join(self.upload_dir, file_name)

        # Make sure upload directory exists
        os.makedirs(self.upload_dir, exist_ok=True)

        # Save the file
        with open(file_path, "wb") as f:
            f.write(file_data)

        # Build full URL
        relative_path = f"/uploads/{file_name}"
        full_url = request.host_url.rstrip('/') + relative_path
        return full_url
    
    def delete_file(self, file_path: str) -> bool:
        local_path = os.path.join(self.upload_dir, os.path.basename(file_path))
        if os.path.exists(local_path):
            os.remove(local_path)
            return True
        return True
    
class RemoteFileStorage(BaseFileStorage):
    def __init__(self):
        self.remote = SupabaseAdapter()

    def init_app(self, app: Flask):
        self.remote.init_app(app)

    def upload_file(self, file_data: bytes, file_name: str, content_type: str) -> str:
        return self.remote.upload_file(file_data=file_data, file_name=file_name, content_type=content_type)

    def delete_file(self, file_path: str) -> str:
        return self.remote.delete_file(file_path)
