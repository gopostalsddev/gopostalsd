"""Explicit file-storage boundary for production uploads."""

import os


class StorageConfigurationError(ValueError):
    """Raised when file storage is unsafe or incomplete."""


def storage_backend(*, required: bool) -> str:
    backend = os.getenv("FILE_STORAGE_BACKEND", "").strip().lower()
    if not backend:
        if required:
            raise StorageConfigurationError(
                "FILE_STORAGE_BACKEND must be explicitly set in production"
            )
        return "local"
    if backend not in {"local", "supabase"}:
        raise StorageConfigurationError(
            "FILE_STORAGE_BACKEND must be one of: local, supabase"
        )
    if required and backend != "supabase":
        raise StorageConfigurationError(
            "Production file storage must use supabase; local storage is ephemeral"
        )
    return backend


def validate_production_storage_settings() -> None:
    storage_backend(required=True)
    missing = [
        key
        for key in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_BUCKET")
        if not os.getenv(key, "").strip()
    ]
    if missing:
        raise StorageConfigurationError(
            "Missing required Supabase storage configuration: " + ", ".join(missing)
        )
