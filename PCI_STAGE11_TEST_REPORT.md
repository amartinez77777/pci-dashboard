# PCI Stage 11 — Build, Timer, Persistence and Regression Test Report

**Project:** PSYCHO-CYBERNETICS-INTELLIGENCE  
**Current app:** `0.11.0` · **Stage:** 11/16 · **Research schema:** `1.0.0` · **Private record schema:** `2.0.0` · **Rehearsal session data:** `1.0.0` · **Event extension:** `2.1.0`

## Actual source inputs inspected

All four prerequisite ZIPs were opened and inspected by extracting their files. Their archive SHA-256 hashes:

| File uploaded | SHA-256 |
|---|---|
| `PCI_APP_STAGE10_FULL(1).zip` | `2c84898ce0ab1f47e8b3c7492f67755112b8568bdadee5d8ff8f34cbd41be210` |
| `PCI_STAGE_10_HANDOFF_iPhone(1).zip` | `7a54796bf2299e1f8288496180d82c0d2f9d1413144c229b4b021fbffa8529f2` |
| `PCI_ACTIVITY_ENGINE_DATA_v1(3).zip` | `4a05f6cd19f49f7e07e9252187302ad427572e0cad28b2fc0e374c2bce4f75ac` |
| `PCI_PERSONALIZATION_ENGINE_v1(2).zip` | `b726f90b2325b3527b37c2f156765b635dc08066b2377310b38c3b3d294bf271` |

Original 332-page book PDF was **not attached to Stage 11**; no fresh primary-source page verification is claimed. The 12 source-linked rehearsal templates and 70 practice provenance rows were inherited unchanged from the Stage06 activity pack, with a new *display-only* attribution projection.

## Implemented, observed in source and checked by executable tests

- Theater of the Mind now mounts at `#/theater`, preserving all 10 original routes and Stage09/10 features.
- 12 structured 5-phase PCI adaptations, with the canonical source concept links, separate original book-practice section, PDF page vs printed-page locators, and a warning that source presence is not empirical validation.
- Private scene builder: reusable scene create/edit/duplicate/delete, optional attached belief/goal ID, optional sensitive storage with explicit consent, no user text written to public assets.
- Deterministic player with Start, Pause, Resume, Previous, Next, Skip, Reset, Complete, Stop early, Save & exit; time-neutral mode, app-designed 300s/60s modes and optional 30–3600s custom mode. All templates retain origin=`PCI_adaptation` and `book_duration_claimed=false`.
- Wall-clock anchor calculations for background/suspension handling. If elapsed exceeds the guided template duration, playback reaches a review state without inventing an automatic completion. Paused time is excluded. Interrupted running sessions are restored paused after reload from the last saved checkpoint.
- Text-based equivalent on every phase. Speech synthesis is optional and feature-detected; Stop speech is implemented. No speech audio files are generated or advertised.
- Session draft and completion records in existing `rehearsal_sessions` (v2 IndexedDB), source IDs immutable. Idempotent `rehearsal.started`, `rehearsal.completed` and additive `rehearsal.stopped` events stored in `events`. Duplicate completion does not double-count. Optional confidence/tension ratings are self-reported observations, not psychological diagnostic scores.

## Actual test commands and results

| Command | Result | Scope |
|---|---|---|
| `node --test tests/data_repo.test.mjs tests/vault_unit.test.mjs tests/labs_model_repo.test.mjs tests/theater_model_repo.test.mjs` | **PASS 69/69** | Existing data/Vault/Belief tests + 20 new Stage11 state/repository tests, synthetic IndexedDB |
| `python tests/validate_assets.py` | **PASS 34/34** | Stage08 research integrity |
| `python tests/validate_vault.py` | **PASS 17/17** | Stage09 research/search and original registry mappings; exact-count assertion updated to allow Stage11 issue IDs |
| `python tests/validate_stage10.py` | **PASS 34/34** | Stage10 lab preservation; same ID-count compatibility correction |
| `python tests/validate_stage11.py` | **PASS 45/45** | Stage10 rollback hash comparisons, source templates, 70 practice rows, schema/refs and privacy boundaries |
| `npm run typecheck` | **PASS** | Strict TypeScript |
| `npm run lint` | **PASS** | Project lightweight source safety lint + TypeScript; **not ESLint** |
| `npm run build:offline` | **PASS** | Offline React16 compatibility build for limited browser checks, **not official React18 production** |
| `python tests/browser_stage11_smoke.py` | **PASS 56/56** | In-memory Chromium React16 bridge, synthetic IndexedDB at 1440, 390, 320 px, no blocking horizontal overflow |
| `npm run build` | **BLOCKED** | TypeScript passed; `vite: not found`, command exit code 127 |
| Chromium `page.goto('http://127.0.0.1:18761/')` | **BLOCKED** | `net::ERR_BLOCKED_BY_ADMINISTRATOR` on localhost, native-origin persistence cannot be verified |
| Native IndexedDB reload, real iOS Safari, VoiceOver, speech audible output | **NOT_TESTED** | Requires supported real origin / device |
| Full offline re-entry after asset cache eviction | **NOT_TESTED** | No service worker or offline caching guarantee |

### Representative executed tests

- Timer start/pause/resume after simulated clock advance; multiple phase crossings after background return; no automatic completion when time expires; untimed, short, full and invalid custom ranges.
- Private create/update/duplicate/delete, sensitive explicit consent, redacted vs full backup, atomic started event, saved draft, completed event idempotency, session-event deletion.
- In-memory Chromium navigation, 12 template cards, scene save, player controls, skip/rewind, optional reflection, single session history, Knowledge Vault and Belief Studio routes, and 3 responsive viewport widths.

**Test interpretation:** these are structural/functional simulated-environment checks, not evidence that visualization changes personality or real-world performance. The in-memory browser harness does not prove durable native IndexedDB transactions or real browser audio availability.

## Known limitations and release gates

1. **`PCI-ISS-ST11-001` critical:** `vite` is unavailable locally. A real React 18/Vite production bundle has not been verified.
2. **`PCI-ISS-ST11-002` major:** actual native IndexedDB, HTTPS-origin reload, iOS Safari and speech are not tested; administrator blocks localhost browser navigation.
3. **`PCI-ISS-ST11-003` major:** no service worker for offline reload; periodic active-session drafts are checkpoints, not crash-atomic guarantees. A browser crash can lose elapsed seconds since the last write.
4. Existing earlier research integrity limitations (including medical and paranormal claims) remain unresolved; original practice attribution `31 book`, `4 updated_edition_editor`, `35 uncertain` is retained.

There are **no newly registered research facts or permanent concept ID changes**. The original 1,778 app IDs are preserved, with 3 new Stage11 issue IDs, total **1,781**.
