# AS-GOV-003 — Developer Approval Worksheet

**Purpose:** Let the delegated Atomic Sentence decision-maker approve, reject, or request changes to each canonical decision. This worksheet is not itself an approval. No boxes have been selected.

The current task context confirms delegated Product Owner authority for Atomic Sentence requirements only. AS-OD-01–05 are reported as selected in prior discussion; their options below are carried as selections, not formal approvals. AS-OD-06–17 remain proposals unless a prior explicit selection is recorded. The QA-04 register requires an explicit outcome, approver identity, and timestamp before marking a decision APPROVED. No name, authenticated identity, or approval time is supplied here.

For each row, select exactly one: **approve**, **reject**, or **request changes**. For OD-03, 09, 15, and 16, the required Research Lead actions remain separate from the developer's Product Owner decision. OD-03's Research Lead review is required by the review history; whether it is co-approval remains unresolved.

## Decision worksheet

| ID | Current selected/proposed outcome | Why this is recommended | Research Lead involvement | Current status | Developer action |
|---|---|---|---|---|---|
| AS-OD-01 | One trusted operational verifier per item; a defined high-risk/disputed subset may receive a second review; gold-set annotation remains two annotators plus adjudication. | Separates operational publication quorum from research gold-set protocol. | Consultation on that separation; no co-approval rule established. | SELECTED; not APPROVED | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-02 | Reject with reason and regenerate as a linked new ID; no separate revision state initially. | Follows PRD immutability and preserves lineage. | None specified for MVP decision. | SELECTED; not APPROVED | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-03 | Keep four PRD roles, map by function, keep evidence origin separate, flag ambiguous cases. | Preserves the PRD enums while making borderline mappings reviewable. | **Role-mapping review required.** Co-approval is not established. | SELECTED; Research Lead review pending | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-04 | Preserve uncertainty, modality, negation, and scope semantically; defer separate classifier, cue, and cue-scope outputs from MVP. | Keeps PRD meaning preservation and resolves the QA-01/QA-02 scope divergence as a product choice. | No current co-approval requirement established; consult if future linguistic tasks enter scope. | SELECTED; not APPROVED | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-05 | Defer separate sentence-uncertainty labels; if added later, distinguish uncertain meaning from unresolved annotation. | Avoids conflating a research label with annotation failure. | Needed if the research label is brought into scope; not required for the proposed deferral. | SELECTED; not APPROVED | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-06 | Defer Hyland stance/engagement from MVP; if later scoped, pilot contextual multi-label spans with an optional primary function. | Keeps taxonomy and evaluation work outside the MVP boundary. | Consultation for any future taxonomy; no co-approval rule established. | OPEN; pending developer confirmation | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-07 | Defer metadiscourse annotation from MVP. | Avoids adding an unapproved label family and its research protocol. | Consultation if reconsidered. | OPEN; pending developer confirmation | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-08 | Defer lens and method with metadiscourse; if later included, decide interactive/reflexive separately from thin/thick. | Prevents silently selecting a framework for a deferred feature. | Research advice for future inclusion; final future authority unspecified. | OPEN; pending developer confirmation | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-09 | Obtain Appendix 1 or use five generic rubric-versioned review slots/notes and optional human-entered total; invent no dimensions, weights, or automatic score. | Preserves PRD FR-10 without fabricating the absent SPS rubric. | **Review/approval required** for the rubric/fallback; joint-signoff rule should be confirmed. | OPEN; developer decision and Research Lead review pending | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-10 | Allow multiple exact evidence spans; distinguish primary claim support from supporting context. | Supports source-grounded context while preserving exact evidence links. | None specified. | OPEN; pending developer confirmation | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-11 | English-only first pilot; use the PRD whitespace word-count convention, punctuation rule, and tokenizer version; mark other languages unsupported until specified and evaluated. | Makes the 25-word rule implementable without claiming multilingual validation. | Corpus-language consultation requested. | OPEN; pending developer confirmation | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-12 | Require a server-trusted reviewer identifier and authorization; do not trust a client-entered display name. | Makes verification and audit attribution enforceable. | None specified. | OPEN; pending developer confirmation | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-13 | Include focal-paper reports of prior work in the verified library only with visible REPORTED_PRIOR_WORK/citation markers; filter them and exclude them from primary-findings views. | Preserves reported evidence without presenting it as a focal-paper result or validation of the cited study. | Consultation on downstream evidence interpretation; no co-approval rule established. | OPEN; pending developer confirmation | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-14 | Bind to PDF, mapping, text, and segmenter identity; stale affected records on change, preserve history, and require new version plus fresh review for re-anchoring. | Protects evidence integrity and review history. | None specified. | OPEN; pending developer confirmation | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-15 | Stratified launch-domain gold set; two independent annotators plus adjudication; paper-level development/test split; sample size confirmed with Research Lead. | Supports interpretable evaluation without paper leakage. | **Review/approval required** for domain, protocol, staffing, and sample size. | OPEN; developer decision and Research Lead review pending | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-16 | Keep PRD 100% process gates; define denominators before evaluation; set model thresholds after pilot; no thresholds for deferred label families. | Separates fixed process gates from unvalidated model targets. | **Review/approval required** for metrics, denominators, and protocol. | OPEN; developer decision and Research Lead review pending | ☐ Approve ☐ Reject ☐ Change |
| AS-OD-17 | Treat numeric model targets and runtime goal as provisional pilot measurements, not release gates until definitions and applicability are approved; retain separate 100% process gates. | Avoids treating aspirational targets as validated release criteria. | Metric interpretation review requested; Technical Lead should define benchmark conditions. | OPEN; pending developer confirmation | ☐ Approve ☐ Reject ☐ Change |

## Approval record fields

Complete these fields only when an explicit decision is made. Record the decision-maker's own identity and time; do not let the transcriber infer them.

| Field | Entry |
|---|---|
| Decision ID(s) |  |
| Action (approve / reject / change) |  |
| Exact selected outcome or replacement wording |  |
| Developer identity / role |  |
| Delegation basis and scope | Product Owner delegation for Atomic Sentence module only |
| Decision timestamp and timezone |  |
| Conditions / rationale |  |
| Research Lead action and identity (where required) |  |
| Research Lead timestamp and timezone (where required) |  |

## Follow-up after worksheet completion

Record each explicit outcome and any required Research Lead action in the controlled decision register. Reconcile QA-04/QA-05 only through a separately reviewed history-preserving update. Do not infer APPROVED from a checked recommendation unless the decision-maker's explicit action and required evidence are recorded.
