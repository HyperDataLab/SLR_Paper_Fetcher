# AS-GOV-002 — Conditional Baseline Review Report

**Result:** Conditional requirements consolidation prepared and READY FOR REVIEW.
**Approval:** No Product Owner or Research Lead approval is created or inferred. AS-OD-01–17 remain OPEN.
**Implementation:** No implementation ticket is currently READY FOR IMPLEMENTATION.

## Deliverables

1. [Conditional requirements baseline](as-gov-002-conditional-requirements-baseline.md)
2. [Requirement-to-ticket matrix](as-gov-002-requirement-ticket-matrix.md)
3. [Dependency resolution proposal](as-gov-002-dependency-resolution.md)
4. This review report.

## What the PRD confirms

The matrix maps all PRD P0 requirements FR-01–FR-13, BR-01–BR-10, the P1/P2 processing stages, input/output and information model, proposed API operations, UX requirements, metrics, nonfunctional requirements, and acceptance scenarios AT-01–AT-14 to canonical tickets where they exist.

The PRD explicitly specifies source-grounded candidate extraction; at-most-25-word, one-main-claim atoms; context ambiguity flags; four functional roles and four evidence origins; exact source evidence/provenance; advisory-only support precheck; human verification; immutable rejection and regeneration lineage; five SPS dimension reviews with an optional human-supplied score; verified-only default search; audit history; and both JSON and CSV export.

CONFIRMED BY PRD records that text is present in the PRD. It does not mean the PRD, MVP, or behavior is formally approved. The PRD calls itself a Proposed MVP specification.

## What remains unresolved

- **Hedge scope:** QA-01 permits a broader three-part hedge annotation if approved. QA-02/04 recommend keeping semantic preservation and deferring separate uncertainty classification, cue spans and cue-linked scope. The candidate retains the PRD semantic rule and carries the QA-02/04 option as PROPOSED — PENDING APPROVAL under AS-OD-04/05.
- **Structured paper JSON input:** The PRD supports structured JSON input if source identity and original-PDF verification are preserved. AS-TECH-01 centers on GROBID/PDF. Source/API contracts must include the PRD input or receive an explicit approved scope change.
- **Structured JSON and CSV output:** PRD FR-13 requires both; the illustrative PRD API endpoint shows JSON only. AS-LIB-002 must contract both formats and shared provenance/access fields.
- **Cross-paper library:** PRD requires filters across papers and reviewers. A per-paper Atomic tab alone is insufficient. Provide an entry into AS-LIB-001 within the existing Analysis workspace.
- **Admin/analytics:** PRD §11 names an analytics screen, but does not assign a priority or dedicated canonical screen ticket. Preserve the stated content and ask the Product Owner to set scope/priority and map acceptance to existing ticket work without inventing an ID.
- **PDF evidence anchoring:** GROBID text offsets do not guarantee PDF.js glyph coordinates. Test quote/page anchors; ambiguous or unavailable anchors must remain explicit and cannot be treated as precise verification evidence.
- **Reviewer identity:** Current workspace gating and local-user attribution do not establish a trusted reviewer principal. AS-OD-12 and technical/security identity integration block human verification and verified-library publication.
- **SPS:** Appendix 1 is unavailable. AS-OD-09 remains OPEN pending the requested Product Owner and Research Lead review/approval. No dimension names, weights, or official automatic score are proposed as final.
- **Dependency cycle:** AS-DATA-002 currently depends on AS-API-002; AS-API-002 depends on AS-DATA-002; AS-SRC-001 additionally waits on both and is itself used as a dependency contract. The dependency proposal separates the source-unit interface and pure indexer from persistence/API integration while keeping all canonical IDs unchanged.
- **Target status:** PRD pilot metric values and the 5,000-word/two-minute benchmark are targets to measure, not validated performance or release gates. OD-16/17 outcomes and denominators remain outstanding.

## Approval responsibilities

- **Product Owner:** Explicit outcome requested for all AS-OD-01–17.
- **Research Lead:** Joint review/approval requested for AS-OD-09, AS-OD-15 and AS-OD-16; role-mapping review requested for AS-OD-03, with mandatory co-approval status unresolved.
- **Technical/Security review:** Can assess source anchors, JSON adapters, language/segmenter feasibility, identity integration, provider handling, retention, queue reliability and migration/rollback. These reviews cannot approve product policy.
- **Backlog Owner:** Must accept any dependency-edge refinement and the canonical ID crosswalk before the external tracker changes. Ticket IDs remain unchanged in this proposal.

## Work and implementation readiness

Read-only architecture/source inspection, fixture/test planning, PDF-anchor coverage analysis, structured-JSON adapter analysis, identity/provider/security feasibility, API/UI/data alternatives, and dependency review are READY FOR REVIEW. They do not select unresolved behavior.

AS-GOV-002’s normative baseline remains BLOCKED — PRODUCT DECISION until authorized outcomes and consistency checks are recorded. AS-DATA-001 can be reviewed as a conditional design alternative, but its canonical approval remains blocked by governance and data-contract decisions. API, storage, source indexing, AI, verification, UI, library, export and release tickets remain blocked under current QA-03 status.

AS-GOV-001 review deliverables are complete per the project context; its 17 decision outcomes remain OPEN. QA-03 still contains the earlier READY FOR REVIEW label for AS-GOV-001, so the Backlog Owner may synchronize that tracker status separately. This report does not modify the backlog.

**Earliest conditional implementation ticket:** If the Product Owner decisions, requested Research Lead reviews, AS-GOV-002 and AS-DATA-001 are approved, and the Backlog Owner accepts the proposed cycle-breaking dependency refinement, AS-SRC-001 may become the first bounded implementation slice: a deterministic indexer against validated fixtures. AS-API-001 could proceed in parallel after its API/state contract is approved. With the current dependency graph unchanged, neither ticket is unblocked.

## Verification and change scope

- The matrix contains individual mappings for FR-01 through FR-13, BR-01 through BR-10, and AT-01 through AT-14, plus UX, API, metrics, nonfunctional requirements and P1 boundaries.
- The baseline accounts for all 17 decisions without changing their OPEN status.
- Canonical ticket IDs and MVP scope are unchanged.
- Existing QA-01 through QA-05, AS-TECH-01, AS-GOV-001 and the original PRD were preserved.
- No application code, database, migration, or QA-06 was created or modified. No tests were run; this is a documentation consolidation task.

This work does not claim the Atomic Sentence module is approved or implemented.
