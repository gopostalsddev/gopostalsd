#!/bin/bash
set -u
export PATH=/usr/sbin:/usr/bin:/sbin:/bin

readonly IDENTITY='ops-gopostal'
readonly VERIFY='/usr/local/share/gopostal-rehearsal-authority/verify-installed.sh'
readonly SOURCE='/srv/gopostal/rehearsal-app'
readonly STACK='/srv/docker/stacks/gopostal-rehearsal'
readonly EXPECTED_SHA='4c94be4a98109ba5807b041e3d39800f88c4b8fd'
readonly -a WRAPPERS=(gopostal-backup gopostal-bootstrap gopostal-compose-build gopostal-compose-down gopostal-compose-restart gopostal-compose-up gopostal-logs gopostal-migrate gopostal-restore-rehearsal gopostal-status gopostal-sync-source gopostal-test)

passes=0
failures=0
pass() { passes=$((passes + 1)); printf 'PASS %s\n' "$1"; }
fail() { failures=$((failures + 1)); printf 'FAIL %s\n' "$1" >&2; }
expect_success() {
  local label=$1; shift
  if "$@" >/dev/null 2>&1; then pass "$label"; else fail "$label"; fi
}
expect_failure() {
  local label=$1; shift
  if "$@" >/dev/null 2>&1; then fail "$label"; else pass "$label"; fi
}

if [ "$(id -u)" -ne 0 ]; then printf 'run acceptance as root\n' >&2; exit 77; fi
if [ "$#" -ne 1 ]; then printf 'usage: %s /absolute/bundle/directory\n' "$0" >&2; exit 64; fi
case "$1" in /*) ;; *) printf 'bundle directory must be absolute\n' >&2; exit 64 ;; esac

# Integrity is the first gate. No behavioral probe runs after drift.
if ! "$VERIFY" "$1"; then
  printf 'FAIL source/install integrity gate\n' >&2
  exit 78
fi
pass 'source/install integrity gate'

expect_success 'identity exists' getent passwd "$IDENTITY"
if [ "$(id -nG "$IDENTITY")" = "$IDENTITY" ]; then pass 'identity has no supplemental groups'; else fail 'identity has no supplemental groups'; fi
expect_failure 'raw Docker socket is unreadable' sudo -u "$IDENTITY" test -r /var/run/docker.sock
expect_failure 'arbitrary docker command denied' sudo -u "$IDENTITY" docker ps
expect_failure 'sudo docker denied' sudo -u "$IDENTITY" sudo -n /usr/bin/docker ps
expect_failure 'root shell denied' sudo -u "$IDENTITY" sudo -n /bin/sh
expect_failure 'systemctl denied' sudo -u "$IDENTITY" sudo -n /usr/bin/systemctl restart docker
expect_failure 'Caddy operation denied' sudo -u "$IDENTITY" sudo -n /usr/bin/caddy validate --config /etc/caddy/Caddyfile
expect_failure 'UFW operation denied' sudo -u "$IDENTITY" sudo -n /usr/sbin/ufw status

for path in \
  /srv/docker/stacks/rezza-staging/.env.staging \
  /srv/docker/stacks/rezza-production/.env.production \
  /etc/rezza/rezza-staging-command.env \
  /var/backups/rezza-staging \
  /var/backups/rezza \
  /var/lib/docker/containers \
  "$STACK/application.env" \
  "$STACK/database.env"
do
  expect_failure "sensitive path unreadable: $path" sudo -u "$IDENTITY" test -r "$path"
done

for path in \
  /etc/caddy/Caddyfile \
  /etc/ssh/sshd_config \
  /etc/sudoers.d \
  /usr/local/bin/gopostal-status \
  /usr/local/lib/gopostal-rehearsal/gopostal-common.inc \
  "$STACK" \
  /srv/gopostal
do
  expect_failure "protected path unwritable: $path" sudo -u "$IDENTITY" test -w "$path"
done

for wrapper in "${WRAPPERS[@]}"; do
  if sudo -u "$IDENTITY" sudo -n -l "/usr/local/bin/$wrapper" 2>/dev/null | grep -q "/usr/local/bin/$wrapper"; then
    pass "exact grant present: $wrapper"
  else
    fail "exact grant present: $wrapper"
  fi
  expect_failure "argument injection denied: $wrapper" \
    sudo -u "$IDENTITY" sudo -n "/usr/local/bin/$wrapper" ';id'
done

if grep -R -Eiq 'rezza|wordpress|portainer|monitoring|caddy|ufw|sshd|/var/run/docker.sock' \
  /usr/local/bin/gopostal-* /usr/local/lib/gopostal-rehearsal/gopostal-common.inc; then
  fail 'installed privileged operations contain no unrelated-workload references'
else
  pass 'installed privileged operations contain no unrelated-workload references'
fi

expect_success 'approved source synchronization succeeds' \
  sudo -u "$IDENTITY" sudo -n /usr/local/bin/gopostal-sync-source
if [ "$(git -C "$SOURCE" rev-parse HEAD 2>/dev/null)" = "$EXPECTED_SHA" ]; then pass 'source SHA is exact'; else fail 'source SHA is exact'; fi
if [ -z "$(git -C "$SOURCE" status --porcelain 2>/dev/null)" ]; then pass 'source tree is clean'; else fail 'source tree is clean'; fi
expect_success 'fixed project status succeeds' sudo -u "$IDENTITY" sudo -n /usr/local/bin/gopostal-status

config=$(GOPOSTAL_IMAGE_TAG="$EXPECTED_SHA" docker compose \
  --project-name gopostal-rehearsal --project-directory "$STACK" \
  --env-file "$STACK/.env" -f "$STACK/docker-compose.rehearsal.yml" config --format json 2>/dev/null) || config=''

effective_port_is_exact() {
  local service=$1 target=$2 published=$3
  printf '%s' "$config" | python3 -c '
import json, sys
document = json.load(sys.stdin)
ports = document.get("services", {}).get(sys.argv[1], {}).get("ports", [])
expected = ("127.0.0.1", int(sys.argv[2]), str(sys.argv[3]))
actual = [
    (str(port.get("host_ip", "")), int(port.get("target", -1)), str(port.get("published", "")))
    for port in ports
]
raise SystemExit(0 if actual == [expected] else 1)
' "$service" "$target" "$published"
}

database_has_no_published_port() {
  printf '%s' "$config" | python3 -c '
import json, sys
document = json.load(sys.stdin)
ports = document.get("services", {}).get("db", {}).get("ports", [])
raise SystemExit(0 if not ports else 1)
'
}

all_published_ports_are_loopback() {
  printf '%s' "$config" | python3 -c '
import json, sys
document = json.load(sys.stdin)
ports = [
    port
    for service in document.get("services", {}).values()
    for port in service.get("ports", [])
]
raise SystemExit(0 if ports and all(str(port.get("host_ip", "")) == "127.0.0.1" for port in ports) else 1)
'
}

no_host_network_or_privileged_service() {
  printf '%s' "$config" | python3 -c '
import json, sys
document = json.load(sys.stdin)
services = document.get("services", {}).values()
unsafe = any(
    service.get("network_mode") == "host" or service.get("privileged") is True
    for service in services
)
raise SystemExit(1 if unsafe else 0)
'
}

if effective_port_is_exact web 5000 8510; then pass 'application exposure is localhost-only'; else fail 'application exposure is localhost-only'; fi
if effective_port_is_exact frontend 8080 8511; then pass 'frontend exposure is localhost-only'; else fail 'frontend exposure is localhost-only'; fi
if database_has_no_published_port; then pass 'PostgreSQL has no host port'; else fail 'PostgreSQL has no host port'; fi
if all_published_ports_are_loopback; then pass 'all published ports reject wildcard exposure'; else fail 'all published ports reject wildcard exposure'; fi
case "$config" in *'gopostal_rehearsal_postgres'*) pass 'dedicated PostgreSQL volume is fixed' ;; *) fail 'dedicated PostgreSQL volume is fixed' ;; esac
case "$config" in *'gopostal_rehearsal_data'*) pass 'dedicated data network is fixed' ;; *) fail 'dedicated data network is fixed' ;; esac
if no_host_network_or_privileged_service; then pass 'host networking and privileged mode absent'; else fail 'host networking and privileged mode absent'; fi

printf '\nTOTAL PASS: %s\nTOTAL FAIL: %s\n' "$passes" "$failures"
[ "$failures" -eq 0 ]
