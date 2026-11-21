# PCI Stage11 compatibility and migration notes

- `pci-private-v1` remains version **2** with the same 25 object stores. No IndexedDB schema upgrade required. The `rehearsals` and `rehearsal_sessions` stores were present in Stage07 and Stage10.
- New private scene payload v1 is a user-owned `PrivateRecord.data`; new session v1 stores `player`, optional user reflection ratings, template/version/scene ID references and actual elapsed milliseconds. New app code must check fields defensively for old records.
- Events `rehearsal.started`, `rehearsal.stopped` are additional names in v2.1.0; existing `rehearsal.completed` kept intact. Consumers ignoring unfamiliar event types remain compatible. No aggregate counter is incremented directly from rendered UI state.
- Public Stage06 `PCI-RH-*` IDs, concept links, source page fields and 70 original author-practice IDs are unchanged. The practice-attribution projection does not rewrite canonical records.
- Stage09/10 asset-check scripts previously assumed registry counts exactly equal to their final stage count; their checks were updated to confirm original IDs and allow append-only new issue IDs. No original content record changed.
- No user-provided personal profile, synthetic fixture, full copyrighted book PDF, or sensitive data was placed in `public/`.
