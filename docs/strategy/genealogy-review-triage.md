# Genealogy Review Gap Triage

Source: External review of Family Book from the perspective of a passionate amateur genealogist and power user.

Date: 2026-03-24

## Context

An experienced genealogy enthusiast reviewed the app against what they need day-to-day: research workflow, source tracking, tree navigation at scale, collaboration with non-technical relatives, and content richness. The review was honest and specific.

Some gaps identified in the review have already been partially addressed by Sprints 11-16 (tree workspace, sidebar tabs, moments/media in sidebar, graph-mode relationship editing, rich storytelling). This triage accounts for that progress and focuses on what remains genuinely missing.

## Tier 1 — Core Loop Improvement (Next 2-3 sprints)

These gaps directly affect CFLSR or block the "genealogy buff power user" persona from productive use. They build on the existing tree-workspace foundation without requiring new data models.

### G-01: Tree Search and Navigation

**Gap:** No way to find a person in the tree without scrolling and zooming. The People page has search but navigates to a profile page, not to the tree node. At 50+ people, this is the single biggest navigation friction.

**CFLSR impact:** High. If members can't find who they're looking for, the collaborative loop stalls.

**Scope:** Add a search input to the tree page that filters/highlights matching nodes and pans the viewport to the selected result.

**Complexity:** Medium. Requires client-side search over `treeData.persons` array, a results dropdown, and D3 zoom-to-node behavior.

### G-02: Person Page Content Hierarchy

**Gap:** On the person profile page (`person.html`), Version History appears above Moments. The most engaging content (stories, photos, tagged moments) is buried below administrative detail. This inverts the content-over-chrome principle.

**CFLSR impact:** Medium. Members who land on a person profile (from tree double-click or direct link) see admin metadata before the content that makes them want to contribute.

**Scope:** Reorder person.html sections: Identity → Bio → Moments → Media → Relationships → Version History. Move the "add moment" affordance higher.

**Complexity:** Low. Template reordering, no backend changes.

### G-03: Research Notes Per Person

**Gap:** No place to record research-in-progress notes separate from the bio. Genealogists need a scratch space: "Searched 1940 census for John Smith in Brooklyn, no results. Check alternate spellings." The bio field is for polished narrative, not research tracking.

**CFLSR impact:** Medium. Power users (the "genealogy cousin" persona) need this to stay productive. Without it, they'll track research externally and the app becomes a display layer rather than a workspace.

**Scope:** Add a `research_notes` text field to Person (2000 chars, not encrypted, visible to all active members). Surface it in the tree sidebar Details tab and person edit page.

**Complexity:** Medium. New model field, migration, API update, template updates in sidebar and edit page.

### G-04: Completeness Prompts and Gap Surfacing

**Gap:** The app shows what exists but doesn't highlight what's missing. A person with no birth date, no photo, no stories just shows empty fields. There's no "5 people have no birth date" dashboard, no "add a story about Great-Aunt Rose" prompt.

**CFLSR impact:** High. Gaps are the primary motivator for contribution in genealogy. Surfacing them converts passive viewers into active contributors.

**Scope:** Two levels: (a) per-person gap prompts in the tree sidebar overview tab ("no birth date — add one?", "no stories yet"), and (b) a family-level completeness summary accessible from the tree or admin page.

**Complexity:** Medium. Client-side gap detection from existing person fields, template additions for prompts. Family-level summary requires an API endpoint with aggregated counts.

### G-05: Sidebar Details Completeness

**Gap:** The tree sidebar Details tab (built in S13-S16) exposes key fields for quick editing. But several important person fields still require navigating to the full edit page: patronymic, birth last name, gender, death date, languages, burial details, medical history.

**CFLSR impact:** Medium. Every field that requires a page navigation is a context-switch cost. Gender and death date are particularly high-frequency for genealogy work.

**Scope:** Expand the sidebar Details tab to include all commonly-edited person fields in collapsible sections: Identity (names, gender), Dates (birth, death), Places (birth, residence, burial), Contact, Notes.

**Complexity:** Medium. Sidebar template expansion, collapsible section UI, matching API calls from tree.js.

## Tier 2 — Power User Retention (Sprints 4-6)

These gaps affect whether genealogy-focused users stay long-term. They require more substantial new features or data model changes.

### G-06: Relationship Calculator

**Gap:** "How is Person A related to Person B?" — the most common question at family gatherings. The graph data exists. No algorithm computes or displays the answer.

**CFLSR impact:** Medium-high. This is the single feature most likely to generate delight and sharing. It makes the tree *useful* in conversation, not just as a reference.

**Scope:** API endpoint that computes shortest relationship path between two persons, expressed in human-readable terms ("second cousin once removed through the Santos line"). UI surface: select two nodes, show the path highlighted on the tree.

**Complexity:** High. BFS/DFS path-finding with relationship-type-aware labeling. Cousin/removal degree calculation. UI for two-node selection mode.

### G-07: Source Citations and Provenance

**Gap:** The `source` field on Person is a technical enum (manual, gedcom_import, etc.) that tracks *how* data entered the system, not *where* the information came from. Genealogists need: "Aunt Maria told me at Thanksgiving 2019" vs "1940 US Census, Ancestry.com." ParentChild has `source_detail` and `confidence`; Person does not.

**CFLSR impact:** Medium. Critical for the power-user persona. Without provenance, the family record has no research credibility.

**Scope:** Add `source_detail` (500 chars) and `confidence` (enum: confirmed, probable, uncertain, unknown) to Person model. Surface in sidebar and edit page. Consider per-field citations as a future enhancement but start with per-person level.

**Complexity:** Medium. New model fields, migration, API/schema update, template additions.

### G-08: Timeline View

**Gap:** No chronological view of family events. The data exists: birth dates, death dates, marriage dates, moment `occurred_at` timestamps. But there's no surface that shows "1920: Maria born → 1943: Maria married Jose → 1945: First child → 1987: Maria died" as a navigable timeline.

**CFLSR impact:** Medium. Timelines bring family history to life in a way the tree can't. They're the natural complement to the spatial tree view.

**Scope:** New page or tree-adjacent panel that renders events chronologically. Filterable by person, branch, event type. Events sourced from person dates + moments + partnerships. See also G-20 for branch-specific timeline filtering ("show me the Santos line").

**Complexity:** High. New route, template, API query that aggregates across multiple entity types. Date normalization for approximate dates.

### G-09: Document Attachment as Source Evidence

**Gap:** Media can be uploaded and tagged to persons, but there's no concept of "this is a source document for this person's birth date." A scanned birth certificate and a vacation photo are treated identically.

**CFLSR impact:** Medium. Genealogists distinguish between photos (memories) and documents (evidence). The media model supports `media_type` and `caption` but has no document/evidence classification.

**Scope:** Add a `purpose` field to Media (enum: memory, document, evidence) or use a tag/label system. Allow documents to be linked to specific person fields as supporting evidence.

**Complexity:** Medium-high. Model change, UI for document vs. memory distinction, linking documents to claims.

### G-10: GEDCOM Import / Export

**Gap:** No way to import existing family trees from Ancestry, FamilySearch, MyHeritage, or other tools. The source enum has `gedcom_import` and import batch infrastructure exists, but no GEDCOM parser is implemented. GEDCOM is the universal exchange format — it carries people, relationships, basic events (birth, death, marriage), and source citations. It does NOT carry photos, media, DNA data, or research notes from online platforms.

**CFLSR impact:** High. For a genealogist with years of research in another platform, starting from scratch is a dealbreaker. GEDCOM import is the single most important onboarding accelerator. It bridges every major platform (Ancestry, FamilySearch, MyHeritage, Gramps, Legacy, RootsMagic) into Family Book.

**Scope:** Parse GEDCOM 5.5.1 files (the de facto standard — most exports use this format). Map INDI records to Person, FAM records to ParentChild/Partnership, basic events to date/place fields. Track import batch for audit. Handle encoding edge cases (ANSEL, UTF-8, Latin-1). Export is lower priority but valuable for data portability.

**Complexity:** High. GEDCOM is a nested tagged-line format with many vendor-specific extensions and encoding quirks. Libraries exist (python-gedcom, gedcompy) but quality varies. The mapping from GEDCOM's family-centric model to Family Book's person-centric model requires careful relationship inference.

### G-16: Family Calendar

**Gap:** No calendar view of family dates. The data already exists: birth dates, death dates, marriage dates (via partnerships), moment `occurred_at` timestamps, and family achievements in stories. But there's no surface that shows "March birthdays", "on this day in family history", or "upcoming anniversaries."

**CFLSR impact:** Medium-high. A calendar is a natural reason to visit the app regularly and turns stored dates into a living family tool. It rewards data entry — every birth date you add makes the calendar richer.

**Scope:** Calendar page showing auto-populated events from Person birth/death dates, Partnership dates, and Moments with dates. Monthly view with day detail. Filterable by event type. Optional manually-added recurring dates (family traditions, immigration arrival dates).

**Complexity:** Medium. New route and template. Date aggregation query across Person + Partnership + Moment models. Calendar UI (vanilla JS grid or lightweight library). No new data model if manual events use the existing Moments system.

### G-17: External Record Search Integration

**Gap:** No way to search external genealogy databases from within Family Book. A researcher working on "Maria Santos, born 1920, Buenos Aires" must separately open FamilySearch, newspaper archives, NARA, etc. in other browser tabs. The app could provide a "search external records" panel that pre-fills the person's name and dates into links or API-driven search results.

**CFLSR impact:** Medium-high. This is what turns Family Book from a display layer into a research workspace. The genealogy-researcher persona needs this to justify using the app as their home base.

**Scope:** Person-level "External Records" panel (sidebar tab or person page section) that queries free public APIs and presents results:
- FamilySearch API (OAuth 2, free) — search historical records by name/date/place
- Chronicling America API (free, no auth) — US newspaper mentions 1777-1963
- Trove API (free, API key) — Australian newspaper mentions
- NARA Catalog API (free, no auth) — US federal records (census, military, immigration)
- DPLA API (free, API key) — cross-institutional US archive search
- Antenati IIIF (free) — Italian civil records image viewer, linked by comune/year

All APIs are free. No paid services.

**Complexity:** High. Multiple external API integrations, each with different auth models and response formats. Needs a server-side proxy layer for API keys and rate limiting. Result display UI per source. FamilySearch OAuth 2 is the most complex piece.

### G-18: CEMLA Immigration Record Search

**Gap:** CEMLA (Centro de Estudios Migratorios Latinoamericanos) holds 4.4M+ Argentine immigration records covering ship passenger lists from 1882 through the 1960s. This is the primary digital source for Italian/Spanish immigration to Argentina — directly relevant to families with Italian-Argentine connections. CEMLA has no public API but has a searchable website.

**CFLSR impact:** Medium. High value for families with Argentine immigration history (which this family has). Niche but irreplaceable for that use case.

**Scope:** Server-side search that queries CEMLA's website, parses HTML results, and presents them within Family Book. Could use a headless browser (Playwright), an LLM-assisted browser tool (Cloudflare Browser Rendering or similar), or direct HTML parsing if the site structure is stable.

**Complexity:** Medium-high. Web scraping is fragile and requires maintenance. Need graceful degradation when the site changes. Rate limiting and caching to be respectful. Consider a "search CEMLA" button that opens results inline vs. linking out as a simpler fallback.

### G-19: Rich Multimedia Playback and Document Support

**Gap:** The backend already accepts video (mp4, webm, quicktime — 100MB limit) and audio (opus, mp3, m4a, ogg — 25MB limit), but the frontend cannot play them. All media renders as `<img>` tags — uploaded videos show as broken images. Audio files cannot even be uploaded from the UI because file inputs only accept `image/*,video/*`, not `audio/*`. PDFs and documents are not accepted at all. Voice recordings, family videos, scanned documents, and old letters are core family history content that the app should handle natively.

**CFLSR impact:** High. Multimedia is what makes a family archive feel alive. A voice recording of a grandparent, a home video from the 1980s, or a scanned immigration document are irreplaceable family artifacts. Without playback, the app is photo-only.

**Scope:**
- Add HTML5 `<video>` element for video media (with controls, poster frame from thumbnail)
- Add HTML5 `<audio>` element for audio media (with controls, waveform optional)
- Add `audio/*` to all file input `accept` attributes
- Add `application/pdf` and `application/msword` to `ALLOWED_MIME_TYPES`
- Add PDF viewer (browser native via `<iframe>` or `<embed>`, or pdf.js for richer experience)
- Update media gallery, moment card, person sidebar, and person page templates to check `media_type` and render the appropriate HTML element
- Add document classification to media (G-09 overlap): distinguish memories from evidence/documents

**Complexity:** Medium. Backend already handles storage and serving for video/audio. The main work is frontend: conditional rendering by media_type, HTML5 player elements, PDF support, and updating file input accept attributes across all upload surfaces.

### G-20: Family Timeline with Branch Filtering

**Gap:** Expands G-08 (Timeline View). Beyond a flat chronological list of all family events, users want to see the timeline for a specific branch: "Show me the Santos line from Italy to Argentina to the USA." This requires filtering the timeline by a selected person's ancestors or descendants, effectively telling the story of one family line through time.

**CFLSR impact:** Medium-high. A branch timeline turns the family tree from a spatial map into a narrative. It's the feature that makes someone say "let me show you our family's journey."

**Scope:** Build on the timeline view (G-08) with a branch-filter picker. Select a person, choose "ancestors" or "descendants", and the timeline shows only events for that lineage. Events include births, deaths, marriages, immigration moments, and stories.

**Complexity:** Medium (on top of G-08). Requires ancestry/descendancy path computation from the graph data, then filtering the timeline query by those person IDs.

### G-21: AI Family Memorial

**Gap:** Long-horizon feature. Use stored voice recordings, biographical data, stories, and research notes to create an AI-powered conversational memorial of a family member. A grandchild could "talk to" a great-grandparent they never met, with responses grounded in that person's actual life history, voice, and personality.

**CFLSR impact:** Transformative (if done well). This is the kind of feature that makes Family Book irreplaceable and emotionally powerful.

**Scope (future):**
- Voice synthesis from stored recordings (ElevenLabs, OpenAI TTS, or open-source models)
- LLM-powered conversational agent grounded in person's bio, stories, moments, and research notes
- Consent and ethics framework: who can create an AI version of a family member? Living vs. deceased?
- Opt-in per person: explicit flag allowing or disallowing AI memorial creation

**Complexity:** Very high. Requires AI/ML integrations, careful prompt engineering, ethical guardrails, and potentially significant API costs. Not a near-term sprint candidate but the groundwork (voice recordings, rich biographical data, detailed stories) is being laid now.

**Prerequisites:** G-19 (multimedia — need voice recordings first), rich bio and stories content, research notes (S17), source citations (G-07).

### G-22: Life Story Fields (Obituary, Education, Career, Organizations, Physical Attributes)

**Gap:** The Person model has identity, dates, places, bio, and contact — but no structured fields for the life-story data that genealogists routinely track and that makes a person record feel complete: education history, career/profession history, organizational memberships (fraternal orders, churches, social clubs, military units), and obituary text.

**CFLSR impact:** Medium-high. These are among the most commonly recorded genealogy data points. Education and career connect to immigration stories ("came to America and worked at the steel mill"). Organizations connect to community identity ("founding member of the Italian-American Society"). Obituaries are often the richest single-source document for a person and contain names, dates, and relationships not recorded anywhere else.

**Scope:**
- **Obituary**: Text field on Person (long text, 5000+ chars). Not encrypted — obituaries are public documents. Optionally include `obituary_source` (newspaper name, date, URL).
- **Education**: JSON array field on Person — `[{institution, degree, field_of_study, year_start, year_end, notes}]`. Add/remove UI in sidebar and edit page.
- **Career**: JSON array field on Person — `[{employer, title, year_start, year_end, location, notes}]`. Add/remove UI.
- **Organizations**: JSON array field on Person — `[{name, role, year_joined, year_left, notes}]`. Covers clubs, churches, lodges, military units, unions, societies.
- **Physical attributes**: Structured fields with international unit support:
  - `height` (stored in cm, displayed in cm or feet/inches based on user locale preference)
  - `weight` (stored in kg, displayed in kg or lbs based on locale)
  - `eye_color` (String, free text or enum: brown, blue, green, hazel, gray, amber, other)
  - `hair_color` (String, free text or enum: black, brown, blonde, red, gray, white, other)
  - `shoe_size` (stored with sizing system: US, EU, UK, CM — JSON: `{size, system}`)
  - All stored in a standard internal unit with display conversion. A family-level or user-level locale preference controls display units.
- **Contact expansion**:
  - `phone_numbers`: JSON array — `[{number, type, label}]` (type: mobile, home, work; E.164 format for storage, localized display). Encrypted.
  - `addresses`: JSON array — `[{label, street, city, state, postal_code, country_code, type}]` (type: home, work, mailing). Encrypted.
  - These supplement existing messaging contacts (WhatsApp, Telegram, Signal, email).
- All fields included in revision snapshots for audit trail.
- All fields surfaced in person profile page and tree sidebar Details tab.
- Physical attributes are not encrypted (not sensitive PII). Phone numbers and addresses are encrypted (same as existing contact fields).

**Complexity:** Medium-high. Multiple new fields across different sensitivity tiers, one migration, schema/API updates, internationalized unit conversion logic, and UI for structured add/remove lists. Follows the same JSON-in-text-column pattern as `languages`.

### G-23: Genetic Profile and Family Health Intelligence

**Gap:** The current `medical_history` field is a single encrypted text blob. It cannot be queried across persons, cannot distinguish inherited vs acquired conditions, and cannot track treatments or outcomes. There is no genetic data support at all — no haplogroups, no admixture data, no way to visualize "where did our family come from genetically?" or "what health conditions run in our family?"

**CFLSR impact:** High. Family health patterns are one of the most practically valuable outputs of genealogy. Knowing that heart disease appears in three generations of the paternal line, or that a specific genetic mutation is present, has real medical value. Haplogroups and admixture data add a deep-ancestry dimension that connects to the immigration story.

**Scope:**
- **Genetic profile** (per person):
  - `maternal_haplogroup` (String, e.g., "H1a1")
  - `paternal_haplogroup` (String, e.g., "R1b-L21")
  - `admixture` JSON array: `[{ethnicity, percentage, source}]` (e.g., "Southern Italian 42%, Iberian 18%")
  - `dna_test_provider` (String, e.g., "23andMe", "AncestryDNA", "MyHeritage")
  - All encrypted at rest
- **Structured medical conditions** (replacing or extending `medical_history`):
  - JSON array: `[{condition, onset_age, status, severity, treatment, is_inherited, hereditary_line, notes}]`
  - `status` enum: active, resolved, managed, unknown
  - `hereditary_line`: free text for "paternal" / "maternal" / specific ancestor
  - Encrypted at rest
- **Family health dashboard**:
  - Cross-person view: "Conditions in this family" showing which conditions appear in which persons and which line
  - Pattern detection: highlight conditions that appear in 2+ related persons
  - Accessible from tree page or admin page
- **Privacy considerations**: genetic and medical data is the most sensitive content in the app. Requires explicit decision on visibility (all family members? opt-in per person? admin-only?).

**Complexity:** High. New encrypted structured fields, migration, UI for structured condition/genetic entry, cross-person health aggregation query, privacy/consent design. The family health dashboard is the most complex piece — it requires querying encrypted JSON across multiple persons.

## Tier 3 — Platform Completeness (Later)

These are important for a mature genealogy tool but not blocking the core collaborative loop or power-user retention. G-10 (GEDCOM) has been promoted to Tier 2 due to its role as the universal platform connector.

### G-11: Fan Chart / Pedigree View

**Gap:** The tree layout is top-down from root. Genealogists also use ancestor-focused views (pedigree chart from a selected person upward) and fan/radial charts.

**Complexity:** High. Alternative D3 layouts.

### G-12: Duplicate Person Detection and Merge

**Gap:** No detection when two users create the same person with slightly different names. No merge capability.

**Complexity:** High. Fuzzy matching, merge conflict resolution, relationship re-linking.

### G-13: Date Math and Age Display

**Gap:** The app stores dates but doesn't compute ages. "Maria was 23 when she married" or "born 4 years after his brother" — useful genealogy context.

**Complexity:** Low-medium. Date parsing from `birth_date` + `birth_date_precision`, age calculation at events.

### G-14: Print / Export Family Sheet

**Gap:** No way to generate a one-page PDF of a person's record to bring to an interview with an elderly relative.

**Complexity:** Medium. Server-side PDF generation or print-optimized CSS.

### G-15: Visual Distinction for Relationship Types on Tree

**Gap:** Adoption, step-parent, and biological parent-child relationships all render identically on the tree. The data model distinguishes them (ParentChild.kind) but the visualization doesn't.

**Complexity:** Low-medium. Different line styles/colors/labels in tree.js renderNode.

## Recommended Sprint Sequence

### Sprint 17: Tree Discovery and Research Foundation

Packets: G-01 (tree search), G-02 (content hierarchy), G-03 (research notes)

Rationale: These three gaps have the highest ratio of CFLSR impact to implementation complexity. Tree search is the single most impactful navigation improvement. Content hierarchy is a quick win. Research notes unlock the genealogy-researcher workflow.

### Sprint 18: Completeness and Detail Depth

Packets: G-04 (completeness prompts), G-05 (sidebar detail expansion)

Rationale: Once the tree is searchable and person pages are better organized, the next bottleneck is motivating contribution and reducing edit-page detours. These two together make the "see a gap, fill it" loop work.

### Sprint 19: External Record Integration Foundation

Packets: G-10 (GEDCOM import), G-17 (external record search), G-18 (CEMLA)

Rationale: GEDCOM import is the single most important onboarding accelerator — it lets users with years of research in Ancestry, FamilySearch, or MyHeritage bring their data into Family Book. External record search (FamilySearch API, newspaper APIs, NARA, Antenati IIIF) turns the app into a research workspace rather than a display layer. CEMLA is high-value for the family's Italian-Argentine immigration connections. All APIs are free.

### Sprint 20: Family Calendar and Relationship Intelligence

Packets: G-16 (family calendar), G-06 (relationship calculator), G-15 (visual relationship types)

Rationale: The calendar auto-populates from existing birth/death/marriage dates and moments, rewarding data entry with a living family tool. The relationship calculator is the highest-delight feature in the backlog. Visual relationship types complement both. Together these make the app feel like something you *visit regularly* rather than update occasionally.

### Sprint 21: Multimedia, Timeline, and Life Story Depth

Packets: G-19 (multimedia playback + documents), G-08 (timeline view), G-20 (branch-specific timeline), G-22 (life story fields)

Rationale: Multimedia playback fixes a real gap — the backend already accepts video/audio but the frontend can't play them. Adding document support (PDFs, scans) completes the archive story. Life story fields (obituary, education, career, organizations) make person records feel genuinely complete. The timeline view is the natural next surface after the calendar, and branch filtering makes it personal. Together these turn Family Book into a full multimedia family archive with narrative history. G-19 also lays critical groundwork for the AI memorial feature (G-21) by enabling voice recordings.

### Sprint 22: Genetic Profile and Family Health Intelligence

Packets: G-23 (genetic profile + structured medical conditions + family health dashboard)

Rationale: This is a dedicated sprint because genetic and medical data is the most sensitive content in the app and requires careful encrypted-field design, privacy policy decisions, and a cross-family aggregation layer. Haplogroups and admixture connect to the deep ancestry story. Structured medical conditions enable the "what runs in our family?" query that has real practical health value. The family health dashboard is the most complex single feature in the backlog.

### Sprint 23+: Power User Depth and AI Foundation

Packets: G-07 (source citations), G-09 (document attachment as evidence), G-13 (date math)

These features make genealogy buffs *live* in the app. Source citations add research credibility, document-as-evidence distinguishes proof from memories, and date math adds genealogy-friendly context.

### Long Horizon: AI Family Memorial

Packet: G-21 (AI voice clone / conversational memorial)

Prerequisites: G-19 (voice recordings), G-22 (life story fields), G-23 (genetic/health data), rich bio/stories content, source citations. Requires AI/ML integration, ethical consent framework, and potentially significant API costs. Not scheduled but the groundwork is being laid across S17-S22.

## Integration Research Summary

### Country-Specific Resources

| Country | Best APIs | Manual-Only Sources |
|---|---|---|
| USA | FamilySearch, Chronicling America, NARA Catalog, DPLA, WikiTree, Internet Archive | Find A Grave, Fold3, Ellis Island, SSDI |
| Australia | Trove (newspapers), FamilySearch | State archives, BDM registries |
| Argentina | FamilySearch (best digital path), CEMLA (scraping required) | Provincial civil registries, AGN, Jewish community records (AMIA, JCA) |
| Italy | FamilySearch, Antenati IIIF (civil records) | Parish records (pre-1806), comunal archives, military leva records |

### Key Integration Facts

- **All recommended APIs are free.** No paid services in the integration roadmap.
- **FamilySearch API covers all four countries** — it is the single highest-value integration.
- **GEDCOM import covers all platforms** — it is the universal onboarding path regardless of which tool the user comes from.
- **CEMLA has no API** — requires HTML parsing or headless browser. Fragile but irreplaceable for Argentine immigration research.
- **Antenati uses IIIF** — images can be embedded via a standard viewer protocol, but there is no name-search API. Users must know the ancestral comune and approximate dates.
- **Newspaper APIs (Chronicling America + Trove)** are the easiest integrations — simple REST, no auth, high discoverability for "search for this person" features.
