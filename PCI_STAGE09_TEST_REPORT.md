# PCI Stage 09 — Build, Source and Functional Test Report

**Scope:** Same PCI application and original Stage 05 canonical data. Executed in the offline container, November 20, 2026. The original book PDF was **not attached**; edition/source PDF claims are inherited and not represented as newly checked.

## Inputs opened

- `PCI_APP_STAGE08_FULL(1).zip` — SHA-256 `f118300f75c9c04026f76b6a70a12127b010f53bef6c977b2c6141f308cc982d`, 349 archive members, whole original app unpacked.
- `PCI_KNOWLEDGE_CANONICAL_v1(4).zip` — SHA-256 `e26e80a5077efd4f39e3cf619e961e15b1acd84664759d02f5f7beebef1f7960`, 71 original canonical source members.
- `PCI_STAGE_08_HANDOFF_iPhone(1).zip` — SHA-256 `5562c4e8caab4db623e82e25b638b7f9685bdccead74b88d762143d9c3e5cc636c20`, exact Stage 08 handoff and TXT read.
- Stage 06/07 source packages are preserved in the full Stage 08 repository under `reference/`. No new book PDF review is claimed.

## Executed tests

| Actual command | Result | Scope |
|---|---|---|
| `npm run lint` | PASS | Lightweight source guard + strict TypeScript, not ESLint |
| `npm run typecheck` | PASS | `tsc --noEmit`, TypeScript 5.8.3 global |
| `npm run test:repo` | PASS **14/14** | Inherited Stage 08 data repositories and private export input guard |
| `npm run test:assets` | PASS **34/34** | Stage 08 canonical data and ID preservation |
| `npm run build:offline` | PASS | Offline TypeScript/React16 compatibility compilation; **not** Vite production |
| `npm run test:vault` | PASS **19/19** | Actual local 504-record search, phrase/chapter/origin/evidence filter, graph endpoints, pagination metadata |
| `npm run test:vault:assets` | PASS **17/17** | Public projection referential integrity, 16 chapters, source boundaries, no original PDF/private fixtures |
| `npm run test:browser` | PASS **54/54** | **In-memory Chromium** React16 compatibility harness with local true JSON; 1440/390/320px views |
| `npm run build` | **BLOCKED** exit 127 | `tsc --noEmit` passed; `vite: not found` because npm dependencies unavailable. No forged lockfile. |
| HTTPS real-origin navigation via intercepted Chromium route | **BLOCKED** `ERR_BLOCKED_BY_ADMINISTRATOR` | Browser policy disallows test origin. Native IndexedDB reload tests could not be run. |

### Chromium in-memory detail

- Existing ten module hash routes loaded.
- 16 chapter cards and chapter-1 concept/practice listings loaded from full preserved datasets.
- A full `PCI-C-CH01-001` dossier showed source page metadata, evidence cautions and link destinations.
- Citation modal opened at PDF p. 13 / printed p. 3 and closed correctly.
- Invalid concept ID displayed a not-found state instead of fabricating a record.
- Exact quoted phrase returned the existing concept; chapter filter could produce an empty state; clearing restored results; editor-origin filter showed exactly four inherited records.
- Graph loaded original relationships, selected an edge rationale, zoomed, and navigated into a two-column source comparison.
- Stage 06 activity specification opened without falsely claiming activity completion.
- 320px and 390px chapter/search/graph pages had no blocking horizontal document overflow.
- No captured JavaScript console/page errors; source screenshots under `audit/stage09_*`.
- When native IndexedDB was unavailable in the in-memory origin, persistence controls were properly disabled.

### Quantified content and integrity

- 16 chapters; 201 original full concepts; 70 source practice records (51 book, 4 updated-edition editor, 15 uncertain author attribution); 32 educational adaptations; 201 applications.
- 504 searchable original record destinations, 109 validated original graph edges, 0 orphan graph endpoints.
- 315 primary source citation metadata records. Original 1,773 registered project identifiers preserved; no new source IDs or changes to evidence statuses.
- Theme/topic and relevance ordering are lexical/navigation aids, **not empirical rankings, psychological diagnosis, or scientific efficacy assessments**.
- The 25 IndexedDB stores and private export v2 contract were unchanged.

## Outstanding tests and risks

- **NOT TESTED:** real React18/Vite production compilation, hosted navigation, cross-origin/page refresh behavior, actual IndexedDB write/reload/delete, browser backup restore after reload, assistive technology screenreader testing, physical iPhone Safari.
- **NOT ASSESSED HERE:** comprehensive independent historical/scientific corroboration or page-image accuracy of each original quote. Inherited research issue registry remains open where applicable.
- **PARTIAL:** Keyboard navigation was covered via DOM semantics, native button/select controls and an accessible graph alternative list, but no full screen-reader walkthrough occurred.
- Existing Stage 08 issues `PCI-ISS-ST08-001` through `PCI-ISS-ST08-004` stay open; no redundant replacement IDs were issued.

See `audit/PCI_STAGE09_VAULT_ASSET_QA.json`, `audit/PCI_STAGE09_CHROMIUM_IN_MEMORY_QA.json`, `audit/PCI_STAGE09_DATA_PROJECTION.json`, `audit/stage09/PCI_STAGE09_EXECUTED_TEST_COMMANDS.log` and `audit/stage09/vite_build_attempt.log` for raw execution evidence.

### Audited search-profile sample

`node tests/vault_profile.mjs` profiled eight queries over all 504 actual search rows (80 runs per query). On this container, example median query time was 13.2 ms for the quoted Chapter 1 concept and 13.0 ms for `feedback` (66 returned hits). These are **Node in-memory local timings**, not mobile Safari timings, and are not a claim of semantic search or measured reading efficacy. Full measurements: `audit/PCI_STAGE09_SEARCH_PROFILE.json`.

### Byte-preservation audit

`audit/PCI_STAGE09_PRESERVATION_QA.json` confirms **143/143 original `reference/` source files unchanged**, original ID and issue registries byte-for-byte unchanged, and 69 previous public data assets identical to Stage 08. The new chapter/search/graph projections are additive.
