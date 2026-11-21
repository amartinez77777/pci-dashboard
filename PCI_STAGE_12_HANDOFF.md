# PCI Stage 12 → Stage 13 Handoff

**Project:** PSYCHO-CYBERNETICS-INTELLIGENCE (1 book, 10 modules)  
**App version:** `0.12.0` · **Knowledge schema:** `1.0.0` · **Personal record envelope:** `2.0.0` · **Feedback/scenario data contracts:** `1.0.0` · **Event version:** `2.1.0`.

## Canonical files and artifact inventory

1. `PCI_APP_STAGE12_FULL.zip` — **authoritative complete updated source repository**, public knowledge data, all 10 routes, functional labs, original Stage11 rollback at `rollbacks/PCI_APP_STAGE11_FULL.zip`, tests, schemas, compiled offline compatibility preview, full reference packs, updated canonical files.
2. `PCI_STAGE12_TEST_REPORT.md` — executed commands and status of each acceptance gate. Included inside source ZIP and separately downloadable.
3. `PCI_STAGE_12_HANDOFF.md` — this file; included inside source ZIP.
4. `PCI_STAGE12_ARCHIVE_QA.json` — independent extracted-ZIP checksums and retest report, separately downloadable.
5. `PCI_STAGE12_MIGRATION_NOTES.md` and `PCI_STAGE12_CHANGELOG.md` — details of additive contracts and explicit deferred issues.

The source ZIP contains `FILE_INVENTORY.json` and `CHECKSUMS.sha256` listing/hashing all inventoried project files (excluding those two inventory files themselves).

## Preserve these app and data contracts

- **All 10 previous routes remain unchanged:** `command-center`, `self-image`, `beliefs`, `theater`, `feedback`, `conditioning`, `scenarios`, `knowledge`, `academy`, `archive`.
- **Canonical book records unchanged:** 201 concepts, 16 chapters, 109 provisional relationships, 70 source-described practices, 12 PCI-created rehearsal templates, 16 authored scenarios; all earlier research reference paths unchanged. No bundled full book PDF.
- **1,781 inherited permanent IDs** preserved exactly. Four additive **issue IDs** `PCI-ISS-ST12-001` to `PCI-ISS-ST12-004` added, for **1,785 registered IDs**. No book or exercise IDs changed.
- **Private IndexedDB:** `pci-private-v1` `DB_VERSION=2` with **25 unchanged stores**. No new stores or destructive migrations.
- **Feedback:** `src/feedback-model.ts`, `src/feedback-repo.ts`, `src/feedback.tsx`; records in `goals`, `experiments`, `predicted_outcomes`, `observed_outcomes`, and minimal `events`. Fields are additive via `feedback_contract_version:1.0.0` on data, with original stable UUIDs. Prediction text never copied into outcome records or global events.
- **Scenarios:** `src/scenario-model.ts`, `src/scenario-repo.ts`, `src/scenarios.tsx`; original `PCI-SC-CHxx-001` definitions in `public/data/scenarios/*.json`; saved `scenario_progress` v1 records and minimal completion/start events. Unknown/malformed definitions quarantined.
- **Theater:** `src/theater-guidance.ts` (new) computes visible instructions from original unchanged templates. `src/theater.tsx` resolves saved scenes by private UUID; all 9 private scene fields are used in the appropriate 5 phases. No private text exported as public assets or copied into global event records.
- **Schemas:** `schema/PCI_STAGE12_*.schema.json`, `schema/PCI_STAGE12_EVENT_EXTENSION.json`. Follow migration notes; do not create parallel new stores for Stages13–14.

## What actually works (as tested)

- Theater default/written guidance and 2 private scene comparisons: Node and simulated Chromium **PASS**.
- Feedback goal, prediction, observation, iteration updates, deletion and minimal event lifecycle: Node and simulated Chromium **PASS**.
- 16 scenario graph validations, branching and simulator UI: Node and simulated Chromium **PASS**.
- 86 Node tests, 38 new Stage12 asset tests and both 50-check/56-check in-memory Chromium suites **PASS**. Exact command transcript and exceptions: `audit/stage12/` and test report.
- TypeScript strict check, lint, offline compatibility compile **PASS**.
- Official Vite/React18 build **BLOCKED** (`vite: not found`); native IndexedDB/Safari **NOT_TESTED**. Do not claim a production release or valid physical-device persistence.

## Mandatory issue ownership

- `PCI-ISS-ST12-001` / `PCI-UX-001`: **RESOLVED** Theater default guidance repair.
- `PCI-ISS-ST12-002` / `PCI-UX-002`: **RESOLVED** private scene playback repair.
- `PCI-ISS-ST12-003` / `PCI-UX-003`: **OPEN, Stage14 owner**, template manual phase timing vs auto-advance mismatch, Stage15 regression required.
- `PCI-ISS-ST12-004` / `PCI-DATA-004`: **OPEN, Stage14 owner**, cross-module hash-route unsaved-work protection.
- `PCI-ISS-ST11-001` and `PCI-ISS-ST11-002`: **OPEN Stage15/16**, real npm Vite production build, native HTTPS-origin IndexedDB, Safari and backup recovery.

## Stage13 attachments and exact starting instructions

Attach **`PCI_APP_STAGE12_FULL.zip` and `PCI_STAGE_12_HANDOFF.md`**. Include `PCI_ACTIVITY_ENGINE_DATA_v1.zip` and `PCI_PERSONALIZATION_ENGINE_v1.zip` only if needed for comparison; full reference contracts and public assets are already embedded in the app ZIP. Do not ask for duplicate packs without first inspecting `reference/activity/` and `reference/personalization/`.

Stage13 must extend the full Stage12 repo. Focus on **Mental Conditioning Lab and Mental Mastery Academy**, using existing 21-day curriculum, personalized recommendation/review algorithms and `events` store. Read the full Stage12 source contracts first. Keep Stage12 Feedback, Theater and Scenario routes functioning; do not invent parallel event schemas, synthetic progress or an unsupported AI evaluator. Preserve Stage12 backup and run the existing automated checks first.

**Release remains conditional** on Stage14 timing/global dirty-navigation fixes and Stage15–16 native browser/production validation.
