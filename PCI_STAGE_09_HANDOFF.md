# PCI Stage 09 Handoff — full Knowledge Vault continuation

**Project:** `PSYCHO-CYBERNETICS-INTELLIGENCE` | **Stage:** 09/16 | **App:** `0.9.0` | **Knowledge schema:** `1.0.0` | **Activity schema:** `1.0.0` | **Private records:** `2.0.0`, IndexedDB database `pci-private-v1` version 2.

## Exact deliverables

- `PCI_APP_STAGE09_FULL.zip`: the **whole** updated modular source project, with `src`, `public`, `reference`, `offline-vendor`, `dist-static`, tests, manifests, validations, and all prior research packs intact.
- `PCI_STAGE09_TEST_REPORT.md` plus iPhone TXT/Markdown ZIP: executed test results, limits, screenshots and coverage.
- `PCI_STAGE_09_HANDOFF.md` plus iPhone TXT/Markdown ZIP: this continuation file.
- `PCI_STAGE09_iPhone_COMPLETE.zip`: iPhone Files-friendly ZIP carrying the 3 primary deliverables and text companions.

## Compatibility and identity

All original 1,773 registered IDs, including 201 concepts, 70 source practices, 109 relationships, 32 PCI activities and the 21-day curriculum, retain their original keys. **No new permanent IDs or research fact changes** in Stage 09. Original Stage 08 complete source and original upstream research are still embedded; Stage 09 updates are additive to the original repository. `PCI_ID_REGISTRY.json`, `PCI_ISSUES.json`, source provenance, and original content fields have not been rewritten. `PCI_PROJECT_MANIFEST.json` now indicates Stage 09 and app version 0.9.0.

## What was built

1. All 16 chapters browsable with source-coverage labels and chapter-specific concepts, source practices, cases, and PCI adaptation links.
2. 201 canonical **full concept dossiers** with thesis, mechanism-as-author-claimed, realistic applications, counterinterpretations, cases, issue/evidence cautions, primary citations, stable permalinks and previous/next.
3. Local search across 504 source-grounded records: phrase/term matching, chapter/record-kind/evidence/origin/topic filters, clear, paging, and deterministic text-match ranking.
4. Same-book 109-edge graph: selected focus and relationship filters, pan and zoom, full provenance and rationale, accessible edge list, source citations and two-concept comparison.
5. Backward-compatible native IndexedDB store actions for bookmarks, manual study plan and manual reading review; no personal entries in public bundle, no unapproved new event types.
6. Stage 08 original routes, Command Center, journal, back-up settings and later-lab states retained.

## Tests actually run

- Stage08 Node repository: **14/14 PASS**, original asset checks **34/34 PASS**.
- Stage09 source search/graph: **19/19 PASS**, source projection **17/17 PASS**.
- In-memory Chromium 1440/390/320 smoke: **54/54 PASS** including all 10 original routes and graph/search/deep pages; *not hosted browser/React18 and not physical iPhone*.
- `npm run lint`, `npm run typecheck`, and `npm run build:offline`: **PASS**.
- `npm run build`: **BLOCKED** (`vite: not found` after passing strict TS). Test-origin navigation: **BLOCKED** by Chromium administrator policy. Actual native IndexedDB reload/transaction behavior: **NOT_TESTED**.
- No source PDF uploaded this stage; page statements are inherited from Stage05, not newly inspected.

## Gaps and release blockers

Carry forward existing `PCI-ISS-ST08-001..004`: real React18/Vite build and valid lockfile, native browser IndexedDB test, legacy offline harness isolation, screenreader/mobile Safari and GitHub Pages HTTPS deployment. Topic group labels and text relevance are heuristic navigational metadata, never empirical validity. Contributor distinctions for source practices remain 51 book / 4 updated-edition editor / 15 uncertain.

## Exact Stage 10 start and files to attach

Attach `PCI_APP_STAGE09_FULL.zip`, `PCI_KNOWLEDGE_CANONICAL_v1.zip` and `PCI_STAGE_09_HANDOFF.md` (or its iPhone ZIP), plus `PCI_STAGE09_TEST_REPORT.md` when possible. Do **not** start a new app, re-ingest chapters or overwrite this repository.

Stage 10 should develop the **Self-Image Intelligence Lab and Belief Reconstruction Studio** in `src/` using the existing Stage07 v2 stores (`identity_notes`, `beliefs`, `belief_revisions`, `evidence_entries`, `experiments`) and content references. Keep all Knowledge Vault URLs, source panels, graph, full content, 10 module routes and `src/vault-data.ts`/`src/vault-storage.ts` contracts. It may introduce schema migrations only with versioned backup/rollback and explicit tests. The source PDFs and sensitive journals never belong in `public/`.

## Important Stage 09 source paths

- `src/vault.tsx`, `src/vault-data.ts`, `src/vault-search.ts`, `src/vault-storage.ts`
- `scripts/build-vault-data.py`, `public/data/vault/`, `public/vault.css`
- `tests/vault_unit.test.mjs`, `tests/validate_vault.py`, `tests/browser_stage09_smoke.py`
- `PCI_STAGE09_MIGRATION_NOTES.md`, `PCI_STAGE09_TEST_REPORT.md`
- `audit/PCI_STAGE09_CHROMIUM_IN_MEMORY_QA.json`, `audit/PCI_STAGE09_VAULT_ASSET_QA.json`

**Known limitation:** No verified React18/Vite production artifact, iPhone Safari run, or real IndexedDB persistence result yet. Preserve the full Stage08 rollback source from the earlier ZIP.

Additional executable audit: `node tests/vault_profile.mjs` logs eight true source-data query timings; `audit/PCI_STAGE09_PRESERVATION_QA.json` verifies 143 originally supplied `reference/` records byte-for-byte. Neither search timings nor data integrity imply scientific validation of book claims.
