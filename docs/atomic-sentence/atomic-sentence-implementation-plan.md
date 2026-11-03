# Atomic Sentence Integration — Implementation Plan

**Status:** Planning only. No implementation is included in this task. The Atomic Sentence PRD and Atomic-specific academic sources were not found in the repository; requirements and evaluation definitions are therefore an explicit first task.

## Delivery principles

- Implement inside the existing SLR Paper Fetcher and keep the current download, paper-analysis, review, graph, and SLR System workflows intact.
- Reuse paper records, validated PDFs, GROBID mappings, configured AI providers, PDF viewer, SQLite file, and deployment volumes.
- Add versioned Atomic records and endpoints only after the logical model and migration are reviewed. Do not overload existing proposition or argument tables with different semantics.
- Do not expose an item in the Verified Atomic Sentence Library until the required human verification decision is present and its source version is current.

## Work items

Priority definitions: **P0** blocks a safe pilot; **P1** required for the first usable workflow; **P2** expansion or hardening after pilot evidence.

### QA and requirements foundation

| Task ID | Task name | Description | Dependencies | Expected output | Acceptance criteria | Priority |
|---|---|---|---|---|---|---|
| QA-01 | Finalize Atomic requirements and annotation contract | Obtain/review the Atomic PRD and research foundation; define atomicity, source/candidate distinction, hedge markers and scope, stance, engagement, metadiscourse labels, context completion, reviewer policy, languages, and out-of-scope cases. | None | Approved product/annotation contract with versioned labels and examples. | Every requested capability has an operational definition, allowed states, examples and edge cases; unresolved decisions are explicitly recorded; no launch quality claim relies on an undefined label. | P0 |
| QA-02 | Build adjudicated evaluation set | Select representative papers and create human-labeled source sentences, scopes, categories, atomizations, and context completions, with reviewer adjudication. | QA-01; suitable source papers | Versioned gold set and annotation guide. | Each label family has examples and known edge cases; disagreements are adjudicated or recorded; source spans resolve against the exact PDF/mapping version; set can be used without exposing private files. | P0 |
| QA-03 | Define quality and coverage gates | Choose task-specific measures and pilot gates for extraction precision/recall, hedge-scope agreement, label agreement, atom support, context completion, provenance coverage, and reviewer burden. | QA-01, QA-02 | Evaluation protocol and pilot report template. | Metrics and denominators are specified before model tuning; AI confidence is not treated as calibrated without calibration evidence; failure/partial thresholds are reviewable. | P0 |

### Database

| Task ID | Task name | Description | Dependencies | Expected output | Acceptance criteria | Priority |
|---|---|---|---|---|---|---|
| DB-01 | Approve additive Atomic persistence design | Translate the logical model into SQLite tables/artifacts, indexes, status enums, uniqueness rules, and migration/rollback plan. | QA-01; data-model review | Versioned persistence and migration specification. | Paper identity and PDF/mapping remain shared; run, candidate, annotation, precheck, and decision semantics are distinct; stale and superseded data remain auditable; no existing row meaning changes. | P0 |
| DB-02 | Persist immutable document and sentence versions | Add the approved persistence for PDF/mapping hashes, text representation, segmenter version, section/paragraph/sentence identities, exact text, offsets, and page spans. | DB-01 | Additive document-version/source-unit storage or approved equivalent artifact format. | Hashes match current artifacts; every stored source span round-trips; updates create a new version; stale source units cannot enter a current run/library result. | P0 |
| DB-03 | Persist Atomic runs, outputs, decisions, and library state | Store run lifecycle, candidates, atomic statements, annotations, context links, precheck findings, reviewer decisions, and verified/stale library eligibility. | DB-01, DB-02; agreed Atomic output contract | Durable Atomic run and review records with required query indexes. | Transactions keep each decision and its history consistent; AI cannot write a human verification decision; old analysis tables and records remain unchanged/readable. | P1 |

### Backend

| Task ID | Task name | Description | Dependencies | Expected output | Acceptance criteria | Priority |
|---|---|---|---|---|---|---|
| BE-01 | Define and mount Atomic API module | Add a dedicated router/service boundary in the existing FastAPI app for paper readiness, run lifecycle, candidates, review decisions, and library queries. | QA-01; DB-01 | Versioned request/response schemas and mounted Atomic routes. | Existing routes remain behaviorally unchanged; Atomic routes validate identifiers and request shapes; failures return safe structured errors; route logic delegates to services. | P0 |
| BE-02 | Connect existing paper and PDF artifacts | Resolve existing paper IDs, validate local PDF/mapping presence, compare checksums, surface source readiness, and create a document-version snapshot without duplicating files or metadata. | BE-01; DB-02 | Atomic paper readiness and ingestion adapter. | Only valid saved sources are accepted; DOI-less repository work IDs are handled through the existing paper key; missing, partial, or stale mappings report actionable state; source artifacts are not modified. | P0 |
| BE-03 | Add independent Atomic run orchestration | Implement enqueue, progress/status, retryable stages, idempotency, cancellation/restart recovery, and error recording using an independent Atomic lifecycle. | BE-01, BE-02, DB-03 | Atomic run service and worker integration. | Atomic failures do not overwrite or fail the existing analysis draft; existing jobs continue to complete; each retry references the exact document and stage versions; concurrent requests do not create unintended duplicate runs. | P1 |
| BE-04 | Enforce review and library invariants | Validate legal human transitions, append decision history, handle edits/reverification, mark stale entries, and query only current verified items by default. | DB-03; QA-01 review policy | Review/library service rules. | AI/precheck endpoints cannot mark an item verified; every decision has reviewer/time/item/source version; edits invalidate verification as specified; stale and rejected items are excluded from default library results. | P1 |
| BE-05 | Confirm optional SLR System integration contract | Inspect the destination API and decide whether Atomic artifacts can be synced; build an adapter only if the API supports the accepted data model. | DB-03; external API owner/contract | Sync decision record and, if supported, isolated adapter. | Local Atomic workflow works without remote sync; sync failure does not discard local results; unsupported payloads are not silently posted through the existing analysis contract. | P2 |

### AI and PDF processing

| Task ID | Task name | Description | Dependencies | Expected output | Acceptance criteria | Priority |
|---|---|---|---|---|---|---|
| AI-01 | Build canonical sentence source index | Deterministically segment the validated mapping text and link each sentence to paragraph/section IDs, exact offsets, page spans, and document/segmenter versions. | QA-01; DB-02; BE-02 | Versioned sentence index. | Each sentence quote equals its mapped substring; offsets and page spans are tested; changes in source or segmenter version invalidate downstream IDs; unresolvable spans are explicitly marked. | P0 |
| AI-02 | Extract candidates and linguistic annotations | Produce candidate sentences and versioned hedge detection/scope, stance, engagement, and metadiscourse annotations under the agreed contract. | QA-01, QA-02; AI-01; existing Ollama/Gemini provider adapter | Candidate and annotation artifacts with evidence and model provenance. | Every item has source evidence or explicit unresolved status; hedge marker and scope are separate; all labels conform to schema; provider/prompt/model versions are saved; output stays pending human review. | P1 |
| AI-03 | Propose semantic atoms and context completion | Generate one or more standalone atomic statements per candidate when warranted; attach supporting source/context spans and label generated wording. | QA-01, QA-02; AI-01, AI-02 | Atomized statements and context-link records. | Original sentence is preserved verbatim; every atom links to its source; every contextual addition has evidence or is flagged unsupported/unresolved; no model result is presented as source text. | P1 |
| AI-04 | Implement deterministic validation and AI precheck | Run schema, ID, span, quote, source-version, scope, support, and completeness checks; allow AI suggestions as separate findings. | QA-03; AI-02, AI-03; BE-03 | Precheck result artifacts with pass/warning/fail/not-assessed findings. | Deterministic checks are reproducible; findings identify affected spans/items; an AI precheck cannot verify/publish; incomplete input yields partial/fail state rather than a false pass. | P1 |
| AI-05 | Tune and evaluate the pilot pipeline | Evaluate prompts/models against the gold set, record errors and reviewer effort, and adjust thresholds/versioning by label family. | QA-02, QA-03; AI-02 through AI-04 | Pilot evaluation and versioned prompt/config revisions. | Results are reported per task/label and language; model changes are reproducible; pilot gates are met or limitations are documented before library publication. | P1 |

### Frontend

| Task ID | Task name | Description | Dependencies | Expected output | Acceptance criteria | Priority |
|---|---|---|---|---|---|---|
| FE-01 | Add Atomic entry point and paper picker | Extend the existing sidebar/workspace with an Atomic page and list eligible papers from the existing library. | BE-01, BE-02; existing UI conventions | Atomic workspace entry and paper readiness list. | Existing navigation and pages remain usable; paper title/DOI/status/source readiness are clear; users cannot start on an unavailable or stale source without a warning. | P1 |
| FE-02 | Build source-linked candidate review workspace | Show candidate text, PDF/source highlight, section context, hedge scopes, stance/engagement/metadiscourse, atomization, context links, and precheck findings. | AI-01 through AI-04; BE-03 | Candidate detail and review interface. | Source and generated text are visibly distinct; clicking evidence opens the correct paper/page or reports that page mapping is unavailable; labels are accessible and editable only through supported review controls. | P1 |
| FE-03 | Add human verification and library views | Add decision controls, rationale/reviewer capture, history, filters, and a verified-only library view. | BE-04; DB-03 | Verification history UI and Verified Atomic Sentence Library. | Only current verified entries appear by default; pending/rejected/stale entries remain discoverable in run history; edits after verification follow the approved re-review policy. | P1 |
| FE-04 | Add export and project-context affordances | Define user-visible export or optional project association after the PRD identifies needed formats and access scope. | QA-01; FE-03; BE-05 for sync | Approved export/project UI contract and, if selected, implementation. | Exports include source/paper/version/review provenance; no external upload occurs without a confirmed contract; local library remains usable if remote integration is unavailable. | P2 |

### QA and release

| Task ID | Task name | Description | Dependencies | Expected output | Acceptance criteria | Priority |
|---|---|---|---|---|---|---|
| QA-04 | Test extraction, provenance, and stale-source behavior | Add fixtures for GROBID mappings, page spans, multiple paragraphs, punctuation edge cases, malformed text, replacement PDFs, and segmentation-version changes. | AI-01; DB-02 | Automated parser/provenance regression coverage. | Exact quotes and offsets round-trip; stale versions are detected; poor/partial extraction does not create silently valid library items. | P0 |
| QA-05 | Regression-test current SLR workflows | Verify download, paper library, RIS export, existing AI analysis/review, SAFFRON/OpenAlex enrichment, PDF view, graph loading, and optional SLR upload after Atomic changes. | BE-01 through BE-04; AI-01 through AI-05; FE-01 through FE-03; QA-04 | Compatibility test results and regression fixes. | Existing tests and representative end-to-end workflows pass; existing payloads and saved runs remain readable; Atomic errors do not alter existing workflow status. | P0 |
| QA-06 | Run usability, accessibility, and pilot acceptance | Review the candidate workflow with researchers; assess source navigation, decision clarity, keyboard access, reduced motion, label comprehension, and reviewer effort. | FE-02, FE-03; AI-05 | Pilot acceptance report and prioritized fixes. | Reviewers can distinguish source wording, AI suggestions, and verified entries; decisions and rationales persist; known limitations are visible; pilot quality gates are met or release is held. | P1 |

## Recommended implementation order

1. **Requirements first:** complete QA-01 and establish QA-02/QA-03 so “atomic,” labels, evidence rules, and quality gates are testable.
2. **Data and source contract:** approve DB-01, then implement DB-02 and AI-01 with exact quote/offset round-trip coverage. Keep the source immutable.
3. **Backend foundation:** implement BE-01 and BE-02; expose readiness and document versions before expensive model work. Add independent run lifecycle and storage (BE-03, DB-03).
4. **AI stages:** implement AI-02 first, followed by AI-03 and AI-04. Evaluate each stage against the adjudicated set; do not combine failures into one opaque confidence score.
5. **Human workflow:** build FE-01 and FE-02, then BE-04 and FE-03. The UI should make evidence inspectable before the library can publish verified items.
6. **Regression and pilot:** complete QA-04, tune and evaluate through AI-05, complete QA-05, then run QA-06 before declaring the library ready for research use.
7. **Expansion:** only after pilot review, consider additional languages, higher throughput, richer exports, shared multi-user adjudication, or external SLR System synchronization (BE-05/FE-04).

## Explicitly out of scope for this analysis task

No Atomic code, API routes, database schema, AI prompts, migrations, dependencies, `.env` edits, or workflow changes are part of this deliverable. All tasks above are future work items; priorities are proposed ordering, not approval to implement them.
