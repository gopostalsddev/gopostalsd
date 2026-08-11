"""Static safety contract for the GP-21 fresh-launch runbook."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = (ROOT / "docs/deployment/gp21-fresh-launch-cutover.md").read_text(
    encoding="utf-8"
)


def test_timeline_is_complete_and_chronological():
    headings = [
        "## T-7 days",
        "## T-24 hours",
        "## T-1 hour",
        "## T-30 minutes",
        "## T0",
        "## T+15 minutes",
        "## T+30 minutes",
        "## T+2 hours",
        "## T+24 hours",
    ]
    positions = [RUNBOOK.index(heading) for heading in headings]
    assert positions == sorted(positions)


def test_exact_gp17_release_gate_is_mandatory():
    assert "verdict=MIGRATION_READY" in RUNBOOK
    assert "release_sha" in RUNBOOK
    assert "exactly equal to `RELEASE_SHA`" in RUNBOOK
    assert "A green CI run is not a substitute" in RUNBOOK


def test_fresh_launch_does_not_invent_a_historical_transfer():
    assert "There is no historical database transfer" in RUNBOOK
    assert "no customer-data write" in RUNBOOK
    assert "release/configuration freeze" in RUNBOOK
    assert "pg_dump" not in RUNBOOK
    assert "final DB dump" not in RUNBOOK


def test_canonical_hostname_remains_an_unresolved_launch_variable():
    assert "`CANONICAL_URL`" in RUNBOOK
    assert "`CANONICAL_HOST`" in RUNBOOK
    assert "https://gopostalsd.com" not in RUNBOOK
    assert "support@gopostalsd.com" in RUNBOOK


def test_migrations_bootstrap_and_backup_precede_public_cutover():
    t24 = RUNBOOK.index("## T-24 hours")
    t0 = RUNBOOK.index("## T0")
    for phrase in (
        "migrate the empty database",
        "run explicit idempotent bootstrap",
        "remove\n   bootstrap credentials",
        "verified pre-launch backup",
    ):
        position = RUNBOOK.index(phrase)
        assert t24 < position < t0


def test_provider_and_dns_mutations_are_deferred_to_t0_and_owner_controlled():
    t0 = RUNBOOK.index("## T0")
    assert RUNBOOK.index("Apply the approved DNS change", t0) > t0
    assert RUNBOOK.index("Update the Square production webhook", t0) > t0
    assert "separate owner authorization" in RUNBOOK


def test_render_dns_is_explicitly_not_a_rollback_target():
    assert "pointing DNS back to Render is not a valid application rollback" in RUNBOOK
    assert "Use GP-22 for every rollback decision" in RUNBOOK
