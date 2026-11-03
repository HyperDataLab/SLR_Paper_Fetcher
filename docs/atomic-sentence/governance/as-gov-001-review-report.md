# AS-GOV-001 — Governance Review Report

**Review result:** Documentation is ready for authorized Product Owner and Research Lead review. The requirements baseline is not established.
**Decision status:** AS-OD-01 through AS-OD-17 remain OPEN; no approval is recorded by this report.
**Implementation status:** No implementation ticket is READY FOR IMPLEMENTATION.

## Executive finding

The PRD, QA-01 through QA-05, the canonical QA-03 backlog, and AS-TECH-01 provide a substantial basis for a proposed MVP and a reviewable technical design. They do not establish an approved product contract. The PRD itself is labeled “Proposed MVP specification”; the decision register and QA-05 verification record contain no authorized outcomes. QA-02 and QA-04 recommendations, the developer's preferences, and this report must remain proposals until the authorized reviewers record decisions.

The strongest alignment is on source-grounded statements, exact evidence/provenance, semantic preservation, human-only verification, immutable rejected/history records, and using the existing paper catalog and PDF viewer. The main blockers are the missing approval record, the unavailable SPS rubric, the untrusted current reviewer identity path, unresolved language/evidence/source policies, and a circular dependency among AS-DATA-002, AS-SRC-001, and AS-API-002.

## Documents inspected

- **PRD:** research/PRD_Atomic_Sentence_Paper_Understanding_v1.0.md, including P0/P1 requirements, pipeline, information model, proposed API, UX, metrics, security/performance notes, test scenarios, and explicit open decisions.
- **QA-01 drafts:** open-decisions.md, annotation contract, lifecycle contract, and evaluation contract. These are labeled proposed/draft, not approved.
- **QA-02:** product-decision proposal, MVP-scope proposal, implementation-readiness assessment, and QA-02 review report.
- **QA-03:** ID reconciliation, dependency map, development backlog, implementation roadmap, and review report; also the earlier architecture, data model, repository audit, and implementation plan.
- **QA-04:** decision register, approval questionnaire, responsibility matrix, dependency analysis, and review report.
- **QA-05:** approval verification, requirements-baseline status, cross-decision consistency, implementation-readiness reassessment, and review report.
- **AS-TECH-01:** all six current architecture/UI/data/API-AI/sequence/review documents.

Existing uncommitted files were inspected before this work. The AS-TECH-01 directory was already untracked; it was retained and not edited. This review creates only the three new governance documents.

## Consistency assessment

| Area | Finding | Governance treatment |
|---|---|---|
| Source authority | PRD v1.0 says it is a proposed MVP specification. QA-01 says PRD statements govern product requirements, while QA-02/04/05 still require Product Owner approval. | Use the PRD as the current requirements source for a candidate baseline; ask the Product Owner to confirm it as the approved baseline input. Do not describe it as formally approved. |
| Core MVP | QA-02/03 preserve the PRD P0 requirements FR-01–FR-13 and defer advanced annotation as separate work. AS-TECH-01 is consistent that Atomic is a feature inside the existing Analysis interface and AI cannot verify. | Keep the MVP boundary unchanged. Build the proposed approval baseline from the PRD and record all proposed deferrals explicitly; a proposal to defer is not a DEFERRED decision. |
| Hedge scope | QA-01 AS-OD-04 says all three hedge-related outputs could be adopted if the requested QA-01 capability is approved. QA-02/04 recommend semantic preservation only and deferral of sentence uncertainty classification, cue spans, and cue-linked scopes. | This is a recommendation divergence. Carry the later QA-02/04 option as the candidate baseline because it preserves the PRD meaning requirement without adding an unlisted subsystem; Product Owner must decide AS-OD-04 and dependent AS-OD-05 before that boundary is normative. |
| Proposal vs decision labels | QA-01 open-decisions.md uses “Open” and “Proposed” in its status field. QA-04/05 use approval status OPEN for all 17. Some QA-01 “Proposed” entries are recommendations, not authorized outcomes. | Keep approval status OPEN as recorded in QA-04/05. In AS-GOV-002, distinguish recommendation/proposal status from approval status so “Proposed” cannot be mistaken for “approved.” Do not rewrite the historical QA-01 records in this review. |
| Annotation contract breadth | QA-01 annotation material describes uncertainty labels, hedge spans, Hyland stance/engagement, and metadiscourse. QA-02/03 and AS-TECH-01 place these separate annotation families outside the proposed MVP, while retaining semantic preservation of uncertainty. | Require an explicit AS-OD-04–08 outcome in the baseline. If deferred, the implementation contract and UI/API/schema must not accidentally add those labels or filters. |
| SPS / FR-10 | PRD FR-10 is P0 and specifies five dimension reviews plus an optional reviewer-entered 0–9 score. The PRD says Appendix 1 was unavailable; no supplied dimensions/weights establish an official rubric. | Do not omit FR-10 or invent dimensions/weights. Research Lead and Product Owner must review the appendix or approve a manual, rubric-versioned fallback under AS-OD-09 before data/UI fields are finalized. |
| Input/source coverage | PRD 5.1 allows selectable-text PDFs and already-parsed structured paper JSON when source identity and original-PDF verification are preserved. MVP proposal retains this. AS-TECH-01 concentrates on the current GROBID mapping/PDF path; the backlog's AS-API-002 mentions supported JSON tests. | Ensure source/index/API contracts explicitly include the permitted structured-JSON path or document a Product Owner-approved scope change. Do not narrow the PRD input scope by implementation convenience. |
| PDF verification anchor | PRD requires original-PDF cross-reference. AS-TECH-01 correctly notes that GROBID text offsets are not PDF.js glyph coordinates and quote/page matching may fail or be ambiguous. | Define the supported anchor/failure behavior and keep unsupported/unresolved evidence out of VERIFIED. Technical feasibility review is needed; source/cardinality/staleness decisions remain governed by AS-OD-10/14. |
| Paper detail tab and library | AS-TECH-01 places the tab on /analysis/paper/{paper_id}?from=/analysis, as requested, but leaves /analysis list mode unchanged. PRD also calls for a cross-paper verified library/search with paper, author/year, section, role, origin, reviewer, and verification-date filters. | Preserve the per-paper tab and map AS-LIB-001/002 to the same existing workspace. Add or clarify an in-workspace library entry/navigation acceptance in the canonical UI contract. A detail-only tab without a route to cross-paper search would not meet FR-11. |
| Admin/analytics UX | PRD §11 describes an Admin/analytics screen; the canonical backlog covers evaluation, pilot and metrics, but no explicit analytics-screen acceptance is readily mapped to a ticket. | Decide whether this is MVP, later operations UI, or excluded by approved scope. Map it to existing canonical QA/UI work or record an approved scope decision; do not add or rename a canonical ID in this report. |
| Authentication and access | PRD requires authorized review and paper-level access. Current application workspace API-key gating and local-user attribution do not establish an individual reviewer principal. AS-TECH-01 records this limitation. | AS-OD-12 remains a hard verification/library blocker. Technical/Security review must identify a trusted server-side principal and access boundary before verify/export endpoints can be enabled. |
| Source retention / provider handling | PRD explicitly asks whether the original PDF is guaranteed retained. It also permits configured local/cloud AI providers, while the reviewed requirements do not define source retention duration or provider data-sharing policy. | Treat source retention and any cloud-provider handling as unresolved operational/security requirements. Obtain project/security-owner guidance before operational use; do not assume the saved-file path is a retention guarantee. |
| Task IDs and dependencies | QA-03 reconciles legacy QA-02/QA-03 and AI/FE stage collisions to AS-AREA-### canonical IDs. However AS-DATA-002 depends on an AS-SRC-001 contract and AS-API-002; AS-API-002 depends on AS-API-001 and AS-DATA-002; AS-SRC-001 depends on AS-DATA-002 and AS-API-002. | Keep canonical IDs unchanged, but clarify whether “contract” means an approved interface/fixture contract rather than predecessor implementation. Refine dependency wording before any dependent code starts. |
| First code-ticket sequence | AS-TECH-01 implementation sequence calls AS-DATA-002 a plausible first coding slice after gates. The backlog puts AS-API-001 before AS-API-002 and gives AS-API-001 a different prerequisite set (AS-GOV-002, AS-DATA-001, API/state contract). | The current safe answer is no implementation ticket. After gates, assess AS-API-001 as a possible first code ticket only if its API/state contract is approved; do not treat AS-DATA-002 as definitively earliest until the cycle and ordering are resolved. |

## Decision review and authority

The detailed 17-row blocker/approval map is in [AS-GOV-001 Blocker Matrix](as-gov-001-blocker-matrix.md). At a high level:

- **Product Owner outcome requested:** Every AS-OD-01–17.
- **Product Owner and Research Lead review/approval requested:** AS-OD-09 (SPS fallback/rubric), AS-OD-15 (gold-set design), and AS-OD-16 (metrics/thresholds). The exact joint-signature procedure remains to be confirmed.
- **Research Lead review requested, co-approval status unclear:** AS-OD-03 role-mapping guidance.
- **Research consultation or input, not documented as mandatory co-approval:** OD-01 gold-set distinction; OD-04 and OD-05–08 if research annotation families are reconsidered; OD-11 corpus language; OD-13 reported-prior interpretation; OD-17 metric interpretation. See the matrix for routing details.
- **Research Lead-only decisions:** None of the 17, according to QA-04.
- **Technical/Security confirmation:** Feasibility can be reviewed for evidence spans, tokenizer/segmenter, identity, stale-source handling, SPS representation, source anchoring and runtime; this does not approve product or research policy.

No approver identity, approval timestamp, or authorization is introduced here. The prior developer preference for QA-02 recommended options remains only a proposal for review.

## Work that can proceed without changing OPEN decisions

These activities are safe as read-only, feasibility, or explicitly conditional preparation:

- Maintain route, UI, PDF.js, GROBID, SQLite/PaperStore, provider, authentication, and test inventories.
- Prepare fixtures and test cases for mapping integrity, Unicode offsets, PDF quote-anchor failure, structured JSON input, stale source, and supported-source readiness.
- Review additive persistence alternatives and map each field/record to an AS-OD decision; do not select a schema or create a migration.
- Refine API/service boundaries and in-workspace navigation alternatives without freezing response/state semantics.
- Assess identity-provider, PDF-anchor coverage, GROBID/structured-JSON adapters, provider/privacy, queue durability, source retention, backup, and rollback feasibility.
- Assemble an AS-GOV-002 traceability draft with the approval states and alternatives preserved. Keep it labeled “proposed” and do not publish it as an approved baseline.

### Technical decisions the developer can finalize independently

The developer can finalize internal, reversible engineering choices that preserve existing behavior and the PRD's source/audit invariants: isolate Atomic route/service/repository modules from existing analysis semantics; reuse the current paper key and PDF.js viewer through adapters; choose an offset-conversion implementation with exact Unicode round-trip tests; enforce source-hash/quote validation and an explicit anchor-failure response; keep AI outputs and human review events as separate types; and plan compatibility/regression tests. These choices do not approve product-facing states, permissions, language scope, labels, evidence cardinality, library policy, or schema fields.

The developer cannot finalize the reviewer identity provider, normative API/state contract, persistence schema, supported launch languages, tokenizer policy, required SPS fields/scoring, evidence cardinality, stale-source publication rules, default reported-prior library behavior, release thresholds, data retention, or cloud-provider data-sharing policy on behalf of the authorized owners.

## Readiness answers

- **What is ready:** AS-GOV-001 is ready for authorized decision review; the technical and governance documentation is reviewable; nonbinding architecture/data/API alternatives can be refined. The existing paper/source/UI architecture can be reused as described in AS-TECH-01.
- **What remains blocked:** The requirements baseline; final lifecycle, identity, source, language, evidence, SPS, origin and library rules; research evaluation; final schema/API contracts; source index and all implementation work.
- **Can AS-GOV-002 safely begin?** Its preparatory traceability and conditional drafting can begin. Its canonical approval/baselining work cannot be completed or marked unblocked until the Product Owner records all 17 outcomes, the requested Research Lead reviews/approvals are recorded, and cross-decision checks are reconciled. Keep AS-GOV-002 BLOCKED under the current backlog.
- **Can AS-DATA-001 safely begin?** Review of alternatives and feasibility can proceed; the AS-TECH-01 logical proposal supplies review material. The canonical “approve additive persistence design” ticket remains BLOCKED until governance/evaluation gates and the data-affecting decisions are resolved. No schema or migration should start.
- **Earliest implementation ticket:** None can start now. After governance and AS-DATA-001 gates, AS-API-001 is a possible first code ticket if its approved API/state contract is ready; the current DATA-002/SRC-001/API-002 dependency cycle must be clarified before downstream sequencing. AS-DATA-002 is not established as the first code ticket by the current graph.

## Status and change-scope statement

All 17 decisions remain OPEN; the proposed baseline is not an approval. The QA-03 readiness summary remains AS-GOV-001 READY FOR REVIEW, other 27 canonical tickets BLOCKED, and zero READY FOR IMPLEMENTATION. No canonical ID, MVP scope, prior QA document, application code, business logic, database, or migration was changed. No QA-06 was created.
