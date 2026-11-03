# Atomic Sentence Product Decisions Proposal

**Status:** Proposed for product-owner review; no decision is approved.  
**Review basis:** Atomic Sentence PRD v1.0, the four QA-01 draft specifications, supplied research, and the current SLR Paper Fetcher repository.  
**Scope:** Product decisions needed before database and application implementation. This proposal does not authorize implementation.

## Decision principles

- The PRD controls MVP requirements. A recommendation below clarifies an open choice; it does not silently change or waive an explicit PRD requirement.
- The PRD's product requirements are distinct from the research papers' linguistic frameworks. The latter inform optional annotations and evaluation, but do not themselves require product features.
- All 17 decisions below remain open until the product owner records an approval. Where a decision also needs research-lead input, both approvals are called out.
- The first release is a source-grounded Atomic Sentence workflow inside the existing SLR Paper Fetcher. It reuses the current paper and PDF artifacts and keeps existing analysis workflows intact.

## AS-OD-01 — Required number of human reviewers

- **Original question:** Is one authorized reviewer sufficient to publish a Verified Atomic Sentence, or do selected claims/roles require two independent reviews and adjudication?
- **Why it matters:** Review quorum affects the verification gate, staffing, audit history, and the meaning of VERIFIED.
- **Options:** One reviewer per item; two reviewers per item; one reviewer by default with a defined second-review subset.
- **PRD evidence:** PRD §§6 P7, 8 BR-06 and 18 decision 2 require an explicit recorded human approval and raise the one-versus-two-reviewer question. §12 separately calls for two independent annotators and reconciliation for the pilot evaluation sample.
- **Scientific evidence:** CoNLL-2010 §5 (supplied PDF p. 5) used two independent linguists and a chief adjudicator for its research annotation dataset. This supports gold-set quality control, not a universal product quorum.
- **Existing-app compatibility:** The app records review decisions and reviewer strings, but uses a local-user fallback; the review route does not provide a trusted individual identity or multi-review quorum today.
- **Recommendation:** Require one authenticated, attributable human verifier for every operational MVP item. Permit a second review for disputed or high-risk items as an explicit exception, with its trigger decided before release. For the research gold set, use two independent annotators plus adjudication, separately from operational publication.
- **Advantages:** Keeps the first workflow usable; preserves a real human gate; separates product throughput from evaluation rigor.
- **Disadvantages:** One review can miss errors; risk-based second-review criteria add policy and UI work if automated.
- **Implementation consequences:** Define reviewer identity, decision event, quorum semantics, exception handling, and immutable history before FE-01/library work. Never infer verification from a model result.
- **Blocks MVP:** Yes, until the one-review default and any second-review exception are approved. It does not prevent a non-publishing prototype.
- **Product-owner approval required:** Yes. This is a proposal only.

## AS-OD-02 — Separate request-revision action

- **Original question:** Should reviewers have a nonterminal REQUEST_REVISION action/state, or should an unsatisfactory candidate be rejected with a reason and regenerated as a new ID?
- **Why it matters:** A revision action can be mistaken for permission to edit an immutable rejected or verified item and can leave precheck results attached to changed content.
- **Options:** Use REJECTED plus REGENERATE only; add a separate revision request that creates a new ID; allow a request for additional context while leaving the candidate pending.
- **PRD evidence:** PRD §6 P7, §8 BR-07/BR-09 and §9.2 specify reject-and-regenerate with a new ID and preserved lineage. They do not define a distinct REQUEST_REVISION state.
- **Scientific evidence:** No supplied linguistic paper determines this workflow choice.
- **Existing-app compatibility:** Existing proposition review/edit paths can mark items needs_revision and record edits. Those semantics mutate current analysis objects and are not safe to reuse as Atomic lifecycle semantics without a separate contract.
- **Recommendation:** Use the PRD's REJECTED plus new-ID regeneration path for the MVP. A reviewer may place an unresolved item in NEEDS_CONTEXT when the PRD allows it, but do not introduce a separate revision action unless the owner defines its lineage and audit rules.
- **Advantages:** Matches explicit PRD behavior; minimizes ambiguous states; makes old precheck findings invalid when a new candidate is created.
- **Disadvantages:** Rejection is a stronger action for a correctable wording issue; the workflow may generate more candidate records.
- **Implementation consequences:** Keep rejected items immutable; link a replacement to its parent; run validation again; do not transfer VERIFIED status or stale precheck results.
- **Blocks MVP:** No if the PRD path is accepted; approve before BE-01/FE-01 to prevent UI and state drift.
- **Product-owner approval required:** Yes. This is a proposal only.

## AS-OD-03 — Mapping content kinds to the four functional roles

- **Original question:** How should definitions, hypotheses, author interpretations, and conclusions map to the only four PRD roles: BACKGROUND, METHOD, FINDING, and LIMITATION?
- **Why it matters:** Adding roles changes the PRD's enum, data contract, filters, exports, and evaluation.
- **Options:** Keep only four roles and map by communicative function; add separate content-kind metadata; exclude content that cannot be consistently assigned.
- **PRD evidence:** PRD §§6 P5 and 7 FR-05 specify only BACKGROUND, METHOD, FINDING, LIMITATION and four evidence origins. Evidence origin and functional role are separate fields.
- **Scientific evidence:** Hyland 2005 distinguishes stance and engagement functions; it does not define the PRD's four Atomic roles. No supplied research source supplies a mapping for definitions or hypotheses.
- **Existing-app compatibility:** Existing proposition_type and argumentative_roles describe current paper-analysis/argumentation semantics. They must not be treated as the Atomic role enum.
- **Recommendation:** Keep the four PRD roles. Assign role by the statement's function in the focal paper: a construct definition generally belongs to BACKGROUND, an operational definition or study hypothesis may belong to METHOD, and a conclusion belongs to FINDING only when it summarizes a focal result; caveats belong to LIMITATION. Use evidence origin independently: AUTHOR_INTERPRETATION for author inference, REPORTED_PRIOR_WORK for cited prior claims, and METHOD_DESCRIPTION for procedural content. If a mapping remains unclear, flag for review instead of inventing a role or origin.
- **Advantages:** Preserves PRD compatibility and separates what a sentence does from where its evidence comes from.
- **Disadvantages:** Some statements genuinely serve multiple functions; the mapping guide needs examples and adjudication.
- **Implementation consequences:** Approve role examples and evaluator guidance before output schema, filters, or UI labels are finalized.
- **Blocks MVP:** Yes for reliable role assignment and evaluation; not for repository, storage, or source-index groundwork.
- **Product-owner approval required:** Yes, with research-lead review of annotation examples. This is a proposal only.

## AS-OD-04 — Hedge annotation scope for the product

- **Original question:** Is Atomic Sentence expected to produce all three outputs—sentence-level uncertainty, exact hedge cues, and cue-linked scopes—or only preserve uncertainty during atomization?
- **Why it matters:** These are separate tasks with different labels, outputs, validation, and model failure modes.
- **Options:** Preserve uncertainty only; add sentence-level classification; add cue and scope spans; include all three as separate outputs.
- **PRD evidence:** PRD §6 P3/P6 and §8 BR-03 require preserving hedges, modality, and uncertainty and flagging dropped uncertainty. The PRD does not require a complete cue/scope subsystem.
- **Scientific evidence:** CoNLL-2010 §§2–4 (supplied PDF pp. 2–5) separates sentence-level uncertainty classification from cue detection and scope resolution. Its minimal-cue/maximal-scope annotation and syntax conventions are corpus/task-specific.
- **Existing-app compatibility:** The paper profile calculates a writing-style hedging-marker count, but there is no Atomic cue-span/scope annotation pipeline. That aggregate style metric is not a hedge detector or scope resolver.
- **Recommendation:** Require semantic preservation in every MVP atom and precheck: retain source modality, negation, qualifiers, and scope; flag a dropped or strengthened hedge. Defer sentence uncertainty classification, cue spans, and cue-linked scope spans as separate product capabilities.
- **Advantages:** Preserves the PRD's meaning-faithfulness requirement without importing a new annotation subsystem or claiming CoNLL performance transfers.
- **Disadvantages:** The MVP will not provide a searchable inventory of hedge cues or explicit scope overlays.
- **Implementation consequences:** Include hedge preservation examples in the atomization contract and evaluation; do not add a cue/scope label family to the MVP output contract.
- **Blocks MVP:** No, if semantic preservation and precheck are implemented and tested. It blocks a claim that MVP performs hedge detection or scope resolution.
- **Product-owner approval required:** Yes, to approve the deferral boundary. This is a proposal only.

## AS-OD-05 — Sentence uncertainty label semantics

- **Original question:** Should the product use the CoNLL binary certain/uncertain label, a three-way certain/uncertain/unknown label, or another scheme for implicit uncertainty and ambiguous cases?
- **Why it matters:** A whole-sentence label can hide mixed factual and uncertain clauses, and “unknown” can mean unresolved annotation rather than epistemic uncertainty.
- **Options:** Binary cue-presence convention; binary semantic judgment; three-way label with an unresolved status.
- **PRD evidence:** The PRD requires meaning preservation but defines no sentence-level uncertainty class.
- **Scientific evidence:** CoNLL-2010 Task 1 classifies sentences as uncertain/certain, while Task 2 separately locates cue and scope. Its binary task does not settle ambiguity or mixed-sentence policy for this product.
- **Existing-app compatibility:** No Atomic sentence classifier exists. Current writing-style metrics are aggregate descriptors and cannot supply this label.
- **Recommendation:** Defer sentence-level uncertainty classification from MVP. Preserve uncertainty in statement wording and support checks. If added later, distinguish semantic uncertainty from annotation-unresolved status rather than collapsing both into a third “unknown” class.
- **Advantages:** Avoids an unrequired label and prevents confusion between model uncertainty and sentence meaning.
- **Disadvantages:** Users cannot filter the MVP library by sentence-level uncertainty.
- **Implementation consequences:** No MVP field or classifier is required; add an independent task contract and gold annotations before future implementation.
- **Blocks MVP:** No.
- **Product-owner approval required:** Yes, to approve deferral. This is a proposal only.

## AS-OD-06 — Stance/engagement overlap policy

- **Original question:** Can one span receive multiple Hyland labels or both a stance and an engagement label, and should a primary function also be required?
- **Why it matters:** Context-sensitive and overlapping labels affect annotation consistency, storage, and metric denominators.
- **Options:** Mutually exclusive labels; multi-label annotation; primary label plus optional secondary labels.
- **PRD evidence:** The PRD does not require stance or engagement labels.
- **Scientific evidence:** Hyland 2005 (supplied PDF pp. 5–15, with discussion of variation through pp. 17–21) defines stance and engagement as related dimensions and warns that forms can serve different functions by context and discipline. Its categories are not a word-to-label lookup list.
- **Existing-app compatibility:** No Atomic stance/engagement output or UI exists. The current proposition role system is not equivalent.
- **Recommendation:** Defer the taxonomy from MVP. If later adopted, pilot context-grounded multi-label annotations, retain evidence spans, permit an optional primary function, and evaluate overlap/agreement explicitly.
- **Advantages:** Keeps MVP focused on supported claims and traceability; avoids premature schema commitment.
- **Disadvantages:** No stance or reader-engagement analysis in the first library.
- **Implementation consequences:** Keep future label families extensible in product planning, but do not create MVP values or filters for them.
- **Blocks MVP:** No.
- **Product-owner approval required:** Yes, to approve deferral. This is a proposal only.

## AS-OD-07 — Metadiscourse in MVP scope

- **Original question:** Is metadiscourse annotation an MVP product capability or a research/analysis layer deferred until after the Atomic Sentence library pilot?
- **Why it matters:** Metadiscourse adds a separate theoretical scope, annotation burden, and evaluation target not required for source-verified atoms.
- **Options:** MVP annotation; optional research-only annotation; defer from product scope.
- **PRD evidence:** The PRD's MVP goals and FR-01–FR-13 do not include metadiscourse; it is not necessary to satisfy the Atomic Sentence workflow.
- **Scientific evidence:** The supplied collection describes competing traditions rather than a single mandatory product taxonomy. Hyland's framework is relevant to interactional language, but does not make it an Atomic Sentence requirement.
- **Existing-app compatibility:** No metadiscourse module exists. Current writing-style metrics are not a substitute for contextual metadiscourse annotation.
- **Recommendation:** Defer metadiscourse labels from MVP. Keep the research framing in documentation for a later independently scoped module.
- **Advantages:** Avoids conflating reusable claims with discourse-function analysis.
- **Disadvantages:** The first release cannot offer metadiscourse search or analysis.
- **Implementation consequences:** Do not block schema, AI, or UI work on metadiscourse taxonomies; retain a future extension point only after a use case is approved.
- **Blocks MVP:** No.
- **Product-owner approval required:** Yes, to approve scope deferral. This is a proposal only.

## AS-OD-08 — Metadiscourse definition lens and analysis method

- **Original question:** If metadiscourse is included, which definitional lens (interactive or reflexive) and which analysis method (thin, thick, or mixed) should be used?
- **Why it matters:** A chosen lens defines what counts as evidence; a chosen method defines how context is analyzed. The two dimensions are related but not interchangeable.
- **Options:** Interactive plus thin; reflexive plus thick; a justified mixed approach; more than one independently reported lens.
- **PRD evidence:** The PRD does not define a metadiscourse feature or output.
- **Scientific evidence:** The collection introduction (supplied PDF pp. 3–6 and 11–12) contrasts interactive and reflexive models and thin-list versus thick contextual methods; they often correlate but are distinct. Ädel's chapter (collection PDF pp. 72, 77, 81, 84) emphasizes contextual/reflexive criteria.
- **Existing-app compatibility:** No such model configuration, annotation UI, or evaluation dataset exists.
- **Recommendation:** Defer both choices with metadiscourse itself. If the capability is proposed later, choose and report the definition lens and analysis method separately; do not label one combination as a PRD requirement.
- **Advantages:** Avoids building a theoretically under-specified label into the first database contract.
- **Disadvantages:** No metadiscourse comparison will be possible in MVP.
- **Implementation consequences:** No MVP configuration fields or annotation processing. Future work requires a use case, annotation guide, and compatible gold set.
- **Blocks MVP:** No.
- **Product-owner approval required:** Yes, to approve deferral; a future research lead must select any adopted framework. This is a proposal only.

## AS-OD-09 — SPS dimensions and scoring

- **Original question:** What are the names and scoring rules for the five SPS dimensions, and how should a total score from 0–9 be calculated?
- **Why it matters:** The SPS is explicitly part of PRD FR-10, but its detailed appendix is unavailable. Invented dimension names or weights would create a false official score.
- **Options:** Obtain Appendix 1; store qualitative dimension notes without a total; accept a manual total with a named rubric version; defer SPS review.
- **PRD evidence:** PRD §7 FR-10 is P0 and requires quality review fields. §8 BR-10 allows human-entered score and rubric version, with five independent notes/ratings; it forbids an assumed official weighting. §12 makes SPS descriptive and optional.
- **Scientific evidence:** The PRD cites its JMIR study as the source for SPS; that paper and Multimedia Appendix 1 were not supplied. The other supplied papers do not define SPS.
- **Existing-app compatibility:** The app has human rubric reviews for argumentative analyses, but that rubric has its own dimensions and 0–4 scores. It must not be reused as SPS.
- **Recommendation:** Preserve FR-10 in MVP as a manual quality-assessment capability: store five independently entered notes/ratings as rubric-versioned slots, allow an optional reviewer-entered 0–9 total only with an explicit rubric version, and never auto-calculate or call it official while the rubric is missing. Do not display invented dimension names. Prefer obtaining Appendix 1 before the first operational review.
- **Advantages:** Retains the PRD P0 requirement while protecting score provenance.
- **Disadvantages:** Generic slots are hard to interpret until a rubric is supplied; manual values are not comparable unless versioned.
- **Implementation consequences:** The owner must approve the fallback representation or obtain the rubric before DB-01. UI and exports must display score provenance and no automatic scoring.
- **Blocks MVP:** Yes for final DB-01 and meaningful SPS review; core extraction can be prototyped without it, but FR-10 cannot be silently omitted from MVP.
- **Product-owner approval required:** Yes; research-lead approval of the rubric is also needed. This is a proposal only.

## AS-OD-10 — Allowed source-to-AS evidence cardinality

- **Original question:** May one AS cite multiple source spans or source sentences when context completion or a compound construction requires them, or must every AS map to one contiguous quote?
- **Why it matters:** Context and complete claims may rely on separate source clauses; a single-span rule can hide how an added referent was supported.
- **Options:** One contiguous span only; one primary span plus supporting context spans; multiple evidence spans per AS.
- **PRD evidence:** PRD §9.1 models EvidenceSpan-to-AtomicSentence as many-to-many through ASSupport. §§6 P1–P4 require exact evidence and supported context completion.
- **Scientific evidence:** The linguistic sources do not define source-link cardinality for this product.
- **Existing-app compatibility:** The current proposition table has one source_quote and source_offsets field per proposition, although the analysis payload may carry richer evidence. It does not implement Atomic support links.
- **Recommendation:** Allow multiple exact evidence spans per AS. Identify one primary claim-support span where possible and distinguish supporting context spans used for referent/condition completion. A verified AS needs at least one exact source span; all additions and material conditions must be supported.
- **Advantages:** Matches the PRD information model and supports context completion without merging source wording.
- **Disadvantages:** Review, export, and evaluation must distinguish direct claim evidence from context evidence.
- **Implementation consequences:** Finalize evidence-cardinality semantics before DB-01, PDF highlighting, and support metrics; do not overload current proposition quote fields.
- **Blocks MVP:** Yes for storage/review contract, not for reuse of the source mapping.
- **Product-owner approval required:** Yes. This is a proposal only.

## AS-OD-11 — Languages and word-count tokenization

- **Original question:** Which languages are supported at launch, and how is the 25-word maximum counted outside English?
- **Why it matters:** The PRD supplies a software convention for English but no multilingual definition, tokenizer, or evaluation data.
- **Options:** English-only pilot; language-specific tokenizers; multilingual pilot with separately validated counting rules; flag other languages as unsupported/unverified.
- **PRD evidence:** PRD §8 BR-02 sets whitespace-delimited English tokens, terminal punctuation stripped, and tokenizer version recorded. §5.1 supports selectable-text PDF or parsed structured paper JSON but does not define multilingual tokenization.
- **Scientific evidence:** No supplied research source defines the product's multilingual policy.
- **Existing-app compatibility:** The application can store UTF-8 text and has Vietnamese-facing content, but Unicode handling does not establish validated Vietnamese or multilingual sentence segmentation or word counting.
- **Recommendation:** Pilot English source and English AS text only, using the exact PRD word-count convention and a recorded tokenizer version. Flag other-language material unsupported for verification until language-specific segmentation, tokenization, and evaluation are approved. Do not translate source claims implicitly.
- **Advantages:** Makes the hard 25-word gate deterministic and testable against the PRD.
- **Disadvantages:** Restricts use for non-English SLR corpora and may be unsuitable for local studies.
- **Implementation consequences:** Owner approval is required for launch language scope; define behavior for mixed-language text and source quotes before validator/UI work.
- **Blocks MVP:** Yes for the 25-word validator and source acceptance policy; English-first MVP is otherwise implementable.
- **Product-owner approval required:** Yes. This is a proposal only.

## AS-OD-12 — Reviewer identity and authorization

- **Original question:** What identity system and permissions authorize extraction, verification, rejection, and access to the verified library?
- **Why it matters:** Reviewer names must be attributable and permissions enforceable; a freely entered string cannot prove authorization.
- **Options:** Reuse current workspace credentials/API scopes; define local reviewer identities; use an external identity provider; combine local and project-scoped identities.
- **PRD evidence:** PRD §§4, 10, and 13 describe actors, role-based verification, access checks, and paper-level permissions. §18 decision 2 asks about review policy.
- **Scientific evidence:** No supplied linguistic paper determines authentication policy.
- **Existing-app compatibility:** The workspace has an API-key gate/configuration, but current review records default to local-user and the analysis review endpoint does not establish an individual reviewer subject. There is no demonstrated per-user identity/role system in this path.
- **Recommendation:** Require a server-trusted reviewer identifier attached to every verification event. For the single-workspace pilot, the owner may approve a named local operator identity, but do not trust a client-supplied display name as authorization. Reuse an existing identity provider only if actually configured.
- **Advantages:** Keeps individual accountability and auditability while avoiding an assumed multi-tenant service.
- **Disadvantages:** A named local operator is less suitable for concurrent or distributed reviewing; stronger identity infrastructure could expand scope.
- **Implementation consequences:** Decide identity source and authorization boundary before DB-01 and FE-01; reviewer identity must be supplied by trusted application context and preserved in exports.
- **Blocks MVP:** Yes for operational verification and publication.
- **Product-owner approval required:** Yes. This is a proposal only.

## AS-OD-13 — Handling REPORTED_PRIOR_WORK

- **Original question:** Should verified Atomic Sentences whose evidence origin is REPORTED_PRIOR_WORK be searchable/exportable with a warning, or excluded from the trusted library until the cited primary paper is reviewed?
- **Why it matters:** The focal paper can support the fact that it reports a claim, but cannot by itself establish that the cited primary study supports it.
- **Options:** Include with prominent origin label; separate library/filter; exclude from trusted search; require retrieval and review of the cited primary paper.
- **PRD evidence:** PRD §6 P5, §8 BR-08, AT-10, and §18 decision 4 require a distinct origin and leave library/export policy open.
- **Scientific evidence:** No supplied linguistic paper changes that source-provenance rule.
- **Existing-app compatibility:** The current library/analysis views can display source-linked material; no Atomic origin-aware search filter exists. The external SLR sync contract does not establish support for this new origin.
- **Recommendation:** Include such items in the general verified Atomic library and exports only when a reviewer verifies that the focal paper reports the claim. Show a conspicuous REPORTED_PRIOR_WORK label and cited marker; state that the cited primary paper was not independently checked. Include origin as a filter and field. Never classify or group it as PRIMARY_FINDING; a primary-findings view must exclude it.
- **Advantages:** Preserves useful reported literature while preventing misattribution.
- **Disadvantages:** Users may still overlook the warning in downstream use; cited-source review would be needed to establish the prior paper's claim directly.
- **Implementation consequences:** Origin must be mandatory, visible in search cards/details/exports, and preserved through downstream links. Remote SLR synchronization remains separate.
- **Blocks MVP:** Yes for default search semantics and export contract; not for candidate generation.
- **Product-owner approval required:** Yes. This is a proposal only.

## AS-OD-14 — Stale source and supersession policy

- **Original question:** What happens to verified entries when the PDF, extracted mapping, page alignment, or segmentation changes, and can a reviewer re-anchor an existing statement?
- **Why it matters:** A claim verified against one text representation may no longer be traceable to the current source.
- **Options:** Mark affected items stale and require a new candidate; re-anchor as a new version with fresh review; retain old history and publish a separately reviewed replacement.
- **PRD evidence:** PRD §§6 P1/P7, 8 BR-09, AT-13, and 9.2 require source identity, stale-source handling, immutable verification, and separately reviewed superseding versions.
- **Scientific evidence:** The supplied papers do not define document-version lifecycle.
- **Existing-app compatibility:** GROBID mappings record the source PDF SHA-256 and are rejected when the PDF changes; mapped offsets are validated. The app has no Atomic sentence/document-version lifecycle, and the mapping artifact itself is not shown as a separately versioned Atomic source.
- **Recommendation:** Bind each run and evidence link to the exact PDF hash, mapping content/version, text representation, and sentence-segmentation version. A change to any of these makes dependent candidates stale and blocks verification. Keep old verified records as history but exclude stale/superseded records from current default results. Re-anchoring or substantive change creates a new candidate/version and fresh review.
- **Advantages:** Prevents silent source drift and preserves reproducibility.
- **Disadvantages:** Mapping/segmenter changes can trigger re-review of many records.
- **Implementation consequences:** Approve invalidation rules, source snapshot identity, old-entry visibility, and reprocessing semantics before DB-01/BE-01/LIB-01.
- **Blocks MVP:** Yes for persistence and current-library eligibility.
- **Product-owner approval required:** Yes. This is a proposal only.

## AS-OD-15 — Gold-set composition and adjudication protocol

- **Original question:** Which disciplines, sections, document qualities, sample sizes, and annotation personnel will form the pilot gold set?
- **Why it matters:** Precision, recall, semantic support, and reviewer agreement cannot be measured without representative adjudicated reference annotations.
- **Options:** One focused domain; stratified multi-discipline pilot; staged pilot with domain-specific gold sets.
- **PRD evidence:** PRD §12 specifies a stratified set including prose, results, tables, and limitations; two annotators independently label and reconcile. It warns against using the workshop's κ=0.77 as an Atomic model benchmark.
- **Scientific evidence:** CoNLL-2010 §5 used independent annotation and chief-adjudicator resolution. Hyland's disciplinary variation reinforces the need to sample the intended domain rather than assume universal label behavior.
- **Existing-app compatibility:** Existing tests cover current workflows, but no Atomic gold set or annotation tool is present.
- **Recommendation:** For the launch domain, select a stratified paper-level sample including prose, results, limitations, and usable table/caption examples. Have two independent annotators label candidate evidence and ideal atoms, then reconcile with a named adjudicator. Split development and test sets by paper. Set sample size with the research lead.
- **Advantages:** Measures omissions and disagreement, reduces paper-level leakage, and separates evidence review from model tuning.
- **Disadvantages:** Requires expert time and permissions for source papers; sample size affects confidence in estimates.
- **Implementation consequences:** Define sampling, annotation instructions, adjudication, source access, and metric denominators before AI tuning and acceptance claims.
- **Blocks MVP:** Blocks validated AI release and quality claims; it need not block approved persistence or a non-AI source-index prototype.
- **Product-owner approval required:** Yes, with research-lead approval.

## AS-OD-16 — Acceptance thresholds for language tasks

- **Original question:** What metric thresholds, if any, must be met for candidate extraction, cue/scope detection, uncertainty, stance, engagement, metadiscourse, context completion, support, provenance, and reviewer agreement?
- **Why it matters:** A metric without a threshold or denominator does not define readiness, and different label families have different error costs.
- **Options:** Approve PRD initial targets where applicable; set label-specific thresholds after pilot; use hard process gates only for an initial research preview; set separate thresholds by role/domain.
- **PRD evidence:** PRD §12 defines process hard gates and initial internal targets for support precision, candidate recall, atomicity, and numeric faithfulness. It says those targets are not published results. The PRD does not provide thresholds for the advanced linguistic tasks.
- **Scientific evidence:** CoNLL and Hyland evaluate corpus-specific annotation tasks; their results are not transferable acceptance thresholds for this product. Metadiscourse literature presents multiple methods rather than a universal product metric.
- **Existing-app compatibility:** The application has validation/evaluation artifacts for other analyses, but no Atomic gold-set or Atomic label-level metrics.
- **Recommendation:** Keep PRD process gates: 100% verified-source traceability, 100% human verification coverage, and 100% verified-item length compliance. Measure PRD's initial internal model targets during the pilot, with denominators, paper-level split, and failure examples; do not make them automatic release gates without owner approval. Set thresholds for any future cue/scope or discourse labels only after annotation and pilot evidence.
- **Advantages:** Preserves explicit gates and targets while avoiding unsupported claims.
- **Disadvantages:** The owner may need to decide a release threshold after the pilot, potentially delaying a broad launch.
- **Implementation consequences:** Define metrics/denominators before QA and model tuning; keep deferred-task metrics out of MVP acceptance.
- **Blocks MVP:** Yes for declaring an evaluated production release; no for early internal prototyping or DB-01.
- **Product-owner approval required:** Yes for release-gate status; research lead should approve the evaluation protocol.

## AS-OD-17 — Approval status of PRD targets and runtime benchmark

- **Original question:** Should the PRD's initial targets (support precision ≥90%, candidate recall ≥80%, atomicity ≥90%, numeric faithfulness ≥99%) and 5,000-word/two-minute benchmark be accepted as release gates?
- **Why it matters:** PRD §12 calls the quality values initial internal targets and §13 calls runtime a goal to measure, not a guarantee or published result.
- **Options:** Adopt all as hard gates now; treat as pilot targets to measure and review; revise after pilot; keep runtime informational until representative infrastructure exists.
- **PRD evidence:** §§12–13 give the values and explicitly qualify their status. The hard 100% process gates are separate.
- **Scientific evidence:** The cited workshop κ=0.77 is human coding agreement for research-topic transformation, not an Atomic model threshold. No supplied research validates these product targets.
- **Existing-app compatibility:** The app uses an in-process asynchronous queue and configured provider services; throughput depends on local hardware, model/provider, paper length, and queue load. The two-minute goal cannot be assumed from current architecture.
- **Recommendation:** Record and report these as provisional pilot targets and benchmark observations. Do not make them automatic release gates until their measurement definitions, sample, infrastructure, and error costs are approved. Retain PRD hard process gates independently.
- **Advantages:** Keeps the PRD's numbers visible and measurable without claiming validation or guaranteed performance.
- **Disadvantages:** Release readiness will require a post-pilot owner decision; runtime will vary across deployments.
- **Implementation consequences:** Capture provider/model, paper size, run latency, denominators, and quality metrics in pilot reporting; do not label targets “met” without measured evidence.
- **Blocks MVP:** No for DB-01; yes for final go/no-go claims that treat these numbers as mandatory.
- **Product-owner approval required:** Yes before adopting any of these as release gates. This is a proposal only.

## Product-owner approval checklist

All items remain **Open** or **Proposed** in the QA-01 decision log. Reviewers should record a decision and date in the product decision record; this proposal does not change those statuses.

- [ ] AS-OD-01 — Approve one operational verifier per item and whether any risk class needs a second.
- [ ] AS-OD-02 — Approve reject-and-regenerate as the only MVP correction path.
- [ ] AS-OD-03 — Approve mapping guidance for definitions, hypotheses, interpretations, and conclusions.
- [ ] AS-OD-04 — Approve uncertainty-preservation-only scope and defer full cue/scope extraction.
- [ ] AS-OD-05 — Approve deferral of sentence-level uncertainty labels.
- [ ] AS-OD-06 — Approve deferral of Hyland stance/engagement labels.
- [ ] AS-OD-07 — Approve deferral of metadiscourse annotation.
- [ ] AS-OD-08 — Approve deferral of metadiscourse lens/method selection.
- [ ] AS-OD-09 — Obtain SPS appendix or approve a manual, rubric-versioned fallback without invented dimension names.
- [ ] AS-OD-10 — Approve multiple evidence spans with primary/supporting-context distinction.
- [ ] AS-OD-11 — Approve English-first input/output and PRD word counting for MVP.
- [ ] AS-OD-12 — Approve trusted reviewer identity and authorization source.
- [ ] AS-OD-13 — Approve origin-visible inclusion of REPORTED_PRIOR_WORK and primary-only filtering.
- [ ] AS-OD-14 — Approve stale-source invalidation and new-version re-verification.
- [ ] AS-OD-15 — Approve gold-set domain, staffing, adjudication, and sampling plan.
- [ ] AS-OD-16 — Approve metric definitions and which targets gate release.
- [ ] AS-OD-17 — Approve the status of numeric targets and runtime goal after the pilot.
