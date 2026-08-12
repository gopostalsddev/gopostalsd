"""GP-17 evidence verifier tests; no live success is simulated or recorded."""

import importlib.util
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = ROOT / "deploy/gopostal/acceptance/requirements.json"
VERIFIER = ROOT / "deploy/gopostal/verify-acceptance-evidence.py"
SPEC = importlib.util.spec_from_file_location("gp17_acceptance", VERIFIER)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)
RELEASE_SHA = "a" * 40
NOW = datetime(2026, 8, 11, 12, 0, tzinfo=timezone.utc)


def _requirement(gate_id):
    document = json.loads(REQUIREMENTS.read_text(encoding="utf-8"))
    return next(item for item in document["requirements"] if item["id"] == gate_id)


def _record(directory, gate_id, **updates):
    requirement = _requirement(gate_id)
    record = {
        "schema_version": 1,
        "gate_id": gate_id,
        "release_sha": RELEASE_SHA,
        "environment": requirement["evidence_environment"],
        "status": "PASS",
        "synthetic": False,
        "observed_at": NOW.isoformat(),
        "summary": "Controlled acceptance observation completed.",
    }
    record.update(updates)
    (directory / f"{gate_id}.json").write_text(json.dumps(record), encoding="utf-8")


def test_missing_live_evidence_is_pending_and_never_migration_ready(tmp_path):
    report, exit_code = MODULE.verify(REQUIREMENTS, tmp_path, RELEASE_SHA, now=NOW)
    assert exit_code == 3
    assert report["verdict"] == "NOT_READY"
    assert report["counts"]["pass"] == 0
    assert report["counts"]["pending"] == len(report["results"])


def test_synthetic_wrong_release_and_stale_evidence_are_invalid(tmp_path):
    _record(tmp_path, "mailersend_delivery", synthetic=True)
    _record(tmp_path, "square_payment_journey", release_sha="b" * 40)
    _record(
        tmp_path,
        "storage_round_trip",
        observed_at=(NOW - timedelta(hours=25)).isoformat(),
    )
    report, exit_code = MODULE.verify(REQUIREMENTS, tmp_path, RELEASE_SHA, now=NOW)
    assert exit_code == 2
    results = {item["id"]: item for item in report["results"]}
    assert results["mailersend_delivery"]["status"] == "INVALID"
    assert results["square_payment_journey"]["status"] == "INVALID"
    assert results["storage_round_trip"]["status"] == "INVALID"


def test_secret_bearing_fields_are_rejected_without_printing_values(tmp_path):
    _record(tmp_path, "mailersend_delivery", api_key="must-never-appear")
    report, exit_code = MODULE.verify(REQUIREMENTS, tmp_path, RELEASE_SHA, now=NOW)
    rendered = json.dumps(report)
    assert exit_code == 2
    assert "must-never-appear" not in rendered
    assert "prohibited" in rendered


def test_complete_current_real_classified_evidence_can_pass(tmp_path):
    requirements = json.loads(REQUIREMENTS.read_text(encoding="utf-8"))["requirements"]
    for requirement in requirements:
        _record(tmp_path, requirement["id"])
    report, exit_code = MODULE.verify(REQUIREMENTS, tmp_path, RELEASE_SHA, now=NOW)
    assert exit_code == 0
    assert report["verdict"] == "MIGRATION_READY"
    assert report["counts"] == {"pass": len(requirements), "pending": 0, "invalid": 0}


def test_requirements_are_unique_and_do_not_claim_historical_recovery():
    document = json.loads(REQUIREMENTS.read_text(encoding="utf-8"))
    ids = [item["id"] for item in document["requirements"]]
    assert len(ids) == len(set(ids))
    combined = json.dumps(document).lower()
    assert "historical production" not in combined
    assert "render postgresql" not in combined
