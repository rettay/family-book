#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ARTIFACT_DIR="${ROOT_DIR}/output/playwright/family-book-flow"
SCREENSHOT_DIR="${ARTIFACT_DIR}/screenshots"
TRACE_DIR="${ARTIFACT_DIR}/traces"
SUMMARY_FILE="${ARTIFACT_DIR}/summary.md"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/family-book-pw.XXXXXX")"
PORT="${PORT:-$(
  python3 - <<'PY'
import socket

with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
PY
)}"
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
LOCAL_PWCLI="${ROOT_DIR}/tests/ui/playwright_cli.sh"
SKILL_PWCLI="${CODEX_HOME}/skills/playwright/scripts/playwright_cli.sh"
if [[ -x "${LOCAL_PWCLI}" ]]; then
  export PWCLI="${LOCAL_PWCLI}"
elif [[ -x "${SKILL_PWCLI}" ]]; then
  export PWCLI="${SKILL_PWCLI}"
else
  echo "Missing Playwright CLI wrapper. Expected ${LOCAL_PWCLI} or ${SKILL_PWCLI}." >&2
  exit 1
fi
export PLAYWRIGHT_CLI_SESSION="family-book-flow-${PORT}"
export PLAYWRIGHT_DAEMON_SOCKETS_DIR="/tmp/playwright-cli"

rm -rf "${ARTIFACT_DIR}"
mkdir -p "${ARTIFACT_DIR}"
mkdir -p "${SCREENSHOT_DIR}"
mkdir -p "${TRACE_DIR}"
mkdir -p "${DATA_DIR}"

: > "${SUMMARY_FILE}"

playwright_finalized=0

finalize_playwright_artifacts() {
  if (( playwright_finalized )); then
    return
  fi

  "${PWCLI}" tracing-stop > "${TRACE_DIR}/trace-stop.txt" 2>&1 || true
  "${PWCLI}" video-stop > "${TRACE_DIR}/video-stop.txt" 2>&1 || true
  "${PWCLI}" close >/dev/null 2>&1 || true
  playwright_finalized=1
}

cleanup() {
  finalize_playwright_artifacts
  if [[ -d "${ROOT_DIR}/.playwright-cli" ]]; then
    cp -R "${ROOT_DIR}/.playwright-cli/." "${TRACE_DIR}/" >/dev/null 2>&1 || true
    rm -rf "${ROOT_DIR}/.playwright-cli"
  fi
  if [[ -n "${SERVER_PID:-}" ]]; then
    kill "${SERVER_PID}" >/dev/null 2>&1 || true
    wait "${SERVER_PID}" >/dev/null 2>&1 || true
  fi
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

failures=0

record_failure() {
  echo "FAIL: $1"
  echo "- FAIL: $1" >> "${SUMMARY_FILE}"
  failures=$((failures + 1))
}

record_success() {
  echo "PASS: $1"
  echo "- PASS: $1" >> "${SUMMARY_FILE}"
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

server_ready=0
for _ in $(seq 1 50); do
  if uv run python - <<'PY' >/dev/null 2>&1
import json
import os
import urllib.request

with urllib.request.urlopen(f"{os.environ['BASE_URL']}/health", timeout=1) as response:
    json.load(response)
PY
  then
    server_ready=1
    break
  fi
  sleep 0.2
done

if (( ! server_ready )); then
  echo "App did not become ready at ${BASE_URL}/health within the startup window." >&2
  exit 1
fi

"${PWCLI}" open "${BASE_URL}/login"
"${PWCLI}" tracing-start >/dev/null
"${PWCLI}" video-start >/dev/null
"${PWCLI}" resize 1440 960
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/login.png" --full-page true >/dev/null

assert_run "login page renders" \
  "${PWCLI}" run-code "async page => { await page.waitForSelector('body'); if (!page.url().includes('/login')) throw new Error('not on login'); }"

"${PWCLI}" goto "${BASE_URL}/people"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/redirect-login.png" --full-page true >/dev/null

assert_run "protected page redirects anonymous browser to login" \
  "${PWCLI}" run-code "async page => { if (!page.url().includes('/login')) throw new Error('expected login redirect'); }"

"${PWCLI}" cookie-set session "${ADMIN_SESSION}" --domain 127.0.0.1 --path / --httpOnly true --sameSite Lax >/dev/null
"${PWCLI}" goto "${BASE_URL}/"
"${PWCLI}" run-code "async page => { await page.waitForURL(/\\/tree$/); await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1200); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/tree-landing-admin.png" --full-page true >/dev/null

assert_run "authenticated root lands on tree" \
  "${PWCLI}" run-code "async page => { if (!page.url().includes('/tree')) throw new Error('expected tree landing'); if (!await page.locator('#tree-svg [role=\"button\"]').count()) throw new Error('tree did not render nodes'); }"

assert_run "tree sidebar supports inline person edits" \
  "${PWCLI}" run-code "async page => { const node = page.locator('#tree-svg [data-id=\"tyler-000-0000-0000-000000000002\"]').first(); await node.click(); await page.locator('#tree-person-edit-form').waitFor(); const nickname = page.locator('#tree-person-edit-form input[name=\"nickname\"]'); await nickname.fill('Tree Captain'); await page.locator('#tree-person-edit-form button[type=\"submit\"]').click(); await page.waitForTimeout(1200); let value = await nickname.inputValue(); if (value !== 'Tree Captain') throw new Error('tree inline edit did not persist'); await nickname.fill(''); await page.locator('#tree-person-edit-form button[type=\"submit\"]').click(); await page.waitForTimeout(1200); value = await page.locator('#tree-person-edit-form input[name=\"nickname\"]').inputValue(); if (value !== '') throw new Error('tree inline edit could not clear nickname'); }"

assert_run "tree name preference hides fallback initials when names are off" \
  "${PWCLI}" run-code "async page => { await page.locator('#pref-show-names').uncheck(); await page.locator('#pref-show-photos').uncheck(); await page.locator('#save-tree-preferences').click(); await page.waitForTimeout(1200); const nodeText = await page.locator('#tree-svg [data-id=\"member-00-0000-0000-000000000005\"]').textContent(); if (nodeText && nodeText.includes('Ja')) throw new Error('fallback initials still visible when names are hidden'); }"

"${PWCLI}" goto "${BASE_URL}/moments"
"${PWCLI}" run-code "async page => { await page.locator('#moments-feed').getByText('Seeded family story').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/home-admin.png" --full-page true >/dev/null

assert_run "moments page still shows seeded story" \
  "${PWCLI}" run-code "async page => { if (!await page.locator('#moments-feed').getByText('Seeded family story').count()) throw new Error('missing seeded story'); }"

assert_run "compose modal supports keyboard open, focus, and escape close" \
  "${PWCLI}" run-code "async page => { await page.locator('#compose-details-button').focus(); await page.keyboard.press('Enter'); await page.locator('#compose-modal[aria-hidden=\"false\"]').waitFor(); await page.waitForFunction(() => document.activeElement && document.activeElement.id === 'compose-kind'); await page.keyboard.press('Escape'); await page.waitForFunction(() => document.getElementById('compose-modal')?.hidden === true); await page.waitForFunction(() => document.activeElement && document.activeElement.id === 'compose-details-button'); if (!await page.locator('#compose-modal[hidden]').count()) throw new Error('compose modal did not close'); }"

"${PWCLI}" run-code "async page => { await page.locator('#compose-input').fill('Playwright quick note'); await page.locator('#compose-send-button').click(); await page.waitForLoadState('networkidle'); }"
"${PWCLI}" run-code "async page => { await page.locator('#moments-feed').getByText('Playwright quick note').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/home-after-quick-post.png" --full-page true >/dev/null

assert_run "quick composer creates a visible note" \
  "${PWCLI}" run-code "async page => { if (!await page.locator('#moments-feed').getByText('Playwright quick note').count()) throw new Error('quick note missing'); }"

"${PWCLI}" run-code "async page => { await page.locator('#compose-details-button').click(); await page.waitForSelector('#compose-modal:not(.hidden)'); await page.locator('#compose-kind').selectOption('story'); await page.locator('#compose-person').selectOption('${TYLER_ID}'); await page.locator('#compose-title').fill('Playwright shared story'); await page.locator('#compose-body').fill('A richer family memory captured by browser automation.'); await page.locator('#compose-occurred-at').fill('2024-07-04'); await page.locator('#compose-tagged-people').selectOption(['${MEMBER_ID}']); await page.locator('#compose-submit-button').click(); await page.waitForLoadState('networkidle'); }"
"${PWCLI}" run-code "async page => { await page.locator('#moments-feed').getByText('Playwright shared story').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/home-after-story.png" --full-page true >/dev/null

assert_run "detailed composer creates a richer shared story" \
  "${PWCLI}" run-code "async page => { const text = await page.locator('#moments-feed').textContent(); if (!text || !text.includes('Playwright shared story') || !text.includes('Jane Martin')) throw new Error('shared story missing'); }"

"${PWCLI}" goto "${BASE_URL}/people/new"
"${PWCLI}" run-code "async page => { await page.locator('#create-person-form').waitFor(); await page.locator('#person-first-name').fill('Playwright'); await page.locator('#person-last-name').fill('Relative'); await page.locator('#person-branch').fill('playwright'); await page.locator('#person-residence-place').fill('Lisbon'); await page.locator('#person-residence-country').fill('PT'); await page.locator('#person-contact-email').fill('playwright-relative@example.com'); await page.locator('#create-btn').click(); await page.waitForLoadState('networkidle'); }"
"${PWCLI}" run-code "async page => { await page.locator('.profile-header__name').getByText('Playwright Relative').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/person-created.png" --full-page true >/dev/null

assert_run "admin can create a new person from the browser flow" \
  "${PWCLI}" run-code "async page => { if (!page.url().includes('/people/')) throw new Error('create flow did not land on person page'); const name = await page.locator('.profile-header__name').textContent(); if (!name || !name.includes('Playwright Relative')) throw new Error('new person missing'); }"

"${PWCLI}" goto "${BASE_URL}/admin"
"${PWCLI}" run-code "async page => { await page.locator('#admin-page').waitFor(); await page.locator('#backup-status').getByText('Protected fields').waitFor(); await page.locator('#theme-settings-form').waitFor(); await page.locator('#admin-accounts-card').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/admin-dashboard.png" --full-page true >/dev/null

assert_run "admin dashboard exposes backup status and theme controls" \
  "${PWCLI}" run-code "async page => { const text = await page.locator('#backup-status').textContent(); if (!text || !text.includes('Protected fields')) throw new Error('backup status missing'); if (!await page.locator('#theme-settings-form').count()) throw new Error('theme form missing'); }"

"${PWCLI}" resize 390 844
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/admin-mobile.png" --full-page true >/dev/null

assert_run "admin dashboard avoids horizontal overflow on mobile" \
  "${PWCLI}" run-code "async page => { const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth); if (overflow > 4) throw new Error('admin page overflows horizontally on mobile'); }"

"${PWCLI}" goto "${BASE_URL}/"
"${PWCLI}" run-code "async page => { await page.waitForURL(/\\/tree$/); await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(800); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/home-mobile.png" --full-page true >/dev/null

assert_run "tree landing avoids horizontal overflow on mobile" \
  "${PWCLI}" run-code "async page => { const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth); if (overflow > 4) throw new Error('tree page overflows horizontally on mobile'); }"

"${PWCLI}" goto "${BASE_URL}/people/new"
"${PWCLI}" run-code "async page => { await page.locator('#create-person-form').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/person-new-mobile.png" --full-page true >/dev/null

assert_run "person create form stacks and avoids horizontal overflow on mobile" \
  "${PWCLI}" run-code "async page => { const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth); if (overflow > 4) throw new Error('person create form overflows horizontally on mobile'); const place = await page.locator('#person-burial-place').boundingBox(); const cemetery = await page.locator('#person-burial-cemetery').boundingBox(); if (!place || !cemetery) throw new Error('missing burial fields'); if (Math.abs(place.y - cemetery.y) < 20) throw new Error('burial fields did not stack on mobile'); }"

"${PWCLI}" resize 1440 960

"${PWCLI}" cookie-set session "${MEMBER_SESSION}" --domain 127.0.0.1 --path / --httpOnly true --sameSite Lax >/dev/null
"${PWCLI}" goto "${BASE_URL}/moments"
"${PWCLI}" run-code "async page => { await page.locator('#moments-feed').getByText('Playwright shared story').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/home-member-view.png" --full-page true >/dev/null

assert_run "second member sees the shared story" \
  "${PWCLI}" run-code "async page => { const text = await page.locator('#moments-feed').textContent(); if (!text || !text.includes('Playwright shared story')) throw new Error('member cannot see shared story'); }"

"${PWCLI}" goto "${BASE_URL}/people"
"${PWCLI}" run-code "async page => { await page.locator('#people-results').getByText('Playwright Relative').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/people-member-view.png" --full-page true >/dev/null

assert_run "second member sees the newly created person" \
  "${PWCLI}" run-code "async page => { const text = await page.locator('#people-results').textContent(); if (!text || !text.includes('Playwright Relative')) throw new Error('new person missing from member people view'); }"

"${PWCLI}" goto "${BASE_URL}/people/${TYLER_ID}"
"${PWCLI}" run-code "async page => { await page.locator('#person-moments').waitFor(); await page.locator('#person-moments').getByText('Playwright shared story').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/person-tyler.png" --full-page true >/dev/null

assert_run "person timeline shows tagged or owned story" \
  "${PWCLI}" run-code "async page => { const text = await page.locator('#person-moments').textContent(); if (!text || !text.includes('Playwright shared story')) throw new Error('person timeline missing story'); }"

"${PWCLI}" goto "${BASE_URL}/tree"
"${PWCLI}" run-code "async page => { await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1500); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/tree.png" --full-page true >/dev/null

assert_run "tree page renders data" \
  "${PWCLI}" run-code "async page => { const status = await page.locator('#tree-status').textContent(); if (!status || !status.match(/\\d+/)) throw new Error('tree status missing count'); }"

assert_run "tree node supports keyboard open and escape close" \
  "${PWCLI}" run-code "async page => { const node = page.locator('#tree-svg [role=\"button\"]').first(); await node.focus(); await page.keyboard.press('Enter'); await page.locator('#person-sidebar:not([hidden])').waitFor(); await page.keyboard.press('Escape'); await page.waitForFunction(() => document.getElementById('person-sidebar')?.hidden === true); if (!await page.locator('#person-sidebar[hidden]').count()) throw new Error('tree sidebar did not close'); }"

"${PWCLI}" run-code "async page => { await page.locator('#tree-filter-branch').fill('martin'); await page.locator('#apply-tree-filters').click(); await page.waitForTimeout(1200); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/tree-filtered.png" --full-page true >/dev/null

assert_run "tree filters can be applied in-browser" \
  "${PWCLI}" run-code "async page => { const status = await page.locator('#tree-status').textContent(); if (!status || !status.match(/\\d+/)) throw new Error('filtered tree status missing count'); }"

"${PWCLI}" goto "${BASE_URL}/map"
"${PWCLI}" run-code "async page => { await page.locator('#map-svg').waitFor(); await page.waitForTimeout(1500); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/map.png" --full-page true >/dev/null

assert_run "map page renders at least one marker" \
  "${PWCLI}" run-code "async page => { if (await page.locator('#map-svg g').count() === 0) throw new Error('no map markers'); }"

assert_run "map marker supports keyboard navigation" \
  "${PWCLI}" run-code "async page => { const marker = page.locator('#map-svg [role=\"link\"]').first(); await marker.focus(); await page.keyboard.press('Enter'); await page.waitForURL(/\\/people\\//); if (!page.url().includes('/people/')) throw new Error('map keyboard navigation failed'); }"

"${PWCLI}" goto "${BASE_URL}/map"
"${PWCLI}" run-code "async page => { await page.locator('#map-svg').waitFor(); await page.waitForTimeout(800); }"

"${PWCLI}" run-code "async page => { await page.locator('#map-filter-residence-country').fill('CA'); await page.locator('#apply-map-filters').click(); await page.waitForTimeout(1200); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/map-filtered.png" --full-page true >/dev/null

assert_run "map filters can be applied in-browser" \
  "${PWCLI}" run-code "async page => { if (await page.locator('#map-svg g').count() === 0) throw new Error('filtered map has no markers'); }"

finalize_playwright_artifacts

if (( failures > 0 )); then
  echo "Playwright flow checks completed with ${failures} failure(s). Artifacts: ${ARTIFACT_DIR}"
  exit 1
fi

echo "" >> "${SUMMARY_FILE}"
echo "Artifacts root: ${ARTIFACT_DIR}" >> "${SUMMARY_FILE}"
echo "Screenshots: ${SCREENSHOT_DIR}" >> "${SUMMARY_FILE}"
echo "Trace capture: ${TRACE_DIR}" >> "${SUMMARY_FILE}"

echo "Playwright flow checks passed. Artifacts: ${ARTIFACT_DIR}"
