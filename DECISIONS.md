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
