# FB-034: Wiki Biography Enhancement and Rich Text Editor

## Objective

Enhance the person wiki pages to follow a Wikipedia-style biography section structure adapted for family history and genealogy, surface all relevant Person model fields in the wiki, replace raw JSON textareas with structured form editing for array fields, and integrate the Trix rich text editor for free-text narrative fields so users never need to know any markup language.

## Why / KPI

**CFLSR impact:** High. The wiki is the narrative layer of Family Book — it turns structured data into readable family stories. Currently, many Person model fields are not surfaced in the wiki (languages, physical attributes, burial details, source citations), the section structure doesn't follow the Wikipedia biography convention users expect, and JSON array editing requires raw JSON input which is unusable for non-technical family members. A rich text editor for narrative fields (bio, obituary, research notes) gives users formatting without markup knowledge.

**User feedback:** User requested Wikipedia biography template alignment, genealogy-specific section additions mapped to the existing data model, and a WYSIWYG rich text editor.

## Research Summary

### Rich Text Editor Selection: Trix

After evaluating TinyMCE, Quill.js, Tiptap, CKEditor 5, ProseMirror, Summernote, Froala, Editor.js, and Trix:

**Winner: [Trix](https://trix-editor.org/) by Basecamp (37signals)**

| Criterion | Trix |
|-----------|------|
| License | MIT — no GPL concerns, no branding, no API keys |
| Bundle size | ~80KB gzipped via CDN |
| Framework requirement | None — uses `<trix-editor>` custom element |
| HTML output | Clean semantic HTML, auto-synced to hidden `<input>` |
| HTMX compatibility | Excellent — built for server-rendered apps (Rails/Turbo), form submissions "just work" |
| Build step required | No — CDN script tag only |
| Formatting scope | Bold, italic, links, headings, lists, blockquotes, code, strikethrough — intentionally limited, perfect for biographical text |

**Why not the others:**
- TinyMCE/CKEditor: GPL v2+ license conflict, heavy bundles (200-350KB)
- Quill: `getSemanticHTML()` bugs in v2.0, uncertain maintenance trajectory
- Tiptap: Requires a bundler (no CDN drop-in), must build custom toolbar
- Editor.js: JSON output (not HTML), requires rendering pipeline on every read path
- Summernote: jQuery dependency
- Froala: Commercial license only

### Wiki Engine Embedding: Not Viable

No existing wiki engine (Wiki.js, MediaWiki, TiddlyWiki, DokuWiki, Gollum) can be embedded into a FastAPI application. They all require separate servers, separate databases, and their editors are not extractable components. The right approach is to enhance the existing HTMX section-editing architecture with a WYSIWYG editor per section.

## In Scope

### 1. Enhanced Wikipedia-Style Section Structure

Expand from 9 sections to 11, aligning with the [Wikipedia Template:Biography](https://en.wikipedia.org/wiki/Template:Biography) and adding genealogy-specific content from the Person data model.

| # | Section ID | Title | Data Source(s) | Edit Fields | Change |
|---|-----------|-------|---------------|-------------|--------|
| 1 | `summary` | Summary | display_name, dates, age, bio | `bio` | Enhanced: add computed age, languages |
| 2 | `early-life` | Early Life | birth_place, birth_country_code, parents, birth_last_name | `birth_place`, `birth_country_code`, `birth_date_raw`, `birth_last_name` | Enhanced: add maiden name |
| 3 | `education` | Education | education[] | `education` | Keep: structured form editing |
| 4 | `career` | Career | career[] | `career` | Keep: structured form editing |
| 5 | `personal-life` | Personal Life | partnerships, children, residence | `residence_place`, `residence_country_code` | Enhanced: add residence info |
| 6 | `organizations` | Organizations & Affiliations | organizations[] | `organizations` | Keep: structured form editing |
| 7 | `physical-description` | Physical Description | height, weight, eye_color, hair_color, blood_type | `height`, `weight`, `eye_color`, `hair_color`, `blood_type` | **NEW** |
| 8 | `later-life` | Later Life | medical_conditions[] (names only) | — | Simplified: residence moved to Personal Life |
| 9 | `death-legacy` | Death & Legacy | death_date_raw, burial_place, burial_cemetery_name, burial_country_code, burial_plot_number, obituary, obituary_source | `death_date_raw`, `burial_place`, `burial_cemetery_name`, `burial_country_code`, `burial_plot_number`, `obituary`, `obituary_source` | Enhanced: add full burial details |
| 10 | `sources` | Sources & Citations | source_detail, confidence | `source_detail`, `confidence` | **NEW** |
| 11 | `research-notes` | Research Notes | research_notes | `research_notes` | Keep |

**Privacy boundaries:** Genetic profile (haplogroups, admixture, dna_test_provider) and encrypted medical_history are NOT surfaced in wiki. Medical conditions show condition names only (existing behavior). Physical attributes are non-encrypted and safe for wiki display.

### 2. Trix Rich Text Editor Integration

Replace plain `<textarea>` with Trix WYSIWYG editor for the three free-text narrative fields:
- `bio` (Summary section)
- `obituary` (Death & Legacy section)
- `research_notes` (Research Notes section)

### 3. Structured Form Editing for JSON Arrays

Replace raw JSON `<textarea>` inputs with proper form UIs for:
- `education[]` — fields: institution, degree, field_of_study, year_start, year_end, notes
- `career[]` — fields: employer, title, year_start, year_end, location, notes
- `organizations[]` — fields: name, role, year_joined, year_left, notes

Each entry rendered as a fieldset with individual inputs, add/remove buttons.

### 4. HTML Sanitization

Add server-side HTML sanitization for Trix output using the `nh3` library (Rust-based, fast, safe).

## Out of Scope

- Genetic profile fields in wiki (encrypted, sensitive)
- Full medical condition details in wiki (only condition names shown)
- Custom wiki sections (user-defined sections)
- Wiki page versioning separate from Person revision history
- Collaborative real-time editing
- Image embedding in rich text (images handled through existing media system)

## Acceptance Criteria

### Section Structure
- [ ] Wiki pages display all 11 sections (when data exists) in the specified order
- [ ] Summary section shows computed age for living persons
- [ ] Summary section lists languages if present
- [ ] Early Life section shows maiden name (birth_last_name) when different from last_name
- [ ] Personal Life section includes residence information
- [ ] Physical Description section renders height, weight, eye/hair color, blood type
- [ ] Death & Legacy section includes full burial details (place, cemetery, country, plot)
- [ ] Death & Legacy section shows obituary_source as citation
- [ ] Sources & Citations section displays source_detail and confidence level
- [ ] Later Life section shows only medical condition names (no change to privacy)
- [ ] Empty Physical Description and Sources sections show "Add" prompt when user can edit

### Rich Text Editor
- [ ] Trix editor loads for bio, obituary, and research_notes fields in wiki edit mode
- [ ] Trix CDN assets (JS + CSS) load only on wiki edit pages (not globally)
- [ ] Rich text content round-trips correctly: edit → save → re-render with formatting preserved
- [ ] HTML is sanitized server-side before storage (allowed tags: p, br, strong, em, a, ul, ol, li, blockquote, h1, h2, h3, pre, code, del, figure, figcaption)
- [ ] Existing plain text content renders correctly (backward compatible)
- [ ] Wiki page renders rich text with `| safe` filter after sanitization

### Structured Form Editing
- [ ] Education entries edited via individual form fields (not raw JSON)
- [ ] Career entries edited via individual form fields (not raw JSON)
- [ ] Organization entries edited via individual form fields (not raw JSON)
- [ ] Add Entry / Remove Entry buttons work for each array type
- [ ] Form submission correctly serializes entries back to JSON for storage

### General
- [ ] Mobile layout unaffected (Trix is responsive by default)
- [ ] Keyboard accessible (Trix has built-in keyboard shortcuts)
- [ ] Root person redaction maintained across all new sections
- [ ] i18n keys added for all new section titles and field labels across 3 locales
- [ ] No regression on existing wiki functionality

## Likely Files

| File | Change |
|------|--------|
| `app/services/wiki_service.py` | Add 2 new section builders (physical-description, sources), enhance existing builders (summary with age/languages, early-life with maiden name, personal-life with residence, death-legacy with full burial), update SECTION order |
| `app/routes/wiki.py` | Update `SECTION_FIELD_MAP` with new sections and fields, add HTML sanitization on save, update field type routing in edit handler |
| `app/templates/wiki_person.html` | Render rich text fields with `\| safe`, update section display for new data |
| `app/templates/partials/wiki_edit_section.html` | Add Trix editor for narrative fields, structured forms for JSON arrays, Trix CDN includes |
| `locales/en.json` | ~20 new wiki section/field keys |
| `locales/es.json` | ~20 new wiki section/field keys |
| `locales/ru.json` | ~20 new wiki section/field keys |

## New Dependencies

| Package | Purpose | License | Size |
|---------|---------|---------|------|
| `nh3` | HTML sanitization (Rust-based) | MIT | ~2MB wheel |
| Trix (CDN) | Rich text editor | MIT | ~80KB gzipped |

## Implementation Notes

### Trix Integration Pattern

```html
<!-- In wiki_edit_section.html for narrative fields -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/trix@2/dist/trix.min.css">
<script src="https://cdn.jsdelivr.net/npm/trix@2/dist/trix.umd.min.js"></script>

<input id="wiki-{{ field }}" type="hidden" name="{{ field }}" value="{{ current_value }}">
<trix-editor input="wiki-{{ field }}"></trix-editor>
```

Trix auto-syncs its content to the hidden `<input>`. When HTMX submits the form, the rich HTML is included automatically. No manual JavaScript wiring needed.

### HTML Sanitization Pattern

```python
import nh3

ALLOWED_TAGS = {"p", "br", "strong", "em", "a", "ul", "ol", "li",
                "blockquote", "h1", "h2", "h3", "pre", "code", "del",
                "figure", "figcaption", "div"}
ALLOWED_ATTRIBUTES = {"a": {"href", "title"}}

def sanitize_html(value: str) -> str:
    return nh3.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
```

### Structured Array Form Pattern

```html
<!-- Replace raw JSON textarea with structured fields -->
<div class="wiki-array-entries" data-field="education">
  {% for entry in entries %}
  <fieldset class="wiki-array-entry">
    <input name="education[{{ loop.index0 }}].institution" value="{{ entry.institution or '' }}">
    <input name="education[{{ loop.index0 }}].degree" value="{{ entry.degree or '' }}">
    <!-- ... more fields ... -->
    <button type="button" onclick="this.closest('.wiki-array-entry').remove()">Remove</button>
  </fieldset>
  {% endfor %}
  <button type="button" onclick="addWikiArrayEntry('education')">Add Entry</button>
</div>
```

The route handler parses indexed form fields back into a list of dicts.

### Backward Compatibility

Existing plain text content in bio, obituary, research_notes will render correctly because:
1. Plain text without HTML tags passes through `nh3.clean()` unchanged
2. The `| safe` filter in templates just means "don't escape" — plain text still renders as text
3. The Trix editor can load plain text as initial content (it wraps it in `<div>` blocks)

### Wikipedia Biography Template Mapping

| Wikipedia Section | Family Book Section | Notes |
|---|---|---|
| Introduction | Summary | Lead paragraph with name, dates, and bio |
| Early life | Early Life | Birth info, parents, maiden name |
| Education | Education | Structured education entries |
| Career | Career | Structured career entries |
| Marriage and children | Personal Life | Partnerships + children + residence |
| (no equivalent) | Organizations & Affiliations | Genealogy-specific |
| (no equivalent) | Physical Description | Genealogy-specific |
| Later life | Later Life | Health conditions overview |
| Death | Death & Legacy | Full burial details + obituary |
| (no equivalent) | Sources & Citations | Genealogy-research-specific |
| (no equivalent) | Research Notes | Genealogy-research-specific |
| Published works | — | Not applicable for family bios |
| Recognition / Honours | — | Could be added later if needed |
| See also | — | Cross-links handled by wiki index |
| References | Sources & Citations | Mapped to source_detail + confidence |

## Complexity

Medium. The Trix integration is low complexity (CDN + custom element). The section structure enhancement is medium (new builders, field mapping). The structured form editing is the highest-complexity slice (parsing indexed form fields, add/remove JS, rendering entries as fieldsets). The nh3 dependency is a one-line install.

## Definition of Done

- Wiki pages follow Wikipedia-style biography section ordering with genealogy additions
- All Person model biographical fields surfaced in appropriate wiki sections
- Trix WYSIWYG editor active for bio, obituary, and research_notes
- HTML sanitized server-side via nh3
- JSON array fields edited via structured forms (not raw JSON)
- i18n parity across all 3 locales
- No regression on existing wiki, root person redaction, or test suite
