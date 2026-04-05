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

assert_run "tree renders seeded headshot images and exposes sidebar headshot controls" \
  "${PWCLI}" run-code "async page => { await page.waitForTimeout(1200); const rossNode = page.locator('#tree-svg [data-id=\"ross-0000-0000-000000000012\"]'); if (await rossNode.locator('image').count() === 0) throw new Error('ross node did not render an image element'); await rossNode.first().click(); await page.locator('button[data-tree-sidebar-tab=\"media\"]').click(); const mediaPanel = page.locator('[data-tree-sidebar-panel=\"media\"]:not([hidden])'); await mediaPanel.waitFor(); await mediaPanel.locator('.tree-sidebar-media-item').first().waitFor({ timeout: 5000 }); const headshotButton = mediaPanel.getByRole('button', { name: /Set as headshot/i }).first(); await headshotButton.waitFor({ timeout: 5000 }); const galleryLink = mediaPanel.getByRole('link', { name: /Person gallery/i }).first(); if (await galleryLink.count() === 0) throw new Error('person gallery link missing from tree sidebar'); }"

assert_run "tree keeps partners on the same generation row" \
  "${PWCLI}" run-code "async page => { const getTranslate = async (id) => { const transform = await page.locator('#tree-svg [data-id=\"' + id + '\"]').first().getAttribute('transform'); const match = /translate\\(([-\\d.]+),([-\\d.]+)\\)/.exec(transform || ''); if (!match) throw new Error('missing transform for ' + id); return { x: Number(match[1]), y: Number(match[2]) }; }; const tyler = await getTranslate('tyler-000-0000-0000-000000000002'); const yuliya = await getTranslate('yuliya-00-0000-0000-000000000003'); const root = await getTranslate('root-0000-0000-0000-000000000001'); const robert = await getTranslate('grndpa-00-0000-0000-000000000004'); if (Math.abs(tyler.y - yuliya.y) > 1) throw new Error('partners rendered on different rows'); if (Math.abs(tyler.x - yuliya.x) > 140) throw new Error('partners were not clustered as a family unit'); if (root.y <= tyler.y) throw new Error('child did not render below parents'); if (Math.abs(robert.x - tyler.x) > Math.abs(robert.x - yuliya.x)) throw new Error('ancestry line favors spouse over blood child'); if (await page.locator('#tree-svg .parent-child-line[data-from=\"tyler-000-0000-0000-000000000002\"][data-to=\"root-0000-0000-0000-000000000001\"]').count() === 0) throw new Error('missing direct parent-child edge'); if (await page.locator('#tree-svg .generation-band').count() < 2) throw new Error('missing generation bands'); }"

assert_run "tree builds a shared family unit for two known parents without a partnership row" \
  "${PWCLI}" run-code "async page => { const getTranslate = async (id) => { const transform = await page.locator('#tree-svg [data-id=\"' + id + '\"]').first().getAttribute('transform'); const match = /translate\\(([-\\d.]+),([-\\d.]+)\\)/.exec(transform || ''); if (!match) throw new Error('missing transform for ' + id); return { x: Number(match[1]), y: Number(match[2]) }; }; const janeId = 'member-00-0000-0000-000000000005'; const alexId = 'alex-000-0000-0000-000000000006'; const jordanId = 'jrdn-000-0000-0000-000000000007'; const jane = await getTranslate(janeId); const alex = await getTranslate(alexId); const jordan = await getTranslate(jordanId); if (Math.abs(jane.y - alex.y) > 1) throw new Error('unpartnered co-parents rendered on different rows'); if (jordan.y <= jane.y || jordan.y <= alex.y) throw new Error('unpartnered co-parent child did not render below both parents'); if (await page.locator('#tree-svg .parent-child-line[data-from=\"' + alexId + '\"][data-to=\"' + jordanId + '\"]').count() === 0) throw new Error('missing direct co-parent edge from Alex'); if (await page.locator('#tree-svg .parent-child-line[data-from=\"' + janeId + '\"][data-to=\"' + jordanId + '\"]').count() === 0) throw new Error('missing direct co-parent edge from Jane'); if (await page.locator('#tree-svg .partnership-line[data-from=\"' + alexId + '\"][data-to=\"' + janeId + '\"]').count()) throw new Error('renderer invented a partnership line for unpartnered co-parents'); }"

assert_run "tree clusters spouse pairs even when they sit between siblings and in-law parents" \
  "${PWCLI}" run-code "async page => { const getTranslate = async (id) => { const transform = await page.locator('#tree-svg [data-id=\"' + id + '\"]').first().getAttribute('transform'); const match = /translate\\(([-\\d.]+),([-\\d.]+)\\)/.exec(transform || ''); if (!match) throw new Error('missing transform for ' + id); return { x: Number(match[1]), y: Number(match[2]) }; }; const madelineId = 'madeline-000-0000-000000000011'; const rossId = 'ross-0000-0000-000000000012'; const johnId = 'johnjr-000-0000-000000000013'; const monicaId = 'monica-000-0000-000000000014'; const fatherId = 'fatherj-000-0000-000000000015'; const motherId = 'motherj-000-0000-000000000016'; const boId = 'bojiang-000-0000-000000000017'; const andrewId = 'andrew-000-0000-000000000018'; const annaId = 'anna-0000-0000-000000000019'; const madeline = await getTranslate(madelineId); const ross = await getTranslate(rossId); const john = await getTranslate(johnId); const monica = await getTranslate(monicaId); const father = await getTranslate(fatherId); const mother = await getTranslate(motherId); const bo = await getTranslate(boId); const andrew = await getTranslate(andrewId); const anna = await getTranslate(annaId); const jiangCenter = (father.x + mother.x) / 2; const monicaHouseholdCenter = (john.x + monica.x) / 2; if (Math.abs(madeline.y - ross.y) > 1) throw new Error('childless spouses rendered on different rows'); if (Math.abs(madeline.x - ross.x) > 145) throw new Error('childless spouses not clustered tightly enough'); if (Math.abs(john.y - monica.y) > 1) throw new Error('nested spouses rendered on different rows'); if (Math.abs(john.x - monica.x) > 145) throw new Error('nested spouses not clustered tightly enough'); if (Math.abs(father.y - mother.y) > 1) throw new Error('parent pair rendered on different rows'); if (await page.locator('#tree-svg .partnership-line[data-from=\"' + fatherId + '\"][data-to=\"' + motherId + '\"]').count() === 0) throw new Error('missing visible parent partnership line'); if (await page.locator('#tree-svg .parent-child-line[data-from=\"' + fatherId + '\"][data-to=\"' + monicaId + '\"]').count() === 0) throw new Error('missing direct father-child edge'); if (await page.locator('#tree-svg .parent-child-line[data-from=\"' + motherId + '\"][data-to=\"' + monicaId + '\"]').count() === 0) throw new Error('missing direct mother-child edge'); if (await page.locator('#tree-svg .parent-child-line[data-from=\"' + fatherId + '\"][data-to=\"' + boId + '\"]').count() === 0) throw new Error('missing sibling direct edge'); if (await page.locator('#tree-svg .parent-child-line[data-from=\"' + motherId + '\"][data-to=\"' + boId + '\"]').count() === 0) throw new Error('missing sibling direct edge from mother'); if (Math.abs(monicaHouseholdCenter - jiangCenter) > 190) throw new Error('child household drifted too far from the parents'); if (Math.abs(bo.x - monicaHouseholdCenter) > 220) throw new Error('siblings did not stay grouped under the same household'); if (andrew.y <= john.y || anna.y <= monica.y) throw new Error('children did not render below their married parents'); }"

assert_run "tree keeps one person in multiple households without duplicating them" \
  "${PWCLI}" run-code "async page => { const getTranslate = async (id) => { const transform = await page.locator('#tree-svg [data-id=\"' + id + '\"]').first().getAttribute('transform'); const match = /translate\\(([-\\d.]+),([-\\d.]+)\\)/.exec(transform || ''); if (!match) throw new Error('missing transform for ' + id); return { x: Number(match[1]), y: Number(match[2]) }; }; const caseyId = 'casey-000-0000-000000000020'; const taylorId = 'taylor-00-0000-000000000021'; const morganId = 'morgan-00-0000-000000000022'; const parkerId = 'parker-00-0000-000000000023'; const quinnId = 'quinn-000-0000-000000000024'; if (await page.locator('#tree-svg [data-id=\"' + caseyId + '\"]').count() !== 1) throw new Error('multi-household person was duplicated'); const casey = await getTranslate(caseyId); const taylor = await getTranslate(taylorId); const morgan = await getTranslate(morganId); const parker = await getTranslate(parkerId); const quinn = await getTranslate(quinnId); if (Math.abs(casey.y - taylor.y) > 1 || Math.abs(casey.y - morgan.y) > 1) throw new Error('multi-household partners are not on the same generation row'); if (Math.abs(casey.x - taylor.x) > 150 || Math.abs(casey.x - morgan.x) > 150) throw new Error('multi-household partners are not clustered locally around the shared person'); if (parker.y <= casey.y || quinn.y <= casey.y) throw new Error('multi-household children did not render below their households'); if (await page.locator('#tree-svg .partnership-line--former.partnership-line--status-dissolved[data-from=\"' + caseyId + '\"][data-to=\"' + taylorId + '\"]').count() === 0) throw new Error('former household styling missing for dissolved partnership'); if (await page.locator('#tree-svg .partnership-line--domestic_partner[data-from=\"' + caseyId + '\"][data-to=\"' + morganId + '\"]').count() === 0) throw new Error('domestic-partner styling missing for active household'); }"

assert_run "tree renders adoptive and single-parent guardian households distinctly" \
  "${PWCLI}" run-code "async page => { const getTranslate = async (id) => { /* Fix: wait for D3 to set transform before reading — guards against intermittent race where layout isn't complete yet */ await page.waitForFunction((nodeId) => { const el = document.querySelector('#tree-svg [data-id=\"' + nodeId + '\"]'); if (!el) return false; const t = el.getAttribute('transform'); return t && /translate\\(/.test(t); }, id, { timeout: 5000 }); const transform = await page.locator('#tree-svg [data-id=\"' + id + '\"]').first().getAttribute('transform'); const match = /translate\\(([-\\d.]+),([-\\d.]+)\\)/.exec(transform || ''); if (!match) throw new Error('missing transform for ' + id); return { x: Number(match[1]), y: Number(match[2]) }; }; const rosaId = 'rosa-0000-0000-000000000025'; const benId = 'ben-00000-0000-000000000026'; const miaId = 'mia-00000-0000-000000000027'; const leeId = 'lee-00000-0000-000000000028'; const juneId = 'june-0000-0000-000000000029'; const rosa = await getTranslate(rosaId); const ben = await getTranslate(benId); const mia = await getTranslate(miaId); const lee = await getTranslate(leeId); const june = await getTranslate(juneId); if (Math.abs(rosa.y - ben.y) > 1) throw new Error('adoptive parents rendered on different rows'); if (mia.y <= rosa.y) throw new Error('adoptive child did not render below adoptive parents'); if (june.y <= lee.y) throw new Error('single-parent guardian child did not render below guardian'); if (await page.locator('#tree-svg .parent-child-line.parent-child-line--adoptive[data-from=\"' + rosaId + '\"][data-to=\"' + miaId + '\"]').count() === 0) throw new Error('adoptive edge missing from Rosa'); if (await page.locator('#tree-svg .parent-child-line.parent-child-line--adoptive[data-from=\"' + benId + '\"][data-to=\"' + miaId + '\"]').count() === 0) throw new Error('adoptive edge missing from Ben'); if (await page.locator('#tree-svg .parent-child-line.parent-child-line--guardian[data-from=\"' + leeId + '\"][data-to=\"' + juneId + '\"]').count() === 0) throw new Error('guardian direct edge missing'); }"

assert_run "tree adds directional parent cues, partner knots, and detached branch frames" \
  "${PWCLI}" run-code "async page => { const partnershipKnots = await page.locator('#tree-svg .partnership-knot').count(); if (partnershipKnots === 0) throw new Error('missing partnership knots'); const arrows = await page.locator('#tree-svg .parent-child-line[marker-end=\"url(#tree-parent-arrow)\"]').count(); if (arrows === 0) throw new Error('missing directional parent arrows'); const frames = await page.locator('#tree-svg .tree-component-frame').count(); if (frames === 0) throw new Error('missing detached branch frames'); const labelText = await page.locator('#tree-svg .tree-component-label').first().textContent(); if (!labelText || !labelText.includes('Detached line')) throw new Error('detached branch surname label missing: ' + labelText); }"

assert_run "tree graph cancel stays hidden until relationship picking starts" \
  "${PWCLI}" run-code "async page => { const prompt = page.locator('#tree-graph-prompt'); if (await prompt.isVisible()) throw new Error('graph cancel prompt visible before graph mode'); await page.locator('#tree-svg [data-id=\"tyler-000-0000-0000-000000000002\"]').first().click(); await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').click(); await page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])').waitFor(); const childCard = page.locator('[data-tree-relationship-card=\"child\"]').first(); await childCard.getByRole('button', { name: 'Pick on tree' }).click(); await prompt.waitFor({ state: 'visible' }); await prompt.getByRole('button', { name: 'Cancel' }).click(); await page.waitForTimeout(400); if (await prompt.isVisible()) throw new Error('graph cancel prompt stayed visible after cancel'); }"

assert_run "tree sidebar summarizes selected family context and focus state" \
  "${PWCLI}" run-code "async page => { await page.locator('#tree-svg [data-id=\"tyler-000-0000-0000-000000000002\"]').first().click(); await page.locator('#tree-sidebar-focus-badge').waitFor({ state: 'hidden' }).catch(() => {}); const summary = page.locator('.tree-sidebar-context__summary'); const text = await summary.textContent(); if (!text || !text.includes('Robert Martin') || !text.includes('Yuliya Semesock') || !text.includes('Our Family')) throw new Error('selected-person summary missing expected relationships'); if (!await page.locator('[data-tree-sidebar-tab=\"overview\"]').evaluate((el) => el.classList.contains('tree-sidebar-tab--active'))) throw new Error('overview tab was not active by default'); if (await page.locator('[data-tree-sidebar-panel=\"overview\"]').evaluate((el) => el.hidden)) throw new Error('overview panel was hidden on initial open'); await page.locator('#tree-sidebar-set-focus').click(); await page.waitForTimeout(500); if (!await page.locator('#tree-sidebar-focus-badge').isVisible()) throw new Error('focus badge not shown for focused person'); }"

assert_run "tree selection highlights lineage across ancestors, descendants, and partner context" \
  "${PWCLI}" run-code "async page => { const monicaId = 'monica-000-0000-000000000014'; const lineageIds = ['fatherj-000-0000-000000000015', 'motherj-000-0000-000000000016', 'andrew-000-0000-000000000018', 'anna-0000-0000-000000000019']; const contextId = 'johnjr-000-0000-000000000013'; await page.evaluate((id) => { const node = document.querySelector('#tree-svg [data-id=\"' + id + '\"]'); if (!node) throw new Error('missing node ' + id); node.dispatchEvent(new MouseEvent('click', { bubbles: true })); }, monicaId); await page.waitForFunction((id) => document.querySelector('[data-tree-sidebar-person-id]')?.getAttribute('data-tree-sidebar-person-id') === id, monicaId); const selfClass = await page.locator('#tree-svg [data-id=\"' + monicaId + '\"]').getAttribute('class'); if (!selfClass || !selfClass.includes('tree-node--selected') || !selfClass.includes('tree-node--lineage')) throw new Error('selected person missing strong lineage highlight'); for (const id of lineageIds) { const cls = await page.locator('#tree-svg [data-id=\"' + id + '\"]').getAttribute('class'); if (!cls || !cls.includes('tree-node--lineage')) throw new Error('missing lineage highlight for ' + id); } const partnerClass = await page.locator('#tree-svg [data-id=\"' + contextId + '\"]').getAttribute('class'); if (!partnerClass || !partnerClass.includes('tree-node--context')) throw new Error('missing context highlight for partner'); const mutedCount = await page.locator('#tree-svg .tree-node--muted').count(); if (mutedCount < 2) throw new Error('non-lineage nodes did not dim'); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/tree-focus-sidebar.png" --full-page true >/dev/null
"${PWCLI}" run-code "async page => { await page.locator('button[data-tree-sidebar-tab=\"details\"]').click(); await page.locator('[data-tree-sidebar-panel=\"details\"]:not([hidden])').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/tree-details-admin.png" --full-page true >/dev/null

assert_run "tree graph mode exits cleanly on escape" \
  "${PWCLI}" run-code "async page => { await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').click(); await page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])').waitFor(); const childCard = page.locator('[data-tree-relationship-card=\"child\"]').first(); await childCard.getByRole('button', { name: 'Pick on tree' }).click(); await page.locator('#tree-graph-prompt:not([hidden])').waitFor(); await page.keyboard.press('Escape'); await page.waitForTimeout(500); if (await page.locator('#tree-graph-prompt').isVisible()) throw new Error('graph prompt stayed visible after escape'); }"

assert_run "tree controls panel collapse keeps the canvas visible across reloads" \
  "${PWCLI}" run-code "async page => { const toggleTab = page.locator('#tree-panel-expand-tab'); await toggleTab.waitFor(); const initialLabel = await toggleTab.textContent(); if (!initialLabel.includes('Hide Family Tree Settings')) throw new Error('expand tab should say Hide when panel is open, got: ' + initialLabel); await toggleTab.click(); await page.waitForTimeout(1200); const collapsedWidth = await page.evaluate(() => ({ pageWidth: document.getElementById('tree-page')?.clientWidth || 0, svgWidth: document.getElementById('tree-svg')?.clientWidth || 0, expandLabel: document.getElementById('tree-panel-expand-tab')?.textContent || '', stored: localStorage.getItem('treePanelCollapsed') })); if (collapsedWidth.pageWidth < 200 || collapsedWidth.svgWidth < 200) throw new Error('tree canvas collapsed to zero width'); if (!collapsedWidth.expandLabel.includes('Expand Family Tree Settings')) throw new Error('collapsed tools affordance label missing, got: ' + collapsedWidth.expandLabel); if (collapsedWidth.stored !== '1') throw new Error('collapsed state was not stored'); await page.reload(); await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1200); const restoredWidth = await page.evaluate(() => ({ pageWidth: document.getElementById('tree-page')?.clientWidth || 0, svgWidth: document.getElementById('tree-svg')?.clientWidth || 0, expandLabel: document.getElementById('tree-panel-expand-tab')?.textContent || '', stored: localStorage.getItem('treePanelCollapsed') })); if (restoredWidth.pageWidth < 200 || restoredWidth.svgWidth < 200) throw new Error('tree canvas stayed collapsed after reload'); if (!restoredWidth.expandLabel.includes('Expand Family Tree Settings')) throw new Error('expand label wrong after reload, got: ' + restoredWidth.expandLabel); if (restoredWidth.stored !== '1') throw new Error('collapsed preference missing after reload'); await page.locator('#tree-panel-expand-tab').click(); await page.waitForTimeout(1200); const expandedWidth = await page.evaluate(() => ({ pageWidth: document.getElementById('tree-page')?.clientWidth || 0, stored: localStorage.getItem('treePanelCollapsed'), hideLabel: document.getElementById('tree-panel-expand-tab')?.textContent || '' })); if (expandedWidth.pageWidth < 200) throw new Error('tree canvas did not recover after expand'); if (expandedWidth.stored !== '0') throw new Error('expanded state was not stored'); if (!expandedWidth.hideLabel.includes('Hide Family Tree Settings')) throw new Error('tab should say Hide after expand, got: ' + expandedWidth.hideLabel); }"

assert_run "tree sidebar supports inline person edits" \
  "${PWCLI}" run-code "async page => { const personId = 'tyler-000-0000-0000-000000000002'; const originalNickname = 'Ty'; const node = page.locator('#tree-svg [data-id=\"' + personId + '\"]').first(); await node.click(); await page.waitForFunction((id) => document.querySelector('[data-tree-sidebar-person-id]')?.getAttribute('data-tree-sidebar-person-id') === id, personId); await page.locator('button[data-tree-sidebar-tab=\"details\"]').click(); await page.locator('[data-tree-sidebar-panel=\"details\"]:not([hidden]) #tree-person-edit-form').waitFor(); const nickname = page.locator('#tree-person-edit-form input[name=\"nickname\"]'); const submit = page.locator('#tree-person-edit-form button[type=\"submit\"]'); await nickname.fill('Tree Captain'); await submit.click(); await page.waitForFunction(async ({ id, expected }) => { const resp = await fetch('/api/persons/' + id); const data = await resp.json(); return data.nickname === expected; }, { id: personId, expected: 'Tree Captain' }); await nickname.fill(originalNickname); await submit.click(); await page.waitForFunction(async ({ id, expected }) => { const resp = await fetch('/api/persons/' + id); const data = await resp.json(); return data.nickname === expected; }, { id: personId, expected: originalNickname }); const origin = page.url().split('/').slice(0, 3).join('/'); await page.goto(origin + '/tree?focus=' + personId); await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1200); }"

assert_run "tree media workspace uploads media without leaving the tree" \
  "${PWCLI}" run-code "async page => { await page.locator('button[data-tree-sidebar-tab=\"overview\"]').click(); await page.locator('[data-tree-sidebar-panel=\"overview\"]:not([hidden])').waitFor(); await page.locator('[data-tree-metric=\"media\"]').click(); await page.locator('[data-tree-sidebar-panel=\"media\"]:not([hidden])').waitFor(); const fileInput = page.locator('#tree-media-form input[type=\"file\"]'); await fileInput.setInputFiles('${ROOT_DIR}/app/static/demo-photos/portrait-carlos.jpg'); await page.locator('#tree-media-form input[name=\"caption\"]').fill('Tree upload'); await page.locator('#tree-media-form button[type=\"submit\"]').click(); const modal = page.locator('#media-upload-modal:not(.hidden)'); await modal.waitFor(); await modal.getByRole('button', { name: /Start upload/i }).click(); await page.locator('#media-upload-modal').waitFor({ state: 'hidden', timeout: 15000 }); const sidebarPid = await page.evaluate(() => document.querySelector('[data-tree-sidebar-person-id]')?.getAttribute('data-tree-sidebar-person-id') || ''); await page.locator('#tree-svg [data-id=\"' + sidebarPid + '\"]').first().click(); await page.waitForFunction((id) => document.querySelector('[data-tree-sidebar-person-id]')?.getAttribute('data-tree-sidebar-person-id') === id, sidebarPid, { timeout: 30000 }); await page.locator('button[data-tree-sidebar-tab=\"media\"]').click(); await page.locator('[data-tree-sidebar-panel=\"media\"]:not([hidden])').waitFor(); await page.waitForFunction(() => { const container = document.getElementById('tree-sidebar-media'); return container && container.getAttribute('aria-busy') !== 'true' && container.querySelector('.tree-sidebar-media-item'); }, null, { timeout: 30000 }); const text = await page.locator('#tree-sidebar-media').textContent(); if (!await page.locator('#tree-sidebar-media img').count()) throw new Error('tree media upload did not render'); if (!text || !text.includes('Tree upload')) throw new Error('tree media workspace did not show uploaded caption'); }"

assert_run "tree name preference hides fallback initials when names are off" \
  "${PWCLI}" run-code "async page => { await page.locator('#pref-show-names').uncheck(); await page.locator('#pref-show-photos').uncheck(); await page.locator('#save-tree-preferences').click(); await page.waitForTimeout(1200); const nodeText = await page.locator('#tree-svg [data-id=\"member-00-0000-0000-000000000005\"]').textContent(); if (nodeText && nodeText.includes('Ja')) throw new Error('fallback initials still visible when names are hidden'); }"

assert_run "tree nickname preference swaps node labels without changing canonical identity" \
  "${PWCLI}" run-code "async page => { await page.locator('#pref-show-names').check(); await page.locator('#pref-show-photos').check(); await page.locator('#pref-show-nicknames').check(); await page.locator('#save-tree-preferences').click(); await page.waitForTimeout(1200); const nodeLabel = await page.locator('#tree-svg [data-id=\"monica-000-0000-000000000014\"]').getAttribute('data-render-label'); if (nodeLabel !== 'Monica Branch') throw new Error('nickname preference did not preserve surname on node: ' + nodeLabel); await page.locator('#pref-show-nicknames').uncheck(); await page.locator('#save-tree-preferences').click(); await page.waitForTimeout(1200); }"

"${PWCLI}" goto "${BASE_URL}/people/new"
"${PWCLI}" run-code "async page => { await page.locator('#create-person-form').waitFor(); await page.locator('#person-first-name').fill('Playwright'); await page.locator('#person-last-name').fill('Relative'); await page.locator('#person-branch').fill('playwright'); await page.locator('#person-residence-place').fill('Lisbon'); await page.locator('#person-residence-country').fill('PT'); await page.locator('#person-contact-email').fill('playwright-relative@example.com'); await page.locator('#create-btn').click(); await page.waitForLoadState('networkidle'); }"
"${PWCLI}" run-code "async page => { await page.waitForURL(/\\/tree/); await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1200); const focusId = await page.evaluate(() => new window.URL(window.location.href).searchParams.get('focus')); if (!focusId) throw new Error('create flow did not redirect to tree with focus'); await page.evaluate((id) => { localStorage.setItem('playwrightRelativeId', id); }, focusId); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/person-created.png" --full-page true >/dev/null

assert_run "admin can create a new person from the browser flow" \
  "${PWCLI}" run-code "async page => { if (!page.url().includes('/tree')) throw new Error('create flow did not land on tree'); const focusId = await page.evaluate(() => new window.URL(window.location.href).searchParams.get('focus')); if (!focusId) throw new Error('create flow missing focus parameter'); }"

assert_run "tree focus recovery controls restore the focused person from URL context" \
  "${PWCLI}" run-code "async page => { const focusId = await page.evaluate(() => new window.URL(window.location.href).searchParams.get('focus')); if (!focusId) throw new Error('missing focus parameter'); await page.waitForTimeout(1200); const node = page.locator('#tree-svg [data-id=\"' + focusId + '\"]').first(); const box = await node.boundingBox(); if (!box) throw new Error('focused node not found after URL focus'); }"

"${PWCLI}" goto "${BASE_URL}/calendar?month=2026-03"
"${PWCLI}" run-code "async page => { await page.locator('#calendar-grid').waitFor(); await page.locator('#cal-upcoming-list .cal__upcoming-item').first().waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/calendar-hero.png" --full-page true >/dev/null

assert_run "calendar lands on the month surface before feed management" \
  "${PWCLI}" run-code "async page => { const grid = await page.locator('#calendar-grid').boundingBox(); if (!grid) throw new Error('calendar grid missing'); const viewport = page.viewportSize(); if (grid.y > viewport.height - 120) throw new Error('calendar grid rendered below the initial viewport'); if (await page.locator('#calendar-manager').isVisible()) throw new Error('calendar manager should be hidden by default'); const title = await page.locator('.calendar-page__title').textContent(); if (!title || !title.includes('Family Calendar')) throw new Error('calendar title missing'); }"

assert_run "calendar surfaces richer family-event labels in month discovery rails" \
  "${PWCLI}" run-code "async page => { const text = await page.locator('#calendar-grid').textContent(); if (!text || !text.includes('Tyler Martin turns 41')) throw new Error('birthday age label missing from calendar'); if (!text.includes('12th anniversary')) throw new Error('anniversary years label missing from calendar'); }"

assert_run "calendar manager groups feed actions and supports search plus copy" \
  "${PWCLI}" run-code "async page => { await page.evaluate(() => { Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: async (value) => { window.__calendarCopied = value; } } }); window.__calendarCopied = ''; }); await page.getByRole('button', { name: 'Manage Calendars' }).click(); await page.locator('#calendar-manager:not([hidden])').waitFor(); const managerText = await page.locator('#calendar-manager').textContent(); if (!managerText || !managerText.includes('Family overview') || !managerText.includes('Focused feed slices')) throw new Error('calendar manager missing grouped feed sections'); const search = page.locator('#calendar-feed-search'); await search.fill('clean recurring'); await page.waitForFunction(() => document.querySelectorAll('[data-feed-card]:not([hidden])').length === 1); const visibleCopy = page.locator('[data-feed-card]:not([hidden]) [data-calendar-copy-link]').first(); await visibleCopy.click(); await page.waitForFunction(() => !!window.__calendarCopied); const copied = await page.evaluate(() => window.__calendarCopied || ''); if (!copied.includes('/calendar/feed.ics?token=')) throw new Error('calendar copy action did not capture feed URL'); }"

assert_run "calendar holiday manager exposes preset layers separately from family feeds" \
  "${PWCLI}" run-code "async page => { await page.locator('[data-calendar-manager-close]').first().click(); await page.waitForFunction(() => document.getElementById('calendar-manager')?.hidden === true); await page.getByRole('button', { name: 'Add Holidays' }).click(); await page.locator('#calendar-manager:not([hidden])').waitFor(); const section = page.locator('#calendar-holidays'); await section.scrollIntoViewIfNeeded(); const text = await section.textContent(); if (!text || !text.includes('United States holidays')) throw new Error('holiday presets missing from manager'); if (!text.includes('Imported calendars')) throw new Error('holiday/import section missing enabled layers section'); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/calendar-manager.png" --full-page true >/dev/null
"${PWCLI}" run-code "async page => { await page.locator('[data-calendar-manager-close]').first().click(); await page.waitForFunction(() => document.getElementById('calendar-manager')?.hidden === true); }"

"${PWCLI}" goto "${BASE_URL}/wiki/tyler-martin"
"${PWCLI}" run-code "async page => { await page.locator('.wiki-infobox').waitFor(); await page.locator('.wiki-infobox__social-link').first().waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/wiki-person.png" --full-page true >/dev/null

assert_run "wiki infobox social links render visibly when social profiles exist" \
  "${PWCLI}" run-code "async page => { const links = page.locator('.wiki-infobox__social-link'); const count = await links.count(); if (count < 2) throw new Error('expected social links in wiki infobox'); for (let index = 0; index < count; index += 1) { const link = links.nth(index); const box = await link.boundingBox(); if (!box || box.width < 40 || box.height < 20) throw new Error('social link rendered with zero or tiny size'); const display = await link.evaluate((el) => getComputedStyle(el).display); if (display === 'none') throw new Error('social link hidden by styles'); } }"

"${PWCLI}" cookie-set locale es --domain 127.0.0.1 --path / --sameSite Lax >/dev/null
"${PWCLI}" goto "${BASE_URL}/tree"
"${PWCLI}" run-code "async page => { await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1200); await page.locator('#tree-svg [data-id=\"tyler-000-0000-0000-000000000002\"]').first().click(); await page.locator('button[data-tree-sidebar-tab=\"details\"]').click(); await page.locator('[data-tree-sidebar-panel=\"details\"]:not([hidden])').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/tree-es.png" --full-page true >/dev/null
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/tree-details-es.png" --full-page true >/dev/null

assert_run "tree quick edit details surface uses locale strings in Spanish" \
  "${PWCLI}" run-code "async page => { const panel = page.locator('[data-tree-sidebar-panel=\"details\"]'); const text = await panel.textContent(); const required = ['Edición rápida', 'Identidad', 'Apellido de Soltera/o', 'Correo Electrónico', 'Notas', 'Historia y notas']; for (const label of required) { if (!text || !text.includes(label)) throw new Error('missing Spanish tree details label: ' + label); } const forbidden = [/\\bIdentity\\b/, /\\bResearch Notes\\b/, /\\bBirth Last Name\\b/, /\\bStory & Notes\\b/]; for (const pattern of forbidden) { if (text && pattern.test(text)) throw new Error('tree details leaked English label: ' + pattern); } }"

"${PWCLI}" run-code "async page => { await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').click(); await page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])').waitFor(); const editButton = page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden]) button[onclick*=\"editTreeRelationship(\"]').first(); await editButton.waitFor(); await editButton.click(); await page.waitForFunction(() => { const shell = document.getElementById('tree-relationship-editor-shell'); return shell && !shell.classList.contains('hidden'); }); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/tree-relationship-editor-es.png" --full-page true >/dev/null

assert_run "tree relationship editor uses locale strings in Spanish" \
  "${PWCLI}" run-code "async page => { const panel = page.locator('[data-tree-sidebar-panel=\"relationships\"]'); const text = await panel.textContent(); const required = ['Editar relación', 'Persona relacionada actual', 'Guardar relación']; for (const label of required) { if (!text || !text.includes(label)) throw new Error('missing Spanish relationship editor label: ' + label); } const editor = panel.locator('[data-tree-relationship-edit-form]:not(.hidden)').first(); await editor.waitFor(); const placeholder = await editor.locator('input[name=\"source\"]').getAttribute('placeholder'); if (placeholder !== 'manual') throw new Error('Spanish relationship editor placeholder was not localized-safe: ' + placeholder); const relatedName = await page.locator('#tree-relationship-editor-related-name').textContent(); if (!relatedName || !relatedName.trim()) throw new Error('Spanish relationship editor did not show current related person'); const forbidden = [/\\bEdit relationship\\b/, /\\bSave relationship\\b/]; for (const pattern of forbidden) { if (text && pattern.test(text)) throw new Error('relationship editor leaked English label: ' + pattern); } await editor.getByRole('button', { name: /Cancelar|Cancel/ }).click(); await page.waitForFunction(() => document.getElementById('tree-relationship-editor-shell')?.classList.contains('hidden')); }"

"${PWCLI}" goto "${BASE_URL}/people/${TYLER_ID}/edit"
"${PWCLI}" run-code "async page => { await page.locator('#person-edit-form').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/person-edit-es.png" --full-page true >/dev/null

assert_run "person edit surface uses locale strings for social and date controls" \
  "${PWCLI}" run-code "async page => { const formText = await page.locator('#person-edit-form').textContent(); const required = ['Contacto y Presencia', 'Redes Sociales', 'Apodo Principal', 'Otros Apodos']; for (const label of required) { if (!formText || !formText.includes(label)) throw new Error('person edit missing Spanish label: ' + label); } const birthInput = page.locator('#edit-birth-date-text'); await birthInput.waitFor(); const placeholder = await birthInput.getAttribute('placeholder'); if (!placeholder || !placeholder.includes('1985')) throw new Error('birth date unified input missing Spanish placeholder'); const calBtn = page.locator('.date-input-unified__picker-btn').first(); const calTitle = await calBtn.getAttribute('title'); if (calTitle !== 'Calendario') throw new Error('calendar button title not Spanish: ' + calTitle); const html = await page.content(); if (!html.includes('Sugerencias de lugares')) throw new Error('place suggestions label was not localized to Spanish in rendered page'); }"

"${PWCLI}" goto "${BASE_URL}/calendar?month=2026-03"
"${PWCLI}" run-code "async page => { await page.locator('#calendar-grid').waitFor(); await page.locator('#cal-upcoming-list').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/calendar-es.png" --full-page true >/dev/null

assert_run "calendar surface uses locale strings in Spanish" \
  "${PWCLI}" run-code "async page => { const gridText = await page.locator('#calendar-grid').textContent(); if (!gridText || !gridText.includes('12 años')) throw new Error('calendar anniversary copy did not localize to Spanish'); await page.getByRole('button', { name: 'Gestionar calendarios' }).click(); await page.locator('#calendar-manager:not([hidden])').waitFor(); const managerText = await page.locator('#calendar-manager').textContent(); if (!managerText || !managerText.includes('Cerrar')) throw new Error('calendar manager close label not localized to Spanish'); if (managerText.includes('common.close')) throw new Error('calendar manager leaked raw close i18n key'); await page.locator('[data-calendar-manager-close]').first().click(); await page.waitForFunction(() => document.getElementById('calendar-manager')?.hidden === true); }"

"${PWCLI}" cookie-set locale en --domain 127.0.0.1 --path / --sameSite Lax >/dev/null

# Auto-accept confirm dialogs for relationship tests that trigger browser prompts
"${PWCLI}" run-code "async page => { page.on('dialog', dialog => dialog.accept()); }"

"${PWCLI}" goto "${BASE_URL}/tree"
"${PWCLI}" run-code "async page => { await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1200); const node = page.locator('#tree-svg [data-id=\"tyler-000-0000-0000-000000000002\"]').first(); await node.click(); await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').waitFor(); }"
"${PWCLI}" run-code "async page => { await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').click(); await page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])').waitFor(); const editButton = page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden]) button[onclick*=\"editTreeRelationship(\"]').first(); await editButton.waitFor(); await editButton.click(); await page.waitForFunction(() => { const shell = document.getElementById('tree-relationship-editor-shell'); return shell && !shell.classList.contains('hidden'); }); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/tree-relationship-editor-admin.png" --full-page true >/dev/null

assert_run "tree relationship editor prefills current metadata on desktop" \
  "${PWCLI}" run-code "async page => { const editor = page.locator('[data-tree-relationship-edit-form]:not(.hidden)').first(); await editor.waitFor(); const relId = await editor.locator('input[name=\"relationship_id\"]').inputValue(); const type = await editor.locator('input[name=\"relationship_type\"]').inputValue(); const related = await page.locator('#tree-relationship-editor-related-name').textContent(); const sourcePlaceholder = await editor.locator('input[name=\"source\"]').getAttribute('placeholder'); if (!relId) throw new Error('relationship editor missing relationship id'); if (!type) throw new Error('relationship editor missing relationship type'); if (!related || !related.trim()) throw new Error('related person summary missing in editor'); if (sourcePlaceholder !== 'manual') throw new Error('unexpected source placeholder in editor: ' + sourcePlaceholder); const kindSelect = editor.locator('select[name=\"kind\"]'); if (await kindSelect.count()) { const kind = await kindSelect.inputValue(); if (!kind) throw new Error('relationship kind was not prefilled'); } const confidenceSelect = editor.locator('select[name=\"confidence\"]'); if (await confidenceSelect.count()) { const confidence = await confidenceSelect.inputValue(); if (!confidence) throw new Error('relationship confidence was not prefilled'); } await editor.getByRole('button', { name: /Cancel|Cancelar/ }).click(); await page.waitForFunction(() => document.getElementById('tree-relationship-editor-shell')?.classList.contains('hidden')); }"

assert_run "tree relationships support direct graph linking from the canvas" \
  "${PWCLI}" run-code "async page => { await page.evaluate(() => { window.confirm = () => true; }); await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').click(); await page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])').waitFor(); const childCard = page.locator('[data-tree-relationship-card=\"child\"]').first(); await childCard.getByRole('button', { name: 'Pick on tree' }).click(); await page.locator('#tree-graph-mode-banner:not(.hidden)').waitFor(); const bannerText = await page.locator('#tree-graph-mode-description').textContent(); if (!bannerText || !bannerText.includes('child')) throw new Error('graph mode prompt missing'); await page.locator('#tree-svg [data-id=\"member-00-0000-0000-000000000005\"]').first().click(); await page.waitForTimeout(1400); const relCard = page.locator('.tree-related-card', { hasText: 'Jane Martin' }).first(); if (!await relCard.count()) throw new Error('graph relationship link did not persist'); }"

assert_run "tree relationships can create and replace relatives in one workspace flow" \
  "${PWCLI}" run-code "async page => { const tylerId = 'tyler-000-0000-0000-000000000002'; const relativeId = await page.evaluate(() => localStorage.getItem('playwrightRelativeId')); if (!relativeId) throw new Error('missing stored relative id'); const origin = page.url().split('/').slice(0, 3).join('/'); await page.goto(origin + '/tree'); await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1200); await page.evaluate(() => { window.confirm = () => true; }); await page.locator('#tree-svg [data-id=\"' + tylerId + '\"]').first().click(); await page.waitForFunction((id) => document.querySelector('[data-tree-sidebar-person-id]')?.getAttribute('data-tree-sidebar-person-id') === id, tylerId, { timeout: 30000 }); await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').click(); const panel = page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])'); await panel.waitFor(); await page.waitForFunction(() => { const panelEl = document.querySelector('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])'); return panelEl && panelEl.textContent.includes('Jane Martin'); }, null, { timeout: 30000 }); const childCard = panel.locator('[data-tree-relationship-card=\"child\"]').first(); await childCard.getByRole('button', { name: 'Create and connect' }).click(); const createForm = panel.locator('details[data-tree-relationship-group=\"child\"][open] [data-tree-create-form=\"child\"]').first(); await createForm.locator('input[name=\"first_name\"]').waitFor({ state: 'visible' }); await createForm.locator('input[name=\"first_name\"]').fill('Graph'); await createForm.locator('input[name=\"last_name\"]').fill('Kid'); await createForm.locator('button[type=\"submit\"]').click(); await page.waitForFunction(() => { const panelEl = document.querySelector('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])'); return panelEl && panelEl.textContent.includes('Graph Kid'); }, null, { timeout: 30000 }); const graphKid = panel.locator('.tree-related-card', { hasText: 'Graph Kid' }).first(); await graphKid.scrollIntoViewIfNeeded(); await graphKid.getByRole('button', { name: 'Replace on tree' }).click(); await page.locator('#tree-graph-mode-banner:not(.hidden)').waitFor(); await page.locator('#tree-svg [data-id=\"' + relativeId + '\"]').first().click(); await page.waitForFunction(() => { const panelEl = document.querySelector('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])'); return panelEl && panelEl.textContent.includes('Playwright Relative') && !panelEl.textContent.includes('Graph Kid'); }, null, { timeout: 30000 }); }"

assert_run "tree relationship forms support edit and reversal corrections" \
  "${PWCLI}" run-code "async page => { await page.evaluate(() => { window.confirm = () => true; }); const tylerId = 'tyler-000-0000-0000-000000000002'; const origin = page.url().split('/').slice(0, 3).join('/'); const suffix = String(Date.now()).slice(-6); const adoptiveFirst = 'Adoptive' + suffix; const adoptiveLast = 'Sprout'; const adoptiveDisplay = adoptiveFirst + ' ' + adoptiveLast; const partnerFirst = 'Former' + suffix; const partnerLast = 'Flame'; const partnerDisplay = partnerFirst + ' ' + partnerLast; const pollTreeFor = async (matcher, timeoutMs = 30000) => { const deadline = Date.now() + timeoutMs; while (Date.now() < deadline) { const data = await page.evaluate(async () => { const resp = await fetch('/api/tree', { cache: 'no-store' }); return await resp.json(); }); const match = matcher(data); if (match) return match; await page.waitForTimeout(250); } return null; }; await page.goto(origin + '/tree?focus=' + tylerId); await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(1200); await page.locator('#tree-svg [data-id=\"' + tylerId + '\"]').first().click(); await page.waitForFunction((id) => document.querySelector('[data-tree-sidebar-person-id]')?.getAttribute('data-tree-sidebar-person-id') === id, tylerId); await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').click(); const panel = page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])'); await panel.waitFor(); const childCard = panel.locator('[data-tree-relationship-card=\"child\"]').first(); await childCard.getByRole('button', { name: 'Create and connect' }).click(); const childCreate = panel.locator('details[data-tree-relationship-group=\"child\"][open] [data-tree-create-form=\"child\"]').first(); await childCreate.locator('input[name=\"first_name\"]').waitFor({ state: 'visible' }); await childCreate.locator('input[name=\"first_name\"]').fill(adoptiveFirst); await childCreate.locator('input[name=\"last_name\"]').fill(adoptiveLast); await childCreate.locator('select[name=\"kind\"]').waitFor({ state: 'visible' }); await childCreate.locator('select[name=\"kind\"]').selectOption('adoptive'); await childCreate.evaluate(async (form, personId) => { var kindSel = form.querySelector('select[name=\"kind\"]'); if (kindSel) { kindSel.value = 'adoptive'; kindSel.dispatchEvent(new Event('input', { bubbles: true })); kindSel.dispatchEvent(new Event('change', { bubbles: true })); } await window.createTreeRelative({ preventDefault() {}, target: form }, personId, 'child'); }, tylerId); const adoptiveRel = await pollTreeFor((data) => { const person = (data.persons || []).find((entry) => entry.display_name === adoptiveDisplay); if (!person) return null; const rel = (data.parent_child || []).find((entry) => entry.parent_id === tylerId && entry.child_id === person.id && entry.kind === 'adoptive'); return rel ? { relId: rel.id, personId: person.id } : null; }); if (!adoptiveRel || !adoptiveRel.relId) throw new Error('tree child create form did not persist adoptive kind'); await page.waitForFunction((displayName) => { const panelEl = document.querySelector('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])'); return panelEl && panelEl.textContent.includes(displayName); }, adoptiveDisplay); const adoptiveCard = panel.locator('.tree-related-card', { hasText: adoptiveDisplay }).first(); await adoptiveCard.getByRole('button', { name: 'Edit relationship' }).click(); await page.waitForFunction(() => { const shell = document.getElementById('tree-relationship-editor-shell'); return shell && !shell.classList.contains('hidden'); }); const childEditor = panel.locator('[data-tree-relationship-edit-form=\"child\"]:not(.hidden)').first(); await childEditor.locator('select[name=\"confidence\"]').selectOption('probable'); await childEditor.locator('input[name=\"source_detail\"]').fill('Corrected from tree test'); await childEditor.locator('textarea[name=\"notes\"]').fill('Initial direction captured for later correction'); await childEditor.getByRole('button', { name: 'Save relationship' }).click(); const updatedRel = await pollTreeFor((data) => { const rel = (data.parent_child || []).find((entry) => entry.id === adoptiveRel.relId); return rel && rel.confidence === 'probable' && rel.source_detail === 'Corrected from tree test' && rel.notes === 'Initial direction captured for later correction' ? rel : null; }); if (!updatedRel) throw new Error('tree relationship editor did not persist child metadata'); await adoptiveCard.getByRole('button', { name: 'Edit relationship' }).click(); const reverseEditor = panel.locator('[data-tree-relationship-edit-form=\"child\"]:not(.hidden)').first(); await reverseEditor.evaluate((form) => { window.confirm = () => true; return window.reverseTreeRelationshipEdit(form); }); const reversedRel = await pollTreeFor((data) => { const rel = (data.parent_child || []).find((entry) => entry.id === adoptiveRel.relId); return rel && rel.child_id === tylerId && rel.parent_id === adoptiveRel.personId ? rel : null; }); if (!reversedRel) throw new Error('tree relationship reverse did not persist corrected direction'); await page.waitForFunction((displayName) => { const panelEl = document.querySelector('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])'); return panelEl && panelEl.textContent.includes(displayName); }, adoptiveDisplay); const adoptiveDelete = await page.evaluate(async (relId) => { const resp = await fetch('/api/relationships/parent-child/' + relId, { method: 'DELETE' }); return resp.status; }, adoptiveRel.relId); if (adoptiveDelete !== 204) throw new Error('failed to delete reversed adoptive relationship'); const partnerCard = panel.locator('[data-tree-relationship-card=\"partner\"]').first(); await partnerCard.getByRole('button', { name: 'Create and connect' }).click(); const partnerCreate = panel.locator('details[data-tree-relationship-group=\"partner\"][open] [data-tree-create-form=\"partner\"]').first(); await partnerCreate.locator('input[name=\"first_name\"]').waitFor({ state: 'visible' }); await partnerCreate.locator('input[name=\"first_name\"]').fill(partnerFirst); await partnerCreate.locator('input[name=\"last_name\"]').fill(partnerLast); await partnerCreate.locator('select[name=\"kind\"]').waitFor({ state: 'visible' }); await partnerCreate.locator('select[name=\"kind\"]').selectOption('domestic_partner'); await partnerCreate.locator('select[name=\"status\"]').selectOption('separated'); await partnerCreate.evaluate(async (form, personId) => { var kindSel = form.querySelector('select[name=\"kind\"]'); var statusSel = form.querySelector('select[name=\"status\"]'); if (kindSel) { kindSel.value = 'domestic_partner'; kindSel.dispatchEvent(new Event('input', { bubbles: true })); kindSel.dispatchEvent(new Event('change', { bubbles: true })); } if (statusSel) { statusSel.value = 'separated'; statusSel.dispatchEvent(new Event('input', { bubbles: true })); statusSel.dispatchEvent(new Event('change', { bubbles: true })); } await window.createTreeRelative({ preventDefault() {}, target: form }, personId, 'partner'); }, tylerId); const partnerRel = await page.waitForFunction(async ({ sourceId, displayName }) => { const resp = await fetch('/api/tree'); const data = await resp.json(); const person = (data.persons || []).find((entry) => entry.display_name === displayName); if (!person) return null; const rel = (data.partnerships || []).find((entry) => ((entry.person_a_id === sourceId && entry.person_b_id === person.id) || (entry.person_b_id === sourceId && entry.person_a_id === person.id)) && entry.kind === 'domestic_partner' && entry.status === 'separated'); return rel ? { relId: rel.id, personId: person.id } : null; }, { sourceId: tylerId, displayName: partnerDisplay }).then((handle) => handle.jsonValue()); if (!partnerRel || !partnerRel.relId) throw new Error('tree partner create form did not persist partnership status'); await page.waitForFunction((displayName) => { const panelEl = document.querySelector('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])'); return panelEl && panelEl.textContent.includes(displayName); }, partnerDisplay); const partnerRelCard = panel.locator('.tree-related-card', { hasText: partnerDisplay }).first(); await partnerRelCard.getByRole('button', { name: 'Edit relationship' }).click(); const partnerEditor = panel.locator('[data-tree-relationship-edit-form=\"partner\"]:not(.hidden)').first(); await partnerEditor.locator('select[name=\"kind\"]').selectOption('co_parent'); await partnerEditor.locator('select[name=\"status\"]').selectOption('dissolved'); await partnerEditor.locator('textarea[name=\"notes\"]').fill('Updated through relationship editor'); await partnerEditor.getByRole('button', { name: 'Save relationship' }).click(); await page.waitForFunction(async (relId) => { const resp = await fetch('/api/tree'); const data = await resp.json(); const rel = (data.partnerships || []).find((entry) => entry.id === relId); return rel && rel.kind === 'co_parent' && rel.status === 'dissolved' && rel.notes === 'Updated through relationship editor'; }, partnerRel.relId); const partnerDelete = await page.evaluate(async (relId) => { const resp = await fetch('/api/relationships/partnership/' + relId, { method: 'DELETE' }); return resp.status; }, partnerRel.relId); if (partnerDelete !== 204) throw new Error('failed to delete partnership relationship'); }"

assert_run "tree relationship cards support guarded removal after graph edits" \
  "${PWCLI}" run-code "async page => { await page.evaluate(() => { window.confirm = () => true; }); const tylerId = 'tyler-000-0000-0000-000000000002'; await page.locator('#tree-svg [data-id=\"' + tylerId + '\"]').first().click(); await page.waitForFunction((id) => document.querySelector('[data-tree-sidebar-person-id]')?.getAttribute('data-tree-sidebar-person-id') === id, tylerId, { timeout: 30000 }); await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').click(); const panel = page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])'); await panel.waitFor(); await page.waitForFunction(() => { const panelEl = document.querySelector('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])'); return panelEl && panelEl.textContent.includes('Playwright Relative'); }, null, { timeout: 30000 }); const removeButton = panel.locator('.tree-related-card', { hasText: 'Playwright Relative' }).first().getByRole('button', { name: 'Remove link' }); await removeButton.waitFor(); await removeButton.click(); await page.waitForFunction(() => { const panelEl = document.querySelector('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])'); return panelEl && !panelEl.textContent.includes('Playwright Relative'); }, null, { timeout: 30000 }); }"

"${PWCLI}" goto "${BASE_URL}/admin"
"${PWCLI}" run-code "async page => { await page.locator('#admin-page').waitFor(); await page.locator('#backup-status').getByText('Protected fields').waitFor(); await page.locator('#theme-settings-form').waitFor(); await page.locator('#admin-accounts-card').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/admin-dashboard.png" --full-page true >/dev/null

assert_run "admin dashboard exposes backup status and theme controls" \
  "${PWCLI}" run-code "async page => { const text = await page.locator('#backup-status').textContent(); if (!text || !text.includes('Protected fields')) throw new Error('backup status missing'); if (!await page.locator('#theme-settings-form').count()) throw new Error('theme form missing'); }"

"${PWCLI}" resize 390 844
"${PWCLI}" goto "${BASE_URL}/calendar?month=2026-03"
"${PWCLI}" run-code "async page => { await page.locator('#calendar-grid').waitFor(); await page.locator('#cal-list').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/calendar-mobile.png" --full-page true >/dev/null

assert_run "calendar mobile view uses agenda fallback without overflow" \
  "${PWCLI}" run-code "async page => { const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth); if (overflow > 4) throw new Error('calendar page overflows horizontally on mobile'); const listVisible = await page.locator('#cal-list').evaluate((el) => getComputedStyle(el).display !== 'none'); const gridVisible = await page.locator('.cal__grid').evaluate((el) => getComputedStyle(el).display !== 'none'); if (!listVisible || gridVisible) throw new Error('calendar mobile view did not use agenda fallback'); const managerBtn = await page.getByRole('button', { name: 'Manage Calendars' }).boundingBox(); if (!managerBtn) throw new Error('calendar manager button missing on mobile'); }"

"${PWCLI}" goto "${BASE_URL}/admin"
"${PWCLI}" run-code "async page => { await page.locator('#admin-page').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/admin-mobile.png" --full-page true >/dev/null

assert_run "admin dashboard avoids horizontal overflow on mobile" \
  "${PWCLI}" run-code "async page => { const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth); if (overflow > 4) throw new Error('admin page overflows horizontally on mobile'); }"

"${PWCLI}" goto "${BASE_URL}/"
"${PWCLI}" run-code "async page => { await page.waitForURL(/\\/tree$/); await page.locator('#tree-svg').waitFor(); await page.waitForTimeout(800); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/tree-mobile.png" --full-page true >/dev/null

assert_run "tree landing avoids horizontal overflow on mobile" \
  "${PWCLI}" run-code "async page => { const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth); if (overflow > 4) throw new Error('tree page overflows horizontally on mobile'); }"

"${PWCLI}" run-code "async page => { const tylerId = 'tyler-000-0000-0000-000000000002'; await page.locator('#tree-svg [data-id=\"' + tylerId + '\"]').first().click(); await page.waitForFunction((id) => document.querySelector('[data-tree-sidebar-person-id]')?.getAttribute('data-tree-sidebar-person-id') === id, tylerId); await page.locator('button[data-tree-sidebar-tab=\"relationships\"]').click(); await page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden])').waitFor(); const editButton = page.locator('[data-tree-sidebar-panel=\"relationships\"]:not([hidden]) button[onclick*=\"editTreeRelationship(\"]').first(); await editButton.scrollIntoViewIfNeeded(); await editButton.click(); await page.waitForFunction(() => { const shell = document.getElementById('tree-relationship-editor-shell'); return shell && !shell.classList.contains('hidden'); }); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/tree-relationship-editor-mobile.png" --full-page true >/dev/null

assert_run "tree relationship editor stays reachable on mobile" \
  "${PWCLI}" run-code "async page => { const viewport = page.viewportSize(); const editor = page.locator('[data-tree-relationship-edit-form]:not(.hidden)').first(); await editor.waitFor(); const actions = editor.locator('.tree-sidebar-inline-actions button'); const count = await actions.count(); if (count < 3) throw new Error('missing mobile correction actions'); for (let index = 0; index < count; index += 1) { const box = await actions.nth(index).boundingBox(); if (!box) throw new Error('mobile correction action hidden at index ' + index); if (box.x < 0 || box.x + box.width > viewport.width + 2) throw new Error('mobile correction action clipped horizontally'); } await editor.getByRole('button', { name: /Cancel|Cancelar/ }).click(); await page.waitForFunction(() => document.getElementById('tree-relationship-editor-shell')?.classList.contains('hidden')); }"

"${PWCLI}" goto "${BASE_URL}/people/new"
"${PWCLI}" run-code "async page => { await page.locator('#create-person-form').waitFor(); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/person-new-mobile.png" --full-page true >/dev/null

assert_run "person create form stacks and avoids horizontal overflow on mobile" \
  "${PWCLI}" run-code "async page => { const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth); if (overflow > 4) throw new Error('person create form overflows horizontally on mobile'); const place = await page.locator('#person-burial-place').boundingBox(); const cemetery = await page.locator('#person-burial-cemetery').boundingBox(); if (!place || !cemetery) throw new Error('missing burial fields'); if (Math.abs(place.y - cemetery.y) < 20) throw new Error('burial fields did not stack on mobile'); }"

"${PWCLI}" goto "${BASE_URL}/people/tyler-000-0000-0000-000000000002/edit"
"${PWCLI}" run-code "async page => { await page.locator('#person-edit-form').waitFor(); await page.locator('#edit-is-living').uncheck(); await page.waitForFunction(() => document.getElementById('memorial-section')?.hidden === false); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/person-edit-mobile.png" --full-page true >/dev/null

assert_run "person edit mobile keeps address and memorial controls reachable" \
  "${PWCLI}" run-code "async page => { const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth); if (overflow > 4) throw new Error('person edit overflows horizontally on mobile'); const viewport = page.viewportSize(); const addAddress = await page.getByRole('button', { name: 'Add Address' }).boundingBox(); const nicknameInput = await page.locator('#nickname-search').boundingBox(); const memorial = await page.locator('#memorial-section').boundingBox(); if (!addAddress || !nicknameInput || !memorial) throw new Error('person edit mobile controls missing'); if (addAddress.x < 0 || addAddress.x + addAddress.width > viewport.width + 2) throw new Error('add-address action clipped on mobile'); }"

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

"${PWCLI}" goto "${BASE_URL}/people/new"
assert_run "new person form exposes place-capture affordances" \
  "${PWCLI}" run-code "async page => { const groups = await page.locator('[data-place-field]').count(); const hints = await page.locator('[data-place-status]').count(); if (groups < 3 || hints < 3) throw new Error('place affordances missing from create form'); }"

"${PWCLI}" goto "${BASE_URL}/people/tyler-000-0000-0000-000000000002/edit"
assert_run "edit person form exposes coordinate-backed place fields" \
  "${PWCLI}" run-code "async page => { await page.locator('#edit-residence-place').waitFor(); if (!await page.locator('input[name=\"residence_place_latitude\"]').count()) throw new Error('missing residence coordinate field'); if (!await page.locator('[data-place-status]').count()) throw new Error('missing place status hint'); }"

assert_run "changing country after place verification clears stale coordinates" \
  "${PWCLI}" run-code "async page => { const latitude = page.locator('input[name=\"residence_place_latitude\"]'); const longitude = page.locator('input[name=\"residence_place_longitude\"]'); await latitude.evaluate((el) => { el.value = '43.6532'; }); await longitude.evaluate((el) => { el.value = '-79.3832'; }); const country = page.locator('#edit-residence-country'); await country.evaluate((el) => { el.value = 'us'; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); }); await page.waitForFunction(() => { const lat = document.querySelector('input[name=\"residence_place_latitude\"]'); const lng = document.querySelector('input[name=\"residence_place_longitude\"]'); const countryInput = document.querySelector('#edit-residence-country'); return lat && lng && countryInput && lat.value === '' && lng.value === '' && countryInput.value === 'US'; }); }"

assert_run "new places autocomplete populates country and coordinates from a suggestion" \
  "${PWCLI}" run-code "async page => { await page.evaluate(() => { const group = document.querySelector('#edit-residence-place').closest('[data-place-field]'); if (!group) throw new Error('missing residence place group'); delete group.dataset.locationBound; group.querySelectorAll('.place-autocomplete-suggestions').forEach((node) => node.remove()); let fetchFieldCalls = 0; const fakePlaces = { AutocompleteSessionToken: function() {}, AutocompleteSuggestion: { fetchAutocompleteSuggestions: async ({ input }) => ({ suggestions: safeText(input).toLowerCase().startsWith('tor') ? [{ placePrediction: { text: { toString() { return 'Toronto, ON, Canada'; } }, toPlace() { const place = { fetchFields: async () => { fetchFieldCalls += 1; place.formattedAddress = 'Toronto, ON, Canada'; place.location = { lat: () => 43.6532, lng: () => -79.3832 }; place.addressComponents = [{ types: ['country'], shortText: 'CA' }]; } }; return place; } } }] : [] }) } }; window.google = { maps: { importLibrary: async (name) => { if (name !== 'places') throw new Error('unexpected library ' + name); return fakePlaces; } } }; window.__placeFetchFieldCalls = () => fetchFieldCalls; window.familyBookLocations.init(document, { apiKey: 'fake-browser-key', hasGoogle: true, manualHint: 'Manual', configuredHint: 'Lookup', verifiedHint: 'Verified', failedHint: 'Failed', suggestionsLabel: 'Place suggestions' }); function safeText(value) { return typeof value === 'string' ? value.trim() : ''; } }); const input = page.locator('#edit-residence-place'); await input.fill('Tor'); await page.waitForSelector('.place-autocomplete-suggestions:not([hidden]) .place-autocomplete-suggestion'); const listLabel = await page.locator('.place-autocomplete-suggestions').first().getAttribute('aria-label'); if (listLabel !== 'Place suggestions') throw new Error('place suggestions aria-label missing on English surface: ' + listLabel); await page.locator('.place-autocomplete-suggestion').first().click(); await page.waitForFunction(() => { const place = document.querySelector('#edit-residence-place'); const country = document.querySelector('#edit-residence-country'); const lat = document.querySelector('input[name=\"residence_place_latitude\"]'); const lng = document.querySelector('input[name=\"residence_place_longitude\"]'); return place && country && lat && lng && place.value === 'Toronto, ON, Canada' && country.value === 'CA' && lat.value === '43.6532' && lng.value === '-79.3832'; }); const fetchCalls = await page.evaluate(() => window.__placeFetchFieldCalls()); if (fetchCalls < 1) throw new Error('new places autocomplete never fetched place fields'); }"

assert_run "person edit supports nickname chips, typed addresses, and respectful memorial disclosure" \
  "${PWCLI}" run-code "async page => { await page.locator('#nickname-search').fill('Ace'); await page.keyboard.press('Enter'); await page.waitForFunction(() => document.getElementById('nickname-hidden')?.value.includes('Ace')); await page.getByRole('button', { name: 'Add Address' }).click(); const cards = page.locator('#contact-address-list .person-edit-address-card'); await cards.last().waitFor(); await cards.last().locator('select[data-address-key=\"type\"]').selectOption('work'); await cards.last().locator('input[data-address-key=\"label\"]').fill('Studio'); await cards.last().locator('input[data-address-key=\"line1\"]').fill('123 Main St'); await cards.last().locator('input[data-address-key=\"city\"]').fill('Toronto'); await cards.last().locator('input[data-address-key=\"state\"]').fill('ON'); await cards.last().locator('input[data-address-key=\"postal_code\"]').fill('M5V 2T6'); await cards.last().locator('input[data-address-key=\"country\"]').fill('Canada'); await page.waitForFunction(() => { const hidden = document.getElementById('contact-addresses-hidden'); if (!hidden) return false; const entries = JSON.parse(hidden.value || '[]'); return entries.length === 1 && entries[0].type === 'work' && entries[0].label === 'Studio' && entries[0].line1 === '123 Main St' && entries[0].city === 'Toronto' && entries[0].state === 'ON' && entries[0].postal_code === 'M5V 2T6' && entries[0].country === 'Canada'; }); if (!await page.locator('#memorial-section').evaluate((el) => el.hidden)) throw new Error('memorial section should start hidden for living person'); await page.locator('#edit-is-living').uncheck(); await page.waitForFunction(() => document.getElementById('memorial-section')?.hidden === false); await page.locator('#edit-remains-disposition').selectOption('cremated'); await page.waitForFunction(() => document.getElementById('burial-site-details')?.hidden === true); const burialInputs = await page.locator('#burial-site-details input:disabled').count(); if (burialInputs < 2) throw new Error('burial site inputs were not disabled when cremated'); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/person-edit-admin.png" --full-page true >/dev/null

# ── Multi-value contact and structured address editing tests ──

"${PWCLI}" goto "${BASE_URL}/people/tyler-000-0000-0000-000000000002/edit"
"${PWCLI}" run-code "async page => { await page.locator('#person-edit-form').waitFor(); }"

assert_run "person edit phone card add/remove and primary toggle" \
  "${PWCLI}" run-code "async page => { await page.getByRole('button', { name: 'Add Phone' }).click(); await page.getByRole('button', { name: 'Add Phone' }).click(); const cards = page.locator('#phone-list .person-edit-address-card'); if (await cards.count() !== 2) throw new Error('expected 2 phone cards, got ' + await cards.count()); await cards.first().locator('input[data-card-key=\"number\"]').fill('+1 555 123 4567'); await cards.first().locator('select[data-card-key=\"type\"]').selectOption('mobile'); await cards.nth(1).locator('input[data-card-key=\"number\"]').fill('+1 555 987 6543'); await cards.nth(1).locator('select[data-card-key=\"type\"]').selectOption('work'); await cards.nth(1).locator('input[name=\"phone_primary\"]').click(); const phonesRaw = await page.locator('#phones-hidden').inputValue(); const phones = JSON.parse(phonesRaw); if (phones.length !== 2) throw new Error('expected 2 phones in hidden, got ' + phones.length); if (phones[0].is_primary !== false) throw new Error('first phone should not be primary after clicking second'); if (phones[1].is_primary !== true) throw new Error('second phone should be primary'); await page.locator('#phone-list .person-edit-address-card').first().locator('button.btn--ghost').click(); const afterRemove = JSON.parse(await page.locator('#phones-hidden').inputValue()); if (afterRemove.length !== 1) throw new Error('expected 1 phone after remove, got ' + afterRemove.length); if (afterRemove[0].number !== '+1 555 987 6543') throw new Error('wrong phone survived removal'); }"

assert_run "person edit email card add/remove and primary toggle" \
  "${PWCLI}" run-code "async page => { await page.getByRole('button', { name: 'Add Email' }).click(); const cards = page.locator('#email-list .person-edit-address-card'); await cards.first().locator('input[data-card-key=\"address\"]').fill('tyler@example.com'); await cards.first().locator('select[data-card-key=\"type\"]').selectOption('personal'); const emailsRaw = await page.locator('#emails-hidden').inputValue(); const emails = JSON.parse(emailsRaw); if (emails.length !== 1) throw new Error('expected 1 email'); if (emails[0].address !== 'tyler@example.com') throw new Error('email address mismatch'); if (emails[0].is_primary !== true) throw new Error('first email should be auto-primary'); }"

assert_run "person edit social account card add/remove" \
  "${PWCLI}" run-code "async page => { await page.getByRole('button', { name: 'Add Account' }).click(); await page.getByRole('button', { name: 'Add Account' }).click(); const cards = page.locator('#social-list .person-edit-address-card'); if (await cards.count() < 2) throw new Error('expected at least 2 social cards'); await cards.first().locator('select[data-card-key=\"platform\"]').selectOption('twitter'); await cards.first().locator('input[data-card-key=\"url\"]').fill('@tylermartin'); await cards.nth(1).locator('select[data-card-key=\"platform\"]').selectOption('linkedin'); await cards.nth(1).locator('input[data-card-key=\"url\"]').fill('https://linkedin.com/in/tylermartin'); const socialRaw = await page.locator('#social-hidden').inputValue(); const socials = JSON.parse(socialRaw); if (socials.length < 2) throw new Error('expected at least 2 social accounts'); if (socials[0].platform !== 'twitter') throw new Error('platform mismatch'); await cards.first().locator('button.btn--ghost').click(); const afterRemove = JSON.parse(await page.locator('#social-hidden').inputValue()); if (afterRemove.length < 1) throw new Error('expected at least 1 social after remove'); if (afterRemove[0].platform !== 'linkedin') throw new Error('wrong social survived removal'); }"

assert_run "person edit name history card add/remove" \
  "${PWCLI}" run-code "async page => { await page.getByRole('button', { name: 'Add Name Change' }).click(); const cards = page.locator('#name-history-list .person-edit-address-card'); await cards.first().locator('input[data-card-key=\"surname\"]').fill('Smith'); await cards.first().locator('select[data-card-key=\"reason\"]').selectOption('marriage'); await cards.first().locator('input[data-card-key=\"year\"]').fill('2015'); const historyRaw = await page.locator('#name-history-hidden').inputValue(); const history = JSON.parse(historyRaw); if (history.length !== 1) throw new Error('expected 1 name history entry'); if (history[0].surname !== 'Smith' || history[0].reason !== 'marriage' || history[0].year !== '2015') throw new Error('name history data mismatch'); }"

assert_run "person edit structured address captures all subfields" \
  "${PWCLI}" run-code "async page => { const existingCards = await page.locator('#contact-address-list .person-edit-address-card').count(); await page.getByRole('button', { name: 'Add Address' }).click(); const cards = page.locator('#contact-address-list .person-edit-address-card'); const newCard = cards.nth(existingCards); await newCard.waitFor(); await newCard.locator('select[data-address-key=\"type\"]').selectOption('residential'); await newCard.locator('input[data-address-key=\"line1\"]').fill('456 Oak Ave'); await newCard.locator('input[data-address-key=\"line2\"]').fill('Apt 2B'); await newCard.locator('input[data-address-key=\"city\"]').fill('Chicago'); await newCard.locator('input[data-address-key=\"state\"]').fill('IL'); await newCard.locator('input[data-address-key=\"postal_code\"]').fill('60601'); await newCard.locator('input[data-address-key=\"country\"]').fill('United States'); await page.waitForFunction((idx) => { const hidden = document.getElementById('contact-addresses-hidden'); if (!hidden) return false; const entries = JSON.parse(hidden.value || '[]'); const addr = entries[idx]; return addr && addr.type === 'residential' && addr.line1 === '456 Oak Ave' && addr.line2 === 'Apt 2B' && addr.city === 'Chicago' && addr.state === 'IL' && addr.postal_code === '60601' && addr.country === 'United States'; }, existingCards); }"

assert_run "person edit education card structured editing replaces JSON textarea" \
  "${PWCLI}" run-code "async page => { if (await page.locator('textarea#edit-education').count()) throw new Error('education JSON textarea should be gone'); await page.getByRole('button', { name: 'Add Education' }).click(); const cards = page.locator('#education-list .person-edit-address-card'); await cards.first().locator('input[data-card-key=\"institution\"]').fill('MIT'); await cards.first().locator('input[data-card-key=\"degree\"]').fill('BS'); await cards.first().locator('input[data-card-key=\"field_of_study\"]').fill('Computer Science'); await cards.first().locator('input[data-card-key=\"year_start\"]').fill('2005'); await cards.first().locator('input[data-card-key=\"year_end\"]').fill('2009'); const eduRaw = await page.locator('#education-hidden').inputValue(); const edu = JSON.parse(eduRaw); if (edu.length !== 1) throw new Error('expected 1 education entry'); if (edu[0].institution !== 'MIT' || edu[0].degree !== 'BS') throw new Error('education data mismatch'); }"

assert_run "person edit career card structured editing replaces JSON textarea" \
  "${PWCLI}" run-code "async page => { if (await page.locator('textarea#edit-career').count()) throw new Error('career JSON textarea should be gone'); await page.getByRole('button', { name: 'Add Position' }).click(); const cards = page.locator('#career-list .person-edit-address-card'); await cards.first().locator('input[data-card-key=\"employer\"]').fill('Acme Corp'); await cards.first().locator('input[data-card-key=\"title\"]').fill('Engineer'); const careerRaw = await page.locator('#career-hidden').inputValue(); const career = JSON.parse(careerRaw); if (career.length !== 1 || career[0].employer !== 'Acme Corp') throw new Error('career data mismatch'); }"

assert_run "person edit bio uses Trix rich text editor" \
  "${PWCLI}" run-code "async page => { if (await page.locator('textarea#edit-bio').count()) throw new Error('bio plain textarea should be replaced by Trix'); const trix = page.locator('trix-editor'); if (!await trix.count()) throw new Error('Trix editor not found for bio'); const hiddenBio = page.locator('#edit-bio'); if (!await hiddenBio.count()) throw new Error('hidden bio input not found'); }"

"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/person-edit-multivalue.png" --full-page true >/dev/null

assert_run "address card Places autocomplete populates structured subfields" \
  "${PWCLI}" run-code "async page => { await page.evaluate(() => { const fakePlaces = { AutocompleteSessionToken: function() {}, AutocompleteSuggestion: { fetchAutocompleteSuggestions: async ({ input }) => ({ suggestions: safeText(input).toLowerCase().startsWith('123') ? [{ placePrediction: { text: { toString() { return '123 Main St, Chicago, IL 60601, USA'; } }, toPlace() { const place = { id: 'ChIJ_fake_place_id', fetchFields: async () => { place.formattedAddress = '123 Main St, Chicago, IL 60601, USA'; place.location = { lat: () => 41.8781, lng: () => -87.6298 }; place.addressComponents = [ { types: ['street_number'], shortText: '123', longText: '123' }, { types: ['route'], shortText: 'Main St', longText: 'Main Street' }, { types: ['locality'], shortText: 'Chicago', longText: 'Chicago' }, { types: ['administrative_area_level_1'], shortText: 'IL', longText: 'Illinois' }, { types: ['postal_code'], shortText: '60601', longText: '60601' }, { types: ['country'], shortText: 'US', longText: 'United States' } ]; } }; return place; } } }] : [] }) } }; window.google = { maps: { importLibrary: async (name) => { if (name !== 'places') throw new Error('unexpected library ' + name); return fakePlaces; } } }; function safeText(value) { return typeof value === 'string' ? value.trim() : ''; } const addrCards = document.querySelectorAll('#contact-address-list .person-edit-address-card'); addrCards.forEach(c => { const grp = c.querySelector('[data-place-field]'); if (grp) { delete grp.dataset.locationBound; grp.querySelectorAll('.place-autocomplete-suggestions').forEach(n => n.remove()); } }); window.familyBookLocations.init(document.getElementById('contact-address-list'), { apiKey: 'fake-key', hasGoogle: true, manualHint: 'Manual', configuredHint: 'Lookup', verifiedHint: 'Verified', failedHint: 'Failed', suggestionsLabel: 'Place suggestions' }); }); const lastCard = page.locator('#contact-address-list .person-edit-address-card').last(); const line1Input = lastCard.locator('input[data-address-key=\"line1\"]'); await line1Input.fill('123 Main'); await page.waitForSelector('.place-autocomplete-suggestions:not([hidden]) .place-autocomplete-suggestion'); await page.locator('.place-autocomplete-suggestion').first().click(); await page.waitForFunction(() => { const card = document.querySelector('#contact-address-list .person-edit-address-card:last-child'); if (!card) return false; const city = card.querySelector('[data-address-key=\"city\"]'); const state = card.querySelector('[data-address-key=\"state\"]'); const zip = card.querySelector('[data-address-key=\"postal_code\"]'); const country = card.querySelector('[data-address-key=\"country\"]'); return city && city.value === 'Chicago' && state && state.value === 'Illinois' && zip && zip.value === '60601' && country && country.value === 'United States'; }); const hiddenVal = JSON.parse(await page.locator('#contact-addresses-hidden').inputValue()); const lastAddr = hiddenVal[hiddenVal.length - 1]; if (lastAddr.city !== 'Chicago') throw new Error('city not populated: ' + lastAddr.city); if (lastAddr.state !== 'Illinois') throw new Error('state not populated: ' + lastAddr.state); if (lastAddr.postal_code !== '60601') throw new Error('postal_code not populated: ' + lastAddr.postal_code); if (lastAddr.country !== 'United States') throw new Error('country not populated: ' + lastAddr.country); }"

"${PWCLI}" goto "${BASE_URL}/map"
"${PWCLI}" run-code "async page => { await page.locator('#map-svg').waitFor(); await page.waitForTimeout(1500); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/map.png" --full-page true >/dev/null

assert_run "map page renders at least one marker" \
  "${PWCLI}" run-code "async page => { if (await page.locator('#map-svg g').count() === 0) throw new Error('no map markers'); }"

assert_run "map marker supports keyboard navigation" \
  "${PWCLI}" run-code "async page => { const marker = page.locator('#map-svg [role=\"link\"]').first(); await marker.focus(); await page.keyboard.press('Enter'); await page.waitForURL(/\\/people\\/[^/]+\\/edit/); if (!page.url().includes('/edit')) throw new Error('map keyboard navigation failed'); }"

"${PWCLI}" goto "${BASE_URL}/map"
"${PWCLI}" run-code "async page => { await page.locator('#map-svg').waitFor(); await page.waitForTimeout(800); }"

assert_run "map focus reveals selected marker semantics" \
  "${PWCLI}" run-code "async page => { const marker = page.locator('#map-svg [role=\"link\"]').first(); await marker.focus(); await page.locator('#map-selected-marker').waitFor(); const text = await page.locator('#map-selected-details').textContent(); if (!text || !text.match(/Residence|Burial|residencia|sepultura|проживания|Захоронение/)) throw new Error('selected marker details missing semantics'); }"

assert_run "configured google map path preserves keyboard navigation" \
  "${PWCLI}" run-code "async page => { await page.evaluate(() => { const mapEl = document.getElementById('google-map'); mapEl.innerHTML = ''; const overlayPane = document.createElement('div'); overlayPane.style.position = 'absolute'; overlayPane.style.inset = '0'; mapEl.appendChild(overlayPane); class FakeMap { constructor(el, opts) { this.el = el; this.opts = opts; } setCenter() {} setZoom() {} fitBounds() {} } class FakeLatLngBounds { constructor() { this.points = []; } extend(value) { this.points.push(value); } getCenter() { return { lat: 20, lng: 0 }; } } class FakeLatLng { constructor(lat, lng) { this.lat = lat; this.lng = lng; } } class FakeOverlayView { setMap(map) { this.map = map; if (map) { if (this.onAdd) this.onAdd(); if (this.draw) this.draw(); } } getPanes() { return { overlayMouseTarget: overlayPane }; } getProjection() { return { fromLatLngToDivPixel() { return { x: 140, y: 140 }; } }; } } window.google = { maps: { Map: FakeMap, OverlayView: FakeOverlayView, LatLngBounds: FakeLatLngBounds, LatLng: FakeLatLng } }; const root = document.getElementById('map-root'); root.dataset.mapProvider = 'google'; root.dataset.googleMapsApiKey = 'fake-google-key'; root.dataset.googleMapsMapId = ''; }); await page.evaluate(() => window.familyBookMap.reload()); await page.locator('.map-google-marker-button').first().waitFor(); const marker = page.locator('.map-google-marker-button').first(); await marker.focus(); await page.keyboard.press('Enter'); await page.waitForURL(/\\/people\\/[^/]+\\/edit/); if (!page.url().includes('/edit')) throw new Error('google map keyboard navigation failed'); }"

"${PWCLI}" goto "${BASE_URL}/map"
"${PWCLI}" run-code "async page => { await page.locator('#map-svg').waitFor(); await page.waitForTimeout(800); }"

"${PWCLI}" run-code "async page => { await page.locator('#map-filter-residence-country').fill('CA'); await page.locator('#apply-map-filters').click(); await page.waitForTimeout(1200); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/map-filtered.png" --full-page true >/dev/null

assert_run "map filters can be applied in-browser" \
  "${PWCLI}" run-code "async page => { if (await page.locator('#map-svg g').count() === 0) throw new Error('filtered map has no markers'); }"

"${PWCLI}" cookie-set locale es --domain 127.0.0.1 --path / --sameSite Lax >/dev/null
"${PWCLI}" goto "${BASE_URL}/map"
"${PWCLI}" run-code "async page => { await page.locator('#map-svg').waitFor(); await page.waitForTimeout(800); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/map-es.png" --full-page true >/dev/null

assert_run "map surface uses locale strings in Spanish" \
  "${PWCLI}" run-code "async page => { const text = await page.locator('#map-root').textContent(); if (!text || !text.includes('Mapa Familiar')) throw new Error('map title did not localize to Spanish'); if (!text.includes('Distancia familiar')) throw new Error('relationship scope filter did not localize to Spanish'); }"

"${PWCLI}" cookie-set locale en --domain 127.0.0.1 --path / --sameSite Lax >/dev/null

"${PWCLI}" resize 390 844
"${PWCLI}" goto "${BASE_URL}/map"
"${PWCLI}" run-code "async page => { await page.locator('#map-svg').waitFor(); await page.waitForTimeout(800); }"
"${PWCLI}" screenshot --filename "${SCREENSHOT_DIR}/map-mobile.png" --full-page true >/dev/null

assert_run "map page avoids horizontal overflow on mobile" \
  "${PWCLI}" run-code "async page => { const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth); if (overflow > 4) throw new Error('map page overflows horizontally on mobile'); const selected = await page.locator('#map-selected-marker').boundingBox(); const filter = await page.locator('#map-filter-relationship-scope').boundingBox(); if (!selected || !filter) throw new Error('map mobile controls missing'); }"

"${PWCLI}" resize 1440 960

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
