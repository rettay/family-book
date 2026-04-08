# Family Book Market Comparison and Roadmap

Report date: April 7, 2026

Prepared from:

- `docs/bizanalysis/deep-research-report.md`
- `docs/bizanalysis/compass_artifact_wf-ea0d0b79-f3a4-4447-9fb8-5a8341724aad_text_markdown.md`
- Current repository inspection as of this report date
- Target stated by founder: 500 paying users by December 31, 2026

## Executive take

Family Book should not try to beat Ancestry, MyHeritage, FamilySearch, or Findmypast on the core genealogy-research loop. Those products win through record collections, hint engines, DNA networks, and search scale. Family Book's credible wedge is different: a private, family-owned living archive that combines a family graph, rich profiles, media, stories, and data portability.

The product is stronger than one analyst report assumed. It now has an interactive tree API/UI, parent-child and partnership modeling, GEDCOM import with duplicate preview, external record search across free/public sources, wiki-style biographies, user-authored stories, relationship path calculation, revisions, backups, PWA plumbing, and Matrix/email ingestion scaffolding. It is not just a contact directory.

However, the product is not yet commercially ready as a privacy-first app. The largest trust gap is that current access control does not implement the README's "graph distance determines what you can see" promise. In `app/access_control.py`, active non-admin users can view full profile/contact details for any visible person and can manage any visible active person, not just themselves or close relatives. This is fix-or-change-copy before asking users to pay.

For the 500-paying-user goal, prioritize a consumer/prosumer "private family archive" motion over a high-net-worth family-office motion. HNW can be a future high-ARPU expansion, but 500 paying users by December 31, 2026 requires short sales cycles, self-serve onboarding, and clear pricing.

Recommended positioning:

> Family Book is a private family archive for people who want a family tree, family stories, and family media without giving their relatives' lives to a data-mining platform.

Recommended first commercial offer:

- Hosted Family plan: $99/year founding price, later $149/year, with a clear storage cap.
- Hosted Steward plan: $249/year for larger archives, priority support, higher storage, and advanced export/backup controls.
- Self-hosted Support plan: $79/year for guided updates, backup/export tooling, and support. Do not make this the main 2026 revenue motion.
- Optional physical book/export upsell: start with downloadable print-ready PDF, then partner for fulfillment.

At 500 paying users, annualized revenue is roughly $49,500 at $99/year, $74,500 at $149/year, or $124,500 at $249/year. That is enough to validate willingness to pay, but not enough to support heavy B2B sales or a large infrastructure burden.

## Market baseline from the reports

Both analyst reports agree on the important market structure:

- Record and DNA incumbents are hard to attack directly. Ancestry, MyHeritage, FamilySearch, and Findmypast are built around record search, matching, DNA, hints, and large user networks.
- Privacy and ownership are real differentiators. Users are frustrated by subscriptions, shared-tree edits, opaque data practices, and vendor lock-in.
- Self-hosted/open-source tools already serve privacy-conscious genealogists, but usually demand technical administration or have dated workflows.
- Story-first products such as Storyworth, Remento, and Storied prove that many families will pay for memories, prompts, books, and emotional deliverables, not only formal genealogy.

The analyst reports differ on the best first wedge. One report recommends high-net-worth family offices. The other recommends privacy-first living-family collaboration. For a goal of 500 paying users by December 31, 2026, the collaboration wedge is the better primary path. Family offices are attractive later because ARPU is high, but the product would need higher trust posture, security proof, concierge onboarding, B2B sales material, and a much slower relationship-driven sales cycle.

## Current Family Book capability assessment

Current strengths visible in the repository:

| Area | Current evidence | Market significance |
|---|---|---|
| Family graph | Parent-child kinds include biological, adoptive, step, foster, guardian, and unknown; partnerships include married, domestic partner, co-parent, engaged, and other in `app/models/relationships.py`. | More culturally and socially flexible than many traditional genealogy schemas. |
| Interactive tree | `/api/tree` filters people by branch, country, and living/deceased status, returns person summaries, parent-child relationships, partnerships, media counts, and current occupation in `app/routes/tree.py`. | Gives the product the expected "family tree app" surface. |
| Rich living profiles | Person records include multilingual/naming fields, life dates, places, education, career, organizations, obituary, physical/genetic/medical data, social accounts, contact fields, name history, place history, and source/confidence fields in `app/models/person.py`. | Strong fit for living-family archive and diaspora use cases. |
| Field-level sensitive data protection | Contact, medical, and genetic fields use Fernet-backed encrypted text in `app/models/person.py` and `app/services/field_protection.py`. | Useful, but should not be described as end-to-end encryption. |
| Media pipeline | Media supports image, video, audio, GIF, embeds, and documents; uploads have size limits, SHA-256 deduplication, EXIF stripping for images, thumbnails, medium variants, and video posters in `app/services/media_service.py`. | Stronger than basic genealogy media attachment; a real archive differentiator. |
| GEDCOM import | `/api/import/gedcom/preview` and `/api/import/gedcom` parse GEDCOM with duplicate candidates and import batches in `app/routes/imports.py`. | Important on-ramp for existing genealogy users. |
| External record search | Research routes and services search or link out to Chronicling America, NARA, Trove, DPLA, FamilySearch, Antenati, and CEMLA in `app/routes/research.py` and `app/services/external_records.py`. | Useful lightweight bridge, but not a record moat. |
| Wiki biographies and stories | Person wiki pages assemble structured sections and support attributed story CRUD in `app/routes/wiki.py` and `app/models/story.py`. | Good foundation for story-first engagement. |
| Relationship calculator | BFS-based relationship paths and human-readable labels exist in `app/services/relationship_calculator.py`. | Fun and shareable, useful at family gatherings. |
| Recovery and backup | Person revisions encrypt protected snapshot fields in `app/services/revision_service.py`; backups include SQLite and media zip creation plus freshness checks in `app/backup/service.py`. | Important for trust and "family steward" positioning. |
| PWA and ingestion scaffolding | PWA share target saves shared media files; Matrix handler converts bridged media messages into Media records in `app/pwa/routes.py` and `app/matrix/handler.py`. | Promising ingestion wedge, but not yet a polished capture loop. |

Important current gaps:

| Gap | Why it matters |
|---|---|
| Privacy claim mismatch | README says graph distance determines permissions, but current code grants all active non-admins broad visibility and broad manage rights for visible profiles. This is the highest-priority trust blocker. |
| No GEDCOM export found | Import exists, but repository search did not find export support. Paid users will expect exitability before trusting the app with family history. |
| No record or DNA moat | The app has external-source search, not record hints, proprietary databases, or DNA matching. This is acceptable only if positioning avoids "better Ancestry." |
| Source citation depth is light | `source_detail` and `confidence` exist, but genealogist-grade citation templates, evidence linking, proof notes, and source/repository objects are not yet mature. |
| Story capture is basic | Stories exist, but there is no prompt cadence, interview workflow, speech-to-story, collaborative prompt campaigns, or book output comparable to Storyworth/Remento/Storied. |
| Mobile capture is incomplete | PWA share target currently saves files but comments indicate Media/Moment record creation is deferred. There is no native mobile auto-backup, background capture, or polished upload queue. |
| Media intelligence is limited | There is no face clustering, OCR, transcript search, AI captioning, or automatic "who/when/where" enrichment. |
| Trust/security language needs precision | The app has selected field encryption and authenticated media serving. It should not claim full zero-knowledge or end-to-end encryption unless the architecture changes. |
| No payment/onboarding funnel | There is no evident billing, hosted account provisioning, usage limits, or product-led onboarding flow for paid users. |

## Comparison to better marketplace options

| Dimension | Best marketplace options | Family Book today | Verdict |
|---|---|---|---|
| Record discovery | Ancestry, MyHeritage, FamilySearch, Findmypast | Lightweight search/link-outs to public/free sources | Falls far short. Do not compete here directly. |
| DNA matching | Ancestry, MyHeritage, FamilyTreeDNA | Stores some encrypted genetic profile fields, but no matching workflow | Falls short by design. Avoid DNA network claims. |
| Shared free research | FamilySearch | No comparable free records scale | Falls short, but FamilySearch has privacy/shared-tree constraints that create room for a private complement. |
| Private/self-hosted ownership | webtrees, Gramps, Family Book | Self-hosted SQLite app with backups and field-level protection | Stands out if packaged with better UX and hosted option. |
| Privacy controls | webtrees has mature privacy rules; FamilySearch protects living people through private spaces | Family Book has hidden/private media concepts and selected encrypted fields, but broad non-admin access today | Potential strength, currently a blocker. |
| Tree visualization | Ancestry, MyHeritage, MacFamilyTree, FTM, webtrees | Interactive tree exists | Competitive enough for early adopters, needs polish and scale testing. |
| Interoperability | GEDCOM-native desktop/self-hosted tools | GEDCOM import exists; export appears absent | Halfway there. Export is required before paid launch. |
| Research rigor | Gramps, RootsMagic, FTM, MacFamilyTree | Light citations and notes | Falls short for serious genealogists. Can stay lightweight if target is family archive. |
| Media archive | MacFamilyTree, MyHeritage photo tools, general photo apps like Immich/Google Photos | Strong upload/media processing basics, EXIF stripping, variants, audio/video/PDF support | Strong foundation. Needs search, albums, tagging UX, mobile capture, and enrichment. |
| Storytelling | Storyworth, Remento, Storied | Wiki pages and authored stories | Good foundation, but not yet a compelling repeat-use loop. |
| Collaboration | FamilySearch/wiki-tree products, Storied groups | Invites/admin flows plus broad editing | Useful but unsafe. Needs explicit roles, approvals, audit, and per-profile/media rules. |
| Mobile | Ancestry, MyHeritage, FamilySearch, Storyworth/Remento flows | PWA and share target, no native app | Adequate for MVP if upload flow is finished; weaker than consumer expectations. |
| Monetization fit | Ancestry subscriptions, Storyworth $99 books, webtrees support/hosting ecosystem | No billing yet | Need hosted plan and export/book upsells. |

## Where Family Book genuinely stands out

1. It is close to the right product shape for "living family archive," not only genealogy. Rich contacts, languages, social profiles, medical/genetic data, memorial data, stories, media, calendar, and relationship labels are more relevant to living families than a pure ancestor research database.

2. It can credibly tell an ownership story. SQLite, self-hosting, backups, and GEDCOM import make the product feel like a family-owned asset instead of another data silo. Add GEDCOM export and full archive export to make that claim much stronger.

3. The media pipeline is unusually serious for a small genealogy app. EXIF stripping, content typing, deduplication, thumbnails, variants, audio/video/PDF support, and authenticated file serving create a stronger "family archive" foundation than basic tree apps.

4. It can become more lovable than formal genealogy tools. The relationship calculator, family calendar, wiki biographies, authored stories, and living-profile model are better suited to a family gathering, reunion, memorial, or "ask grandma" workflow than Gramps/webtrees-style research administration.

5. It can avoid incumbent trust failures. An explicit "we do not sell data, we do not sell DNA, you can leave, and we make cancellation/export obvious" posture would be meaningfully different from subscription-heavy and data-moat incumbents.

## Where it falls short

1. Privacy is not yet product-grade. Before a paid privacy-first launch, Family Book needs role-based and graph-distance access that is actually enforced. At minimum: owner/admin/steward/member/viewer roles, explicit per-profile visibility, private contact/medical/genetic defaults, and "who can edit this" controls.

2. It lacks a daily/weekly reason to return. Genealogy tools retain users through hints and discoveries; Storyworth retains through prompts. Family Book needs a recurring capture loop: weekly questions, anniversary/birthday prompts, "ask this relative," family digest, and new-media/story notifications.

3. It lacks a buyer-ready onboarding path. A paying user needs to create a hosted archive, import or add first people, invite relatives safely, upload first media, and see a satisfying first family page in under 15 minutes.

4. It lacks exit proof. GEDCOM import is useful, but paid users need GEDCOM export, media export, story export, and a single "download my archive" action.

5. It is not yet superior to specialist tools in their domains. It cannot beat Ancestry on records, MacFamilyTree on polished native desktop genealogy, webtrees on mature GEDCOM/privacy controls, or Storyworth on book-driven story capture.

6. It has a messaging risk. README claims like "no subscription" and "graph distance determines what you can see" conflict with a likely hosted paid plan and current code behavior. Marketing should be precise: "open source and self-hostable; optional paid hosting."

## Strategic recommendation

Primary 2026 niche:

> Privacy-first private family archive for families who want to preserve living relatives, stories, photos, and a family tree without turning their relatives into platform data.

Avoid these traps:

- Do not position as "Ancestry but private." That invites a record/DNA comparison the app cannot win.
- Do not lead with HNW/family-office unless you are prepared for direct sales, security reviews, concierge migration, and long cycles.
- Do not lead with self-hosting only. Self-hosting is a trust enhancer and enthusiast channel, not the fastest way to 500 paying users.
- Do not call it end-to-end encrypted or zero-knowledge unless the architecture actually supports client-side encryption and key handling.

Best early audience:

- Existing family historians who are tired of subscription lock-in but already have a GEDCOM.
- Privacy-conscious families who keep photos/stories in WhatsApp, Facebook, Google Photos, and email.
- Diaspora/multilingual families where rich name/language/place fields matter.
- Genealogy-adjacent "family steward" users: the person organizing a reunion, memorial, milestone birthday, anniversary, or family book.

## Roadmap to a lovable paid app

### Phase 0: Trust and positioning reset - April 2026

Goal: remove launch-blocking trust contradictions.

- Decide and document the paid strategy: "free self-hosted, paid hosted/support."
- Rewrite privacy copy to match implementation, or implement graph-distance privacy before public paid launch.
- Add a simple pricing/waitlist page with one primary CTA: "Start a private family archive."
- Add instrumentation for activation metrics: archive created, first 10 people added/imported, first media upload, first invite sent, first story created.
- Define a clear privacy promise: no DNA marketplace, no data sale, obvious export, obvious cancellation, selected field encryption, authenticated media, backups.

Exit criteria:

- Marketing claims match code.
- Waitlist can collect emails and intent.
- Demo shows a family archive use case, not only generic tree browsing.

### Phase 1: Paid-launch minimum - April to May 2026

Goal: make the app safe enough and useful enough for first paying families.

- Implement real role and permission model:
  - Owner/admin/steward/member/viewer roles.
  - Default private contact, medical, genetic, and minor data.
  - Graph-distance rules if still part of the product promise.
  - Per-media visibility: private, profile-only, family, share-link.
  - "Who can edit" controls and visible edit history.
- Add GEDCOM export and full archive export:
  - GEDCOM file.
  - Media zip.
  - Stories and wiki sections as Markdown/HTML.
  - A manifest with people, relationships, sources, and media metadata.
- Finish PWA share target so shared media becomes a real Media record attached to the right person or an inbox queue.
- Add first-run onboarding:
  - Create archive.
  - Add yourself.
  - Add parents/partner/children.
  - Import GEDCOM or start manually.
  - Upload first photo.
  - Invite one relative.
- Add billing if hosted:
  - Stripe checkout.
  - Trial or annual founding plan.
  - Storage limits.
  - Cancel/export path.

Exit criteria:

- A new user can reach "I have a real family archive" in under 15 minutes.
- A user can leave with their data.
- A privacy-conscious user can understand who sees what.

### Phase 2: Make it lovable - May to July 2026

Goal: create emotional payoff and repeat use.

- Add weekly family prompts:
  - "Ask Mom about her first home."
  - "Add a photo from this decade."
  - "Who knows the story behind this person?"
- Add story campaigns:
  - Birthday campaign.
  - Memorial page.
  - Family reunion collection.
  - Immigration journey.
  - "Grandparent interview."
- Add family digest email:
  - New photos.
  - New stories.
  - Upcoming birthdays/anniversaries.
  - Unanswered prompts.
- Add media delight:
  - Albums and collections.
  - Person/tag search.
  - Timeline by person and decade.
  - "Unknown people in this photo" manual tagging workflow.
- Add lightweight AI as opt-in only:
  - Transcribe audio/video.
  - Draft story from notes.
  - Suggest titles/captions.
  - Extract dates/places from descriptions.
  - Always show provenance and allow edits.

Exit criteria:

- Families have a reason to return weekly.
- The product produces something emotionally valuable within the first session.
- AI is a helper, not a black box.

### Phase 3: Launch and acquire first 100 paying users - July to August 2026

Goal: validate conversion, pricing, and support load.

- Launch a hosted founding plan at $99/year for the first 100-250 accounts.
- Offer white-glove migration for the first 25 paying users in exchange for interviews/testimonials.
- Create landing pages for:
  - Private alternative to Ancestry trees.
  - Private family archive.
  - GEDCOM family archive.
  - Family reunion memory collection.
  - Memorial family archive.
- Publish comparison pages that do not overclaim:
  - Family Book vs Ancestry for private family archives.
  - Family Book vs webtrees for non-technical families.
  - Family Book vs Storyworth for multi-person family archives.
- Seed distribution:
  - Genealogy newsletters and podcasts.
  - Privacy/self-hosting communities.
  - Diaspora and heritage organizations.
  - Family reunion planners and local genealogical societies.

Exit criteria:

- 100 paying users.
- Activation rate measured.
- Churn/refund reasons categorized.
- At least 20 user interviews completed.

### Phase 4: Reach 500 paying users - September to December 2026

Goal: scale the working acquisition channel and add one giftable output.

- Add family book export:
  - Start with PDF/Markdown export.
  - Then partner with print fulfillment if demand is proven.
- Add referral/gifting:
  - "Gift a private family archive."
  - "Invite a family steward."
  - Holiday/year-end family book campaign.
- Add storage-tier clarity:
  - Family: $149/year, modest storage.
  - Steward: $249/year, higher storage and priority support.
  - Optional additional storage.
- Add trust center:
  - Security model.
  - Data export instructions.
  - Backup model.
  - Plain-English privacy policy.
  - Incident/contact process.
- Run channel experiments:
  - 10 genealogical society webinars.
  - 20 newsletter/podcast sponsorships or affiliate tests.
  - 5 diaspora/community organization pilots.
  - 3 estate attorney/funeral home exploratory pilots, but do not depend on these for 2026 volume.

Exit criteria:

- 500 paying users by December 31, 2026.
- At least one repeatable acquisition channel with CAC below first-year gross margin.
- At least 40 percent of paid archives have invited a second family member.
- At least 30 percent have added stories or media after week 1.

## Pricing recommendation

Use annual-first pricing to reduce subscription fatigue while still funding hosted operations.

| Tier | Launch price | Later price | Target buyer | Notes |
|---|---:|---:|---|---|
| Hosted Family | $99/year | $149/year | Family steward | Primary 2026 plan. Keep simple. |
| Hosted Steward | $199/year | $249/year | Serious family historian | More storage, export/backup controls, priority support. |
| Self-host Support | $79/year | $99/year | Technical privacy users | Support and tooling, not core revenue motion. |
| Concierge Migration | $199 one-time | $299+ one-time | GEDCOM/media import help | Useful early cash and learning loop. |
| Family Book Export | $29-99/export or print margin | TBD | Gift/milestone buyers | Start digital, validate print demand later. |

Do not start with a free hosted tier unless the funnel needs it. A limited trial is safer for the privacy story than a permanent free cloud plan. If a free path is necessary, make it either self-hosted or a small local/demo archive that cannot become an ongoing storage cost.

## 500-user operating math

By December 31, 2026:

- 500 users at $99/year = $49,500 annual run-rate.
- 500 users at $149/year = $74,500 annual run-rate.
- 500 users at blended $175/year = $87,500 annual run-rate.
- 500 users at $249/year = $124,500 annual run-rate.

Practical implication: the business should stay lean and product-led. A high-touch HNW/family-office motion can be tested, but it cannot be the main path to 500 users unless the goal shifts from user count to revenue.

Reasonable funnel target:

- 10,000 qualified visitors or community touches.
- 1,000 trial/waitlist signups.
- 600 activated archives.
- 500 paid conversions or founding customers.

The conversion target is aggressive. It requires a narrow audience, a sharp offer, white-glove migration for early users, and a giftable/story-driven hook in Q4.

## Prioritized backlog

P0 before paid launch:

- Fix or remove graph-distance privacy claims.
- Implement real roles and edit permissions.
- Add GEDCOM export and full archive export.
- Finish hosted billing/provisioning if charging for hosted.
- Finish media share inbox/attachment flow.
- Add plain-English privacy, export, cancellation, and backup documentation.

P1 for activation:

- First-run onboarding.
- GEDCOM import polish and migration checklist.
- Invite flow that shows exactly what invitees can see and edit.
- Profile completeness prompts.
- Media gallery search/tagging/albums.
- Story prompt campaigns.
- Family digest.

P2 for differentiation:

- AI transcription and story drafting with provenance.
- Family book export.
- Private share links for selected stories/media.
- Memorial page mode.
- Diaspora/multilingual improvements: multi-script search, name variants, localized relationship labels.

P3 later:

- HNW/family-office concierge offering.
- Estate attorney/funeral home pilots.
- Native mobile app or background photo backup.
- Deeper source citation model.
- DNA import/analysis workflows, only if strongly demanded.

## Recommended success metrics

Activation:

- 60 percent of trial users create or import at least 10 people.
- 50 percent upload at least one media item.
- 40 percent invite at least one relative.
- 30 percent create at least one story or answer one prompt.

Retention:

- 35 percent weekly active archives during the first month.
- 25 percent of invited relatives contribute media/story/profile edits.
- 20 percent of paid users export or generate a family book draft within 90 days.

Trust:

- 100 percent of paid users can export their archive.
- 0 ambiguous privacy claims in marketing.
- Support response SLA defined for paid hosted users.

Revenue:

- 100 paid users by August 31, 2026.
- 250 paid users by October 31, 2026.
- 500 paid users by December 31, 2026.
- Blended ARPU target: at least $149/year by Q1 2027.

## Source notes

Local reports:

- `docs/bizanalysis/deep-research-report.md`
- `docs/bizanalysis/compass_artifact_wf-ea0d0b79-f3a4-4447-9fb8-5a8341724aad_text_markdown.md`

External checks used for current market baselines:

- [Ancestry products and pricing](https://www.ancestry.com/c/allproducts)
- [FamilySearch subscription fee help article](https://www.familysearch.org/en/help/helpcenter/article/does-familysearch-charge-subscription-fees)
- [FamilySearch living-person privacy help article](https://www.familysearch.org/en/help/helpcenter/article/what-is-a-private-space-in-family-tree)
- [webtrees overview](https://webtrees.net/)
- [webtrees privacy documentation](https://webtrees.net/user/privacy/)
- [Geni Pro price help article](https://help.geni.com/hc/en-us/articles/229706227-How-much-is-a-Geni-Pro-subscription)
- [Family Tree Maker Ancestry sync documentation](https://www.familytreemaker.com/aboutsync.html)
- [Storyworth pricing help article](https://help.storyworth.com/en_US/book-pricing)
- [Storyworth public pricing page](https://welcome.storyworth.com/storyworth-pricing)
- [StoriedBook pricing help article](https://wp.storied.com/storiedbooks-help-center/managing-your-account/how-much-does-a-storiedbook-cost)

Confidence notes:

- Current app assessment is based on code inspection, not a full product QA pass or user test.
- Marketplace pricing and packaging change frequently; re-check before publishing pricing comparisons externally.
- The 500-user roadmap is a product-market hypothesis. It should be validated with interviews, launch metrics, and paid conversion tests.
