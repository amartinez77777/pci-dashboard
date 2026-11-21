# PCI | Stage 06 Handoff for Prompt 07

**Date:** 2026-11-20. **Project:** PSYCHO-CYBERNETICS-INTELLIGENCE. **Schema:** Stage 06 content v1.0.0; canonical knowledge v1.0.0, research v1.3.0 unchanged. **Primary PDF SHA-256:** `4dd7a311a21af58aa075176abb48fd60b348c70bb314a2ca09f66383922e7e9b`.

## Attach to Prompt 07

1. `PCI_KNOWLEDGE_CANONICAL_v1.zip` from Stage 05 (the source-of-truth research pack; do not reconstruct 1,676 records from chat).
2. `PCI_ACTIVITY_ENGINE_DATA_v1.zip` from Stage 06 (this deliverable).
3. `PCI_ACTIVITY_DESIGN_AUDIT.md` or its iPhone TXT equivalent.
4. `PCI_STAGE_06_HANDOFF.md` or its iPhone TXT equivalent.
5. Original PDF **only** when disputed book exercise timing or source meaning needs new direct inspection (provided and checked this stage).

## Input verification

Opened actual uploaded canonical ZIP, both supplied iPhone ZIPs containing Stage 05 report and handoff, and original PDF. ZIP SHA-256 `e26e80a5077efd4f39e3cf619e961e15b1acd84664759d02f5f7beebef1f7960`; PDF fingerprint matched canonical manifest. Reexecuted extracted canonical validator: **PASS 23/23**. Did not rewrite canonical research records.

## Files delivered and semantic contracts

`PCI_ACTIVITY_ENGINE_DATA_v1.zip` contains `PCI_PROJECT_MANIFEST.json`, `PCI_ID_REGISTRY.json`, `PCI_ISSUES.json`, `README.md`, `PCI_ACTIVITY_DESIGN_AUDIT.md`, this handoff, `CHECKSUMS.sha256`, `FILE_INVENTORY.json` and:

- `data/PCI_EXECUTABLE_ACTIVITIES.json`: 32 declarative runnable step sequences `PCI-ACT-CHxx-00x`, linked back to existing `PCI-EDU-*` and `PCI-C-*` IDs.
- `data/PCI_BRANCHING_SCENARIOS.json`: 16 `PCI-SC-CHxx-001` graphs with 2 decision nodes per path and 4 hypothetical endings, plus safe exit.
- `data/PCI_REHEARSAL_TEMPLATES.json`: 12 `PCI-RH-001..012` templates with 5 manual phases and full/reduced/no-timer variants.
- `data/PCI_FEEDBACK_PATTERNS.json`, `PCI_REVIEW_RUBRICS.json`, `PCI_FEEDBACK_CYCLES.json` (5/3/2 entries).
- `data/PCI_AUTHOR_PRACTICE_LOOKUP.json`: 70 reference-only bridges to canonical `PCI-AP-*`; book timings and attribution are not overwritten.
- `indexes/`: per-chapter, per-concept and author-practice bridge maps (all targets resolve against Stage 05).
- `schema/`: JSON Schemas for activities, scenarios, rehearsals, feedback, rubric and private event, plus `PCI_RUNTIME_CONTRACT.json`.
- `types/PCI_ACTIVITY_ENGINE_TYPES.ts`: public content TypeScript contracts.
- `tests/run_content.py`: working stateless reference interpreter; validator `validate_stage06.py`; negative tests `test_negative_cases.py`; execution fixtures.
- `audits/`: executed QA and negative-test outputs; coverage matrix, PDF spot checks and TypeScript build log.

New permanent IDs: 32 `PCI-ACT-*`, 16 `PCI-SC-*`, 12 `PCI-RH-*`, 5 `PCI-FB-*`, 3 `PCI-RUB-*`, 2 `PCI-LOOP-*`, and 1 `PCI-ISS-056`: **71 new**. Prior **1,676** IDs preserved; updated registry **1747**. No prior identifier renumbered, redirected or retired. Private events have a proposed schema but no private data in the public pack.

## Actual tests and caveats

- Baseline canonical validator: **PASS 23/23**.
- Stage 06 check suite: **PASS 42/42**; source/FK validation, 64 scenario paths, step completion/skip and timers.
- Negative-input suite: **PASS 10/10**.
- TypeScript `tsc --noEmit`: **PASS**.
- Actual PDF pages 34, 52 and 143 directly reviewed for original book timing distinctions. Not an exhaustive recheck of all 70 author practices.
- **NOT TESTED**: browser interaction, IndexedDB persistence, real-device accessibility, medical/psychological efficacy or longitudinal improvement.

## Stage 07 implementation requirements

Use canonical + Stage 06 bundles. Build device-local profile/goals and choice-dependent, **nonclinical** recommendations only after explicit user preferences; no hidden AI. Render the generic activity/scenario/rehearsal schemas instead of hardcoding 60 unique pages. Store private event log and user-created scenes in IndexedDB with schema migration and versioned JSON export/import. Use explicit optional limits on reminders and never report psychological trait scores. Preserve source/evidence status labels. Validate iPhone Safari, mobile keyboard, skip/stop, accessibility and loss-of-data recovery once a browser UI exists.

Known blockers: 55 inherited research issues plus new `PCI-ISS-056`, stage 05 subsection-status ambiguity, and future real-browser testing. No existing working app was supplied or claimed in Stage 06.
