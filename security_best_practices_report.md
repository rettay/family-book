# Family Book Security Assessment

Assessment date: 2026-03-19

## Executive Summary

Family Book currently treats "any authenticated family member" as a trusted principal for most of the application. In practice, that means a single low-privilege account can enumerate nearly the entire family graph, read sensitive contact details and media, and inject content onto other users' profiles. The most serious issues are authorization failures, not classic injection bugs: the app rarely enforces ownership, family-distance, or role-based visibility beyond `require_auth`.

Railway-specific deployment choices increase the blast radius. The public-facing service can be exposed with a generated domain, internal private-network hostnames are reachable from the app at runtime, and the repo's current storage path conventions make persistent-vs-ephemeral data placement easy to misconfigure. I did not find committed production secrets in tracked files, and a `pip-audit` run against the installed Python environment returned no known CVEs, but the container and image supply chain remains loosely pinned.

## Scope Notes

- No evidence of SQL injection, command injection, `eval`, `exec`, unsafe deserialization, or Jinja SSTI was found in the reviewed code paths.
- Cookie auth is in place, session tokens are generated with `secrets.token_hex(32)`, and session values are stored hashed server-side.
- No committed real secrets were found in tracked files. An untracked local `.env` exists and contains active secret/config values, so operational hygiene still matters.
- Railway platform behavior cited here was checked against current Railway docs:
  - Public networking is only exposed after generating a domain: [Public Networking](https://docs.railway.com/networking/public-networking)
  - Relative writes persist only if the mount path matches `/app/...`: [Volumes](https://docs.railway.com/volumes)
  - Variables are available during both build and runtime: [Variables](https://docs.railway.com/variables)
  - Internal service DNS uses `*.railway.internal`: [Private Networking](https://docs.railway.com/networking/private-networking)

## Route Auth Inventory

Current public routes:

- `GET /`
- `GET /login`
- `POST /auth/google`
- `GET /health`
- `POST /api/inbound/envelope` (HMAC webhook, no user session)

Current authenticated-member routes:

- `POST /auth/logout`
- `GET /auth/me`
- `GET /api/tree`
- `GET /api/persons`
- `GET /api/persons/{person_id}`
- `PUT /api/persons/{person_id}` (self or admin)
- `POST /api/media`
- `GET /api/media`
- `GET /api/media/{media_id}`
- `GET /api/media/{media_id}/file`
- `GET /api/media/{media_id}/thumbnail`
- `GET/POST/PUT/DELETE /api/moments...`
- `POST /api/share` (redirects to login if unauthenticated)
- Page and partial routes under `/tree`, `/people`, `/settings`, `/partials/...`

Current admin routes:

- All `/api/relationships/*`
- All `/api/admin/backup*`
- `/admin`
- `/admin/people/new`
- `/partials/audit-log`

Expected auth requirements that are currently missing:

- Person, media, moment, and comment reads should be relationship-aware or ownership-aware, not merely "logged in".
- Writes that affect another person's profile or timeline should be self/admin/delegate only.
- `"admins"` visibility on moments should be enforced as admin-only everywhere.
- Hidden person page routes should deny non-admin access consistently, not only in one API handler.

## Findings

### Critical / High

### FB-01
- **Severity**: High
- **Location**: `app/routes/persons.py:21-62`, `app/routes/tree.py:20-60`, `app/routes/pages.py:183-269`
- **Description**: The app's core read paths enforce only `require_auth`, not relationship distance, ownership, or field-level privacy. `GET /api/persons/{person_id}` returns highly sensitive fields such as `contact_email`, `contact_whatsapp`, `contact_signal`, residence details, and biography for any non-hidden person. `GET /api/tree` returns the full visible family graph. Page routes render the same underlying data with no additional privacy layer.
- **Exploit Scenario**: A newly invited distant relative, or anyone who compromises one family member's session, can enumerate `/api/persons`, `/api/tree`, and `/people/{id}` to harvest contact info, household geography, family structure, and identity links for the entire family. This is a full horizontal privacy collapse.
- **Remediation**: Build a centralized authorization layer that decides access by relationship distance, ownership, and role. Apply it at router or dependency level so handlers cannot "forget" it. Redact contact and location fields by default, then explicitly opt them in for self/admin/approved relatives.

### FB-02
- **Severity**: High
- **Location**: `app/routes/media.py:18-63`, `app/routes/media.py:66-168`, `app/routes/pages.py:450-467`
- **Description**: Media upload and read endpoints are classic IDORs. Upload only checks that `person_id` exists; it does not verify that the caller owns that profile or is an admin. Listing, metadata, file download, and thumbnail routes require only a valid session and perform no subject-level authorization.
- **Exploit Scenario**: Any logged-in member can upload manipulated or abusive media to another relative's profile by posting to `/api/media` with that victim's `person_id`. The same member can then list and download private photos and documents for any other person they can identify.
- **Remediation**: Require `person_id == current_user.id`, admin, or an explicit delegated permission on all media writes. Gate every media read by the same privacy policy used for people and moments. Remove `file_path`, `file_hash`, and similar internal metadata from normal-user responses.

### FB-03
- **Severity**: High
- **Location**: `app/routes/moments.py:205-208`, `app/routes/moments.py:221-246`, `app/routes/moments.py:254-269`, `app/routes/pages.py:136-149`, `app/routes/pages.py:382-423`
- **Description**: The `"admins"` visibility level is not enforced. Non-admin filtering only excludes `"hidden"`, so `"admins"` content is served to ordinary members in API and HTML feeds. Separately, `POST /api/moments` lets any authenticated user set `person_id` arbitrarily, allowing users to create moments on behalf of other people without consent.
- **Exploit Scenario**: A normal member can create defamatory or misleading posts attached to another family member's profile, then mark them `"admins"` to imply legitimacy. Meanwhile, real admin-only timeline entries are still visible to all members because the filter is wrong.
- **Remediation**: Enforce visibility semantics consistently: `members` for authorized members, `admins` for admins only, `hidden` for explicitly hidden objects. Require self/admin/delegate authorization when a write targets another person's profile or timeline. Recheck visibility in comments and reaction endpoints too.

### FB-04
- **Severity**: High
- **Location**: `app/inbound/routes.py:76-123`
- **Description**: The inbound email webhook blindly fetches attacker-supplied attachment URLs with `httpx`, without an allowlist, private-network rejection, or download-size cap. On Railway, services in the same environment can be reached via `*.railway.internal`, so this becomes a meaningful SSRF primitive if the webhook secret is exposed or abused by an upstream provider.
- **Exploit Scenario**: An attacker who obtains `ENVELOPE_WEBHOOK_SECRET` sends a validly signed webhook whose attachment URL points to `http://some-service.railway.internal/...` or another internal HTTP target. Even as a blind SSRF, the app will fetch it, write the body to disk, and reveal success/failure side effects. The same endpoint can be aimed at huge files to exhaust disk space.
- **Remediation**: Only accept signed download URLs from a tightly controlled provider domain allowlist. Reject private IPs, loopback, link-local ranges, and `*.railway.internal`. Enforce maximum content length, stream with quotas, and fail closed if the source host is not explicitly trusted.

### Medium

### FB-05
- **Severity**: Medium
- **Location**: `app/static/sw.js:44-95`, `app/templates/base.html:43-48`
- **Description**: The service worker caches all successful GET `/api/*` responses and pages without any per-user isolation, logout eviction, or `Cache-Control: no-store` support. This includes tree data, people lists, media responses, and moment feeds.
- **Exploit Scenario**: On a shared phone or laptop using the same browser profile, one family member signs in and browses private data, then signs out. Another local user can continue to retrieve stale cached content through the service worker, especially while offline or during network failures. Any future XSS would also inherit a rich local cache of private family data.
- **Remediation**: Do not cache authenticated API or media responses by default. If offline access is a product requirement, partition caches by user/session, purge them on logout, and mark sensitive responses `Cache-Control: private, no-store`.

### FB-06
- **Severity**: Medium
- **Location**: `app/main.py:44-51` (inference from default `FastAPI()` settings)
- **Description**: The app creates `FastAPI()` without disabling or protecting interactive docs. In production this exposes `/docs`, `/redoc`, and `/openapi.json`, which provides a full route and schema map to anyone who can reach the public domain.
- **Exploit Scenario**: An internet attacker hits `/openapi.json`, learns every auth-protected route, payload shape, and admin path, and then concentrates brute-force and auth-bypass attempts on the most valuable endpoints.
- **Remediation**: Disable docs endpoints in production with `docs_url=None`, `redoc_url=None`, and `openapi_url=None`, or protect them behind admin auth or a network allowlist.

### FB-07
- **Severity**: Medium
- **Location**: `app/config.py:11-12`, `README.md:116-120`, `Dockerfile:16-24`, `app/backup/service.py:23-38`
- **Description**: Railway volume usage is easy to misconfigure because the repo mixes relative SQLite paths (`sqlite:///data/family.db`) with absolute media paths (`/data`). Railway documents that relative paths write under `/app`, and that the mount path must match where the app writes. If operators follow the current README literally, the database may live on ephemeral `/app/data` while media or backups live elsewhere.
- **Exploit Scenario**: No attacker input is required. A normal Railway redeploy, crash, or container replacement can destroy the family database while the operator believes the app is safely using a persistent volume. That is a severe integrity and availability risk for the core dataset.
- **Remediation**: Standardize on absolute volume-backed paths everywhere, for example `DATABASE_URL=sqlite:////data/family.db` and `DATA_DIR=/data`, or read `RAILWAY_VOLUME_MOUNT_PATH` at runtime. Validate on startup that the SQLite path and media/backups path all live under the mounted volume.

### FB-08
- **Severity**: Medium
- **Location**: `app/routes/media.py:36-49`, `app/pwa/routes.py:47-50`, `app/services/media_service.py:121-124`
- **Description**: The app reads uploaded files fully into memory before enforcing its application-level size limits. The same pattern appears in the share-target endpoint. This creates an avoidable memory exhaustion path against a small Railway instance.
- **Exploit Scenario**: Any authenticated user repeatedly uploads very large multipart bodies. The process consumes memory before the size check fires, the app is OOM-killed, and the in-memory rate limiter resets on restart, making the DoS easy to repeat.
- **Remediation**: Enforce request size limits at the edge and before `read()`, reject oversized `Content-Length` values, and stream uploads to disk or chunked processing with hard caps.

### Low / Informational

### FB-09
- **Severity**: Low
- **Location**: `Dockerfile:1-24`, `docker-compose.yml:25-72`
- **Description**: The current runtime and auxiliary services are supply-chain fragile. The Docker base image is not pinned by digest, `pip install uv` is unpinned, the container runs as root, and the Compose stack references several `:latest` images for Conduit and Mautrix bridges. `pip-audit` found no known CVEs in the installed Python packages, but image provenance and rebuild reproducibility are weak.
- **Exploit Scenario**: A compromised upstream package or container image lands during a future build, executes in the build/runtime container, and gains root-level access to mounted family data. This is less likely than the auth bugs above, but the impact is complete compromise.
- **Remediation**: Pin container images by digest, pin `uv` to an exact version, drop unnecessary packages, run the app as a non-root user where practical, and replace `:latest` image tags with reviewed immutable versions.

### FB-10
- **Severity**: Informational
- **Location**: `app/routes/health.py:11-27`, `app/main.py:89-91`
- **Description**: `/health` is publicly reachable and returns the application version plus `persons_count`. There is also no visible `TrustedHostMiddleware`, so host-header validation is absent in app code. This is not a primary exploit by itself, but it improves reconnaissance for attackers.
- **Exploit Scenario**: An external scanner learns the app version, confirms a live database, estimates family size, and then probes the public service more efficiently.
- **Remediation**: Reduce `/health` to a minimal status payload, add host-header validation, and keep richer diagnostics behind admin auth.

## Top 5 Priority Fixes

1. Build and apply a single authorization layer for people, moments, comments, and media, then default all sensitive routes to deny unless explicitly allowed.
2. Lock down writes that target other people: no arbitrary `person_id` on moments or media uploads without admin/delegate permission.
3. Fix moment visibility enforcement so `"admins"` is truly admin-only across feeds, detail endpoints, comments, and partials.
4. Remove or redesign service-worker caching for authenticated responses and add `Cache-Control: private, no-store` on sensitive routes.
5. Harden the inbound webhook against SSRF and storage abuse with host allowlisting, private-network blocking, and strict download-size controls.

## Security Posture Score

**4/10**

The app has some solid fundamentals: server-side session hashing, no obvious injection sinks, a restrictive CORS configuration, and current Python dependencies without known CVEs. The score is pulled down hard by systemic authorization failures, weak privacy enforcement, and a webhook SSRF path that becomes more dangerous in a Railway private-networked environment. This is not safely deployable as a privacy-sensitive family archive until access control is redesigned and enforced centrally.
