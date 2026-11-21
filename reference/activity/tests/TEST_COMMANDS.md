# Executed commands and classifications

```bash
# From extracted canonical Stage 05 directory
python tests/validate_canonical.py --root .
# From the Stage 06 package root, with canonical sibling dir
python tests/validate_stage06.py --root . --canonical-dir ../canonical --out audits/PCI_STAGE06_QA.json
python tests/test_negative_cases.py
tsc --noEmit --pretty false --strict --target ES2020 --module ESNext types/PCI_ACTIVITY_ENGINE_TYPES.ts
python tests/run_content.py --root . --mode activity --id PCI-ACT-CH03-002
python tests/run_content.py --root . --mode scenario --id PCI-SC-CH10-001 --choices 0,1
```

- Schema and graph results are structural/functional checks, **not proof of psychology or scientific effectiveness**.
- TypeScript compilation is not browser/IndexedDB testing.
- ZIP checksum validation is packaging integrity, not source content corroboration.
