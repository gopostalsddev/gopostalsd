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
  --env-file "$STACK/.env" -f "$STACK/docker-compose.rehearsal.yml" config 2>/dev/null) || config=''
case "$config" in *'127.0.0.1:8510'*) pass 'application exposure is localhost-only' ;; *) fail 'application exposure is localhost-only' ;; esac
case "$config" in *'127.0.0.1:8511'*) pass 'frontend exposure is localhost-only' ;; *) fail 'frontend exposure is localhost-only' ;; esac
case "$config" in *'gopostal_rehearsal_postgres'*) pass 'dedicated PostgreSQL volume is fixed' ;; *) fail 'dedicated PostgreSQL volume is fixed' ;; esac
case "$config" in *'gopostal_rehearsal_data'*) pass 'dedicated data network is fixed' ;; *) fail 'dedicated data network is fixed' ;; esac
if printf '%s' "$config" | grep -Eq 'network_mode:[[:space:]]*host|privileged:[[:space:]]*true'; then
  fail 'host networking and privileged mode absent'
else
  pass 'host networking and privileged mode absent'
fi

printf '\nTOTAL PASS: %s\nTOTAL FAIL: %s\n' "$passes" "$failures"
[ "$failures" -eq 0 ]
