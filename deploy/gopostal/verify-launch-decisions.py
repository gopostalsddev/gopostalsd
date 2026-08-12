#!/usr/bin/env python3
"""Validate the non-secret GP-20 owner decision ledger."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ALLOWED_STATUS = {"APPROVED", "NOT_APPLICABLE", "PENDING"}
SECRET_FIELDS = {
    "secret",
    "password",
    "token",
    "api_key",
    "private_key",
    "authorization",
    "cookie",
}


def _secret_field(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in SECRET_FIELDS:
                return str(key)
            found = _secret_field(nested)
            if found:
                return found
    elif isinstance(value, list):
        for nested in value:
            found = _secret_field(nested)
            if found:
                return found
    return None


def verify(path: Path) -> tuple[dict[str, Any], int]:
    document = json.loads(path.read_text(encoding="utf-8"))
    decisions = document.get("decisions")
    if document.get("schema_version") != 1 or not isinstance(decisions, list):
        raise ValueError("unsupported decision schema")
    if _secret_field(document):
        raise ValueError("decision ledger contains a prohibited secret-bearing field")

    seen: set[str] = set()
    results: list[dict[str, str]] = []
    for decision in decisions:
        if not isinstance(decision, dict):
            raise ValueError("decision must be an object")
        decision_id = decision.get("id")
        status = decision.get("status")
        if not isinstance(decision_id, str) or not re.fullmatch(
            r"[a-z][a-z0-9_]+", decision_id
        ):
            raise ValueError("invalid decision id")
        if decision_id in seen:
            raise ValueError(f"duplicate decision id: {decision_id}")
        seen.add(decision_id)
        if status not in ALLOWED_STATUS:
            raise ValueError(f"invalid status for {decision_id}")
        value = decision.get("value")
        if status == "PENDING" and value is not None:
            raise ValueError(f"pending decision {decision_id} must have a null value")
        if status == "APPROVED" and (not isinstance(value, str) or not value.strip()):
            raise ValueError(f"approved decision {decision_id} requires a value")
        if status == "NOT_APPLICABLE" and value is not None:
            raise ValueError(f"not-applicable decision {decision_id} must have a null value")
        results.append({"id": decision_id, "status": status})

    pending = [item["id"] for item in results if item["status"] == "PENDING"]
    report = {
        "schema_version": 1,
        "verdict": "CLOSED" if not pending else "OPEN",
        "pending": pending,
        "counts": {"total": len(results), "pending": len(pending)},
    }
    return report, 0 if not pending else 3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decisions", required=True, type=Path)
    args = parser.parse_args()
    try:
        report, exit_code = verify(args.decisions)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"launch decision configuration error: {exc}", file=sys.stderr)
        return 64
    print(json.dumps(report, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
