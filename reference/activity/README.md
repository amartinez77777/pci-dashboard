# PCI Stage 06 — Executable learning content data

This is **not** a UI or deployed application. The JSON files are declarative execution specs for a generic Step, Scenario and Rehearsal renderer in Stage 7–13. Existing canonical research identifiers, record contents, and schema remain unchanged; the canonical ZIP must still be attached to Stage 07.

## Folders
- `data/`: 32 executable PCI-adaptation activities, 16 multi-step decision scenarios, 12 mental rehearsals, 5 feedback patterns, 3 rubrics, 2 feedback cycles, and a read-only origin/timing lookup for all 70 original author practices.
- `schema/`: 6 Draft 2020-12 JSON Schemas and runtime contract.
- `types/`: TypeScript public content/event interfaces.
- `indexes/`: chapter, concept, and original-practice links.
- `tests/`: runnable Python validator and deterministic state engine; test fixtures, failure cases, and reports.
- `audits/`: coverage, quality, source audit and actual executed test output.

## Architecture rules
1. Treat everything in activity/scenario/rehearsal JSON as an original PCI learning adaptation. Only the separate read-only book-practice lookup preserves author instructions and printed timing; this pack never changes 21-day or 30-day prescriptions.
2. `source_status=verified_in_pdf` means that a book claim appears in the source, not that it is scientifically validated. All scenario consequences are hypothetical.
3. Never attempt to infer personality, clinical diagnosis, or comprehension from text keywords. Choice feedback is deterministic and disclosed. Rubric totals measure self-recorded artifact completeness, not mental traits.
4. For any emotional topic, allow skip/stop, fictional input and non-contact alternatives. No required forgiveness, trauma exploration or medical claims.
5. Future user entries are local private state, not bundled public research content. Do not publish a user export to GitHub Pages.
6. Verify with `python tests/validate_stage06.py --root . --canonical-dir ../canonical`. This pack intentionally does not contain the book PDF or original canonical archive.
