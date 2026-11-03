# QA-05 Implementation Readiness Reassessment

**Requirements baseline:** NOT ESTABLISHED.  
**Decision status:** 17 OPEN; 0 approved.
**Canonical implementation tickets READY FOR IMPLEMENTATION:** 0.
**MVP scope and canonical ticket IDs:** Unchanged.

## Readiness categories

- **READY FOR REVIEW:** Nonbinding analysis or design alternatives can be reviewed by the relevant owner. This status does not approve a contract or unblock implementation.
- **BLOCKED:** The canonical implementation ticket depends on unresolved Product Owner or Research Lead decisions, an approved contract, or a blocked predecessor.
- **COMPLETE (read-only):** Repository inspection was performed without changing application behavior or data.

## Technical preparation that can proceed

| Preparatory activity | Status | Safe scope | Boundary |
|---|---|---|---|
| Existing architecture and persistence inventory | COMPLETE (read-only) | FastAPI and SQLite/PaperStore are present. Existing tables cover papers, analyses, source sections, propositions, and analysis review; GROBID validation checks the PDF hash and exact section/paragraph offsets. | Inspected files contain no Atomic-specific tables or routes. Review attribution defaults to `local-user`; inspection does not imply Atomic tables, routes, or workflows exist. |
| PDF/GROBID source-integration analysis | READY FOR REVIEW | Document current PDF hash, mapping, offset, page, and partial-source behavior; list fixtures and failure cases needed for a later source-index contract. | Do not select sentence segmentation, language eligibility, evidence cardinality, or stale-source policy. |
| AS-DATA-001 persistence alternatives | READY FOR REVIEW | Draft additive logical-model alternatives and a decision-to-field impact matrix for lifecycle, identity, SPS, evidence links, language/tokenizer, origins, and source versions. | Keep alternatives conditional. Do not select a schema, change existing table meanings, or write migrations. AS-DATA-001 remains BLOCKED as a canonical design/approval ticket. |
| API and service-boundary alternatives | READY FOR REVIEW | Sketch module/service boundaries, readiness responses, run lifecycle options, and review/library invariants against existing app patterns. | Request/response semantics and routes remain draft until the data and product contracts are approved; no application code. |
| Frontend component architecture | READY FOR REVIEW | Map possible paper picker, source viewer, candidate queue, review, and library components to current UI conventions. | No workflow actions, labels, permissions, or visible status semantics are approved. |
| AI pipeline architecture | READY FOR REVIEW | Document candidate extraction, atomization, context, deterministic checks, advisory precheck, provenance, and failure boundaries as alternatives. | Do not adopt output schemas or launch prompts, generate product records, or claim evaluated performance before the annotation and source contracts are approved. |
| Technical feasibility review | READY FOR REVIEW | Technical Lead may assess span storage/display, tokenization/segmentation, trusted identity options, stale-source invalidation, SPS representation, and benchmark conditions. | Feasibility findings inform owners; they do not approve product or research policy. Role assignment/authority remains to be confirmed by the team. |
| AS-GOV-001 decision review | READY FOR REVIEW | Product Owner reviews all 17 options; Research Lead reviews the requested research/evaluation items. | The developer's QA-02 preferences are proposals only. AS-OD-09/15/16 stay OPEN pending Research Lead review and Product Owner approval. |

These activities are preparation for review and do not alter the QA-03 backlog status of the canonical tickets.

## Canonical implementation readiness

| Workstream / canonical tickets | Status | Blocking decisions or prerequisites |
|---|---|---|
| Approved requirements contract — AS-GOV-002 | BLOCKED | Product Owner outcomes for AS-OD-01–17; required Research Lead review/co-approval; cross-decision consistency review and versioned baseline. |
| Persistence design — AS-DATA-001; source/run records — AS-DATA-002/003 | BLOCKED | Reviewer policy/identity, lifecycle, role/origin, SPS, evidence cardinality, language/tokenizer, stale-source rules, and the QA-03 governance/evaluation gate. |
| Canonical source indexing — AS-SRC-001 | BLOCKED | Approved source representation, language/segmentation boundary, evidence-span contract, and PDF/mapping/segmenter identity and invalidation policy. |
| Backend readiness, orchestration, and review — AS-API-001–004 | BLOCKED | Approved API/data contracts; current source snapshot; run lifecycle; trusted reviewer identity; authorized transitions and stale-source rules. |
| Candidate extraction, atomization, context, and precheck — AS-AI-001–004 | BLOCKED | Approved role/origin rules, evidence/context links, language/tokenizer, source versioning, output contract, and evaluation requirements before validated release. |
| UI, verification, library, and export — AS-UI-001–003; AS-LIB-001/002 | BLOCKED | Approved workflow, identity/authorization, review lifecycle, SPS fields, source eligibility, library semantics, origin treatment, and export contract. |
| Gold set, evaluation, regression, and pilot — AS-QA-001–006 | BLOCKED | Research/Product Owner choices for launch sample, annotation and adjudication, metric definitions/denominators, target status, and approved MVP contract. |

## Backlog status preservation

- **AS-GOV-001 — Review and record product decisions:** READY FOR REVIEW.
- **Other 27 canonical tickets:** BLOCKED.
- **READY FOR IMPLEMENTATION:** 0 tickets.

This reassessment does not change ticket IDs, ticket states, or the MVP proposal. Drafting technical alternatives does not make the corresponding implementation ticket ready.

## Next practical development task

Prepare a reviewable, options-based technical note for AS-DATA-001: show alternative additive data boundaries, map each unresolved field to its AS-OD decision, and record SQLite/PaperStore compatibility, integrity, and rollback considerations. Keep the note conditional and send it for Technical Lead and Product Owner review. In parallel, the Product Owner/Research Lead must complete AS-GOV-001. Do not start schema approval, migrations, or application implementation until those gates are met.
