# AS-TECH-01 — Implementation Sequence and Readiness

**Status:** Conditional sequence for review. It does not change QA-03 ticket statuses or start implementation.
**Decision status:** AS-OD-01–17 remain OPEN; the approved requirements baseline does not exist.
**MVP and IDs:** Unchanged from QA-02/QA-03/QA-05.

## Current readiness

| Work | Status now | Safe scope |
|---|---|---|
| Repository/page/source architecture inspection | READY FOR REVIEW | Complete as documentation in this AS-TECH-01 set. |
| UI/API/database/pipeline alternatives | READY FOR REVIEW | Reviewable proposal only; no final labels, contracts, schema or state transitions selected. |
| AS-GOV-001 decision review | READY FOR REVIEW | Product Owner reviews all 17 decisions; requested Research Lead review/approval is completed for OD-09/15/16. |
| AS-GOV-002 requirements baseline | BLOCKED | Wait for explicit authorized outcomes, required research input/co-approval, consistency review and versioned baseline. |
| AS-DATA-001 persistence design approval | BLOCKED | This note supplies alternatives; it cannot approve the schema while the governance dependencies remain unresolved. |
| AS-DATA-002, AS-DATA-003, AS-SRC-001 | BLOCKED | Depend on approved schema, source/language/evidence/stale rules and upstream ticket contracts. |
| AS-API-001–004, AS-AI-001–004, AS-UI-001–003, AS-LIB-001/002 | BLOCKED | Depend on approved requirements, data, identity, lifecycle and source contracts. |
| AS-QA-001–006 | BLOCKED | Research/Product Owner evaluation scope, gold set, metrics and release gates remain unresolved. |

The QA-03 backlog remains **AS-GOV-001 READY FOR REVIEW; other 27 canonical tickets BLOCKED; zero READY FOR IMPLEMENTATION**. No canonical ticket ID or state is changed here.

## Approval and design gates

1. **Product decision review:** Authorized Product Owner records an explicit outcome, identity, timestamp/timezone, conditions/rationale for each AS-OD decision. The developer's preferences are proposals only.
2. **Research review:** Research Lead reviews/co-approves OD-09, OD-15 and OD-16 as requested. Clarify any mandatory co-approval for OD-03. Keep these items OPEN until the required actions are recorded.
3. **Cross-decision consistency:** Reconcile reviewer quorum vs gold-set adjudication, role vs evidence origin, language vs tokenizer/word-count gate, identity vs review authorization, and source versions vs verification/library status.
4. **Requirements baseline:** Complete AS-GOV-002 and version the approved product/research contract, keeping the current MVP scope and canonical IDs unless an authorized scope change is recorded.
5. **AS-DATA-001:** Review the additive model alternatives, integrity constraints, data-retention/rollback, identity/provenance and query requirements. Only then may schema design be approved.
6. **Contract dependency clarification:** Before coding, resolve the current AS-DATA-002 ↔ AS-SRC-001 dependency loop. Define whether a source-unit contract is a reviewed interface/fixture contract rather than completion of the source index, and place API-002 integration at a non-circular point. Do not rename/re-key canonical tickets.

## Conditional implementation order after gates

The order below is a proposal contingent on approvals and dependency clarification; it is not a changed backlog state.

1. Finalize AS-GOV-002 and approve AS-DATA-001.
2. Define a source-unit interface and fixture contract, then sequence AS-DATA-002, AS-SRC-001 and AS-API-002 without a circular completion dependency. A likely coding slice is validated source snapshot and deterministic sentence unit round-trip on fixtures, reusing the existing full-text mapping validator.
3. Implement separate Atomic repository/run/candidate/evidence/review-event storage under the approved schema (AS-DATA-003) and source/paper readiness API (AS-API-001/002).
4. Implement isolated run orchestration (AS-API-003), source-grounded extraction/atomization and precheck (AS-AI-001–004), with prompt/schema provenance and no auto-verification.
5. Add the Atomic tab and existing PDF.js viewer bridge (AS-UI-001/002), then authenticated review controls (AS-UI-003 / AS-API-004) only after the identity and lifecycle contract is enforceable.
6. Add approved library/search and JSON/CSV export (AS-LIB-001/002), then gold-set/evaluation and regression gates (AS-QA tickets) according to Research/Product approval.

### First implementation ticket that can safely start

**None is implementation-ready today.** AS-TECH-01 is design work and is being completed as documentation. AS-GOV-001 can proceed as a human review task, but it is not an implementation ticket. Once AS-GOV-002 and AS-DATA-001 are approved and the dependency loop is clarified, **AS-DATA-002** is a plausible first code candidate for immutable source-version/source-unit persistence and exact offset round-trip, provided its approved source-unit contract and AS-API-002 dependency are made non-circular. Until then, do not create schema, migration, or application code.

## Future integration and regression test strategy

No tests are run or created in this task. When implementation is authorized, add targeted tests in addition to the existing suite:

- Source mapping: PDF hash/size mismatch; missing, malformed, partial and complete mapping; section/paragraph hierarchy and exact source slices; quote/offset integrity; Unicode and offset-unit conversion; page spans missing/coarse; deterministic segmenter versions and source-version changes.
- Persistence: foreign keys, paper-key compatibility (DOI and `slrwork_…`), idempotency, append-only review events, candidate/AS lineage, transaction rollback, stale-source invalidation/revalidation, and unchanged legacy rows/semantics.
- API: schema/error/status contracts, authorization, missing identity rejection, no AI-to-VERIFIED path, retry/idempotency, pagination/filtering, project access, and JSON/CSV provenance.
- AI: source-only inputs; valid zero/one/many extraction; numeric/unit/comparison/negation/qualifier/context preservation; malformed provider output; timeout/error handling; provider/model/prompt/schema provenance; provider output cannot set review state.
- UI: tab only in paper detail mode, exact route/return path, keyboard behavior, responsive three-region layout, source-vs-AI distinction, synchronized section/queue/evidence selection, PDF highlight and anchor-failure behavior, review controls disabled without identity/current evidence, and regression coverage for existing PDF/Toulmin/AIF views.
- Regression: retain and run the existing `tests/test_outline_analysis.py` mapping/offset suite and `tests/test_research_results_table.mjs`; add route and browser coverage without changing their existing semantics.

## Definition of implementation start

A developer may begin a code ticket only when its stated upstream contracts and approvals are satisfied, the ticket's dependencies are non-circular, and acceptance criteria do not require inventing unresolved policy. Technical preparation, design review, test-fixture planning, and feasibility analysis remain safe to continue as nonbinding work.
