# PCI Stage 11 · Theater of the Mind

This is the **entire Stage 10-derived React/Vite source project**, now with the Theater of the Mind. All 10 routes, canonical research and private-store names remain intact. Stage11 adds guided session timing, user-created scene templates, optional read-aloud, privacy-aware persistence and session history. Read `PCI_STAGE_11_HANDOFF.md` and `PCI_STAGE11_TEST_REPORT.md` before extending.

## Standard React18 / Vite (requires dependencies not available in this execution environment)

```sh
npm install
npm run typecheck
npm run build
npm run dev
```

Only generate `package-lock.json` after an actual `npm install`. No lockfile was forged here.

## Offline compatibility test suite (NOT React18 production)

```sh
npm run build:offline
node --test tests/data_repo.test.mjs tests/vault_unit.test.mjs tests/labs_model_repo.test.mjs tests/theater_model_repo.test.mjs
python tests/validate_stage11.py
python tests/browser_stage11_smoke.py
```

The source app uses a separate `dist-static/` React16 compatibility build for in-memory Chromium checks. The browser harness uses synthetic IndexedDB: it cannot prove durable storage on Safari. Serve the real production build on a secure origin and test native persistence before release. The user-provided full PDF and any user journal are not bundled into `public/`.
