# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Atomic Sentence Extraction & Verification — Paper Understanding

| Field | Value |
|---|---|
| Version | 1.0 — 03 November 2026 |
| Module | Atomic Sentence (AS) |
| Parent product | Paper Understanding |
| Scope | Independent module; no dependency on Writing or Argument Construction |
| Status | Proposed MVP specification |
| Primary scientific basis | Liu S-W, Chu S-Y, Wang H-C, Lee M-S. *Teaching the Atomic Sentence Method for Source-Verified, AI-Assisted Literature Synthesis to Clinical Health Care Professionals: Single-Cohort Feasibility and Acceptability Study*. JMIR Form Res. 2026;10:e98343. https://doi.org/10.2196/98343 |

> **Source policy:** The JMIR paper above is the only methodological source for this PRD. Items marked **[Paper]** are explicitly described in that paper. Items marked **[Design]** are proposed software-engineering requirements or operationalizations, not findings or validated thresholds from the paper. Multimedia Appendix 1, which contains the detailed SPS rubric, was linked in the article but could not be retrieved for this specification.

## 1. Executive Summary

The module transforms each scientific paper into a searchable, source-verifiable library of **Atomic Sentences (AS)**: short, independently intelligible, semantically complete knowledge units whose claims can be checked against specific original-source spans. The core workflow is:

`Paper → Structure/Anchors → Candidate Claims → Semantic Atomization → Context Completion → Preliminary Verification → Human Review → Verified AS Library`

**[Paper]** A valid AS is semantically complete, independently readable (a new reader can accurately paraphrase it within 30 seconds), recomposable with other units, and at most 25 words long. It is tagged with `Author | Year | Page | Functional role (Background / Method / Finding / Limitation)`. AS quality is assessed by the 9-point Semantic Purity Score (SPS) across five dimensions. Every claim or statistic must be manually cross-checked against the original PDF. Unverifiable units are discarded, rather than repaired in place.

**[Design]** AI may identify, generate, classify, and pre-check candidates, but cannot finalize verification. A human reviewer must explicitly approve a candidate before it receives `VERIFIED` status. Every approved AS retains immutable source provenance and a verification record.

## 2. Problem & Opportunity

### 2.1 Problem
- A paper contains claims within long, compound sentences and paragraphs, often with implicit subjects, comparisons, study populations, conditions, numerical denominators, and limitations.
- Generic paper summaries can lose data-bearing detail. Merely storing a DOI or citation cannot demonstrate that the article supports a specific statement.
- AI-generated restatements may overstate the results, remove uncertainty, merge unrelated claims, or incorrectly turn cited prior work into findings from the focal paper.
- Reviewers require an efficient view that places the AS beside its exact source evidence and preserves an audit trail.

### 2.2 Desired outcome
Build a verified, reusable, searchable paper-level knowledge layer without performing literature synthesis or generating manuscript prose in the MVP.

### 2.3 Goals
- G1: Detect research-relevant claim candidates from parsed paper content.
- G2: Split compound statements into single-main-claim AS units of ≤25 words.
- G3: Preserve the complete proposition, including subject, scope, qualifiers, units, comparisons, and denominators.
- G4: Attach each AS to exact original evidence and paper metadata.
- G5: Classify each AS by one of four functional roles described in the paper.
- G6: Support human source verification with an explicit reject-and-regenerate policy.
- G7: Search, filter, inspect, and export the verified library.

### 2.4 Non-goals (MVP)
- Multi-paper synthesis; constructing Toulmin/AIF arguments; rhetorical writing or sentence polishing.
- Automatically issuing citations for generated writing.
- Fact-checking other papers cited inside the input paper.
- Guaranteeing absence of hallucinations or reporting a proven citation-accuracy improvement.
- Replacing human source verification.
- Treating the paper's reported workshop Cohen κ=0.77 as model accuracy; this κ concerns human classification of research-topic transformations, **not** AS detection.

## 3. Scientific Requirements vs Engineering Interpretations

| Principle | Origin | Implementation rule |
|---|---|---|
| Semantic completeness | [Paper] | AS understandable outside source paragraph; explicit subject and important qualifiers. |
| Independent readability | [Paper] | Human review question: can an unfamiliar researcher paraphrase the AS accurately within 30 seconds? |
| Recomposability | [Paper] | Unit carries one main testable/reusable proposition; compatible with other independently intelligible units. |
| Length ≤25 words | [Paper] | Hard validation for AS approval; 18–22 words may be useful but is **not** a mandatory interval. |
| Author, year, page, functional role | [Paper] | Persist metadata; if source has no page (HTML), use section and character anchor and mark `page=null` pending PDF alignment. |
| Four functional roles | [Paper] | Enumerated: BACKGROUND, METHOD, FINDING, LIMITATION. |
| SPS: 9 points, 5 dimensions | [Paper] | Store dimension assessments and optional reviewer-supplied 0–9 score. Do **not** invent the official allocation without appendix. |
| Source anchoring | [Paper] | Candidate may be generated only from loaded original content. |
| Cross-reference verification | [Paper] | Reviewer opens the original PDF and checks that the linked location supports the precise claim. |
| Discard, not edit | [Paper] | Reject a failed candidate; regenerate a new candidate ID from evidence. Never silently overwrite rejected claim. |
| One main proposition | [Design] | Operational definition of atomicity for automated splitting, not a fourth criterion attributed to the paper. |
| Source provenance granularity | [Design] | Paper → section → paragraph → text span (+ page/bbox when available). |
| Evidence-origin classification | [Design] | Differentiate original findings, source-reported prior studies, author interpretation, and method description. |

## 4. Users & User Jobs

| Actor | Job | Access |
|---|---|---|
| Researcher / Reviewer | Inspect AS and source side-by-side; verify or reject; search trusted library | Review, verify, export |
| Research assistant / Annotator | Trigger extraction and triage candidate claims | Generate, classify, submit for review |
| Module administrator | Configure extraction defaults, monitor quality and audit history | Configuration, metrics, reprocessing |
| Downstream system | Query approved AS with traceable evidence | Read-only `VERIFIED` API |

## 5. Inputs, Outputs & Assumptions

### 5.1 Input
- Required: `paper_id`, paper content (parsed paragraphs or uploaded full text/PDF), stable source identity.
- Desired: title, authors, year, DOI, section headings, page numbering, paragraph order, citation markers, table/figure captions, precise text positions.
- Supported in MVP: PDF with selectable text, and already-parsed structured paper JSON. HTML input can work with paragraph/character anchors; PDF-level verification requires original PDF availability.
- Unsupported or flagged: OCR-only sources with unreliable text, unreadable scans, missing provenance, or tables whose layout is not preserved. Such evidence cannot become `VERIFIED` until a reviewer confirms against the original PDF.

### 5.2 Output
- Candidate AS collection with candidate IDs and extraction metadata.
- Verified AS collection with exact source anchors, classification, quality reviews, approval identity and time.
- Rejected candidate log including reason and link to a newly generated replacement if any.
- JSON/CSV export and filtered search results.

## 6. End-to-End Processing Pipeline

### P1. Paper ingestion & segmentation
- Parse paper hierarchy: `Paper → Section → Paragraph → Sentence`, preserving ordering and original character offsets.
- Identify tables/captions and mark limitations of extraction where text is non-linear.
- Resolve title/authors/year/DOI from metadata. Never fill unavailable fields with guessed values.
- Generate stable span IDs and source checksums.

### P2. Candidate detection
- Scan paragraph-level text with the current section heading and immediate contextual neighbors.
- Find research-relevant facts/claims: scientific background, methods, empirical findings, limitations.
- Distinguish assertions from questions, navigation text, references-only lines, boilerplate, and headings.
- Permit a paragraph to contain zero, one, or multiple candidate claims; no fixed quota.

### P3. Semantic atomization
- Split compound statements where separate propositions can remain complete and independently verifiable.
- Preserve negation, hedges, modality, populations, interventions, measurements, numbers, units, comparisons, confidence/uncertainty, and study context.
- Avoid splitting a numerator from its denominator, a finding from its essential condition, or a comparison from its reference group.
- Do not add claims that are only plausible from general knowledge.

### P4. Context completion
- Replace ambiguous anaphora (e.g., `this study`, `these results`, `it`) with the precise source referent **only if the provided context supports it**.
- Complete implicit entities while staying within 25 words; otherwise split further or flag for review.
- If ambiguity is unresolved, mark `NEEDS_CONTEXT` rather than inventing content.

### P5. Metadata and origin labeling
- Assign `role`: BACKGROUND / METHOD / FINDING / LIMITATION.
- Assign `evidence_origin`: PRIMARY_FINDING / REPORTED_PRIOR_WORK / AUTHOR_INTERPRETATION / METHOD_DESCRIPTION.
- Record exact source spans plus original citation marker(s) if present.
- Note: `REPORTED_PRIOR_WORK` can establish only that the current paper *reports* a claim, not whether the prior work supports it.

### P6. Preliminary automated validation
- Check `word_count <= 25`, schema completeness, valid evidence span, source checksum, and allowed role.
- Assess semantic support against the provided source only. Distinguish `SUPPORTED`, `PARTIAL`, `CONTRADICTED`, `UNDETERMINED` with an explanation.
- Flag numeric mismatches, unit conversions not present in the source, scope inflation, dropped uncertainty, ambiguous actors, and missing comparisons.
- AI verdict is **advisory**; it can never assign `VERIFIED`.

### P7. Human cross-reference review
- Present AS, source text highlighted in the original PDF, paper metadata, and checks side by side.
- Reviewer chooses `VERIFY` only if exact source existence and support are confirmed and the AS passes the quality criteria.
- On failure choose `REJECT`, mandatory reason, and optional `REGENERATE` as a separate new candidate.
- After approval, AS text and evidence linkage become immutable. Revisions require a new candidate and a new human review.

### P8. Library indexing
- Index `VERIFIED` entries for full-text search by claim, role, section, paper, author/year, evidence origin and verification status.
- Keep candidate/rejected records visible to reviewers but excluded by default from trusted retrieval.

## 7. Functional Requirements

Priority: P0 = must-have for MVP; P1 = next iteration.

| ID | Requirement | Priority | Acceptance summary |
|---|---|---|---|
| FR-01 | Paper intake and traceable segmentation | P0 | Each paragraph has stable ID + exact source text. |
| FR-02 | Candidate claim detection | P0 | Zero-to-many candidates per paragraph; location stored. |
| FR-03 | 1:N atomization | P0 | Distinct AS IDs; each contains at most 25 words. |
| FR-04 | Context completion with ambiguity flags | P0 | No invented entities; unresolved references flagged. |
| FR-05 | Four-role classification | P0 | Only BACKGROUND/METHOD/FINDING/LIMITATION. |
| FR-06 | Source-anchor and metadata capture | P0 | Exact supporting span; paper/section/page or best available locator. |
| FR-07 | Support & consistency pre-check | P0 | Support verdict and explanation saved; cannot auto-verify. |
| FR-08 | Human verification workflow | P0 | Explicit human approval and evidence check. |
| FR-09 | Discard-not-edit / regeneration | P0 | Rejected candidate immutable; replacement has new ID and lineage. |
| FR-10 | Quality review and SPS fields | P0 | Five rubric-dimension reviews stored; optional 0–9 SPS supplied by reviewer only. |
| FR-11 | Verified library with search/filter | P0 | Query returns verified records by default. |
| FR-12 | Audit trail and extraction provenance | P0 | Reviewer, model/prompt version, source checksum and events retained. |
| FR-13 | Structured JSON / CSV export | P0 | All verified claims exported with source/evidence IDs. |
| FR-14 | Re-extraction and deduplication | P1 | New runs preserve historical decisions and identify near-duplicates. |
| FR-15 | Batch review and keyboard shortcuts | P1 | Reviewers can process large candidate queues. |
| FR-16 | Table/figure evidence alignment | P1 | Claims citing tables/figures link to correct region/cell. |

## 8. Business Rules and Validation

**BR-01: Source-only generation.** The generator must receive only authorized paper text. External search and unsourced text are excluded from claim generation.

**BR-02: Word limit.** All approvable AS units have `word_count <= 25` (software convention: whitespace-delimited English tokens, stripping terminal punctuation; exact tokenizer version stored). An over-length AS is flagged for re-atomization. This token convention is a product choice, not specified in the paper.

**BR-03: Semantic preservation.** No approval if the AS changes the original study population, time horizon, sample size, condition, comparison, metric, direction, negation, uncertainty, or quantification.

**BR-04: One main claim.** A single AS must not join independent statements that merit separate evidence checks. Related numerical values (e.g., numerator/denominator/percentage representing one result) remain together.

**BR-05: Evidence support.** Each accepted AS must have at least one original-source evidence span. A page citation alone is insufficient for trusted retrieval.

**BR-06: Manual decision.** The system cannot transition directly from generated/prechecked to `VERIFIED` without a recorded human action.

**BR-07: Reject, do not overwrite.** A contradicted, unsupported or ambiguous AS is `REJECTED`, not silently edited. Regeneration creates a new candidate linked through `parent_candidate_id`.

**BR-08: Source-reported vs primary.** A claim citing other researchers within the paper must not be labeled as a primary finding of the focal paper.

**BR-09: Immutable verification.** Any change to verified text or evidence must revoke/supersede the old approval and require a fresh verification event.

**BR-10: SPS provenance.** The paper says SPS has a nine-point rubric and five dimensions. Until the appendix's detailed scoring matrix is available, do not calculate an “official SPS” from an assumed weighting. MVP can store a human-entered `sps_total_0_9` with `rubric_version` and five independent notes/ratings; an internal heuristic must use a different label.

## 9. Information Model

### 9.1 Core entities

| Entity | Important fields | Relation |
|---|---|---|
| `Paper` | id, DOI, title, authors, year, source_hash, original_pdf_uri | 1:N Section/ExtractionRun |
| `PaperSection` | id, paper_id, heading, type, order, start/end offsets | 1:N Paragraph |
| `SourceParagraph` | id, section_id, content, page_start/page_end, offsets | 1:N EvidenceSpan |
| `EvidenceSpan` | id, paper_id, paragraph_id, exact_quote, start/end char, page, bbox?, checksum | N:M AtomicSentence via `ASSupport` |
| `ExtractionRun` | id, paper_id, model_id, prompt_version, parser_version, run_status, timestamps | 1:N AS candidates |
| `AtomicSentence` | id, paper_id, run_id, text, word_count, role, evidence_origin, status, parent_candidate_id? | N:M EvidenceSpan |
| `ASSupport` | atomic_sentence_id, evidence_span_id, support_kind, is_primary_support | AS-to-evidence mapping |
| `QualityAssessment` | id, AS id, five dimension reviews, optional SPS score, scoring rubric, assessor | N:1 AS |
| `VerificationEvent` | id, AS id, reviewer, action, reason, verified_against, timestamp | N:1 AS |

### 9.2 State machine

`DRAFT → PRECHECKED → PENDING_REVIEW → VERIFIED`

Alternative terminal/exception paths:
- `DRAFT / PRECHECKED → NEEDS_CONTEXT → PENDING_REVIEW`
- `DRAFT / PRECHECKED / PENDING_REVIEW → REJECTED`
- `VERIFIED → SUPERSEDED` (a new version is separately reviewed)
- `REJECTED → REGENERATED_AS_NEW_ID` (lineage reference only, not a reversal of the rejected item)

No transition allows AI alone to set `VERIFIED`. `REJECTED` cannot transition to `VERIFIED` in place.

### 9.3 Example AS JSON

```json
{
  "id": "AS-JMIR-0004",
  "paper_id": "P-10.2196-98343",
  "text": "Eleven of 18 workshop participants improved their research-topic formulation after the workshop (61%).",
  "word_count": 13,
  "role": "FINDING",
  "evidence_origin": "PRIMARY_FINDING",
  "section": "Results > Research-Topic Transformation",
  "evidence_spans": [
    {
      "span_id": "EV-RTT-02",
      "source_text": "After consensus, short-term improvement in the research topic (substantial transformation [category A] or refinement [category B]) was observed in 11 (61%) participants",
      "page": null,
      "source_locator": "HTML section/paragraph; original PDF alignment pending"
    }
  ],
  "source_support": "SUPPORTED",
  "status": "PENDING_REVIEW",
  "sps_total_0_9": null,
  "verified_by": null,
  "verified_at": null,
  "generation_provenance": {
    "model": "configurable",
    "prompt_version": "v1",
    "source_hash": "sha256:<computed-on-import>"
  }
}
```

*Example wording is a concise restatement of the article's Results; HTML evidence is not equivalent to completed human PDF verification.*

## 10. REST API Contract (Proposed)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/papers/{paperId}/atomic-extractions` | Start extraction; return run ID. |
| GET | `/api/atomic-extractions/{runId}` | Get run progress and counts. |
| GET | `/api/papers/{paperId}/atomic-sentences` | Filter/sort/page AS by status, role, section, origin. |
| GET | `/api/atomic-sentences/{asId}` | Detailed AS, anchors, quality and history. |
| POST | `/api/atomic-sentences/{asId}/precheck` | Execute automated precheck only. |
| POST | `/api/atomic-sentences/{asId}/verify` | Record authorized human approval. |
| POST | `/api/atomic-sentences/{asId}/reject` | Record rejection reason. |
| POST | `/api/atomic-sentences/{asId}/regenerate` | Create replacement candidate linked to rejected AS. |
| POST | `/api/atomic-sentences/{asId}/assess-quality` | Save reviewer assessment and optional SPS. |
| GET | `/api/atomic-sentences/search` | Trusted search; default verified-only. |
| GET | `/api/papers/{paperId}/atomic-sentences/export?format=json` | Structured export. |

### API response behavior
- `400 VALIDATION_ERROR`: invalid role, word count, missing required fields.
- `403 REVIEWER_REQUIRED`: non-reviewer attempts to verify.
- `409 STALE_SOURCE_HASH`: evidence source has changed since candidate generation.
- `409 IMMUTABLE_VERIFIED_AS`: client attempts to overwrite approved AS.
- `422 UNSUPPORTED_CLAIM`: blocking mismatch discovered at review gate.
- `422 MISSING_SOURCE_ANCHOR`: cannot verify without source.
- `202 ACCEPTED`: extraction enqueued; `run_id` returned.

All write actions must be idempotent where appropriate, including a request-id for reviewer actions. Access checks and paper-level permissions apply to every query.

## 11. UX Requirements

### Main screen: Atomic Sentence Explorer

Three synchronized areas on desktop (two panels on smaller screens):
1. **Paper navigation:** section tree, paragraph counts, AS statuses, filters for role and evidence origin.
2. **Atomic Sentence queue:** card/list of concise AS with ID, status, role, word count, support flag, and snippet.
3. **Evidence & verification:** original PDF viewer at precise page/highlight; extracted source excerpt; numeric/qualifier diff flags; quality review; VERIFY / REJECT / REGENERATE actions.

**Interactions:** selecting a card scrolls the PDF to evidence; clicking a highlighted span selects the AS; reviewer can open the entire source paragraph to judge context. `VERIFY` requires a confirmation of paper/source claim support; `REJECT` requires a reason. The UX must not make AI precheck look like human verification.

### Library screen
Search claim text and filter by paper, role, source section, evidence origin, reviewer and verification date. Default is `VERIFIED`; include a separate toggle to inspect drafts and rejected history. Exports include source locators and review provenance.

### Admin/analytics screen
Show extraction run durations, generated/prechecked/verified/rejected counts, reasons for rejection, reviewer workload, role distribution, exact source coverage, and model/prompt version.

## 12. Quality & Metrics (Product-defined, Not Published Results)

| Metric | Operational definition | Initial internal target |
|---|---|---|
| Source Traceability | Verified AS with resolvable original evidence / all verified AS | 100% hard gate |
| Human Verification Coverage | Verified AS with authorized human review event / all verified AS | 100% hard gate |
| Length Compliance | Verified AS with ≤25 words / all verified AS | 100% hard gate |
| Evidence Support Precision | Supported generated claims / candidates sampled and independently judged | ≥90% pilot target |
| Candidate Recall | Reference AS facts recovered / all reference facts on a human-annotated sample | ≥80% pilot target |
| Atomicity Pass Rate | Candidate AS with exactly one main proposition / evaluated candidates | ≥90% pilot target |
| Numeric Faithfulness | Reviewed numeric AS preserving numerator, denominator, units, scope and direction / all numeric AS reviewed | ≥99% pilot target |
| Reviewer Rejection Rate | Rejected candidates / all reviewed candidates | Observe, no arbitrary success target |
| SPS Distribution | Optional human-scored SPS (0–9) by five qualitative dimensions | Descriptive; no arbitrary cutoff |

**Pilot protocol:** select a stratified set of article sections including prose, results, tables and limitations. Two human annotators independently label candidate-relevant evidence and ideal atomizations, reconcile disagreements, then compare model output. Do not use the workshop's κ=0.77 as a benchmark. Targets above are internal design aspirations; they have not been established by the JMIR study.

## 13. Nonfunctional Requirements

- **Integrity:** deterministic source anchors/checksums, immutable review history, versioned AI prompts, no source-free claim promotion.
- **Security:** role-based verification, paper-level access control, encrypted data in transit/at rest per platform policy.
- **Observability:** structured per-run logging; all model calls record version, latency, warnings, token usage and relevant identifiers, without duplicating restricted full texts into telemetry.
- **Resilience:** paragraph-level retries; one malformed paragraph must not destroy all generated AS; failures explicitly logged.
- **Reproducibility:** record parser and source versions; extraction can be repeated without overwriting existing reviewer decisions.
- **Performance goal:** process a typical accessible-text 5,000-word article into preliminary candidates within 2 minutes on provisioned infrastructure; this is a proposed benchmark to measure during pilot, not a guarantee or published finding.
- **Accessibility:** text-selectable evidence and keyboard-navigable verification; clear semantic status labels beyond colors.

## 14. Test & Acceptance Scenarios

| Test | Input / trigger | Expected outcome |
|---|---|---|
| AT-01 | Compound results sentence reports two distinct findings | System proposes two separately supported AS, not one fused claim. |
| AT-02 | Result says `11 of 18 (61%)` | AS keeps numerator, denominator and percentage together. |
| AT-03 | Source says `associated with` | AS must not rewrite as `caused`. |
| AT-04 | Original says `did not assess citation accuracy` | AS preserves explicit negation. |
| AT-05 | Candidate contains `this study` without clear referent | Flag `NEEDS_CONTEXT`; do not fabricate subject. |
| AT-06 | AS has 26 or more words | Cannot become `VERIFIED`; prompt re-atomization. |
| AT-07 | AS has no resolvable evidence span | Block verification (`MISSING_SOURCE_ANCHOR`). |
| AT-08 | Model reports `SUPPORTED` and reviewer rejects | Candidate becomes `REJECTED`, never `VERIFIED`. |
| AT-09 | Reviewer requests regeneration after rejection | New AS ID created; prior rejection preserved, lineage linked. |
| AT-10 | Paper summarizes data from an external cited paper | Label `REPORTED_PRIOR_WORK`, not `PRIMARY_FINDING`. |
| AT-11 | Someone attempts to overwrite a verified AS | Operation rejected; versioned new candidate required. |
| AT-12 | Library search called without status filter | Only `VERIFIED` AS returned. |
| AT-13 | Paper was reuploaded and checksum changed | Previously generated pending candidates marked stale; verification blocked until reanchored. |
| AT-14 | Reviewer scores SPS without the exact rubric available | Store manual score and rubric version; never claim auto-calculated official SPS. |

### Release gates
- All P0 functional acceptance scenarios pass.
- No `VERIFIED` record without an anchored evidence span and human reviewer event.
- No approved AS over 25 words.
- Every verified item export includes `paper_id`, claim text, section/locator, evidence IDs, role, reviewer and verification time.
- Pilot human evaluation completed; accuracy/recall results reported with denominators and examples of failures.

## 15. Suggested Delivery Phases

**M0 — Provenance foundation:** source parser, section/paragraph/span identifiers, source viewer, immutable checksums.

**M1 — AI candidate engine:** detect candidate claims, atomize, context completion, classify role/origin, record run provenance.

**M2 — Verification workspace:** automated warning flags, side-by-side evidence, user decisions, discard/regenerate lineage, quality reviews.

**M3 — Verified library & evaluation:** search, filters, export, pilot reference annotations, metric dashboard, release-gate testing.

**Deferred P1:** table-cell/figure alignment, duplicate clustering, batch review, official SPS formula configuration after exact appendix review, deeper cross-paper aggregation.

## 16. AI Task Contracts (Suggested)

### Extractor system instruction (conceptual)

```text
You are an Atomic Sentence candidate extractor.
Use ONLY the provided original paper paragraph and supplied local context.
Produce zero or more short, independently readable scientific claims.
Each candidate must contain no more than 25 words and one main proposition.
Preserve the source's actors, numbers, denominators, units, polarity,
uncertainty, conditions, comparisons and temporal scope.
Attach the original evidence_span_id and one of four functional roles.
Never invent source claims, metadata, or citations.
If context is insufficient, flag uncertainty rather than fill gaps.
Return schema-valid JSON; no prose outside the JSON object.
```

### Verification assistant instruction (conceptual)

```text
Compare candidate AS only with its supplied evidence span and necessary context.
Return support status: SUPPORTED, PARTIAL, CONTRADICTED, UNDETERMINED.
Identify exactly which source details were preserved, added or omitted.
Pay particular attention to negation, hedging, quantities, denominators,
population, study design, comparative baseline and source-reported prior work.
This is a preliminary automated check and must not mark the AS VERIFIED.
```

## 17. Known Risks & Controls

| Risk | Mitigation |
|---|---|
| Hallucinated or overstated candidate | Evidence-first generation, source-only prompt, advisory precheck + mandatory human review. |
| Claim provenance lost | Exact source span and hash required; preserve original PDF alignment. |
| Quantitative distortion | Dedicated numerical consistency flags and human check. |
| Secondary study mislabeled as primary result | Explicit `evidence_origin` and manual confirmation. |
| Invalid split destroys meaning | `NEEDS_CONTEXT`, broader source view, reviewer rejection/regeneration. |
| False confidence from a 9-point SPS | Record uncertainty and rubric version; no invented official score derivation. |
| Incorrect inference of efficacy | Do not claim this module has proven citation hallucination reduction; measure independent validation. |
| Multiple extraction runs corrupt approved records | Immutable verified versions, run lineage, source hash checks. |

## 18. Explicit Open Decisions

1. Which PDF parsing component and evidence highlight technology is already available inside Paper Understanding?
2. Should verified AS require one reviewer or two independent reviewers for high-stakes papers?
3. Is the original PDF guaranteed to be retained for manual cross-reference verification?
4. Should `REPORTED_PRIOR_WORK` remain exportable with a stronger warning or require reading the cited primary paper later?
5. Should an exact official SPS rubric be loaded once Multimedia Appendix 1 is obtained, or will the MVP retain manual qualitative dimensions only?

## 19. Done Definition

The MVP is complete when an authorized user can open an imported paper, generate short AS candidates, see each claim aligned to original-source evidence, verify or reject claims without silent edits, inspect quality and provenance, then search and export only the verified library. This product must present source integrity as a reviewable process, not an unverified automation guarantee.

---

## Reference (single methodological source)

Liu S-W, Chu S-Y, Wang H-C, Lee M-S. **Teaching the Atomic Sentence Method for Source-Verified, AI-Assisted Literature Synthesis to Clinical Health Care Professionals: Single-Cohort Feasibility and Acceptability Study.** *JMIR Formative Research*. 2026;10:e98343. Published August 27, 2026. https://formative.jmir.org/2026/1/e98343/ — DOI: 10.2196/98343.

Relevant sections: *Methods → Stage 3: The AS Method (Core)*; *Discussion → Implications / Limitations*; the linked *Multimedia Appendix 1* (not inspected).
