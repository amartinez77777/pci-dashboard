# PCI | Stage 07 Handoff for Prompt 08

**Date:** 2026-11-20. **Project:** PSYCHO-CYBERNETICS-INTELLIGENCE. **Source edition:** PCI-ED-001, revised 2002 Prentice Hall Press edition, source SHA-256 inherited `4dd7a311a21af58aa075176abb48fd60b348c70bb314a2ca09f66383922e7e9b` (not independently rechecked against a PDF in Stage 07). **Schema versions:** knowledge 1.0.0 retained, Stage 06 content 1.0.0 retained, private-data schema 2.0.0 (additive), personalization engine 1.0.0.

## Exactly what was opened and preserved

Opened 4 actual attached ZIPs:

- `PCI_KNOWLEDGE_CANONICAL_v1(2).zip` SHA-256 `e26e80a5077efd4f39e3cf619e961e15b1acd84664759d02f5f7beebef1f7960` (Stage 05 knowledge source).
- `PCI_ACTIVITY_ENGINE_DATA_v1(1).zip` SHA-256 `4a05f6cd19f49f7e07e9252187302ad427572e0cad28b2fc0e374c2bce4f75ac` (Stage 06 activity source).
- `PCI_STAGE_06_HANDOFF_iPhone(1).zip` SHA-256 `507d09eae0b928b10196ba25fcd80be949a8e75cc525798262d3b41ef8b17395` (contains Markdown/TXT).
- `PCI_ACTIVITY_DESIGN_AUDIT_iPhone(1).zip` SHA-256 `d01d8dd2bd370d4d3d455dee4bdb90561d55bc47e4a59f5cb2741ee4f47f65a2` (contains Markdown/TXT).

The original PDF was **not attached** in this stage. 1,747 inherited registry entries and 56 inherited issues are preserved exactly. Baseline original validators were rerun: **Stage 05 23/23 PASS**, **Stage 06 42/42 PASS**. There is no existing browser UI in these supplied packages.

## Canonical deliverables and versions

- `PCI_PERSONALIZATION_ENGINE_v1.zip`: Stage 07 populated JSON content, TS source + compiled JS, standalone private v2 schemas, 21-day curriculum, recommendation catalog, review seeds, module event map, synthetic-only input/output examples, test scripts/results, ID registry, manifest, integration guide and this handoff. No source PDF or user profile.
- `PCI_EXPERIENCE_INTEGRATION_GUIDE.md`: integration responsibilities, privacy, UX, events and staged testing.
- `PCI_STAGE_07_HANDOFF.md` (this file): actual inventory and continuation requirements.
- `PCI_STAGE_07_iPhone_COMPLETE.zip`: convenience ZIP containing the canonical Stage 07 archive and readable TXT/MD guide/handoff. All ZIPs can be extracted with the iOS Files app.

Schema contract: Stage 05 canonical v1.0.0 and Stage 06 activity v1.0.0 are immutable inputs. New `schema/PCI_PRIVATE_RECORD_v2.schema.json`, `PCI_PRIVATE_EXPORT_v2.schema.json`, `PCI_EVENT_v2.schema.json`, `PCI_INDEXEDDB_CONTRACT.json`, `PCI_ALGORITHM_CONTRACTS.json` are additive contracts and do **not** rewrite their earlier schemas.

## Created/changed IDs and coverage

New permanent IDs: `PCI-PROG-021` and `PCI-DAY-01` through `PCI-DAY-21` (**22 added, registry now 1,769**). No earlier IDs were changed, renumbered, redirected or retired. The **21 populated daily records** reference verified-in-the-source or provisional concept statuses as inherited, 21 existing `PCI-ACT-*` mappings, optional existing scenario/rehearsal IDs, and unique concrete tasks. Four checkpoints: 4, 9, 15, 21. **All 10 modules** are represented. 60 ranking candidates cover all 32 Stage 06 activities, 16 scenarios and 12 rehearsals. 201 concept seeds are included for the review queue.

Private record IDs are user-generated UUID-style IDs at runtime, **never prefilled** in public production assets. Synthetic sample identifiers live **only** in test files and explicitly labeled fixture examples. Legacy v1 IDs are retained in `legacy_id` during migration using deterministic namespaced wrapper UUIDs. Stage 07 adds **25 local store contracts** (6 legacy retained, 19 new), explains v1→v2 migration and exports; no actual browser database or real user data is included.

## Algorithms, tests and results

- `impl/pci-core.ts`: pure `recommend` with explicit `reason_codes`/point breakdown and deterministic tie-break; SM-2-like `scheduleReview`, `replayReviews` undo, DST-safe local calendar, transparent `gradeObjective`, user-driven `selfRateArtifact`, `aggregateMetrics` idempotency, optional 21-day progression, onboarding state transitions.
- `impl/pci-private.ts`: v1 backup migration, redacted v2 export helper, dry-run validator, optional checksum, proposed browser IndexedDB open/append/import and consent checks. **Browser transactions NOT tested**.
- `tests/test_algorithms.cjs` and `tests/test_backup_async.cjs`: executed Node pure-function tests; results in `audits/PCI_ALGORITHM_TESTS.log` and `audits/PCI_BACKUP_TESTS.log`.
- `tests/validate_stage07.py`: executed real JSON Schema checks + referential integrity + content QA, output `audits/PCI_STAGE07_SCHEMA_QA.json`.
- `tsc -p tsconfig.json`: TypeScript compile **PASS**. This is not a browser build or mobile test.
- `PCI_STAGE_07_QA.json` and `audits/PCI_STAGE07_ARCHIVE_QA.json`: final test and extracted-archive verification summaries.

All historical Stage 05/06 reference records were preserved. Inherited scientific uncertainty and **56** research/quality issues remain open or in their original states. No new scientific validation, therapeutic effect or automatic user characterization is claimed.

## Implementation semantics for Prompt 08

1. Read the **actual Stage 05 canonical ZIP**, **actual Stage 06 activities ZIP** and **actual Stage 07 personalization ZIP**; fail visibly if missing. Also attach this handoff and `PCI_EXPERIENCE_INTEGRATION_GUIDE.md`.
2. Build the Vite+TypeScript frontend shell and responsive navigation for the 10 locked modules; consume the existing 32 activity schemas, 16 scenario graphs and 12 rehearsals instead of hardcoding substitutes.
3. Keep all book content read-only and local private data in IndexedDB v2. The six legacy stores are retained, no versionchange deletion. Ask consent before sensitive fields and imports; default backup excludes sensitive data, warns of unencrypted JSON, and never uploads automatically.
4. Build ONE event dispatcher using Stage 07 event `schema_version=2.0.0`; adapt Stage 06 proposed v1 events explicitly. Use unique event idempotency keys, derived projections, safe undo and empty states.
5. Render recommendation reason codes, allow manual choice and optional cold start. Implement the 21-day curriculum as optional user-paced participation, **not** book doctrine. Provide skip, rest, restart and accessibility controls.
6. Validate **actual browser** IndexedDB transactions, refresh persistence, atomic import rollback, iPhone Safari behavior, Files export/import, keyboard and VoiceOver, responsive touch targets, no fake AI, no psychological trait scores and no personal records in static assets.

**Attach for Prompt 08 exactly:** `PCI_KNOWLEDGE_CANONICAL_v1.zip`, `PCI_ACTIVITY_ENGINE_DATA_v1.zip`, `PCI_PERSONALIZATION_ENGINE_v1.zip`, `PCI_EXPERIENCE_INTEGRATION_GUIDE.md` (or iPhone TXT), `PCI_STAGE_07_HANDOFF.md` (or iPhone TXT). Original PDF only for future disputed source checks. **Do not reconstruct preceding content from chat.**

## Open limitations / truthful status

- **PASS**: identity stability, source links as inherited, 21 distinct days, explainable deterministic ranking, pure scheduler/undo/DST tests, simulated event idempotency, schema and fixture checks.
- **PARTIAL**: full end-to-end storage migration/consent workflows (storage adapter implemented but not used in a browser), completeness of earlier research (inherited 56 issues, no new direct PDF checks).
- **NOT_TESTED**: IndexedDB browser run, Safari mobile persistence, accessibility interaction, encrypted backups, server sync (out of scope), clinical or longitudinal efficacy.

Every asserted final test result is accompanied by actual executable commands and audit artifacts in the ZIP. No prior release was deleted or changed.
