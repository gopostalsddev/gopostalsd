"""GP-13 tests for request limits and the production storage boundary."""

from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch

from flask import Flask, jsonify
import pytest

from server.controllers.print_product_controller import _validate_image_upload
from server.request_limits import configure_request_limits
from server.services import FileStorage
from server.storage_config import (
    StorageConfigurationError,
    validate_production_storage_settings,
)
from server.thirdparty.supabase import SupabaseAdapter
from werkzeug.datastructures import FileStorage as WerkzeugFileStorage


PRODUCTION_STORAGE = {
    "FILE_STORAGE_BACKEND": "supabase",
    "SUPABASE_URL": "https://project.example.test",
    "SUPABASE_SERVICE_KEY": "mock-service-role-key",
    "SUPABASE_BUCKET": "gopostalsd-uploads",
}


def _limited_app(environment=None):
    app = Flask(__name__)
    called = {"value": False}
    with patch.dict("os.environ", environment or {}, clear=True):
        configure_request_limits(app)

    @app.post("/upload")
    def upload():
        called["value"] = True
        return jsonify({"ok": True})

    return app, called


def test_oversized_json_is_rejected_before_route_service_work():
    app, called = _limited_app(
        {"MAX_REQUEST_BYTES": "2048", "MAX_JSON_REQUEST_BYTES": "1024"}
    )
    response = app.test_client().post(
        "/upload", data=b'"' + (b"x" * 1100) + b'"', content_type="application/json"
    )
    assert response.status_code == 413
    assert response.get_json()["error"]["code"] == "REQUEST_TOO_LARGE"
    assert called["value"] is False


def test_global_multipart_limit_rejects_body_before_route_service_work():
    app, called = _limited_app(
        {"MAX_REQUEST_BYTES": "1024", "MAX_JSON_REQUEST_BYTES": "512"}
    )
    response = app.test_client().post(
        "/upload",
        data={"image": (BytesIO(b"x" * 1500), "large.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 413
    assert response.get_json()["error"]["code"] == "REQUEST_TOO_LARGE"
    assert called["value"] is False


@pytest.mark.parametrize(
    "environment",
    (
        {},
        {"FILE_STORAGE_BACKEND": "local"},
        {"FILE_STORAGE_BACKEND": "filesystem"},
    ),
)
def test_production_never_silently_uses_local_storage(environment):
    with patch.dict("os.environ", environment, clear=True):
        with pytest.raises(StorageConfigurationError):
            validate_production_storage_settings()


def test_production_requires_service_role_storage_credentials():
    environment = dict(PRODUCTION_STORAGE)
    environment.pop("SUPABASE_SERVICE_KEY")
    with patch.dict("os.environ", environment, clear=True):
        with pytest.raises(StorageConfigurationError, match="SUPABASE_SERVICE_KEY"):
            validate_production_storage_settings()


def test_production_file_storage_selects_remote_backend_only():
    app = Flask(__name__)
    app.config["ENVIRONMENT"] = "production"
    remote = Mock()
    with (
        patch.dict("os.environ", PRODUCTION_STORAGE, clear=True),
        patch("server.services.RemoteFileStorage", return_value=remote),
        patch("server.services.LocalFileStorage") as local_type,
    ):
        storage = FileStorage()
        storage.init_app(app)
    remote.init_app.assert_called_once_with(app)
    local_type.assert_not_called()


def test_gif_and_extension_magic_mismatch_are_rejected():
    gif = WerkzeugFileStorage(stream=BytesIO(b"GIF89a"), filename="image.gif")
    mismatch = WerkzeugFileStorage(stream=BytesIO(b"not-a-png"), filename="image.png")
    assert "not allowed" in _validate_image_upload(gif)
    assert "does not match" in _validate_image_upload(mismatch)


def test_supabase_provider_failure_does_not_log_secret_response(caplog):
    secret = "provider-response-containing-secret"
    adapter = SupabaseAdapter()
    adapter.bucket = "test-bucket"
    adapter.client = Mock()
    adapter.client.storage.from_.return_value.upload.side_effect = RuntimeError(secret)
    with caplog.at_level("ERROR"):
        with pytest.raises(RuntimeError, match=secret):
            adapter.upload_file(b"data", "safe.png", "image/png")
    assert secret not in caplog.text


def test_storefront_discloses_that_artwork_is_not_transferred():
    source = (
        Path(__file__).resolve().parents[2]
        / "frontend"
        / "src"
        / "pages"
        / "Shop"
        / "components"
        / "ProductDetailPage.jsx"
    ).read_text(encoding="utf-8")
    assert "It is not uploaded or attached to your order" in source
