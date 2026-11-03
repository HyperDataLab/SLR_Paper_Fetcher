# QA-04 Review Report — Product Decision Approval Preparation

**Status:** Approval package prepared; no decision was approved.  
**Decision count:** 17 prepared, 0 approved, 17 OPEN.  
**DB-01:** Still blocked.

## What was reviewed

- Original Atomic Sentence PRD v1.0.
- All four QA-01 draft specifications and the AS-OD-01–17 open-decision register.
- QA-02 product decision proposal, MVP scope, implementation readiness, and review report.
- QA-03 task ID reconciliation, dependency map, development backlog, implementation roadmap, and review report.
- The existing repository implementation plan and relevant current architecture/code facts already established by QA-02/03. Draft architecture/data-model proposals were not treated as implemented features.

The QA-02 research review found CoNLL-2010 and Hyland 2005 PDFs readable and relevant; the metadiscourse collection's relevant introduction and Ädel sections were reviewed, not the complete 226-page volume chapter by chapter. The cited JMIR paper and detailed SPS Appendix 1 remain unavailable in the supplied research folder.

## What was created

All five QA-04 deliverables are under docs/atomic-sentence/qa04/:

1. [Decision approval register](qa04-decision-approval-register.md)
2. [Approval questionnaire](qa04-approval-questionnaire.md)
3. [Approval responsibility matrix](qa04-approval-responsibility-matrix.md)
4. [Approval dependency analysis](qa04-approval-dependency-analysis.md)
5. [This review report](qa04-review-report.md)

## Decision and approval counts

- **Prepared:** AS-OD-01 through AS-OD-17 (17 total).
- **APPROVED:** 0.
- **OPEN:** 17.
- **REJECTED / NEEDS REVISION / DEFERRED:** 0.
- **Decision dates and approver identities:** None recorded.

Each register entry includes the question, QA-02 recommendation, alternatives and consequences, rationale, proposed approver routing, dependent canonical tickets, status, blank approval date/identity, and notes/conditions field.

## Approval responsibility summary

- **Product Owner approval requested:** All 17 decisions. This is the approval path requested by QA-02 and QA-04; the named person's identity must still be confirmed.
- **Product Owner and Research Lead approval requested:** AS-OD-09 (SPS fallback/rubric), AS-OD-15 (gold set), AS-OD-16 (metrics/evaluation). Formal joint-signature details need confirmation.
- **Research Lead review requested:** AS-OD-03 role-mapping examples; the prior documents do not establish whether this is formal co-approval.
- **Backlog Owner acceptance:** Adopt the proposed AS-AREA-### namespace and crosswalk. This is not one of the 17 product decisions; the responsible person's authority needs confirmation.
- **Technical Lead confirmation:** Feasibility/impact review for evidence cardinality, tokenizer/segmentation, reviewer identity integration, source-version invalidation, and runtime measurement. Technical review does not approve product policy; role authority needs confirmation.
- **Unclear authority:** The responsibility matrix explicitly marks uncertain role assignments as NEEDS OWNER CONFIRMATION. This is a responsibility note, not a decision status.

## Critical blockers

- **DB-01:** Blocked until schema-affecting choices are explicit, especially reviewer policy/identity, lifecycle, four-role mapping, SPS handling, evidence cardinality, language/tokenizer, and stale-source behavior. QA-03 M1 also requires the evaluation/gold-set protocol and target status before the DB-01 milestone.
- **Canonical source index:** Blocked on source/evidence representation, language/segmentation, and source-version invalidation.
- **Extraction/atomization:** Blocked on role/origin guidance, evidence links, language/word count, uncertainty-preservation scope, and gold-set contract for validated release.
- **Context/precheck:** Blocked on item/version lineage, evidence cardinality, language/length rules, and stale behavior.
- **Human verification/library:** Blocked on reviewer quorum and trusted identity, lifecycle, SPS handling, evidence display, origin behavior, and stale-source policy.
- **Gold-set construction/evaluation:** Blocked on approved annotation scope, launch domain, sampling/adjudication, metric definitions, and target status.

Full stage-by-stage dependencies and decisions that can be explicitly deferred without changing MVP are in [the dependency analysis](qa04-approval-dependency-analysis.md).

## MVP scope and existing IDs

The MVP scope has not changed. QA-02's recommendations remain proposals; no deferred capability was silently removed or promoted. Semantic preservation of uncertainty remains required, while sentence uncertainty classification, hedge cue/scope extraction, stance/engagement, and metadiscourse remain separately deferrable decisions.

Canonical ticket IDs and the QA-03 crosswalk are unchanged. No backlog ticket was marked READY FOR IMPLEMENTATION. The register, questionnaire, and responsibility matrix do not alter AS-GOV-001's READY FOR REVIEW status or the 27 BLOCKED tickets.

## Database/code change confirmation

Only the five QA-04 approval-preparation documents in docs/atomic-sentence/qa04/ were created. No application code, database schema, migrations, routes, prompts, dependencies, existing QA-01/02/03 documents, canonical ticket IDs, or .env file were changed.

## Exact human actions required

1. **Product Owner:** Confirm your identity/authority in the approval record, then answer each AS-OD-01–17 in the questionnaire with a selected option or precise revision request.
2. **Research Lead:** Confirm whether you are a required co-approver for AS-OD-09, AS-OD-15, and AS-OD-16; review AS-OD-03 role-mapping examples; confirm gold-set/evaluation choices.
3. **Product Owner and Research Lead:** Resolve AS-OD-09 by obtaining Appendix 1 or explicitly approving a manual, rubric-versioned fallback without invented dimensions or weights.
4. **Backlog Owner:** Confirm acceptance or request changes to the AS-AREA-### namespace and historical crosswalk.
5. **Technical Lead:** Confirm feasibility implications for evidence links, tokenization/segmentation, identity, source-version invalidation, and the runtime benchmark; do not substitute technical confirmation for product approval.
6. **After approvals:** Update the register with decision ID, selected option, approver identity, timestamp with timezone, conditions/rationale, and status. Then version the approved requirements contract. DB-01 remains blocked until this is complete.
