from flask import Flask
from server.services.file_storage_service import LocalFileStorage, RemoteFileStorage

_ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
_MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB

# Minimal magic-byte signatures for the allowed image formats.
_IMAGE_SIGNATURES = [
    b'\xff\xd8\xff',           # JPEG
    b'\x89PNG\r\n\x1a\n',     # PNG
    b'RIFF',                   # WebP (followed by 4-byte size then b'WEBP')
]


def _validate_image_upload(file_data: bytes, content_type: str) -> str | None:
    """Return an error message if the upload is invalid, else None."""
    if content_type not in _ALLOWED_IMAGE_TYPES:
        return f"File type '{content_type}' is not allowed. Accepted types: JPEG, PNG, WebP."
    if len(file_data) > _MAX_UPLOAD_BYTES:
        return f"File size {len(file_data) // 1024} KB exceeds the 5 MB limit."
    # Basic magic-byte check so clients can't bypass by lying about content_type.
    if not any(file_data.startswith(sig) for sig in _IMAGE_SIGNATURES):
        return "File content does not match a recognised image format."
    return None


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

    def upload_file(self, file_data: bytes, file_name: str, content_type: str) -> str:
        error = _validate_image_upload(file_data, content_type)
        if error:
            raise ValueError(error)
        return self.backend.upload_file(file_data, file_name, content_type)

    def delete_file(self, *args, **kwargs):
        return self.backend.delete_file(*args, **kwargs)
    
    @property
    def current_backend(self):
        return type(self.backend).__name__