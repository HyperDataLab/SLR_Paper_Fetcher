# Atomic Sentence Annotation Contract

**Contract version:** 0.1.0 (proposed)  
**Status:** Draft for product and research review; no decision in this document is approved.  
**Date:** 2026-11-03  
**Product source:** [Atomic Sentence PRD v1.0](../research/PRD_Atomic_Sentence_Paper_Understanding_v1.0.md)  
**Scientific sources:** [CoNLL-2010 hedge task](../research/W10-3001.pdf), [Hyland 2005](../research/Stance_and_engagement_a_model_of_interac.pdf), and [Metadiscourse: Diverse and Divided Perspectives](../research/Metadiscourse_Diverse_and_Divided_Perspectives.pdf).

## 1. Authority and interpretation labels

The PRD is authoritative for product scope and workflow. Academic papers ground the linguistic distinctions; they do not independently make those distinctions mandatory product features. The additional stance, engagement, metadiscourse, and uncertainty annotations in this contract are proposed because QA-01 asks to define them. Their inclusion in the product still requires owner approval because the PRD does not list them as Atomic Sentence MVP fields.

Rules and statements are marked as follows:

- **[PRD]** Explicit requirement or rule in the supplied PRD.
- **[Research]** Concept or distinction described in a supplied paper.
- **[Proposal]** Operational interpretation for review; not attributed to the PRD or paper as a validated software rule.
- **[Open]** Requires a product or annotation decision before implementation.

All examples below are constructed for this specification unless explicitly identified as an example from a paper. Constructed examples are not claims about actual research findings.

## 2. Operational definition of an Atomic Sentence

### 2.1 Definition

**[PRD]** An Atomic Sentence (AS) is a short, semantically complete knowledge unit that can be read independently, recombined with other units, and checked against exact evidence in its original paper. An unfamiliar researcher should be able to paraphrase it accurately within 30 seconds. An approvable AS contains at most 25 words. It carries the paper’s Author, Year, Page or best available locator, and one functional role: `BACKGROUND`, `METHOD`, `FINDING`, or `LIMITATION`.

**[PRD, marked Design in the PRD]** The software-level working test for atomicity is one main testable or reusable proposition per AS. This is an operationalization, not a scientific criterion attributed to the JMIR study.

The word limit is strict for approval. The PRD notes 18–22 words as a potentially useful range, but it is not a requirement. Word count follows the PRD’s software convention: whitespace-delimited English tokens, with terminal punctuation stripped; the tokenizer version must be recorded. **[Open]** Behavior for non-English texts, hyphenated tokens, formulas, and table cells needs a locale and tokenization decision.

### 2.2 Inclusion and exclusion

| Rule | Contract | Origin |
|---|---|---|
| Include research-relevant claims | Extract zero or more source-supported candidates from a paragraph. Candidate types include background claims, methods, empirical findings, and limitations. | [PRD §6 P2; §7 FR-02] |
| Preserve focal-paper provenance | Record whether the sentence describes a primary finding, reported prior work, author interpretation, or method description. A paper’s report of another study is not evidence that the focal study found it. | [PRD §6 P5; §8 BR-08] |
| Exclude non-claims | Do not promote questions, navigation text, headings alone, references-only lines, or boilerplate as factual AS candidates unless product guidance later defines a valid use. | [PRD §6 P2] |
| Require source evidence | Each candidate/AS needs at least one exact source span. A page number or citation alone is insufficient. | [PRD §8 BR-05] |
| Flag unusable input | Unreliable OCR, unreadable scans, missing provenance, and non-linear tables/captions with unreliable extraction cannot become verified without manual checking against the original PDF. | [PRD §5.1] |
| No external claim generation | Generate candidates only from authorized paper content and supplied local context; do not use outside search or general knowledge to add claims. | [PRD §8 BR-01] |

### 2.3 Sentence splitting and semantic preservation

**[PRD]** A source sentence may yield zero, one, or multiple candidates. If a compound statement contains independently complete claims that can be checked separately, propose separate AS records with separate IDs and evidence links. Keep each resulting statement at 25 words or fewer.

**[Proposal]** Apply these splitting rules:

1. Split coordinated clauses only when each clause expresses a distinct proposition that remains independently intelligible and verifiable.
2. Keep together a measure and its numerator/denominator, a result and its comparison baseline, a claim and its essential condition, and a statement whose meaning depends on negation, modality, or contrast.
3. A split statement may repeat an explicit source referent (such as the intervention name) only when the supplied paragraph or neighboring context supports that referent. Link the added referent to its supporting span.
4. If splitting would remove a causal/contrastive relation, scope, condition, or qualification, retain the relation in the AS or preserve linked evidence for each resulting statement.
5. Do not change association into causation, possibility into certainty, a limited population into a general claim, or a reported comparison into an unqualified effect.

**Constructed example:** Source sentence: “The intervention reduced symptom scores, and the reduction was larger among participants aged over 60.” Two proposed AS records may be “The intervention reduced symptom scores.” and “The intervention reduced symptom scores more among participants aged over 60.” Each retains an independently checkable proposition; the second keeps the comparison group. If the source instead says only “may reduce,” each AS must preserve that uncertainty.

**Constructed numeric example:** If a source reports “11 of 18 participants (61%) improved,” do not separate 11, 18, and 61% into different AS records. They form one result and must remain together.

### 2.4 Claims, definitions, hypotheses, findings, limitations, and conclusions

The PRD defines four **functional roles**, not six content-type labels. It does not define a separate role for definitions, hypotheses, or conclusions. Do not add them to the role enum without approval.

| Source content | Contract treatment | Role/origin handling |
|---|---|---|
| Definition | Include if it is a research-relevant source claim needed for independent interpretation. Preserve the defined term and scope. | Likely `BACKGROUND` is a proposal; confirm in the product contract. |
| Hypothesis | Preserve as a proposed or tested statement with its modality and population. Do not relabel a hypothesis as a finding. | `METHOD` may fit a stated study hypothesis, but the PRD does not specify the mapping. **Open.** |
| Primary result/finding | Preserve the outcome, direction, comparator, population, timeframe, units, denominator, and uncertainty as reported. | `FINDING` + `PRIMARY_FINDING` when the focal paper reports its own result. |
| Claim/interpretation | Retain only if source-supported and independently intelligible; distinguish data from author interpretation. | Use one of the four roles based on function; origin may be `AUTHOR_INTERPRETATION`. Exact role assignment is **Open** where unclear. |
| Limitation | Preserve what the authors say was not measured, could bias the result, restricts generalization, or remains uncertain. | `LIMITATION`; source origin is usually `AUTHOR_INTERPRETATION`, but confirm where the paper reports a measured constraint. |
| Conclusion | Capture only when it states a source-supported reusable claim. Do not create an additional `CONCLUSION` role. | Map to `FINDING`, `BACKGROUND`, or `LIMITATION` only by its function; mapping policy is **Open**. |
| Report of prior work | Keep the current paper as the source of the report and retain citation markers; do not imply verification of the cited primary paper. | `REPORTED_PRIOR_WORK`, never `PRIMARY_FINDING` for the focal paper. |

## 3. Source and generated-item distinctions

| Object | Meaning | Mutability and required links |
|---|---|---|
| **Original source sentence** | Exact sentence text from the parsed source representation, with source document version, section/paragraph, offsets, and page when available. | Immutable. Keep its original punctuation and wording. |
| **Extracted candidate** | A machine-selected claim/evidence item, usually drawn from one sentence and its paragraph context. It may be absent even when a paragraph contains no suitable claim. | Pending item with exact quote/span, run provenance, and candidate ID. Never overwrite source text. |
| **Proposed atomic statement** | A short standalone wording expressing one main proposition from the candidate. It can quote or restate the source but remains generated output. | Each atom gets a separate ID and source link; one source sentence may produce multiple atoms. Preserve original source quote separately. |
| **Context-completed statement** | A proposed atom in which a source-supported pronoun, implicit referent, condition, or other necessary context is made explicit. | Store completion separately from source text and link every added referent/condition to evidence spans. If ambiguity remains, set `NEEDS_CONTEXT`. |
| **Human-verified statement** | An AS for which an authorized reviewer has confirmed the exact source and claim support against the original PDF and required quality criteria. | Immutable after approval. Any substantive edit requires a new candidate/version and a new verification event; retain prior history. |

## 4. Hedge and uncertainty annotations

### 4.1 Three different tasks

The CoNLL-2010 paper separates **sentence-level uncertainty classification** from **cue detection** and **in-sentence scope resolution**. They must not be stored as one “hedge” field.

1. **Sentence-level uncertainty:** one label for a whole sentence (proposed values `UNCERTAIN`, `CERTAIN`, `UNKNOWN`). In the CoNLL task, this is binary classification; the paper’s benchmark convention treats sentences containing an annotated hedge/weasel cue as uncertain. That convention is corpus/task-specific, not a claim that every implicit uncertainty is always cue-triggered.
2. **Cue detection:** zero or more exact spans identifying the minimal lexical unit that expresses hedge force. One cue can be a phrase rather than a word.
3. **Scope resolution:** a span linked to a cue, covering the uncertain content interpreted under that cue. Scope can differ from the cue span and can overlap another scope.

The CoNLL paper evaluated Task 1 at sentence level with F1 for the uncertain class; Task 2 used scope-level F1 requiring matching cue and scope boundaries. Cue-only scores were reported separately. A sentence-classification result therefore cannot substitute for cue/scope annotation, and a cue/scope result cannot by itself establish a sentence-level label.

### 4.2 Cue and scope rules

**[Research]** CoNLL lists potential cues including auxiliaries (`may`, `might`, `could`), verbs with speculative content (`suggest`, `seem`), adjectives/adverbs (`likely`, `possibly`), conjunctions, and multiword expressions. It also warns that these forms are not automatically hedges in every context. Its annotation uses a “minimum cue / maximum scope” convention: mark the smallest unit carrying the hedge force and the largest syntactic unit under the uncertain interpretation. The cue and scope are consecutive text spans in that dataset, and one scope is linked to each cue. Nested or overlapping scopes can occur.

**[Proposal]** Each hedge annotation stores:

- `cue_span`: exact start/end offsets and cue text;
- `scope_span`: exact start/end offsets and scope text, independently checked;
- `sentence_uncertainty`: whole-sentence decision, separate from both spans;
- `cue_type` / `scope_status`: versioned labels and an explicit ambiguous/unresolved value;
- optional rationale and supporting context span;
- annotation scheme version and annotator/model provenance.

For a phrase that functions as a single cue, mark the phrase rather than assigning an independent cue to each word. For overlapping cues, keep separate cue IDs and linked scopes. Do not force disjoint scopes when the evidence supports overlap. Punctuation and parenthetical citation boundaries should follow one annotation convention in the gold set; CoNLL notes that strict boundary matching is arguable and can penalize minor boundary differences.

**Research example (short excerpt):** In the CoNLL example “Mild bladder wall thickening **raises the question of** cystitis,” the phrase “raises the question of” is the cue; the uncertain diagnostic content extends into “cystitis.” This illustrates why the cue is not the entire scope. [CoNLL-2010, PDF pp. 2–3, §3.1.]

### 4.3 Contextual disambiguation

Do not label a word solely because it appears in a cue lexicon. Confirm its function in context. For example, `may` is a hedge when it marks epistemic possibility (“The treatment may reduce symptoms”), but not when it is a month or a proper name. A reporting verb such as `suggest` can introduce a source’s tentative interpretation, but the relevant scope and whose commitment it expresses must be resolved from the sentence and context. When annotators cannot decide whether a form functions as a hedge, retain an ambiguous/unresolved annotation for adjudication rather than guessing.

When atomizing a hedge-bearing sentence, preserve its cue force and scope. Do not remove a hedge merely to shorten the AS. If the uncertainty scope applies to only one clause, do not spread it to a factual clause; if a single hedge scopes over multiple coordinated claims, preserve that relationship or keep linked scope evidence.

## 5. Hyland stance and engagement taxonomy

Hyland presents two related but distinct writer-reader dimensions: **stance** is the writer’s attitudinal positioning, judgments, opinions, and commitments; **engagement** is the writer’s alignment with and positioning of readers. Forms can serve more than one function, and function is contextual. Do not collapse these categories into sentiment, tone, or a single interpersonal score. [Hyland 2005, supplied PDF pp. 5–15.]

The examples below are constructed to illustrate annotation and are not quotations from Hyland.

### 5.1 Stance

| Category | Definition and communicative function | Typical indicators | Constructed example | Evidence and ambiguous cases |
|---|---|---|---|---|
| **Hedges** | Reduce full commitment or present a proposition as plausible rather than certain; can open space for reader evaluation. | Epistemic `may`, `might`, `could`; `possibly`, `likely`; reporting verbs such as `suggest` or `appear`. | “The intervention may reduce repeat admissions.” | Mark the cue and, if the hedge layer is enabled, its scope. `May` can be temporal or lexical rather than epistemic; `suggest` may report a method rather than hedge a claim. |
| **Boosters** | Strengthen the writer’s expressed certainty/commitment and may signal solidarity around shared information. | `clearly`, `obviously`, `demonstrate`, `show`, `indeed`. | “The measurements clearly show a decline.” | Annotate the proposition the booster strengthens. `Show` can be a literal perceptual/reporting verb without an emphatic interpersonal function. |
| **Attitude markers** | Express affective or evaluative stance toward a proposition (for example importance, surprise, agreement, or frustration), rather than epistemic certainty. | Attitude verbs (`agree`, `prefer`), adverbs (`unfortunately`, `remarkably`), adjectives (`important`, `unexpected`). | “The unexpectedly large decline warrants follow-up.” | Link marker to its evaluated proposition. Some adjectives describe a measured property rather than the author’s attitude. |
| **Self-mention** | Make the author’s presence explicit and signal authorial identity, responsibility, or perspective. | First-person pronouns and possessives (`I`, authorial `we`, `our`). | “We recruited participants at three clinics.” | Determine whether `we` refers to authors, authors plus readers, researchers generally, or people in the world. A pronoun alone is not enough to identify self-mention. |

### 5.2 Engagement

| Category | Definition and communicative function | Typical indicators | Constructed example | Evidence and ambiguous cases |
|---|---|---|---|---|
| **Reader pronouns** | Explicitly acknowledge readers or include them as participants in the argument. Inclusive `we` can construct shared goals/understanding. | `you`, `your`, inclusive `we`, `us`, `our`. | “We can now compare the two estimates.” | Distinguish inclusive writer-reader `we` from author-only `we`, generic `we`, or a real-world group. `Our participants` is not reader engagement. |
| **Directives** | Guide readers to perform an action or adopt a way of seeing/interpreting something. Hyland distinguishes textual, physical, and cognitive directions. | Imperatives (`consider`, `note`), reader-directed obligation (`should`, `must`), necessity/importance constructions. | “Consider the baseline difference before interpreting the effect.” | Confirm that the addressee is the reader. A method instruction addressed to study participants is not automatically reader engagement. |
| **Questions** | Bring readers into a dialogic issue or anticipate objections; many academic questions are rhetorical and expect no answer. | Interrogative clauses, including immediately answered or rhetorical questions. | “Why might the groups differ at follow-up?” | Distinguish a question discussed as study content from one that positions the reader. Record whether it solicits an answer, is rhetorical, or is unresolved when known. |
| **Appeals to shared knowledge** | Explicitly invite readers to recognize information as familiar, accepted, or shared within a discourse community. | `of course`, `as is well known`, `obviously`, explicit `we know`. | “As is well established in this field, follow-up loss can bias estimates.” | The same wording can be a booster or ordinary claim. Label engagement only when it appeals to assumed common ground; overlap with stance may be retained. |
| **Personal asides** | A brief interruption that addresses the reader or makes an interpersonal comment, building a writer-reader connection beyond the proposition’s content. | Parenthetical or dash-delimited comments, interjections, brief direct address. | “The estimate—surprisingly, given the small sample—was stable.” | Parentheses can contain citations, definitions, methods, or essential qualifications rather than an aside. Determine the discourse function in context. |

### 5.3 Annotation evidence and overlap

For each stance/engagement label, store the exact marker span, the proposition or discourse span it affects, and a short function note or adjudication rationale. Labels should be multi-dimensional: one token may express a hedge and also contribute to engagement, but the two tags answer different questions. Keep primary and secondary functions when the annotation protocol permits; do not resolve every overlap by forcing one exclusive class.

Hyland’s framework is grounded in a corpus of 240 research papers across eight disciplines and highlights disciplinary variation. Its frequency findings are not universal thresholds or a model of every field. **[Open]** Whether the product supports multi-label annotations, a primary-function field, or both requires an explicit label policy.

## 6. Metadiscourse frameworks and analysis approaches

The supplied collection describes two **definitional models** and two **analytical approaches**. They are related in the literature but are not interchangeable axes or per-sentence labels. [Ädel & Mauranen, “Metadiscourse: Diverse and Divided Perspectives,” supplied PDF pp. 4–6 and 11–12; Ädel, “A Taxonomy of Metadiscourse in Academic English,” supplied PDF pp. 72, 77, 81, 84.]

| Dimension | Approach | Meaning and evidence | Limitation/relevance |
|---|---|---|---|
| **Definition** | **Interactive model** | Broadly treats metadiscourse as writer-audience interaction. Depending on the taxonomy, features such as hedges, connectives, or reader-oriented markers can count as metadiscourse because of their interpersonal/textual functions. | Useful for examining reader positioning and textual interaction. A form’s inclusion does not itself establish its specific contextual function. |
| **Definition** | **Reflexive model** | Narrower: metadiscourse requires explicit language that refers reflexively to the evolving discourse, its linguistic form, current discourse participants, or the communicative event. It asks whether the language is discourse-internal and about the current text/event. | A pronoun, hedge, or connective is not automatically metadiscourse; contextual criteria matter. It may exclude interactional features that the interactive model includes. |
| **Method** | **Thin approach** | Quantitatively retrieves a predefined list of forms and often counts them without contextual review. Unit of analysis is fixed in advance and relatively decontextualized. | Scales to larger corpora and supports frequency/distribution comparison, but can be superficial, static, miss off-list items, and assume a form has a stable function. |
| **Method** | **Thick approach** | Retrieves candidates, filters irrelevant uses, and examines larger contextual units, co-occurrence patterns, or discourse functions. | Provides context-sensitive function analysis but usually covers fewer categories/items and requires more manual interpretation. |

**Relationship:** The editors report that the interactive model tends to align with the thin approach and the reflexive model tends to align with the thick approach. They also describe mixed studies and an intermediate research-activity model. Therefore, an implementation or evaluation must record the selected **definition lens** and **analysis method** independently. It must not emit `INTERACTIVE`, `REFLEXIVE`, `THIN`, or `THICK` as though they were interchangeable sentence labels.

**Relevance to Atomic Sentence:** Metadiscourse can help characterize how source sentences position claims and readers, but the PRD does not require a metadiscourse module. The present taxonomy is a research-grounded proposal requested by QA-01; its product inclusion, preferred definition, and whether analysis is thin, thick, or mixed remain open. Do not treat Hyland stance/engagement labels as an automatic substitute for either metadiscourse model.

## 7. Context completion and source support

**[PRD]** Complete an ambiguous anaphor only when supplied context supports the exact referent. Make implicit entities explicit only when doing so remains within the word limit and does not add a claim. If context cannot resolve the referent, use `NEEDS_CONTEXT`; do not use general knowledge to fill the gap.

For each completed statement:

1. Retain the original sentence and candidate wording unchanged in separate fields.
2. Store the completed wording as generated text.
3. Link each substituted pronoun, implicit actor, condition, comparison group, or time reference to the exact supporting sentence/span and paper checksum.
4. Keep the source’s scope, modality, negation, measurement, units, denominator, comparison, and temporal limits.
5. Flag additions without evidence as `UNDETERMINED` or `CONTRADICTED` (as appropriate) in precheck and do not present them as completed facts.
6. If context requires more than 25 words, split only if meaning remains complete; otherwise leave `NEEDS_CONTEXT` for reviewer handling.

**Constructed example:** Source: “These results were stable at 12 months.” If the adjacent source paragraph identifies “these results” as a named outcome, a completion may replace the pronoun with that exact outcome and cite its span. If the antecedent is not explicit, do not guess from the abstract or outside literature.

The automated support values are `SUPPORTED`, `PARTIAL`, `CONTRADICTED`, and `UNDETERMINED`. They are advisory precheck results, not verification states. [PRD §6 P6; §8 BR-06.]

## 8. Human verification rules

- A reviewer must inspect the linked original PDF and determine that the exact source supports the entire AS, including qualifiers and numbers. **[PRD §6 P7]**
- Record reviewer identity, timestamp, action, and required rejection rationale. The PRD also calls for approval identity/time and audit history. **[PRD §5.2; §8 BR-09; §9.1]**
- AI support status, cue detection, taxonomy labels, or SPS cannot assign `VERIFIED`. **[PRD §6 P6–P7; §8 BR-06]**
- Rejected content is immutable. `REGENERATE` creates a new candidate ID linked to the rejected parent; it does not change the rejection. **[PRD §8 BR-07]**
- Once verified, AS text and evidence links are immutable. Any change needs a new version/candidate and a new human verification. **[PRD §6 P7; §8 BR-09]**
- An item without a resolvable evidence span or an authorized human review event is excluded from the trusted library. **[PRD §8 BR-05–06; §14 AT-07]**
- Whether one reviewer is sufficient, whether a second review is mandatory, the identity source for reviewers, and a distinct request-revision action are unresolved. See [open decisions](open-decisions.md).

## 9. Requirement traceability

| Requirement/concept | Origin | Source location / concept |
|---|---|---|
| Independent readability, semantic completeness, recomposability, ≤25 words, bibliographic role tag | PRD | §1 Executive Summary; §3 Semantic completeness, independent readability, recomposability, length, metadata and role rows. |
| Detect claims, 1:N atomization, preserve qualifiers and context | PRD | §2.3 G1–G4; §6 P2–P4; §7 FR-02–04; §14 AT-01–06. |
| Exactly four roles and four evidence origins | PRD | §6 P5; §7 FR-05; §9.1; §8 BR-08. |
| Source anchor, checksums, role, reviewer, audit provenance | PRD | §6 P1, P5–P8; §7 FR-06, FR-12; §8 BR-05. |
| Support labels, AI precheck advisory only | PRD | §6 P6; §7 FR-07; §8 BR-06. |
| Reject rather than silently edit; regenerate as new ID | PRD | §1; §6 P7; §7 FR-09; §8 BR-07, BR-09. |
| Sentence uncertainty differs from cue/scope task | Research | Farkas et al., [CoNLL-2010 PDF](../research/W10-3001.pdf), PDF pp. 1, 4–5; §4.1–4.3 separates sentence classification from linked cue/scope spans and evaluates them differently. |
| Minimal cue, maximal syntactic scope; phrase cues and contextual ambiguity | Research | CoNLL-2010 PDF pp. 2–4; §3.1 and §4.2. Scope principles were developed for its annotated domains and require validation for the product corpus. |
| Stance vs engagement and nine category names | Research | Hyland 2005, [supplied PDF](../research/Stance_and_engagement_a_model_of_interac.pdf), PDF pp. 5, 7–15. Definitions, category functions, contextual overlap, and discipline variation. |
| Interactive/reflexive model distinction | Research | Ädel & Mauranen, [collection PDF](../research/Metadiscourse_Diverse_and_Divided_Perspectives.pdf), PDF pp. 4, 11; Ädel chapter PDF pp. 72, 77, 81. |
| Thin/thick methodological distinction; models are correlated but not equivalent | Research | Ädel & Mauranen, collection PDF pp. 4–6, 11–12. Thin list retrieval vs thick contextual filtering/function analysis; mixed approaches and an intermediate study are described. |
| Map definition/hypothesis/conclusion into four PRD roles | Proposal / open | PRD defines only `BACKGROUND`, `METHOD`, `FINDING`, `LIMITATION`; no separate roles for definition, hypothesis, or conclusion. Mapping proposals in §2.4 require approval. |
| Annotation overlap, language support, reviewer count, rubric dimensions | Open | PRD §5, §8, §12, §18; exact SPS dimensions/weighting and review count are not defined by the supplied materials. |

### Bibliographic references

- Liu S-W, Chu S-Y, Wang H-C, Lee M-S. *Teaching the Atomic Sentence Method for Source-Verified, AI-Assisted Literature Synthesis to Clinical Health Care Professionals: Single-Cohort Feasibility and Acceptability Study*. PRD primary method source, cited as JMIR Form Res. 2026;10:e98343. The supplied PRD notes that Multimedia Appendix 1 with the detailed SPS rubric was not retrieved.
- Farkas R, Vincze V, Móra G, Csirik J, Szarvas G. *The CoNLL-2010 Shared Task: Learning to Detect Hedges and their Scope in Natural Language Text*. Proceedings of CoNLL 2010 Shared Task, pp. 1–12.
- Hyland K. “Stance and engagement: a model of interaction in academic discourse.” *Discourse Studies* 7(2), 2005, pp. 173–191. Page references above use the supplied PDF pagination.
- Ädel A, Mauranen A. “Metadiscourse: Diverse and Divided Perspectives.” Supplied collection PDF, pp. 1–11 for the introduction; Annelie Ädel’s “A Taxonomy of Metadiscourse in Academic English,” collection PDF pp. 69–97.
