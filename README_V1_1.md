# PCI v1.1 — Enhanced source candidate

This is the cumulative `PSYCHO-CYBERNETICS-INTELLIGENCE` React/TypeScript source, extending the original 10 modules rather than replacing them. **Not production certified.** The authoritative fixed data comprises 201 source-linked concepts, 16 chapters, 109 provisional relationships, 70 indexed original practices, 12 PCI-designed rehearsal templates, 16 scenarios, and 21 authored Academy days. The book PDF and private user journal records are **not** included.

### New in v1.1
- Explainable, deterministic local recommendations using only user-created, on-device records; no AI API or invented psychological scoring.
- A more useful Command Center showing actual learning history, pending feedback, voluntary goals, next steps, and private links.
- Goal/belief→Theater→Feedback→Archive and Academy→Knowledge Vault→Conditioning→review/Archive routes based on explicitly saved IDs or authored source links, not inferred psychology.
- Small-screen Command Center refinement, touch-friendly controls, sensitive-title masking and optional suggestion visibility.

### Run source and tests
Requires Node 22+ and access to npm. `npm install --no-audit --no-fund` (generates a genuine lockfile only after successful resolution), `npm run typecheck`, `npm run lint`, `npm run build:offline`, `node --test tests/*.test.mjs`, `python tests/validate_v11.py`, `python scripts/audit_final_research.py`, then **`npm run build`**. Serve only Vite's actual `dist/` on HTTPS. The `dist-static/` compatibility output is a synthetic-test harness, **not the production application**. The preserved GitHub Actions workflow performs these gates for GitHub Pages when dependencies are available.

`npm install` in this environment failed with `EAI_AGAIN` for `registry.npmjs.org/react`, so the official production build remains unverified here. No fake `package-lock.json` was created.

### Data safety
User records stay in existing IndexedDB database `pci-private-v1` v2 (25 stores), separate from `public/data`. Export/import uses versioned JSON; downloaded backups are **unencrypted** unless you encrypt them separately. There is no account or cloud sync. No personal fixtures are included in deployed research assets. Sensitive entries are hidden from ordinary Command Center previews and redacted by default in export.

### Research honesty
The automatic-success mechanism is the book's metaphor, not a scientifically verified discrete brain organ. No exercises are presented as clinical interventions. Source refs and source/evidence status were inherited, **not independently checked against PDF images in this stage**. New links to conditioning exercises are labeled PCI adaptations.

Read `V1_1_HANDOFF.txt` and `V1_1_TEST_MATRIX.json` for exact tests, unresolved gates and GitHub deployment instructions.
