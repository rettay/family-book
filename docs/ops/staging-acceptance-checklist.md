# Staging Acceptance Checklist

Run this checklist on the staging environment before promoting to production.

**Staging URL:** `https://family-book-staging.up.railway.app`

---

## Quick Smoke Test (2 minutes)

For low-risk changes (copy, styling, minor fixes). If any item fails, do NOT promote.

- [ ] `/health` returns `{"status":"ok","db":"connected"}`
- [ ] Login with Google OAuth succeeds → lands on tree page
- [ ] Tree renders nodes with photos/initials — click a node → sidebar opens
- [ ] Upload a photo via sidebar Media tab → photo appears in media list
- [ ] Edit a field in sidebar Details tab → auto-save indicator shows "Saved"

---

## Full Acceptance (15 minutes)

For significant changes (new features, data model changes, auth changes). Run the quick smoke test first, then continue with these sections.

### Health & Infrastructure

- [ ] `/health` returns ok
- [ ] Server logs show no startup errors (check Railway logs dashboard)
- [ ] Alembic migrations ran successfully on boot

### Authentication & Access

- [ ] Login with Google OAuth → redirected to tree
- [ ] Logout → redirected to login page
- [ ] Session persists across page reload (no re-login required)
- [ ] Admin dashboard accessible at `/admin`
- [ ] Non-admin user cannot access `/admin`

### Tree

- [ ] Tree renders all persons as nodes with names/initials
- [ ] Persons with headshots show photos in node circles
- [ ] Click node → sidebar opens with person overview
- [ ] Right-click node → context menu appears with actions
- [ ] Context menu "View branch" filters tree to that person's lineage
- [ ] "Show full tree" restores complete tree
- [ ] Double-click node → navigates to person edit page
- [ ] Search (left panel) finds persons by name
- [ ] Display preferences toggle (names, photos, dates) works

### Person Editing

- [ ] Sidebar Details tab → edit a field → auto-save shows "Saved"
- [ ] Sidebar Details tab → "Edit more details" reveals hidden sections
- [ ] Person edit page → save changes → data persists on reload
- [ ] Place history → add a residence entry → saves correctly
- [ ] Language autocomplete → type a language → suggestions appear

### Media

- [ ] Upload a photo via sidebar → upload modal appears with progress bar
- [ ] Set as headshot (star button) → tree node updates on reload
- [ ] Delete media (trash button) → item removed after confirmation
- [ ] Global gallery page (`/gallery`) renders with filters
- [ ] Click avatar circle → file picker opens → photo uploads as headshot

### Wiki / Family Bios

- [ ] Person wiki page (`/wiki/{slug}`) renders all sections
- [ ] Wiki page shows media gallery section when person has media
- [ ] Place history section renders chronologically

### Admin

- [ ] Admin dashboard shows person list with last login timestamps
- [ ] Active session counts visible per person
- [ ] "Log out all" button works for a person with sessions
- [ ] Create invite → delivery status shows (Sent/Failed/Not configured)

### Internationalization

- [ ] Switch browser locale to Spanish → key surfaces render in Spanish
- [ ] Tree sidebar labels show translated text

### Mobile / Responsive

- [ ] Tree page: no horizontal overflow at 390px viewport width
- [ ] Sidebar: usable at 390px (fields reachable, tabs work)
- [ ] Person edit page: form stacks properly on narrow viewport

---

## After Acceptance

If all items pass:
1. Merge `codex/staging` → `main`
2. Approve the production deploy in GitHub Actions
3. Verify `/health` on production after deploy

If any items fail:
1. Note the failing items
2. Fix on a feature branch
3. Re-deploy to staging
4. Re-run the failed checklist items
