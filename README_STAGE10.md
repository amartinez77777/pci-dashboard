# PCI Stage 10 · Self-Image & Belief Reconstruction

This is the **full Stage09 PCI React/Vite application with Stage10 additive features**, not a standalone demo. The 10 original routes and the advanced source-linked Knowledge Vault remain present. The source PDF is intentionally excluded from public build assets.

## Run with dependencies (when available)

```sh
npm install
npm run typecheck
npm run build
npm run dev
```

**The current environment could not fetch Vite from npm and does not have a valid lockfile**. `npm run build` was attempted and stops at `vite: not found` (exit 127). Do not confuse the following offline preview with a production React 18/Vite release:

```sh
npm run build:offline
python tests/browser_stage10_smoke.py
```

The offline builder uses a React 16 hooks compatibility harness for checking rendering and event handling only. Native IndexedDB is denied in the in-memory Chromium origin. The UI test injects a clearly labeled synthetic IndexedDB facade. Node model/repository tests use that same synthetic facade; neither proves HTTPS/real-device persistence.

## New source files

- `src/personal-labs.tsx`: fully integrated guided self-image inventory, private reflection editor, belief studio, revision compare, outcome follow-up, safety and provenance links.
- `src/personal-labs-model.ts`: deterministic data validation, domain-to-real-concept links, revisions comparisons, nonclinical interpretation constraints.
- `src/personal-labs-repo.ts`: version-2 IndexedDB repository with atomic writes, consent, conflict protection, history, local events and cascade delete.
- `schema/PCI_STAGE10_BELIEF_DATA.schema.json` and `schema/PCI_STAGE10_EVENT_EXTENSION.json`: additional app data contract; Stage07 schemas are preserved.
- `public/styles.css`: dark premium lab design added without rewriting Stage09 knowledge styles.
- `tests/labs_model_repo.test.mjs`, `tests/browser_stage10_smoke.py`, `tests/validate_stage10.py`: executable contract, in-memory UI and preservation tests.

See `PCI_STAGE10_MIGRATION_NOTES.md`, `PCI_STAGE10_TEST_REPORT.md`, and `PCI_STAGE_10_HANDOFF.md` for exact status and Stage11 interfaces.
