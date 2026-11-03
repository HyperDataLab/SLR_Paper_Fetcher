# QA-05 Implementation Readiness Reassessment

**Requirements baseline:** NOT ESTABLISHED.  
**Approval state:** 17 OPEN; 0 approved.  
**Statuses below use only BLOCKED, READY FOR REVIEW, or READY FOR IMPLEMENTATION.**

## Workstream readiness

| Workstream / canonical tickets | Status | Required approvals | Technical dependencies | Remaining blockers | Conditions for starting |
|---|---|---|---|---|---|
| **DB-01 persistence design — AS-DATA-001** | **BLOCKED** | Resolve AS-OD-01/02/03/09/10/11/12/13/14; explicitly resolve MVP scope for AS-OD-04–08; satisfy QA-03 M1 gate for AS-OD-15–17. | Existing SQLite/PaperStore conventions; approved logical data/source-version contract; rollback and backup plan. | Reviewer identity/quorum, lifecycle, role mapping, SPS P0 fallback, span cardinality, language/tokenizer, origin behavior, stale policy, and evaluation gate status are open. | Record required human decisions and approved specifications; technical design review; preserve existing table meaning; no migration in this QA-05 task. |
| **Canonical sentence source indexing — AS-SRC-001** | **BLOCKED** | Approve source/evidence contract and AS-OD-10/11/14; approve AS-OD-03 for downstream role labels; establish explicit deferrals for unrelated advanced labels. | Existing validated PDF, GROBID .fulltext.json, PDF hash/offset checks, PDF.js viewer; new deterministic segmenter/version and source-index representation. | Text representation, language boundary, evidence-span rules, source/mapping/segmenter identity and stale behavior are open; no Atomic index exists. | Approve source representation and segmentation policy; design approved additive storage/artifact; exact quote/offset fixtures defined. |
| **Candidate extraction and atomization — AS-AI-001/002** | **BLOCKED** | Approve AS-OD-03/04/10/11/13; approve gold-set scope and evaluation requirements AS-OD-15/16/17 before evaluated release. | Validated source index; existing Ollama/Gemini structured-call utilities; approved prompt/output schema and held-out gold set. | Role/origin mapping, uncertainty scope, evidence cardinality, language/tokenizer, prior-work handling, and gold data are open. | Approve annotation/output contract; verify source index; establish source-only prompts and evaluation fixtures. |
| **Context completion and precheck — AS-AI-003/004** | **BLOCKED** | Approve AS-OD-02/03/04/10/11/14; approve human handoff rules AS-OD-01/12 before review. | Versioned candidate/atom output; exact source/context links; deterministic hash/quote/length checks; configured provider only for semantic precheck. | Context-link cardinality, state transition after failure, version invalidation, and the distinction between machine verdict and human verification remain open. | Approve context support and verdict semantics; confirm changes invalidate precheck; ensure precheck cannot write VERIFIED. |
| **Human verification — AS-API-004, AS-UI-003** | **BLOCKED** | Approve AS-OD-01/02/09/10/11/12/14 and visible role/origin rules AS-OD-03/13. | Trusted reviewer identity; current PDF.js/source display; Atomic-specific append-only decisions and transition enforcement. | Current app review path defaults to local-user and is mutable; no Atomic identity, quorum, immutable decision lifecycle, or SPS fallback exists. | Confirm authorized reviewer identity and quorum; approve review actions, evidence display, rejection/re-generation, and re-verification rules. |
| **Verified Atomic Sentence library — AS-LIB-001** | **BLOCKED** | Approve AS-OD-01/09/10/11/12/13/14 and role/origin policy AS-OD-03. | Verified-event model, current source version, eligibility service, existing paper metadata and PDF links. | No approved definition of current VERIFIED eligibility, stale status, prior-work default inclusion, or reviewer authority. | Establish human verification and source-current invariants; define role/origin presentation; exclude non-current/unverified states by default. |
| **Search and JSON/CSV export — AS-LIB-001/002** | **BLOCKED** | Approve AS-OD-03/09/10/11/12/13/14 and required export/access policy. | Library API/query contract, access control, JSON/CSV serializers, one-to-many evidence representation. | Role/origin filtering, evidence serialization, language metadata, reviewer identity, stale filtering, and SPS fields are unsettled. | Approve search filters and export fields; verify only current VERIFIED entries export by default; preserve provenance/origin. |
| **Gold-set and evaluation — AS-QA-001/002/003** | **BLOCKED** | Approve AS-OD-03/04/11/15/16/17; include OD-05–08 only if those features are approved rather than deferred. | Authorized source sample; two annotators plus adjudication; paper-level split; approved metric definitions and denominators. | No selected domain/sample, label contract, language boundary, adjudication protocol, or target/gate status. | Approve sample and annotation guide; identify annotators/adjudicator; define metrics before model tuning; report failures and denominators. |

## Current QA-03 backlog status

- **AS-GOV-001 — Review and record product decisions:** remains READY FOR REVIEW.
- **Other 27 tickets:** remain BLOCKED.
- **READY FOR IMPLEMENTATION:** 0 tickets.

No ticket has become unblocked because no valid human approval was found. This document does not modify the QA-03 backlog or its IDs.

## Readiness decision

DB-01 cannot start. The application infrastructure is reusable, but technical compatibility does not replace approval of source, evidence, identity, lifecycle, role/origin, SPS, and stale-source semantics. The requirements baseline must be established before the readiness conditions above can be satisfied.
