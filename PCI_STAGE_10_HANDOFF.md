# PCI Stage 10 Handoff — Self-Image and Belief Reconstruction

**Project:** `PSYCHO-CYBERNETICS-INTELLIGENCE` · **App source:** `0.10.0` · **Knowledge schema:** `1.0.0` · **Private records:** `2.0.0` · **DB:** `pci-private-v1` v2 · **Stage:** 10/16.

## Downloadable canonical files

1. **`PCI_APP_STAGE10_FULL.zip`**: the complete updated Stage09 React/Vite source, read-only canonical data, 10 routes, 2 functioning new labs, original research packs, prior test suites, rollback copy of Stage09, additional schemas, offline compatibility build, new tests, file inventory and checksums.
2. **`PCI_STAGE10_TEST_REPORT.md`**: exact tests/commands, browser limitations, source preservation audit and open issues.
3. **`PCI_STAGE_10_HANDOFF.md`**: this continuation specification.
4. **`PCI_STAGE10_iPhone_COMPLETE.zip`**: Files-app friendly archive containing the complete source ZIP, the report, this handoff, readable TXT copies and QA metadata.

## What actually changed

- `src/personal-labs.tsx`: fully mounted Self-Image Lab and Belief Studio. Self-image inventory has domain, context, observation, goal, optional research links, revisions and independent reflections. Belief Studio has 5 steps, evidence vs interpretation, supporting/counterevidence, barriers, alternatives, hypothesis, safe action, forecast, voluntary 0–100 subjective conviction, revision comparison, manual draft save, planned experiment outcome, and confirmed delete.
- `src/personal-labs-model.ts`: deterministic explicit-domain-to-source concept recommendations and input/compare validation.
- `src/personal-labs-repo.ts`: private record operations, atomic v2 IndexedDB writes, guarded revision conflict, preserved source IDs, sensitive-data consent, deletion cascade, experiment observation and minimal event metadata.
- `src/app.tsx`, `public/styles.css`, `package.json`: additive routes and dark responsive styling; 10 original routes and Stage09 Knowledge Vault continue working.
- `schema/PCI_STAGE10_BELIEF_DATA.schema.json`, `schema/PCI_STAGE10_EVENT_EXTENSION.json`, `PCI_STAGE10_MIGRATION_NOTES.md`: explicit stable contracts and compatibility explanation.
- `tests/labs_model_repo.test.mjs`, `tests/browser_stage10_smoke.py`, `tests/idb_test_facade.js`, `tests/validate_stage10.py`: executable synthetic-storage, UI, preservation and privacy checks.

## Stable data/API contracts for Stage 11

- Keep the original `PCI_ID_REGISTRY.json` mappings and all canonical IDs. **1,773 inherited IDs unchanged**, plus 5 new issue records `PCI-ISS-ST10-001..005` (total 1,778). No permanent source concept, claim, author-practice or exercise record changed.
- Keep Stage07 `PrivateRecord` v2 envelopes and all 25 stores. Use `src/storage.ts` exactly as the authority for local IndexedDB. No v3 migration.
- Consume `beliefs.data` as the user's latest `BeliefSnapshot`; history is in `belief_revisions.data.before/after`. Do not flatten or overwrite it. `evidence_entries` and `experiments` link using `belief_id`, `revision_id`; completed observations use `observed_outcomes`.
- Use `src/personal-labs-repo.ts` (`loadLabRecords`, `revisionFor`, `experimentFor`, `recordOutcome`) for stable personal data. Stage11 rehearsal sessions should store references to belief/goal IDs, never replicate the entire personal belief text in public data.
- Existing v2 event names: `belief.created`, `belief.revised`, `journal.saved`, `experiment.outcome_recorded`. New `experiment.planned` is an additive **2.1.0 tagged** event which older Stage07 consumers must ignore safely if unrecognized. See schema extension file.
- The explicit example source links are canonical `PCI-C-*` IDs, and the Knowledge Vault route is `#/knowledge/concept/<ID>`. `#/theater` remains the reserved Stage11 route; deep links can pass source IDs as path segments, but never personal text in URLs.
- No personal records, sensitive journal or copyrighted source PDF belongs in `public/`.

## Executed checks / limitations

- Initial Stage09 tests: Node repository **14/14**, source graph/search **19/19**, assets **34/34**, vault projection **17/17**, TypeScript **PASS**.
- Stage10: model/repo mock-IDB tests **16/16**, preservation/privacy checks **34/34**, compatibility Chromium interface **43/43**, prior Stage09 browser regression **54/54**, offline build **PASS**.
- `npm run build` **BLOCKED** (TypeScript passed, `vite: not found`, exit 127). No npm lockfile forged.
- Native HTTPS-origin IndexedDB and physical iPhone Safari **NOT_TESTED**; Chromium navigation blocked by administrative policy. The IDB unit/browser tests use a synthetic implementation and cannot establish native persistence after reload. Screen reader behavior also untested.
- Manual Save draft exists. Background autosave was intentionally deferred to avoid unsolicited storage of sensitive unsaved input. Existing Settings export/import remains v2.0.0, with a clear unencrypted-backup warning.
- Stage10 has not independently rechecked the primary PDF. Source citation and evidence status are inherited unchanged from the canonical Stage05 research pack.

## Exact files to attach for PCI Prompt 11

1. `PCI_APP_STAGE10_FULL.zip` (mandatory; Stage11 must modify this complete project).
2. `PCI_ACTIVITY_ENGINE_DATA_v1.zip` (mandatory for the 12 original guided rehearsal templates).
3. `PCI_PERSONALIZATION_ENGINE_v1.zip` (mandatory for event, private data and learning contracts).
4. `PCI_STAGE_10_HANDOFF.md` or its iPhone TXT/Markdown ZIP (mandatory).
5. `PCI_KNOWLEDGE_CANONICAL_v1.zip` when reopening disputed source concepts or source links.

## Stage 11 first actions

Revalidate the preserved original tests, inspect all files, and implement the Theater of the Mind against `rehearsal_sessions`, the existing belief/goal IDs and Stage06 reusable templates, with no invented outcome or AI claims. Run native HTTPS-origin IndexedDB once browser access permits. Preserve working Stage09 Knowledge Vault and both new Stage10 labs.
