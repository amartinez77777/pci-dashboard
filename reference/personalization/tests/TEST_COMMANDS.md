# Stage 07 executed test commands

1. Stage 05 baseline: `cd ../canonical && python tests/validate_canonical.py --root . --out ../canonical_baseline.json` → **PASS 23/23**.
2. Stage 06 baseline: `cd ../activity && python tests/validate_stage06.py --root . --canonical-dir ../canonical --out ../activity_baseline.json` → **PASS 42/42**.
3. TypeScript: `tsc -p tsconfig.json` → **PASS** (this compiled pure algorithms and DOM declarations; not a browser run).
4. Algorithms: `node tests/test_algorithms.cjs` → executed, log `audits/PCI_ALGORITHM_TESTS.log`.
5. Backup: `node tests/test_backup_async.cjs` → executed, log `audits/PCI_BACKUP_TESTS.log`.
6. JSON Schema/foreign keys: `python tests/validate_stage07.py --root . --canonical-dir ../canonical --activity-dir ../activity --out audits/PCI_STAGE07_SCHEMA_QA.json` → executed.
7. Independent extracted ZIP revalidation → `audits/PCI_STAGE07_ARCHIVE_QA.json`, after packaging.

**NOT TESTED:** genuine browser IndexedDB transactions, iPhone Safari, background recovery, optional encryption, empirical efficacy, or actual identity change. This file is an audit of commands that ran, not a promise of comprehensive runtime correctness.
