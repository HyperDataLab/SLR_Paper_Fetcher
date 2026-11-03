# QA-03 Proposed Implementation Roadmap

**Status:** Proposed roadmap; no product decision or implementation stage is approved.  
**MVP boundary:** Unchanged from the QA-02 proposal. No deferred linguistic annotation features are added.

## Roadmap principles

- Keep the existing SLR Paper Fetcher, FastAPI/Jinja application, paper store, PDF artifacts, GROBID path, AI provider configuration, and source viewer as the foundation.
- Keep Atomic run state, sentence records, and review decisions independent of current paper-analysis drafts and proposition/relation tables.
- Resolve product and annotation semantics before persistence, prompts, or review UI.
- Validate exact source indexing before model-generated candidates or atoms.
- Keep semantic uncertainty preservation in MVP; do not build or claim a separate hedge classifier/scope subsystem.
- Do not publish an entry until a trusted human verifies it against current source evidence.
- Do not treat this roadmap as permission to implement.

## Milestone M0 — Product decision review

- **Objective:** Obtain explicit owner decisions for the open product and research choices.
- **Deliverables:** Recorded decisions for AS-OD-01–17; confirmed English/language boundary; reviewer/identity policy; MVP boundary; SPS resolution; selected canonical ticket IDs.
- **Entry criteria:** QA-03 proposal documents are available for review. This criterion is met by this planning package.
- **Exit criteria:** Product owner records each decision as approved, deferred, rejected, or returned for revision, with rationale and date; research lead signs off on gold-set and evaluation choices; no recommendation is mistaken for an approval.
- **Dependencies:** Product owner and research lead availability; SPS appendix retrieval if possible.
- **Risks:** A partial decision set leaves downstream schema and workflow assumptions open. Approval must be explicit; elapsed time or draft existence does not count.
- **Can start now:** Yes, as owner review. No application development is authorized.

## Milestone M1 — Approved requirements, contract, and evaluation design

- **Objective:** Convert the M0 decisions into a versioned and testable MVP specification.
- **Deliverables:** Approved annotation/lifecycle/data-output contract; confirmed PRD FR-01–FR-13 scope; approved metric definitions and gold-set protocol; documented source and reviewer policies.
- **Entry criteria:** M0 decisions that affect scope, roles/origins, evidence, lifecycle, language, SPS, and review are recorded.
- **Exit criteria:** Each P0 requirement has an acceptance criterion; deferred features are explicit; the gold-set design uses two independent annotators plus adjudication; target numbers and runtime goal have agreed pilot/release status.
- **Dependencies:** M0; source-paper permissions; research-lead review.
- **Risks:** The JMIR method paper/SPS appendix is unavailable; five rubric dimensions and score weighting cannot be invented. The current QA-01 drafts must be versioned only after decisions are accepted.
- **Can start now:** Contract review preparation can proceed; final contract approval and gold annotation wait on M0.

## Milestone M2 — Persistence and API design approval

- **Objective:** Design additive Atomic persistence and interfaces without changing existing database behavior.
- **Deliverables:** DB-01 persistence design, migration/rollback plan, source-version strategy, state/identity contract, API boundary and error contract.
- **Entry criteria:** M1's data-affecting decisions are approved; task IDs are reconciled; current PaperStore and data-volume constraints are documented.
- **Exit criteria:** Design preserves current rows/workflows; identifies document/mapping/text/segmenter identity; supports multi-span evidence, review lineage, stale eligibility, SPS provenance, and verified-only queries; owner/technical review is recorded.
- **Dependencies:** M1; existing paper_store.py SQLite conventions; app.py FastAPI composition; current file/data volume layout.
- **Risks:** PaperStore creates/migrates tables during initialization; schema assumptions can affect all app startup. Current reviewer identity and mapping-version model are insufficient without explicit decisions.
- **Can start now:** No implementation. Design ticket remains blocked until M0/M1 exit.

## Milestone M3 — Backend source readiness and canonical sentence index

- **Objective:** Make existing saved papers usable as exact, versioned source units.
- **Deliverables:** Atomic paper-readiness adapter; canonical sentence index; validated PDF/mapping/source snapshot; source integrity fixtures and stale-state behavior.
- **Entry criteria:** M2 design approval; valid saved PDF/mapping; approved source text representation, language, segmentation, and stale-source policy.
- **Exit criteria:** Each sentence quote equals its mapped substring; offsets resolve; version/hash mismatch blocks use; missing page spans remain explicit; current analysis and paper records are unchanged.
- **Dependencies:** AS-API-001/002, AS-DATA-002, AS-SRC-001, AS-QA-004 in the canonical backlog.
- **Risks:** GROBID layout extraction can be partial; there is no configured OCR service; mappings may not contain usable table/caption anchors.
- **Can start now:** Repository review and non-mutating fixture inventory are complete/plannable; implementation waits for M2.

## Milestone M4 — Candidate extraction and semantic atomization

- **Objective:** Create source-grounded candidate claims and <=25-word standalone statements.
- **Deliverables:** Versioned candidate extraction and atomization stages; outputs with source spans, allowed role/origin, run/model/prompt provenance; baseline evaluation results.
- **Entry criteria:** M3 source indexing passes; M1 contract and gold-set instructions are approved; model/provider settings are agreed.
- **Exit criteria:** Zero-to-many candidates supported; one-to-many atomization supported; exact source quote retained; numerical relations and conditions preserved; uncertainty/modality preserved; unsupported additions and overlength statements cannot pass review.
- **Dependencies:** AS-AI-001/002; AS-QA-001; existing Ollama/Gemini structured-call utilities.
- **Risks:** Fluent output may alter meaning, lose scope, misattribute prior work, or omit denominators; no model target is validated before evaluation.
- **Can start now:** No. The gold set and annotation contract are required first.

## Milestone M5 — Context completion and advisory precheck

- **Objective:** Make statements independently intelligible only when source evidence supports additions, and expose validation warnings before review.
- **Deliverables:** Context-link records; NEEDS_CONTEXT behavior; deterministic validation; advisory support verdict/rationale and implicated spans.
- **Entry criteria:** M4 outputs and evidence cardinality are stable; source versioning works; PRD verdict and lifecycle semantics are approved.
- **Exit criteria:** Added referents/conditions link to exact source context; unsupported context is blocked or flagged; precheck uses PRD verdicts and never sets VERIFIED; edits invalidate prior precheck.
- **Dependencies:** AS-AI-003/004; AS-DATA-003; AS-API-003; gold-set evaluation.
- **Risks:** Model verdict may be misread as scientific validation; stale results can attach to changed wording/source if version dependencies are weak.
- **Can start now:** No; waits for M4 and approved evidence/lifecycle policies.

## Milestone M6 — Human verification workspace

- **Objective:** Let an authorized researcher compare generated material with exact paper evidence and record an accountable decision.
- **Deliverables:** Candidate review workspace; source/PDF display; verify/reject controls; reviewer identity, rationale, timestamp, and immutable history; supported regeneration lineage.
- **Entry criteria:** M2 API/data design; M3 source linking; M5 precheck contract; trusted reviewer identity and lifecycle decisions approved.
- **Exit criteria:** Reviewer sees source and generated text distinctly; legal transitions enforced; no AI-only verification; reject reason and lineage persist; verified edits require new version and re-review; no change to existing analysis review workflow.
- **Dependencies:** AS-API-004, AS-UI-002/003, PDF.js viewer/highlight patterns, approved identity source.
- **Risks:** Existing local-user default is not individual attribution; source page alignment can be absent; reviewer actions are high-integrity writes.
- **Can start now:** No. Identity and transition policy are blockers.

## Milestone M7 — Verified library, search, and export

- **Objective:** Retrieve and export only current, human-verified records with traceable provenance.
- **Deliverables:** Library eligibility service; verified-only default search; role/origin/section/paper filters; JSON and CSV export with source/reviewer provenance.
- **Entry criteria:** M6 verification gate works; stale and superseded rules and prior-work presentation are approved; P0 export/search contract is specified.
- **Exit criteria:** Pending, rejected, stale, and superseded records are excluded by default; REPORTED_PRIOR_WORK is visibly distinct and never presented as PRIMARY_FINDING; source and review provenance survive search and export.
- **Dependencies:** AS-LIB-001/002; AS-API-004; current paper metadata and PDF links.
- **Risks:** Wrong eligibility or origin display can make unverified/stale/secondary claims appear trusted; CSV needs a defined one-to-many evidence representation.
- **Can start now:** No. Library depends on verified lifecycle and origin policy.

## Milestone M8 — Regression, pilot evaluation, and release decision

- **Objective:** Demonstrate the MVP is usable, source-faithful, compatible, and understood within the defined pilot limits.
- **Deliverables:** Source-integrity test results; current SLR regression results; pilot quality report; accessibility/usability findings; owner release decision.
- **Entry criteria:** M3–M7 integrated; adjudicated gold set and metrics approved; feature flags/rollback plan available if required by technical review.
- **Exit criteria:** PRD hard process gates met; metric denominators and failure examples reported; targets carry approved status; current app workflows pass; known limitations and non-English/poor-scan behavior are visible.
- **Dependencies:** AS-QA-001–006; current repository test suite and representative end-to-end workflows.
- **Risks:** Pilot quality may vary by discipline and extraction quality; passing process gates does not establish scientific truth or broad model performance.
- **Can start now:** Test planning can be reviewed; release evaluation waits for implementation and gold annotations.

## Critical path and work that can proceed now

### Can proceed now

- Product-owner review of AS-OD-01–17 and research-lead review of evaluation/gold-set recommendations.
- Retrieval of the cited JMIR paper and SPS Appendix 1, if available.
- Confirmation of source-paper permissions, launch corpus/domain, and reviewer identity provider/operator.
- Planning-system update to preserve legacy IDs and adopt the proposed canonical AS-AREA-### IDs.
- Non-mutating repository/source-mapping inventory or technical review that does not set product behavior.

### Requires approved product decisions

- Final annotation/lifecycle/evaluation contracts.
- DB-01 persistence design and any migration plan.
- API schemas, reviewer actions, library eligibility, export fields, tokenizer behavior, origin filtering, and stale-source rules.

### Requires approved annotation/data contract

- Canonical source index/segmentation, candidate output, atomization, context completion, and AI precheck.
- Gold annotation, evaluation denominators, and model release gates.

### Requires trusted reviewer identity or other infrastructure

- Human verification controls and any publication to the verified library.
- Per-reviewer audit and authorization tests.
- Concurrent review or multi-user collaboration, if later approved.

## No parallel implementation before approval

Product decisions, role/origin policy, evidence-cardinality, language/tokenization, lifecycle, and reviewer identity are shared assumptions. Do not parallelize DB/API/AI/UI feature work before those are stable. After the contract is approved, gold-set preparation and DB/API design may proceed as separately reviewed workstreams if they use the same versioned contract; source indexing still precedes candidate/atomization implementation.
