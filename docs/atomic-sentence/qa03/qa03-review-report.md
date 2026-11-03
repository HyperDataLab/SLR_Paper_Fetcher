# QA-03 Review Report — Implementation Planning and Backlog Alignment

**Status:** Planning deliverables complete; no implementation is authorized.  
**Review date:** 2026-11-03  
**MVP scope:** Unchanged from the QA-02 proposal.  
**Implementation readiness:** No feature ticket is READY FOR IMPLEMENTATION.

## What was inspected

- Original Atomic Sentence PRD v1.0 and its explicit P0/P1 requirements, workflow, business rules, metrics, test scenarios, and open decisions.
- All QA-01 draft specifications: annotation contract, lifecycle, evaluation contract, and open-decisions register.
- All four QA-02 documents: product decisions proposal, MVP scope, implementation readiness, and review report.
- Existing Atomic Sentence repository audit, architecture proposal, logical data model, and implementation plan.
- Current application code relevant to integration: FastAPI route/worker composition in app.py; SQLite schema and review persistence in paper_store.py; GROBID mapping/source validation and provider flow in ai_analysis.py; PDF source display/highlights; configuration, templates, static scripts, and Compose wiring.
- Supplied scientific source findings already reviewed for QA-01/02: CoNLL-2010 separates uncertainty classification from cue and scope tasks; Hyland distinguishes contextual stance/engagement categories; the metadiscourse collection's relevant introduction and Ädel taxonomy sections distinguish theoretical lenses from thin/thick methods. The 226-page metadiscourse volume was not read cover-to-cover.
- The cited JMIR method article and detailed SPS Appendix 1 remain unavailable in the supplied research directory. No .env file was opened.

The Atomic architecture/data model and QA-01/02 documents are proposals or drafts. No Atomic routes, database records, sentence index, extraction prompts, reviewer workflow, or library were assumed to exist.

## What was created

All five deliverables are under docs/atomic-sentence/qa03/:

1. [Task ID reconciliation](qa03-task-id-reconciliation.md)
2. [Dependency map](qa03-dependency-map.md)
3. [Development backlog](qa03-development-backlog.md)
4. [Implementation roadmap](qa03-implementation-roadmap.md)
5. [This review report](qa03-review-report.md)

## Task ID conflicts resolved in the proposal

- Legacy QA-02 means “Build adjudicated evaluation set” in the implementation plan. The separate QA-02 Product & Research Decision Review is preserved as a completed documentation task.
- Legacy QA-03 means “Define quality and coverage gates.” The current QA-03 Implementation Planning & Backlog Alignment is preserved as the completed planning task.
- QA-02's proposed AI-01/AI-02 stages conflict with legacy AI-01 source indexing and AI-02 candidate/linguistic extraction; the canonical map separates source indexing, candidate extraction, atomization, context, and precheck.
- QA-02's FE-01 verification-workspace label conflicts with legacy FE-01 paper picker. The canonical map keeps the paper picker and verification workspace separate.
- QA-02's LIB-01 has no equivalent legacy ID; search and export were split from legacy FE-03/FE-04.
- New forward tickets use AS-AREA-###. Historical IDs are retained in crosswalks and the existing implementation plan is not renamed or edited.

These conflicts are resolved as a proposed crosswalk for future planning. The product owner or backlog administrator still needs to accept the canonical naming in the planning system.

## Which decisions remain open

All 17 product decisions remain Open or Proposed. None was approved by QA-03. The major blockers are:

- Operational reviewer count, trusted reviewer identity, lifecycle and immutable edit/rejection rules.
- Role mapping and reported-prior library treatment.
- Evidence-span cardinality and stale-source policy.
- Language/tokenizer scope.
- Manual SPS representation while the source rubric is unavailable.
- Gold-set composition and evaluation thresholds/target status.
- Approval of the QA-02 deferrals for full hedge cue/scope, sentence uncertainty labels, stance/engagement, and metadiscourse.

The recommendations remain distinct from PRD requirements. The backlog does not treat draft files or completed QA reviews as product approval.

## Which tasks are ready and which are blocked

- **READY FOR REVIEW:** AS-GOV-001, review and record the 17 product decisions.
- **READY FOR IMPLEMENTATION:** None. No application implementation ticket is independent of the unapproved product/annotation/lifecycle decisions or its blocked predecessors.
- **BLOCKED:** All other tickets in the proposed backlog, including DB-01 design, source indexing, API work, AI pipeline, reviewer UI, and library/search/export. Each ticket lists its blockers and prerequisites.

Planning/review work can proceed now: owner review, research-lead review, SPS appendix retrieval if possible, corpus/source permissions confirmation, reviewer-identity selection, and adoption of canonical IDs. That work does not authorize application changes.

## Whether the MVP changed

**It did not change.** QA-03 preserves the QA-02 boundary and all explicit PRD P0 requirements, including paper/source segmentation, candidate extraction, atomization, <=25-word compliance, exact provenance, roles/origins, context completion, advisory precheck, human verification, quality-review/SPS fields with rubric provenance, verified-only library, search, audit trail, and JSON/CSV export.

Uncertainty and modality remain semantic preservation requirements. A sentence uncertainty classifier, hedge-cue detector, and hedge-scope resolver remain distinct deferred tasks. Full Hyland stance/engagement, metadiscourse, multilingual support, automatic OCR, and automated multi-review adjudication remain outside the initial MVP proposal.

## Conflicts and missing information

- The historical repository audit said the PRD/research pack was not found. Those files are present now; the earlier statement is stale and was not rewritten.
- The QA-02/QA-03 task labels collide with legacy QA-02/QA-03 backlog items; AI and FE stage IDs also conflict by scope. The canonical mapping is documented but still needs acceptance in the external planning system.
- The earlier architecture proposal includes advanced linguistic annotation stages that QA-02 defers. The architecture is a proposal, not evidence of implementation or an approved MVP.
- PRD FR-10 marks quality-review/SPS fields P0, but SPS dimensions and weighting are unavailable. Do not invent them or omit the PRD item; obtain Appendix 1 or approve a manual/versioned fallback before DB-01.
- Current source mapping validates PDF checksum and offsets, but Atomic mapping/segmenter version snapshots do not exist. Current review attribution defaults to local-user and does not establish a trusted individual identity.
- Current analysis uses an in-process queue and mutable analysis review paths. New Atomic work must isolate its lifecycle and identity rules.
- Existing application artifacts do not establish an Atomic SLR System sync contract or OCR capability.

## Recommended next action

The product owner should review AS-OD-01–17 in the product decisions proposal and record an explicit outcome for each decision. The research lead should confirm the launch corpus, two-annotator/adjudication plan, evaluation measures, and the missing SPS rubric or approved manual fallback. The product/backlog owner should then adopt the AS-AREA-### identifiers while retaining the legacy crosswalk.

Only after those approvals should the team finalize the QA-01 contracts and begin DB-01 persistence design. No database or application implementation should start before that review.

## Change-scope confirmation

Only the five QA-03 planning documents in docs/atomic-sentence/qa03/ were created. No application code, database schema, migrations, API routes, frontend components, AI prompts, dependencies, .env file, existing QA-01/02 documents, or existing implementation plan were modified.
