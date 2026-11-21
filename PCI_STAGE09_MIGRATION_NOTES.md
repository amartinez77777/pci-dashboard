# Stage 09 — compatibility and migration notes

## Persistent user data

- **No schema or database version change.** Continue using IndexedDB `pci-private-v1`, version 2, with the existing 25 store names and Stage 07 record/envelope version `2.0.0`.
- Bookmarks are saved to `bookmarks`, manual study-plan membership to `program_progress`, and manual reading acknowledgements to `review_ratings`. Stage 07-defined `bookmark.saved` and `exercise.reviewed` events are stored in `events` with idempotency keys and `concept_reading` scope for the latter. They do **not** imply assessment performance or mastery.
- Stage 09 uses a `knowledge_bookmark` record kind, but also **reads and toggles legacy `concept_bookmark` records**, retaining their IDs and prior data. No bulk personal rewrite occurs.
- Existing Stage 08 private exports can be imported through the unchanged settings action. Every new user record still uses a UUID generated when the user explicitly clicks Save.
- Real browser IndexedDB tests are blocked in this execution environment; test on an HTTPS origin with an existing version-2 database before promoting to production.

## Public knowledge content

- No original record IDs were retired, merged, replaced or renumbered. No source assertion/evidence status was modified. Canonical collections are byte-preserved under `reference/knowledge`.
- All new public files under `public/data/vault/` are **read-only projections** of the existing source research, rebuilt deterministically with `python scripts/build-vault-data.py`.
- Content tags and search relevance are editorial text navigation, not empirical research classifications. Do not treat the local search weights as psychological or educational effectiveness scores.
- Stable permalink routes: `#/knowledge/concept/PCI-C-CH01-001`; `#/knowledge/chapter/PCI-CH-01`; `#/knowledge/graph/PCI-C-CH01-001`; `#/knowledge/compare/PCI-C-CH01-001/PCI-C-CH01-002`. The original `#/knowledge/PCI-C-CH01-001` form remains recognized.
- Vite source uses the unchanged relative `base: './'` and hash router. The existing React 16 offline preview is a **test-only** fallback, not a verified React 18 Vite production build.

## Stage 10 API contracts

- `src/data.ts` remains available and unchanged (canonical segmented repositories).
- `src/vault-data.ts`: `getVaultSearch`, `getVaultGraph`, `getVaultTopics`, `getChapterResearch`, `lookupVaultRecord`, `relatedActivityLinks`.
- `src/vault-search.ts`: `searchVault`, `neighborhood`, `getCitationLabel`, pure deterministic query/filter/edge validation.
- `src/vault-storage.ts`: `readKnowledgeState`, `toggleKnowledgeTarget`, `markConceptReviewed`, using the inherited private storage module.
- `src/vault.tsx` integrates the above; Stage 10 should modify this same app repository and avoid reusing its private stores for unrelated belief/identity records.
