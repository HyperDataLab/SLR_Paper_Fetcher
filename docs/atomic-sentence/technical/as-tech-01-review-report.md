# AS-TECH-01 — Review Report

**Result:** Technical inspection and design proposals completed.
**Implementation status:** Not implemented. No application code, business logic, database, migration, `.env`, or existing QA document was modified.
**Approval status:** Product and research decisions remain pending under QA-04/QA-05.

## Deliverables

1. [Current architecture inspection](as-tech-01-current-architecture.md)
2. [UI integration design](as-tech-01-ui-integration-design.md)
3. [Additive database design proposal](as-tech-01-database-design-proposal.md)
4. [API and AI architecture proposal](as-tech-01-api-and-ai-architecture.md)
5. [Implementation sequence and readiness](as-tech-01-implementation-sequence.md)
6. [This review report](as-tech-01-review-report.md)

## Where the tab will appear

The proposed **Atomic Sentences** tab appears in the existing `analysis.html` tab strip on the current paper detail route, `/analysis/paper/{paper_id}?from=/analysis`. It uses the selected existing paper, remains part of the Paper Analysis interface, and is not a standalone application. In the tab, a section navigation rail and Atomic queue share the analysis area; the Evidence & Verification region reuses the existing `#pdfPane` and PDF.js viewer, with a separate Atomic excerpt/context inspector and review controls.

## Reusable existing components and services

- `/analysis/paper/{doi:path}`, `_analysis_paper_id()`, current paper metadata and `PaperStore` paper lookup.
- `/api/analysis/pdf/{doi}` and the saved original PDF.
- `ai_analysis._load_and_validate_fulltext_mapping()` and the existing GROBID mapping's exact text, section/paragraph offsets, source PDF identity and available page spans.
- Existing `analysis.html` tab registration/accessibility patterns, paper-detail split/mobile behavior, toolbar and locally hosted PDF.js viewer/text layer.
- PDF.js quote highlight functions (`highlightQuoteOnPage()`/`selectPdfSource()`) through a narrow adapter, with explicit ambiguity/unavailable state.
- Existing Ollama/Gemini JSON transport as an option for a separately versioned Atomic provider adapter; do not reuse current analysis prompts or semantics.
- Existing source-mapping tests as regression inputs.

## New components/services proposed

- Frontend: `AtomicSentencesTab`, `AtomicPaperNavigation`, `AtomicSectionTree`, `AtomicFilters`, `AtomicSentenceQueue`, `AtomicSentenceRow`, `AtomicEvidenceInspector`, `AtomicPrecheckWarnings`, `AtomicReviewActions`, and a bridge to the existing viewer. A small `static/js/atomic-sentences.js` and `static/css/atomic-sentences.css` are proposed.
- Backend: an isolated Atomic router, schemas, application service, additive repository, source/mapping adapter, run orchestrator, provider adapter, evidence-anchor adapter, and trusted reviewer identity integration.
- Storage: additive versioned document/source units, runs, candidates, AS versions, evidence spans/links, prechecks and append-only review events; a quality-review entity remains conditional on the official SPS rubric and AS-OD-09 approval.

## Database and API proposal

The design reuses the existing paper row and source file and adds no duplicate catalog or PDF. Atomic records remain separate from existing `analysis_runs`, propositions, relations and review history. Store immutable source hash/mapping/text/segmenter identity, exact source offsets and page spans where present, AI lineage, evidence links, provider provenance and human events. Treat SQLite DDL/migrations as future work after AS-DATA-001 approval.

The API proposal adds an Atomic route/service boundary for paper readiness, source index, run creation/status, candidates, AS detail/precheck, human verify/reject/regenerate, library/search and JSON/CSV export. Human verification requires trusted server identity, current source and required evidence. AI can only produce proposals/prechecks; no AI path may set VERIFIED.

## Approval dependencies

QA-04/QA-05 remain authoritative for decision status: **AS-OD-01 through AS-OD-17 are all OPEN; zero approvals are recorded.** The developer's selected/preferred QA-02 options are proposals pending authorized review, not product approval. Product Owner outcomes are missing for all 17. AS-OD-09, AS-OD-15 and AS-OD-16 remain OPEN pending both requested Product Owner and Research Lead review/approval. Research Lead review is requested for AS-OD-03, with formal co-approval authority still to be clarified. The approved requirements baseline AS-GOV-002 is therefore absent.

Approval responsibilities are distinct:

- **Product blockers:** Product Owner decisions for AS-OD-01–17, including scope, lifecycle, evidence, language/tokenization, identity, stale-source handling, origin, library/search and release policy.
- **Research blockers:** Research Lead input/co-approval requested for AS-OD-09, AS-OD-15 and AS-OD-16; AS-OD-03 mapping guidance needs the requested review and a decision about whether that review is mandatory co-approval.
- **Technical preparation:** Repository/source/UI/API/database alternatives, fixture and regression strategy, identity feasibility, PDF anchor coverage and dependency clarification can proceed as reviewable proposals. Technical feasibility does not approve product or research policy.

Full hedge cue/scope detection, sentence uncertainty classification, Hyland stance/engagement, and metadiscourse remain outside the proposed MVP unless formally approved. MVP scope and canonical ticket IDs remain unchanged. No module-wide approval is claimed.

## What QA-05 completed and what remains unresolved

QA-05's five documents are preserved and unchanged. They establish the approval verification, requirements baseline, cross-decision consistency review and technical readiness without inventing approver identity or time. AS-TECH-01 adds six technical design documents and remains consistent with that record.

Still unresolved: all 17 Product Owner decisions; requested Research Lead reviews/approvals; trusted reviewer identity; approved lifecycle and data/API contracts; language/segmentation and word-count policy; evidence cardinality and PDF-anchor coverage; source staleness policy; SPS appendix/rubric; gold-set and evaluation thresholds; and the circular contract dependencies among AS-DATA-002, AS-SRC-001 and AS-API-002.

## First practical development task

No implementation ticket is safe to start now; the QA-03 backlog still has zero READY FOR IMPLEMENTATION tickets. The next practical team action is to complete AS-GOV-001 review and record the required Product Owner/Research Lead outcomes, then establish AS-GOV-002 and review AS-DATA-001. After approval and a non-circular source-unit contract, AS-DATA-002 is a candidate for the first coding slice, subject to its approved dependencies. AS-GOV-001 itself is a review task, not a code ticket.

## Verification performed

- Inspected the current worktree before writing: it was clean.
- Inspected all five QA-04 and all five QA-05 documents and confirmed their approval/readiness status.
- Inspected the route/template, tab handling, PDF.js viewer/highlight bridge, GROBID mapping writer/validator, PaperStore schema and review path, provider adapter/configuration, test inventory, MVP proposal, and canonical dependency notes.
- Confirmed this change set contains only the six new Markdown design documents under `docs/atomic-sentence/technical/`; QA-04/QA-05 and application files remain untouched.
- No tests were run because this is a documentation-only inspection/design task.

## Explicit non-claims

These documents do not mean the Atomic Sentence module is implemented, the UI tab exists, any schema/API/prompt is final, any migration is approved, any human has approved the 17 decisions, or the module as a whole is approved. No QA-06 was created.
