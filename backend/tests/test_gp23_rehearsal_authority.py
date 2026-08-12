from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "deploy" / "gopostal" / "rehearsal-authority"
WRAPPER_DIR = BUNDLE / "wrappers"
COMMON = (BUNDLE / "lib" / "gopostal-common.inc").read_text()
COMPOSE = (BUNDLE / "docker-compose.rehearsal.yml").read_text()
FRONTEND_DOCKERFILE = (BUNDLE / "frontend.Dockerfile").read_text()
PROVISION = (BUNDLE / "provision.sh").read_text()
VERIFY = (BUNDLE / "verify-installed.sh").read_text()
ACCEPTANCE = (BUNDLE / "acceptance.sh").read_text()
SUDOERS = (BUNDLE / "sudoers.ops-gopostal").read_text()

EXPECTED_WRAPPERS = {
    "gopostal-sync-source",
    "gopostal-compose-build",
    "gopostal-compose-up",
    "gopostal-compose-down",
    "gopostal-compose-restart",
    "gopostal-status",
    "gopostal-logs",
    "gopostal-migrate",
    "gopostal-bootstrap",
    "gopostal-test",
    "gopostal-backup",
    "gopostal-restore-rehearsal",
}
DIRECT_SCRIPTS = {
    "deploy/gopostal/rehearsal-authority/provision.sh",
    "deploy/gopostal/rehearsal-authority/verify-installed.sh",
    "deploy/gopostal/rehearsal-authority/acceptance.sh",
    *{
        f"deploy/gopostal/rehearsal-authority/wrappers/{name}"
        for name in EXPECTED_WRAPPERS
    },
}


def test_exact_wrapper_inventory_and_no_argument_sudo_grants():
    assert {path.name for path in WRAPPER_DIR.iterdir() if path.is_file()} == EXPECTED_WRAPPERS
    grants = re.findall(
        r"^ops-gopostal ALL=\(root\) NOPASSWD: (/usr/local/bin/gopostal-[a-z-]+) \"\"$",
        SUDOERS,
        re.MULTILINE,
    )
    assert {Path(grant).name for grant in grants} == EXPECTED_WRAPPERS
    assert len(grants) == len(EXPECTED_WRAPPERS) == 12
    assert "/usr/bin/docker" not in SUDOERS
    assert "ALL=(ALL)" not in SUDOERS
    assert "*" not in SUDOERS


def test_all_wrappers_are_bash_syntax_clean_and_fail_on_arguments():
    scripts = [
        BUNDLE / "provision.sh",
        BUNDLE / "verify-installed.sh",
        BUNDLE / "acceptance.sh",
        *sorted(WRAPPER_DIR.iterdir()),
    ]
    for script in scripts:
        assert script.read_bytes().startswith(b"#!/bin/bash")
        subprocess.run(["bash", "-n", str(script)], check=True)
    for wrapper in WRAPPER_DIR.iterdir():
        assert 'no_args "$@"' in wrapper.read_text()


def test_every_directly_executed_bundle_script_has_git_mode_100755():
    result = subprocess.run(
        ["git", "ls-files", "--stage", "--", *sorted(DIRECT_SCRIPTS)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    modes = {
        line.split(maxsplit=1)[1].split("\t", maxsplit=1)[1]: line.split(maxsplit=1)[0]
        for line in result.stdout.splitlines()
    }
    assert set(modes) == DIRECT_SCRIPTS
    assert set(modes.values()) == {"100755"}


def test_common_boundary_is_fixed_and_scrubs_redirection_environment():
    expected_literals = (
        "GOP_PROJECT='gopostal-rehearsal'",
        "GOP_SOURCE='/srv/gopostal/rehearsal-app'",
        "GOP_STACK='/srv/docker/stacks/gopostal-rehearsal'",
        "GOP_REPOSITORY='https://github.com/gopostalsddev/gopostalsd.git'",
        "GOP_SHA='bf6f38707c9d39648213d9bd545c86fa7580e82c'",
        "GOP_BRANCH='main'",
        "--project-name \"$GOP_PROJECT\"",
        "-f \"$GOP_COMPOSE\"",
    )
    for literal in expected_literals:
        assert literal in COMMON
    for variable in (
        "DOCKER_HOST",
        "DOCKER_CONFIG",
        "DOCKER_CONTEXT",
        "DOCKER_TLS_VERIFY",
        "COMPOSE_FILE",
        "COMPOSE_PROJECT_NAME",
        "GIT_CONFIG_SYSTEM",
        "GIT_SSH_COMMAND",
        "BASH_ENV",
        "LD_PRELOAD",
    ):
        assert variable in COMMON
    assert "assert_source" in COMMON
    assert "assert_stack" in COMMON
    assert "assert_project_resources" in COMMON
    assert "GOP_ALLOWED_IMAGES" in COMMON


def test_source_sync_is_exact_public_git_flow_and_never_user_selectable():
    sync = (WRAPPER_DIR / "gopostal-sync-source").read_text()
    assert 'git clone --no-checkout --origin origin "$GOP_REPOSITORY"' in sync
    assert 'git -C "$tmp" checkout --detach "$GOP_SHA"' in sync
    assert 'git -C "$GOP_SOURCE" fetch --no-tags origin "$GOP_BRANCH"' in sync
    assert 'git -C "$GOP_SOURCE" checkout --detach "$GOP_SHA"' in sync
    assert 'assert_source_checkout' in sync
    assert 'assert_source' in sync
    assert "$1" not in sync
    assert "reset --hard" not in sync


def test_compose_is_rehearsal_only_local_and_hardened():
    assert "name: gopostal-rehearsal" in COMPOSE
    assert '"127.0.0.1:8510:5000"' in COMPOSE
    assert '"127.0.0.1:8511:8080"' in COMPOSE
    assert "postgres:17.6-bookworm" in COMPOSE
    assert "gopostal_rehearsal_postgres" in COMPOSE
    assert "gopostal_rehearsal_edge" in COMPOSE
    assert "gopostal_rehearsal_data" in COMPOSE
    assert "internal: true" in COMPOSE
    assert 'user: "10001:10001"' in COMPOSE
    assert "read_only: true" in COMPOSE
    assert "no-new-privileges:true" in COMPOSE
    assert "cap_drop:\n      - ALL" in COMPOSE
    assert "privileged:" not in COMPOSE
    assert "network_mode: host" not in COMPOSE
    assert "/var/run/docker.sock" not in COMPOSE
    forbidden = ("rezza", "wordpress", "portainer", "monitoring")
    assert not any(value in COMPOSE.lower() for value in forbidden)
    assert "node:20.19.0-bookworm-slim" in FRONTEND_DOCKERFILE
    assert "nginxinc/nginx-unprivileged:1.27.5-alpine" in FRONTEND_DOCKERFILE
    assert "proxy_pass http://web:5000" in FRONTEND_DOCKERFILE


def test_provisioning_keeps_operator_away_from_docker_and_secrets():
    assert "useradd --create-home" in PROVISION
    assert "must have no supplemental group memberships" in PROVISION
    assert "usermod -aG docker" not in PROVISION
    assert "chmod 0600" in PROVISION
    assert "install -m 0440" in PROVISION
    assert "visudo -cf" in PROVISION
    assert "MAILERSEND_API_KEY=rehearsal-placeholder-not-live" in PROVISION
    assert "SQUARE_ENVIRONMENT=sandbox" in PROVISION
    assert "SQUARE_MOCK_PAYMENTS=false" in PROVISION
    assert "PUBLIC_BASE_URL=https://rehearsal.invalid" in PROVISION
    assert "support@gopostalsd.com" in PROVISION
    assert "no supplemental groups" in ACCEPTANCE
    assert "raw Docker socket" in ACCEPTANCE


def test_acceptance_starts_with_integrity_and_covers_forbidden_surfaces():
    integrity = ACCEPTANCE.index('if ! "$VERIFY" "$1"')
    first_behavior = ACCEPTANCE.index("expect_success 'identity exists'")
    assert integrity < first_behavior
    required_phrases = (
        "source/install integrity gate",
        "arbitrary docker command denied",
        "sudo docker denied",
        "root shell denied",
        "Caddy operation denied",
        "UFW operation denied",
        "argument injection denied",
        "approved source synchronization succeeds",
        "application exposure is localhost-only",
        "frontend exposure is localhost-only",
        "PostgreSQL has no host port",
        "all published ports reject wildcard exposure",
        "host networking and privileged mode absent",
        "TOTAL FAIL",
    )
    for phrase in required_phrases:
        assert phrase in ACCEPTANCE
    assert "config --format json" in ACCEPTANCE
    assert 'port.get("host_ip", "")' in ACCEPTANCE
    assert 'service.get("network_mode") == "host"' in ACCEPTANCE
    assert 'service.get("privileged") is True' in ACCEPTANCE
    assert "case \"$config\" in *'127.0.0.1:" not in ACCEPTANCE


def test_install_verifier_rejects_drift_stale_wrappers_and_orphan_grants():
    assert "wrapper hash mismatch" in VERIFY
    assert "installed file hash mismatch" in VERIFY
    assert "installed wrapper inventory mismatch" in VERIFY
    assert "expected 12 exact no-argument sudo grants" in VERIFY
    assert "orphan or duplicate ops-gopostal sudo grant detected" in VERIFY
    assert "bundle script Git mode is not 100755" in VERIFY
    assert "sha256sum --check --strict" in VERIFY
    assert "bash -n" in VERIFY
    assert "visudo -cf" in VERIFY
