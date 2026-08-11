#!/bin/bash
set -euo pipefail
export PATH=/usr/sbin:/usr/bin:/sbin:/bin

readonly SHARE='/usr/local/share/gopostal-rehearsal-authority'
readonly BUNDLE=${1:-}
readonly -a EXPECTED=(gopostal-backup gopostal-bootstrap gopostal-compose-build gopostal-compose-down gopostal-compose-restart gopostal-compose-up gopostal-logs gopostal-migrate gopostal-restore-rehearsal gopostal-status gopostal-sync-source gopostal-test)

if [ "$(id -u)" -ne 0 ]; then printf 'root execution required\n' >&2; exit 77; fi
if [ "$#" -gt 1 ]; then printf 'usage: %s [bundle-directory]\n' "$0" >&2; exit 64; fi

if [ -n "$BUNDLE" ]; then
  [ -d "$BUNDLE" ] && [ ! -L "$BUNDLE" ] || { printf 'invalid bundle directory\n' >&2; exit 66; }
  cd "$BUNDLE"
  sha256sum --check --strict MANIFEST.sha256 >/dev/null
  repo_root=$(git -C "$BUNDLE" rev-parse --show-toplevel)
  for script in provision.sh verify-installed.sh acceptance.sh; do
    [ -x "$BUNDLE/$script" ] || { printf 'bundle script is not executable: %s\n' "$script" >&2; exit 78; }
    relative=${BUNDLE#"$repo_root"/}/$script
    [ "$(git -C "$repo_root" ls-files -s -- "$relative" | awk '{print $1}')" = '100755' ] || {
      printf 'bundle script Git mode is not 100755: %s\n' "$script" >&2; exit 78;
    }
  done
  for name in "${EXPECTED[@]}"; do
    [ -x "$BUNDLE/wrappers/$name" ] || { printf 'bundle wrapper is not executable: %s\n' "$name" >&2; exit 78; }
    relative=${BUNDLE#"$repo_root"/}/wrappers/$name
    [ "$(git -C "$repo_root" ls-files -s -- "$relative" | awk '{print $1}')" = '100755' ] || {
      printf 'bundle wrapper Git mode is not 100755: %s\n' "$name" >&2; exit 78;
    }
    bundle_hash=$(sha256sum "wrappers/$name" | cut -d ' ' -f1)
    installed_hash=$(sha256sum "/usr/local/bin/$name" | cut -d ' ' -f1)
    [ "$bundle_hash" = "$installed_hash" ] || { printf 'wrapper hash mismatch: %s\n' "$name" >&2; exit 78; }
  done
  bundle_hash=$(sha256sum lib/gopostal-common.inc | cut -d ' ' -f1)
  installed_hash=$(sha256sum /usr/local/lib/gopostal-rehearsal/gopostal-common.inc | cut -d ' ' -f1)
  [ "$bundle_hash" = "$installed_hash" ] || { printf 'common include hash mismatch\n' >&2; exit 78; }
  for mapping in \
    'docker-compose.rehearsal.yml:/usr/local/share/gopostal-rehearsal-authority/docker-compose.rehearsal.yml' \
    'docker-compose.rehearsal.yml:/srv/docker/stacks/gopostal-rehearsal/docker-compose.rehearsal.yml' \
    'frontend.Dockerfile:/usr/local/share/gopostal-rehearsal-authority/frontend.Dockerfile' \
    'sudoers.ops-gopostal:/etc/sudoers.d/ops-gopostal' \
    'acceptance.sh:/usr/local/share/gopostal-rehearsal-authority/acceptance.sh' \
    'verify-installed.sh:/usr/local/share/gopostal-rehearsal-authority/verify-installed.sh' \
    'MANIFEST.sha256:/usr/local/share/gopostal-rehearsal-authority/MANIFEST.sha256'
  do
    source_path=${mapping%%:*}
    installed_path=${mapping#*:}
    cmp -s "$source_path" "$installed_path" || { printf 'installed file hash mismatch: %s\n' "$installed_path" >&2; exit 78; }
  done
else
  [ -r "$SHARE/MANIFEST.sha256" ] || { printf 'installed manifest missing\n' >&2; exit 66; }
fi

mapfile -t installed < <(find /usr/local/bin -maxdepth 1 -type f -name 'gopostal-*' -printf '%f\n' | sort)
[ "$(printf '%s\n' "${installed[@]}")" = "$(printf '%s\n' "${EXPECTED[@]}")" ] || { printf 'installed wrapper inventory mismatch\n' >&2; exit 78; }
for name in "${EXPECTED[@]}"; do
  [ "$(stat -c '%u:%g:%a' "/usr/local/bin/$name")" = '0:0:755' ] || { printf 'unsafe wrapper ownership/mode: %s\n' "$name" >&2; exit 78; }
  bash -n "/usr/local/bin/$name"
done
[ "$(stat -c '%u:%g:%a' /etc/sudoers.d/ops-gopostal)" = '0:0:440' ]
visudo -cf /etc/sudoers.d/ops-gopostal >/dev/null
grant_count=$(grep -c '^ops-gopostal ALL=(root) NOPASSWD: /usr/local/bin/gopostal-.* ""$' /etc/sudoers.d/ops-gopostal)
[ "$grant_count" -eq 12 ] || { printf 'expected 12 exact no-argument sudo grants\n' >&2; exit 78; }
mapfile -t identity_grant_files < <(grep -RIl --include='*' 'ops-gopostal' /etc/sudoers /etc/sudoers.d 2>/dev/null | sort -u)
[ "${#identity_grant_files[@]}" -eq 1 ] && [ "${identity_grant_files[0]}" = '/etc/sudoers.d/ops-gopostal' ] || {
  printf 'orphan or duplicate ops-gopostal sudo grant detected\n' >&2; exit 78;
}
printf 'GoPostal installed authority integrity: PASS (12 wrappers, 12 grants)\n'
