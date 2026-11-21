# PCI | Stage 05 Knowledge Integrity Report

**Project:** PSYCHO-CYBERNETICS-INTELLIGENCE  
**Date:** 2026-11-20  
**Schema:** `1.0.0` unchanged | **Research data:** `1.3.0` | **Canonical pack:** `1.0.0`  
**Primary source:** 332-page supplied 2002 Prentice Hall Press trade-paperback revision; SHA-256 `4dd7a311a21af58aa075176abb48fd60b348c70bb314a2ca09f66383922e7e9b`.

## Source restoration and baseline

Opened the actual supplied source PDF, Foundation ZIP, Parts 01–04 ZIPs, Stage 04 coverage JSON and Stage 04 handoff. The five source/archive SHA-256 values are in `PCI_ORIGINAL_ARCHIVE_FINGERPRINTS.json`. The Stage 04 iPhone ZIP was opened and its Markdown handoff matched the embedded Stage 04 handoff. Found no source-fingerprint mismatch.

| Original validator | Command/script | Result |
|---|---|---|
| Stage 01 | `foundation/validate_pci.py` | PASS 11/11 |
| Stage 02 | `p2/validate_stage02.py` | PASS 39/39 |
| Stage 03 | `p3/validate_stage03.py` | PASS 44/44 |
| Stage 04 | `p4/validate_stage04.py` | PASS 26/26 |

Baseline commands, inputs, reports, and logs are retained under `audits/baseline/`, with the original scripts in the source ZIPs. The canonical merge preserved every inherited JSON record **by content value** and all **1,668** existing IDs. It added **8** issue records (`PCI-ISS-048` to `PCI-ISS-055`) without reassigning or deleting anything. New ID count **1,676**.

## Actual merged collections

| Record type | Count |
|---|---:|
| Book | 1 |
| Chapters | 16 |
| Sections | 270 |
| Coverage records | 16 |
| Concept dossiers | 201 |
| Book claims | 201 |
| Anecdotes | 115 |
| Book practices | 70 |
| Educational activities | 32 |
| Applications | 201 |
| Mechanisms | 32 |
| Evidence assessments | 42 |
| Citations | 315 |
| Knowledge relationships | 109 |
| Open issues (including 8 new) | 55 |
| **All registered records** | **1,676** |

`data/PCI_*` files keep original rich record objects, not truncated search snippets. `PCI_RECORD_PROVENANCE.json` links every ID to its original ZIP member, archive fingerprint and original record checksum. Section metadata has **three inherited representations**; `indexes/PCI_SECTIONS_APP_VIEW.json` is a derived common projection. Original nested section structures in `data/PCI_CHAPTERS.json` remain unchanged.

## Duplicates, redirects, and graph

- **0** unexplained duplicate permanent IDs and **0** confirmed semantic merges; all 201 concepts remain. `audits/PCI_DUPLICATE_REVIEW.json` documents **13** plausible cross-chapter overlaps and their explicit classification `overlapping_but_distinct`, with rationale and both source anchors. This is **not** an exhaustive semantic-identity guarantee.
- `PCI_ID_REDIRECTS.json` intentionally contains no redirects or tombstones. A later verified true merge must preserve the superseded ID as an addressable redirect.
- **109** previously established graph edges are retained; **90** are cross-chapter. All have resolvable endpoints and recorded source anchors. No decorative graph edges were manufactured.
- Potentially conflicting ideas, such as the value of corrective feedback versus harms of excessive self-monitoring, are retained as scoped explanations, not forcibly blended. The graph is an interpretive map, not experimental neuroscience.

## App-ready content and navigation

- `indexes/PCI_SEARCH_DOCUMENTS.json`: **1,604** lightweight records linking to detailed documents.
- `indexes/PCI_SEARCH_INVERTED.json`: **4,214** indexed search terms, fully local and deterministic; TypeScript helper in `types/PCI_LOCAL_SEARCH.ts`.
- Topic collections and canonical IDs in `indexes/PCI_THEME_INDEX.json`; lexical tags are *navigation suggestions* rather than source-grounded causal relationships.
- Concept-to-practice, practice-to-claim, concept-to-application, chapter-to-exercise and citation-to-record lookup files contain checked IDs. Page-proximity or topical suggested links are explicitly labeled as editorial navigation heuristics; they are not attributed to the author.
- Stage 03 scenario and quiz candidates are preserved under `learning/` and **not silently registered** as permanent scenario/quiz IDs. Stage 06 must decide their canonical status and issue IDs with migration notes.
- TypeScript interfaces and JSON Schema `1.0.0` included. Stage 06 should use these structures directly for local-first, static-hostable learning tools, with personal responses stored separately in IndexedDB.

## Full-book coverage interpretation

All 16 chapter boundaries are indexed and all 16 contain substantive research dossiers. The supplied `PCI_FULL_BOOK_INGESTION_COVERAGE.json` reports no unread assigned pages, but prior subchapter records have differing precision, and Chapters 5–12 contain `NOT_REVIEWED_CANDIDATES` section-review labels despite substantive concept dossiers. Stage 05 **does not certify** exhaustive paragraph-by-paragraph semantic completeness (count certified: **0**). Front matter (PDF pages 1–10) and back matter (317–332) remain excluded from chapter coverage.

Stage 05 directly spot-checked one representative **PDF page in each of 16 chapters**, recorded separately in `audits/PCI_PRIMARY_PDF_SPOT_CHECKS.json`. Passages were actually read and two pages (45 and 291) additionally visually rendered. This confirms selected wording and page geometry, **not every paraphrase**. OCR has a line-broken word on page 45, so keyword checking was corrected to use an intact page token rather than incorrectly marking the source absent.

## Research and evidence integrity

- `verified_in_pdf` means the book contains a claim, not that it is true. Structural source references, PDF offsets, and JSON validation do not prove efficacy.
- The book's automatic success/failure mechanism remains a historical cybernetics model/metaphor, not an independently isolated brain subsystem.
- The book's hypnosis, vivid imagery, healing, aging, and extraordinary perception assertions vary greatly in strength and scientific support. Direct PDF pages do not establish causal effects or universal success.
- Four inherited bibliographic sources were revisited. The NIH NCCIH hypnosis factsheet was read directly; the sports imagery and ESP papers were bibliographically matched but not given a comprehensive critical appraisal. See `audits/PCI_EXTERNAL_SOURCE_VERIFICATION.json` and `PCI_EVIDENCE_LIMITATIONS.md`.
- Anecdotes, case studies, Chapter 16 testimonials, and purported cures are not randomized trials. No claims of certain recovery, trauma cure, guaranteed success, or a universal 21-day program should be added to the app.
- Source author/editor attribution is composite unless directly marked. The 70-entry full-book practice index retains durations and `exercise_origin` uncertainty; no universal cadence is manufactured.

## Independent QA and remaining defects

`audits/PCI_STAGE05_QA.json`: **25/25 PASS** across schema validity, unique IDs, provenance, graph integrity, search/index targets, chapter coverage, privacy and direct PDF spot checks. TypeScript `tsc --noEmit` PASS separately in `audits/PCI_TYPESCRIPT_TEST.json`. The eventual ZIP was separately extracted, its inventory compared, and the bundled validator rerun (see standalone `PCI_STAGE05_ARCHIVE_QA.json`). These are automated data/compilation checks, **not browser UX, IndexedDB persistence, or psychological-efficacy tests**.

**Open issues:** 55 inherited/new items, of which 8 are Stage 05 additions. Highest-risk follow-ups: source-meaning spot checks, Chapter 15 medical and longevity extrapolations, Chapter 16 recovery testimonials, paranormal inferences, and exercise attribution/privacy. The Stage 06 activity engine may proceed with honest source-status labels, but it must not present clinically risky claims as advice.

## Safety and redistribution

The static research pack excludes the original copyrighted PDF and any personal journals, profiles, or entries. Public research is largely independent paraphrase with short page citations. No private user data belongs in GitHub Pages assets. A static host has no account sync or live AI by default.
