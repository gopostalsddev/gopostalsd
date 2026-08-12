"""Static GP-18 backup, retention, and restore safety contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKUP = (ROOT / "deploy/gopostal/backup-database.sh").read_text(encoding="utf-8")
RESTORE = (ROOT / "deploy/gopostal/restore-drill.sh").read_text(encoding="utf-8")
SERVICE = (ROOT / "deploy/gopostal/systemd/gopostal-backup.service").read_text(encoding="utf-8")
TIMER = (ROOT / "deploy/gopostal/systemd/gopostal-backup.timer").read_text(encoding="utf-8")


def test_backup_is_gopostal_only_root_only_and_custom_format():
    assert "EUID -ne 0" in BACKUP
    assert "'/var/backups/gopostal'" in BACKUP
    assert "'/srv/gopostal/current'" in BACKUP
    assert "--format=custom" in BACKUP
    assert "rezza" not in BACKUP.lower()


def test_backup_is_published_only_after_structural_verification():
    assert "pg_restore --list" in BACKUP
    assert "sha256sum" in BACKUP
    assert BACKUP.index("pg_restore --list") < BACKUP.index('mv "$partial" "$archive"')
    assert "implausibly small" in BACKUP
    assert "trap cleanup_partial EXIT" in BACKUP


def test_retention_is_bounded_by_tier_and_paths_are_guarded():
    for tier, keep in (("nightly", 7), ("weekly", 5), ("monthly", 12), ("pre-deploy", 5)):
        assert f"prune_tier {tier} {keep}" in BACKUP
    assert '[[ $candidate == "$BACKUP_DIR"/' in BACKUP


def test_offsite_copy_is_required_but_never_invented():
    assert "'/usr/local/sbin/gopostal-backup-offsite'" in BACKUP
    assert "encrypted off-host hook is missing" in BACKUP
    assert 'exit 2' in BACKUP
    assert "s3://" not in BACKUP and "rclone:" not in BACKUP


def test_restore_is_disposable_checksum_verified_and_measured():
    assert "sha256sum --check --status" in RESTORE
    assert "gopostal_restore_drill_" in RESTORE
    assert "createdb" in RESTORE
    assert "pg_restore --exit-on-error --single-transaction" in RESTORE
    assert "dropdb --if-exists" in RESTORE
    assert "trap drop_drill EXIT" in RESTORE
    assert '"duration_seconds"' in RESTORE
    assert "SELECT count(*) FROM alembic_version" in RESTORE


def test_timer_is_persistent_and_service_is_sandboxed():
    assert "Persistent=true" in TIMER
    assert "RandomizedDelaySec=" in TIMER
    assert "User=root" in SERVICE
    assert "NoNewPrivileges=true" in SERVICE
    assert "ProtectSystem=strict" in SERVICE
    assert "ReadWritePaths=/var/backups/gopostal" in SERVICE
