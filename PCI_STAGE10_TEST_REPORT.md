# PCI Stage 10 — Build, Research Continuity and Test Report

**Stage:** 10/16 · **Project:** `PSYCHO-CYBERNETICS-INTELLIGENCE` · **App version:** `0.10.0` · **Report date:** November 20, 2026

## Actual evidence opened

| Exact incoming attachment | SHA-256 | Notes |
|---|---|---|
| `PCI_APP_STAGE09_FULL(1).zip` | `7815b94e3d27655195af5a6f2ae248961a4516f053dc25036e804065dc2adbba` | Opened 430 archive members. App restored and original tests run. |
| `PCI_KNOWLEDGE_CANONICAL_v1(5).zip` | `e26e80a5077efd4f39e3cf619e961e15b1acd84664759d02f5f7beebef1f7960` | Opened actual canonical research. |
| `PCI_STAGE_09_HANDOFF_iPhone(1).zip` | `45156fa44d29a616e5452d39c5123a50938bcfb42b9e88fd9110d34a0ae0d2f5` | Read handoff contents. |
| `PCI_PERSONALIZATION_ENGINE_v1.zip` (already present in the current session) | `b726f90b2325b3527b37c2f156765b635dc08066b2377310b38c3b3d294bf271` | Opened contracts and v2 event/private-record schemas. |
| `PCI_ACTIVITY_ENGINE_DATA_v1.zip` (already present in the current session) | `4a05f6cd19f49f7e07e9252187302ad427572e0cad28b2fc0e374c2bce4f75ac` | Opened activity data and source linkage specifications. |

The original book PDF was **not attached in Stage 10**. Page references and scientific evidence status are inherited from canonical Stage05, not newly verified here.

## Changes actually implemented

The existing app now mounts both guided labs through the original `#/self-image` and `#/beliefs` hash routes. The Self-Image Lab supports voluntary area selection, 3-step inventory, field-separated observations/goals, an explicit user-entered connection map, edits/history, and private reflections. The Belief Studio supports multiple belief/draft records, 5-stage creation, separate evidence for/against, situational barriers, alternative interpretations, testable hypotheses, optional small experiments, revision comparisons, voluntary conviction trends, experiment outcomes and confirmed deletion.

All personal fields stay in the original 25-store version-2 IndexedDB schema. Sensitive records require explicit consent. Old and new snapshots remain attached to stable belief UUIDs. Source recommendations use explicit domain selection and actual concept IDs. No AI-generated evaluations, hidden psychological scores, diagnostic inferences, or complete copyrighted PDF were added.

## Executed tests and observed outcomes

| Command/test | Result | Environment limitation |
|---|---|---|
| `npm run typecheck` | **PASS** | Strict TypeScript, compiler installed. |
| `npm run test:repo` | **PASS 14/14** | Original data repository tests. |
| `npm run test:vault` | **PASS 19/19** | Original Stage09 search/graph suite. |
| `npm run test:assets` | **PASS 34/34** | Original Stage08 asset checks. |
| `npm run test:vault:assets` | **PASS 17/17** | Stage09 source projection checks. |
| `npm run test:labs` | **PASS 16/16** | Node with synthetic IndexedDB facade; covers create/revise/evidence/consent/outcome/export/cascade-delete and stale-edit conflict. **Not native IndexedDB.** |
| `npm run test:stage10:assets` | **PASS 34/34** | Original static research bytes, ID continuity, links, lab schemas and privacy code checks. |
| `npm run build:offline` | **PASS** | React 16 compatibility preview only, not React 18/Vite production. |
| `python tests/browser_stage09_smoke.py` | **PASS 54/54** | In-memory Chromium, no origin or IndexedDB. Previous 10 routes, vault and graph unchanged. |
| `python tests/browser_stage10_smoke.py` | **PASS 43/43** | In-memory Chromium + *synthetic* IndexedDB facade; UI creation, editing, history, outcomes, delete, source links; 1440, 390, 320 px. Not iPhone or native IndexedDB. |
| `npm run build` | **BLOCKED / exit 127** | `tsc --noEmit` passed; `vite: not found`. npm cache lacks Vite and no valid lockfile was invented. |
| HTTPS-origin Chromium / native IndexedDB / physical iPhone | **NOT_TESTED** | `page.goto()` blocked by administrator policy for localhost and mock HTTPS. Native IndexedDB denied in `about:blank`. |
| Screen reader / iPhone Safari persistence and reload | **NOT_TESTED** | Requires testing on a real origin/device. |

Earlier intermittent first smoke failures were test-harness/environment issues: synthetic IDB assignment did not replace Chromium's denied native getter, and an edit-flow test attempted a step-3 field while still on step 2. The facade property assignment and navigation test were corrected; **final** executions passed 16/16 and 43/43. Earlier failures are not presented as successful native browser tests.

## Preservation, security and integrity

- The original **1,773** ID assignments and metadata are unchanged; 5 new issue IDs are registered for unresolved engineering tasks. Combined registry: **1,778 IDs**.
- All inherited segmented knowledge JSON and full canonical reference assets remain byte-identical to the uploaded Stage09 source, including 201 concepts, 109 graph edges, 70 indexed author-practice records, and 504 search destinations.
- Personal data is not preseeded. Synthetic test fixtures exist only in `tests/`, not in `public/` or the runtime default state.
- No personal text is written into analytics events; event metadata has IDs and origin/revision information only. Existing Study/Knowledge Vault storage contracts are unchanged.
- Default personal export excludes sensitive flagged records; full backup requires explicit choice and contains unencrypted user-controlled data.
- Existing 10 routes and accessible non-graph source panels remain available. Browser and touch accessibility require real-device follow-up.

## Open issues

`PCI-ISS-ST10-001..005` are retained in `PCI_ISSUES.json`, covering native storage/device testing, official Vite production build, additive event consumer compatibility, unsaved navigation/native recovery testing, and opt-in background draft autosave. These are genuine blockers/deferrals, not completed features.

**Stage 11 input:** `PCI_APP_STAGE10_FULL.zip`, `PCI_ACTIVITY_ENGINE_DATA_v1.zip`, `PCI_PERSONALIZATION_ENGINE_v1.zip`, `PCI_STAGE_10_HANDOFF.md` (plus canonical pack for source dispute verification). Stage11 must modify the whole application and use saved `beliefs`/`experiments` v2 records rather than copying them into a new system.
