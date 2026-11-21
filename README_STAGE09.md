# PCI Stage 09 — Advanced Knowledge Vault

This is **the complete Stage 08 project extended**, not a separate or replacement application. Original canonical knowledge/activities/personalization research remains under `reference/`, and the 10 Stage 08 module routes remain intact.

## Implemented Knowledge Vault

- 16-chapter reading interface with actual source boundaries, coverage status, canonical concept index, original author-practice index, PCI activities and source anecdotes.
- 201 full research concept dossiers: original thesis, author mechanism, cautions, applications, cases, evidence classifications, distinct PDF and printed page citations, chapter prev/next.
- 504-entry local full-text search index: concept, author practice, educational exercise, application; quoted phrases, terms, chapter/type/topic/evidence/origin filters, clear, paginated results, original content destination.
- 109 traceable within-book relationships; interactive focus, relationship filtering, node selection, zoom/pan, explanatory edge inspector and fully accessible relationship list; source-supported within-book comparison.
- Local-only bookmarking, add/remove study-plan actions, manual concept review (not mastery), permalink copy, and visible privacy/storage errors.
- 320 px, 390 px and desktop responsive layout and keyboard interactions. No full PDF or sensitive personal records in web assets.

## Running the actual app

Production source dependencies: `react@18.3.1`, `react-dom@18.3.1`, `vite` and TypeScript. **An npm registry is required to install them; they were absent in this execution environment.** Run `npm install`, commit the resulting genuine lockfile, then `npm run build` and `npm run dev` on an online machine. A lockfile was **not** fabricated. Only the generated production `dist/` should be deployed to GitHub Pages.

Test-only offline fallback: `npm run build:offline`. This compiles TypeScript and produces `dist-static/` using a legacy React 16 compatibility harness, with all public assets. It has passed in-memory Chromium smoke, **but must not be presented as a verified React 18/Vite release**.

## QA and data generation

```
python scripts/build-vault-data.py
npm run lint
npm run typecheck
npm run test:repo
npm run test:assets
npm run build:offline
npm run test:vault
npm run test:vault:assets
npm run test:browser
npm run build       # documented blocked until Vite available
```

The complete commands, counts, and limitations are in `PCI_STAGE09_TEST_REPORT.md`. See `PCI_STAGE09_MIGRATION_NOTES.md` for private-data and old-ID compatibility and `PCI_STAGE_09_HANDOFF.md` for Stage 10.

**Archive preservation:** The original `reference/` directory, original canonical ID registry, issue registry and original public research data are byte-preserved. Additional Stage 09 projections are generated without editing source records.
