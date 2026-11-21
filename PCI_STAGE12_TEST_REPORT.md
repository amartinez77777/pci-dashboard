# PCI Stage 12 — Executed Test & Integrity Report

**Release candidate:** `0.12.0` · **Date:** 2026-11-20 · **Scope:** Theater personalization repairs, functional Feedback Lab and Scenario Simulator in the preserved Stage 11 repository.

## Verified inputs and restoration

| Opened input | SHA-256 | Purpose |
|---|---|---|
| `PCI_APP_STAGE11_FULL(1).zip` | `b93e70829a367eee89d032060ac1d9f1a67969a6faeffd2733683ca1823f7d5a` | Actual source, full rollback |
| `PCI_ACTIVITY_ENGINE_DATA_v1(4).zip` | `4a05f6cd19f49f7e07e9252187302ad427572e0cad28b2fc0e374c2bce4f75ac` | Full activity/scenario authoring pack |
| `PCI_PERSONALIZATION_ENGINE_v1(3).zip` | `b726f90b2325b3527b37c2f156765b635dc08066b2377310b38c3b3d294bf271` | Personal event and v2 private-data contract |
| `PCI_KNOWLEDGE_CANONICAL_v1(6).zip` | `e26e80a5077efd4f39e3cf619e961e15b1acd84664759d02f5f7beebef1f7960` | Source and ID comparison |
| `PCI_STAGE_11_HANDOFF_iPhone(1).zip` | `31bfc64081b895640f8658a989e8cc526b9cc12db8156e39ac12a2537f436414` | Continuity notes |
| `PCI_STAGE11_INDEPENDENT_AUDIT.md` | Opened directly | Defect reproducers and issue aliases |

The standalone Stage 06 and Stage 07 artifacts were available and their original source/contract files were also found intact under `reference/activity` and `reference/personalization` in Stage 11. No missing prerequisites. No new primary-book PDF was attached; source-page provenance is inherited, not newly checked against book page images.

## Baseline BEFORE Stage 12 modifications

- `npm run typecheck`: **PASS** (exit 0).
- `npm run test:repo`: **PASS**, 14 tests.
- `npm run test:vault`: **PASS**, 19 tests.
- `npm run test:labs`: **PASS**, 16 tests.
- `npm run test:theater`: **PASS**, 20 tests.
- Legacy source asset validators: **PASS**, Stage08 34, Vault 17, Stage10 34, Stage11 45.
- `npm run build`: **BLOCKED**, exit 127 at `vite: not found` after typecheck. Original npm installation lockfile absent. No lockfile fabricated.

Command transcript files are included in `audit/stage12/base_*`.

## Changes that were actually implemented

1. **Theater defect A:** `src/theater-guidance.ts` generates different default and nonvisual guidance from each template's actual phase, scene, and educational purpose. Original template IDs, wording and source records remain unchanged. Written alternatives provide an actionable script/checklist adapted for each phase rather than the inherited repeated sentence.
2. **Theater defect B:** `src/theater.tsx` resolves the **actual private scene by UUID** from `rehearsals`, including restoration of saved sessions. Context appears in the 5 relevant phases using safe React text nodes, with intentionally blank-field prompts and a recoverable deleted-scene state. Template selection now starts the chosen template, not the previous state value.
3. **Feedback Lab:** functional `#/feedback` goal CRUD, separate `predicted_outcomes` and `observed_outcomes`, optional source/practice/belief and rehearsal links, review dates, multiple experiments per goal, revision snapshots, revised next actions, local reload of history, and event idempotency. No synthetic goal metrics.
4. **Scenario Simulator:** `#/scenarios` loads and validates all **16 supplied** scenarios. Generic 2-decision-path playback, choice consequence/tradeoff, safe exit, back, restart, manual completion, reflection, resume and history. Malformed graphs are quarantined. Outcomes explicitly hypothetical.
5. Shared `learning-events.ts` uses the **existing IndexedDB v2 stores** for multi-store write transactions and duplicate-event checks. Event payloads exclude user-authored scene, reflection, prediction and observation prose.

## Executed POST-CHANGE tests

| Command or test | Result | Scope |
|---|---|---|
| `npm run typecheck` | **PASS** | Strict TypeScript for full app |
| `npm run lint` | **PASS** | Source lint |
| `npm run test:repo` | **PASS**, 14/14 | Original data repository |
| `npm run test:vault` | **PASS**, 19/19 | Original Knowledge Vault |
| `npm run test:labs` | **PASS**, 16/16 | Original Self-Image / Belief Studio |
| `npm run test:theater` | **PASS**, 20/20 | Original player/session model |
| `npm run test:stage12` | **PASS**, 17/17 | Source-specific guidance, scene comparison, v2 private record lifecycle, all scenario graph branches, event protection, deletion |
| `npm run test:assets` | **PASS**, 34/34 | Updated honest Stage08 audit (no stale claim of zero completed sessions) |
| `npm run test:vault:assets` | **PASS**, 17/17 | Vault source graph and assets |
| `npm run test:stage10:assets` | **PASS**, 34/34 | Preserved Stage10 contract |
| `npm run test:stage11:assets` | **PASS**, 45/45 | Stage11 contract with documented Stage12 ID extension |
| `npm run test:stage12:assets` | **PASS**, 38/38 | All inherited IDs, source bytes, source links, schema and new issues |
| `npm run build:offline` | **PASS** | Inherited React16 compatibility preview; **not** React18/Vite build |
| `python tests/browser_stage11_smoke.py` | **PASS**, 56/56 | React16 in-memory Chromium, synthetic IndexedDB, desktop/390px/320px old Theater & Vault controls |
| `python tests/browser_stage12_smoke.py` | **PASS**, 50/50 | React16 in-memory Chromium, synthetic IndexedDB, 1440px/390px Feedback, Scenario, Theater, labs and source routes |
| `npm run build` | **BLOCKED**, exit 127 (`vite: not found`) | Actual React18/Vite production verification unavailable |
| HTTPS-origin IndexedDB reload / real iPhone Safari | **NOT_TESTED** | Browser origin was blocked by environment; do not claim native persistence |

**Existing Node cases + new Node cases:** 69 + 17 = **86/86 PASS**. Source validators all pass, and 2 simulated Chromium suites report **106 PASS** checks. These counts are automated code/UI checks, not empirical validation of the book's theories.

The extended **320px Stage12** browser interaction attempt exceeded its runtime budget and was stopped. That extra run is **NOT_TESTED** as a complete Stage12 suite. Its earlier Stage11-only 320px regression remains PASS. Stage12 full scenario and Feedback tests were verified at 390px and 1440px without horizontal overflow.

## Gate outcomes

| Gate | Result | Evidence and caveat |
|---|---|---|
| **12.1: Specific Theater phase guidance and nonvisual alternative** | **PASS** | 60 alternatives inspected via `stage12_model_repo.test.mjs`; rendered phase-switching checks |
| **12.2: Two private scenes on one template differ visibly** | **PASS** | Actual rendered scene title **and setting** compared in simulated Chromium; HTML-like user content escaped |
| **12.3: Goal -> prediction -> action -> observation -> adjust -> review** | **PARTIAL** | Functional model and simulated browser PASS, revisit after route remount PASS; **native browser reload/durability NOT_TESTED** |
| **12.4: All valid scenarios playable, branch and persist progress** | **PASS with qualification** | 16/16 graphs structurally valid; 2+ choices and 4 distinct outcomes each; browser simulation and repo saves PASS; native persistence NOT_TESTED |
| **12.5: No proven Stage08–11 regression** | **PASS with qualification** | 86 Node tests, inherited asset validators and 56 preserved Chromium smoke checks PASS. Official Vite build remains BLOCKED |

## Open release gates and owners

- `PCI-ISS-ST12-003` / `PCI-UX-003`: all 12 templates declare `auto_advance=false` and `pause_after=true` but `settleClock` crosses phases with elapsed time. **Stage14** must reconcile model and metadata; **Stage15** must retest interruptions.
- `PCI-ISS-ST12-004` / `PCI-DATA-004`: global hash navigation can lose dirty Theater scene/feedback edits without a cross-route warning. **Stage14** global navigation guard / draft retention required.
- Inherited `PCI-ISS-ST11-001`: install genuine dependencies and perform real React18/Vite production build with valid generated lockfile. **Stage15–16**.
- Inherited `PCI-ISS-ST11-002`: HTTPS-origin native IndexedDB, backup/restore and physical iPhone/Safari QA. **Stage15–16**.
- Mobile-density/touch-target and speech availability audits remain pending physical-device review.

**Interpretation:** Stage12 features have real source code and executable tests, with meaningful simulated UI checks. This does not constitute a production-ready or native-storage-certified release.
