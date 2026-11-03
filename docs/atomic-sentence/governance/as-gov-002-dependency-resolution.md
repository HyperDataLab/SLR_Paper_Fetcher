# AS-GOV-002 — Dependency Resolution Proposal

**Status:** READY FOR REVIEW
**Authority:** Proposed dependency refinement only; the QA-03 backlog remains unchanged and no ticket is unblocked by this document.
**Canonical IDs:** Preserved exactly as recorded in QA-03.

## Current readiness boundary

The AS-GOV-001 review deliverables are complete per the current project context, while all 17 product decisions remain OPEN. The QA-03 backlog snapshot still labels AS-GOV-001 READY FOR REVIEW, the other 27 tickets BLOCKED, and zero tickets READY FOR IMPLEMENTATION; this is a tracker-status synchronization item for the Backlog Owner, not evidence of approval. AS-GOV-002 cannot become an approved requirements contract until authorized Product Owner outcomes and requested Research Lead reviews are recorded.

This document proposes how to remove the circular source/data/API dependencies while retaining the existing ticket IDs and scopes. A Backlog Owner must accept a dependency refinement before the planning system is changed. Until then, current statuses and edges remain as-is.

## Current dependency cycle

The QA-03 backlog currently states:

| Ticket | Current prerequisite text |
|---|---|
| AS-DATA-002 | AS-DATA-001; AS-SRC-001 contract; AS-API-002; AS-OD-10/11/14. |
| AS-SRC-001 | AS-GOV-002; AS-DATA-001/002; AS-API-002; AS-OD-10/11/14. |
| AS-API-002 | AS-API-001; AS-DATA-002; AS-OD-11/14. |
| AS-API-001 | AS-GOV-002; AS-DATA-001; API/state contract. |

As written, AS-DATA-002 cannot complete before AS-API-002, while AS-API-002 cannot complete before AS-DATA-002. AS-SRC-001 also waits on both implementation tickets, although the source index can be specified and tested as a deterministic transformation of a validated mapping fixture. If “AS-SRC-001 contract” means completion of the source-index implementation, DATA-002 also waits on SRC-001 while SRC-001 waits on DATA-002: a second cycle. The words “contract” and “ticket complete” are therefore conflated.

This is a real sequencing blocker, not permission to bypass the dependency list or start a blocked ticket.

## Proposed contract/implementation separation

Keep the canonical tickets and their objectives. Refine acceptance/dependency language so design artifacts and pure transformations can exist before runtime integration:

| Canonical ticket | Proposed prerequisite refinement | Safe completion boundary |
|---|---|---|
| AS-DATA-001 | Remains after AS-GOV-001/002, schema-affecting decision outcomes, reviewed logical model, and required governance/evaluation design gate. | Approve an additive logical/physical data design, source-unit contract, integrity/version rules, indexes, backup/rollback plan. No migration in this governance task. |
| AS-API-001 | Remains after AS-GOV-002 and AS-DATA-001 plus approved API/state contract. | Define and mount an isolated router/schema/service boundary. No source-ingestion behavior is required to complete this ticket. |
| AS-SRC-001 | Proposed dependencies: AS-GOV-002; approved AS-DATA-001 source-unit interface; OD-10/11/14 outcomes; validated mapping fixtures. Remove dependency on completion of AS-DATA-002 and AS-API-002. | Implement a deterministic, side-effect-free index builder that consumes a validated source mapping and produces stable exact source units. Persistence and paper lookup are adapters owned by later tickets. |
| AS-DATA-002 | Proposed dependencies: AS-DATA-001; approved source-unit interface; AS-SRC-001 output contract/fixtures (or implementation); OD-10/11/14. Remove dependency on AS-API-002 completion. | Persist immutable document/source versions and source units; round-trip exact quotes/offsets; does not resolve the catalog/PDF through an API endpoint. |
| AS-API-002 | Proposed dependencies: AS-API-001; AS-DATA-002; AS-SRC-001; OD-11/14. | Integrate existing paper key, saved PDF/structured JSON source, validated GROBID mapping, source index and persistence; return readiness and explicit unsupported/stale/anchor states. |
| AS-DATA-003 | Retain AS-DATA-001/002 and approved lifecycle/output contract with OD-01/02/09/12/14. | Persist runs, candidates, evidence, prechecks and human events separately from current analysis semantics. |
| AS-API-003 | Retain AS-API-001/002, AS-DATA-003 and approved lifecycle. | Independent run orchestration; do not reuse current analysis status or assume its in-process queue is durable. |
| AS-API-004 | Retain AS-DATA-003, AS-GOV-002 and OD-01/02/12/14. | Enforce authorized transitions, append-only history, and current-source library eligibility. |

The proposed split treats an interface/fixture contract as a reviewed dependency artifact, not as completion of another implementation ticket. It also puts the pure source-index function before source storage and API integration, eliminating the DATA-002/API-002 completion cycle.

## Proposed dependency-safe sequence

### Gate 0 — Human governance

1. Authorized Product Owner records outcomes for AS-OD-01–17 in the QA-04 register.
2. Research Lead review/approval requested for AS-OD-09, AS-OD-15 and AS-OD-16 is recorded; AS-OD-03 mapping review is completed and its co-approval requirement is clarified.
3. Resolve cross-decision consistency, confirm the PRD input scope (including structured paper JSON), library route and Admin/analytics priority, source retention/provider handling, and PDF anchor failure semantics.
4. Complete AS-GOV-002 with the versioned requirements/annotation/lifecycle/evaluation contract. Until then, AS-GOV-002 remains BLOCKED — PRODUCT DECISION.

### Gate 1 — Evaluation and data design

5. Approve AS-QA-002 metric definitions and evaluation plan at the design level; numeric thresholds that require pilot evidence remain deferred until AS-QA-001/003.
6. Complete AS-QA-001 gold-set preparation only after the approved annotation/language contract, source permissions, and AS-OD-15 protocol. Its dual annotation/adjudication is separate from operational review quorum.
7. Review and approve AS-DATA-001 only after required decisions and data/evaluation gates are explicit. No migration may precede that approval.
8. Freeze source-unit, source-version, offset-unit, API/state, identity and evidence-link contracts as reviewable artifacts within the existing canonical tickets. Do not add new ticket IDs.

### Gate 2 — First bounded implementation work

9. After AS-GOV-002 and AS-DATA-001 are approved and dependencies are formally refined, AS-SRC-001 can implement the deterministic source-index function against validated fixtures. AS-API-001 can be implemented in parallel if its API/state contract is approved. AS-SRC-001 is the proposed earliest bounded source-processing implementation ticket under the revised graph; this is conditional, not current READY FOR IMPLEMENTATION status.
10. AS-DATA-002 persists the approved source versions and AS-SRC-001 units. Run AS-QA-004 source, offset, hash and stale fixtures as part of this increment.
11. AS-API-002 integrates the existing paper catalog and PDF/structured-JSON/GROBID artifacts with source indexing and persistence. No paper/PDF duplication.
12. AS-DATA-003 and AS-API-003 add Atomic-only run, candidate, evidence, precheck, and independent orchestration state.

### Gate 3 — AI, human review, and retrieval

13. AS-AI-001 extracts source-grounded candidates; AS-AI-002 atomizes; AS-AI-003 completes supported context; AS-AI-004 validates and provides advisory precheck. Use approved label/language/source contracts and versioned provider/output provenance. No AI-to-VERIFIED path.
14. AS-API-004 enforces human lifecycle/library invariants using trusted identity and approved stale-source rules.
15. AS-UI-001 adds the entry/paper selector inside the existing application; AS-UI-002 builds the source-linked review workspace reusing the existing PDF.js viewer; AS-UI-003 adds authorized human actions/history.
16. AS-LIB-001 implements cross-paper verified-only default search in the same workspace; AS-LIB-002 exports both JSON and CSV using the approved fields/access contract.

### Gate 4 — Evaluation and release

17. AS-QA-003 evaluates/tunes against the approved gold set and metric definitions; AS-QA-004 checks source integrity/stale behavior; AS-QA-005 regression-tests existing workflows; AS-QA-006 performs usability/accessibility/pilot acceptance.
18. Do not make model targets/runtime release gates until OD-16/17 outcomes and observed pilot denominators are recorded. Keep AS-QA-007 and AS-AI-005 for explicitly approved post-MVP linguistic extensions only.
19. AS-INT-001 remains optional and blocked until an external SLR System contract and privacy/access approval exist.

## Earliest implementation eligibility

**Today: none.** The current QA-03 status of zero READY FOR IMPLEMENTATION tickets is preserved.

**Conditional earliest source implementation:** AS-SRC-001 after Product Owner outcomes, required Research Lead reviews, AS-GOV-002 approval, AS-DATA-001 approval, a frozen source-unit contract, and Backlog Owner acceptance of the dependency refinement. This is a deterministic source function using validated mapping fixtures; it does not create a migration or require API-002 runtime integration.

**Possible parallel ticket:** AS-API-001 after the same governance/data gates and an approved API/state contract. Its route/service composition can proceed without depending on source-index persistence. The Backlog Owner should confirm whether it is parallel with or precedes AS-SRC-001.

AS-DATA-002 is not the earliest ticket in this proposal: it consumes the approved source-unit contract/index output and must precede the integration work in AS-API-002. This refines the provisional AS-TECH-01 sequence without editing that prior review history.

## Technical preparation that can proceed now

All items below are READY FOR REVIEW and must not change unresolved product behavior:

- Read-only mapping inventory and fixtures for PDF SHA-256/size, full-text reconstruction, section/paragraph offsets, Unicode offset units, page spans and partial-source errors.
- Test design for structured paper JSON input, source identity, citation markers and original-PDF checks.
- PDF.js quote/page anchor coverage study with missing, duplicate and ambiguous match cases.
- Source-unit contract and pure-indexer test cases for punctuation, abbreviations, decimals, hyphenation, Unicode, paragraph boundaries and exact substring round-trip.
- API/router/component/data alternatives and a dependency graph refinement proposal.
- Identity-provider, paper/project authorization, local/cloud provider handling, telemetry privacy, PDF retention, queue durability, backup and rollback feasibility reviews.
- Regression test inventory and acceptance scenarios for existing Analysis/Toulmin/AIF/PDF workflows.

These activities do not approve a schema, migration, API response/state, launch language, review policy, export visibility, score rubric, or release threshold. Do not alter the PRD or QA-03 backlog in this task.
