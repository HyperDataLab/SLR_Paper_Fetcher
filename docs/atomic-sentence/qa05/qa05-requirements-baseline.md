# QA-05 Requirements Baseline Status

**Baseline status: NOT ESTABLISHED.**  
**Baseline version:** None.  
**Approved decisions:** 0 of 17.  
**Decision register status:** All AS-OD-01–17 remain OPEN.

The developer's chat preference is to carry the QA-02 recommended options forward as proposals for Product Owner review. It is not an authorized decision. The developer explicitly requested that AS-OD-09, AS-OD-15, and AS-OD-16 remain OPEN pending Research Lead review.

## Why no baseline can be established

QA-05 requires explicit, valid human approvals for mandatory decisions and a consistent approved decision set. The QA-04 register contains no authorized decision outcome, approver identity, approval authority evidence, approval timestamp, or recorded conditions. The questionnaire contains blank selections. QA-02 recommendations and the developer's stated preference are proposals, not human approvals by the Product Owner or Research Lead.

Accordingly, this document does not declare any QA-02 recommendation or PRD implementation interpretation to be an approved product baseline. It also does not mark any requirement as formally deferred.

## Approval inventory

| Baseline category | Current result |
|---|---|
| Approved product requirements from AS-OD decisions | None |
| Approved research/evaluation requirements from AS-OD decisions | None |
| Requirements formally deferred by an authorized approver | None |
| Developer preferences recorded for Product Owner review | QA-02 recommended options for AS-OD-01–17; not approved |
| Unresolved decisions | AS-OD-01–AS-OD-17 |
| Approved baseline version/date | None |
| Approval provenance | None |

## Candidate requirements to carry forward for approver review

These are source requirements or draft-contract statements to consider when a baseline is prepared. They are **not** declared approved by this document.

- The PRD lists P0 requirements FR-01–FR-13, including source segmentation, candidate detection, atomization, <=25-word rule, context completion, four roles, evidence/provenance, advisory precheck, human verification, immutable rejection/regeneration, quality-review/SPS fields, verified-only search/library, audit trail, and JSON/CSV export.
- The PRD requires preserving uncertainty, modality, negation, quantities, comparisons, units, population, and scope during atomization. This is distinct from a standalone sentence classifier or hedge cue/scope subsystem.
- The QA-02 MVP proposal recommends deferring sentence-level uncertainty classification, full hedge cue/scope detection, stance/engagement, metadiscourse, multilingual processing, OCR, and automated multi-review adjudication. None is formally DEFERRED until an authorized human records that outcome.
- The SPS dimensions/weights remain unavailable. No official score can be derived from invented values.
- The existing application provides paper/PDF/GROBID/AI/review infrastructure, but the Atomic-specific schema, pipeline, and library are not implemented.

## Proposed mapping after approval

This mapping is a planning cross-reference only. It does not unblock or approve tickets.

| Decision group | Canonical backlog tickets likely affected |
|---|---|
| Product decisions and approved specifications | AS-GOV-001, AS-GOV-002 |
| Gold set and evaluation protocol | AS-QA-001, AS-QA-002, AS-QA-003 |
| Persistence, source versions, and evidence | AS-DATA-001, AS-DATA-002, AS-DATA-003, AS-SRC-001 |
| Backend readiness, orchestration, review invariants | AS-API-001 through AS-API-004 |
| Extraction, atomization, context, precheck | AS-AI-001 through AS-AI-004 |
| Reviewer UI and verified library/export | AS-UI-001 through AS-UI-003, AS-LIB-001, AS-LIB-002 |
| Regression and pilot acceptance | AS-QA-004 through AS-QA-006 |

## Requirements baseline gate

A future baseline may be established only after:

1. Every mandatory decision has a valid human outcome and required co-approval.
2. Product scope, role/origin policy, evidence cardinality, language/tokenizer, identity, lifecycle, SPS, and stale-source rules are explicit.
3. Conditional decisions are consistent (including OD-04/05, OD-07/08, OD-01/15, and OD-15/16/17).
4. Research/evaluation choices are recorded with an approved gold-set protocol and metric definitions.
5. A baseline version, date, approver identities, conditions, and ticket mapping are recorded.

Until then, AS-GOV-002 cannot complete; no ticket may rely on a baseline that does not exist.

Read-only inspection and nonbinding design alternatives may proceed for review. They do not establish the baseline or change canonical backlog statuses.
