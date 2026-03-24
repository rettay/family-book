# Family Book V1 Product Requirements

## Product Goal

Deliver a functional private family wiki where invited family members can collaboratively maintain a shared family record with a tree, person profiles, media, stories, and timeline context.

## V1 Must-Have Workflows

1. Admin invites a family member by email, that user signs in, and enters the shared family space.
2. A family member adds a person and relationships, and other members can see that person in the tree.
3. A family member uploads media, tags one or more people, and other members can view it.
4. A family member adds a story or note to a person, and it appears on the person page and timeline where appropriate.
5. A family member can manage contact information for a person.
6. A family member can record burial details and tombstone media for a deceased person.
7. A family member can adjust tree display preferences and apply tree filters.
8. A family member can view relevant people and burial locations on a map.
9. An admin can manage accounts, invites, and policy settings.
10. Content changes are auditable.

## Functional Requirements

### Accounts and access

- The system must support admin-managed invites by email.
- Users must sign in to access family content.
- Active family members must have flat shared access to family content.
- Admins must be able to add, edit, disable, and remove accounts.

### Person records

Each person must support:

- names and identity fields
- living/deceased status
- birth and death data
- relationships
- stories and notes
- contact information
- medical history
- burial details
- geographic/location fields
- attached and tagged media

### Content and media

- The system must support photos, videos, and audio recordings.
- Media must support tagging one or more people.
- Media and stories must be viewable by other authenticated family members.
- Timeline items must support person references and media references.

### Tree view

- The tree must show shared family data to active members.
- Each user must be able to choose what attributes are displayed, such as name, dates, relationships, and photo.
- Users must be able to filter the tree by criteria including location, birth nation, and living/deceased state.

### Timeline

- The app must support timeline-style family moments.
- Timeline entries must support manual stories and notes.
- Timeline entries must support tagged people and media.

### Map

- The app must support a geographic map view for living locations and burial locations.

### Admin and settings

- Admins must have a panel for account and invite management.
- Admins must be able to configure theme colors.
- User-level display preferences must persist.

### Security and integrity

- Traffic must be encrypted in transit.
- Sensitive stored data must be protected at rest.
- Major mutations must be auditable.
- The app must support backup and restore.

## Out of Scope for V1

- Automated Facebook or social-media ingestion
- External news augmentation on timelines
- Fine-grained permission classes beyond the flat family model
- Federation between separate family installations

## Acceptance-Test Intent

Every must-have workflow above should map to an executable test, not just a document claim.
