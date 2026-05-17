from flask import Flask
from server.services.file_storage_service import LocalFileStorage, RemoteFileStorage

class FileStorage:
    def __init__(self):
        self.backend = None

    def init_app(self, app: Flask):
        environment = app.config.get("ENVIRONMENT", "development")

        if environment in ["development", "testing"]:
            self.backend = LocalFileStorage()
        else:
            self.backend = RemoteFileStorage()

        self.backend.init_app(app)

        # Add to Flask extensions
        app.extensions["filestorage"] = self

    def upload_file(self, *args, **kwargs):
        return self.backend.upload_file(*args, **kwargs)

    def delete_file(self, *args, **kwargs):
        return self.backend.delete_file(*args, **kwargs)
    
    @property
    def current_backend(self):
        return type(self.backend).__name__