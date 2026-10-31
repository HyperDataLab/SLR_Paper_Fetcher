# SLR Term and Taxonomy Quality Contract

## What an extracted term record must preserve

### Takeaway
Treat extraction as a versioned, source-grounded proposal attached to an immutable paper artifact and a specific text representation. Store enough evidence to replay the mention and its derivation; do not let an unreviewed proposal silently become a production filter.

### Cited Findings
- W3C PROV-O models provenance through Entities, Activities, and Agents, with relations for usage, generation, derivation, and responsibility. This maps naturally to PDF/text artifacts, extraction runs, and software/model/reviewer actors. — [W3C PROV-O](https://www.w3.org/TR/prov-o/)
- W3C Web Annotation supports text quote selectors (exact text plus optional prefix/suffix) and text position selectors (zero-based start, exclusive end). Positions must use Unicode code points and the same normalized text representation; position selectors are brittle if the source representation changes. — [W3C Web Annotation Data Model](https://www.w3.org/TR/annotation-model/)
- GROBID can return PDF page coordinates when requested; its page index starts at 1, coordinates use PDF units with a top-left origin, and page dimensions are needed to render/scale them correctly. Coordinates depend on the PDF CropBox/MediaBox. — [GROBID PDF coordinates documentation](https://github.com/grobidOrg/grobid/blob/master/doc/Coordinates-in-PDF.md)
- The project overview says the fetcher already pins PDF filename, SHA-256, byte size and versioned section/paragraph IDs, and validates analysis propositions against exact PDF text-layer spans/page-local offsets. — [SLR Paper Fetcher project overview](https://E:/obsidian/project/projects/slr-paper-fetcher/overview.md) (local context note; verify implementation before treating as current behavior).

### Inferences
- A term mention should include: `paper_id`/DOI; source PDF SHA-256 and byte size; text extraction artifact ID/hash and parser/version; run ID/time; extractor name/version/config; source section/paragraph ID; zero-based Unicode code-point `start`/exclusive `end` against a named immutable text artifact; exact surface quote plus prefix/suffix; optional one-based page and PDF bounding boxes; and validation state. Keep `surface_form` distinct from normalized label and concept identity.
- Fail closed on broken provenance: if PDF hash changes, text artifact cannot be resolved, offsets do not select the stored quote, or parser version/text mapping is absent, mark evidence stale/unresolved and exclude it from reviewed filter feeds until re-extracted or manually repaired.
- Prefer source-text offsets as the durable anchor and quote/context as a recovery aid. PDF page/box coordinates are useful for reviewer navigation but are not a substitute for text anchors; keep coordinate frame/page dimensions and PDF hash alongside them.

### Gaps
- PROV-O and Web Annotation specify general models, not a SLR-specific JSON schema, extraction accuracy threshold, or policy for whether exact evidence must be public. Those are product decisions.
- The project overview is context, not code verification; inspect current extractor/mapping implementation before claiming the described behavior is intact.

## Term identity, language, and controlled vocabulary

### Takeaway
Separate a paper’s literal mention from a normalized label and from a concept. Normalize only mechanically and reversibly where possible; synonymy, translation equivalence, and taxonomy placement require explicit evidence or review.

### Cited Findings
- SKOS distinguishes preferred, alternative, and hidden labels; labels can carry language tags, and a concept has at most one preferred label per language tag. It distinguishes `exactMatch` (high-confidence interchangeability across broad retrieval contexts) from `closeMatch` (interchangeable only in some information-retrieval applications); `closeMatch` is intentionally non-transitive to prevent compound errors. — [W3C SKOS Reference: labeling](https://www.w3.org/TR/skos-reference/); [mapping properties](https://www.w3.org/TR/skos-reference/#mapping)
- SKOS uses `broader`/`narrower` for immediate hierarchical links; transitive closure is represented separately. SKOS itself does not impose integrity conditions preventing all mapping cycles, so applications must decide additional constraints. — [W3C SKOS Reference: broader/narrower](https://www.w3.org/TR/skos-reference/#semantic-relations); [cycles and mapping relations](https://www.w3.org/TR/skos-reference/#mapping)
- BCP 47 language tags identify languages (and optionally script/region variants); RFC 5646 defines canonicalization and case-insensitive comparison. SKOS lexical labels use Unicode strings and language tags. — [RFC 5646](https://www.rfc-editor.org/rfc/rfc5646); [W3C SKOS Reference](https://www.w3.org/TR/skos-reference/)
- ISO 25964-1 is for thesauri used in information retrieval, covers multilingual thesauri, and supplies a model and interchange format; ISO’s current page says a second edition is under publication and will replace the 2011 edition. — [ISO 25964-1](https://www.iso.org/standard/86713.html)
- A 2026 ACL Anthology evaluation across four domains and three languages reports LLM term-extraction F1 spanning .36–.72 and identifies boundary/normalization disagreements in its error analysis. This is evidence that task/domain/language and annotation policy matter, not a transferable estimate for SAFFRON or this corpus. — [Large Language Models Are Good Term Extractors: A Systematic Evaluation](https://aclanthology.org/2026.lrec-1.605/)

### Inferences
- Model three separate entities: (1) `mention` (verbatim source span), (2) `term/concept` (stable ID with preferred/alternate labels per BCP 47 language), and (3) relation/mapping assertion with typed semantics and provenance. Do not collapse inflections, spelling variants, abbreviations, translations, or near-neighbors into one identity merely because embeddings are close.
- Preserve raw label and language as extracted; add normalized forms with a named method/version (Unicode NFC, whitespace/case normalization, optional language-specific lemma) and retain reversibility. Do not strip diacritics, translate, stem, or expand abbreviations as identity operations without explicit policy/evidence.
- Represent mapping strength explicitly (`exact`, `close`, `broader`, `narrower`, `related`, `translation-equivalent`, or unresolved candidate) and store source/target scheme IDs and evidence. Use an established external vocabulary only when concept scope and licensing/identifier stability fit; otherwise mint local stable IDs and record mappings rather than overwriting identities.
- For API filters, expose reviewed concepts as the selectable vocabulary; provide a separate, clearly marked candidate suggestion channel. Define whether selecting a parent includes descendants as an explicit query option, since direct `broader` links and transitive expansion are not the same assertion.

### Gaps
- The ISO public abstract does not expose the full normative rules or interchange model. Do not claim detailed ISO conformance without access to the licensed standard.
- No universal normalization policy works across all SLR domains/languages. Determine supported languages from source data and evaluate each separately.

## Review states, confidence, taxonomy validation, and feedback

### Takeaway
Use confidence to prioritize review, not to certify truth. Promote filters only through an auditable human review workflow, and validate taxonomy edges as typed, evidence-backed hypotheses before release.

### Cited Findings
- Guo et al. define calibration as probability estimates corresponding to empirical correctness likelihood and find modern neural networks can be poorly calibrated; their temperature-scaling results are empirical for tested classification datasets, not a guarantee for term extraction or LLMs. — [On Calibration of Modern Neural Networks, ICML/PMLR](https://proceedings.mlr.press/v70/guo17a.html)
- The cited ACL 2026 term-extraction evaluation reports substantial variation across model size, domains, languages, and term-boundary judgments; its benchmark results do not establish calibrated confidence for another extractor or use case. — [ACL Anthology paper](https://aclanthology.org/2026.lrec-1.605/)
- SKOS semantics distinguish hierarchical relations from associative and cross-scheme mapping relations; `closeMatch` is not transitive, and SKOS permits some mapping cycles. — [W3C SKOS Reference](https://www.w3.org/TR/skos-reference/)
- PRISMA-S asks reviewers to report complete search strategies exactly as run and details of sources/searches to support transparent, reproducible review methods. It concerns literature search reporting, not term extraction, but supports preserving filter/query versions and execution history. — [PRISMA-S](https://pmc.ncbi.nlm.nih.gov/articles/PMC8270366/)

### Inferences
- Model lifecycle explicitly: `candidate → accepted` or `rejected`; allow `needs_review`, `superseded`, and `stale_evidence`. Store reviewer, timestamp, decision reason, previous version, and changes. Only `accepted` concepts/relations enter default SLR API filter lists; keep candidates searchable in a review queue, never silently auto-promote.
- If numeric scores are exposed internally, label them `raw_score` or `estimated_probability`, record calibration dataset/version and evaluation date, and report per-language/domain precision/recall and calibration error with sample counts. Calibrate against independently double-reviewed examples; route low-evidence, disagreement, new-language, and out-of-distribution cases to review. Do not treat even a calibrated probability as proof for an individual term.
- Require each taxonomy edge to have a relation type, source/target concept IDs, supporting mention(s)/paper(s), assertion provenance, status, reviewer, and scope. Validate endpoints exist, no self-edge, duplicates are canonicalized, relation direction is consistent, and—if the chosen local taxonomy is a tree/DAG—reject cycles and flag multiple parents for review. These are application-level constraints; do not imply SKOS universally requires a tree or forbids cycles.
- Keep an adjudication log and versioned vocabulary snapshots. Record for every filter run the accepted concept IDs, included descendants/expansion policy, vocabulary version, query parameters, and result set provenance so inclusion/exclusion decisions can be reproduced and revised.
- Track quality at two levels: mention evidence (span resolves against pinned text/PDF; extraction errors and stale rates) and concept/taxonomy (review acceptance, duplicate/merge rate, edge reversal/cycle rate, inter-reviewer agreement, filter precision on sampled results). Split evaluation by domain and language; use reviewer labels as the gold set, not model outputs.

### Gaps
- There is no sourced universal confidence cutoff, minimum reviewer agreement, or acceptable error rate for SLR filters. Set thresholds from the cost of false inclusion/exclusion and measured validation data.
- PRISMA-S supports reproducibility but does not define a term/taxonomy workflow. The proposed review states, graph constraints, and metrics are recommendations tailored to this integration, not requirements from that guideline.
