# PCI Stage 10 — compatibility and private-data migration notes

## Scope

- This repository is the **Stage 09 source with additive Stage 10 changes**, not a rebuilt application.
- All **1,773** IDs, app routes, original chapter/concept/search/graph assets, Stage 07 storage structures and 25 store names remain intact. **Five new quality issue IDs** are registered in `PCI_ID_REGISTRY.json`: `PCI-ISS-ST10-001..005`. No book claim, practice or source ID was changed.
- IndexedDB remains **`pci-private-v1` version 2**, with `PrivateRecord.schema_version = "2.0.0"`. No database migration is required.

## New records in existing stores

- `beliefs`: current user belief data plus `status` (`active`/`draft`), own optional `conviction`, and revision number. Text is kept only in local `PrivateRecord.data`.
- `belief_revisions`: immutable copies of `before`, `after`, the unchanged belief ID, revision number and date. First snapshot has `before:null`.
- `evidence_entries`: source-separated user-observed supporting/counterexamples, linked to the belief and revision ID. User assertions are not independent scientific evidence.
- `experiments`: optional safe actions, dates and user predictions. `observed_outcomes`: the user's own observation, never a confirmed psychological effect.
- `identity_notes`, `reflection_notes`: user-entered self-image notes with dated `history` snapshots. These are private and optional, and can be deleted.
- `consents`: explicit local consent metadata when any user record is marked sensitive. Sensitive record revisions must **remain sensitive** while prior snapshots exist.
- `events`: `belief.created`, `belief.revised`, `journal.saved`, and `experiment.outcome_recorded` use existing Stage 07 v2 names. New optional `experiment.planned` is an **additive event extension** with embedded `schema_version=2.1.0`, while the enclosing private record remains `2.0.0`. Older Stage 07 consumers should ignore unknown event types instead of rejecting all events. See `schema/PCI_STAGE10_EVENT_EXTENSION.json`.

## Transaction, revision and deletion behavior

- Create and revise operations commit the belief, revision, evidence, experiment plan, consent and non-sensitive event metadata **in one IndexedDB read-write transaction**.
- Revisions check the expected `updated_at` in the transaction. A stale edit aborts to prevent silent replacement.
- Deleting a belief removes its revision/evidence/experiment/outcome/event records together, preserving independent reflections but unlinking their deleted belief ID. A deletion confirmation is required.
- Editing an inventory or reflection preserves the previous content in dated `history`, rather than silently overwriting it.
- Manual **Save draft** persists partial worksheets. No background draft autosave is enabled in Stage 10; introducing automatic storage without explicit user consent was intentionally avoided.
- Export/import remain the existing Stage 07 PCI v2 envelope. **Default export excludes records marked sensitive**. Users must explicitly opt into an unencrypted full export in Settings and store the resulting file safely. No cloud recovery is provided.

## Research and route behavior

- `#/self-image` displays the voluntary Self-Image Intelligence Laboratory.
- `#/beliefs` and `#/beliefs/<UUID>` display the Belief Reconstruction Studio.
- Each domain recommendation uses explicit, verified-existing source IDs (`src/personal-labs-model.ts`) and transparent selected-domain logic; no hidden psychological profiling.
- Deep links to `#/knowledge/concept/<ID>` preserve the Stage 09 source panels; `#/theater`, `#/feedback`, and `#/archive` remain intentionally future-stage modules as described in the interface.
- No personal data is written to public JSON, assets, or source research. The training fixtures in `tests/` are synthetic, never default application state.

## Future release requirements

Real React 18/Vite production build, native IndexedDB reload tests, iOS Safari, screen reader QA, secure-origin backup restore, and Stage 07 event consumer handling are **not yet verified**. See `PCI_ISSUES.json` for precise follow-up tickets.
