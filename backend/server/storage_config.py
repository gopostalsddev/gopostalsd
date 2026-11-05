"""Explicit file-storage boundary for production uploads."""

import os


class StorageConfigurationError(ValueError):
    """Raised when file storage is unsafe or incomplete."""


_REMOTE_BACKENDS = {"supabase", "r2"}


def storage_backend(*, required: bool) -> str:
    backend = os.getenv("FILE_STORAGE_BACKEND", "").strip().lower()
    if not backend:
        if required:
            raise StorageConfigurationError(
                "FILE_STORAGE_BACKEND must be explicitly set in production"
            )
        return "local"
    if backend not in {"local"} | _REMOTE_BACKENDS:
        raise StorageConfigurationError(
            "FILE_STORAGE_BACKEND must be one of: local, supabase, r2"
        )
    if required and backend not in _REMOTE_BACKENDS:
        raise StorageConfigurationError(
            "Production file storage must use a remote backend (supabase or r2); local storage is ephemeral"
        )
    return backend


def validate_production_storage_settings() -> None:
    backend = storage_backend(required=True)
    if backend == "r2":
        missing = [
            key
            for key in ("R2_ENDPOINT_URL", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET", "R2_PUBLIC_URL")
            if not os.getenv(key, "").strip()
        ]
    else:
        missing = [
            key
            for key in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_BUCKET")
            if not os.getenv(key, "").strip()
        ]
    if missing:
        raise StorageConfigurationError(
            f"Missing required {backend} storage configuration: " + ", ".join(missing)
        )
