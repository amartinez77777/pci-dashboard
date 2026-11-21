# PCI Stage 07 — Experience Integration Guide

**Project:** PSYCHO-CYBERNETICS-INTELLIGENCE (single-book, 16-stage). **Stage:** 07. **Knowledge schema:** v1.0.0 unchanged. **Stage 06 activity content:** v1.0.0 unchanged. **New private-data schema:** v2.0.0. **Personalization engine:** v1.0.0.

## 1. What the engine is and is not

This deliverable contains executable, deterministic TypeScript learning and storage helpers; 21 populated curriculum days; recommendations over the existing 32 activities + 16 scenarios + 12 guided rehearsals; and 201 concept review seeds. It is **not a frontend or a validated iPhone IndexedDB implementation**. It does not infer identity, diagnoses, subconscious change, learning styles, or any hidden trait. The ranking `score` is merely an explainable **content-match priority**, not a psychological measure. A book citation proves only that the revised book contains a claim; it does not make the claim scientifically true.

The optional PCI-created 21-day path is **not** the source book's universal prescription or a scientifically established transformation timeframe. Book-specific practices and timings remain in the unchanged Stage 05 and 06 source packs.

## 2. Data sources and boundaries

- Public, read-only content: `PCI_KNOWLEDGE_CANONICAL_v1.zip` and `PCI_ACTIVITY_ENGINE_DATA_v1.zip`. Retain all 1,747 earlier IDs and the exact source/evidence statuses.
- New public Stage 07 content: `data/PCI_21_DAY_CURRICULUM.json`, `data/PCI_RECOMMENDATION_CATALOG.json`, `data/PCI_REVIEW_SEEDS.json`, `data/PCI_MODULE_EVENT_MAP.json`, and `PCI_ID_REGISTRY.json`. No private profile or user journal is included.
- Private user-owned content: `pci-private-v1` IndexedDB database, version **2**. Defined in `schema/PCI_INDEXEDDB_CONTRACT.json`. The 6 legacy stores remain intact; 19 additive stores introduce versioned typed records. The browser-side adapter is provided but **not browser-tested**.
- There is **no server sync**, remote model, account authentication, automatic cloud backup, background data export, or default analytics. Static GitHub Pages hosting cannot store user records on its own. Users must be told that deleting site data, changing device/browser or private browsing restrictions may erase local entries.

## 3. Onboarding, preference and recovery journey

1. Start `not_started`. Show what is local, what is sourced, limitations, and an option to browse without supplying a profile.
2. `preferences_optional`: choose local time zone, duration/intensity, topic interests and whether sensitive examples can appear. **No response is mandatory**. Sensitive notes require separately recorded permission.
3. `choose_goal`: optionally create a specific, reversible goal or select an exploratory path. Avoid demanding motivation, trauma disclosure or personal history.
4. `choose_activity`: call `recommend(catalog, context)` with explicit goals, due reviews and history. Display **reason codes**, short plain-English rationales, source status and content origin. Include manual browsing and exclusion controls.
5. `doing_activity`: use the **Stage 06** generic step, scenario or rehearsal renderer; preserve its safe exit, short/no-timer option, source links and feedback mappings.
6. `review_optional`: ask for an objective answer (if answer key exists) or voluntary 0–2 self-rating of observable steps, then optionally schedule a review. Never infer understanding from journal text.
7. `resting` / `returning`: no missed-day penalty. After 30+ calendar days, recommend a smaller restart. User can skip, pause or stop at any point.

Transitions are implemented in `transitionJourney`. Presentation and persistence of the current journey state belong to Stage 08/11 UI. Accessibility: keyboard navigation, manual timers, screen reader labels, motion reduction, no required sensory imagery, and stop/skip on every sensitive route.

## 4. Recommendations, fairness and traceability

`recommend` reads only selected goal priority/tags, interests, reported difficulty topics, due reviews, observed activity history, explicit excluded/pinned IDs, duration preference, sensitivity opt-in and a supplied local date. The ranking formula is deliberately simple: goal match +12 to +32, interest +12, difficulty +8, due review +25, new content +10, cold-start baseline, and recent activity penalties. Manual pin adds +100 but **does not override sensitivity or exclusion settings**. Stable ID is the deterministic tie-breaker. All contributions and `reason_codes` appear in output.

Examples in `examples/PCI_RECOMMENDATION_CASES_SYNTHETIC.json`: no preferences; goal preference; returned after 30+ days; recent skip; conflicting selected goals; manual override. These are **synthetic fixtures**, never a real user profile. Missing preferences do not generate an AI judgment. Users can always choose content directly.

## 5. Spaced review and assessments

`review` ratings 0=Again, 1=Hard, 2=Good, 3=Easy are voluntary memory/comfort ratings. The documented SM-2-like algorithm begins at an ease of 2.5 (min 1.3, max 3.0); advances 1/2/1/3 days respectively for the initial review, then adapts based on the **previous actual interval**. Intervals are capped at 365 days. Dates are **calendar days**: `addCivilDays` uses UTC noon to avoid DST 23-/25-hour drift, and `toLocalDate` converts an ISO timestamp using an IANA time zone. Schedule updates require explicit review actions, not a background clock.

Undo is modeled with `review.undone` pointing to the event ID; `replayReviews` excludes that event and recomputes state. Recognition and retrieval are distinct assessment modes for the frontend; the scheduler never equates a 3 with objective correctness. `gradeObjective` compares actual choice IDs to a provided answer key and rationale. `selfRateArtifact` reports only user-selected rubric anchors and refuses to score unspecified criteria. No psychological trait, IQ, diagnosis or therapeutic success score is computed.

## 6. 21-day path, pacing and four checkpoints

`PCI-PROG-021` links 21 **distinct** voluntary session records to source concepts and existing `PCI-ACT-*` activities, sometimes also scenarios or rehearsals. Each day has a concrete task, optional experiment, question, approximately 3-minute alternative, and source/evidence status. The program covers all **10 modules** and includes checkpoints on **days 4, 9, 15 and 21** to review goals, evidence, intensity and rest. Emotionally difficult exercises accept fictional examples and never require forced forgiveness, clinical disclosure or real-world contact.

`advanceProgram` never advances because midnight passed: it advances only on an explicit `complete` or `skip`. `pause` preserves next day; `resume` continues; `restart` creates a fresh in-memory progress state but prior journal/event history must be retained separately. To make a shorter session count, user acknowledges a short attempt, not a meaningful psychic change. Program progress includes completed/skipped day IDs; if idle for several weeks, the queue is still available without catch-up.

## 7. Private event contracts and module projections

See `schema/PCI_EVENT_v2.schema.json` and `data/PCI_MODULE_EVENT_MAP.json` for the exact 17 event types and the 10 consumer modules. Important examples:

| Event | Primary consumers | What it proves |
|---|---|---|
| `belief.created`, `belief.revised` | Belief Reconstruction, Self-Image Lab, Archive | User saved a statement, not whether it was true |
| `activity.completed` | Command Center, Academy, Self-Image Lab, Mental Conditioning, Archive | User explicitly ended one activity session |
| `rehearsal.completed` | Theater of the Mind, Command Center, Archive | One voluntary rehearsal attempt |
| `scenario.completed` | Real-Life Simulator, Command Center, Archive | A hypothetical scenario was explored |
| `exercise.reviewed`, `review.undone` | Academy, Vault, Command Center | The user-rated review and any undone state |
| `experiment.outcome_recorded` | Feedback Lab, Belief Studio, Archive | A user-recorded observation, not a cause |
| `program.day_completed` | Command Center, Academy, Archive | User acknowledged a day, not proven transformation |
| `journal.saved` | Personal Evolution Archive | One private entry was saved |

Events have `event_id`, **unique idempotency_key**, exact `target_id`, `session_id`, ISO timestamp, IANA time zone, version and private payload. Stage 06 uses event v1 as a *proposal*; Stage 07 v2 is the next additive runtime envelope. The UI must explicitly adapt Stage 06 v1 event fields into this v2 event format rather than silently substituting. `aggregateMetrics` deduplicates by idempotency key and content+session to prevent duplicate increments. With no events, show an honest empty state. Avoid materializing a stale counter as the source of truth; compute views from the event log and applicable undone events. Source links remain immutable references to earlier IDs.

## 8. Private record store, export/import, deletion

`schema/PCI_PRIVATE_RECORD_v2.schema.json` defines UUID-style local record IDs, offset-bearing ISO timestamps, `owner=user`, `privacy_mode=device_local`, `refs` to immutable content, and a `sensitive` flag requiring a `consent_id`. Private data types include goals, beliefs/revisions, evidence, reflections, rehearsal sessions, activities, review ratings, practices, scenario progress, experiments, predictions, outcomes, bookmarks, profile settings, backup metadata, program progress and event log.

Versioned export uses format `PCI_PRIVATE_EXPORT`, version 2, and does not automatically upload or encrypt the user-owned JSON. `buildPrivateBackup` **excludes sensitive records by default**. Full exports require a deliberate UI action, a warning and appropriate consent. Optional SHA-256 identifies accidental modifications, **not encryption or authenticity**. `dryRunImport` validates data/version and duplicate IDs before writing. `importBackupAtomic` checks optional checksums, and if sensitive records exist, checks corresponding granted consent entries in the local DB or inside the explicitly approved import, then writes in one transaction. Unknown future formats are rejected without mutation. Account synchronization and conflict resolution across devices do **not** exist.

Stage 05's proposed **v1 backup envelope** is preserved for **import only**: its six stores remain supported. `migrateV1Backup` wraps old user records with deterministic namespaced UUID-style IDs and retains the original legacy ID in metadata rather than silently discarding it; consent is required before this step. The six legacy IndexedDB stores also remain untouched on v1→v2 database upgrades. This is migration readiness, **not a real-browser migration test**. In Stage 08, test transactions and recovery on iPhone Safari, including private browsing, quota errors, versionchange blocked by another tab, duplicate event submission, browser refresh and interrupted imports.

## 9. What Stage 08 should implement

Build the actual responsive Vite/TypeScript application shell and **consume these exact contracts**. Load read-only Stage 05/06/07 JSON separately from private IndexedDB. Implement a single storage service, a common event emitter, an initial onboarding and Command Center experience, activity/scenario/rehearsal renderers using existing schemas, and export/import dialogs with consent. Provide browser-level tests for data round-trip, blocked upgrades, rollback, persistence across refresh and mobile accessibility. Never bundle fixture profiles, book PDF, private exports or long quotations into public assets.

## 10. Test commands and scope

From this ZIP's extracted root, alongside the separately extracted `canonical` and `activity` dependencies:

```sh
tsc -p tsconfig.json
node tests/test_algorithms.cjs
node tests/test_backup_async.cjs
python tests/validate_stage07.py --root . --canonical-dir ../canonical --activity-dir ../activity --out audits/recheck.json
```

These tests run **Node-level pure functions and JSON Schema validation**, not IndexedDB transactions, browser navigation or real psychological outcomes. Test logs and fixtures are bundled. Additional permissions/consent and mobile interaction tests belong to Stage 08.
