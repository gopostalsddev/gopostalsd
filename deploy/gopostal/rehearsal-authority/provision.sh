#!/bin/bash
set -euo pipefail
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
umask 077

readonly IDENTITY='ops-gopostal'
readonly BASE_DIR=$(cd -- "$(dirname -- "$0")" && pwd -P)
readonly MANIFEST="$BASE_DIR/MANIFEST.sha256"
readonly LIB_DIR='/usr/local/lib/gopostal-rehearsal'
readonly SHARE_DIR='/usr/local/share/gopostal-rehearsal-authority'
readonly STACK_DIR='/srv/docker/stacks/gopostal-rehearsal'
readonly BACKUP_DIR='/var/backups/gopostal-rehearsal'
readonly EVIDENCE_DIR='/var/lib/gopostal-rehearsal/evidence'
readonly SUDOERS='/etc/sudoers.d/ops-gopostal'
readonly -a EXPECTED_WRAPPERS=(gopostal-backup gopostal-bootstrap gopostal-compose-build gopostal-compose-down gopostal-compose-restart gopostal-compose-up gopostal-logs gopostal-migrate gopostal-restore-rehearsal gopostal-status gopostal-sync-source gopostal-test)
readonly -a DIRECT_SCRIPTS=(provision.sh verify-installed.sh acceptance.sh)

if [ "$(id -u)" -ne 0 ]; then
  printf 'run provisioning as root\n' >&2
  exit 77
fi
if [ "$#" -ne 1 ]; then
  printf 'usage: %s /absolute/path/to/ops_gopostal_ed25519.pub\n' "$0" >&2
  exit 64
fi
case "$1" in /*) ;; *) printf 'public key path must be absolute\n' >&2; exit 64 ;; esac
[ -f "$1" ] && [ ! -L "$1" ] || { printf 'public key must be a regular file\n' >&2; exit 66; }
key=$(cat -- "$1")
[ "$(wc -l <"$1")" -eq 1 ] || { printf 'public key file must contain exactly one line\n' >&2; exit 65; }
case "$key" in ssh-ed25519\ *) ;; *) printf 'only a single ssh-ed25519 public key is accepted\n' >&2; exit 65 ;; esac

cd "$BASE_DIR"
sha256sum --check --strict "$MANIFEST"

repo_root=$(git -C "$BASE_DIR" rev-parse --show-toplevel)
for script in "${DIRECT_SCRIPTS[@]}"; do
  [ -x "$BASE_DIR/$script" ] || { printf 'bundle script is not executable: %s\n' "$script" >&2; exit 78; }
  relative=${BASE_DIR#"$repo_root"/}/$script
  [ "$(git -C "$repo_root" ls-files -s -- "$relative" | awk '{print $1}')" = '100755' ] || {
    printf 'bundle script Git mode is not 100755: %s\n' "$script" >&2; exit 78;
  }
done

mapfile -t wrappers < <(find wrappers -mindepth 1 -maxdepth 1 -type f -printf '%f\n' | sort)
[ "${#wrappers[@]}" -eq 12 ] || { printf 'expected 12 wrappers, found %s\n' "${#wrappers[@]}" >&2; exit 78; }
[ "$(printf '%s\n' "${wrappers[@]}")" = "$(printf '%s\n' "${EXPECTED_WRAPPERS[@]}")" ] || { printf 'wrapper inventory mismatch\n' >&2; exit 78; }
for wrapper in "${wrappers[@]}"; do bash -n "wrappers/$wrapper"; done
for wrapper in "${wrappers[@]}"; do
  [ -x "wrappers/$wrapper" ] || { printf 'bundle wrapper is not executable: %s\n' "$wrapper" >&2; exit 78; }
  relative=${BASE_DIR#"$repo_root"/}/wrappers/$wrapper
  [ "$(git -C "$repo_root" ls-files -s -- "$relative" | awk '{print $1}')" = '100755' ] || {
    printf 'bundle wrapper Git mode is not 100755: %s\n' "$wrapper" >&2; exit 78;
  }
done
bash -n provision.sh
bash -n verify-installed.sh
bash -n acceptance.sh
visudo -cf sudoers.ops-gopostal >/dev/null

if ! getent passwd "$IDENTITY" >/dev/null; then
  useradd --create-home --home-dir "/home/$IDENTITY" --shell /bin/bash "$IDENTITY"
fi
[ "$(id -u "$IDENTITY")" -ne 0 ]
[ "$(getent passwd "$IDENTITY" | cut -d: -f6-7)" = "/home/$IDENTITY:/bin/bash" ] || {
  printf '%s has an unexpected home or shell\n' "$IDENTITY" >&2; exit 78;
}
if [ "$(id -nG "$IDENTITY")" != "$IDENTITY" ]; then
  printf '%s must have no supplemental group memberships\n' "$IDENTITY" >&2
  exit 78
fi

install -d -m 0755 -o root -g root /srv/gopostal
install -d -m 0700 -o root -g root "$STACK_DIR" "$BACKUP_DIR" "$EVIDENCE_DIR"
install -d -m 0755 -o root -g root "$LIB_DIR" "$SHARE_DIR"
install -m 0644 -o root -g root lib/gopostal-common.inc "$LIB_DIR/gopostal-common.inc"
install -m 0644 -o root -g root docker-compose.rehearsal.yml "$SHARE_DIR/docker-compose.rehearsal.yml"
install -m 0644 -o root -g root docker-compose.rehearsal.yml "$STACK_DIR/docker-compose.rehearsal.yml"
install -m 0644 -o root -g root frontend.Dockerfile "$SHARE_DIR/frontend.Dockerfile"
install -m 0644 -o root -g root MANIFEST.sha256 "$SHARE_DIR/MANIFEST.sha256"
install -m 0755 -o root -g root verify-installed.sh "$SHARE_DIR/verify-installed.sh"
install -m 0755 -o root -g root acceptance.sh "$SHARE_DIR/acceptance.sh"
for wrapper in "${wrappers[@]}"; do
  install -m 0755 -o root -g root "wrappers/$wrapper" "/usr/local/bin/$wrapper"
done

if [ ! -e "$STACK_DIR/database.env" ]; then
  db_password=$(openssl rand -hex 32)
  cat >"$STACK_DIR/database.env" <<EOF
POSTGRES_USER=gopostal_rehearsal
POSTGRES_PASSWORD=$db_password
POSTGRES_DB=gopostal_rehearsal
EOF
else
  db_password=$(sed -n 's/^POSTGRES_PASSWORD=//p' "$STACK_DIR/database.env")
  [ -n "$db_password" ] && [ "$(printf '%s' "$db_password" | tr -cd '0-9a-f' | wc -c)" -eq 64 ] || {
    printf 'existing rehearsal database password has an unexpected format\n' >&2; exit 78;
  }
fi

if [ ! -e "$STACK_DIR/application.env" ]; then
  secret_key=$(openssl rand -hex 48)
  jwt_key=$(openssl rand -hex 48)
  oauth_key=$(openssl rand -hex 32)
  synthetic_jwt='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
  cat >"$STACK_DIR/application.env" <<EOF
ENVIRONMENT=production
DEBUG=false
FLASK_DEBUG=0
ENABLE_SWAGGER_UI=false
DATABASE_URL=postgresql://gopostal_rehearsal:$db_password@db:5432/gopostal_rehearsal
SECRET_KEY=$secret_key
JWT_SECRET_KEY=$jwt_key
SESSION_COOKIE_SECURE=true
FRONTEND_URL=https://rehearsal.invalid
PUBLIC_BASE_URL=https://rehearsal.invalid
TRUSTED_PROXY_HOPS=1
EMAIL_PROVIDER=mailersend
EMAIL_FROM_ADDRESS=support@uzimaprints.com
EMAIL_FROM_NAME=Uzima Prints
MAILERSEND_API_KEY=rehearsal-placeholder-not-live
SQUARE_ENVIRONMENT=sandbox
SQUARE_ACCESS_TOKEN=rehearsal-placeholder-not-live
SQUARE_APPLICATION_ID=sandbox-sq0idb-rehearsal-placeholder
SQUARE_LOCATION_ID=rehearsal-placeholder
SQUARE_WEBHOOK_SIGNATURE_KEY=rehearsal-placeholder-not-live
SQUARE_WEBHOOK_URL=https://rehearsal.invalid/api/payments/webhook
SQUARE_MOCK_PAYMENTS=false
OAUTH_TOKEN_ENCRYPTION_KEY=$oauth_key
SINALITE_BASE_URL=https://rehearsal.invalid
SINALITE_CLIENT_ID=rehearsal-placeholder
SINALITE_CLIENT_SECRET=rehearsal-placeholder-not-live
FILE_STORAGE_BACKEND=supabase
SUPABASE_URL=https://rehearsal.invalid
SUPABASE_KEY=$synthetic_jwt
SUPABASE_SERVICE_KEY=$synthetic_jwt
SUPABASE_BUCKET=gopostal-rehearsal
AUTH_RATE_LIMIT_STORE=memory
LOG_LEVEL=INFO
READINESS_DB_TIMEOUT_MS=2000
EOF
fi

cat >"$STACK_DIR/.env" <<'EOF'
GOPOSTAL_IMAGE_TAG=b3eb15cd3e47c6962d994a241838ad12e3d0b60e
EOF
chmod 0600 "$STACK_DIR/.env" "$STACK_DIR/database.env" "$STACK_DIR/application.env"
chown root:root "$STACK_DIR/.env" "$STACK_DIR/database.env" "$STACK_DIR/application.env"

home=$(getent passwd "$IDENTITY" | cut -d: -f6)
install -d -m 0700 -o "$IDENTITY" -g "$IDENTITY" "$home/.ssh"
printf 'no-port-forwarding,no-agent-forwarding,no-X11-forwarding,no-user-rc,no-pty %s\n' "$key" \
  >"$home/.ssh/authorized_keys"
chown "$IDENTITY:$IDENTITY" "$home/.ssh/authorized_keys"
chmod 0600 "$home/.ssh/authorized_keys"

install -m 0440 -o root -g root sudoers.ops-gopostal "$SUDOERS"
visudo -cf "$SUDOERS" >/dev/null

"$SHARE_DIR/verify-installed.sh"
printf 'GoPostal rehearsal authority provisioned; no containers were created or started.\n'
