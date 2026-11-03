# AS-GOV-003 — Atomic Sentence Decision Register

**Prepared:** 2026-11-03
**Register status:** READY FOR REVIEW
**Approval status:** 0 APPROVED; AS-OD-01–05 are recorded as SELECTED; all remaining outcomes are OPEN or pending required review.
**Scope:** Atomic Sentence module only. Delegated Product Owner authority does not extend to the rest of SLR_Paper_Fetcher.

## Authority and evidence assessment

The current task context explicitly confirms that the developer has delegated Product Owner authority for requirements within Atomic Sentence. This is accepted here as the authority basis for reviewing and deciding these module requirements. It does not establish authority over project-wide behavior. The developer's name, authenticated identity, and approval timestamp were not supplied and are not inferred.

The current task context says AS-OD-01 through AS-OD-05 were explicitly selected in prior discussions. Their selected options are recorded below as the QA-04 recommended outcomes. Selection is not recorded as formal approval: QA-04 requires an explicit approval outcome, approver identity, and timestamp. The available context establishes delegated scope and selected options, but the formal approval fields are absent. No decision is marked APPROVED in this register.

AS-OD-06 through AS-OD-17 remain proposals pending developer confirmation unless an explicit selection is found. No item-specific selections for those decisions were found in the inspected project records. AS-OD-09, AS-OD-15, and AS-OD-16 also require the requested Research Lead review/approval. AS-OD-03 requires Research Lead role-mapping review; the records do not establish that this review is co-approval.

QA-04 and QA-05 are preserved as historical records. QA-04 records 17 OPEN and 0 APPROVED; QA-05 records no approved baseline. This register adds the new selection/delegation context without editing those prior records or backdating a status change.

## Status vocabulary

- **SELECTED:** The task context says this option was selected. It is not a formal approval record.
- **APPROVED:** A formally recorded authorized outcome meeting the applicable approval-evidence requirements. No decision currently has this status.
- **PENDING RESEARCH LEAD:** Required Research Lead review/approval has not been recorded. For AS-OD-03 this means review is pending; co-approval is not presumed.
- **OPEN:** No explicit selected outcome or complete approval record exists. For AS-OD-06–17, developer confirmation is still required.

## Decision register

### AS-OD-01 — Required number of human reviewers

- **Decision statement:** Is one authorized reviewer sufficient to publish a Verified Atomic Sentence, or do selected claims/roles require two independent reviews and adjudication?
- **Current proposed/selected outcome:** **SELECTED:** One trusted operational verifier per item, with a second review for an explicitly defined disputed/high-risk subset. Separately, use two independent annotators plus adjudication for the research gold set.
- **Evidence:** Prior-discussion selection as reported in the current task; QA-04 recommended option; AS-GOV-001 recommendation; PRD §§6, 12, 18; AS-GOV-002 baseline.
- **Approval authority/status:** Delegated Product Owner authority for the Atomic Sentence module is confirmed in the current task context. **SELECTED; not APPROVED** because QA-04 approval identity and timestamp are not recorded.
- **Remaining action:** Developer explicitly approve, reject, or revise the selected outcome in the worksheet. Keep operational quorum separate from gold-set annotation. No additional Research Lead approval is specified for the operational quorum.
- **Affected requirements/tickets/tests:** FR-08, FR-11; AT-08, AT-12. Tickets: AS-GOV-002, AS-DATA-003, AS-API-004, AS-UI-003, AS-LIB-001, AS-QA-001.

### AS-OD-02 — Separate request-revision action

- **Decision statement:** Should reviewers have a nonterminal REQUEST_REVISION action/state, or should an unsatisfactory candidate be rejected with a reason and regenerated as a new ID?
- **Current proposed/selected outcome:** **SELECTED:** Reject with a reason; regenerate as a new candidate ID linked to the rejected item. Do not add a separate revision state initially.
- **Evidence:** Prior-discussion selection as reported in the current task; QA-04 recommended option; PRD §§6, 8, 9.2; AS-GOV-002 baseline and AT-09 mapping.
- **Approval authority/status:** Delegated Product Owner authority is confirmed within module scope. **SELECTED; not APPROVED** because the formal QA-04 identity/time fields are absent.
- **Remaining action:** Developer explicitly approve, reject, or revise in the worksheet; then align lifecycle, API, and UI contracts. Technical state/API review is feasibility input only.
- **Affected requirements/tickets/tests:** FR-09, BR-07/09; AT-09. Tickets: AS-GOV-002, AS-DATA-003, AS-API-004, AS-AI-003, AS-UI-003.

### AS-OD-03 — Mapping content kinds to the four functional roles

- **Decision statement:** How should definitions, hypotheses, author interpretations, and conclusions map to BACKGROUND, METHOD, FINDING, or LIMITATION?
- **Current proposed/selected outcome:** **SELECTED:** Keep the four PRD roles only and map by function; keep evidence origin separate. Use a review flag when function is ambiguous.
- **Evidence:** Prior-discussion selection as reported in the current task; QA-04 recommended option; PRD FR-05 and §6 P5; AS-GOV-002 role/origin requirements.
- **Approval authority/status:** Delegated Product Owner authority is confirmed within module scope. **SELECTED; PENDING RESEARCH LEAD review.** QA-02/04 request Research Lead review of the role-mapping guide. Whether that review is co-approval is not established and remains unspecified.
- **Remaining action:** Developer explicitly approve, reject, or revise in the worksheet. Research Lead reviews role-mapping examples and guidance. Do not infer a co-approval rule; record it only if the authority owner defines one.
- **Affected requirements/tickets/tests:** FR-05 and role/origin rules in BR-05. No dedicated role-mapping AT is identified in the AS-GOV-002 matrix; role examples belong in AS-QA-001/002. Tickets: AS-GOV-002, AS-QA-001/002, AS-AI-001/002, AS-LIB-001/002.

### AS-OD-04 — Hedge annotation scope for the product

- **Decision statement:** Must MVP preserve uncertainty during atomization only, or also output sentence labels, hedge cue spans, and cue-linked scope spans?
- **Current proposed/selected outcome:** **SELECTED:** Require semantic preservation of uncertainty, modality, negation, and scope in every MVP atom; defer the three separate annotation tasks.
- **Evidence:** Prior-discussion selection as reported in the current task; QA-04 recommendation; QA-01 broader conditional wording; QA-02/04 deferral recommendation; PRD §§6 and 8; AS-GOV-002 hedge divergence analysis.
- **Approval authority/status:** Delegated Product Owner authority is confirmed within module scope. **SELECTED; not APPROVED** because the formal QA-04 identity/time fields are absent. This choice determines MVP scope.
- **Remaining action:** Developer explicitly approve, reject, or revise in the worksheet. Preserve the PRD semantic-meaning rule regardless. If separate annotations are later selected, scope the separate AS-AI-005 / AS-QA-007 work with its own guide and evaluation; do not infer it into MVP.
- **Affected requirements/tickets/tests:** FR-03/07 and semantic-preservation rules; AT-02/03/04. Tickets: AS-GOV-002, AS-QA-001/002, AS-AI-002/004; AS-AI-005 only if advanced annotation is later approved.

### AS-OD-05 — Sentence uncertainty label semantics

- **Decision statement:** If a separate sentence uncertainty label is added, should it use a binary cue-presence rule, binary semantic judgment, or a third unresolved status?
- **Current proposed/selected outcome:** **SELECTED:** Defer this label from MVP. If later added, distinguish uncertain meaning from annotation-unresolved status.
- **Evidence:** Prior-discussion selection as reported in the current task; QA-04 recommendation; PRD does not define a sentence-level uncertainty class; AS-GOV-002 hedge analysis.
- **Approval authority/status:** Delegated Product Owner authority is confirmed within module scope. **SELECTED; not APPROVED** because the formal QA-04 identity/time fields are absent.
- **Remaining action:** Developer explicitly approve, reject, or revise in the worksheet. If a research label is later brought into scope, obtain the applicable Research Lead review then.
- **Affected requirements/tickets/tests:** No separate PRD P0 requirement or dedicated AT; uncertainty preservation under OD-04 remains. Tickets: AS-GOV-002; AS-AI-005 and AS-QA-007 only if later added.

### AS-OD-06 — Stance/engagement overlap policy

- **Decision statement:** If Hyland stance/engagement labels are included later, may one span receive multiple labels, and is a primary label required?
- **Current proposed outcome:** **PROPOSED:** Defer the taxonomy from MVP. If adopted later, pilot context-grounded multi-label spans with optional primary function.
- **Evidence:** QA-04 recommended option; QA-02/04 scope proposal; PRD P1/non-goal boundary as mapped in AS-GOV-002. No explicit selection found in project records.
- **Approval authority/status:** Delegated Product Owner authority applies within module scope. **OPEN — pending developer confirmation.** Research Lead consultation is recommended for any future taxonomy; no current co-approval rule is established.
- **Remaining action:** Developer approve, reject, or request changes in the worksheet. Any future inclusion requires separately reviewed research scope and evaluation.
- **Affected requirements/tickets/tests:** Outside MVP; no dedicated PRD FR or AT. Tickets: AS-GOV-002; AS-AI-005 / AS-QA-007 only if later included.

### AS-OD-07 — Metadiscourse in MVP scope

- **Decision statement:** Is metadiscourse annotation required in MVP, optional research analysis, or deferred from the first product release?
- **Current proposed outcome:** **PROPOSED:** Defer metadiscourse annotation from MVP.
- **Evidence:** QA-04 recommended option; QA-02/04 scope proposal; AS-GOV-002 MVP boundary. No explicit selection found in project records.
- **Approval authority/status:** Delegated Product Owner authority applies within module scope. **OPEN — pending developer confirmation.** Research consultation is recommended only if reconsidered.
- **Remaining action:** Developer approve, reject, or request changes in the worksheet. Do not add labels or taxonomy while open.
- **Affected requirements/tickets/tests:** Outside MVP; no dedicated PRD FR or AT. Tickets: AS-GOV-002; AS-AI-005 / AS-QA-007 only if later included.

### AS-OD-08 — Metadiscourse definition lens and analysis method

- **Decision statement:** If metadiscourse is later included, which definition lens and method should be used?
- **Current proposed outcome:** **PROPOSED:** Defer both choices with the feature. If later approved, choose and report interactive/reflexive and thin/thick as separate dimensions.
- **Evidence:** QA-04 recommended option; AS-GOV-002 MVP boundary. No explicit selection found in project records.
- **Approval authority/status:** Delegated Product Owner authority applies within module scope. **OPEN — pending developer confirmation.** Research Lead advice is recommended for future framework selection; final authority for that future work is unspecified.
- **Remaining action:** Developer approve deferral, reject, or request changes in the worksheet. Reopen lens/method only if the feature itself is later scoped.
- **Affected requirements/tickets/tests:** Outside MVP; no dedicated PRD FR or AT. Tickets: AS-GOV-002; AS-AI-005 / AS-QA-007 only if later included.

### AS-OD-09 — SPS dimensions and scoring

- **Decision statement:** How should the MVP satisfy PRD FR-10 quality-review/SPS fields while the detailed five dimensions and 0–9 scoring rules are unavailable?
- **Current proposed outcome:** **PROPOSED:** Retrieve Appendix 1 if possible. Otherwise, approve a manual, rubric-versioned fallback with five independent generic review slots/notes and an optional human-entered total; do not invent dimension names, weights, or automatic scoring.
- **Evidence:** QA-04 recommended option; PRD FR-10 and missing Appendix 1; QA-02/04 SPS analysis; AS-GOV-002 baseline and AT-14.
- **Approval authority/status:** Delegated Product Owner authority applies within module scope. **OPEN — pending developer confirmation; PENDING RESEARCH LEAD review/approval.** QA-02/04 request both; formal joint-signoff rule should be confirmed, not assumed.
- **Remaining action:** Developer chooses an outcome; Research Lead reviews/approves the rubric/fallback. Obtain Appendix 1 if available. Do not invent dimensions or weights.
- **Affected requirements/tickets/tests:** FR-10; AT-14. Tickets: AS-GOV-002, AS-DATA-001/003, AS-UI-003, AS-LIB-002, AS-QA-002.

### AS-OD-10 — Allowed source-to-AS evidence cardinality

- **Decision statement:** May one AS cite multiple exact spans/sentences, or must it cite one contiguous source quote?
- **Current proposed outcome:** **PROPOSED:** Allow multiple exact evidence spans; distinguish primary claim support from supporting context spans.
- **Evidence:** QA-04 recommended option; PRD evidence/context requirements; AS-GOV-002 source anchoring and matrix.
- **Approval authority/status:** Delegated Product Owner authority applies within module scope. **OPEN — pending developer confirmation.** Technical feasibility review is needed for storage/display, not product approval.
- **Remaining action:** Developer approve, reject, or request changes in the worksheet; Technical Lead confirms exact-span storage, PDF anchoring, and display feasibility.
- **Affected requirements/tickets/tests:** FR-06/08; AT-07 and AT-13 (source anchoring/version integrity). Tickets: AS-GOV-002, AS-DATA-001/002/003, AS-SRC-001, AS-AI-002/003/004, AS-UI-002, AS-LIB-001/002.

### AS-OD-11 — Languages and word-count tokenization

- **Decision statement:** Which source/output languages are supported at launch, and how will the 25-word maximum be enforced outside English?
- **Current proposed outcome:** **PROPOSED:** English-only source and AS output for the first pilot; implement the PRD whitespace-delimited English token rule, terminal punctuation convention, and tokenizer version. Flag other languages unsupported until separately specified and evaluated.
- **Evidence:** QA-04 recommended option; PRD BR-02 and language-related open questions; AS-GOV-002 language/tokenization analysis. No explicit selection found in project records.
- **Approval authority/status:** Delegated Product Owner authority applies within module scope. **OPEN — pending developer confirmation.** Technical Lead confirms tokenizer/segmenter feasibility; Research Lead corpus-language consultation is requested.
- **Remaining action:** Developer select launch language/tokenization behavior; technical feasibility review; research corpus-language input. Do not imply UTF-8 support means multilingual validation.
- **Affected requirements/tickets/tests:** BR-02; AT-06. Tickets: AS-GOV-002, AS-DATA-001/002, AS-API-002, AS-SRC-001, AS-AI-002, AS-LIB-002, AS-QA-001/002.

### AS-OD-12 — Reviewer identity and authorization

- **Decision statement:** Which trusted identity and permission source authorizes extraction, verification, rejection, and library access?
- **Current proposed outcome:** **PROPOSED:** Require a server-trusted reviewer identifier for every verification event. For a single-workspace pilot, use a named local operator only if the owner approves its accountability limits; do not trust a client-entered name as proof of authorization.
- **Evidence:** QA-04 recommended option; PRD authorization and audit requirements; AS-GOV-002 current identity-mechanism finding. No explicit selection found in project records.
- **Approval authority/status:** Delegated Product Owner authority applies within module scope. **OPEN — pending developer confirmation.** Technical/Security review must confirm the available trusted principal and authorization boundary.
- **Remaining action:** Developer choose policy; Technical/Security review the existing identity mechanism. Do not claim current local-user attribution authenticates a reviewer.
- **Affected requirements/tickets/tests:** FR-08/11/12; AT-08/12. Tickets: AS-GOV-002, AS-DATA-001/003, AS-API-001/004, AS-UI-003, AS-LIB-001/002, AS-QA-005/006.

### AS-OD-13 — Handling REPORTED_PRIOR_WORK

- **Decision statement:** Should verified reports of prior work be searchable/exportable with a warning, separated by filter, excluded from trusted retrieval, or require review of the cited primary paper?
- **Current proposed outcome:** **PROPOSED:** Include in the general verified library only as a verified report from the focal paper, with a prominent REPORTED_PRIOR_WORK label and citation marker; allow origin filters and exclude it from primary-findings views.
- **Evidence:** QA-04 recommended option; PRD role/origin and BR-08; AS-GOV-002 cross-paper library/export analysis. No explicit selection found in project records.
- **Approval authority/status:** Delegated Product Owner authority applies within module scope. **OPEN — pending developer confirmation.** Research Lead consultation is recommended on downstream evidence interpretation; co-approval is not specified.
- **Remaining action:** Developer approve, reject, or request changes in the worksheet. Preserve the distinction between a focal-paper report and validation of the cited primary paper.
- **Affected requirements/tickets/tests:** FR-05/11/13, BR-08; AT-10/12. Tickets: AS-GOV-002, AS-DATA-003, AS-API-004, AS-AI-001, AS-LIB-001/002.

### AS-OD-14 — Stale source and supersession policy

- **Decision statement:** What happens when PDF, mapping, page alignment, text representation, or segmentation changes, and may an existing verified item be re-anchored in place?
- **Current proposed outcome:** **PROPOSED:** Treat dependent items as stale when source/mapping/segmenter identity changes; block current verification/publication; preserve old records historically; create a new candidate/version and fresh verification for re-anchoring.
- **Evidence:** QA-04 recommended option; PRD checksum, immutable verification and supersession requirements; AS-GOV-002 anchor/version analysis. No explicit selection found in project records.
- **Approval authority/status:** Delegated Product Owner authority applies within module scope. **OPEN — pending developer confirmation.** Technical Lead confirms source-version and invalidation feasibility.
- **Remaining action:** Developer approve, reject, or request changes in the worksheet; technical owner documents hash/version and stale transitions.
- **Affected requirements/tickets/tests:** FR-06/08/09/11/12; AT-07/11/13. Tickets: AS-GOV-002, AS-DATA-001/002/003, AS-SRC-001, AS-API-002/004, AS-AI-004, AS-LIB-001/002, AS-QA-004.

### AS-OD-15 — Gold-set composition and adjudication protocol

- **Decision statement:** Which domain, paper/section sample, source qualities, sample size, and annotator/adjudicator roles will define the pilot gold set?
- **Current proposed outcome:** **PROPOSED:** Use a stratified sample from the intended launch domain, with two independent annotators and adjudication; split development/test by paper. Confirm sample size with the Research Lead.
- **Evidence:** QA-04 recommended option; PRD §12; QA-02/04 research approval routing; AS-GOV-002 evaluation baseline. No explicit selection found in project records.
- **Approval authority/status:** Delegated Product Owner authority applies within module scope. **OPEN — pending developer confirmation; PENDING RESEARCH LEAD review/approval.** Both are requested; confirm formal joint-signoff details.
- **Remaining action:** Developer selects scope/staffing proposal; Research Lead reviews domain, sample, protocol and sample size. Do not use unadjudicated examples as gold labels.
- **Affected requirements/tickets/tests:** PRD §12 evaluation of pipeline FR-01–FR-10; AT-01–AT-14 are candidate scenario coverage, not a claim that all are mandatory gold-set strata. Tickets: AS-GOV-002, AS-QA-001/002/003/006, AS-AI-001/002/003/004.

### AS-OD-16 — Acceptance thresholds for language tasks

- **Decision statement:** Which metric thresholds and denominators govern candidate extraction, atomization, support, context completion, provenance, and reviewer agreement?
- **Current proposed outcome:** **PROPOSED:** Keep PRD's 100% source traceability, human verification coverage, and length compliance as process gates; define metric denominators before evaluation; set model thresholds after the pilot. Do not set thresholds for deferred label families.
- **Evidence:** QA-04 recommended option; PRD §§12/14; QA-02/04 research approval routing; AS-GOV-002 metrics and release-gate mapping. No explicit selection found in project records.
- **Approval authority/status:** Delegated Product Owner authority applies within module scope. **OPEN — pending developer confirmation; PENDING RESEARCH LEAD review/approval** for metric definitions, denominators, and protocol. Formal joint-signoff details remain to be confirmed.
- **Remaining action:** Developer decides which requirements are release gates; Research Lead reviews metrics/denominators/protocol. Keep numeric model thresholds provisional until pilot evidence exists.
- **Affected requirements/tickets/tests:** PRD §§12/14; AT-01–AT-14 as evaluation scenarios. Tickets: AS-GOV-002, AS-QA-001/002/003/006, AS-AI-001/002/004.

### AS-OD-17 — Approval status of PRD targets and runtime benchmark

- **Decision statement:** Should the PRD's ≥90% support precision, ≥80% candidate recall, ≥90% atomicity, ≥99% numeric faithfulness, and 5,000-word/two-minute goal be hard release gates?
- **Current proposed outcome:** **PROPOSED:** Measure them as provisional pilot targets and benchmark observations; require explicit approval before making them mandatory gates. Retain the separate 100% PRD process gates.
- **Evidence:** QA-04 recommended option; PRD §12 initial targets/runtime benchmark; QA-02/04; AS-GOV-002 pilot-versus-gate analysis. No explicit selection found in project records.
- **Approval authority/status:** Delegated Product Owner authority applies within module scope. **OPEN — pending developer confirmation.** Research Lead metric review and Technical Lead benchmark feasibility input are requested; neither is assumed to be co-approval.
- **Remaining action:** Developer decide release-gate status; Research Lead reviews metric interpretation; Technical Lead defines measurable runtime conditions and instrumentation.
- **Affected requirements/tickets/tests:** PRD §§12/14 and runtime NFR; no unique functional AT is defined for the benchmark. Tickets: AS-GOV-002, AS-QA-002/003/006, AS-API-003.

## Register totals

| Status | Count | Decisions |
|---|---:|---|
| APPROVED | 0 | None |
| SELECTED; formal approval not recorded | 5 | AS-OD-01–05 |
| PENDING RESEARCH LEAD review/approval | 3 | AS-OD-09/15/16 |
| PENDING RESEARCH LEAD review; co-approval unresolved | 1 | AS-OD-03 |
| OPEN; awaiting developer confirmation | 9 | AS-OD-06–08, AS-OD-10–14, AS-OD-17 |

Counts overlap for OD-03 and OD-09/15/16: there are 17 unique decisions, 5 selected, 12 without a selected outcome, and no formal approvals. All 17 still need an approval record before QA-04/QA-05 can be reconciled to a formal baseline.
