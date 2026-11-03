# QA-04 Product and Research Approval Questionnaire

**Use:** The authorized approver selects one option per decision or requests a revision. Recommendations are identified, not preselected.  
**Current state:** Every decision status is OPEN. No response is recorded.

## How to answer

For each item, select an option letter or write a precise alternative. If rejecting or requesting changes, state the rationale or requested change. For every approval, supply the decision ID, selected option, approver identity, timestamp with timezone, and any conditions/rationale. The decision register records the formal status.

### AS-OD-01 — Number of operational reviewers

**Question:** How many human verifiers are required for each MVP Atomic Sentence?

- A. One trusted verifier for every item.
- B. Two independent verifiers for every item, with adjudication when they disagree.
- C. One verifier by default and a second verifier for a defined high-risk/disputed subset. **QA-02 recommendation; not approved.**

**Impact:** Sets review effort, quorum, history, and publication eligibility.  
**Blocks:** Human verification and verified-library publication until policy is approved. Gold-set annotation remains separate and should use two independent annotators plus adjudication.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-02 — Correction after a failed review

**Question:** What action should a reviewer take when a candidate needs correction?

- A. Reject with a reason; regeneration creates a new linked ID. **QA-02 recommendation; not approved.**
- B. Add a separate revision-request action that creates a new item/version.
- C. Leave the item pending while requesting context, with a defined resolution rule.

**Impact:** Defines immutability, item lineage, and whether precheck results remain valid.  
**Blocks:** Final lifecycle/API/review workflow; a separate revision state can be deferred if A is approved.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-03 — Mapping content kinds to PRD roles

**Question:** How should definitions, hypotheses, interpretations, and conclusions map to BACKGROUND, METHOD, FINDING, or LIMITATION?

- A. Keep the four PRD roles; map by communicative function and keep evidence origin separate. **QA-02 recommendation; not approved.**
- B. Keep the four roles and add separately approved content-kind metadata.
- C. Exclude content that cannot be mapped consistently.

**Impact:** Affects role assignment, AI output, review guidance, filters, and gold-set labels.  
**Blocks:** Role-labeled extraction and evaluation; no new role/origin values are assumed.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-04 — Uncertainty and hedge-analysis scope

**Question:** Which uncertainty-related outputs are required in MVP?

- A. Preserve source uncertainty, modality, negation, and scope in atomization; no separate classifier/cue/scope labels. **QA-02 recommendation; not approved.**
- B. Also classify whole sentences as uncertain/certain.
- C. Also detect hedge cues and resolve their scopes.
- D. Implement all three outputs as separate annotations.

**Impact:** Affects output contract, model stages, annotation cost, and evaluation.  
**Blocks:** Final MVP/AI contract. Separate classifier/cue/scope work can be deferred if A is approved; semantic preservation remains required in every option.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-05 — Separate sentence uncertainty label

**Question:** Should MVP include a whole-sentence uncertainty label?

- A. Defer the label; preserve uncertainty semantically in each atom. **QA-02 recommendation; not approved.**
- B. Use binary cue-presence labels.
- C. Use binary semantic uncertain/certain labels.
- D. Use a semantic label plus a distinct unresolved-annotation status.

**Impact:** Determines classifier, label semantics, and evaluation metric.  
**Blocks:** Only the separate sentence-label feature; an explicit deferral does not block other MVP processing.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-06 — Stance/engagement overlap

**Question:** Should Hyland stance and engagement annotation be part of MVP, and if later included, how should overlap work?

- A. Defer both label families from MVP. **QA-02 recommendation; not approved.**
- B. Include them with mutually exclusive labels.
- C. Include contextual multi-label spans.
- D. Include a primary label with optional secondary labels.

**Impact:** Adds label families, contextual annotation, UI, and agreement/evaluation work.  
**Blocks:** The optional stance/engagement feature; deferral does not block MVP.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-07 — Metadiscourse in MVP

**Question:** Should metadiscourse annotation be included in the first release?

- A. Include it as an MVP annotation.
- B. Allow it as optional research-only annotation.
- C. Defer it from the first product release. **QA-02 recommendation; not approved.**

**Impact:** Changes product scope, annotation effort, storage, UI, and evaluation.  
**Blocks:** Metadiscourse implementation only; C does not block the Atomic Sentence MVP.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-08 — Metadiscourse framework and method

**Question:** If metadiscourse is later included, which definition lens and analysis method should be used?

- A. Interactive model with thin/list-based analysis.
- B. Reflexive model with thick/contextual analysis.
- C. A justified mixed approach or separately reported lenses/methods.
- D. Defer both choices with metadiscourse itself. **QA-02 recommendation; not approved.**

**Impact:** Determines what text qualifies and whether outputs are comparable.  
**Blocks:** Metadiscourse work only; D leaves the MVP unaffected.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-09 — SPS fields and scoring

**Question:** How should PRD FR-10 be implemented while the SPS appendix is unavailable?

- A. Obtain Appendix 1 and use its exact rubric.
- B. Store five independent qualitative notes/ratings without a total until the rubric is available.
- C. Allow an optional reviewer-entered total with an explicit rubric version; no automatic or “official” score without the rubric.
- D. Defer SPS fields, which would require an explicit change to PRD P0 FR-10.
- E. Approve a combination of B and C as a manual, versioned fallback. **QA-02 recommendation; not approved.**

**Impact:** Affects required P0 quality-review data, UI, exports, and DB design.  
**Blocks:** DB-01 field design and SPS review behavior. No dimension names or weights may be invented.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-10 — Evidence spans per Atomic Sentence

**Question:** May one AS cite multiple source spans, including separate context support?

- A. Require one contiguous span only.
- B. Allow one primary claim-support span plus supporting context spans. **QA-02 recommendation; not approved.**
- C. Allow multiple equal evidence spans without a primary distinction.

**Impact:** Affects evidence storage, source highlighting, atomization, context completion, and export.  
**Blocks:** DB-01 evidence design, source-linked context, review, and library provenance.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-11 — Language and word counting

**Question:** Which languages can be processed and verified in the first pilot?

- A. English-only source and output, using the PRD whitespace token rule and recorded tokenizer version. **QA-02 recommendation; not approved.**
- B. Add one or more language-specific tokenizers with separate evaluation.
- C. Run a multilingual pilot with separately validated segmentation/counting.
- D. Accept other languages for intake but flag them unsupported/unverified.

**Impact:** Affects sentence segmentation, <=25-word validation, model evaluation, and eligibility.  
**Blocks:** Source-index and word-count implementation until the launch boundary is explicit.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-12 — Reviewer identity and authorization

**Question:** Which trusted identity source authorizes verification and library access?

- A. Reuse current workspace/API scopes if they identify an individual reviewer.
- B. Use approved named local reviewer identities for the single-workspace pilot.
- C. Integrate an external identity provider.
- D. Combine local identity with project-scoped permissions.
- E. Select a single-workspace identity only after Technical Lead confirms the existing path; do not trust a client-entered name. **QA-02 recommendation; not approved.**

**Impact:** Affects audit integrity, authorization, DB fields, and multi-user access.  
**Blocks:** Human verification, verified-library publication, and related DB-01 design.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-13 — REPORTED_PRIOR_WORK in the library

**Question:** How should a verified statement that reports prior work appear in search and export?

- A. Include in the general verified library with a prominent origin/citation label and a primary-findings exclusion filter. **QA-02 recommendation; not approved.**
- B. Keep it in a separate library/filter.
- C. Exclude it from trusted search and export.
- D. Require retrieval and review of the cited primary paper before inclusion.

**Impact:** Affects trust semantics, default result sets, filters, and exports.  
**Blocks:** Library/search/export policy, not initial source indexing.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-14 — Stale source and supersession

**Question:** What happens to linked items when the PDF, mapping, text representation, or segmenter changes?

- A. Mark dependent items stale; require a new candidate/version and fresh verification for re-anchoring. **QA-02 recommendation; not approved.**
- B. Re-anchor in a new version with a new review event.
- C. Keep old records as history and publish a separately reviewed replacement.

**Impact:** Affects source identity, verification validity, library eligibility, and reprocessing.  
**Blocks:** DB-01, canonical source indexing, verification, and current library publication.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-15 — Gold-set composition

**Question:** What launch domain, paper/section sample, sample size, and annotation/adjudication staffing will define the gold set?

- A. One focused domain and a small pilot sample.
- B. Stratified sample across intended launch subdomains, two independent annotators, adjudication, and paper-level split. **QA-02 recommendation; not approved.**
- C. Staged domain-specific gold sets with separate evaluation reports.

**Impact:** Determines annotation cost and the scope supported by model-quality claims.  
**Blocks:** Gold-set construction and validated AI release; not DB-01 by itself.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-16 — Metrics and release thresholds

**Question:** Which quality metrics and thresholds govern MVP readiness?

- A. Keep PRD 100% traceability, human-verification coverage, and length as hard process gates; define denominators and set model thresholds after the pilot. **QA-02 recommendation; not approved.**
- B. Adopt applicable PRD initial numeric targets as hard gates immediately.
- C. Use process gates only for an initial research preview.
- D. Set different thresholds by role/domain after pilot data.

**Impact:** Determines release decision, evaluation work, and any model-quality claims.  
**Blocks:** Final release gating and evaluated readiness; not DB-01 if metrics remain report-only during design.  
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

### AS-OD-17 — PRD numeric targets and runtime goal

**Question:** Should PRD's support precision, recall, atomicity, numeric-faithfulness, and 5,000-word/two-minute values be hard release gates?

- A. Adopt all as hard gates now.
- B. Measure them as provisional pilot targets; approve any mandatory gates after results. **QA-02 recommendation; not approved.**
- C. Revise targets after the pilot.
- D. Keep targets descriptive and defer the runtime benchmark until infrastructure is fixed.

**Impact:** Affects release claims, pilot reporting, and performance sizing.  
**Blocks:** Claims that the targets are mandatory or achieved; does not block DB-01.
**Select:** ___  **Status:** OPEN  **Conditions/rationale:** ___

## Cross-decision consistency checks

- **AS-OD-01 and AS-OD-15:** Operational reviewer quorum and research gold-set annotator/adjudicator staffing are separate choices. Do not use a one-review operational choice to reduce independent gold-set annotation.
- **AS-OD-04 and AS-OD-05:** If AS-OD-04 selects sentence-level classification, AS-OD-05 must define that label's semantics. If the classifier is deferred, AS-OD-05 should also be deferred. Uncertainty preservation remains required in all cases.
- **AS-OD-07 and AS-OD-08:** If metadiscourse is deferred, defer framework selection too. If it is included or research-only, select the theoretical lens and method separately.
- **AS-OD-03 and AS-OD-11:** Gold-set role examples and sampling must use the approved role mapping and launch language.
- **AS-OD-15, AS-OD-16, and AS-OD-17:** The pilot sample informs model thresholds; explicitly distinguish metric definitions, provisional targets, and release gates.

## Response record template

Copy once for each decision. For joint approval, include a separate identity/timestamp for each required approver.

| Field | Approver response |
|---|---|
| Decision ID | |
| Selected option or exact custom wording | |
| Decision status | OPEN / APPROVED / REJECTED / NEEDS REVISION / DEFERRED |
| Approver identity and role | |
| Approval timestamp with timezone | |
| Conditions or rationale | |
| Research Lead identity/timestamp, if required | |
| Follow-up owner/date, if NEEDS REVISION or DEFERRED | |
