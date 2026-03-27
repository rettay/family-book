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

"${PWCLI}" goto "${BASE_URL}/wiki"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/redirect-login.png" --full-page true >/dev/null

assert_run "protected page redirects anonymous browser to login" \
  "${PWCLI}" run-code "async page => { if (!page.url().includes('/login')) throw new Error('expected login redirect'); }"

"${PWCLI}" cookie-set session "${ADMIN_SESSION}" --domain 127.0.0.1 --path / --httpOnly true --sameSite Lax >/dev/null
"${PWCLI}" goto "${BASE_URL}/"
"${PWCLI}" run-code "async page => { await page.waitForURL(/\\/tree$/); await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1200); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/tree-landing-admin.png" --full-page true >/dev/null

assert_run "authenticated root lands on tree" \
  "${PWCLI}" run-code "async page => { if (!page.url().includes('/tree')) throw new Error('expected tree landing'); if (!await page.locator('#tree-svg [role=\"button\"]').count()) throw new Error('tree did not render nodes'); }"

assert_run "tree keeps partners on the same generation row" \
  "${PWCLI}" run-code "async page => { const getTranslate = async (id) => { const transform = await page.locator('#tree-svg [data-id=\"' + id + '\"]').first().getAttribute('transform'); const match = /translate\\(([-\\d.]+),([-\\d.]+)\\)/.exec(transform || ''); if (!match) throw new Error('missing transform for ' + id); return { x: Number(match[1]), y: Number(match[2]) }; }; const tyler = await getTranslate('tyler-000-0000-0000-000000000002'); const yuliya = await getTranslate('yuliya-00-0000-0000-000000000003'); const root = await getTranslate('root-0000-0000-0000-000000000001'); if (Math.abs(tyler.y - yuliya.y) > 1) throw new Error('partners rendered on different rows'); if (root.y <= tyler.y) throw new Error('child did not render below parents'); }"

assert_run "tree graph cancel stays hidden until relationship picking starts" \
  "${PWCLI}" run-code "async page => { const prompt = page.locator('#tree-graph-prompt'); if (await prompt.isVisible()) throw new Error('graph cancel prompt visible before graph mode'); await page.locator('#tree-svg [data-id=\"tyler-000-0000-0000-000000000002\"]').first().click(); await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').click(); await page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])').waitFor(); const childCard = page.locator('[data-tree-relationship-card=\"child\"]').first(); await childCard.getByRole('button', { name: 'Pick on tree' }).click(); await prompt.waitFor({ state: 'visible' }); await prompt.getByRole('button', { name: 'Cancel' }).click(); await page.waitForTimeout(400); if (await prompt.isVisible()) throw new Error('graph cancel prompt stayed visible after cancel'); }"

assert_run "tree controls panel collapse keeps the canvas visible across reloads" \
  "${PWCLI}" run-code "async page => { await page.locator('#tree-panel-collapse-btn').click(); await page.waitForTimeout(1200); const collapsedWidth = await page.evaluate(() => ({ pageWidth: document.getElementById('tree-page')?.clientWidth || 0, svgWidth: document.getElementById('tree-svg')?.clientWidth || 0, expandedVisible: !document.getElementById('tree-panel-expand-tab')?.hidden, stored: localStorage.getItem('treePanelCollapsed') })); if (collapsedWidth.pageWidth < 200 || collapsedWidth.svgWidth < 200) throw new Error('tree canvas collapsed to zero width'); if (!collapsedWidth.expandedVisible) throw new Error('expand tab hidden after collapse'); if (collapsedWidth.stored !== '1') throw new Error('collapsed state was not stored'); await page.reload(); await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1200); const restoredWidth = await page.evaluate(() => ({ pageWidth: document.getElementById('tree-page')?.clientWidth || 0, svgWidth: document.getElementById('tree-svg')?.clientWidth || 0, expandedVisible: !document.getElementById('tree-panel-expand-tab')?.hidden, stored: localStorage.getItem('treePanelCollapsed') })); if (restoredWidth.pageWidth < 200 || restoredWidth.svgWidth < 200) throw new Error('tree canvas stayed collapsed after reload'); if (!restoredWidth.expandedVisible) throw new Error('expand tab missing after reload'); if (restoredWidth.stored !== '1') throw new Error('collapsed preference missing after reload'); await page.locator('#tree-panel-expand-tab').click(); await page.waitForTimeout(1200); const expandedWidth = await page.evaluate(() => ({ pageWidth: document.getElementById('tree-page')?.clientWidth || 0, stored: localStorage.getItem('treePanelCollapsed') })); if (expandedWidth.pageWidth < 200) throw new Error('tree canvas did not recover after expand'); if (expandedWidth.stored !== '0') throw new Error('expanded state was not stored'); }"

assert_run "tree sidebar supports inline person edits" \
  "${PWCLI}" run-code "async page => { const node = page.locator('#tree-svg [data-id=\"tyler-000-0000-0000-000000000002\"]').first(); await node.click(); await page.locator('button[data-tree-sidebar-tab=\"details\"]').click(); await page.locator('[data-tree-sidebar-panel=\"details\"]:not([hidden]) #tree-person-edit-form').waitFor(); const nickname = page.locator('#tree-person-edit-form input[name=\"nickname\"]'); await nickname.fill('Tree Captain'); await page.locator('#tree-person-edit-form button[type=\"submit\"]').click(); await page.waitForTimeout(1200); let value = await page.locator('#tree-person-edit-form input[name=\"nickname\"]').inputValue(); if (value !== 'Tree Captain') throw new Error('tree inline edit did not persist'); await nickname.fill(''); await page.locator('#tree-person-edit-form button[type=\"submit\"]').click(); await page.waitForTimeout(1200); value = await page.locator('#tree-person-edit-form input[name=\"nickname\"]').inputValue(); if (value !== '') throw new Error('tree inline edit could not clear nickname'); }"

assert_run "tree media workspace uploads media without leaving the tree" \
  "${PWCLI}" run-code "async page => { await page.locator('button[data-tree-sidebar-tab=\"overview\"]').click(); await page.locator('[data-tree-sidebar-panel=\"overview\"]:not([hidden])').waitFor(); await page.locator('[data-tree-metric=\"media\"]').click(); await page.locator('[data-tree-sidebar-panel=\"media\"]:not([hidden])').waitFor(); const fileInput = page.locator('#tree-media-form input[type=\"file\"]'); await fileInput.setInputFiles('${ROOT_DIR}/app/static/demo-photos/portrait-alex.jpg'); await page.locator('#tree-media-form input[name=\"caption\"]').fill('Tree upload'); await page.locator('#tree-media-form button[type=\"submit\"]').click(); await page.waitForTimeout(1500); const text = await page.locator('#tree-sidebar-media').textContent(); if (!await page.locator('#tree-sidebar-media img').count()) throw new Error('tree media upload did not render'); if (!text || !text.includes('Tree upload')) throw new Error('tree media workspace did not show uploaded caption'); }"

assert_run "tree name preference hides fallback initials when names are off" \
  "${PWCLI}" run-code "async page => { await page.locator('#pref-show-names').uncheck(); await page.locator('#pref-show-photos').uncheck(); await page.locator('#save-tree-preferences').click(); await page.waitForTimeout(1200); const nodeText = await page.locator('#tree-svg [data-id=\"member-00-0000-0000-000000000005\"]').textContent(); if (nodeText && nodeText.includes('Ja')) throw new Error('fallback initials still visible when names are hidden'); }"

"${PWCLI}" goto "${BASE_URL}/people/new"
"${PWCLI}" run-code "async page => { await page.locator('#create-person-form').waitFor(); await page.locator('#person-first-name').fill('Playwright'); await page.locator('#person-last-name').fill('Relative'); await page.locator('#person-branch').fill('playwright'); await page.locator('#person-residence-place').fill('Lisbon'); await page.locator('#person-residence-country').fill('PT'); await page.locator('#person-contact-email').fill('playwright-relative@example.com'); await page.locator('#create-btn').click(); await page.waitForLoadState('networkidle'); }"
"${PWCLI}" run-code "async page => { await page.waitForURL(/\\/tree/); await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1200); const url = new URL(page.url()); const focusId = url.searchParams.get('focus'); if (!focusId) throw new Error('create flow did not redirect to tree with focus'); await page.evaluate((id) => { localStorage.setItem('playwrightRelativeId', id); }, focusId); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/person-created.png" --full-page true >/dev/null

assert_run "admin can create a new person from the browser flow" \
  "${PWCLI}" run-code "async page => { if (!page.url().includes('/tree')) throw new Error('create flow did not land on tree'); const focusId = new URL(page.url()).searchParams.get('focus'); if (!focusId) throw new Error('create flow missing focus parameter'); }"

"${PWCLI}" goto "${BASE_URL}/wiki/tyler-martin"
"${PWCLI}" run-code "async page => { await page.locator('.wiki-infobox').waitFor(); await page.locator('.wiki-infobox__social-link').first().waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/wiki-person.png" --full-page true >/dev/null

assert_run "wiki infobox social links render visibly when social profiles exist" \
  "${PWCLI}" run-code "async page => { const links = page.locator('.wiki-infobox__social-link'); const count = await links.count(); if (count < 2) throw new Error('expected social links in wiki infobox'); for (let index = 0; index < count; index += 1) { const link = links.nth(index); const box = await link.boundingBox(); if (!box || box.width < 40 || box.height < 20) throw new Error('social link rendered with zero or tiny size'); const display = await link.evaluate((el) => getComputedStyle(el).display); if (display === 'none') throw new Error('social link hidden by styles'); } }"

"${PWCLI}" cookie-set locale es --domain 127.0.0.1 --path / --sameSite Lax >/dev/null
"${PWCLI}" goto "${BASE_URL}/people/${TYLER_ID}/edit"
"${PWCLI}" run-code "async page => { await page.locator('#edit-social-instagram').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/person-edit-es.png" --full-page true >/dev/null

assert_run "person edit surface uses locale strings for social and date controls" \
  "${PWCLI}" run-code "async page => { const socialHeading = page.getByRole('heading', { name: 'Perfiles Sociales' }); await socialHeading.waitFor(); const birthInput = page.locator('#edit-birth-date-text'); await birthInput.waitFor(); const placeholder = await birthInput.getAttribute('placeholder'); if (!placeholder || !placeholder.includes('1985')) throw new Error('birth date unified input missing Spanish placeholder'); const calBtn = page.locator('.date-input-unified__picker-btn').first(); const calTitle = await calBtn.getAttribute('title'); if (calTitle !== 'Calendario') throw new Error('calendar button title not Spanish: ' + calTitle); }"

"${PWCLI}" cookie-set locale en --domain 127.0.0.1 --path / --sameSite Lax >/dev/null

"${PWCLI}" goto "${BASE_URL}/tree"
"${PWCLI}" run-code "async page => { await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1200); const node = page.locator('#tree-svg [data-id=\"tyler-000-0000-0000-000000000002\"]').first(); await node.click(); await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').waitFor(); }"

assert_run "tree relationships support direct graph linking from the canvas" \
  "${PWCLI}" run-code "async page => { await page.evaluate(() => { window.confirm = () => true; }); await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').click(); await page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])').waitFor(); const childCard = page.locator('[data-tree-relationship-card=\"child\"]').first(); await childCard.getByRole('button', { name: 'Pick on tree' }).click(); await page.locator('#tree-graph-mode-banner:not(.hidden)').waitFor(); const bannerText = await page.locator('#tree-graph-mode-description').textContent(); if (!bannerText || !bannerText.includes('child')) throw new Error('graph mode prompt missing'); await page.locator('#tree-svg [data-id=\"member-00-0000-0000-000000000005\"]').first().click(); await page.waitForTimeout(1400); const relCard = page.locator('.tree-related-card', { hasText: 'Jane Martin' }).first(); if (!await relCard.count()) throw new Error('graph relationship link did not persist'); }"

assert_run "tree relationships can create and replace relatives in one workspace flow" \
  "${PWCLI}" run-code "async page => { await page.evaluate(() => { window.confirm = () => true; }); const relativeId = await page.evaluate(() => localStorage.getItem('playwrightRelativeId')); if (!relativeId) throw new Error('missing stored relative id'); await page.locator('#tree-svg [data-id=\"tyler-000-0000-0000-000000000002\"]').first().click(); await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').click(); await page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])').waitFor(); const childCard = page.locator('[data-tree-relationship-card=\"child\"]').first(); await childCard.getByRole('button', { name: 'Create and connect' }).click(); await page.locator('details[data-tree-relationship-group=\"child\"][open]').waitFor(); const createForm = page.locator('[data-tree-create-form=\"child\"]').first(); await createForm.locator('input[name=\"first_name\"]').fill('Graph'); await createForm.locator('input[name=\"last_name\"]').fill('Kid'); await createForm.locator('button[type=\"submit\"]').click(); await page.waitForTimeout(1400); const graphKid = page.locator('.tree-related-card', { hasText: 'Graph Kid' }).first(); if (!await graphKid.count()) throw new Error('create-and-connect child did not persist'); await graphKid.getByRole('button', { name: 'Replace on tree' }).click(); await page.locator('#tree-graph-mode-banner:not(.hidden)').waitFor(); await page.locator('#tree-svg [data-id=\"' + relativeId + '\"]').first().click(); await page.waitForTimeout(1400); const relText = await page.locator('[data-tree-sidebar-panel=\"relationships\"]').textContent(); if (!relText || !relText.includes('Playwright Relative')) throw new Error('replacement did not link existing person'); if (relText.includes('Graph Kid')) throw new Error('replacement left the old child relationship in place'); }"

assert_run "tree relationship cards support guarded removal after graph edits" \
  "${PWCLI}" run-code "async page => { await page.evaluate(() => { window.confirm = () => true; }); await page.locator('#tree-svg [data-id=\"tyler-000-0000-0000-000000000002\"]').first().click(); await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').click(); await page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])').waitFor(); const relCard = page.locator('.tree-related-card', { hasText: 'Playwright Relative' }).first(); await relCard.getByRole('button', { name: 'Remove link' }).click(); await page.waitForTimeout(1200); const relText = await page.locator('[data-tree-sidebar-panel=\"relationships\"]').textContent(); if (relText && relText.includes('Playwright Relative')) throw new Error('relationship removal did not persist'); }"

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
"${PWCLI}" goto "${BASE_URL}/tree"
"${PWCLI}" run-code "async page => { await page.waitForURL(/\\/tree$/); await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1200); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/tree-member-view.png" --full-page true >/dev/null

assert_run "second member can view the tree" \
  "${PWCLI}" run-code "async page => { if (!page.url().includes('/tree')) throw new Error('member not on tree'); if (!await page.locator('#tree-svg [role=\"button\"]').count()) throw new Error('tree has no nodes for member'); }"

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
  "${PWCLI}" run-code "async page => { const marker = page.locator('#map-svg [role=\"link\"]').first(); await marker.focus(); await page.keyboard.press('Enter'); await page.waitForURL(/\\/people\\/[^/]+\\/edit/); if (!page.url().includes('/edit')) throw new Error('map keyboard navigation failed'); }"

"${PWCLI}" goto "${BASE_URL}/map"
"${PWCLI}" run-code "async page => { await page.locator('#map-svg').waitFor(); await page.waitForTimeout(800); }"

assert_run "configured google map path preserves keyboard navigation" \
  "${PWCLI}" run-code "async page => { await page.evaluate(() => { const mapEl = document.getElementById('google-map'); mapEl.innerHTML = ''; const overlayPane = document.createElement('div'); overlayPane.style.position = 'absolute'; overlayPane.style.inset = '0'; mapEl.appendChild(overlayPane); class FakeMap { constructor(el, opts) { this.el = el; this.opts = opts; } setCenter() {} setZoom() {} fitBounds() {} } class FakeLatLngBounds { constructor() { this.points = []; } extend(value) { this.points.push(value); } getCenter() { return { lat: 20, lng: 0 }; } } class FakeLatLng { constructor(lat, lng) { this.lat = lat; this.lng = lng; } } class FakeOverlayView { setMap(map) { this.map = map; if (map) { if (this.onAdd) this.onAdd(); if (this.draw) this.draw(); } } getPanes() { return { overlayMouseTarget: overlayPane }; } getProjection() { return { fromLatLngToDivPixel() { return { x: 140, y: 140 }; } }; } } window.google = { maps: { Map: FakeMap, OverlayView: FakeOverlayView, LatLngBounds: FakeLatLngBounds, LatLng: FakeLatLng } }; const root = document.getElementById('map-root'); root.dataset.mapProvider = 'google'; root.dataset.googleMapsApiKey = 'fake-google-key'; root.dataset.googleMapsMapId = ''; }); await page.evaluate(() => window.familyBookMap.reload()); await page.locator('.map-google-marker-button').first().waitFor(); const marker = page.locator('.map-google-marker-button').first(); await marker.focus(); await page.keyboard.press('Enter'); await page.waitForURL(/\\/people\\/[^/]+\\/edit/); if (!page.url().includes('/edit')) throw new Error('google map keyboard navigation failed'); }"

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
