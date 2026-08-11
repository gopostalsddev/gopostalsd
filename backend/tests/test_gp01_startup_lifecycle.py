"""GP-01 regression tests for side-effect-free application startup."""

from pathlib import Path
import importlib.util
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory

from server import create_server
from server import startup


def _load_gp01_migration():
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "gp01_pricing_policy_alembic.py"
    )
    spec = importlib.util.spec_from_file_location("gp01_pricing_policy", migration_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_repository_has_exactly_one_alembic_head():
    backend_dir = Path(__file__).resolve().parents[1]
    config = AlembicConfig(str(backend_dir / "migrations" / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "migrations"))

    heads = ScriptDirectory.from_config(config).get_heads()

    assert heads == ["gp01_pricing_policy"]


def test_migration_mode_skips_runtime_integrations_and_bootstrap():
    with (
        patch("server.sinalite.init_app") as sinalite_init,
        patch("server.filestorage.init_app") as storage_init,
        patch(
            "server.startup.bootstrap_required_data",
            side_effect=AssertionError("migration mode performed data bootstrap"),
        ),
        patch(
            "server.startup_admin.ensure_production_admin",
            side_effect=AssertionError("migration mode performed admin bootstrap"),
        ),
    ):
        app = create_server("testing", migration_mode=True)

    assert app.config["MIGRATION_MODE"] is True
    assert "migrate" in app.extensions
    sinalite_init.assert_not_called()
    storage_init.assert_not_called()


def test_normal_startup_does_not_run_data_or_admin_bootstrap():
    with (
        patch(
            "server.startup.bootstrap_required_data",
            side_effect=AssertionError("normal startup performed data bootstrap"),
        ) as data_bootstrap,
        patch(
            "server.startup_admin.ensure_production_admin",
            side_effect=AssertionError("normal startup performed admin bootstrap"),
        ) as admin_bootstrap,
    ):
        app = create_server("testing", migration_mode=False)

    assert app.config["MIGRATION_MODE"] is False
    data_bootstrap.assert_not_called()
    admin_bootstrap.assert_not_called()


def test_bootstrap_refuses_to_create_missing_schema(monkeypatch):
    fake_inspector = SimpleNamespace(has_table=lambda _table: False)
    monkeypatch.setattr(startup, "inspect", lambda _engine: fake_inspector)
    app = create_server("testing", migration_mode=True)

    with app.app_context():
        with pytest.raises(RuntimeError, match="Run `flask db upgrade` first"):
            startup._require_migrated_schema()


def test_bootstrap_verifies_migration_owned_unclassified_type(monkeypatch):
    fake_inspector = SimpleNamespace(has_table=lambda _table: True)
    monkeypatch.setattr(startup, "inspect", lambda _engine: fake_inspector)
    monkeypatch.setattr(startup.db.session, "get", lambda *_args: None)
    app = create_server("testing", migration_mode=True)

    with app.app_context():
        with pytest.raises(RuntimeError, match="Do not repair it at runtime"):
            startup.bootstrap_required_data()


def test_pricing_policy_migration_adopts_compatible_legacy_table(monkeypatch):
    migration = _load_gp01_migration()
    inspector = SimpleNamespace(
        has_table=lambda table: table == "pricing_policies",
        get_columns=lambda _table: [
            {"name": name} for name in sorted(migration._EXPECTED_COLUMNS)
        ],
    )
    monkeypatch.setattr(migration.op, "get_bind", lambda: object())
    monkeypatch.setattr(migration.sa, "inspect", lambda _bind: inspector)

    with patch.object(migration.op, "create_table") as create_table:
        migration.upgrade()

    create_table.assert_not_called()


def test_pricing_policy_migration_rejects_incompatible_legacy_table(monkeypatch):
    migration = _load_gp01_migration()
    inspector = SimpleNamespace(
        has_table=lambda table: table == "pricing_policies",
        get_columns=lambda _table: [{"name": "id"}],
    )
    monkeypatch.setattr(migration.op, "get_bind", lambda: object())
    monkeypatch.setattr(migration.sa, "inspect", lambda _bind: inspector)

    with pytest.raises(RuntimeError, match="incompatible"):
        migration.upgrade()


def test_legacy_order_table_utility_refuses_direct_schema_changes():
    from utility_scripts import create_order_tables

    with pytest.raises(RuntimeError, match="Direct table create/drop is prohibited"):
        create_order_tables.create_order_tables()
    with pytest.raises(RuntimeError, match="Direct table create/drop is prohibited"):
        create_order_tables.drop_order_tables()
