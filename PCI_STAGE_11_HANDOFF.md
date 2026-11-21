# PCI Stage 11 Handoff — Theater of the Mind

**Project** `PSYCHO-CYBERNETICS-INTELLIGENCE` · **App version** `0.11.0` · **Stage** 11 of 16. **Canonical research schema** `1.0.0` · **private IndexedDB records** `2.0.0` (`pci-private-v1`, DB version 2) · **rehearsal session data** `1.0.0` · **event extension** `2.1.0`.

## Required outputs

- `PCI_APP_STAGE11_FULL.zip`: entire Stage10-derived application with Stage11 source, read-only data, prior research/reference packs, 10 routes, tests, QA files, original Stage10 rollback ZIP, and checksum inventory. This is a full source repository, not a patch/detached demo.
- `PCI_STAGE11_TEST_REPORT.md`: commands/results and observed limits.
- `PCI_STAGE_11_HANDOFF.md`: this handoff.
- `PCI_STAGE11_iPhone_COMPLETE.zip`: complete downloadable iPhone Files ZIP holding the above source archive, readable TXT/Markdown reports, and QA JSON.

## Primary files added or modified

**New:** `src/theater.tsx`, `src/theater-model.ts`, `src/theater-repo.ts`, `public/data/practice-attribution.json`, `schema/PCI_STAGE11_SCENE.schema.json`, `schema/PCI_STAGE11_SESSION.schema.json`, `schema/PCI_STAGE11_EVENT_EXTENSION.json`, `tests/theater_model_repo.test.mjs`, `tests/browser_stage11_smoke.py`, `tests/validate_stage11.py`, `README_STAGE11.md`, `PCI_STAGE11_MIGRATION_NOTES.md`.

**Updated in place:** `src/app.tsx`, `src/react-compat.d.ts`, `offline-vendor/react16-hooks-bridge.js` (offline compatibility-only ref hook), `public/styles.css`, `package.json`, `PCI_PROJECT_MANIFEST.json`, `PCI_ISSUES.json`, `PCI_ID_REGISTRY.json`, and preexisting Stage09/10 assertions that assumed an exact previous ID count. Stage10 data repositories and research packs remain untouched.

## Stable contracts for Stage12

- Preserve `src/storage.ts`: all **25 existing stores**, same IndexedDB name/version 2, `PrivateRecord` envelopes and v2 export/import. Session records live in `rehearsal_sessions`; user-created reusable scenes live in `rehearsals`. Source templates remain immutable `PCI-RH-001..012` from `public/data/rehearsals.json`.
- `src/theater-model.ts`: `PlayerState`, `TimingMode`, `settleClock`, `phaseBudgets`, `pausePlayer`, `stepPlayer`, `finishPlayer`, `stopPlayer`, `interruptOnLoad`. `PlayerState.elapsed_ms` is observed active wall time excluding explicit pauses and cannot prove behavior change. Optional full/short/custom/untimed modes are PCI app designs; original author practices have distinct source attribution and timing.
- `src/theater-repo.ts`: `getRehearsalLibrary`, `saveScene`, `duplicateScene`, `deleteScene`, `makeSession`, `updateSession`, `resumeSession`, `removeSession`. `updateSession` performs transactional session+event updates with deterministic event idempotency keys `<event_type>:<session_uuid>`.
- `rehearsal.completed` payload includes `session_id`, `template_id`, `template_version`, `duration_mode`, `actual_elapsed_ms`, `skipped_count`, `source_origin`. Never pass scene or belief body text into generic events. Stage12 can link a separately user-entered experiment outcome by `rehearsal_sessions.id` (UUID). Do not treat a predicted rehearsal scene as observed event outcome.
- Keep source routes `#/knowledge/concept/<PCI-C-ID>` and app route `#/theater`; all original modules retained. Stage12 Feedback Lab currently reserved `#/feedback`, real scenarios currently reserved `#/scenarios`. Do not fabricate functionality before implementing it.
- Preserve original 1,778 permanent IDs, 3 new **issue-only** IDs `PCI-ISS-ST11-001..003` (1,781 total). No concept, practice, source or book research IDs changed. `PCI_PROJECT_MANIFEST.json`, `PCI_ID_REGISTRY.json`, `PCI_ISSUES.json` are canonical.
- Stage12 must **modify this complete Stage11 application** and consume preserved Stage06 scenarios and Stage07 event contracts. The source ZIP contains the inherited reference packs; attaching explicit source archives is encouraged for source-dispute checks.

## Verified work and open defects

- Existing 49 Node tests plus 20 new tests: **69/69 PASS**. Source asset tests Stage08 34/34, Stage09 17/17, Stage10 34/34, Stage11 45/45 PASS. Strict TypeScript, lightweight lint, and React16 *compatibility* offline compilation PASS. In-memory Chromium simulated IndexedDB 56/56 PASS (1440/390/320 px).
- **BLOCKED** `npm run build`: `vite: not found`, exit 127 after typecheck success. Native localhost Chromium navigation attempted and **BLOCKED** `net::ERR_BLOCKED_BY_ADMINISTRATOR`.
- **NOT_TESTED:** React18/Vite production interactions, native IndexedDB persistence across reload, real physical iOS Safari/VoiceOver, audible browser speech and offline application re-entry. User text remains device-local by design; browser behavior still requires independent QA.
- Model clock simulates background intervals and supports periodic 15-second checkpointing; crash recovery of seconds since last durable write is not guaranteed. Do not claim that visualization improves performance or that self-rated scores demonstrate treatment effects.

## Exact inputs for Prompt12

1. `PCI_APP_STAGE11_FULL.zip` **mandatory**, never replace it with an isolated demo.
2. `PCI_ACTIVITY_ENGINE_DATA_v1.zip` **mandatory** for the 16 authored branching scenarios and feedback patterns.
3. `PCI_PERSONALIZATION_ENGINE_v1.zip` **mandatory** for event/goal/review contracts.
4. `PCI_STAGE_11_HANDOFF.md` **mandatory**, TXT or Markdown in iPhone ZIP acceptable.
5. `PCI_KNOWLEDGE_CANONICAL_v1.zip` recommended for direct source-dispute and citation audits. The original PDF is required for any new primary-source verification claims.

**Stage12 first actions:** verify this ZIP and its checksums, preserve baseline tests, implement Feedback Lab + Scenario Simulator against existing `experiments`, `observed_outcomes`, `scenario_progress` and event stores. Link rehearsal session IDs without copying sensitive text. Re-test secure-origin IndexedDB and React18 as soon as tooling permits.
