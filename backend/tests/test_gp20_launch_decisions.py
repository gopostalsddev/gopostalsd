"""GP-20 owner-decision ledger contract."""

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DECISIONS = ROOT / "deploy/gopostal/launch-decisions.json"
VERIFIER = ROOT / "deploy/gopostal/verify-launch-decisions.py"
SPEC = importlib.util.spec_from_file_location("gp20_decisions", VERIFIER)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _document():
    return json.loads(DECISIONS.read_text(encoding="utf-8"))


def test_approved_owner_decisions_are_recorded_exactly():
    decisions = {item["id"]: item for item in _document()["decisions"]}
    assert decisions["database_launch_path"]["value"] == "fresh_postgresql"
    assert decisions["historical_data_recovery"]["status"] == "NOT_APPLICABLE"
    assert decisions["email_provider"]["value"] == "mailersend"
    assert decisions["default_sender"]["value"] == "support@gopostalsd.com"


def test_canonical_url_and_live_provider_decisions_remain_pending():
    decisions = {item["id"]: item for item in _document()["decisions"]}
    for decision_id in (
        "canonical_url",
        "dns_change_authority",
        "mailersend_domain_verification",
        "square_production_configuration",
        "object_storage_production_configuration",
        "offsite_backup_provider",
        "backup_retention_rpo_rto",
        "alert_recipient",
        "rollback_authority",
        "initial_admin_identity",
    ):
        assert decisions[decision_id]["status"] == "PENDING"
        assert decisions[decision_id]["value"] is None


def test_current_ledger_fails_closed_with_only_ids_in_report():
    report, exit_code = MODULE.verify(DECISIONS)
    assert exit_code == 3
    assert report["verdict"] == "OPEN"
    assert "canonical_url" in report["pending"]
    rendered = json.dumps(report)
    assert "support@gopostalsd.com" not in rendered


def test_ledger_contains_no_credential_fields_or_canonical_url_guess():
    raw = DECISIONS.read_text(encoding="utf-8")
    lowered = raw.lower()
    for field in ('"secret"', '"password"', '"token"', '"api_key"'):
        assert field not in lowered
    assert "https://gopostalsd.com" not in lowered


def test_duplicate_or_value_bearing_pending_decisions_are_rejected(tmp_path):
    document = _document()
    document["decisions"].append(dict(document["decisions"][0]))
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text(json.dumps(document), encoding="utf-8")
    try:
        MODULE.verify(duplicate)
    except ValueError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("duplicate decision was accepted")

    document = _document()
    canonical = next(item for item in document["decisions"] if item["id"] == "canonical_url")
    canonical["value"] = "https://guessed.invalid"
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps(document), encoding="utf-8")
    try:
        MODULE.verify(invalid)
    except ValueError as exc:
        assert "must have a null value" in str(exc)
    else:
        raise AssertionError("value-bearing pending decision was accepted")
