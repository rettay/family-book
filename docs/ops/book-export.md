# Family Book Export

## Purpose

The S51 family-book export turns selected people, stories, media, and timeline highlights into a giftable draft.

## Current Output

- Markdown draft
- Basic PDF draft generated from the same content model

## Content Rules

- Only selected people, stories, and media are included.
- Exports respect the requesting actor's visibility limits.
- Private media that the requesting actor cannot view is excluded.
- Source and provenance notes are included when a person or story carries source data.

## Delivery

- Exports are generated on demand for the project creator.
- Markdown and PDF are streamed directly in the download response.
- Family-book drafts are not retained as durable files on disk after generation.

## Operational Notes

- PDF output is intentionally simple and text-first.
- The PDF renderer is deterministic and does not depend on an external browser or layout engine.
- Download authorization is limited to the project creator so saved project selections cannot become a cross-staff data leak.
- If richer print layout is needed later, build it as a separate stage on top of the same project content model rather than changing the S51 export contract.
