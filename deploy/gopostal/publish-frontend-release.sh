#!/bin/sh
set -eu

if [ "$#" -ne 2 ]; then
    printf 'usage: %s <release-sha> <built-dist-directory>\n' "$0" >&2
    exit 64
fi

release_sha=$1
source_dist=$2
release_root=${GOPOSTAL_RELEASES_DIR:-/srv/gopostal/releases}
current_link=${GOPOSTAL_CURRENT_LINK:-/srv/gopostal/current}

case "$release_sha" in
    *[!0-9a-f]*|'')
        printf 'release SHA must contain only lowercase hexadecimal characters\n' >&2
        exit 64
        ;;
esac

if [ "${#release_sha}" -lt 7 ] || [ ! -f "$source_dist/index.html" ] || [ ! -d "$source_dist/assets" ]; then
    printf 'release SHA or Vite dist is invalid\n' >&2
    exit 65
fi

umask 022
target="$release_root/$release_sha"
staging="$release_root/.${release_sha}.new"

if [ -e "$target" ] || [ -e "$staging" ]; then
    printf 'release or incomplete staging path already exists for: %s\n' "$release_sha" >&2
    exit 73
fi

mkdir -p "$release_root"
mkdir "$staging"
cp -R "$source_dist" "$staging/frontend-dist"
test -f "$staging/frontend-dist/index.html"
mv "$staging" "$target"

link_parent=$(dirname "$current_link")
link_name=$(basename "$current_link")
temporary_link="$link_parent/.${link_name}.${release_sha}"
ln -s "$target" "$temporary_link"
mv -Tf "$temporary_link" "$current_link"

printf 'published immutable frontend release %s\n' "$release_sha"
