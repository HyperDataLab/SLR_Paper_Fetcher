# QA-03 Dependency Map

**Status:** Proposed sequencing; no product decision is approved.  
**Scope:** MVP dependency map only. Full hedge extraction, stance/engagement, metadiscourse, OCR, multilingual processing, and automated multi-review adjudication are deferred per the QA-02 proposal.

## Dependency overview

Recommended sequence:

1. Product decisions and versioned specification approval.
2. Gold set and evaluation protocol, in parallel with data/API design only after annotation scope is approved.
3. DB-01 additive persistence design.
4. Backend module and paper/source readiness.
5. Canonical sentence source index.
6. Candidate extraction.
7. Semantic atomization, then context completion.
8. Deterministic validation and advisory AI precheck.
9. Human verification and rejection workflow.
10. Verified library, search, and JSON/CSV export.
11. Regression, evaluation, usability, and release decision.

No feature tickets should be split across teams in a way that presumes open contract choices. The dependencies below are logical gates; after owner approval, engineering can refine them into milestones and sprint-sized work.

## 1. Product decisions and specification approval

- **Required inputs:** Original PRD; QA-01 annotation/lifecycle/evaluation/open-decision drafts; QA-02 decision proposal and MVP proposal; current application facts.
- **Expected outputs:** Recorded product-owner decisions for AS-OD-01–17; approved MVP scope; versioned annotation, lifecycle, source/evidence, and evaluation contract; accepted language and SPS handling.
- **Dependencies:** None for review; all implementation areas depend on the resulting contract.
- **Blocking decisions:** All 17 remain unapproved. Schema and workflow blockers include reviewer quorum/identity (01, 12), revision/lifecycle (02, 14), roles/origins (03, 13), annotation exclusions (04–08), SPS (09), evidence cardinality (10), language/tokenization (11), and evaluation targets/gold set (15–17).
- **Existing reusable components:** PRD, current QA-01/02 documentation, repository audit, proposed architecture/data model, existing analysis/evaluation patterns.
- **New components that may be required:** Decision record/version convention; approved annotation/evaluation addendum. No application component can substitute for product approval.
- **Acceptance criteria:** Every decision has an owner, approval/rejection/defer status, date, rationale, and versioned wording; no draft recommendation is represented as approved; QA-03 task-ID collisions are resolved in the planning system.

## 2. Canonical sentence source index

- **Required inputs:** Existing paper key; validated saved PDF; current checksum-pinned GROBID mapping; approved source text representation; sentence segmentation and version policy.
- **Expected outputs:** Stable section/paragraph/sentence source units with exact text, hierarchy/order, half-open offsets into a named text representation, available page spans, PDF hash, mapping identity, segmenter version, and warnings.
- **Dependencies:** Approved product/source contract; DB-01 and document-version persistence design; backend source-readiness adapter. Existing mapping structure is a prerequisite, not a completed sentence index.
- **Blocking decisions:** AS-OD-10 evidence anchors, AS-OD-11 language/segmentation scope, AS-OD-14 stale-source policy. AS-OD-03 affects downstream labels. Source integrity gate depends on the approved definition of mapping identity.
- **Existing reusable components:** GROBID extraction; adjacent .fulltext.json with full_text, sections, offsets/page spans and source PDF SHA-256; existing loader's checksum, text-coverage, and offset validation; PDF.js source viewer.
- **New components that may be required:** Deterministic sentence segmenter/indexer; Atomic source-version artifact or persistence; source readiness states for missing, partial, stale, or unsupported mapping. No OCR is configured.
- **Acceptance criteria:** Every indexed quote equals its exact substring in the declared mapping representation; offsets and section/paragraph relations round-trip; PDF hash mismatch or unsupported source prevents a current index; segmentation/mapping changes create a new identity and make dependents stale; unresolved page anchors remain explicitly absent rather than guessed.

## 3. Atomic candidate extraction

- **Required inputs:** Approved candidate inclusion/exclusion guide; indexed source sentences; section heading and immediate neighboring context; exact source anchors; launch language; model/provider and prompt version.
- **Expected outputs:** Zero-to-many candidate claim records per paragraph, each linked to exact source sentence/span(s), source origin/citation markers when present, selection provenance, and unresolved status when evidence is inadequate.
- **Dependencies:** Product contract; source index; gold-set sample for evaluated model acceptance; AI provider adapter.
- **Blocking decisions:** AS-OD-03 role/origin mapping; AS-OD-11 language; AS-OD-13 treatment of reported prior work; AS-OD-15 gold-set protocol; AS-OD-16/17 evaluation gates.
- **Existing reusable components:** Existing GROBID paragraphs/sections; source-grounded proposition extraction patterns; Ollama/Gemini structured call utilities.
- **New components that may be required:** Atomic candidate schema/prompt, candidate selection stage, run provenance and candidate lineage.
- **Acceptance criteria:** Only authorized source content is used; zero candidates are allowed; candidate quote/span resolves exactly; reported prior work is not classified as primary finding; unsupported or ambiguous candidates cannot be silently promoted; candidate recall/precision is evaluated against a paper-level held-out set.

## 4. Atomization and context completion

- **Required inputs:** Candidate records, source sentence/context, approved one-main-proposition and splitting guide, 25-word tokenizer rule, context/evidence cardinality.
- **Expected outputs:** Zero or more standalone AS records per candidate; original source wording retained; generated wording/version separate; each AS contains at most 25 English words, uses an approved role/origin, and links to supporting evidence.
- **Dependencies:** Candidate extraction; source index; decision approvals for roles, evidence spans, and language; gold-set instructions for reference atomizations.
- **Blocking decisions:** AS-OD-03, AS-OD-10, AS-OD-11, AS-OD-14 and approved treatment of AS-OD-02. Gold-set completion AS-OD-15 blocks evaluated model release.
- **Existing reusable components:** Existing paper context and mapped offsets; JSON AI call utilities. Existing proposition records are not an Atomic output contract.
- **New components that may be required:** Atomization stage and lineage records; source-supported context-link representation; versioned tokenizer/word-count validator.
- **Acceptance criteria:** One main independently verifiable proposition per AS; split claims retain necessary conditions, comparisons and quantitative values; no unsupported entity is added; every added referent or condition links to source context; preserve uncertainty, modality, negation, units and scope; overlength outputs cannot proceed to verification.

## 5. Deterministic validation and AI advisory precheck

- **Required inputs:** Versioned AS text, source/evidence links, source/document identity, tokenizer version, allowed roles/origins, context links, approved verdict definitions.
- **Expected outputs:** Reproducible deterministic findings plus an advisory semantic-support result of SUPPORTED, PARTIAL, CONTRADICTED, or UNDETERMINED with rationale and cited spans.
- **Dependencies:** Atomization/context output contract; source index; DB-01/DB-02/DB-03; evaluation set and metric protocol before model-level acceptance.
- **Blocking decisions:** AS-OD-02, AS-OD-03, AS-OD-09–12, AS-OD-14, and AS-OD-16/17. Hedge preservation is required, but separate hedge labels remain deferred.
- **Existing reusable components:** PDF/mapping identity and quote/offset checks in ai_analysis.py; existing structured provider output handling.
- **New components that may be required:** Deterministic Atomic validators; independent precheck record and review-safe API; support prompt/version if AI is used for semantics.
- **Acceptance criteria:** Check schema, allowed enums, length, exact quote/offset round-trip, evidence links, PDF/mapping/version identity, and unresolved context; save explanation and affected spans; a precheck cannot create VERIFIED; changes to the item invalidate its findings; evaluate support and error types against adjudicated references.

## 6. Human verification and rejection workflow

- **Required inputs:** Reviewable candidate/AS, exact evidence and source version, precheck warnings, reviewer identity and permissions, approved state transition/rejection rules, SPS/manual quality fields.
- **Expected outputs:** Append-only review event with action, trusted reviewer, timestamp, rationale/rejection reason, source version, and item version; immutable rejection; regenerated child ID where requested; VERIFIED only after human confirmation.
- **Dependencies:** Stable records and API; source index/PDF display; approved reviewer and lifecycle policy; SPS fallback.
- **Blocking decisions:** AS-OD-01, AS-OD-02, AS-OD-09, AS-OD-10, AS-OD-12, AS-OD-14.
- **Existing reusable components:** Analysis review presentation, PDF.js viewer/highlights, existing review history and change records.
- **New components that may be required:** Atomic review screen, trusted actor identity for this workflow, Atomic-specific transition enforcement and decision lineage.
- **Acceptance criteria:** Reviewer can inspect source and generated wording together; no AI-only verification; reject requires a reason; regeneration gets a new ID; substantive verified edits require new version/review; reviewer identity cannot be supplied as an untrusted display string; current analysis review behavior is unchanged.

## 7. Verified Atomic Sentence library

- **Required inputs:** Current verified AS version, qualifying review event, current source identity, role/origin and source locators, approved stale and prior-work rules.
- **Expected outputs:** Queryable current verified records with claim, focal paper metadata, evidence/source links, origin, review provenance, and stale/superseded status.
- **Dependencies:** Human verification, DB-01/DB-03, stable source versioning, origin and stale policy.
- **Blocking decisions:** AS-OD-01, AS-OD-09–14.
- **Existing reusable components:** Paper metadata, local SQLite access, analysis/review patterns, PDF endpoint/viewer.
- **New components that may be required:** Atomic library query/service and UI view; current eligibility derivation/index.
- **Acceptance criteria:** Default library results include only current VERIFIED items; rejected/pending/stale/superseded items are excluded; REPORTED_PRIOR_WORK is conspicuously labeled and never presented as focal PRIMARY_FINDING; source/reviewer provenance is inspectable.

## 8. Search and JSON/CSV export

- **Required inputs:** Library eligibility, approved filters and sort behavior, origin display, required PRD export fields, access policy.
- **Expected outputs:** Verified-only search/filter and JSON/CSV records with claim text, role, origin, paper identity, source evidence IDs/quotes/locators, source version, reviewer/time, and lineage as available.
- **Dependencies:** Library, DB/API query contract, human verification policy, export permission and encoding rules.
- **Blocking decisions:** AS-OD-11–14; AS-OD-12 controls access; AS-OD-13 controls origin semantics. PRD FR-11/FR-13 define search and JSON/CSV as P0.
- **Existing reusable components:** Current result/export UI conventions, paper metadata, PDF links, RIS export patterns.
- **New components that may be required:** Atomic search endpoint, library filters, JSON/CSV serializers and export tests.
- **Acceptance criteria:** Query without an explicit status filter still returns only eligible VERIFIED records; origin and source are not lost in filters/exports; reported prior work is clearly distinguished; exports conform to a versioned contract and include required provenance.

## 9. Testing and evaluation

- **Required inputs:** Approved annotation/lifecycle contract, representative source papers and permissions, two annotators plus adjudicator, metric definitions and denominators, source/mapping fixtures.
- **Expected outputs:** Versioned gold set, parser/provenance regression suite, AI quality report, current SLR regression results, usability/accessibility report, pilot release recommendation.
- **Dependencies:** Product decisions and approved contract. Gold labels precede model tuning. Regression tests run after integration; they do not authorize skipped acceptance criteria.
- **Blocking decisions:** AS-OD-03–11, AS-OD-15–17, with source-access approvals and reviewer identity.
- **Existing reusable components:** Current tests for analysis/research-results workflows; existing structured source validation and app smoke checks.
- **New components that may be required:** Atomic fixtures and acceptance tests; gold annotation guide/data; per-task metric/report scripts; review/usability protocol.
- **Acceptance criteria:** Exact quote/offset and stale-source behavior round-trip; PRD hard gates are measured with denominators; candidate/atomization/support quality is evaluated by paper-level split; two annotators reconcile gold labels; no use of κ=0.77 as an Atomic model threshold; legacy workflows pass regression; failures and unsupported inputs are reported.

## Reusable components vs new components

| Reuse | Add only after contract approval |
|---|---|
| Existing paper identity and local file paths | Atomic source version and sentence index |
| Validated PDF and GROBID .fulltext.json | Atomic run/candidate/atom/context/precheck records |
| GROBID service, section/paragraph mapping, source PDF hash checks | Atomic-specific prompt/output schemas and versioned orchestration |
| Ollama/Gemini configuration and structured-call conventions | Atomic deterministic validators and support precheck |
| FastAPI, Jinja/JavaScript workspace, PDF.js viewer/highlights | Atomic review workspace, verified library, filters, and JSON/CSV export |
| SQLite connection/transaction patterns and data volume | Additive Atomic persistence after DB-01; do not overload propositions/review rows |
| Existing review history patterns | Trusted Atomic reviewer identity and immutable lifecycle |

## Scheduling constraints

- The gold set and its annotation guide must be approved before model tuning; do not parallelize annotation against a moving label contract.
- The source index must be validated before extracting candidates or generating atoms.
- Context completion and precheck need stable evidence links and output versions.
- Human review cannot start until trusted identity and legal transitions are defined.
- Library/search/export cannot start until VERIFIED and stale-source eligibility is deterministic.
- Existing SLR regression is cross-cutting but should run after each integration milestone and before the pilot gate.
