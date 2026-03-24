# Family Book Product Vision

Status: Active launch contract

## What This Document Is

This is the authoritative launch product contract for Family Book.

If another document describes broader or conflicting behavior, this document wins for anything presented as shipping in the near term.

## One-Line Definition

Family Book is a private, collaborative family wiki that combines a family tree, person records, stories, media, and timeline history into one shared family knowledge base.

## What This Is Not

- Not a graph-distance privacy experiment
- Not a read-only genealogy viewer
- Not a social feed clone
- Not a public social network
- Not a HIPAA product or enterprise medical-record system

## Core Problem

Family history is fragmented across memory, chat threads, photos, documents, and separate people. Traditional family tree tools capture lineage but not the lived texture of a family: stories, media, burial details, contact information, and ongoing collaboration.

## Core Promise

Log in as a family member and contribute to one shared, private family record that everyone in the family can actually use.

## Product Principles

### 1. Collaboration over gatekeeping

The system should behave more like a family wiki than an admin-only directory.

### 2. Truthfulness over feature theater

The product should only promise workflows that the current implementation can actually support.

### 3. Rich family history over narrow lineage cards

Stories, tagged media, notes, timeline entries, burial details, and contact information are first-class content.

### 4. Privacy by family boundary, not by hidden graph rules

The launch model is a private family space for authenticated members, with account control and auditability replacing opaque graph-distance restrictions.

### 5. Reliability over speculative integrations

Core shared workflows should work before external imports, social ingestion, or broader automation.

## Primary Users

- **Admin:** manages accounts, invites, settings, moderation, and policy
- **Family member:** views and edits shared family content

Guests are out of scope for launch.

## Launch Product Contract

### Members can

- view the shared family tree
- view shared person records
- create and edit family content
- upload and view family media
- add stories, notes, and timeline items
- manage shared family history collaboratively

### Admins can

- invite and manage accounts
- link accounts to person records
- disable or remove accounts
- control app-level settings and theme
- inspect audit history

## Core Product Surfaces

- Tree view
- Person view
- Timeline view
- Map view
- Admin panel
- Settings

## Content Types

- People
- Relationships
- Stories and notes
- Photos
- Videos
- Audio recordings
- Timeline events
- Burial records
- Contact records
- Medical-history records

## Not Part of the Launch Contract

- Automatic social-media ingestion
- Local news enrichment
- Federation between family instances
- Fine-grained graph ACLs
- AI-heavy runtime behavior

## Success Criteria

Family Book is succeeding at launch when:

- invited members can sign in without manual database intervention
- multiple members can see the same shared tree and media
- one member's change becomes visible to another member correctly
- the product feels like a shared family system rather than a single-admin tool
