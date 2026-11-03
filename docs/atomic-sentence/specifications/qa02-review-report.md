# QA-02 Review Report — Atomic Sentence Product & Research Decisions

**Status:** Documentation review and recommendation only. No product decision is approved.  
**Review date:** 2026-11-03  
**Conclusion:** DB-01 is not ready. Obtain product-owner decisions and finalize the requirements/evaluation contract before designing persistence.

## Documents reviewed

### Product and scientific sources

- Atomic Sentence PRD v1.0: read in full. It defines P0 workflow requirements, hard process gates, role and evidence-origin enums, the English word-count convention, advisory precheck, human review, lifecycle, exports, and explicit open decisions.
- CoNLL-2010 hedge task PDF: text was extracted and all 12 pages reviewed. Its distinction between sentence-level uncertainty, cue detection, and scope resolution informs the recommendation to defer complete hedge annotation while retaining semantic uncertainty during atomization.
- Hyland 2005 stance and engagement PDF: readable; its definition of stance/engagement, category discussions, overlap, and disciplinary/context variation (supplied PDF pp. 5–15 and 17–21) were reviewed for the requested decisions.
- Metadiscourse collection PDF: readable. The introduction (PDF pp. 3–13) and relevant Ädel taxonomy sections (including PDF pp. 72, 77, 81, and 84) were reviewed; the volume's extracted text was searched for the relevant framework discussions. The full 226-page collection was not read chapter by chapter. The reviewed sections distinguish interactive/reflexive models from thin/thick methods and do not prescribe one universal product scheme.
- The JMIR study and detailed SPS appendix cited by the PRD were not supplied. The PRD itself says Multimedia Appendix 1 was unavailable; no independent claim is made here about the missing rubric or article.

### QA-01 and repository documents

- Reviewed the annotation contract, lifecycle, evaluation contract, and all 17 records in open-decisions.md. These documents are explicitly drafts; recommendations and proposed statuses have not become approved requirements.
- Reviewed the repository audit, proposed architecture, proposed data model, and implementation plan. These are planning documents, not evidence that Atomic routes, tables, prompts, sentence indexing, or library behavior exist.
- Inspected the relevant current code in app.py, paper_store.py, ai_analysis.py, browser_pdf.py, configuration, templates, static scripts, and deployment files. The findings in the readiness document are grounded in the current repository, not inferred from the proposed architecture.

## Summary of all 17 decision recommendations

All decisions remain **Open** or **Proposed** in the QA-01 decision log. None is marked Approved.

| Decision | Recommendation | MVP / readiness effect |
|---|---|---|
| AS-OD-01 Reviewer count | One trusted operational verifier for every item; second review for an owner-defined exception set. Use two independent annotators plus adjudication for the research gold set. | Approval blocks operational verification/library readiness. |
| AS-OD-02 Request revision | Use immutable REJECTED plus regeneration as a new ID; do not add a separate request-revision state initially. | Does not block source/storage groundwork; approve before review API/UI. |
| AS-OD-03 Role mapping | Keep the four PRD roles and four origins. Map content by function; keep role and origin orthogonal; flag ambiguous mappings. | Blocks reliable label output and evaluation. |
| AS-OD-04 Hedge scope | Preserve modality, uncertainty, negation, and scope semantically; defer whole-sentence classification, cue detection, and scope spans. | Semantic preservation is required; full hedge subsystem is deferred. |
| AS-OD-05 Sentence uncertainty | Defer a separate sentence-level uncertainty label. If added later, distinguish meaning from annotation-unresolved status. | Does not block MVP. |
| AS-OD-06 Stance/engagement overlap | Defer Hyland labels. If adopted later, evaluate contextual multi-label spans and overlap explicitly. | Does not block MVP. |
| AS-OD-07 Metadiscourse scope | Defer metadiscourse from the first product release. | Does not block MVP. |
| AS-OD-08 Metadiscourse lens/method | Defer both choices; if revisited, decide interactive/reflexive and thin/thick independently. | Does not block MVP. |
| AS-OD-09 SPS | Preserve PRD FR-10 as manual, rubric-versioned quality fields; do not invent dimensions or weights or calculate an official score without the appendix/approved rubric. | Blocks final DB-01 field design until fallback/rubric is approved. |
| AS-OD-10 Evidence cardinality | Allow multiple exact spans; distinguish primary claim support from context support. | Blocks final evidence persistence/review contract. |
| AS-OD-11 Language/tokenizer | Propose English-only source/output for the pilot; use and version the PRD whitespace token rule. Flag other languages unsupported until specified/evaluated. | Blocks word-count/source eligibility contract. |
| AS-OD-12 Reviewer identity | Require trusted server-side reviewer identity; do not rely on a client-supplied name. | Blocks operational verification. |
| AS-OD-13 Reported prior work | Include as a verified report from the focal paper, with prominent origin/citation label and filters; never present it as a focal primary finding. | Blocks library/search/export semantics. |
| AS-OD-14 Stale source | Bind output to PDF, mapping/text, and segmentation versions; make dependent items stale on change; require fresh verification for a new version. | Blocks DB/library eligibility policy. |
| AS-OD-15 Gold set | Stratified launch-domain sample; two independent annotators and adjudication; split by paper. | Blocks validated AI release and quality claims, not basic source indexing. |
| AS-OD-16 Language-task thresholds | Retain PRD 100% process gates; define metrics/denominators before evaluation; set advanced-label thresholds only after a pilot. | Blocks release-readiness claims, not DB-01. |
| AS-OD-17 PRD targets/runtime | Measure the PRD's numeric targets and 5,000-word/two-minute goal as provisional pilot targets; require approval before making them hard release gates. | Does not block DB-01; blocks claims that targets are approved or achieved. |

Detailed questions, options, PRD/research traceability, application compatibility, advantages/disadvantages, implementation consequences, and approval status are in [the product decisions proposal](atomic-sentence-product-decisions-proposal.md).

## Recommended MVP boundary

### Required

- Reuse existing paper records, valid local PDFs, and current GROBID mappings; preserve the original PDF and source text.
- Index exact sentences with stable source location, offsets, available pages, and source-version provenance.
- Find zero-to-many research-relevant candidate claims and propose one-to-many independently understandable atoms, each at most 25 words using the PRD English tokenizer.
- Preserve source-supported context, meaning, numbers, units, comparisons, negation, qualifiers, uncertainty, and modality.
- Use only the PRD's four roles and four evidence origins.
- Retain exact source evidence and distinguish primary claim spans from supporting context spans.
- Run support/precheck checks with the PRD verdicts; keep AI advisory.
- Require attributable human verification, immutable rejected/verified history, and new-ID regeneration.
- Provide verified-only default search, origin-aware presentation, and JSON/CSV export with source/reviewer provenance.
- Preserve PRD FR-10 quality-review fields while preventing invented or auto-calculated official SPS.

### Optional after the first working release

Advanced search/ranking, dashboards, batch-review controls, additional export formats, richer reviewer/adjudication tools, re-extraction/deduplication, table/figure region alignment, and optional external synchronization after its contract is confirmed.

### Deferred

Full Hyland stance/engagement annotation; full metadiscourse annotation and its theoretical/methodological selections; separate sentence-level uncertainty classification; advanced hedge cue and scope extraction; multilingual processing; automatic OCR; and an automated multi-reviewer adjudication UI.

Preserving uncertainty in the atom is an MVP semantic requirement. It is not equivalent to implementing a sentence uncertainty classifier, hedge cue detector, or hedge-scope resolver.

## Existing-application fit and readiness

The current application already provides the main substrate: FastAPI/Jinja workspace, DOI/work-keyed paper store, validated saved PDFs, GROBID full-text mapping with source PDF SHA-256 and offset checks, PDF.js source display/highlighting, Ollama/Gemini calls, SQLite persistence, and human review patterns. The Atomic module can reuse these resources inside the existing application.

It does not yet provide Atomic-specific records, routes, sentence index, candidate extraction, annotations, review state, or verified library. Existing proposition and review records have different mutable analysis semantics and should not be repurposed as Atomic data. Current reviewer values can default to local-user; this does not satisfy attributable identity. Existing mapping pins to the source PDF, but no Atomic snapshot of mapping/segmentation versions exists. The app has no configured OCR pipeline, and its current in-process analysis queue is not a durable high-throughput job service.

The full readiness assessment and acceptance criteria for DB-01, BE-01, AI-01, AI-02, FE-01, and LIB-01 are in [the implementation readiness document](atomic-sentence-implementation-readiness.md).

## Remaining unresolved issues

- Product owner approval is needed for the one-review operational policy, revision/rejection behavior, role mapping, MVP annotation boundary, SPS fallback, evidence cardinality, language scope, reviewer identity, reported-prior search behavior, stale-source rules, evaluation protocol, and status of performance/model targets.
- The detailed SPS rubric is unavailable. The PRD's FR-10 is P0, so the field representation cannot simply be omitted; owner approval or the source appendix is required before final persistence design.
- The supplied PRD names its JMIR method paper, but the research pack does not contain it. This limits independent verification of PRD method claims.
- English-only is a safe initial proposal, not an approved constraint. If launch SLR corpora include Vietnamese or another language, tokenizer/segmentation and gold-set requirements must be decided before processing those papers.
- GROBID can produce incomplete structure, particularly for tables, equations, and poor scans. Human source verification needs an explicit partial/unsupported path.
- Individual reviewer identity and project-level access are not supplied by the current reviewer path.
- A mapping hash and deterministic sentence-segmenter version must be recorded for Atomic runs; the current mapping validates PDF identity and offsets but does not establish those Atomic version records.
- The actual SLR System destination contract for Atomic data is unknown; local verification/library should not depend on remote sync.

## Conflicts and stale planning information

1. **Historical source-availability statement:** the earlier repository audit says the Atomic PRD/research pack was not found. The files are now present under docs/atomic-sentence/research and were reviewed for this task. The old audit is left unchanged, as requested; its absence statement is now stale.
2. **Task-ID collision:** the existing implementation plan already uses QA-02 for “Build adjudicated evaluation set.” This request uses QA-02 for product/research decision review. Backlog IDs need reconciliation before ticket creation.
3. **AI stage-ID mismatch:** the implementation plan uses AI-01 for canonical sentence indexing, AI-02 for extraction/linguistic labels, AI-03 for atomization/context, and AI-04 for precheck. This request defines AI-01 as extraction/atomization and AI-02 as context completion/precheck. Stage names and IDs need one canonical mapping.
4. **Scope difference from earlier architecture:** the architecture proposal describes full hedge cue/scope, stance, engagement, and metadiscourse stages. This QA-02 proposal defers those subsystems while requiring uncertainty preservation. The architecture document is a proposal, not evidence these stages exist; obtain owner approval for the narrower MVP scope.
5. **SPS tension:** the PRD marks quality review/SPS fields P0 but the rubric appendix is unavailable. The proposed manual/versioned fallback respects FR-10 without fabricating score rules, but needs owner approval before DB-01.
6. **QA-01 status:** the four QA-01 specification files are drafts and the open-decision register remains unapproved. They are not an approved schema or implementation contract.

## DB-01 decision

**The project is not ready for DB-01.** The existing SQLite store is reusable, and an additive Atomic design is technically compatible, but the open product decisions affect state transitions, reviewer identity, evidence links, SPS fields, tokenizer behavior, library eligibility, and stale-source handling. Designing tables before those decisions are recorded would encode assumptions.

Before DB-01, the product owner should approve the MVP boundary and the schema-affecting recommendations in AS-OD-01–04, AS-OD-09–14. Research/product leads should settle the gold-set plan (AS-OD-15) and evaluation gates/target status (AS-OD-16/17). The SPS appendix should be retrieved if possible. Resolve the QA-02 and AI-stage ID collisions before turning the existing plan into tickets.

This task stops at decision review. No database or application work should begin until product-owner review.

## QA-02 deliverables

- [Product decisions proposal](atomic-sentence-product-decisions-proposal.md)
- [MVP scope proposal](atomic-sentence-mvp-scope.md)
- [Implementation readiness](atomic-sentence-implementation-readiness.md)
- [This review report](qa02-review-report.md)

Only these four QA-02 files were created. No application code, database schema, migrations, API routes, frontend components, prompts, dependencies, .env file, or existing QA-01 files were changed.
