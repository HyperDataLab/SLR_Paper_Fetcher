# Atomic Sentence Evaluation Contract

**Contract version:** 0.1.0 (proposed)  
**Status:** Draft for product and research review; no numerical acceptance target is approved here.  
**Date:** 2026-11-03  
**Primary source:** [Atomic Sentence PRD v1.0](../research/PRD_Atomic_Sentence_Paper_Understanding_v1.0.md)  
**Related contract:** [Annotation contract](atomic-sentence-annotation-contract.md)

## 1. Purpose and evaluation principles

Evaluation must determine whether the system finds appropriate source claims, preserves uncertainty and meaning, produces standalone statements supported by the paper, maps each statement back to exact source evidence, and leaves final verification to humans.

The evaluation contract separates:

- **Task metrics** (how candidate or annotation output is compared with reviewed ground truth);
- **Process gates** (conditions required for a record to be verified/published);
- **Numerical targets** (proposed thresholds that require owner approval).

Do not collapse the tasks into one score. In particular:

- CoNLL-2010 evaluates sentence uncertainty classification separately from hedge cue/scope spans.
- Cue detection and scope resolution must be measured separately as well.
- A linguistically plausible or “SUPPORTED” model score is not human verification.
- AI confidence is not a calibrated probability unless a calibration study demonstrates calibration on the target corpus.
- Hyland’s corpus frequencies and the CoNLL shared-task scores are scientific results, not product acceptance targets.
- The PRD’s cited workshop Cohen κ=0.77 measures human coding of research-topic transformations, not Atomic Sentence model performance.

## 2. Evaluation tasks

The metrics below are **proposed methods**, not approved acceptance thresholds. Exact matching and overlap diagnostics should both be reported where boundary choices can vary.

| Task | Evaluation objective | Unit | Proposed metric(s) | Ground-truth requirements | Known limitations |
|---|---|---|---|---|---|
| **1. Candidate extraction** | Measure whether the system retrieves source-supported, research-relevant claim candidates without excessive false candidates or omissions. | Candidate claim linked to source evidence; count both claim-level and supporting-span matches. | Precision, recall, F1 for semantically matched candidates; exact evidence-span precision/recall and relaxed span-overlap diagnostics. Report per role/origin and section type. | Human-selected candidate inventory on sampled source paragraphs, with evidence spans, role/origin, and adjudicated match criteria. Split train/dev/test by paper. | “Candidate” depends on inclusion scope; recall requires annotators to identify all relevant candidates. Paragraphs can legitimately have zero candidates. |
| **2. Hedge cue detection** | Find the minimal exact cue span and distinguish contextual hedge uses from non-hedging uses of the same form. | Cue phrase span linked to its sentence. | Strict exact-span precision/recall/F1; token-level span F1 or overlap as a diagnostic. Report phrase and single-token cues separately. | Context-labeled cue spans with ambiguous/non-cue uses and adjudicated boundaries. | Exact punctuation/citation boundaries can be debatable. Lexicons miss off-list items; cues are domain-sensitive. |
| **3. Hedge scope resolution** | Identify the uncertain linguistic content governed by each cue. | Cue–scope pair, with start/end boundaries and stable cue ID. | Strict scope-level precision/recall/F1 requiring the correct cue and exact scope boundaries; relaxed token-overlap score for diagnosis only. Also report cue accuracy separately. | Gold cue spans and linked scope spans; allow nested/overlapping scopes where the annotation scheme permits them. | CoNLL strict boundary matching is intentionally severe; disagreements about punctuation or exact syntactic extent can lower exact F1 without equivalent practical harm. |
| **4. Sentence-level uncertainty** | Classify whether a complete sentence contains uncertain/speculative content under the approved scheme. | Whole sentence. | Precision, recall, F1 for the UNCERTAIN class; confusion matrix and class prevalence. | Binary or approved three-way labels assigned to whole sentences; annotation guidance must state how implicit uncertainty and cue-free uncertainty are handled. | A sentence label hides which clause is uncertain and can mark a mixed factual/uncertain sentence as one class. It is not a substitute for cue/scope spans. |
| **5. Stance classification** | Classify contextual instances as hedges, boosters, attitude markers, or self-mention. | Marker/function instance with the affected proposition span; multi-label where needed. | Per-category precision/recall/F1, macro and micro averages, confusion matrix, and exact-span match. Report overlap/multi-label cases separately. | Contextual annotations using the approved Hyland taxonomy; annotators must distinguish epistemic stance, affect, and author presence. | Categories can co-occur; disciplinary practice and context change function. Hyland’s categories are not a universal word-to-label dictionary. |
| **6. Engagement classification** | Classify reader-directed resources as reader pronouns, directives, questions, shared-knowledge appeals, or personal asides. | Marker/function instance with the reader or discourse span it targets. | Per-category precision/recall/F1, macro/micro averages, exact-span match, and ambiguity/adjudication rate. | Contextual labels following the approved Hyland categories; distinguish reader address from author-only pronouns, content questions, method instructions, and ordinary parentheses. | Reader orientation can be implicit; inclusive “we” and rhetorical questions vary by discipline and genre. |
| **7. Metadiscourse annotation** | Evaluate the chosen metadiscourse definition and method without conflating them. | Contextual discourse function (thick analysis) or prelisted marker occurrence (thin analysis), with framework/method metadata. | For a thin list: precision/recall/F1 against the approved marker set, plus frequency agreement. For a thick analysis: span and function-label F1 plus human agreement. Report each selected definition lens separately. | Before annotation, declare interactive or reflexive definition, thin/thick or mixed method, scope of context, and category scheme. Annotators must be trained on the same choice. | The research documents disagreement between models and methods. Scores from different lenses are not directly comparable; broad retrieval may overcount functions while contextual analysis costs more. |
| **8. Semantic support of atomic statements** | Determine whether the proposed AS is supported by the supplied paper and whether it adds, omits, or contradicts material details. | AS plus all linked evidence and necessary context. | Human-labeled support-class precision/recall/F1 for SUPPORTED, PARTIAL, CONTRADICTED, UNDETERMINED; precision of SUPPORTED is especially relevant. Separately report element-level preservation for actor, population, condition, comparator, time, metric, unit, direction, negation, and uncertainty. | Adjudicated AS/evidence pairs labeled against the original PDF, not only extracted mapping. Include primary findings and reported prior work. | Human judgments can differ; source text may itself be ambiguous, tables may be non-linear, and support class does not prove scientific truth. |
| **9. Context completion correctness** | Test whether pronouns/implicit referents are resolved from the paper and whether generated additions preserve source meaning. | Each completion decision and completed AS, including each inserted referent/condition. | Correct referent resolution accuracy; proportion with complete supporting spans; unsupported-addition rate; human semantic-preservation judgment; length compliance. | Gold antecedent/context links and adjudicated completed wording. Include unresolved cases that should remain NEEDS_CONTEXT. | Exact wording may vary while meaning is preserved. The PRD does not define a complete context-completion taxonomy. |
| **10. Source provenance accuracy** | Ensure quotes, offsets, page/section locators, and source hashes point to the correct original document. | Evidence span/document identity, including page mapping where available. | Exact quote/offset round-trip rate; source-hash match rate; page alignment accuracy on manually checked pages; report unresolved spans separately. | Original PDF plus checksum-pinned text mapping and manually confirmed span/page alignment. | PDF page numbers may differ from printed pagination; GROBID can lack coordinates; tables and poor scans may not have reliable linear offsets. |
| **11. Human reviewer agreement** | Measure reproducibility of candidate, linguistic, semantic-support, and verify/reject decisions. | Same item independently labeled by two or more reviewers. | Raw agreement plus Cohen’s κ for two annotators or Krippendorff’s α for multiple annotators/missing labels; report per category, prevalence, confusion matrices, adjudication rate, and disagreements. | Independent blinded annotations before adjudication, with reviewer training and a shared versioned guide. | Kappa/alpha is affected by class prevalence and label imbalance. One agreement value cannot summarize all label types. |

## 3. Ground-truth and sampling protocol

### 3.1 Corpus design

Build a gold set from the same accessible PDF and structured-paper inputs the product will support. Stratify by discipline, paper section (introduction, methods, results, discussion/conclusion, limitations), claim role, evidence origin, document quality, and linguistic phenomena. Include:

- sentences with no candidate claim;
- one and multiple candidate claims;
- compound and coordinated statements;
- mixed factual/uncertain sentences and multiple hedge cues;
- nested or overlapping scopes where present;
- numeric claims with denominators, units, comparators, and conditions;
- pronouns/implicit entities requiring context or remaining unresolved;
- source-reported prior work versus focal-paper findings;
- selectable-text PDF, structured JSON, and flagged OCR/table cases.

Keep paper-level splits between development and evaluation to reduce leakage from repeated style, terminology, or claims in the same paper. Version the source PDF, text mapping, sentence segmentation, tokenizer, annotation guide, and label schema alongside the gold set.

### 3.2 Annotation and adjudication

Use at least two independent trained annotators for the pilot gold set and a named adjudicator to resolve differences, following the CoNLL dataset protocol. Annotators should mark source evidence before judging a generated AS. For every item, retain:

- original text and exact source span(s);
- cue and scope spans as separate labels;
- whole-sentence uncertainty label;
- stance/engagement/metadiscourse labels under their chosen framework;
- atomic statement and context-completion judgment;
- support verdict and element-level changes;
- reviewer disagreement and adjudication outcome.

Do not tune category definitions after examining test outputs without changing the contract version and documenting the change. If labels are changed, reannotate or version the affected data and report results by contract version.

### 3.3 Reporting

For each metric, report numerator/denominator, sample size, paper and section counts, uncertainty interval where appropriate, language/domain, annotation version, and relevant failure examples. Report per-class results, not only aggregate values. Separate exact-match scoring from relaxed diagnostics. Report the number of items excluded for unreliable extraction and why.

## 4. Thresholds and gates

### 4.1 PRD hard process gates

These are product rules in the supplied PRD, not model-performance targets:

- **Source Traceability:** 100% of verified AS must have resolvable original evidence.
- **Human Verification Coverage:** 100% of verified AS must have a human review event satisfying the approved reviewer policy.
- **Length Compliance:** 100% of verified AS must be at most 25 words under the recorded tokenizer.
- No verified entry without a source anchor, current source identity, and human action.

These are publication controls for the verified library. They do not imply that candidate extraction or language annotations are 100% accurate.

### 4.2 PRD initial internal targets — proposed, not approved

The PRD’s §12 calls the following “Product-defined, Not Published Results” and labels them initial internal targets. They are recorded here for owner decision; this contract does **not** approve them as release thresholds.

| PRD metric | PRD initial target | Status in this contract | Decision needed |
|---|---:|---|---|
| Evidence Support Precision | ≥90% | Proposed, unapproved | Define sample, adjudication, and whether threshold applies overall or by role/origin. |
| Candidate Recall | ≥80% | Proposed, unapproved | Define the reference candidate universe and sample size. |
| Atomicity Pass Rate | ≥90% | Proposed, unapproved | Approve one-main-proposition rubric and reviewer agreement. |
| Numeric Faithfulness | ≥99% | Proposed, unapproved | Define denominator and what counts as correct for units/rounding/derived values. |
| Reviewer Rejection Rate | Observe; no arbitrary target | Descriptive only | Decide whether rejection rates trigger review of extraction quality. |
| SPS distribution | Descriptive; no arbitrary cutoff | Descriptive only | Resolve the official rubric and whether to collect a total score. |

The PRD also proposes a performance benchmark of processing a typical accessible-text 5,000-word paper into preliminary candidates within two minutes on provisioned infrastructure. Treat it as a benchmark to measure, not a guarantee or an approved release gate.

### 4.3 Undecided thresholds

The PRD provides no numeric acceptance thresholds for hedge cue/scope accuracy, sentence uncertainty classification, Hyland stance categories, engagement categories, metadiscourse labels, context-completion correctness, or human inter-reviewer agreement. Do not invent them. Establish them only after:

1. the relevant categories and annotation guide are approved;
2. the gold set is adjudicated and representative;
3. baseline model results and disagreement are measured;
4. error costs are agreed by the product owner and researchers.

The 2010 CoNLL shared-task scores, Hyland’s feature frequencies, and the workshop κ=0.77 cited in the PRD are not candidate targets for this product.

## 5. Semantic Purity Score (SPS)

The PRD says SPS is a nine-point assessment across five dimensions, but the supplied PRD states that Multimedia Appendix 1 containing the detailed rubric could not be retrieved. Therefore:

- store dimension-level human assessments only after dimension definitions are confirmed;
- allow an optional reviewer-entered 0–9 total only with a rubric version;
- do not infer the five dimension names, point allocations, weighting, pass line, or compute an “official SPS” from an assumed rubric;
- if an internal heuristic is later introduced, label it as a different metric.

## 6. Traceability

| Evaluation requirement | Source and location |
|---|---|
| Product targets and hard process metrics | PRD §12 “Quality & Metrics”; §14 release gates. |
| SPS dimensions and missing official rubric | PRD §1 source policy; §3 SPS row; §8 BR-10; §18 decision 5. |
| Sentence-level uncertainty F1 vs scope-level F1 | Farkas et al., [CoNLL-2010 PDF](../research/W10-3001.pdf), PDF p. 4 §4.1–4.3; exact cue/scope evaluation on PDF pp. 4–5. |
| Independent annotators and adjudication | CoNLL-2010 PDF p. 5 §5. |
| Nested scope and XML span representation | CoNLL-2010 PDF p. 6 §5.4. |
| Contextuality, category overlap, and discipline variation | Hyland 2005, [supplied PDF](../research/Stance_and_engagement_a_model_of_interac.pdf), PDF pp. 5–7, 17–21. |
| Metadiscourse lens/method differences | Ädel & Mauranen, [collection PDF](../research/Metadiscourse_Diverse_and_Divided_Perspectives.pdf), PDF pp. 4–6, 11–12; Ädel chapter PDF pp. 72, 77, 81. |

## 7. Open acceptance decisions

See [open-decisions.md](open-decisions.md) for decision IDs, options, recommendations, and status. No task-specific model threshold is marked Approved in version 0.1.0.
