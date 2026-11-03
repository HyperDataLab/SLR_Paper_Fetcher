# AS-GOV-003 — Implementation Readiness

**Assessment:** No canonical implementation ticket is READY FOR IMPLEMENTATION under the current QA-03 backlog and approval record.
**Scope:** Ticket readiness and dependencies only; no dependency edge or canonical status is changed here.

## Current gates

- AS-GOV-003 records five selected options, but none is formally APPROVED. AS-OD-06–17 remain proposed/open, with Research Lead review/approval pending for OD-09/15/16 and review pending for OD-03.
- AS-GOV-002 cannot be treated as a final versioned contract until decision outcomes, required review, and cross-decision consistency are recorded.
- AS-DATA-001 is a planning/design approval ticket, not permission to create a migration. It depends on GOV-002, a reviewed data model, and outcomes affecting reviewer policy, lifecycle, roles, SPS, evidence, language, identity, library, and stale-source behavior.
- QA-03 records zero tickets READY FOR IMPLEMENTATION. QA-03 dependency edges remain authoritative until the Backlog Owner accepts a refinement.
- The QA-03 dependency cycle among AS-DATA-002, AS-SRC-001, and AS-API-002 remains unresolved in the tracker. AS-GOV-002's proposed refinement is not itself an accepted dependency change.

## Work that can proceed as review or preparation

These are nonbinding design/review tasks and do not select unresolved behavior:

| Canonical ticket/work area | Safe work now | Boundary |
|---|---|---|
| AS-TECH-01 | Review the documented route, tab, source, PDF.js, GROBID, AI provider, identity, and service architecture. | Documents remain proposals; the Atomic tab is not implemented. |
| AS-SRC-001 | Inventory existing mapping fixtures and prepare non-mutating cases for exact quote/offset round-trip, Unicode, segmentation boundaries, page spans, missing/ambiguous anchors, and source changes. | No production indexer implementation until GOV-002, DATA-001, source-unit contract, OD-10/11/14 outcomes, and accepted dependencies. |
| AS-API-001 | Draft API/state contract alternatives and router composition boundary; compare with existing API/service patterns. | No route code until GOV-002, DATA-001, and the approved API/state contract. |
| AS-DATA-001 | Compare additive logical persistence alternatives, lineage/version constraints, backup/rollback, and access requirements. | Design review only. No DDL or migration until decisions and model are approved. |
| AS-QA-004 | Inventory source-integrity and stale-state fixtures and expected behaviors. | Test design can proceed; implementation and test claims wait for approved source contract and code. |
| AS-UI-001 / AS-UI-002 | Refine the integration design for a visible Atomic Sentences tab on the existing paper detail Analysis page, reuse of the existing PDF.js viewer, responsive layout, and source/AI distinction. | No UI behavior is final; API readiness/access dependencies remain. Align backlog acceptance wording with the existing-page tab objective before implementation. |
| AS-QA-001 / AS-QA-002 | Review gold-set and metric design alternatives; document data access and evaluation inputs. | Do not label research data or finalize metrics before OD-15/16 Research Lead actions and the approved annotation contract. |

## Implementation-ticket assessment

| Ticket | Current implementation status | Blocking conditions |
|---|---|---|
| AS-DATA-001 | BLOCKED — design approval ticket, not implementation authorization | GOV-002 approval; selected outcomes formalized; OD-09/10/11/12/13/14 outcomes; reviewed logical model; applicable Research Lead actions. No migration in this task. |
| AS-DATA-002 | BLOCKED — TECHNICAL DEPENDENCY | DATA-001; approved source-unit/version contract; AS-SRC-001 output contract; OD-10/11/14; existing API-002 dependency cycle must be formally refined. |
| AS-SRC-001 | BLOCKED — TECHNICAL DEPENDENCY | GOV-002 and DATA-001; OD-10/11/14; validated mapping fixtures; current QA-03 dependencies DATA-002/API-002; Backlog Owner acceptance of any cycle-breaking change. |
| AS-API-001 | BLOCKED — PRODUCT DECISION / TECHNICAL DEPENDENCY | GOV-002; DATA-001; approved API/state contract; current ticket dependencies. Shared source/readiness semantics must be agreed before integration contracts diverge. |
| AS-API-002 | BLOCKED — TECHNICAL DEPENDENCY | API-001, DATA-002, OD-11/14; structured-paper-JSON and existing paper/PDF/mapping readiness behavior must be contracted. |
| AS-UI-001 | BLOCKED — PRODUCT DECISION / TECHNICAL DEPENDENCY | API-001/002 readiness APIs, approved access/language policy, and accepted ticket wording for the in-page tab. The existing QA-03 ticket's paper-picker wording does not fully spell out the AS-TECH-01 per-paper tab objective. |
| AS-UI-002 / AS-UI-003 | BLOCKED — PRODUCT / RESEARCH / TECHNICAL DEPENDENCY | Source and AI outputs, PDF anchor behavior, stable state contract, trusted reviewer identity, lifecycle decisions, SPS resolution where surfaced, and Research Lead-dependent review policy. |
| AS-QA-001 | BLOCKED — RESEARCH REVIEW | OD-15 and OD-11; source permissions, approved annotation guide, annotators/adjudicator, and paper-level split. |
| AS-QA-002 | BLOCKED — RESEARCH REVIEW / PRODUCT DECISION | OD-16/17 and approved evaluation contract; Research Lead metric/denominator review. |
| AS-AI-001–004 and AS-QA-003 | BLOCKED — RESEARCH REVIEW / PRODUCT DECISION / TECHNICAL DEPENDENCY | Approved annotation/language/source contracts and gold-set/evaluation prerequisites; no AI-to-VERIFIED path. |
| AS-LIB-001/002 | BLOCKED — PRODUCT DECISION / TECHNICAL DEPENDENCY | OD-01/09/12/13/14 as applicable; approved cross-paper visibility, reviewer authorization, SPS fields, source freshness, JSON/CSV contracts. |

## AS-SRC-001 and AS-API-001 relationship

The current QA-03 graph remains in force, so neither ticket can begin implementation now. The AS-GOV-002 document proposes that the source index can be a deterministic transformation over validated fixtures and that an isolated API router can be composed independently. That proposal has not been accepted by the Backlog Owner and cannot be treated as a dependency change.

If the Backlog Owner accepts a non-circular graph, the two code tasks do not need to depend on each other's implementation. They do require a shared, reviewed contract before parallel work that is intended to integrate:

- source and paper identity, hash/version fields, exact offset units, stable source-unit identifiers, and absent/ambiguous page-anchor semantics;
- API readiness/status/error shapes and versioning; and
- which contract is owned by AS-DATA-001, AS-SRC-001, and AS-API-001/002.

Once the shared boundary is approved, AS-SRC-001 can implement the pure source-index transformation against validated fixtures while AS-API-001 implements isolated routing/schema composition. This is conditional parallelism, not current readiness. Do not remove DATA-002/API-002 edges until the Backlog Owner records the accepted refinement against the existing canonical IDs.

## Earliest implementation eligibility

**Currently:** None. No implementation ticket is READY FOR IMPLEMENTATION.

**Conditional earliest bounded source implementation:** AS-SRC-001, after:

1. Product outcomes are explicitly approved and entered in the controlled register; required Research Lead reviews/approvals for OD-03/09/15/16 are completed or the decision authority formally clarifies the required review boundary.
2. AS-GOV-002 is versioned as an approved, internally consistent contract.
3. AS-DATA-001 approves the additive logical model and source-unit boundary.
4. The shared source/API contract and validated mapping fixtures are reviewed.
5. The Backlog Owner formally accepts a non-circular dependency refinement.

AS-API-001 may then proceed in parallel only after its API/state contract and the common source/readiness semantics are approved. AS-DATA-002 and AS-API-002 remain later integration work under the accepted graph.

## Visible Atomic Sentences tab

The technical proposal places **Atomic Sentences** in the existing `analysis.html` tab strip on the paper detail route, for example `/analysis/paper/{paper_id}?from=/analysis`; it reuses the selected paper and existing PDF.js viewer. It is not a separate application. This is a documented UI target, not an implemented feature. Before code starts, align AS-UI-001's QA-03 acceptance wording (currently entry point/paper picker) with this per-paper tab objective while preserving its canonical ID and dependencies.
