# QA-03 Task ID Reconciliation

**Status:** Proposed canonical naming for future work; no task is authorized for implementation by this document.  
**Purpose:** Remove identifier ambiguity while preserving all existing task IDs as historical references.

## Canonical ID format

Use AS-AREA-### for all new Atomic Sentence backlog tickets. The area code names the workstream; the three-digit sequence is unique within that area.

| Area code | Workstream |
|---|---|
| GOV | Product decisions, requirements, specification approval |
| QA | Gold set, evaluation, regression, and release quality |
| SRC | Source identity, parsing, and canonical sentence indexing |
| DATA | Persistence design and implementation |
| API | Backend router, paper readiness, run lifecycle, review rules |
| AI | Candidate extraction, atomization, context, precheck |
| UI | Frontend entry point and human review |
| LIB | Verified library, search, and export |
| INT | Existing-system compatibility and optional integrations |

New tickets use these canonical IDs in their title and references. Legacy IDs remain written as “legacy QA-01,” “legacy AI-02,” and so on, only to preserve traceability to the existing implementation plan or prior task artifacts. Do not recycle a legacy ID for a different scope.

## Existing implementation-plan ID crosswalk

The “canonical ticket” values below point to proposed tickets in [the QA-03 backlog](qa03-development-backlog.md). A mapping can split an old ticket where the new scope differs, or mark advanced work as deferred; this preserves its history without treating its old description as an approved MVP requirement.

| Historical ID | Existing implementation-plan title/scope | Canonical forward reference | Reconciliation |
|---|---|---|---|
| QA-01 | Finalize Atomic requirements and annotation contract | AS-GOV-001, AS-GOV-002 | Requirement approval and contract approval are separate gates. QA-01 remains the historical label. |
| QA-02 | Build adjudicated evaluation set | AS-QA-001 | Preserve as gold-set work; do not confuse with the completed QA-02 decision-review request. |
| QA-03 | Define quality and coverage gates | AS-QA-002 | Evaluation definitions/thresholds remain subject to decision approval. |
| DB-01 | Approve additive Atomic persistence design | AS-DATA-001 | Same general purpose; must not start before schema-affecting decisions are approved. |
| DB-02 | Persist immutable document and sentence versions | AS-DATA-002 | Includes versioned PDF/mapping/text/segmenter identity. |
| DB-03 | Persist Atomic runs, outputs, decisions, and library state | AS-DATA-003 | Atomic-specific persistence; do not reuse analysis tables for different semantics. |
| BE-01 | Define and mount Atomic API module | AS-API-001 | Backend boundary after approved API and data contracts. |
| BE-02 | Connect existing paper and PDF artifacts | AS-API-002 | Reuse existing paper key, PDF, mapping, and readiness checks. |
| BE-03 | Add independent Atomic run orchestration | AS-API-003 | Independent lifecycle/worker; queue reliability is a separate risk. |
| BE-04 | Enforce review and library invariants | AS-API-004 | Enforce approved identity, transitions, history, and stale rules. |
| BE-05 | Confirm optional SLR System integration contract | AS-INT-001 | Deferred until the destination contract and need are confirmed. |
| AI-01 | Build canonical sentence source index | AS-SRC-001 | Keep the source-index work, but use a non-conflicting canonical ID. |
| AI-02 | Extract candidates and linguistic annotations | AS-AI-001; deferred annotations AS-AI-005 | Retain candidate extraction. Do not implement deferred hedge cue/scope, stance, engagement, or metadiscourse labels in the MVP ticket. |
| AI-03 | Propose semantic atoms and context completion | AS-AI-002; AS-AI-003 | Split atomization from context completion to make dependencies and acceptance testable. |
| AI-04 | Implement deterministic validation and AI precheck | AS-AI-004 | Keep machine checks distinct from human verification. |
| AI-05 | Tune and evaluate the pilot pipeline | AS-QA-003 | Align pilot evaluation with the approved gold set and thresholds. |
| FE-01 | Add Atomic entry point and paper picker | AS-UI-001 | Preserve the paper-picker scope; it is not the whole human verification workspace. |
| FE-02 | Build source-linked candidate review workspace | AS-UI-002 | Provides source-linked candidate inspection. |
| FE-03 | Add human verification and library views | AS-UI-003; AS-LIB-001 | Split verification controls/history from library query behavior. |
| FE-04 | Add export and project-context affordances | AS-LIB-002; AS-INT-001 | JSON/CSV export is PRD P0; optional project sync remains deferred and contract-dependent. |
| QA-04 | Test extraction, provenance, and stale-source behavior | AS-QA-004 | Retain as source integrity and stale-version regression testing. |
| QA-05 | Regression-test current SLR workflows | AS-QA-005 | Retain current-feature regression as an explicit release gate. |
| QA-06 | Run usability, accessibility, and pilot acceptance | AS-QA-006 | Retain as final user/pilot acceptance. |

AS-AI-005 and AS-QA-007 in the backlog are future/deferred work items rather than direct replacements for an MVP task.

## QA-02 task and proposed-stage reconciliation

### Task-level collision

The historical **QA-02 Product & Research Decision Review** was a review/documentation task and its deliverables are in docs/atomic-sentence/specifications/. It is not the same work item as legacy **QA-02 Build adjudicated evaluation set** in the implementation plan. Preserve both descriptions in records; use AS-GOV-001 for future decision approval and AS-QA-001 for gold-set creation.

The current **QA-03 Implementation Planning & Backlog Alignment** is likewise the planning task that produced this folder; it collides by label with legacy **QA-03 Define quality and coverage gates**. Preserve the former as this completed QA-03 planning artifact and use AS-QA-002 for future metric/gate work.

### Proposed stage ID collision

QA-02 names these high-level stages: DB-01 additive database design, BE-01 backend foundation, AI-01 extraction/atomization, AI-02 context completion/precheck, FE-01 human verification workspace, and LIB-01 verified library.

| QA-02 stage reference | Legacy ID with same label | Difference | Canonical mapping |
|---|---|---|---|
| DB-01 additive database design | DB-01 additive persistence design | Substantially aligned, but neither is approved for implementation. | AS-DATA-001 through AS-DATA-003 |
| BE-01 backend foundation | BE-01 API module | Same general boundary; readiness should include the paper-readiness adapter as a separate ticket. | AS-API-001 and AS-API-002 |
| AI-01 extraction and atomization | AI-01 source indexing; AI-02 candidate/linguistic extraction; AI-03 atomization/context | AI-01 is a direct scope collision. QA-02 groups work that the legacy plan splits. | AS-SRC-001, AS-AI-001, and AS-AI-002 |
| AI-02 context completion and precheck | AI-02 candidate/linguistic extraction; AI-03 atomization/context; AI-04 precheck | Same numeric IDs refer to different stages. | AS-AI-003 and AS-AI-004 |
| FE-01 human verification workspace | FE-01 Atomic entry/paper picker; FE-02 candidate review; FE-03 verification/library | FE-01 is a direct scope collision; verification requires several UI/backend pieces. | AS-UI-001 through AS-UI-003 and AS-API-004 |
| LIB-01 verified library | No matching legacy ID | New stage, but search is partly in legacy FE-03 and export in FE-04. | AS-LIB-001 and AS-LIB-002 |

The original implementation-plan IDs are historical aliases only. QA-02's stage labels are also preserved as aliases in traceability notes. Ticket systems, branches, commits, and future docs should use the canonical AS-AREA-### IDs.

## Status preservation

- No old task is renamed or deleted in the source implementation plan.
- A canonical crosswalk changes future references, not the meaning of past records.
- No task status is inferred from the existence of a draft document.
- All implementation tickets dependent on unapproved decisions remain BLOCKED.
- A recommendation in QA-02 is not equivalent to product-owner approval.
