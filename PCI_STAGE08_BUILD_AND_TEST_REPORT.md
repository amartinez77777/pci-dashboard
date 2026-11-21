# PCI — Stage 08 Build and Test Report

Date: 2026-11-20 · Application source version: 0.8.0 · Source package: `PCI_APP_STAGE08_FULL.zip`

## Actual prerequisites opened

- `PCI_KNOWLEDGE_CANONICAL_v1(3).zip` — complete canonical knowledge source, research schemas, ID registry and original validators.
- `PCI_ACTIVITY_ENGINE_DATA_v1(2).zip` — executable activities, 16 branching scenarios, 12 rehearsals, schemas and validators.
- `PCI_PERSONALIZATION_ENGINE_v1(1).zip` — 21-day curriculum, Stage 07 private v2 data contracts, algorithms and testing artifacts.
- `PCI_STAGE_07_HANDOFF_iPhone(1).zip` — original Stage 07 handoff in readable MD/TXT.
- `PCI_EXPERIENCE_INTEGRATION_GUIDE_iPhone(1).zip` — original integration guide in MD/TXT.

No book PDF was attached in this stage. The previously verified PDF source fingerprint is inherited from Stage 05. No new direct PDF reading is claimed.

## Executed validations and commands

| Test / command | Result | Actual scope |
|---|---|---|
| `python tests/validate_canonical.py --root .` (extracted Stage 05 pack) | **PASS 23/23** | Inherited record/schema/source-reference checks |
| `python tests/validate_stage06.py --root . --canonical-dir ../knowledge` | **PASS 42/42** | Inherited activity and graph checks |
| `python tests/validate_stage07.py --root . --canonical-dir ../knowledge --activity-dir ../activity` | **PASS 41/41** | Inherited curriculum and data contracts |
| `node tests/test_algorithms.cjs` and `node tests/test_backup_async.cjs` (Stage 07 pack) | **PASS**; backup 9/9 | Pure logic and synthetic backup fixtures |
| `tsc -p tsconfig.json` | **PASS** | Strict TS compile of application source, not Vite bundling |
| `npm run lint` | **PASS** | Lightweight local safety lint + TypeScript; not ESLint |
| `npm run build:offline` | **PASS** | Offline ESM static compilation using legacy React compatibility harness; not Vite |
| `npm run test:repo` | **PASS 14/14** | Node actual segmented JSON lookup and backup-schema guards |
| `python tests/validate_assets.py` | **PASS 34/34** | Canonical preservation, segmentation, privacy boundary and source integrity |
| `python tests/browser_smoke.py` | **PASS 35/35** | Actual Chromium DOM tests with in-memory assets, React16 hook shim and intercepted JSON |
| `npm view vite version` | **BLOCKED** | npm registry `getaddrinfo EAI_AGAIN` DNS / network restriction |
| `npm run build` | **BLOCKED** | Strict TS ran, then `vite: not found` because npm dependencies unavailable |
| Chromium `page.goto(http://127.0.0.1:8788/)` and `page.goto(file:///...)` | **BLOCKED** | Both blocked by managed Chromium policy `ERR_BLOCKED_BY_ADMINISTRATOR` |
| Real-origin IndexedDB transactions / imported backup in browser | **NOT_TESTED** | An about:blank in-memory page is an opaque origin and denies IndexedDB access |
| React18 + Vite bundled browser runtime | **NOT_TESTED** | Only source typecheck and separate compatibility-harness browser smoke possible |
| iPhone Safari / VoiceOver | **NOT_TESTED** | Device not available |

**Do not conflate** runtime rendering in the offline compatibility harness with production React18 build success or real IndexedDB persistence. No valid npm `package-lock.json` was fabricated.

## Browser viewport and navigation checks

In Chromium in-memory mode, 10 hash routes rendered independently and returned navigable content. `#/knowledge` loaded 201 index entries through a file-backed fetch mock and opened full, cited concept dossiers. `#/academy` displayed 21 authored days. An invalid route presented a recovery button. At 1440, 390, and 320 CSS pixel widths, measured `document.documentElement.scrollWidth <= innerWidth` in tested states. Mobile drawer opening and route changes worked at 390 and 320 CSS pixels. These are **in-memory** rather than production-hosted browser checks.

Screenshots and named checks are in `audit/`. Contrast calculations, keyboard-only complete flows and assistive-technology narration were not evaluated.

## Real implementation, not demos

- 10 genuine module route names retained. Future lab stages are labeled rather than claimed built.
- Command Center live research counts: 16 chapters, 201 concepts, 32 executable activities; personal entries count comes from IndexedDB when available.
- Knowledge Vault: typed data repository with chapter-chunked concept JSON, title/index search, complete concept detail, source status and PDF/printed page locators.
- Archive: create and delete local journal entries, explicit sensitive-information opt-in, empty state and unavailable-storage handling.
- Settings: v2 private JSON export/import baseline and data controls; imported UUID collisions are skipped, not silently overwritten.
- Real canonical research, activity and personalization files preserved in `reference/` without renumbering or paraphrasing them again.
- `public/` does not include the PDF or any production private data fixtures.

## Outstanding limitations

1. Vite production build, a real lockfile and verification on React18 with actual installed dependencies are **BLOCKED**, not PASS.
2. Browser IndexedDB write/read/update/delete, persistence after reload, migration and backup flows are **NOT_TESTED** on a real origin.
3. Offline compatibility harness uses React16 solely for smoke testing because no modern runtime could be installed; it is deliberately not included in `public/` or the Vite production entry point.
4. The ten routes are all accessible but Stage 09–14 lab-specific interactive tools are not falsely presented as complete. Archive/save is only a basic baseline.
5. The current compact React JSX compatibility type definitions are weaker than the official modern React typings and should be upgraded after dependencies install.

This report is a reproducible checkpoint, not a claim of released production-grade browser compatibility.
