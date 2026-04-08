# 📖 Family Book

**A private, self-hosted family tree and archive.** Your family's story, on your terms.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)

### Deploy in One Click

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.app/new/template?template=https://github.com/tymrtn/family-book)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/tymrtn/family-book)

Or with Docker:
```bash
git clone https://github.com/tymrtn/family-book.git && cd family-book
cp .env.example .env   # Edit with your values
docker compose up -d
# Open http://localhost:8000
```

---

## 🎮 Live Demo

**→ [family-book-production.up.railway.app](https://family-book-production.up.railway.app)**

Browse a demo family tree with seed data. No sign-up required to explore. This is a live instance running the latest `main` branch with a fictional demo family so you can see what Family Book looks like before deploying your own.

---

## Your family's memories don't belong to Facebook

Every photo you upload, every conversation you have, every relationship you map on a platform becomes training data for AI models. Your grandmother's recipe in a WhatsApp group is feeding a neural network right now. You agreed to it in a terms update you never read.

Platforms change without asking. WhatsApp rewrites its privacy policy. Instagram kills features. Ancestry gets acquired. Your data follows the corporate roadmap, not yours.

Governments block platforms overnight. Russia restricted Telegram and WhatsApp. Families who kept their archives on those services lost access with no warning. If your country bans the app, your memories go dark.

Your family's data has real value. Today you give it away for free. As personal data licensing matures, you will want to decide who accesses it and on what terms. You can't license what you don't control.

A SQLite file on your own server outlives every startup, every acquisition, every terms-of-service change. No subscription to lapse. No company to shut down. Your great-grandchildren can open it in 50 years.

Family Book gives you that file.

---

## Why Family Book?

Every family has a story. Photos on someone's phone. Names nobody remembers. A great-grandmother's maiden name lost because nobody wrote it down. A voice note from a grandparent, sitting in a WhatsApp chat that'll be deleted when the phone dies.

Family Book exists because **your family's history shouldn't depend on a cloud service's business model**.

- **No subscription.** Deploy once, run forever.
- **No data mining.** Your family photos don't train anyone's AI.
- **No platform risk.** You own the server, the database, the files. Move them anytime.
- **No walled garden.** Standard SQLite database. Export everything.

### How It's Different

| | Family Book | Ancestry.com | FamilySearch | MyHeritage |
|---|---|---|---|---|
| **Who owns your data?** | **You. Forever.** | Ancestry Inc. | LDS Church | MyHeritage Ltd. |
| Self-hosted | ✅ | ❌ | ❌ | ❌ |
| Free forever | ✅ | ❌ ($299/yr) | ✅ (limited) | ❌ |
| Own your data | ✅ SQLite file | ❌ | ❌ | ❌ |
| Privacy by default | ✅ | ❌ DNA selling | ❌ | ❌ |
| WhatsApp import | 🚧 Planned | ❌ | ❌ | ❌ |
| Multi-language | ✅ en/es/ru | Partial | ✅ | Partial |
| Open source | ✅ MIT | ❌ | ❌ | ❌ |

---

## Features

### 🌳 Interactive Family Tree
A D3.js-powered tree visualization with branches, partnerships, and multi-generational navigation. Click any person to see their profile, relationships, and photos.

### 👤 Rich Person Profiles
Birth dates (with fuzzy precision — "about 1943" is valid), locations, languages spoken, patronymics, maiden names, nicknames. Every culture's naming conventions respected. Parent-child subtypes: biological, adoptive, step, foster, guardian.

### 📷 Media Gallery
Upload photos and documents. SHA-256 dedup means the same photo uploaded twice takes no extra space. Every file served through authenticated endpoints — no public URLs to your family photos.

### 📅 Moments
A family timeline. First steps. Weddings. Graduations. That Tuesday when grandpa told the story about the war. Each moment has comments and emoji reactions. Sort by date, filter by person, search by keyword.

### 🔐 Privacy by Design
Family Book uses role plus relationship distance. Owner/admin accounts can view all active profiles. Stewards can manage visible non-staff profiles. Members and viewers only see visible relatives connected within the configured family-graph distance. Contact, medical, and genetic fields are further restricted by per-profile privacy policy.

### 🌍 Multi-Language
English, Spanish, Russian out of the box. Add any language with a JSON file. Names render in their native script — Бабушка Юки stays Бабушка Юки.

### 📱 PWA
Install on your phone. Works offline for browsing. Feels native. No app store required.

### 💾 Automatic Backups
Daily SQLite backups to the persistent volume. Restore with one command. Your database is a single file — copy it anywhere.

---

## Quick Start

### Local Development

```bash
git clone https://github.com/tymrtn/family-book.git
cd family-book

cp .env.example .env    # Edit with your values
uv sync                 # Install dependencies
uv run alembic upgrade head   # Create database
uv run python -m app.seed     # Load demo family (optional)

uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open [localhost:8000](http://localhost:8000). You'll see the landing page. Register, add your first family member, start building.

### Deploy to Railway (recommended)

```bash
# Install Railway CLI: https://docs.railway.com/guides/cli
railway login
railway init --name family-book
railway up
railway domain    # Get your public URL
```

Set environment variables:
```
SECRET_KEY=<generate with: python3 -c "import secrets; print(secrets.token_hex(32))">
FERNET_KEY=<generate with: python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
DATABASE_URL=sqlite:////data/family.db
DATA_DIR=/data
BASE_URL=https://your-app.up.railway.app
LOAD_DEMO_DATA=false
BOOTSTRAP_ADMIN_EMAIL=you@example.com
BOOTSTRAP_ADMIN_FIRST_NAME=Admin
BOOTSTRAP_ADMIN_LAST_NAME=User
```

Railway and Docker deployments do not load the demo family by default. Set `LOAD_DEMO_DATA=true` only if you explicitly want the fictional sample tree on startup.
On a brand new empty deployment, set `BOOTSTRAP_ADMIN_EMAIL` so the app creates your first admin profile automatically at startup. After first login, you can edit that profile normally.
Sensitive person contact and medical fields are protected through the application persistence layer. The current protection and backup contract is documented in [`docs/ops/protection-and-backup-contract.md`](docs/ops/protection-and-backup-contract.md).
The current Railway release model, including staging and production flow, is documented in [`docs/ops/railway-release-flow.md`](docs/ops/railway-release-flow.md).

### Deploy with Docker

```bash
docker compose up -d
```

The `docker-compose.yml` includes the app, persistent volume for `/data`, and optional Matrix bridge for WhatsApp/Messenger import.
Set explicit immutable image references for the bridge services in `.env` before using Compose; the stack intentionally refuses to default to mutable `:latest` tags.

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend | Python 3.12 + FastAPI | Async, type-safe, great for APIs |
| Database | SQLite (WAL mode) | Single file, zero config, fast |
| ORM | SQLAlchemy 2.0 + Alembic | Async support, migrations |
| Frontend | Jinja2 + HTMX | Server-rendered, no build step, instant interactivity |
| Tree | D3.js | The gold standard for data visualization |
| Auth | Magic links (passwordless) | No passwords to forget or leak |
| Media | Local filesystem + SHA-256 dedup | Simple, reliable, deduplicated |
| i18n | JSON locale files | Easy to add languages |
| Deploy | Docker + Railway | One-click cloud or self-hosted |

### Why Not React/Vue/Angular?

Family Book is deliberately **not a SPA**. Server-rendered HTML + HTMX gives you:
- No build step (no webpack, no node_modules, no 200MB of JavaScript tooling)
- Works without JavaScript (graceful degradation)
- Instant page loads (HTML is fast)
- Easy to understand (read the template, see the page)

HTMX handles the interactive bits: inline editing, live search, modal dialogs. D3.js handles the tree. That's it.

---

## Architecture

```
app/
├── main.py              # FastAPI app + startup
├── config.py            # Settings from environment
├── models/              # SQLAlchemy models
│   ├── person.py        # Person, with all name variants
│   ├── relationships.py # ParentChild, Partnership
│   ├── media.py         # Media files + metadata
│   ├── moments.py       # Timeline events
│   └── auth.py          # Users, sessions, magic links
├── routes/              # API + page routes
│   ├── persons.py       # CRUD + search
│   ├── relationships.py # Add/remove connections
│   ├── tree.py          # Tree data endpoint for D3
│   ├── media.py         # Upload + authenticated serving
│   └── moments.py       # Timeline CRUD
├── services/            # Business logic
├── templates/           # Jinja2 + HTMX pages
│   ├── base.html        # Layout with nav
│   ├── tree.html        # D3 tree visualization
│   ├── person.html      # Profile page
│   ├── people.html      # People grid
│   └── partials/        # HTMX fragments
├── static/              # CSS, JS, D3 config
├── importers/           # WhatsApp, Messenger, GEDCOM (planned)
└── matrix/              # Matrix bridge integration (planned)
data/                    # Persistent volume
├── family.db            # SQLite database
├── media/               # Uploaded files
└── backups/             # Daily backups
locales/                 # i18n: en.json, es.json, ru.json
```

### Key Design Decisions

**Siblings are derived, not stored.** Two people who share a parent are siblings. No explicit sibling table — the relationship is computed from parent-child links. This prevents impossible states (A is B's sibling but B is not A's).

**Partnerships, not marriages.** The `Partnership` model supports married, domestic_partner, engaged, separated, divorced, widowed, and other. No gender constraints. Same model for every relationship type.

**Fuzzy dates.** Not everyone knows their grandmother's exact birthday. `birth_date_raw` stores what the family member actually said ("about 1943", "spring 1967"). `birth_date_precision` indicates year/month/day confidence.

**Source tracking.** Every Person, relationship, and media file has a `source` field: manual, gedcom_import, whatsapp, messenger, email. When you import from WhatsApp in 2026, the fact that "this photo came from WhatsApp" is preserved forever.

---

## Vision

Family Book isn't just a family tree app. It's the **private social network your family actually needs**.

### The Problem

Your family's memories are scattered across platforms that don't care about your family:

- **WhatsApp** — Photos and voice notes buried in group chats. Phone dies, memories die.
- **Facebook** — Your family photos train their AI. Your grandmother's face is in a dataset.
- **iCloud/Google Photos** — Shared albums with no context. Who is this person? What year was this?
- **Ancestry.com** — $299/year to see your own family tree. Your DNA sold to insurance companies.
- **Physical albums** — Rotting in a closet in Portland. One flood away from gone.

### The Vision

A single place where:

1. **Every family memory flows in automatically.** WhatsApp photos arrive via Matrix bridge. Email forwards get parsed. Old scanned photos get uploaded with dates and context.

2. **Access follows role and family context.** Your cousin in Tokyo can see a different slice of the archive than a steward or admin. Graph distance controls baseline visibility, while contact and sensitive fields stay behind stricter privacy policies.

3. **The archive is portable.** Admins can download GEDCOM, full archive ZIP exports, and operational backups. Your family can leave with the data instead of negotiating with a vendor.

4. **Every fact has provenance.** "Grandma was born in 1943" — who said that? When? Was it from a GEDCOM import, a WhatsApp message from Aunt Yuki, or a birth certificate scan? Source tracking on every piece of data.

5. **It works for every culture.** Patronymics (Russian), maiden names (Western), Eastern name order (Japanese), fuzzy dates ("about 1943"), and relationship labels that respect the actual complexity of modern families — step-parents, adoptive parents, guardians, domestic partners.

6. **It survives you.** SQLite database. Single file. Copy it to a USB drive. Your great-grandchildren can open it in 50 years with any programming language on any platform. No vendor lock-in. No subscription to expire. No company to go bankrupt.

### The Bridge Problem (and the Opportunity)

The biggest technical challenge is importing from messaging platforms. WhatsApp, Messenger, and iMessage don't offer easy APIs for personal data export. The current architecture uses Matrix bridges (Mautrix) to connect to these platforms using your own account — no business verification needed.

But for non-technical families, setting up Matrix bridges is unrealistic. A potential path: a hosted bridge service (like a "Family Book Connector") that handles the Twilio/WhatsApp Business API complexity, pre-approved for personal family use. One-click enable, and your family's WhatsApp photos flow into your Family Book automatically.

This is an unsolved problem in the self-hosted space. Whoever solves it unlocks a massive market of families who want to own their data but can't navigate API onboarding.

---

## Roadmap

- [x] **Phase 1** — Core models, API, tests (45/45 green)
- [x] **Phase 2A** — Media gallery, Moments timeline, Comments, Reactions
- [x] **Phase 2B** — HTMX frontend: tree, profiles, people grid, media, moments, auth
- [x] **Phase 3** — Docker, automated backup, i18n, PWA, security middleware
- [ ] **Phase 4** — WhatsApp import via Matrix/Mautrix bridge
- [x] **Phase 5** — GEDCOM export and full archive export
- [ ] **Phase 6** — Facebook/Messenger photo import
- [ ] **Phase 7** — Push notifications, email digests
- [ ] **Phase 8** — Advanced search, timeline filtering, family statistics

---

## Contributing

Family Book is MIT licensed. Contributions welcome! See **[CONTRIBUTING.md](CONTRIBUTING.md)** for full details on setting up your dev environment, running tests, and submitting PRs.

```bash
make dev      # Start dev server with auto-reload
make test     # Run the test suite
make seed     # Load demo data
make migrate  # Run database migrations
```

Please read `CLAUDE.md` for architecture rules before submitting PRs.

---

## FAQ

**Q: Can I import from Ancestry/FamilySearch/MyHeritage?**
GEDCOM is the interoperability path. Family Book now supports GEDCOM export and archive export, and GEDCOM import support continues to evolve around the existing parser/import pipeline.

**Q: What about DNA/genetic data?**
Family Book can store genetic and medical context, but those fields default to stricter privacy rules than ordinary profile data.

**Q: Can multiple family members use it?**
Yes. Magic link auth means anyone with an email can log in, while role and family-graph distance determine what they can see and edit.

**Q: How do I back up?**
Automated daily backups run via cron. The database is a single SQLite file at `/data/family.db`. Copy it anywhere. Restore by replacing the file and running migrations.

**Q: How do I leave with my data?**
Admins can download a GEDCOM export, a full archive ZIP with JSON and media, or the latest operational backup ZIP.

**Q: Is there a hosted version?**
Not yet. Self-hosted only. If there's demand, a hosted option may come later.

---

## Part of the Sovereign Stack

Family Book is part of [**The Sovereign Stack**](https://github.com/tymrtn/sovereign-stack) — a portfolio of tools for personal data sovereignty. Own your lineage, your email, your content, and your physical footprint. Stop renting your digital life.

---

## License

MIT — do whatever you want with it.

---

*Built with love for Mia.* 🌙
