# Atomic Sentence Open Decisions

**Decision log version:** 0.1.0 (proposed)  
**Status:** No decision below is approved.  
**Date:** 2026-11-03  
**Basis:** [Atomic Sentence PRD v1.0](../research/PRD_Atomic_Sentence_Paper_Understanding_v1.0.md) and supplied research papers.

This log records gaps the product owner or research lead must resolve before implementation. A recommendation is not an approval. Status values are Open, Proposed, or Approved; no item is marked Approved.

## Product and annotation decisions

### AS-OD-01 — Required number of human reviewers

- **Question:** Is one authorized reviewer sufficient to publish a Verified Atomic Sentence, or do selected claims/roles require two independent reviews and adjudication?
- **Why it matters:** It defines the verification gate, review workload, audit requirements, and whether the trusted library can publish after one event.
- **Available options:** One reviewer for every AS; two reviewers for every AS; one reviewer by default with a second reviewer for a risk-defined subset.
- **Recommendation:** For the pilot gold set, use two independent annotators plus adjudication so annotation quality can be assessed, following the CoNLL dataset procedure. Keep the product publication rule open until the owner chooses.
- **Implementation impact:** Reviewer authorization, candidate state transitions, quorum logic, library eligibility, audit display, staffing, and evaluation agreement.
- **Status:** Open.
- **Traceability:** PRD §4, §6 P7, §18 decision 2; CoNLL-2010 supplied PDF p. 5 §5.

### AS-OD-02 — Separate “request revision” action

- **Question:** Should reviewers have a nonterminal REQUEST_REVISION action/state, or should an unsatisfactory candidate be rejected with a reason and regenerated as a new ID?
- **Why it matters:** The PRD specifies a reject-and-regenerate policy and immutable rejected candidates, but does not define a separate revision state.
- **Available options:** Use only REJECTED plus REGENERATE; add a separate revision request that preserves the current candidate; allow a reviewer to request more context without rejecting.
- **Recommendation:** Start from the PRD’s explicit reject-and-regenerate rule. Add a separate action only if a product owner defines whether it edits the candidate or creates a new ID and how the decision is audited.
- **Implementation impact:** State machine, candidate lineage, reviewer controls, edit history, and whether old precheck results remain valid.
- **Status:** Proposed.
- **Traceability:** PRD §6 P7; §7 FR-09; §8 BR-07 and BR-09; §9.2.

### AS-OD-03 — Mapping content kinds to the four functional roles

- **Question:** How should definitions, hypotheses, author interpretations, and conclusions map to the only four PRD roles: BACKGROUND, METHOD, FINDING, and LIMITATION?
- **Why it matters:** These content kinds are not separate PRD roles. Unapproved extra roles would change the data contract and search filters.
- **Available options:** Use only the four roles and map by communicative function; add content-kind tags alongside the four roles; exclude some content kinds from the MVP.
- **Recommendation:** Keep role and evidence origin orthogonal. Use only the four PRD roles until a mapping guide is approved; define separate content-kind tags only if reviewers demonstrate a concrete need.
- **Implementation impact:** Label schema, annotator guide, UI filters, quality metrics, and compatibility with downstream consumers.
- **Status:** Open.
- **Traceability:** PRD §6 P5 and §7 FR-05; the PRD defines four roles and four evidence origins but no separate definition/hypothesis/conclusion labels.

### AS-OD-04 — Hedge annotation scope for the product

- **Question:** Is Atomic Sentence expected to produce all three outputs—sentence-level uncertainty, exact hedge cues, and cue-linked scopes—or only preserve uncertainty during atomization?
- **Why it matters:** The PRD requires preservation of uncertainty/modality but does not list a hedge-cue/scope analyzer. The supplied CoNLL paper treats sentence classification and cue/scope resolution as distinct tasks.
- **Available options:** Preserve uncertainty only; add sentence-level classification; add cue and scope spans; include all three as independently versioned annotations.
- **Recommendation:** If the requested QA-01 hedge capability is approved, annotate and evaluate all three separately. Use the CoNLL min-cue/max-scope convention as a starting hypothesis and validate it on the target corpus rather than assuming it transfers unchanged.
- **Implementation impact:** Annotation schema, spans and overlap handling, test corpus, evaluator, UI overlays, and required model stages.
- **Status:** Proposed.
- **Traceability:** PRD §2.3 G3, §6 P3 and P6; CoNLL-2010 supplied PDF pp. 1–5, especially §4.1–4.3.

### AS-OD-05 — Sentence uncertainty label semantics

- **Question:** Should the product use the CoNLL binary certain/uncertain label, a three-way certain/uncertain/unknown label, or another scheme for implicit uncertainty and ambiguous cases?
- **Why it matters:** The CoNLL binary task uses corpus-specific cue conventions; it does not settle how to classify every implicit, mixed, or unresolved sentence in this product.
- **Available options:** Binary cue-presence convention; binary semantic uncertainty judgment; three-way label with unresolved status.
- **Recommendation:** Keep UNKNOWN available in the annotation protocol if the product decides to classify sentence uncertainty. Do not force uncertain cases into CERTAIN or UNCERTAIN without adjudication.
- **Implementation impact:** Label enum, training/gold set, sentence classifier, confusion matrix, and aggregation from cue annotations.
- **Status:** Open.
- **Traceability:** CoNLL-2010 supplied PDF p. 4 §4.1; its task classifies sentence uncertainty separately from cue/scope annotation.

### AS-OD-06 — Stance/engagement overlap policy

- **Question:** Can one span receive multiple Hyland labels or both a stance and an engagement label, and should a primary function also be required?
- **Why it matters:** Hyland notes that forms can perform more than one function and that broad categories can hide this overlap.
- **Available options:** Mutually exclusive labels; multi-label only; primary label plus optional secondary labels.
- **Recommendation:** Prefer multi-label annotation with explicit evidence and an optional primary function, unless pilot annotators cannot apply it consistently.
- **Implementation impact:** Label schema, annotation UI, precision/recall computation, agreement analysis, and filters.
- **Status:** Proposed.
- **Traceability:** Hyland 2005, supplied PDF pp. 5–6 and category discussions pp. 7–15.

### AS-OD-07 — Metadiscourse in MVP scope

- **Question:** Is metadiscourse annotation an MVP product capability or a research/analysis layer deferred until after the Atomic Sentence library pilot?
- **Why it matters:** The QA-01 request asks for a taxonomy, but the PRD does not list metadiscourse as an MVP requirement or output.
- **Available options:** MVP annotation; optional research-only annotation; defer from product scope.
- **Recommendation:** Keep it optional/research-only until the owner approves a concrete use case and evaluation set. Do not make a theoretical framework a mandatory user-facing feature by default.
- **Implementation impact:** Added annotation stages, schema, reviewer work, user interface, model/evaluation effort, and release scope.
- **Status:** Open.
- **Traceability:** PRD §2.3 non-goals and §7 functional requirements; Hyland 2005; Ädel & Mauranen collection PDF pp. 3–6.

### AS-OD-08 — Metadiscourse definition lens and analysis method

- **Question:** If metadiscourse is included, which definitional lens (interactive or reflexive) and which analysis method (thin, thick, or mixed) should be used?
- **Why it matters:** The supplied collection treats these as separate dimensions that tend to correlate, not interchangeable labels. Different choices include different linguistic evidence and produce non-comparable counts.
- **Available options:** Interactive + thin; reflexive + thick; a justified mixed approach; more than one independently reported lens.
- **Recommendation:** Store the definition lens and analysis method as separate versioned run configuration. Choose only after deciding the product use case and annotation budget.
- **Implementation impact:** Which spans qualify, whether context is required, gold-set labels, output interpretation, and evaluation comparability.
- **Status:** Open.
- **Traceability:** Ädel & Mauranen, collection PDF pp. 4–6 and 11–12; Ädel chapter PDF pp. 72, 77, 81, 84.

### AS-OD-09 — SPS dimensions and scoring

- **Question:** What are the names and scoring rules for the five SPS dimensions, and how should a total score from 0–9 be calculated?
- **Why it matters:** The PRD says SPS has five dimensions and nine points but says Multimedia Appendix 1 with the detailed rubric was not retrieved.
- **Available options:** Obtain Appendix 1 and adopt its rubric; store qualitative dimension notes without a total; keep a manual 0–9 score with a named rubric version; defer SPS.
- **Recommendation:** Do not calculate an official SPS until Appendix 1 or an approved rubric is available. Preserve separate human-entered values/notes and clearly label any locally designed rubric.
- **Implementation impact:** Quality fields, score validation, reviewer UI, exports, training guidance, and claims about comparability.
- **Status:** Open.
- **Traceability:** PRD §1 source policy; §3 SPS row; §8 BR-10; §18 decision 5.

### AS-OD-10 — Allowed source-to-AS evidence cardinality

- **Question:** May one AS cite multiple source spans or source sentences when context completion or a compound construction requires them, or must every AS map to one contiguous quote?
- **Why it matters:** The PRD’s information model permits an AS to link to multiple EvidenceSpan records, while the candidate wording is designed to express one main proposition. Context may be distributed across a paragraph.
- **Available options:** One contiguous span only; one primary span plus supporting context spans; multiple required evidence spans for one AS.
- **Recommendation:** Use one primary evidence span and allow separately typed supporting-context spans. Keep the distinction visible so readers can tell which text directly states the claim and which context resolves a referent.
- **Implementation impact:** Span/link model, UI highlighting, support validation, exports, and evaluator matching.
- **Status:** Proposed.
- **Traceability:** PRD §6 P1–P4; §9.1 EvidenceSpan and ASSupport model; §11 UX.

### AS-OD-11 — Languages and word-count tokenization

- **Question:** Which languages are supported at launch, and how is the 25-word maximum counted outside English?
- **Why it matters:** The PRD specifies whitespace-delimited English tokens and stores a tokenizer version, but does not define multilingual behavior or whether non-English text is unsupported.
- **Available options:** English-only pilot; language-specific tokenizers; multilingual pilot with separately validated counting rules; accept other languages only as flagged, unverified inputs.
- **Recommendation:** Use the PRD’s counting convention only for declared English output in the pilot. Treat other languages as unsupported or partial until a tokenizer and evaluation set are approved.
- **Implementation impact:** Input readiness, language detection, word-count enforcement, model configuration, and evaluation partitions.
- **Status:** Open.
- **Traceability:** PRD §5.1, §8 BR-02, §13 performance; no supplied source defines multilingual requirements.

### AS-OD-12 — Reviewer identity and authorization

- **Question:** What identity system and permissions authorize extraction, verification, rejection, and access to the verified library?
- **Why it matters:** The PRD names researcher/reviewer, annotator, administrator, and downstream-system actors and calls for role-based verification, but does not define identity lifecycle, reviewer attribution, or project-level access.
- **Available options:** Reuse existing workspace credentials/API scopes; add explicit local reviewer identities; use an external identity provider; combine local and project-scoped identities.
- **Recommendation:** Define the identity and audit model before implementation. Do not use a freely editable display name as proof of reviewer authorization.
- **Implementation impact:** Authentication/authorization, API access, audit quality, multi-user data boundaries, export security, and reviewer count policy.
- **Status:** Open.
- **Traceability:** PRD §4 Users & User Jobs; §10 API behavior; §13 Security; §18 decision 2.

### AS-OD-13 — Handling REPORTED_PRIOR_WORK

- **Question:** Should verified Atomic Sentences whose evidence origin is REPORTED_PRIOR_WORK be searchable/exportable with a warning, or excluded from the trusted library until the cited primary paper is reviewed?
- **Why it matters:** The PRD says the focal paper proves only that it reports the prior claim, not that the prior work supports it. The PRD explicitly lists this as an open decision.
- **Available options:** Include with prominent origin label; separate library/filter; exclude from trusted search; require retrieval/review of cited primary paper.
- **Recommendation:** Keep this origin visibly distinct in search and exports. Do not present it as a focal-paper finding. Decide whether it belongs in default verified search based on downstream use.
- **Implementation impact:** Library filters, API response fields, citation provenance, trust semantics, and whether a second paper is needed for verification.
- **Status:** Open.
- **Traceability:** PRD §6 P5; §8 BR-08; §18 decision 4.

### AS-OD-14 — Stale source and supersession policy

- **Question:** What happens to verified entries when the PDF, extracted mapping, page alignment, or segmentation changes, and can a reviewer re-anchor an existing statement?
- **Why it matters:** The PRD requires checksum tracking, stale-source blocking, immutable verified text, and superseded versions, but does not fully specify the user workflow for revalidation.
- **Available options:** Mark all affected entries stale and require a new candidate; re-anchor text as a new version with fresh review; retain old version as historical and publish a separately reviewed replacement.
- **Recommendation:** Preserve the original as historical, exclude it from current verified search after source identity changes, and require a new verification event for a re-anchored or regenerated item.
- **Implementation impact:** Source versioning, invalidation, library filters, migration/backfill, re-review workload, and audit history.
- **Status:** Proposed.
- **Traceability:** PRD §6 P1/P7; §8 BR-09; §14 AT-13; §9.2 VERIFIED→SUPERSEDED.

## Evaluation decisions

### AS-OD-15 — Gold-set composition and adjudication protocol

- **Question:** Which disciplines, sections, document qualities, sample sizes, and annotation personnel will form the pilot gold set?
- **Why it matters:** Candidate recall, hedge-scope quality, and semantic support depend on representative and independently reviewed ground truth. A paper-level split is needed to avoid leakage.
- **Available options:** One focused domain; stratified multi-discipline pilot; staged pilot with domain-specific gold sets.
- **Recommendation:** Start with a stratified pilot over the intended launch domain, use at least two independent annotators plus adjudication, and split development/test by paper. Confirm the sample size with the research lead.
- **Implementation impact:** Prompt/model selection, staffing, annotation tooling, evaluation confidence, and rollout claims.
- **Status:** Proposed.
- **Traceability:** PRD §12 pilot protocol; CoNLL-2010 supplied PDF p. 5 §5 uses independent annotation and chief-adjudicator resolution.

### AS-OD-16 — Acceptance thresholds for language tasks

- **Question:** What metric thresholds, if any, must be met for candidate extraction, cue/scope detection, uncertainty, stance, engagement, metadiscourse, context completion, support, provenance, and reviewer agreement?
- **Why it matters:** Without agreed thresholds, a metric report cannot determine readiness. No supplied research paper establishes a transferable threshold for this product.
- **Available options:** Approve the PRD’s initial internal targets where applicable; set label-specific thresholds after the pilot; use hard process gates only for an initial research preview; require separate thresholds by role/domain.
- **Recommendation:** Do not invent numeric thresholds. Approve metric definitions first, collect pilot baselines, then set error-cost-aware thresholds with the product owner. Keep 100% source traceability, human review, and ≤25-word length as verified-library process gates from the PRD.
- **Implementation impact:** Release gating, review sampling, status labels, model comparisons, and product claims.
- **Status:** Open.
- **Traceability:** PRD §12 lists initial internal targets and labels them not published results; CoNLL and Hyland report research-specific findings, not this product’s thresholds.

### AS-OD-17 — Approval status of the PRD’s initial targets and runtime benchmark

- **Question:** Should the PRD’s initial targets (support precision ≥90%, candidate recall ≥80%, atomicity ≥90%, numeric faithfulness ≥99%) and 5,000-word/two-minute benchmark be accepted as release gates?
- **Why it matters:** The PRD calls these internal targets/benchmarks to measure, not guarantees or published results. Treating them as approved silently changes their status.
- **Available options:** Adopt unchanged; revise after pilot; retain only as descriptive targets; defer until the gold set is ready.
- **Recommendation:** Keep them proposed until the owner approves their measurement definition and applicability. Do not describe them as research-validated or achieved.
- **Implementation impact:** Pilot schedule, deployment sizing, release criteria, and external reporting.
- **Status:** Open.
- **Traceability:** PRD §12 Quality & Metrics and §13 Performance goal.

## Source gaps and non-decisions

- The PRD identifies a JMIR paper as its primary scientific basis, but the supplied research folder does not include that paper. This contract uses the PRD’s explicit Paper/Design distinctions and does not claim to have independently assessed the full JMIR article.
- Multimedia Appendix 1 with the detailed SPS rubric is unavailable according to the PRD itself.
- The supplied CoNLL, Hyland, and metadiscourse sources support linguistic distinctions and evaluation design; they do not add product requirements by themselves.
- CoNLL’s scientific-paper cue/scope conventions were developed on its specific corpus/domain. Their transfer to the intended SLR corpus remains to be evaluated.
- Hyland’s stance/engagement categories overlap in use and vary across disciplines; the supplied paper does not provide product acceptance thresholds.
- The metadiscourse collection preserves competing definitional and methodological traditions; it does not endorse one universal scheme for this product.

## Decision status summary

At version 0.1.0, all decisions remain Open or Proposed. Product owner and research-lead approval must be recorded before any Approved status is assigned or database/application implementation begins.
