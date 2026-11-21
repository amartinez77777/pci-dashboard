# PCI Knowledge Canonical v1.0.0

This ZIP is a full consolidated, source-attributed PCI research database for the 2002 revised *The New Psycho-Cybernetics*, not an executable user dashboard.

**Read in order:** `PCI_PROJECT_MANIFEST.json`, `PCI_KNOWLEDGE_INTEGRITY_REPORT.md`, `PCI_EVIDENCE_LIMITATIONS.md`, `PCI_STAGE_05_HANDOFF.md`.

**App entry points:** `data/PCI_CONCEPTS.json` (full dossiers), `data/PCI_CLAIMS.json`, `data/PCI_AUTHOR_PRACTICES.json`, `data/PCI_EDUCATIONAL_EXERCISES.json`, `data/PCI_RELATIONSHIPS.json`; search in `indexes/PCI_SEARCH_DOCUMENTS.json` and `PCI_SEARCH_INVERTED.json`; types in `types/PCI_KNOWLEDGE_TYPES.ts`.

**Local-first contract:** users' personal reflections must be stored outside the static research bundle in IndexedDB. GitHub Pages does not add a backend, login or live AI. The book PDF is deliberately excluded and should never be hosted as a public asset.

**Audit:** Run `python tests/validate_canonical.py --root .` (requires jsonschema). Optional PDF page tests require your original private PDF and PyMuPDF. The included test reports record what ran, and what was not tested. Data exists in final JSON files, not only chat transcript.
