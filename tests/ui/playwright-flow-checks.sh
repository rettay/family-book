#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ARTIFACT_DIR="${ROOT_DIR}/output/playwright/family-book-flow"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/family-book-pw.XXXXXX")"
PORT="${PORT:-8766}"
BASE_URL="http://127.0.0.1:${PORT}"

export SECRET_KEY="test-secret-key-not-for-production-use-1234567890"
export FERNET_KEY="$(
  uv run python - <<'PY'
import base64
import hashlib

print(base64.urlsafe_b64encode(hashlib.sha256(b"family-book-playwright-test-key").digest()).decode())
PY
)"
export BASE_URL
export DATABASE_URL="sqlite:///${TMP_DIR}/family-book-ui.db"
export DATA_DIR="${TMP_DIR}/data"
export GOOGLE_CLIENT_ID="test-google-client-id.apps.googleusercontent.com"
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export PWCLI="${CODEX_HOME}/skills/playwright/scripts/playwright_cli.sh"
export PLAYWRIGHT_CLI_SESSION="family-book-flow-${PORT}"
export PLAYWRIGHT_DAEMON_SOCKETS_DIR="/tmp/playwright-cli"

mkdir -p "${ARTIFACT_DIR}"
mkdir -p "${DATA_DIR}"

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]]; then
    kill "${SERVER_PID}" >/dev/null 2>&1 || true
    wait "${SERVER_PID}" >/dev/null 2>&1 || true
  fi
  "${PWCLI}" close >/dev/null 2>&1 || true
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

failures=0

record_failure() {
  echo "FAIL: $1"
  failures=$((failures + 1))
}

record_success() {
  echo "PASS: $1"
}

assert_run() {
  local description="$1"
  shift
  if "$@"; then
    record_success "${description}"
  else
    record_failure "${description}"
  fi
}

cd "${ROOT_DIR}"

uv run python tests/ui/playwright_seed.py > "${TMP_DIR}/seed.env"
# shellcheck disable=SC1090
source "${TMP_DIR}/seed.env"

uv run python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port "${PORT}" > "${ARTIFACT_DIR}/server.log" 2>&1 &
SERVER_PID=$!

for _ in $(seq 1 50); do
  if uv run python - <<'PY' >/dev/null 2>&1
import json
import os
import urllib.request

with urllib.request.urlopen(f"{os.environ['BASE_URL']}/health", timeout=1) as response:
    json.load(response)
PY
  then
    break
  fi
  sleep 0.2
done

env -u PLAYWRIGHT_CLI_SESSION "${PWCLI}" install-browser >/dev/null
"${PWCLI}" open "${BASE_URL}/login"
"${PWCLI}" resize 1440 960
"${PWCLI}" screenshot --filename "${ARTIFACT_DIR}/login.png" --full-page true >/dev/null

assert_run "login page renders" \
  "${PWCLI}" run-code "async page => { await page.waitForSelector('body'); if (!page.url().includes('/login')) throw new Error('not on login'); }"

"${PWCLI}" cookie-set session "${ADMIN_SESSION}" --domain 127.0.0.1 --path / --httpOnly true --sameSite Lax >/dev/null
"${PWCLI}" goto "${BASE_URL}/"
"${PWCLI}" run-code "async page => { await page.locator('#moments-feed').getByText('Seeded family story').waitFor(); }"
"${PWCLI}" screenshot --filename "${ARTIFACT_DIR}/home-admin.png" --full-page true >/dev/null

assert_run "authenticated home feed shows seeded story" \
  "${PWCLI}" run-code "async page => { if (!await page.locator('#moments-feed').getByText('Seeded family story').count()) throw new Error('missing seeded story'); }"

"${PWCLI}" run-code "async page => { await page.locator('#compose-input').fill('Playwright quick note'); await page.locator('#compose-send-button').click(); await page.waitForLoadState('networkidle'); }"
"${PWCLI}" run-code "async page => { await page.locator('#moments-feed').getByText('Playwright quick note').waitFor(); }"
"${PWCLI}" screenshot --filename "${ARTIFACT_DIR}/home-after-quick-post.png" --full-page true >/dev/null

assert_run "quick composer creates a visible note" \
  "${PWCLI}" run-code "async page => { if (!await page.locator('#moments-feed').getByText('Playwright quick note').count()) throw new Error('quick note missing'); }"

"${PWCLI}" run-code "async page => { await page.locator('#compose-details-button').click(); await page.waitForSelector('#compose-modal:not(.hidden)'); await page.locator('#compose-kind').selectOption('story'); await page.locator('#compose-person').selectOption('${TYLER_ID}'); await page.locator('#compose-title').fill('Playwright shared story'); await page.locator('#compose-body').fill('A richer family memory captured by browser automation.'); await page.locator('#compose-occurred-at').fill('2024-07-04'); await page.locator('#compose-tagged-people').selectOption(['${MEMBER_ID}']); await page.locator('#compose-submit-button').click(); await page.waitForLoadState('networkidle'); }"
"${PWCLI}" run-code "async page => { await page.locator('#moments-feed').getByText('Playwright shared story').waitFor(); }"
"${PWCLI}" screenshot --filename "${ARTIFACT_DIR}/home-after-story.png" --full-page true >/dev/null

assert_run "detailed composer creates a richer shared story" \
  "${PWCLI}" run-code "async page => { const text = await page.locator('#moments-feed').textContent(); if (!text || !text.includes('Playwright shared story') || !text.includes('Jane Martin')) throw new Error('shared story missing'); }"

"${PWCLI}" cookie-set session "${MEMBER_SESSION}" --domain 127.0.0.1 --path / --httpOnly true --sameSite Lax >/dev/null
"${PWCLI}" goto "${BASE_URL}/"
"${PWCLI}" run-code "async page => { await page.locator('#moments-feed').getByText('Playwright shared story').waitFor(); }"
"${PWCLI}" screenshot --filename "${ARTIFACT_DIR}/home-member-view.png" --full-page true >/dev/null

assert_run "second member sees the shared story" \
  "${PWCLI}" run-code "async page => { const text = await page.locator('#moments-feed').textContent(); if (!text || !text.includes('Playwright shared story')) throw new Error('member cannot see shared story'); }"

"${PWCLI}" goto "${BASE_URL}/people/${TYLER_ID}"
"${PWCLI}" run-code "async page => { await page.locator('#person-moments').waitFor(); await page.locator('#person-moments').getByText('Playwright shared story').waitFor(); }"
"${PWCLI}" screenshot --filename "${ARTIFACT_DIR}/person-tyler.png" --full-page true >/dev/null

assert_run "person timeline shows tagged or owned story" \
  "${PWCLI}" run-code "async page => { const text = await page.locator('#person-moments').textContent(); if (!text || !text.includes('Playwright shared story')) throw new Error('person timeline missing story'); }"

"${PWCLI}" goto "${BASE_URL}/tree"
"${PWCLI}" run-code "async page => { await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1500); }"
"${PWCLI}" screenshot --filename "${ARTIFACT_DIR}/tree.png" --full-page true >/dev/null

assert_run "tree page renders data" \
  "${PWCLI}" run-code "async page => { const status = await page.locator('#tree-status').textContent(); if (!status || !status.match(/\\d+/)) throw new Error('tree status missing count'); }"

"${PWCLI}" goto "${BASE_URL}/map"
"${PWCLI}" run-code "async page => { await page.locator('#map-svg').waitFor(); await page.waitForTimeout(1500); }"
"${PWCLI}" screenshot --filename "${ARTIFACT_DIR}/map.png" --full-page true >/dev/null

assert_run "map page renders at least one marker" \
  "${PWCLI}" run-code "async page => { if (await page.locator('#map-svg g').count() === 0) throw new Error('no map markers'); }"

if (( failures > 0 )); then
  echo "Playwright flow checks completed with ${failures} failure(s). Screenshots: ${ARTIFACT_DIR}"
  exit 1
fi

echo "Playwright flow checks passed. Screenshots: ${ARTIFACT_DIR}"
