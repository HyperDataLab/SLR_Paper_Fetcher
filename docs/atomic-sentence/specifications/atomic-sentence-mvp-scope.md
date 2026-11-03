# Atomic Sentence MVP Scope Proposal

**Status:** Proposed for product-owner review; no decision is approved.  
**Purpose:** Define a minimum useful Atomic Sentence workflow within the existing SLR Paper Fetcher.  
**Authority:** The supplied Atomic Sentence PRD v1.0 controls explicit requirements. QA-02 recommendations clarify the MVP boundary and remain subject to approval.

## MVP objectives

The MVP should let a researcher select an existing paper, inspect source-grounded candidate claims and short standalone statements, verify each item against the original paper, and retrieve only currently verified statements by default.

Atomic Sentence is a new feature module in the current application. It is not a replacement paper catalog, downloader, analysis pipeline, PDF viewer, or external SLR System. It does not synthesize claims across papers or produce manuscript prose.

## A. MVP — Required

The MVP must retain all PRD P0 requirements FR-01 through FR-13. The following list interprets those requirements for the existing application; it does not waive any of them.

### Paper selection and source readiness

- Reuse the existing paper catalog and selected paper's saved, validated PDF. Do not create a second paper catalog or duplicate the PDF.
- Reuse an available GROBID full-text mapping only when it identifies the same PDF SHA-256 and passes the current mapping/offset checks. Keep the original PDF and mapping immutable.
- For the first operational workflow, process selectable-text PDFs with usable mapped text and retained original PDF. The PRD also allows already-parsed structured paper JSON when its source identity and original PDF verification path are preserved.
- Preserve paper/section/paragraph order, exact mapped source text, offsets, page spans where available, and extraction warnings. Create stable source-sentence units as an additive index.
- Flag missing mappings, unreliable OCR, unreadable scans, unaligned tables/captions, or source-hash mismatch. Such inputs cannot be silently treated as review-ready.

### Candidate extraction and semantic atomization

- Read source content only. Consider paragraph text, section heading, and immediate neighboring context. Allow zero, one, or multiple research-relevant candidates per paragraph.
- Retain the exact source sentence and evidence span separately from any generated statement.
- Permit one candidate to yield zero, one, or multiple proposed Atomic Sentences. Each proposed AS states one main independently verifiable proposition and is no more than 25 words under the PRD English counting rule.
- Preserve population, time horizon, intervention/exposure, measure, units, numerator/denominator, comparison, direction, negation, causality limits, conditions, and uncertainty. Do not invent a claim from general knowledge.
- Complete a pronoun or implicit referent only when supplied paper context supports it. Link the supporting source context. If the referent or condition remains ambiguous, mark NEEDS_CONTEXT.
- Distinguish a generated/context-completed statement from the paper's exact wording. Do not replace the original sentence or quote.

### PRD roles, evidence origins, and provenance

- Use only the PRD roles: BACKGROUND, METHOD, FINDING, LIMITATION.
- Use only the PRD evidence origins: PRIMARY_FINDING, REPORTED_PRIOR_WORK, AUTHOR_INTERPRETATION, METHOD_DESCRIPTION.
- Store role and origin separately. Do not map the existing paper-analysis proposition type or Toulmin/AIF role into the Atomic role field.
- Attach at least one exact source span to every reviewable AS. Allow supporting context spans when needed; display primary claim evidence separately from context evidence.
- Retain paper identity, source PDF checksum, source mapping/version, section/page or best available locator, exact quote, candidate/run lineage, and model/prompt/parser provenance.
- When the focal paper reports a cited study, retain REPORTED_PRIOR_WORK and original citation markers. A reviewer can verify that the focal paper reports the claim, not that the cited study itself proves it.

### AI precheck and human verification

- Save a preliminary support result of SUPPORTED, PARTIAL, CONTRADICTED, or UNDETERMINED with an explanation. Include deterministic checks for word count, valid evidence links, source identity, schema completeness, and quote/offset consistency.
- Treat all AI findings as advisory. No automated action can set VERIFIED.
- Present the proposed AS next to its exact source quote, surrounding paragraph, paper metadata, and original PDF/page/highlight where available.
- Require a trusted human reviewer identity, verification action, time, and a record of the source version reviewed. If reviewer identity is unresolved, the item cannot be published.
- Make rejected candidates immutable. Regeneration creates a new candidate/AS ID linked to the rejected record. Any material edit to verified wording or evidence requires a new version/candidate and a fresh human verification.
- Record quality review in accordance with PRD FR-10. Until the SPS appendix is available, do not invent dimension names or weights, calculate an official score, or treat an informal rubric as comparable. A manual score must include rubric provenance.

### Verified library, search, and export

- The library returns only VERIFIED items by default and excludes rejected, pending, stale, and superseded records.
- Provide search/filtering at minimum for claim text, paper, author/year, section, role, evidence origin, and verification status as specified by PRD FR-11.
- Keep REPORTED_PRIOR_WORK in the general verified library only with an explicit origin badge and citation marker. Do not present it as a focal-paper primary finding; allow a primary-findings view/filter to exclude it.
- Provide both JSON and CSV export as required by PRD FR-13. Include paper identity, claim text, role, evidence origin, source quote/span/locator, source version, evidence IDs, verification identity/time, and candidate lineage as available.
- Preserve existing search/acquisition, repository, analysis/review, PDF, graph, SAFFRON/OpenAlex, export, and optional SLR System workflows.

## Uncertainty preservation is not a hedge subsystem

The MVP must preserve uncertainty and modality while atomizing claims. A source statement that says “may,” “is associated with,” “did not assess,” or otherwise limits commitment must not become more certain, causal, or broad in the generated statement. Precheck should flag a dropped or altered qualifier, negation, or scope.

This semantic requirement does **not** require three separate linguistic outputs:

1. whole-sentence uncertain/certain classification;
2. exact hedge-cue detection;
3. cue-linked hedge-scope resolution.

The CoNLL paper treats these as distinct tasks with distinct annotations and evaluation. None is necessary to meet the PRD's minimum preservation rule. Defer the classifiers and span overlays until a separate product use case, annotation contract, and evaluation set are approved.

## B. MVP+ — Optional extensions

These capabilities can follow a working and evaluated MVP. Their deferral must not block FR-01–FR-13.

- Advanced search, ranking, near-duplicate detection, and additional filters beyond PRD FR-11.
- Evaluation/quality dashboards beyond required audit/export fields and pilot reports.
- Batch review, keyboard shortcuts, reviewer assignment, and richer disagreement workflow. PRD FR-15 is P1.
- Table/figure cell or region alignment. PRD FR-16 is P1 and current extraction quality is layout-dependent.
- Additional export formats beyond required JSON and CSV.
- Second-review workflows for an owner-defined risk subset; multiple annotator adjudication remains required for the research gold set, but not necessarily a multi-review product UI.
- Re-extraction/deduplication workflows beyond preserving run history and source staleness. PRD FR-14 is P1.
- A second uncertainty review or a future linguistic analysis panel, after a product owner defines the labels and evidence model.
- Optional SLR System synchronization only after the destination supports a confirmed Atomic payload. Local use must not depend on it.

## C. Deferred — Out of scope initially

- Full Hyland stance and engagement labeling. Hyland's categories are contextual and can overlap; they are not needed to establish an evidence-supported Atomic Sentence.
- Full metadiscourse annotation. The interactive/reflexive models and thin/thick methods are distinct research choices, not mandatory Atomic Sentence labels.
- Advanced hedge cue and scope annotation and sentence-level uncertainty classification. Preserve uncertainty semantically in MVP; do not claim these classifiers exist.
- Multilingual source processing or tokenization. For the initial pilot, propose English source and output only; non-English or mixed-language text must be flagged unsupported until separately defined and evaluated.
- Automatic OCR for scanned/unreadable papers. The repository has no configured OCR pipeline. The MVP may report unsupported/partial source status and require readable original evidence.
- Automated multi-reviewer adjudication interface. Use two independent annotators plus adjudication for the evaluation gold set; an operational MVP needs one authorized reviewer per item unless the product owner approves a stricter rule.
- Cross-paper synthesis, argument construction, manuscript writing, and automatic citation generation.

## Proposed user workflow

1. Select a paper from the existing local paper library.
2. Check PDF validity, mapping availability, PDF checksum, text coverage, and source-readiness warnings.
3. Index exact mapped source sentences and retain hierarchy, ordering, offsets, and page spans.
4. Generate zero or more research-relevant claim candidates from source text and local context.
5. Propose one or more short standalone statements; retain original source text and link every statement to exact evidence.
6. Complete only source-supported context; leave unresolved items in NEEDS_CONTEXT.
7. Run deterministic validation and advisory AI precheck; show support result, explanation, and warnings.
8. A reviewer opens the source excerpt/PDF, verifies support and wording, then records VERIFY or REJECT with identity, time, and reason as applicable.
9. Rejected material remains in history; regeneration creates a new ID. Verified material becomes immutable and eligible for current-source library search.
10. Search verified items and export JSON/CSV with source and reviewer provenance.

## Definition of Done

The first operational release is complete only when:

- The feature uses existing saved papers, PDFs, mapping artifacts, and application workspace; no duplicate catalog or altered existing workflow is introduced.
- PRD P0 FR-01 through FR-13 have implemented acceptance criteria and have been approved as the MVP contract.
- Every candidate and AS is tied to exact source evidence in a versioned source representation; source offsets round-trip to the exact quote.
- PDF checksum mismatch, unsupported extraction, and stale evidence prevent current verification/publication.
- Every verified AS is at most 25 words by the versioned PRD English tokenizer and preserves all material meaning, including uncertainty.
- Only the four PRD role values and four PRD evidence-origin values are emitted.
- AI precheck is advisory; a trusted human decision and identity/time event are required for VERIFIED.
- Rejected/verified text and evidence are immutable under the approved lineage rules.
- Verified-only default search excludes stale/rejected/pending entries, and origin labels are visible.
- JSON and CSV exports retain evidence, source version, role/origin, and verification provenance.
- Required regression and Atomic acceptance checks pass without breaking current SLR workflows.
- Pilot quality results include denominators, failures, and source coverage. PRD hard process gates are met; unapproved model targets are reported as targets, not guarantees.

## Functional acceptance criteria

| Area | Acceptance criterion |
|---|---|
| Source identity | A PDF checksum mismatch or unusable/missing mapping blocks current source processing or marks the run partial/stale with an actionable reason. |
| Segmentation | Each indexed sentence quote equals its exact source substring; paragraph/section/page locator is retained when available. |
| Candidate recall workflow | A paragraph can yield zero, one, or multiple candidates without a quota; candidate evidence is traceable. |
| Atomization | Compound claims split only when each result remains independently interpretable and supported; quantitative relations and essential comparisons/conditions stay intact. |
| Length | An AS over 25 words cannot be verified; count follows the documented English tokenizer version. |
| Context | Every added referent/condition has contextual evidence; unresolved references remain NEEDS_CONTEXT. |
| Roles/origins | Outputs use only allowed PRD enums and keep role distinct from evidence origin. |
| Precheck | Verdict is one of SUPPORTED, PARTIAL, CONTRADICTED, UNDETERMINED; its rationale and implicated spans are stored; no precheck writes VERIFIED. |
| Human review | A reviewer can inspect exact text and the original PDF, confirm/reject, and see the review record. |
| Rejection/edit | Reject requires a reason; regeneration creates a new ID and parent link; modifying verified content requires fresh verification. |
| Library | Default query returns only current VERIFIED records; REPORTED_PRIOR_WORK remains visibly distinct. |
| Export | JSON and CSV include claim text, source/evidence locator, role/origin, and reviewer/time provenance. |
| SPS | No automatic or “official” score is produced without the supplied/approved rubric; any manual total is versioned. |

## Non-functional acceptance criteria

- **Integrity:** Every verified item has source traceability and human verification (100% hard gates in PRD); no verified item exceeds 25 words.
- **Reproducibility:** Record PDF/mapping/segmenter, model/provider, prompt/schema, tokenizer, and run versions required to explain output.
- **Auditability:** Preserve item lineage, source version, reviewer action, timestamp, reason, and edit/reverification history.
- **Security:** Verification and library access respect the approved identity and paper-access policy; avoid copying full text into logs.
- **Resilience:** Partial or failed paragraph/run processing is explicit and does not invalidate prior review history.
- **Accessibility:** Source evidence is text-selectable where possible; review actions are keyboard-accessible and status is conveyed with text as well as color.
- **Performance:** Record the PRD's 5,000-word/two-minute goal as a pilot benchmark. It is not a guarantee until measured on defined infrastructure.
- **Compatibility:** Existing paper acquisition, PDF display, analysis, review, graph, export, enrichment, and repository workflows remain usable and their stored results remain readable.

## Known limitations

- The JMIR paper cited as the primary method source and its SPS appendix were not supplied with the research pack. Do not claim independent validation of that source or infer the SPS dimensions.
- GROBID mapping/page anchors may be incomplete for tables, equations, scans, and layout-dependent content. The app has no configured OCR pipeline.
- The current repository uses a local SQLite workspace, a single in-process analysis worker, and reviewer attribution that defaults to local-user; collaboration and throughput need explicit design.
- The existing mapping is pinned to the source PDF checksum, but Atomic document/run records and an Atomic mapping/segmenter version do not yet exist.
- The existing proposition/argument analysis is not Atomic Sentence functionality and must remain separate.
- Linguistic labels deferred from MVP will not be available for search, statistics, or export.
- Non-English use is not defined by the PRD's English word-count rule and is not included in this proposal's pilot boundary.

## Sources and traceability

- PRD v1.0 §§5–9 defines inputs, P1–P8 workflow, FR-01–FR-16, business rules, source model, and lifecycle.
- PRD §§12–14 defines metric targets, performance goal, and acceptance scenarios.
- CoNLL-2010 supplied PDF pp. 1–5 distinguishes sentence uncertainty from cue/scope tasks and describes its dataset annotation.
- Hyland 2005 supplied PDF pp. 5–15 defines stance/engagement categories and pp. 17–21 discuss context/disciplinary variation.
- The supplied metadiscourse collection PDF pp. 3–6 and 11–12 distinguishes interactive/reflexive models and thin/thick approaches.
- Existing application evidence is summarized in the repository audit and architecture proposal; those documents are proposals/audit notes, not implemented Atomic behavior.
