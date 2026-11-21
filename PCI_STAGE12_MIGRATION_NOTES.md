# Stage 12 compatibility and storage

- **IndexedDB**: `pci-private-v1`, `DB_VERSION=2`, **25 stores unchanged**. No destructive upgrade. Existing Stage 08–11 user records retain their original UUIDs and contents.
- **New additive data contracts**: goal/experiment/prediction/observation use `feedback_contract_version=1.0.0`; scenario_progress uses `scenario_contract_version=1.0.0`. Existing goal/experiment data are not rewritten; Stage12 UI scopes its workflow to new contract records while preserving and retaining legacy records for Stage14 consolidation.
- **Idempotent events**: `events` store reuses the inherited envelope `schema_version=2.0.0`; event keys are deduplicated within one write transaction; user prose never copied into event payload.
- **Theater**: stable template and scene IDs unchanged. Player re-reads private scenes from `rehearsals` by scene UUID. Phase guidance is generated at runtime from existing immutable template fields. Source practice attribution stays separate from PCI adaptations.
- **Deferred**: `PCI-UX-003` automatic timing vs manual metadata and `PCI-DATA-004` hash-navigation unsaved changes are REQUIRED Stage14 release gates.
- **Backups**: export/import remains the Stage07 version 2 private record envelope. Records in new workflows appear in existing stores and are compatible with existing export/import.
- **Privacy**: No private fixture data are published. Synthetic test data exist only under `tests/`. Stored private records are local, unencrypted, and user-controlled.
