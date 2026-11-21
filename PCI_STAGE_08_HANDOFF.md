# PCI Stage 08 Handoff — Stage 09 start contract

## Exact deliverables

- `PCI_APP_STAGE08_FULL.zip` — entire source app, immutable inherited source data, strict TS/Vite configuration, safe data repositories, tests, offline preview, manifests, QA logs and screenshots.
- `PCI_STAGE08_BUILD_AND_TEST_REPORT.md` — executed commands and limitations.
- `PCI_STAGE_08_HANDOFF.md` — this handoff (a TXT companion is supplied for iPhone).
- `PCI_STAGE08_iPhone_COMPLETE.zip` — iPhone-oriented bundle of the above, readable report/handoff and original source ZIP.

## Versions and provenance

- App source: `0.8.0`; book schema: `1.0.0`; canonical knowledge pack `1.0.0`; Stage 06 activities `1.0.0`; Stage 07 personalization `1.0.0`; private data schema `2.0.0` / IndexedDB database `pci-private-v1` version 2.
- Original PDF source hash (inherited, not rechecked here): `4dd7a311a21af58aa075176abb48fd60b348c70bb314a2ca09f66383922e7e9b`.
- Existing **1,769 permanent IDs** preserved intact; 4 new engineering-issue IDs: `PCI-ISS-ST08-001` through `PCI-ISS-ST08-004`; updated registry contains **1,773 IDs**. No research data IDs were renumbered or merged.
- Inherited issues preserved; four new testing / release blockers separately registered in Stage 08 root `PCI_ISSUES.json`.
- The five incoming attachment hashes and internal inventory are in `PCI_STAGE08_INPUT_FINGERPRINTS.json` and `FILE_INVENTORY.json` inside the source ZIP.

## What is actually implemented

1. React18-compatible TypeScript source and Vite base-relative config with ten working hash routes, desktop sidebar, mobile drawer, settings and About.
2. Dark premium visual tokens and UI components, keyboard-semantic forms and empty/error/loading states, responsive 320/390px in-memory layout checks.
3. Real canonical source loading via `src/data.ts` and 16 chapter-segmented immutable research documents; full inherited data and schemas kept under `reference/`.
4. Basic IndexedDB v2 typed repository in `src/storage.ts`, 25 declared stores, UUID records, transactions, create/read/update/delete API, bounded import/export v2 shape. Actual real-origin persistence remains untested.
5. Functional Command Center and searchable Knowledge Vault, source-status labels, Chapter/Concept lookups; initial private journal in Archive with edit-by-delete/recreate baseline and simple backup UI.
6. Stage 09–14 features are transparently labeled as future work, not simulated AI or invented psychological metrics.
7. Executed Stage05/06/07 validations and Stage08 source/Node/in-memory browser tests. `npm run build` blocked by registry access; no forged lockfile. See build report.

## Exact modifications for Stage 09

- **Start from this complete Stage08 repository**. Do not independently regenerate the app or discard `src/data.ts`, `src/storage.ts`, public data chunks, manifests or the ten routes.
- Implement the **Self-Image Intelligence Lab** within route `#/self-image` using the 201 source-grounded concept registry and Stage06 executable activities. Save private user self-image observations in the defined IndexedDB stores (`identity_notes`, `beliefs`, `evidence_entries`, etc.), never public JSON.
- Preserve Stage07 private event payloads and reasons, and integrate structured activities instead of inventing personality scores. Keep source references visible, `source_status` separate from clinical evidence.
- Fix `PCI-ISS-ST08-001`: run `npm install` online, generate real lockfile, verify strict TS and real `npm run build` under React18; then test actual hosted localhost or HTTPS navigation.
- Fix `PCI-ISS-ST08-002`: real Chromium/Safari IndexedDB create/read/update/delete, reload persistence, export/import and error flows. Add compatibility test for pre-existing `pci-private-v1` database.
- Fix `PCI-ISS-ST08-003`: remove unused offline compatibility artifacts from production workflow; modernize JSX/React typing using official types if possible. Offline React16 build is a fallback, not a production substitute.
- Fix `PCI-ISS-ST08-004`: keyboard/VoiceOver/contrast tests, 320px and iPhone Safari actual-device checks, and GitHub Pages subpath deployment test.
- Keep last validated output as a rollback ZIP and document migrations for any `schema_version`, event or store changes.

## Exact Stage 09 input attachments

Attach `PCI_APP_STAGE08_FULL.zip`, `PCI_KNOWLEDGE_CANONICAL_v1.zip` and `PCI_STAGE_08_HANDOFF.md`; the build report is strongly recommended. The complete Stage06/07 content is already present under `reference/`, but attach the Stage06/07 ZIPs too if the Stage09 prompt explicitly requires independent pack verification.

## Existing tests and exact commands

```
npm run lint
npm run build:offline
npm run test:repo
npm run test:assets
npm run test:browser
npm run build        # BLOCKED: vite binary unavailable due offline registry
```

### Compliance warnings

- Do not publish `reference/`, `offline-vendor/`, source PDF, or private user JSON backups. Only a verified modern production `dist/` should be deployed publicly.
- `dist-static/` is the tested **offline compatibility** preview, not the React18 production build.
- No account sync, backend, AI provider or automatic success-mechanism neuroscience claim is present.
- This handoff and companion TXT can be opened using iPhone Files after extracting the ZIP.
