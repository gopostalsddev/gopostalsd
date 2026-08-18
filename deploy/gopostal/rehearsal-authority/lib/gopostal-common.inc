set -euo pipefail

unset BASH_ENV ENV CDPATH GLOBIGNORE LD_PRELOAD LD_LIBRARY_PATH PYTHONPATH \
  DOCKER_HOST DOCKER_CONFIG DOCKER_CONTEXT DOCKER_TLS_VERIFY DOCKER_CERT_PATH \
  DOCKER_API_VERSION COMPOSE_FILE COMPOSE_PROJECT_NAME COMPOSE_PROJECT_DIR \
  COMPOSE_PROFILES COMPOSE_ENV_FILES COMPOSE_PARALLEL_LIMIT \
  GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY \
  GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_COMMON_DIR GIT_NAMESPACE GIT_EXEC_PATH \
  GIT_CONFIG_SYSTEM GIT_CONFIG_GLOBAL GIT_CONFIG_NOSYSTEM GIT_CONFIG_COUNT \
  GIT_SSH GIT_SSH_COMMAND GIT_ASKPASS SSH_ASKPASS GIT_PROXY_COMMAND \
  GIT_TERMINAL_PROMPT HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY \
  http_proxy https_proxy all_proxy no_proxy 2>/dev/null || true
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
export HOME=/root
IFS=$'\n\t'
umask 077

readonly GOP_PROJECT='gopostal-rehearsal'
readonly GOP_SOURCE='/srv/gopostal/rehearsal-app'
readonly GOP_STACK='/srv/docker/stacks/gopostal-rehearsal'
readonly GOP_COMPOSE="$GOP_STACK/docker-compose.rehearsal.yml"
readonly GOP_SHARE='/usr/local/share/gopostal-rehearsal-authority'
readonly GOP_BACKUPS='/var/backups/gopostal-rehearsal'
readonly GOP_EVIDENCE='/var/lib/gopostal-rehearsal/evidence'
readonly GOP_REPOSITORY='https://github.com/gopostalsddev/gopostalsd.git'
readonly GOP_BRANCH='main'
readonly GOP_SHA='6f7c9e8ea4b5d4fac4d5cc05c36f3d249d91acac'
readonly GOP_IMAGE_TAG='6f7c9e8ea4b5d4fac4d5cc05c36f3d249d91acac'
readonly -a GOP_ALLOWED_CONTAINERS=(gopostal_rehearsal_db gopostal_rehearsal_web gopostal_rehearsal_frontend)
readonly -a GOP_ALLOWED_NETWORKS=(gopostal_rehearsal_edge gopostal_rehearsal_data)
readonly -a GOP_ALLOWED_VOLUMES=(gopostal_rehearsal_postgres)
readonly -a GOP_ALLOWED_IMAGES=("gopostal-rehearsal-web:$GOP_IMAGE_TAG" "gopostal-rehearsal-frontend:$GOP_IMAGE_TAG")

no_args() {
  if [ "$#" -ne 0 ]; then
    printf '%s takes no arguments\n' "${0##*/}" >&2
    exit 64
  fi
}

require_root() {
  [ "$(id -u)" -eq 0 ] || { printf 'root execution required\n' >&2; exit 77; }
}

require_regular_root_file() {
  local path=$1 mode owner
  [ -f "$path" ] && [ ! -L "$path" ] || { printf 'unsafe or missing file: %s\n' "$path" >&2; exit 78; }
  owner=$(stat -c '%u:%g' "$path")
  mode=$(stat -c '%a' "$path")
  [ "$owner" = '0:0' ] || { printf 'file is not root-owned: %s\n' "$path" >&2; exit 78; }
  (( (8#$mode & 022) == 0 )) || { printf 'file is group/world writable: %s\n' "$path" >&2; exit 78; }
}

require_root_directory() {
  local path=$1 owner mode
  [ -d "$path" ] && [ ! -L "$path" ] || { printf 'unsafe or missing directory: %s\n' "$path" >&2; exit 78; }
  owner=$(stat -c '%u:%g' "$path")
  mode=$(stat -c '%a' "$path")
  [ "$owner" = '0:0' ] || { printf 'directory is not root-owned: %s\n' "$path" >&2; exit 78; }
  (( (8#$mode & 022) == 0 )) || { printf 'directory is group/world writable: %s\n' "$path" >&2; exit 78; }
}

assert_source_checkout() {
  require_root_directory "$GOP_SOURCE"
  [ "$(git -C "$GOP_SOURCE" remote get-url --all origin | wc -l)" -eq 1 ] &&
    [ "$(git -C "$GOP_SOURCE" remote get-url origin)" = "$GOP_REPOSITORY" ] || {
    printf 'unexpected GoPostal origin\n' >&2; exit 78;
  }
  git -C "$GOP_SOURCE" diff --quiet --ignore-submodules -- &&
    git -C "$GOP_SOURCE" diff --cached --quiet --ignore-submodules -- &&
    [ -z "$(git -C "$GOP_SOURCE" status --porcelain --untracked-files=normal)" ] || {
      printf 'GoPostal source tree is dirty\n' >&2; exit 78;
    }
}

assert_source() {
  assert_source_checkout
  [ "$(git -C "$GOP_SOURCE" rev-parse HEAD)" = "$GOP_SHA" ] || {
    printf 'GoPostal source is not at the reviewed SHA\n' >&2; exit 78;
  }
}

assert_stack() {
  require_root_directory "$GOP_STACK"
  require_regular_root_file "$GOP_COMPOSE"
  require_regular_root_file "$GOP_STACK/.env"
  require_regular_root_file "$GOP_STACK/database.env"
  require_regular_root_file "$GOP_STACK/application.env"
  require_regular_root_file "$GOP_SHARE/docker-compose.rehearsal.yml"
  require_regular_root_file "$GOP_SHARE/frontend.Dockerfile"
  cmp -s "$GOP_COMPOSE" "$GOP_SHARE/docker-compose.rehearsal.yml" || {
    printf 'installed Compose configuration drifted from the reviewed bundle\n' >&2; exit 78;
  }
}

resource_project_label() {
  local kind=$1 name=$2
  case "$kind" in
    container) docker inspect --type container --format '{{index .Config.Labels "com.docker.compose.project"}}' "$name" ;;
    network) docker network inspect --format '{{index .Labels "com.docker.compose.project"}}' "$name" ;;
    volume) docker volume inspect --format '{{index .Labels "com.docker.compose.project"}}' "$name" ;;
    *) return 64 ;;
  esac
}

assert_resource_if_present() {
  local kind=$1 name=$2 label
  if label=$(resource_project_label "$kind" "$name" 2>/dev/null); then
    [ "$label" = "$GOP_PROJECT" ] || {
      printf 'refusing foreign %s named %s\n' "$kind" "$name" >&2; exit 78;
    }
  fi
}

assert_project_resources() {
  local name
  for name in "${GOP_ALLOWED_CONTAINERS[@]}"; do assert_resource_if_present container "$name"; done
  for name in "${GOP_ALLOWED_NETWORKS[@]}"; do assert_resource_if_present network "$name"; done
  for name in "${GOP_ALLOWED_VOLUMES[@]}"; do assert_resource_if_present volume "$name"; done
  for name in "${GOP_ALLOWED_IMAGES[@]}"; do
    if label=$(docker image inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$name" 2>/dev/null); then
      [ "$label" = "$GOP_PROJECT" ] || { printf 'refusing foreign image named %s\n' "$name" >&2; exit 78; }
    fi
  done
}

assert_boundary() {
  require_root
  assert_source
  assert_stack
  assert_project_resources
}

compose() {
  GOPOSTAL_IMAGE_TAG="$GOP_IMAGE_TAG" docker compose \
    --project-name "$GOP_PROJECT" \
    --project-directory "$GOP_STACK" \
    --env-file "$GOP_STACK/.env" \
    -f "$GOP_COMPOSE" "$@"
}
