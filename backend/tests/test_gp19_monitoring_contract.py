"""Static GP-19 monitoring and alerting contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RULES = (ROOT / "deploy/gopostal/monitoring/prometheus-alerts.yml").read_text(encoding="utf-8")
SCRAPE = (ROOT / "deploy/gopostal/monitoring/prometheus-scrape.yml.template").read_text(encoding="utf-8")
CADDY = (ROOT / "deploy/gopostal/Caddyfile").read_text(encoding="utf-8")
TEMPORARY_CADDY = (ROOT / "deploy/gopostal/Caddyfile.temporary").read_text(encoding="utf-8")
BACKUP = (ROOT / "deploy/gopostal/backup-database.sh").read_text(encoding="utf-8")
SERVICE = (ROOT / "deploy/gopostal/systemd/gopostal-backup.service").read_text(encoding="utf-8")


def test_canonical_hostname_stays_an_unresolved_template_value():
    assert "__GOPOSTAL_HOST__" in SCRAPE
    assert "gopostalsd.com" not in SCRAPE
    assert "__GOPOSTAL_POSTGRES_EXPORTER_TARGET__" in SCRAPE
    assert "__GOPOSTAL_BLACKBOX_EXPORTER_TARGET__" in SCRAPE
    assert "__GOPOSTAL_CADDY_METRICS_TARGET__" in SCRAPE
    assert "127.0.0.1:2019" not in SCRAPE
    assert "127.0.0.1:9115" not in SCRAPE


def test_blackbox_caddy_and_postgres_jobs_are_separate():
    for job in ("blackbox-gopostal", "caddy-gopostal", "gopostal-postgres"):
        assert f"job_name: {job}" in SCRAPE
    assert "/health/ready" in SCRAPE


def test_minimum_blocking_alert_domains_are_present():
    for alert in (
        "GoPostalPublicUnavailable",
        "GoPostalReadinessUnavailable",
        "GoPostalCertificateExpiresSoon",
        "GoPostalBackendContainerMissing",
        "GoPostalDatabaseUnavailable",
        "GoPostalContainerMemoryHigh",
        "GoPostalHostDiskLow",
        "GoPostalBackupMissingOrStale",
        "GoPostalHttp5xxElevated",
        "GoPostalHttpLatencyHigh",
    ):
        assert f"alert: {alert}" in RULES


def test_backup_metric_means_local_and_offsite_success():
    metric_write = BACKUP.index("gopostal_backup_last_success_timestamp_seconds")
    offsite_success = BACKUP.index('if ! "$OFFSITE_HOOK"')
    assert metric_write > offsite_success
    assert "/var/lib/node_exporter/textfile_collector" in BACKUP
    assert "/var/lib/node_exporter/textfile_collector" in SERVICE


def test_caddy_metrics_are_local_admin_only_and_per_host():
    for configuration in (CADDY, TEMPORARY_CADDY):
        assert "admin localhost:2019" in configuration
        assert "metrics {\n\t\tper_host\n\t}" in configuration


def test_probe_alerts_fail_closed_when_metrics_disappear():
    assert 'absent(probe_success{job="blackbox-gopostal",probe="root"})' in RULES
    assert 'absent(probe_success{job="blackbox-gopostal",probe="readiness"})' in RULES
    assert 'absent(probe_ssl_earliest_cert_expiry{job="blackbox-gopostal"})' in RULES


def test_rules_do_not_embed_secrets_or_cross_application_names():
    combined = (RULES + SCRAPE).lower()
    assert "authorization" not in combined
    assert "password" not in combined
    assert "rezza" not in combined
