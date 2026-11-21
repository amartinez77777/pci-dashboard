# PCI | Stage 06 Activity Design Audit

**Stage:** 06/16 | **Date:** 2026-11-20 | **New execution-content schema:** `1.0.0` | **Inherited knowledge schema:** `1.0.0` (unchanged)  
**Primary source:** user-supplied 332-page revised trade-paperback PDF, SHA-256 `4dd7a311a21af58aa075176abb48fd60b348c70bb314a2ca09f66383922e7e9b`.  
**Canonical knowledge ZIP opened:** `PCI_KNOWLEDGE_CANONICAL_v1(1).zip`, SHA-256 `e26e80a5077efd4f39e3cf619e961e15b1acd84664759d02f5f7beebef1f7960`. The supplied iPhone knowledge-integrity and Stage 05 handoff ZIPs were opened and inspected. No source/edition mismatch.

## Actual content shipped

| Collection | Populated records | Distinction |
|---|---:|---|
| Executable educational activities | **32** | 2 per chapter, each distinct from preserved `PCI-EDU-*` records |
| Multi-step branching scenarios | **16** | 1 per chapter, each path has 2 decisions, 4 distinct hypothetical outcomes and safe exit |
| Guided mental-rehearsal templates | **12** | Reusable phases with full/short/no-timer modes and text alternative |
| Feedback patterns | 5 | Rule-based, nonclinical feedback; never semantic AI scoring |
| Self-review rubrics | 3 | 0–8 completion-artifact scores; not efficacy or personality scores |
| Feedback-cycle templates | 2 | Goal, hypothesis, action, observation, revision |
| Source-described book practice bridge | 70 | Read-only mapping to canonical `PCI-AP-*`, unchanged timing and origin |
| Newly registered issue | 1 | `PCI-ISS-056`: inherited subsection semantics need resolution |
| **New permanent registrations** | **71** | Prior 1,676 registrations preserved, total 1747 |

**Activity quality:** 16/32 have action/feedback as their primary emphasis, and the other 16 are observation/reflection activities; all 32 include at least one concrete choice, alternative check and a bounded plan. This means all 32 include observable planning or choice behavior, but it does *not* mean 32 real-world actions were performed. Completion describes recording activity fields only.

## Chapter coverage: 32 activities, 16 scenarios, 12 rehearsals

| Ch. | Named activities | Scenario | Rehearsals |
|---|---|---|---:|
| 1 | Identity statement audit, One identity-consistent action | After the first failed presentation | 0 |
| 2 | Feedback-loop observation, Test one course correction | Learning a new work skill | 0 |
| 3 | Prediction versus observed social evidence, Short imagery plus real rehearsal | Before a difficult introduction | 2 |
| 4 | Find the hidden comparison standard, Safe belief prediction experiment | A limiting benchmark | 1 |
| 5 | Belief audit without self-blame, Low-stakes hypothesis test | A harsh self-belief | 1 |
| 6 | Decision-loop observer, One-task attention trial | Overchecking a prepared task | 1 |
| 7 | Fact and meaning in a hard day, Prosocial action plus mood log | A frustrating commute | 0 |
| 8 | SUCCESS as a nonclinical skill map, Confidence ladder with repair | Constructive courage on a team | 1 |
| 9 | Signal versus identity, Correct course, keep destination | Tension after performance feedback | 1 |
| 10 | Boundaries versus generalized withdrawal, Action not identity | Boundary after an insensitive joke | 1 |
| 11 | Others-mindreading audit, One minute of authentic expression | Speaking in a group | 0 |
| 12 | Notification cue inventory, Transition pause test | Notification during focus work | 1 |
| 13 | Pressure map with realistic stakes, Low-pressure rehearsal and feedback | Performing under deadline pressure | 1 |
| 14 | Success evidence without magical certainty, Small-wins ladder | Using a past success responsibly | 1 |
| 15 | Engagement without longevity claims, Future-oriented connection experiment | Meaningful activity without medical promises | 0 |
| 16 | Testimony evidence audit, Link imagining with action | Interpreting a transformation testimonial | 1 |

The 16 chapter entries are complete **content records**, not proof that every page or subsection in the research source has been exhaustively verified. The inherited 16 chapters contain substantial concept dossiers, but the canonical source manifest retains ambiguous `indexed only` labels for some research batches. Issue `PCI-ISS-056` explicitly holds this conflict for later resolution.

## Scenario and exercise depth assessment

Every executable activity includes the original research exercise's actual task instructions as prompts plus: (a) an optional/fictitious context input; (b) observation versus interpretation; (c) a 3-option conceptual reasoning check with explicit feedback; (d) a bounded next-step plan; (e) a performed/simulated/planned/declined observation state; and (f) a final review. These fields are intentionally **not automatically semantically graded**. No diagnosis, hidden psychological index, or inner-state improvement claim is made. A future UI must clearly label the choice feedback as educational, not authoritative psychological assessment.

Each branching scenario has an opening case, three known facts, initial choice, context-sensitive second decision, four distinct hypothetical consequences, a tradeoff, a debrief question and safe exit. All four decision paths per scenario were traversed, for **64 completed path simulations**. Sensitivity is handled with fictional-only cases and no requirement to disclose personal experiences; the Chapter 10 scenario explicitly does not require forgiveness or reconciliation.

The rehearsal templates are **PCI-original adaptations**, not transcriptions of the revised-edition practice schedules. Each supports 300-second guidance as an optional app design, a 60-second alternative, and no timer. These durations are not represented as author-recommended. A written checklist replaces visualization if preferred; any upcoming skill still requires appropriate external practice and feedback.

## Direct primary-source checks and limitations

Three actual PDF pages were inspected, including their page images: **PDF 34 (printed 24)** describes a month-long exemplar study; **PDF 52 (printed 42)** describes 10–15 minute target imagery for 21 days; **PDF 143 (printed 133)** describes a different 30-day habit experiment. These examples demonstrate why an app-level fixed duration cannot be attributed to the book. Direct checks cover **3/332 PDF pages in this stage**; inherited citations were structurally checked against existing canonical IDs, but all 70 book practices were *not* reverified from scratch.

Scientific efficacy of self-image reconstruction, mental imagery as substitution for physical practice, the purported automatic servo-mechanism and medical/longevity claims was **NOT TESTED** in Stage 06. The learning content uses these as attributed or metaphorical educational constructs. Source statuses of the original canonical records remain unchanged and are preserved rather than promoted to experimental evidence.

## Tests actually run

- Baseline from extracted prior knowledge: `python tests/validate_canonical.py --root .` in canonical directory: **PASS 23/23**, before the new overlay.
- `python tests/validate_stage06.py --root . --canonical-dir ../canonical --out audits/PCI_STAGE06_QA.json`: **PASS {qa_detail}/{qa_detail}**, including source IDs, 16 chapters, schemas, all 64 scenario paths, 32 activity completions, 32 activity skips, timers, privacy, and indexes.
- `python tests/test_negative_cases.py`: **PASS {neg_count}/{neg_count}**, deliberately malformed inputs, missing endpoints, cycles, invalid choices, declined steps.
- `tsc --noEmit --pretty false --strict --target ES2020 --module ESNext types/PCI_ACTIVITY_ENGINE_TYPES.ts`: **PASS**, TypeScript compile only. No React/browser/IndexedDB runtime test claimed.
- ZIP extraction and checksum revalidation results are captured separately in `PCI_STAGE06_ARCHIVE_QA.json` after packaging.

## Material limitations and Stage 07 responsibilities

1. The JSON activity runner and scenario interpreter are reference code that really execute deterministic logic, **not a deployed browser UI**. The next stage must implement durable private IndexedDB storage, resume/cancel, keyboard focus and screen reader semantics, and versioned private export/import.
2. The 32 activities are derived from existing canonical `PCI-EDU-*` content, not externally validated interventions. Every adapted activity remains a distinct new record linked to its unchanged source.
3. A scenario consequence is an educational possibility, not a prediction about people or a judgment of character. UI must avoid scoring 'good'/'bad' people.
4. Per-chapter completeness should not be inflated: the `PCI-ISS-056` discrepancy requires verification, and inherited 55 issues remain open.
5. The plain JSON content pack and public TypeScript interfaces contain no personal user inputs; future private responses and user-created rehearsal scenes must never be committed to GitHub Pages.
