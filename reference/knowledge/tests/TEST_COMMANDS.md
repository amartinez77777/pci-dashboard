# PCI Stage 05 tests (executed 2026-11-20)

Original validators (paths refer to extracted private input directory):

```
python input/foundation/validate_pci.py --foundation input/foundation --research input/p1 --out baselines/stage01.json
python input/p2/validate_stage02.py --foundation input/foundation --part1 input/p1 --part2 input/p2 --pdf '<original private book PDF>' --out baselines/stage02.json
python input/p3/validate_stage03.py --foundation input/foundation --part1 input/p1 --part2 input/p2 --part3 input/p3 --pdf '<original private book PDF>' --out baselines/stage03.json
python input/p4/validate_stage04.py --foundation input/foundation --part1 input/p1 --part2 input/p2 --part3 input/p3 --part4 input/p4 --pdf '<original private book PDF>' --out baselines/stage04.json
```

Rebuild from extracted packs and original private PDF (not distributed):

```
python tools/rebuild_stage05_from_extracted_packs.py --input <extracted-input-folder> --out <canonical-output-folder> --pdf '<original private book PDF>' --archive-dir <directory-containing-original-5-zips>
```

Canonical data QA (without PDF: checks all structural tests; with PDF: 16 direct-page spot tests):

```
python tests/validate_canonical.py --root . --pdf '<original private book PDF>' --out audits/PCI_STAGE05_QA.json
```

TypeScript compile test:

```
tsc --noEmit --target es2020 --lib es2020,dom --module es2020 types/PCI_KNOWLEDGE_TYPES.ts types/PCI_LOCAL_SEARCH.ts
```

Requires Python 3.10+, `jsonschema`, and optionally PyMuPDF (`fitz`) when checking private PDF; build inputs include original ZIPs. No network, backend or application browser is required by these validators.

Baseline, canonical, TypeScript and extracted-ZIP QA results are recorded separately. These tests do not test personal IndexedDB writes or browser interactions.
