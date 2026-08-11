"""GP-14 static contract tests; CI also builds and boots the real image."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE = (ROOT / "backend" / "Dockerfile").read_text(encoding="utf-8")
COMPOSE = (
    ROOT / "deploy" / "gopostal" / "docker-compose.production.yml"
).read_text(encoding="utf-8")
DOCKERIGNORE = (ROOT / "backend" / ".dockerignore").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/gp14-container-contract.yml").read_text(
    encoding="utf-8"
)


def _service_block(name, next_name=None):
    start = COMPOSE.index(f"  {name}:\n")
    end = COMPOSE.index(f"  {next_name}:\n", start) if next_name else COMPOSE.index("\nvolumes:", start)
    return COMPOSE[start:end]


def test_runtime_image_is_pinned_multistage_and_non_root():
    assert DOCKERFILE.count("FROM python:3.12.10-slim-bookworm") == 2
    assert " AS wheels" in DOCKERFILE
    assert "USER 10001:10001" in DOCKERFILE
    assert DOCKERFILE.rindex("USER 10001:10001") < DOCKERFILE.rindex("CMD [")
    assert "PYTHONDONTWRITEBYTECODE=1" in DOCKERFILE


def test_image_contains_no_environment_or_test_context():
    required = {".env", "*.env", "tests/", "uploads/", "instance/", "*.log"}
    assert required.issubset(set(DOCKERIGNORE.splitlines()))
    assert "COPY . ." not in DOCKERFILE


def test_web_is_loopback_only_immutable_and_least_privilege():
    web = _service_block("web")
    assert '"127.0.0.1:${GOPOSTAL_HOST_PORT:-8500}:5000"' in web
    assert "read_only: true" in web
    assert 'user: "10001:10001"' in web
    assert "cap_drop:\n      - ALL" in web
    assert "no-new-privileges:true" in web
    assert "pids_limit: 256" in web
    assert "mem_limit: 768m" in web
    assert "cpus: 1.0" in web
    assert "--workers" not in COMPOSE  # command is immutable in the image


def test_database_is_private_persistent_and_health_gated():
    database = _service_block("db", "web")
    assert "postgres:17.6-bookworm" in database
    assert "ports:" not in database
    assert "gopostal_production_postgres:/var/lib/postgresql/data" in database
    assert "pg_isready" in database
    assert "gopostal_data" in database
    assert "condition: service_healthy" in _service_block("web")
    assert "internal: true" in COMPOSE


def test_app_and_database_receive_separate_root_owned_env_files():
    assert "/etc/gopostal/production.env" in _service_block("web")
    assert "/etc/gopostal/database.env" in _service_block("db", "web")
    assert "password" not in COMPOSE.lower()


def test_health_and_logging_contracts_match_gp12():
    assert COMPOSE.count("/health/ready") == 1
    assert "/health/ready" in DOCKERFILE
    assert 'max-size: "10m"' in COMPOSE
    assert 'max-file: "5"' in COMPOSE


def test_no_upload_volume_or_cross_application_resource_name():
    assert not re.search(r"uploads?.*:/", COMPOSE, flags=re.I)
    assert "rezza" not in COMPOSE.lower()


def test_privileged_compose_steps_preserve_only_the_required_image_tag():
    command = 'sudo env GOPOSTAL_IMAGE_TAG="$GOPOSTAL_IMAGE_TAG"'
    assert WORKFLOW.count(command) == 2
    assert "sudo docker compose" not in WORKFLOW
