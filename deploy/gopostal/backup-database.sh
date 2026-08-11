#!/usr/bin/env bash
set -euo pipefail

readonly BACKUP_DIR='/var/backups/gopostal'
readonly RELEASE_DIR='/srv/gopostal/current'
readonly COMPOSE_FILE="$RELEASE_DIR/deploy/gopostal/docker-compose.production.yml"
readonly OFFSITE_HOOK='/usr/local/sbin/gopostal-backup-offsite'

if [[ $EUID -ne 0 ]]; then
    printf 'GoPostal backups must run as root\n' >&2
    exit 77
fi

if [[ $# -ne 1 ]]; then
    printf 'usage: %s scheduled|pre-deploy\n' "$0" >&2
    exit 64
fi

case "$1" in
    scheduled)
        day=$(date -u +%d)
        weekday=$(date -u +%u)
        if [[ $day == 01 ]]; then
            tier=monthly
        elif [[ $weekday == 7 ]]; then
            tier=weekly
        else
            tier=nightly
        fi
        ;;
    pre-deploy) tier=pre-deploy ;;
    *) printf 'unsupported backup reason\n' >&2; exit 64 ;;
esac

if [[ ! -r $COMPOSE_FILE ]]; then
    printf 'GoPostal production Compose file is unavailable\n' >&2
    exit 66
fi

umask 077
install -d -m 0700 -o root -g root "$BACKUP_DIR"
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
stem="gopostal-${tier}-${timestamp}"
partial="$BACKUP_DIR/.${stem}.dump.partial"
archive="$BACKUP_DIR/${stem}.dump"
checksum="$archive.sha256"
metadata="$archive.json"

compose=(docker compose --project-name gopostal-production \
    --project-directory "$RELEASE_DIR" -f "$COMPOSE_FILE")

cleanup_partial() {
    rm -f -- "$partial"
}
trap cleanup_partial EXIT

if ! "${compose[@]}" exec -T db sh -eu -c \
    'exec pg_dump --format=custom --no-owner --no-acl -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
    >"$partial"; then
    printf 'GoPostal pg_dump failed; no backup was published\n' >&2
    exit 1
fi

bytes=$(stat -c %s "$partial")
if (( bytes < 1024 )); then
    printf 'GoPostal dump is implausibly small: %s bytes\n' "$bytes" >&2
    exit 1
fi

if ! "${compose[@]}" exec -T db pg_restore --list <"$partial" >/dev/null; then
    printf 'GoPostal dump failed pg_restore list validation\n' >&2
    exit 1
fi

mv "$partial" "$archive"
trap - EXIT
(cd "$BACKUP_DIR" && sha256sum "${archive##*/}" >"${checksum##*/}")
sha256=$(cut -d ' ' -f 1 "$checksum")
printf '{"application":"gopostal","created_at":"%s","tier":"%s","bytes":%s,"sha256":"%s","format":"postgres-custom"}\n' \
    "$timestamp" "$tier" "$bytes" "$sha256" >"$metadata"
chmod 0600 "$archive" "$checksum" "$metadata"

prune_tier() {
    local name=$1 keep=$2 candidate
    mapfile -t candidates < <(
        find "$BACKUP_DIR" -maxdepth 1 -type f -name "gopostal-${name}-*.dump" -printf '%T@ %p\n' \
            | sort -rn | tail -n "+$((keep + 1))" | cut -d ' ' -f 2-
    )
    for candidate in "${candidates[@]}"; do
        [[ $candidate == "$BACKUP_DIR"/gopostal-"$name"-*.dump ]] || exit 70
        rm -f -- "$candidate" "$candidate.sha256" "$candidate.json"
    done
}

prune_tier nightly 7
prune_tier weekly 5
prune_tier monthly 12
prune_tier pre-deploy 5

if [[ ! -x $OFFSITE_HOOK ]]; then
    printf 'Local backup verified, but required encrypted off-host hook is missing: %s\n' "$OFFSITE_HOOK" >&2
    exit 2
fi

if ! "$OFFSITE_HOOK" "$archive" "$checksum" "$metadata"; then
    printf 'Local backup verified, but encrypted off-host copy failed\n' >&2
    exit 2
fi

printf 'GoPostal backup complete: %s (%s bytes)\n' "${archive##*/}" "$bytes"
