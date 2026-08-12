#!/usr/bin/env python3
"""Fail-closed verifier for GP-17 migration-readiness evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


RELEASE_SHA = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_ENVIRONMENTS = {
    "fresh-vps-rehearsal",
    "provider-sandbox",
    "owner-controlled-test",
}
PROHIBITED_FIELDS = {
    "authorization",
    "cookie",
    "password",
    "secret",
    "access_token",
    "refresh_token",
    "api_key",
    "private_key",
}


def _load_object(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise ValueError("symbolic links are not accepted")
    if not path.is_file():
        raise ValueError("not a regular file")
    if os.name == "posix" and stat.S_IMODE(path.stat().st_mode) & 0o022:
        raise ValueError("evidence is group/world writable")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def _parse_time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("observed_at must be an ISO-8601 string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("observed_at must include a timezone")
    return parsed.astimezone(timezone.utc)


def _prohibited_field(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in PROHIBITED_FIELDS:
                return str(key)
            found = _prohibited_field(nested)
            if found:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = _prohibited_field(nested)
            if found:
                return found
    return None


def verify(
    requirements_path: Path,
    evidence_dir: Path,
    release_sha: str,
    *,
    now: datetime | None = None,
) -> tuple[dict[str, Any], int]:
    if not RELEASE_SHA.fullmatch(release_sha):
        raise ValueError("release SHA must be exactly 40 lowercase hexadecimal characters")
    requirements_doc = _load_object(requirements_path)
    requirements = requirements_doc.get("requirements")
    if requirements_doc.get("schema_version") != 1 or not isinstance(requirements, list):
        raise ValueError("unsupported requirements schema")

    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    seen: set[str] = set()
    results: list[dict[str, Any]] = []

    for requirement in requirements:
        if not isinstance(requirement, dict):
            raise ValueError("requirement must be an object")
        gate_id = requirement.get("id")
        if not isinstance(gate_id, str) or not re.fullmatch(r"[a-z][a-z0-9_]+", gate_id):
            raise ValueError("invalid requirement id")
        if gate_id in seen:
            raise ValueError(f"duplicate requirement id: {gate_id}")
        seen.add(gate_id)

        path = evidence_dir / f"{gate_id}.json"
        result: dict[str, Any] = {"id": gate_id, "status": "PENDING"}
        if not path.exists():
            result["reason"] = "evidence_missing"
            results.append(result)
            continue

        try:
            record = _load_object(path)
            if record.get("schema_version") != 1:
                raise ValueError("unsupported evidence schema")
            if record.get("gate_id") != gate_id:
                raise ValueError("gate_id mismatch")
            if record.get("release_sha") != release_sha:
                raise ValueError("release_sha mismatch")
            if record.get("environment") != requirement.get("evidence_environment"):
                raise ValueError("environment mismatch")
            if record.get("environment") not in ALLOWED_ENVIRONMENTS:
                raise ValueError("environment is not allowed")
            if record.get("status") != "PASS":
                raise ValueError("status is not PASS")
            if record.get("synthetic") is not False:
                raise ValueError("synthetic or unclassified evidence is not accepted")
            if not isinstance(record.get("summary"), str) or not record["summary"].strip():
                raise ValueError("non-empty summary is required")
            if _prohibited_field(record):
                raise ValueError("evidence contains a prohibited secret-bearing field")
            observed_at = _parse_time(record.get("observed_at"))
            if observed_at > now + timedelta(minutes=5):
                raise ValueError("observed_at is in the future")
            max_age = timedelta(hours=int(requirement["max_age_hours"]))
            if now - observed_at > max_age:
                raise ValueError("evidence is stale")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            result.update(status="PASS", observed_at=observed_at.isoformat(), sha256=digest)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            result.update(status="INVALID", reason=str(exc))
        results.append(result)

    pending = sum(result["status"] == "PENDING" for result in results)
    invalid = sum(result["status"] == "INVALID" for result in results)
    passed = sum(result["status"] == "PASS" for result in results)
    verdict = "MIGRATION_READY" if passed == len(results) and not invalid else "NOT_READY"
    report = {
        "schema_version": 1,
        "release_sha": release_sha,
        "generated_at": now.isoformat(),
        "verdict": verdict,
        "counts": {"pass": passed, "pending": pending, "invalid": invalid},
        "results": results,
    }
    return report, 0 if verdict == "MIGRATION_READY" else (2 if invalid else 3)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requirements", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--release-sha", required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    try:
        report, exit_code = verify(args.requirements, args.evidence_dir, args.release_sha)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"acceptance verifier configuration error: {exc}", file=sys.stderr)
        return 64

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
