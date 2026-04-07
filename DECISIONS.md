# Family Book Decisions

## Active Decisions

### 1. Family Book is a family wiki, not a restrictive genealogy viewer

Launch direction is a shared family knowledge base: part family tree, part archive, part story system. Collaboration is a first-class behavior, not a narrow admin workflow.

### 2. Flat family access replaces graph-distance privacy for launch work

The current graph-distance access model does not match the intended product. For launch-oriented implementation work, authenticated active family members should be treated as peers with broad shared visibility and edit capability.

### 3. Admins manage accounts and policy, not all content creation

Admins own invites, account lifecycle, settings, moderation, and policy. Members should still be able to create and edit shared family content.

### 4. Rich family history is first-class content

The product is not limited to names and relationships. Stories, notes, photos, videos, audio, tagged content, burial information, contact data, medical history, and timeline entries are all part of the launch direction.

### 5. Canonical launch docs override speculative older material

For launch implementation, the canonical sources are:

- `foundation/PRODUCT_VISION.md`
- `foundation/V1_PRODUCT_REQUIREMENTS.md`
- `foundation/COLLABORATION_AND_PRIVACY.md`
- `operating_system.md`

Older docs such as `SPEC.md` remain useful context but do not override the canonical launch contract when they conflict.

### 6. Product truthfulness is a release gate

Documentation and UI must not claim behavior that the runtime does not actually support. This is especially important for:

- shared visibility,
- invites/onboarding,
- media rendering,
- medical/contact data handling,
- encryption and privacy language.

### 7. Sensitive data is shared within the authenticated family boundary at launch

The launch assumption, based on current product direction, is that active family members have flat access to shared content, including contact and medical information. This increases the need for:

- explicit invite/account control,
- audit history,
- reversible changes,
- encryption in transit and at rest.

If that assumption changes later, it should become an explicit new decision and packet sequence.

### 8. The UX North Star is a canonical launch contract

The experience-design contract (`foundation/UX_NORTH_STAR.md`) defines how Family Book should feel to use. It complements the product vision (what the app does) and V1 requirements (what capabilities exist) by defining the interaction model. Key principles:

- The tree is the workspace, not a visualization
- In-context editing over page-navigation detours
- Progressive disclosure over form walls
- Empty states are invitations, not dead labels
- Content (stories, media) over chrome (version history, admin metadata)
- Research-friendly data entry (partial info, confidence, provenance)

### 9. Genealogy-researcher persona is a first-class user

Family Book serves both casual family members and genealogy-focused power users. The genealogy researcher who actively tracks family history, records provenance, and motivates others to contribute is critical to the collaborative loop — they're the one who keeps the family record alive. Features should support their workflow without making the app inaccessible to casual contributors.

### 10. Research notes are shared family knowledge, not sensitive PII

Research notes (per-person working notes about genealogy research progress) are visible to all active family members. They are not encrypted. They exist to support collaborative research, not to store private information. Sensitive findings should go in the bio or medical history fields, which have appropriate protection.

### 11. External integration strategy: free APIs only, GEDCOM as universal connector

Family Book integrates exclusively with free, public genealogy APIs and data sources. No paid API subscriptions. The integration tier:

- **GEDCOM import** is the universal onboarding path — it bridges Ancestry, FamilySearch, MyHeritage, Gramps, and every other platform that exports .ged files.
- **FamilySearch API** (free, OAuth 2) is the single highest-value live integration — it covers USA, Australia, Argentina, and Italy.
- **Newspaper APIs** (Chronicling America for USA, Trove for Australia) are the easiest integrations — free, no auth, high discoverability.
- **NARA Catalog API** and **DPLA API** cover US federal records and cross-institutional archives.
- **Antenati IIIF** provides access to Italian civil records (71M+ images) via standard image viewer protocol.
- **CEMLA** (Argentine immigration, 4.4M records, no API) is integrated via HTML parsing with graceful fallback to link-out behavior.

This strategy maximizes coverage across the family's four countries (USA, Australia, Argentina, Italy) without incurring subscription costs or depending on platforms that restrict API access.

### 12. Family calendar is a natural extension of existing data

A family calendar surface auto-populated from Person birth/death dates, Partnership dates, and Moment timestamps is a planned feature. It rewards data entry (every date you add makes the calendar richer), gives members a reason to visit regularly, and surfaces family knowledge without requiring active search. Calendar events use existing data models — no new entity type needed for auto-populated dates. Manually-added recurring dates (family traditions, immigration anniversaries) can use the existing Moments system.

### 13. Family Book is a full multimedia archive, not photo-only

The backend already supports video (100MB), audio (25MB), and image uploads. The frontend must catch up: HTML5 video/audio players, document (PDF) support, and media-type-aware rendering across all surfaces. Voice recordings, home videos, scanned documents, and old letters are core family history content. This also lays the groundwork for the long-horizon AI memorial feature (G-21).

### 14. AI family memorial is a long-horizon goal

Creating an AI-powered conversational memorial of a family member — using stored voice recordings, biographical data, stories, and research notes — is a compelling long-term vision. It requires: (a) voice recording storage (G-19), (b) rich biographical content including life story fields (G-22), (c) genetic/health context (G-23), (d) AI/ML integrations, and (e) an ethical consent framework. The groundwork is being laid across S17-S22 (research notes, multimedia support, life story fields, genetic profile, source citations). Not scheduled for implementation but explicitly recognized as a north-star feature that justifies the depth of data collection the app encourages.

### 15. Person records should capture full life context, not just genealogy skeleton

Genealogy tools typically store names, dates, places, and relationships. Family Book goes deeper by also capturing: obituaries (often the richest single-source document), education history, career/profession history, organizational memberships (churches, clubs, fraternal orders, military units), physical attributes, expanded contact info, and detailed notes. These are stored as structured JSON arrays on Person (same pattern as `languages`) for add/remove editing. Obituaries are a dedicated long-text field. All are included in revision snapshots.

### 17. Physical attributes use metric storage with locale-aware display

Height (cm), weight (kg), and shoe size are stored internally in a single standard unit. Display conversion to imperial (feet/inches, pounds) or other systems is controlled by a locale preference at the family or user level. This avoids data ambiguity while supporting international families. Eye color, hair color, and other descriptive attributes are free-text or light enum fields.

### 18. Contact info is structured and encrypted

Phone numbers are stored as a JSON array with type labels (mobile, home, work) in E.164 format. Addresses are stored as structured JSON with components (street, city, state, postal code, country). Both are encrypted at rest, consistent with the existing treatment of WhatsApp, Telegram, Signal, and email contact fields.

### 16. Genetic and medical data requires structured storage and encryption

The existing `medical_history` field is a single encrypted text blob — adequate for notes but insufficient for cross-family health pattern analysis. The planned expansion (G-23) adds:
- Structured medical conditions (condition, onset, severity, treatment, inherited flag, hereditary line)
- Genetic profile (maternal/paternal haplogroups, admixture percentages, DNA test provider)
- Family health dashboard for cross-person condition aggregation

All genetic and medical data is encrypted at rest. Visibility policy for health/genetic data across family members requires an explicit decision before implementation — the current flat-access model may need a per-field or per-person opt-in for this category.

### 19. Calendar is a primary family surface; feed management is secondary

`/calendar` is not a feed-administration page. Its primary job is to help family members understand what is happening this month and why it matters. The month or agenda surface should therefore be the hero at first render, while outbound subscriptions and inbound holiday/source configuration live behind a clear secondary management affordance such as `Manage Calendars` or `Add Holidays`.

Implications:

- the calendar surface should be visible above the fold before any long list of feed links
- family-feed subscription and holiday-layer setup are distinct concepts in the UI
- raw URLs are transport details, not the main UX
- event detail should emphasize family meaning such as birthdays, anniversaries, and upcoming milestones rather than generic labels alone

### 20. Google Maps platform uses a unified provider with separate browser and server credentials

Family Book should use the Google Maps Platform through a single provider model, while separating browser and server credentials for security:

- `GOOGLE_MAPS_BROWSER_API_KEY` is the preferred browser-side key for map display and Places-style client lookup
- `GOOGLE_MAPS_SERVER_API_KEY` is the preferred server-side key for geocoding and other backend Google calls
- `GOOGLE_MAPS_API_KEY` remains a legacy fallback during migration so deploys do not break mid-cutover
- `GOOGLE_MAPS_MAP_ID` is optional and enables styled maps when configured

Implications:

- the product should not introduce a separate `GOOGLE_PLACES_API_KEY` contract unless Google itself requires it operationally
- map rendering and Places autocomplete use the browser key, while server geocoding uses the server key
- missing Google config should degrade gracefully to the current fallback map behavior and manual place entry rather than pretending advanced lookup is available

### 21. Map trust requires normalized places and persisted coordinates, not country centroids alone

The current country-centroid map is a truthful fallback, but it is not the intended long-term map behavior. When Family Book claims to show where family members are, it should persist normalized location data and coordinates derived from user-confirmed place selection or geocoding.

Implications:

- location-entry UX should capture normalized place and country information, not just free-text plus a guessed ISO code
- the map should evolve to plot persisted coordinates for residence, burial, and other supported place types
- kinship-aware map views should be built on actual relationship-distance calculations from the family graph, not arbitrary manual tagging
- if coordinates are unknown, the UI should either fall back explicitly or omit misleading precision rather than silently implying exact location

### 22. Relationship correction must be edit-first, not delete-first

Family members will make genealogy mistakes while editing the tree. When they do, the product should support direct correction of an existing relationship instead of requiring users to infer that they must delete a wrong link and recreate a new one.

Implications:

- parent-child relationships need a truthful correction contract, including direction reversal when safe
- tree relationship cards should expose explicit `edit`, `reverse direction`, and `remove` actions where they make sense
- parent-child reversal must be validated server-side against ancestry cycles rather than implemented as a fragile client-side delete/recreate sequence
- relationship correction should happen in the tree workspace, since the tree is the primary editing surface

### 23. Media management uses per-item visibility and soft-delete

Family media (photos, videos, audio, documents) is the most emotionally valuable content in the archive. The media system uses:

- Per-media `visibility` field (family/private/hidden) enforced at all serving endpoints
- Non-admin deletion is always soft (sets visibility=hidden, files preserved on disk)
- Admin deletion is permanent (files removed, DB record deleted)
- Image uploads generate thumb (200x200 crop) and medium (800px max) variants for gallery performance
- Video/audio metadata (duration, dimensions) extracted at upload time via ffmpeg/mutagen
- Primary headshot managed via `Person.photo_url` pointing to a media ID, settable from gallery

Implications:

- all media serving endpoints must check visibility before returning files
- soft-deleted media is recoverable by admins via moderation queue
- gallery thumbnails use variant endpoints, not original files, for performance
- local filesystem storage is sufficient for a single-family app; cloud migration deferred until scale requires it

### 24. Authentication should be passwordless, email-recoverable, and passkey-upgradable

Family Book should not introduce site-local passwords unless a future decision explicitly reverses this direction. The near-term auth model is:

- email magic links as the universal sign-in and recovery fallback
- MXroute SMTP as the supported outbound email path
- Google sign-in retained as optional convenience, not a requirement
- passkeys/WebAuthn as the stronger repeat-login upgrade after email fallback is working
- admin-issued one-time links for support, generated fresh and audited rather than reconstructed from stored raw tokens
- no custom QR-code bearer-token login; QR-style cross-device login should come from platform passkey flows

Implications:

- invite and magic-link tokens remain bearer credentials and should be stored only as hashes
- admin support can generate new one-time links but should not retrieve historical raw invite URLs
- login and recovery flows must be easy for low-confidence relatives and must not reveal whether an email belongs to an account

Implementation note:

- S46 closed this direction on 2026-04-07: SMTP/MXroute replaced Resend-specific outbound delivery, magic links became the primary login/recovery path, admin support links are fresh one-time credentials, and passkeys/WebAuthn are available as an optional repeat-login path.
