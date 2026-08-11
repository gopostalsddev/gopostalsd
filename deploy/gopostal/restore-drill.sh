#!/usr/bin/env bash
set -euo pipefail

readonly BACKUP_DIR='/var/backups/gopostal'
readonly EVIDENCE_DIR='/var/lib/gopostal/restore-evidence'
readonly RELEASE_DIR='/srv/gopostal/current'
readonly COMPOSE_FILE="$RELEASE_DIR/deploy/gopostal/docker-compose.production.yml"

if [[ $EUID -ne 0 ]]; then
    printf 'GoPostal restore drills must run as root\n' >&2
    exit 77
fi
if [[ $# -ne 1 ]]; then
    printf 'usage: %s <backup-basename.dump>\n' "$0" >&2
    exit 64
fi

basename=$1
case "$basename" in
    gopostal-*.dump) ;;
    *) printf 'invalid GoPostal backup basename\n' >&2; exit 64 ;;
esac
[[ $basename != */* ]] || { printf 'backup must be a basename\n' >&2; exit 64; }

archive="$BACKUP_DIR/$basename"
checksum="$archive.sha256"
[[ -r $archive && -r $checksum ]] || { printf 'backup or checksum is missing\n' >&2; exit 66; }
(cd "$BACKUP_DIR" && sha256sum --check --status "${checksum##*/}")

compose=(docker compose --project-name gopostal-production \
    --project-directory "$RELEASE_DIR" -f "$COMPOSE_FILE")
drill_db="gopostal_restore_drill_$(date -u +%Y%m%dT%H%M%S)_$$"
[[ $drill_db =~ ^gopostal_restore_drill_[0-9T]+_[0-9]+$ ]] || exit 70

drop_drill() {
    "${compose[@]}" exec -T db sh -eu -c \
        'dropdb --if-exists -U "$POSTGRES_USER" "$1"' sh "$drill_db" >/dev/null
}
trap drop_drill EXIT

started=$(date +%s)
"${compose[@]}" exec -T db sh -eu -c \
    'createdb -U "$POSTGRES_USER" --template=template0 "$1"' sh "$drill_db"
"${compose[@]}" exec -T db sh -eu -c \
    'pg_restore --exit-on-error --single-transaction --no-owner --no-acl -U "$POSTGRES_USER" -d "$1"' \
    sh "$drill_db" <"$archive"

version_rows=$("${compose[@]}" exec -T db sh -eu -c \
    'psql -XAt -U "$POSTGRES_USER" -d "$1" -c "SELECT count(*) FROM alembic_version"' \
    sh "$drill_db")
table_count=$("${compose[@]}" exec -T db sh -eu -c \
    'psql -XAt -U "$POSTGRES_USER" -d "$1" -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = '\''public'\''"' \
    sh "$drill_db")
[[ $version_rows == 1 ]] || { printf 'restored Alembic version row count is not one\n' >&2; exit 1; }
(( table_count > 0 )) || { printf 'restored public schema is empty\n' >&2; exit 1; }

duration=$(( $(date +%s) - started ))
install -d -m 0700 -o root -g root "$EVIDENCE_DIR"
evidence="$EVIDENCE_DIR/${basename%.dump}-restore.json"
printf '{"application":"gopostal","backup":"%s","completed_at":"%s","duration_seconds":%s,"alembic_rows":1,"public_tables":%s,"result":"pass"}\n' \
    "$basename" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$duration" "$table_count" >"$evidence"
chmod 0600 "$evidence"
printf 'GoPostal disposable restore drill passed in %s seconds\n' "$duration"
