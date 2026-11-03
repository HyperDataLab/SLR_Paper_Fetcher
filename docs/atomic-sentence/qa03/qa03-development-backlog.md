# QA-03 Atomic Sentence Development Backlog

**Status:** Proposed backlog. Except for the owner-review ticket, implementation tickets are blocked pending approval; none is READY FOR IMPLEMENTATION.  
**Canonical ID format:** AS-AREA-###. See [task ID reconciliation](qa03-task-id-reconciliation.md).  
**Scope:** QA-02 proposed MVP only. This is planning material and authorizes no code or schema changes.

## Status definitions

- **BLOCKED:** Depends on an unapproved product decision, unfinished contract, external dependency, or blocked predecessor.
- **READY FOR REVIEW:** A reviewable proposal/action is ready for the responsible owner; this does not mean coding can start.
- **READY FOR IMPLEMENTATION:** All required product decisions, specifications, and prerequisites are approved. No current implementation ticket meets this status.

Priorities retain the existing plan's intent: P0 blocks a safe MVP, P1 completes the working workflow, P2 is later or optional. These are proposed priorities, not approvals.

## Governance and evaluation

### AS-GOV-001 — Review and record product decisions

- **Objective:** Resolve AS-OD-01 through AS-OD-17 without treating recommendations as approvals.
- **Scope:** Product owner reviews the decision proposal/checklist; research lead reviews gold-set, linguistic, and evaluation choices; record decision, rationale, owner, and date.
- **Technical location or likely files:** docs/atomic-sentence/specifications/atomic-sentence-product-decisions-proposal.md; docs/atomic-sentence/specifications/open-decisions.md; decision record location selected by the owner.
- **Dependencies:** None; QA-02 proposal is the input.
- **Acceptance criteria:** Each decision has an explicit approved/deferred/rejected outcome and rationale; no status is inferred from this backlog; SPS and target decisions are explicit.
- **Testing requirements:** Human cross-check each outcome against PRD traceability; verify all 17 IDs are covered and no recommendation is copied as an approval.
- **Risks:** Partial decisions leave downstream data/API assumptions incompatible.
- **Status:** READY FOR REVIEW.
- **Priority:** P0.

### AS-GOV-002 — Approve MVP and versioned annotation/lifecycle contract

- **Objective:** Turn approved product choices into a stable implementation contract.
- **Scope:** Finalize Atomic Sentence definition, inclusion/splitting rules, role/origin mapping, context/evidence policy, English counting, state transitions, reviewer policy, SPS fallback, and explicit MVP exclusions.
- **Technical location or likely files:** docs/atomic-sentence/specifications/atomic-sentence-annotation-contract.md; atomic-sentence-lifecycle.md; atomic-sentence-evaluation-contract.md; atomic-sentence-mvp-scope.md.
- **Dependencies:** AS-GOV-001. Final pilot metric thresholds may be refined after AS-QA-001/002, without reopening approved semantic rules.
- **Acceptance criteria:** Each PRD P0 has an unambiguous requirement and acceptance rule; unsupported linguistic labels are excluded; requirements retain source traceability; all documents share one approved version.
- **Testing requirements:** Specification traceability review; verify role/origin enums and lifecycle against the PRD; check no unresolved decision is silently encoded.
- **Risks:** SPS Appendix 1 is unavailable; product owner must explicitly accept a manual/versioned fallback or obtain the source.
- **Status:** BLOCKED.
- **Priority:** P0.

### AS-QA-001 — Build the adjudicated MVP gold set

- **Objective:** Establish references for extraction, atomization, context completion, support, and provenance.
- **Scope:** Select authorized, representative launch-domain papers; annotate evidence and ideal atoms independently; adjudicate disagreements; split train/dev/test by paper.
- **Technical location or likely files:** Research-approved corpus/annotation workspace; test fixture location selected after privacy and source-access review; docs/atomic-sentence/specifications/atomic-sentence-evaluation-contract.md.
- **Dependencies:** AS-GOV-002; AS-OD-15 and AS-OD-11; source permissions; two annotators and an adjudicator.
- **Acceptance criteria:** The set covers relevant prose/results/limitations and approved source types; each label has guidance; spans resolve against exact source/mapping versions; sample and split are documented.
- **Testing requirements:** Double-annotation and adjudication checks; span/offset round-trip; verify no paper occurs in more than one split; protect restricted source files.
- **Risks:** Domain/sample bias, insufficient annotation capacity, or unavailable rights can invalidate model evaluation.
- **Status:** BLOCKED.
- **Priority:** P0.

### AS-QA-002 — Define metrics and release gates

- **Objective:** Specify metric definitions, denominators, and which results govern release.
- **Scope:** Preserve PRD hard gates; define candidate precision/recall, atomicity, numeric faithfulness, evidence support, review coverage, provenance, and error reporting. Do not define thresholds for deferred linguistic labels.
- **Technical location or likely files:** docs/atomic-sentence/specifications/atomic-sentence-evaluation-contract.md; evaluation report template.
- **Dependencies:** AS-GOV-001/002; AS-QA-001 for thresholds based on pilot evidence; AS-OD-16/17.
- **Acceptance criteria:** Metrics are task-specific and have denominators; hard process gates are distinguished from provisional PRD targets; κ=0.77 is not used as an Atomic model threshold.
- **Testing requirements:** Review metric formulas against hand-calculated examples; verify zero-candidate paragraphs and per-paper sampling are counted as defined.
- **Risks:** Undefined matching/adjudication rules can produce misleading precision or recall.
- **Status:** BLOCKED.
- **Priority:** P0.

### AS-QA-003 — Evaluate and tune the MVP pipeline

- **Objective:** Measure candidate, atomization, context, and precheck performance and document model/prompt changes.
- **Scope:** Run versioned pipeline against the held-out gold set; report denominators, errors, reviewer effort, and PRD provisional targets; tune only after baseline capture.
- **Technical location or likely files:** Evaluation tooling and report location selected during AS-QA-002; AI prompt/config files only in a later implementation task.
- **Dependencies:** AS-QA-001/002; AS-AI-001 through AS-AI-004; source fixtures.
- **Acceptance criteria:** Results are reproducible by model/provider/prompt version; error types include unsupported additions, lost uncertainty, numeric distortion, and unresolvable evidence; thresholds are reported with owner-approved status.
- **Testing requirements:** Repeat metric calculations from saved outputs; verify paper-level held-out evaluation and deterministic validators.
- **Risks:** Small or narrow gold set may not support broad claims.
- **Status:** BLOCKED.
- **Priority:** P1.

### AS-QA-004 — Test source indexing, provenance, and stale behavior

- **Objective:** Prevent evidence offsets, quotes, or source versions from drifting.
- **Scope:** Add fixtures for valid GROBID mappings, page spans, paragraph boundaries, punctuation, malformed/partial text, PDF replacement, mapping changes, and segmenter changes.
- **Technical location or likely files:** tests/ and Atomic source-index/parser modules selected during implementation; current mapping validation in ai_analysis.py is precedent.
- **Dependencies:** AS-SRC-001; AS-DATA-002; approved source-version policy.
- **Acceptance criteria:** Exact quote/offset round-trips pass; source/mapping/segmenter changes invalidate dependent current records; partial mappings remain explicit.
- **Testing requirements:** Automated unit and regression fixtures; PDF hash mismatch and boundary/property tests; no live model calls required.
- **Risks:** Golden fixtures may not represent layout-heavy source failures.
- **Status:** BLOCKED.
- **Priority:** P0.

### AS-QA-005 — Regression-test existing SLR workflows

- **Objective:** Preserve the current Fetcher while Atomic changes are integrated.
- **Scope:** Verify paper search/download, repository, RIS export, current AI analysis/review, PDF view, graphs, SAFFRON/OpenAlex, and optional SLR sync.
- **Technical location or likely files:** Existing tests/ and repository CI/test entry points.
- **Dependencies:** AS-API-001 through AS-API-004; AS-SRC-001; AS-AI-001 through AS-AI-004; AS-UI-001 through AS-UI-003; AS-LIB-001/002; AS-QA-004.
- **Acceptance criteria:** Existing payloads and saved analyses remain readable; Atomic failures do not alter current analysis status or data; legacy workflows pass.
- **Testing requirements:** Run existing automated suite plus documented representative workflow regression; report failures and environment.
- **Risks:** Current app.py composition and PaperStore initialization create cross-feature regression risk.
- **Status:** BLOCKED.
- **Priority:** P0.

### AS-QA-006 — Usability, accessibility, and pilot acceptance

- **Objective:** Confirm reviewers can inspect, verify, reject, and retrieve source-linked items safely.
- **Scope:** Conduct researcher walkthroughs; assess source navigation, evidence distinction, keyboard access, status comprehension, and reviewer workload.
- **Technical location or likely files:** Pilot protocol/report under docs/atomic-sentence/qa03/ or approved QA location; implemented UI after prerequisite tickets.
- **Dependencies:** AS-UI-002/003; AS-LIB-001/002; AS-QA-003/005; approved reviewer policy.
- **Acceptance criteria:** Reviewers distinguish source text, AI wording, and verified records; decisions persist; accessibility and known limitations are documented; release decision is explicit.
- **Testing requirements:** Moderated usability and keyboard/accessibility checklist; collect reviewer errors and completion time.
- **Risks:** Pilot feedback is not representative without intended-domain reviewers.
- **Status:** BLOCKED.
- **Priority:** P1.

### AS-QA-007 — Evaluate deferred linguistic annotation extensions

- **Objective:** Preserve a future path for optional hedge cues/scopes, stance/engagement, and metadiscourse without adding them to MVP.
- **Scope:** Only proceed after a separate product use case, framework/annotation decision, and gold set exist.
- **Technical location or likely files:** Future research/evaluation documentation and extension modules.
- **Dependencies:** Product-owner scope approval; language/task-specific annotation contract and data.
- **Acceptance criteria:** Each future label family has an independent task definition and evaluation; uncertainty preservation is not reported as hedge detection.
- **Testing requirements:** Inter-annotator agreement and task-specific exact/overlap span metrics approved by research lead.
- **Risks:** Framework transfer across disciplines may yield inconsistent labels.
- **Status:** BLOCKED.
- **Priority:** P2.

## Data and source

### AS-DATA-001 — Approve additive persistence design (legacy DB-01)

- **Objective:** Specify how Atomic data fits the existing SQLite store without changing meanings of current tables.
- **Scope:** Decide normalized records vs versioned artifacts, relationships, constraints, indexes, history, source versions, access, backup, and rollback.
- **Technical location or likely files:** paper_store.py initialization/migration path is the future integration point; logical model in docs/atomic-sentence/atomic-sentence-data-model.md.
- **Dependencies:** AS-GOV-001/002; AS-OD-01/02/03/09/10/11/12/13/14; reviewed data model.
- **Acceptance criteria:** Additive design, no existing-row semantic changes, exact provenance, idempotency/uniqueness, stale handling, migration and rollback documented; no schema is changed in this ticket's planning phase.
- **Testing requirements:** Design review of migration/rollback and old-run readability; implementation later requires migration and transaction tests.
- **Risks:** PaperStore initializes schema at app startup; unapproved assumptions could affect all users/data.
- **Status:** BLOCKED.
- **Priority:** P0.

### AS-DATA-002 — Persist immutable document and sentence versions (legacy DB-02)

- **Objective:** Store or artifact the approved PDF/mapping/text/segmenter identity and sentence source units.
- **Scope:** Implement approved document version, exact source units, offsets, page spans, warnings, and stale invalidation.
- **Technical location or likely files:** paper_store.py plus Atomic data/service modules; .fulltext.json reader in ai_analysis.py is a source adapter, not to be rewritten without need.
- **Dependencies:** AS-DATA-001; AS-SRC-001 contract; AS-API-002; AS-OD-10/11/14.
- **Acceptance criteria:** Every source unit ties to current paper and immutable source identity; exact text/offsets round-trip; source/mapping/segmenter changes create new versions; old versions remain auditable.
- **Testing requirements:** Migration tests, source fixture tests, hash mismatch and version-change tests, backup/restore check.
- **Risks:** Current mapping has PDF hash and schema version but no Atomic mapping/segmenter snapshot; page coordinates may be absent.
- **Status:** BLOCKED.
- **Priority:** P0.

### AS-DATA-003 — Persist runs, candidates, decisions, and library eligibility (legacy DB-03)

- **Objective:** Store Atomic run outputs and human lifecycle history separately from existing paper analyses.
- **Scope:** Persist runs/stages, candidates/atoms, evidence links, context, precheck, review events, lineage, and derived library state.
- **Technical location or likely files:** paper_store.py only after approved additive design; versioned artifact strategy if accepted.
- **Dependencies:** AS-DATA-001/002; approved lifecycle/output contract; AS-OD-01/02/09/12/14.
- **Acceptance criteria:** Transactions preserve decisions/history; AI cannot create a verification event; changes after verification require approved new version; current library eligibility is reproducible.
- **Testing requirements:** Transaction rollback, FK/integrity, history immutability, concurrency/idempotency, and no-change-to-existing-analysis tests.
- **Risks:** Existing review_decisions and propositions have mutable, differently scoped semantics.
- **Status:** BLOCKED.
- **Priority:** P1.

### AS-SRC-001 — Build canonical sentence source index (legacy AI-01)

- **Objective:** Turn the existing mapped full text into deterministic sentence source units with stable exact anchors.
- **Scope:** Segment validated mapping text; retain hierarchy/order, offsets, page spans, text representation, and segmenter version; surface unsupported layout.
- **Technical location or likely files:** New Atomic source-index module; adapter around ai_analysis.py mapping validation; no mutation of source artifacts.
- **Dependencies:** AS-GOV-002; AS-DATA-001/002; AS-API-002; AS-OD-10/11/14.
- **Acceptance criteria:** Every sentence equals the exact mapped substring; IDs are stable for one version; reprocessing a changed source or segmenter creates a new identity; no guessed page/offset.
- **Testing requirements:** Unit fixtures for punctuation, abbreviations, decimals, hyphenation, Unicode, paragraph boundaries, page spans, and malformed mappings; QA-004.
- **Risks:** Sentence segmentation varies by language and layout; English-only pilot must be explicit.
- **Status:** BLOCKED.
- **Priority:** P0.

## Backend

### AS-API-001 — Define and mount the Atomic API module (legacy BE-01)

- **Objective:** Add a separate route/service boundary within the existing FastAPI application.
- **Scope:** Define versioned schemas and route composition for paper readiness, runs, candidates, review events, library, and export as approved.
- **Technical location or likely files:** app.py composition point; new Atomic router/service package; no route code in this planning ticket.
- **Dependencies:** AS-GOV-002; AS-DATA-001; API/state contract.
- **Acceptance criteria:** Atomic behavior is isolated; route logic delegates to services; safe structured errors; existing /api/analysis and other endpoints retain their payload/behavior.
- **Testing requirements:** Route/schema contract tests and application startup test; legacy route regression.
- **Risks:** app.py is a large composition module; careless sharing can couple Atomic and current analysis lifecycle.
- **Status:** BLOCKED.
- **Priority:** P0.

### AS-API-002 — Connect existing paper and PDF artifacts (legacy BE-02)

- **Objective:** Resolve eligible existing papers and validate their local PDF/mapping without duplicate storage.
- **Scope:** Support current paper keys including DOI and slrwork_ IDs; report readiness, mapping, hash, and extraction warnings.
- **Technical location or likely files:** New Atomic repository adapter/service; paper_store.py lookup; current PDF validation and ai_analysis.py mapping loader.
- **Dependencies:** AS-API-001; AS-DATA-002; AS-OD-11/14.
- **Acceptance criteria:** Only valid saved sources accepted; no duplicate catalog/PDF; missing, partial, unsupported, or stale artifacts have explicit status; original files remain unchanged.
- **Testing requirements:** DOI and work-ID fixtures; missing PDF/mapping, wrong checksum, corrupt PDF, partial mapping, and supported JSON input tests.
- **Risks:** Current papers table key is named doi though some records use work IDs; mapping page anchors are not universal.
- **Status:** BLOCKED.
- **Priority:** P0.

### AS-API-003 — Add independent Atomic run orchestration (legacy BE-03)

- **Objective:** Run Atomic stages without overwriting or blocking the current analysis workflow.
- **Scope:** Enqueue, status/progress, retries, idempotency, cancellation/recovery, errors, and exact document/stage version association.
- **Technical location or likely files:** New Atomic service/worker; app lifespan integration only after queue policy is selected.
- **Dependencies:** AS-API-001/002; AS-DATA-003; approved lifecycle.
- **Acceptance criteria:** Atomic and current analysis statuses are independent; interrupted tasks recover or fail visibly; retries are idempotent; no model error changes existing drafts.
- **Testing requirements:** Worker lifecycle, restart recovery, duplicate request, cancellation and parallel paper tests; existing analysis queue regression.
- **Risks:** Current implementation uses an in-process asyncio queue and a single worker; durable job semantics are not present.
- **Status:** BLOCKED.
- **Priority:** P1.

### AS-API-004 — Enforce review and library invariants (legacy BE-04)

- **Objective:** Enforce human-only verification, immutable rejection/verification, and current-source library eligibility.
- **Scope:** Implement approved transition rules, identity validation, append-only events, regeneration lineage, stale invalidation, and verified-only query guards.
- **Technical location or likely files:** Atomic review/library services; authenticated app context; Atomic data layer.
- **Dependencies:** AS-DATA-003; AS-GOV-002; AS-OD-01/02/12/14.
- **Acceptance criteria:** AI/precheck cannot verify; unauthorized actor cannot review; rejection reason and history persist; verified edits require a fresh version/review; stale items are excluded.
- **Testing requirements:** State transition table tests, authorization tests, stale-source tests, append-only history tests.
- **Risks:** Existing local-user reviewer fallback is not a trusted identity mechanism.
- **Status:** BLOCKED.
- **Priority:** P1.

## AI and PDF processing

### AS-AI-001 — Extract source-grounded claim candidates (legacy AI-02, reduced MVP scope)

- **Objective:** Identify research-relevant candidate claims from indexed source paragraphs.
- **Scope:** Zero-to-many candidates; use current section and neighboring context; retain exact anchors and run/model provenance; no linguistic label families deferred from MVP.
- **Technical location or likely files:** New Atomic extraction module and prompt/schema; existing Ollama/Gemini structured-call helper may be reused.
- **Dependencies:** AS-SRC-001; AS-GOV-002; AS-QA-001 for evaluated acceptance.
- **Acceptance criteria:** Source-only generation; non-claims excluded under contract; no fixed candidate quota; every candidate links to an exact source; report PRIOR_WORK with correct origin and citation marker.
- **Testing requirements:** Candidate precision/recall against adjudicated sample; false-positive/omission analysis; no external content supplied to claim generation.
- **Risks:** Prompt drift, discipline differences, and extraction artifacts may bias candidate selection.
- **Status:** BLOCKED.
- **Priority:** P1.

### AS-AI-002 — Propose semantic Atomic Sentences (legacy AI-03, atomization portion)

- **Objective:** Convert a candidate into zero or more short, standalone, source-supported atoms.
- **Scope:** Apply one-main-proposition splitting; preserve numbers, comparison groups, conditions, negation, causality limits, uncertainty, and study scope; enforce <=25 words.
- **Technical location or likely files:** New Atomic atomization stage, output schema and versioned prompt/config.
- **Dependencies:** AS-AI-001; AS-GOV-002; AS-QA-001; approved role/origin, tokenizer, and evidence rules.
- **Acceptance criteria:** Original source text stays verbatim and separate; each AS has exact evidence; each atom is independently interpretable; overlength or unsupported output cannot be verified.
- **Testing requirements:** Atomicity, source support, semantic preservation and numeric faithfulness evaluation; edge fixtures for association/causation, negation, modality, denominators, and comparisons.
- **Risks:** Generated text can strengthen claims or omit conditions even when fluent.
- **Status:** BLOCKED.
- **Priority:** P1.

### AS-AI-003 — Complete supported context (legacy AI-03, context portion)

- **Objective:** Make proposed atoms independently readable using only source-supported context.
- **Scope:** Resolve explicit pronouns/implicit referents; link all additions to supporting source spans; leave unresolved cases in NEEDS_CONTEXT.
- **Technical location or likely files:** Atomic context service/prompt and evidence-link output contract.
- **Dependencies:** AS-AI-002; AS-SRC-001; AS-GOV-002; AS-OD-02/10/14.
- **Acceptance criteria:** No entity or condition is invented; every contextual addition has evidence; unresolved ambiguity remains flagged; completion cannot rewrite original source.
- **Testing requirements:** Gold-set context-completion accuracy; adversarial ambiguous antecedent and missing-condition tests.
- **Risks:** Context may be supported in neighboring text but still change a claim's scope.
- **Status:** BLOCKED.
- **Priority:** P1.

### AS-AI-004 — Validate and run advisory precheck (legacy AI-04)

- **Objective:** Detect invalid structure, source mismatch, overlength text, missing context, and unsupported/altered claims before human review.
- **Scope:** Deterministic schema/ID/quote/offset/hash/length/status checks plus optional AI semantic support verdict and rationale.
- **Technical location or likely files:** Atomic validator and precheck service; provider helper only for semantic assessment.
- **Dependencies:** AS-AI-002/003; AS-DATA-003; AS-QA-001/002; AS-GOV-002.
- **Acceptance criteria:** Verdict uses PRD support values; deterministic failures are repeatable; issue points to spans; no model outcome can set VERIFIED; stale inputs block review.
- **Testing requirements:** Unit/property tests for deterministic checks; measured support precision/error analysis on held-out papers.
- **Risks:** “Supported” may be confused with human verification or scientific truth unless presentation and API distinguish them.
- **Status:** BLOCKED.
- **Priority:** P1.

### AS-AI-005 — Add deferred linguistic annotation extension

- **Objective:** Preserve the historical plan's advanced label work as a separately approved future capability.
- **Scope:** Only after new approval, implement selected hedge cue/scope, sentence uncertainty, stance/engagement, or metadiscourse tasks under separate contracts. Not part of MVP.
- **Technical location or likely files:** Future Atomic annotation modules and evaluation data; no MVP field or prompt changes.
- **Dependencies:** AS-QA-007; product use case; new annotation decision; separate gold data and metrics.
- **Acceptance criteria:** Each selected task has its own label semantics, evidence spans, versions, evaluation, and approved scope; semantic uncertainty preservation remains separate.
- **Testing requirements:** Task-specific agreement and exact/overlap span metrics.
- **Risks:** The research frameworks are context-dependent and not interchangeable; adding all labels would expand MVP.
- **Status:** BLOCKED.
- **Priority:** P2.

## Frontend and library

### AS-UI-001 — Add Atomic entry point and paper picker (legacy FE-01)

- **Objective:** Let researchers open Atomic and select an eligible existing paper.
- **Scope:** Add navigation/page consistent with existing workspace; show paper metadata and source readiness; do not add a duplicate uploader/catalog.
- **Technical location or likely files:** templates/components/sidebar.html; new Jinja page or Atomic view; shared static JavaScript/CSS.
- **Dependencies:** AS-API-001/002; approved access and language policy.
- **Acceptance criteria:** Existing navigation remains usable; eligible/ineligible source status is clear; no unavailable/stale input starts unnoticed.
- **Testing requirements:** Navigation and paper-list UI tests; keyboard access; integration test against readiness API.
- **Risks:** The app's main views use Jinja/JavaScript; avoid introducing a second frontend build for a simple workspace.
- **Status:** BLOCKED.
- **Priority:** P1.

### AS-UI-002 — Build source-linked candidate review workspace (legacy FE-02)

- **Objective:** Show candidate and atom text beside exact evidence and the original PDF.
- **Scope:** Render source sentence, paragraph/section context, generated wording, page/highlight where available, context links, and precheck findings. Do not show deferred linguistic annotations.
- **Technical location or likely files:** New Atomic Jinja view and JavaScript; reuse analysis PDF endpoint/PDF.js/highlight patterns.
- **Dependencies:** AS-API-003; AS-SRC-001; AS-AI-001 through AS-AI-004; stable output contract.
- **Acceptance criteria:** Source and generated text are visually distinct; evidence opens correct page where mapped; missing page mapping is explicit; warnings and versions are visible.
- **Testing requirements:** Browser interaction and source-navigation tests; text-only fallback; accessibility and responsive layout checks.
- **Risks:** PDF coordinates may be unavailable or inaccurate for some extracted text.
- **Status:** BLOCKED.
- **Priority:** P1.

### AS-UI-003 — Add human verification controls and history (legacy FE-03, review portion)

- **Objective:** Capture explicit, attributable human review without using mutable existing proposition semantics.
- **Scope:** Verify/reject, rejection reason, identity/time, rationale, history, and supported re-generation action.
- **Technical location or likely files:** Atomic review workspace JavaScript/Jinja; AS-API-004; no change to templates/analysis.html business logic.
- **Dependencies:** AS-API-004; AS-GOV-002; trusted identity and state contract.
- **Acceptance criteria:** Reviewer can see all relevant evidence and precheck; invalid transitions are disabled/rejected; decisions and history persist; edits follow approved new-version policy.
- **Testing requirements:** UI transition tests, identity attribution test, decision persistence and unauthorized review tests.
- **Risks:** Current review attribution uses local-user; adopting that default would not meet audit needs.
- **Status:** BLOCKED.
- **Priority:** P1.

### AS-LIB-001 — Add verified-only library and search (legacy FE-03, library portion)

- **Objective:** Retrieve current verified Atomic statements without exposing untrusted candidates as approved.
- **Scope:** Search by claim/paper/author/year/section/role/origin and show provenance, status, and source links.
- **Technical location or likely files:** Atomic library service/API; new Jinja/JavaScript library view.
- **Dependencies:** AS-API-004; AS-DATA-003; AS-OD-01/09/10/12/13/14.
- **Acceptance criteria:** Default query returns only current VERIFIED records; origin is visible; REPORTED_PRIOR_WORK is not shown as PRIMARY_FINDING; stale/rejected/pending items are excluded by default.
- **Testing requirements:** Query/filter tests for every state/origin and stale-source version; access boundary tests.
- **Risks:** Incorrect eligibility logic can misrepresent a reported claim or stale evidence as trusted.
- **Status:** BLOCKED.
- **Priority:** P1.

### AS-LIB-002 — Export verified items as JSON and CSV (legacy FE-04, PRD P0 export)

- **Objective:** Provide required structured exports without losing source and reviewer provenance.
- **Scope:** Implement JSON and CSV export for approved library fields; keep other formats and project synchronization optional.
- **Technical location or likely files:** Atomic serializer/API and library UI; existing RIS export is a format precedent only.
- **Dependencies:** AS-LIB-001; AS-API-004; approved field/encoding/access contract.
- **Acceptance criteria:** Export includes paper key, statement, role, evidence origin, source quote/span/locator, source version, evidence IDs, reviewer/time, and lineage where available; only eligible records export by default.
- **Testing requirements:** Golden JSON/CSV contract tests; Unicode/quoting/escaping tests; verify source version and origin survive round-trip.
- **Risks:** CSV flattening can lose one-to-many evidence links unless a documented representation is used.
- **Status:** BLOCKED.
- **Priority:** P0.

### AS-INT-001 — Confirm optional SLR System synchronization (legacy BE-05/FE-04)

- **Objective:** Determine whether Atomic content has a supported external destination contract.
- **Scope:** Inspect destination capabilities and prepare a decision; implement an isolated adapter only after separate approval.
- **Technical location or likely files:** Existing app.py SLR integration and destination API documentation; future Atomic sync adapter if approved.
- **Dependencies:** AS-DATA-003; confirmed external API owner/contract; privacy/access approval.
- **Acceptance criteria:** Local Atomic workflow operates independently; unsupported payload is not sent through existing analysis upload; sync failure cannot discard local results.
- **Testing requirements:** Contract/mock integration tests only after endpoint and payload are approved.
- **Risks:** Destination schema/capability is not established; premature work can leak or mislabel Atomic data.
- **Status:** BLOCKED.
- **Priority:** P2.

## Current readiness summary

- **READY FOR REVIEW:** AS-GOV-001 only.
- **READY FOR IMPLEMENTATION:** None. No implementation ticket is independent of the unapproved product/annotation/lifecycle choices or its blocked predecessor.
- **BLOCKED:** All other listed tickets. Tickets may be unblocked individually only after their specified decisions, inputs, and predecessor acceptance criteria are recorded.
- Creating this backlog and reconciling IDs is planning work; it does not authorize DB-01 or any other implementation.
