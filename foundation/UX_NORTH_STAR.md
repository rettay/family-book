# Family Book UX North Star

Status: Active launch contract

## What This Document Is

This is the authoritative experience-design contract for Family Book. It defines how the product should *feel to use*, sitting between the product vision (what the app does) and task packets (what to build next).

If a UI pattern or interaction design conflicts with these principles, this document wins for launch-oriented work.

## One-Line Experience Goal

A family member opens the tree, sees their family, and enriches it right there.

## Core Experience Principles

### 1. The tree is the workspace, not a visualization

The tree is where family history work happens. Browsing, editing, adding stories, uploading photos, linking relatives, and discovering gaps should all be possible without leaving the tree context. Other pages (person profile, moments feed, admin) exist as deep-dives, not as the default destination for every action.

The tree sidebar is the primary editing surface. The person profile page is the reading surface. The person edit page is the last resort, not the first step.

### 2. In-context over detour

When a user wants to change something, the editing affordance should appear where the user already is. Clicking a name should make it editable. Clicking a metric should open that content. Tapping "add parent" should let you pick from the tree itself.

Navigation to a separate page is a cost. Every time a user leaves the tree to fill out a form and then has to navigate back, the experience breaks. Minimize those breaks.

### 3. Progressive disclosure over form walls

Show the basics first. Let users expand for detail. A sidebar with 9 visible form sections is a wall. A sidebar with a clean overview that lets you tap into Details, Moments, Media, or Relationships is an invitation.

The same applies to person creation: start with name and relationship, let everything else be added later incrementally. Don't demand 20 fields upfront.

### 4. Empty states are invitations, not dead labels

When a person has 0 stories, 0 photos, or no birth date, the UI should prompt action — not display a zero. "No stories yet — add one" is better than "Stories: 0". "Birth date unknown — do you know it?" is better than a blank field.

Gaps in the family record are the primary motivator for contribution. Surface them as opportunities, not as data-entry debt.

### 5. Content over chrome

Stories, photos, and moments are the most engaging content in the app. They should be prominent — not buried below version history or admin metadata. On a person's page, the hierarchy should be:

1. Identity (who is this person)
2. Their story (bio, stories, moments)
3. Their connections (relationships, tagged content)
4. Their media (photos, documents)
5. Administrative detail (version history, audit, source metadata)

### 6. Research-friendly data entry

Real family history is messy and incremental. The app must support:

- Partial and uncertain information ("born around 1920", "possibly buried in Guadalajara")
- Incremental enrichment (add a name now, fill in dates later, attach a photo next month)
- Provenance awareness (where did this information come from?)
- Confidence levels (is this confirmed or uncertain?)

The data model already supports date precision, relationship confidence, and flexible text dates. The UI must surface these capabilities rather than hiding them behind developer-only fields.

### 7. Collaboration feels rewarding, not tedious

Contributing to the family record should feel like sharing at a family gathering, not filling out a government form. The moments/stories system is the social glue — it should be easy to reach from any context. Quick contributions (a photo with a caption, a one-line memory) should be as frictionless as posting to a chat.

## Interaction Patterns

### Tree interactions

- **Click node** → sidebar opens with overview and tabs
- **Double-click node** → navigate to full person profile
- **Search in tree** → find and zoom to a person without leaving the tree
- **Graph mode** → click one node, then another to connect them as relatives
- **Metric clicks** → expand to show that content (moments, media) in the sidebar

### Sidebar tabs

The tree sidebar uses tabbed progressive disclosure:

- **Overview**: identity, key dates, bio summary, relationship chips, gap prompts
- **Details**: all editable person fields in collapsible sections
- **Moments**: stories and timeline entries for this person, with inline creation
- **Media**: photo grid with upload, preview, and tagging
- **Relationships**: current relationships with edit/remove, plus add-new flows

### Person profile page

The person profile is the deep-reading surface. It should feel like opening a chapter about someone — their story, their photos, their connections, their place in the family. It is not the primary editing surface; that's the tree sidebar.

### Moments feed

The moments feed is the social pulse of the family. It shows what's been shared recently across all family members. It should feel alive and current, like a family group chat that also archives.

## What This Is Not

- Not a mandate to rebuild the UI from scratch. These principles should guide incremental improvement through scoped task packets.
- Not a design spec with pixel values. It defines interaction philosophy, not visual design.
- Not a replacement for the product vision or V1 requirements. It complements them by defining the experience layer those docs don't cover.

## Relationship to Other Documents

- `PRODUCT_VISION.md` defines what the app does → this doc defines how it feels
- `V1_PRODUCT_REQUIREMENTS.md` defines must-have capabilities → this doc defines how they're surfaced
- `COLLABORATION_AND_PRIVACY.md` defines access rules → this doc defines the interaction model within those rules
- Task packets define scoped work → this doc is the north star they align to
