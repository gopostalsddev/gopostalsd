"""Static safety contract for GP-22 rollback and recovery."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = (ROOT / "docs/deployment/gp22-fresh-launch-rollback.md").read_text(
    encoding="utf-8"
)


def test_three_write_boundaries_are_explicit_and_ordered():
    phases = (
        "## Phase A — before canonical DNS changes",
        "## Phase B — DNS changed, proven zero real writes",
        "## Phase C — first real write has occurred",
    )
    positions = [RUNBOOK.index(phase) for phase in phases]
    assert positions == sorted(positions)
    assert "When uncertain, assume a\nreal write has occurred" in RUNBOOK


def test_database_divergence_rules_are_fail_closed():
    for rule in (
        "Never restore the pre-launch database over new writes",
        "Never run an Alembic\ndowngrade",
        "DNS changes alone cannot resolve database divergence",
        "preserve the database",
    ):
        assert rule in RUNBOOK
    assert "flask db downgrade`" in RUNBOOK
    assert "flask db downgrade` to" not in RUNBOOK


def test_render_is_never_treated_as_a_working_rollback_target():
    assert "historical Render database is unavailable" in RUNBOOK
    assert "database-broken Render API" in RUNBOOK
    assert "Never point DNS at Render" in RUNBOOK


def test_provider_events_survive_rollback():
    assert "keeping health diagnostics and the Square webhook receiver available" in RUNBOOK
    assert "keep the canonical webhook endpoint\nreachable" in RUNBOOK
    assert "inbox/idempotency" in RUNBOOK
    assert "do not replay captured bodies" in RUNBOOK.lower()


def test_migration_restore_frontend_and_integration_failures_are_covered():
    for heading in (
        "### Migration failure",
        "### Database restore failure",
        "### Backend or readiness failure",
        "### Frontend or Caddy failure",
        "### Square webhook or payment failure",
        "### MailerSend failure",
        "### Object-storage failure",
        "### Monitoring failure",
    ):
        assert heading in RUNBOOK


def test_reopen_requires_new_release_bound_acceptance():
    assert "fresh GP-17 `MIGRATION_READY` report bound to the active release SHA" in RUNBOOK
    assert "reconciled all writes/provider events" in RUNBOOK


def test_canonical_url_is_unresolved_and_no_live_operation_is_authorized():
    assert "unresolved `CANONICAL_URL`" in RUNBOOK
    assert "https://gopostalsd.com" not in RUNBOOK
    assert "authorizes no host, DNS, provider, or database\nmutation" in RUNBOOK
