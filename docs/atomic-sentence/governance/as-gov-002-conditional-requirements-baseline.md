# AS-GOV-002 — Conditional Requirements Baseline

**Version:** Candidate 0.1
**Work status:** READY FOR REVIEW
**Approval status:** PROPOSED — PENDING APPROVAL
**Decision status:** AS-OD-01 through AS-OD-17 remain OPEN
**Purpose:** Consolidate PRD requirements and unapproved proposals into a traceable input for the future normative AS-GOV-002 contract.

## Authority and status meanings

The supplied PRD v1.0 is the source for requirements explicitly stated in that document. Its header calls it a “Proposed MVP specification”; therefore, CONFIRMED BY PRD means “the requirement is explicitly present in the PRD,” not that an authorized Product Owner has approved it. The Product Owner must confirm it as the controlling input before this can become a normative baseline.

QA-01 specifications, QA-02 recommendations, QA-03 backlog/roadmap, QA-04 approval register, QA-05 verification, AS-TECH-01, and AS-GOV-001 provide draft interpretations, review assignments, technical observations, and canonical ticket mapping. They do not override the PRD or turn a proposed option into an approval.

Status labels describe source evidence or the current gate:

- **CONFIRMED BY PRD:** The source explicitly states the requirement. This is not approval.
- **PROPOSED — PENDING APPROVAL:** A QA/technical interpretation or recommendation that needs an authorized decision.
- **BLOCKED — PRODUCT DECISION:** Product Owner outcome is required before the dependent contract or behavior is final.
- **BLOCKED — RESEARCH REVIEW:** Research Lead review/approval requested by QA-04/05 is incomplete.
- **BLOCKED — TECHNICAL DEPENDENCY:** An implementation/interface/infrastructure dependency remains unresolved.
- **READY FOR REVIEW:** Nonbinding requirements or technical material is reviewable; coding is not thereby unblocked.

## Scope of this candidate

The candidate preserves the PRD P0 functional requirements FR-01 through FR-13 and applicable business rules/process gates. It keeps Atomic Sentence inside the existing SLR Paper Fetcher and Paper Analysis experience. It does not add another paper catalog, duplicate PDFs, change Toulmin/AIF semantics, silently drop a PRD requirement, or promote an optional/P1 feature into MVP.

The PRD P1 requirements FR-14 through FR-16 remain outside MVP unless separately approved. The PRD also describes an Admin/analytics screen without assigning it a P0/P1 priority or acceptance ticket. This candidate records that screen as PRD-stated UX with unresolved scope/priority; it does not silently label it P0 or delete it.

## Conditional product requirements

### Source, provenance, and paper eligibility

- Inputs include an existing paper ID, parsed paragraphs or uploaded full text/PDF, and stable source identity.
- PRD-supported MVP inputs include selectable-text PDFs and already-parsed structured paper JSON. PDF-level cross-reference requires the original PDF to be available. HTML/paragraph anchors may be usable where applicable, but do not substitute for original-PDF review when the workflow claims PDF verification.
- Preserve paper/section/paragraph/sentence order, exact source text and offsets, stable span identifiers, source checksum, page/section locators where available, citation markers, and extraction warnings. Never guess missing metadata or source positions.
- Flag unreliable OCR, unreadable scans, missing provenance, layout-damaged tables, partial extraction, mapping/hash mismatch, unsupported language, or unavailable original PDF. Unresolved source cannot silently become reviewable or VERIFIED.
- Reuse the existing paper identity, saved source and validated GROBID mapping where available. The structured-JSON input path must also be represented in the source adapter contract; the GROBID-centered design in AS-TECH-01 does not authorize narrowing the PRD input formats.
- An existing source offset is not itself a PDF coordinate. The technical contract must distinguish exact full-text offsets from a PDF.js text-layer highlight and state when the latter cannot be located unambiguously.

### Candidate extraction, atomization, and context

- Candidate detection scans paragraph text with the current section heading and immediate neighboring context. A paragraph may yield zero, one, or multiple research-relevant candidates; no quota is required.
- Candidate extraction distinguishes claims from questions, navigation text, reference-only lines, boilerplate, and headings.
- A candidate may yield zero or more proposed Atomic Sentences. Each AS is independently readable and recomposable, expresses one main proposition that merits one evidence check, and is at most 25 words under the eventually approved count convention.
- Preserve source wording separately from generated statement text. Keep candidate IDs, AS IDs, run lineage, prompt/model/parser information, and parent links.
- Context completion may resolve an actor, referent, condition, or scope only where supplied paper context supports it. Ambiguity remains flagged as NEEDS_CONTEXT; the model must not invent entities or rely on general knowledge.
- Preserve the source population, time horizon, intervention/exposure, sample size, metric, units, numerator/denominator, comparison, direction, negation, uncertainty, modality, causal limitation, and quantification. Preserve related numeric components that jointly express one finding.

### Roles, evidence origins, and language

- The PRD enumerates four functional roles: BACKGROUND, METHOD, FINDING, LIMITATION.
- It separately enumerates evidence origins: PRIMARY_FINDING, REPORTED_PRIOR_WORK, AUTHOR_INTERPRETATION, METHOD_DESCRIPTION.
- Role and evidence origin remain separate fields. Existing proposition types and Toulmin/AIF roles are not substitutes.
- A focal paper’s report of another study is evidence that the focal paper reports that claim; it is not evidence that the cited primary study supports it. A primary-finding view must not misrepresent reported prior work.
- PRD BR-02 gives a whitespace-delimited English token rule, stripping terminal punctuation, and requires a stored tokenizer version. Launch language and implementation behavior remain subject to AS-OD-11. The QA-02 English-only pilot proposal is not approved.

### Precheck, human review, lifecycle, and library

- Precheck validates schema, word count, evidence span, source checksum and role, then assesses source-only support as SUPPORTED, PARTIAL, CONTRADICTED or UNDETERMINED with an explanation. Numeric/unit, qualifier, negation, comparison, scope, actor and missing-evidence discrepancies are surfaced.
- AI results remain advisory. No AI, run, precheck or background process may create a human review event or set VERIFIED.
- Authorized human review checks the exact claim against the source and original PDF. VERIFY requires anchored evidence and a human event; REJECT requires a reason; regeneration creates a new ID and preserves rejection. Material change to verified text/evidence requires fresh review.
- Pending, rejected, stale and superseded records remain auditable and out of default trusted retrieval. The PRD specifies verified-only default search. Source-change and re-anchoring behavior remains subject to AS-OD-14.
- Reviewer identity and paper/project access must be authenticated and authorized on the server. A display name, the current local-user fallback, or an API key used only as a workspace gate is not proof of individual reviewer identity.
- Operational reviewer quorum is subject to AS-OD-01. Gold-set double annotation/adjudication remains separate from operational publication quorum.

### Quality review and SPS

PRD FR-10 requires five dimension reviews and permits an optional reviewer-supplied 0–9 SPS score. The detailed Appendix 1 rubric is unavailable in supplied project materials. Do not invent dimension names, score allocations, weights, or an official automatic score. QA-02/04’s generic manual, rubric-versioned fallback is a proposal only. AS-OD-09 remains OPEN pending the requested Product Owner and Research Lead review/approval. Final data fields, reviewer controls, scoring, exports, and comparisons remain blocked until resolved.

### Verified library, search, and export

- The PRD P0 library returns VERIFIED items by default and supports search/filtering for claim text, paper, author/year, section, role, evidence origin, reviewer, and verification date. Draft/rejected history may be separately inspectable by authorized reviewers.
- PRD §11 describes a Library screen; the per-paper tab alone does not provide cross-paper retrieval. A library entry must be mapped into the same existing workspace through AS-UI-001 / AS-LIB-001, not a standalone app.
- Default treatment of REPORTED_PRIOR_WORK remains an AS-OD-13 decision. If included, preserve the origin marker/citation and do not present it as a focal-paper primary result.
- PRD FR-13 explicitly requires both JSON and CSV export of verified claims with source/evidence IDs. The PRD’s proposed endpoint example shows a JSON format parameter only; the approved API contract must cover both formats, their field schema, encoding/escaping, access, and provenance. AS-LIB-002 owns the canonical export ticket.
- Export records preserve paper identity, claim text, role/origin, source quote/span/locator, source version, evidence IDs, reviewer identity/time and candidate lineage where available. AI precheck is never exported as human verification.

### UX, metrics, security, and operations

- The PRD main Explorer describes three synchronized desktop areas: paper navigation, Atomic Sentence queue, and evidence/verification with original PDF, quote, numeric/qualifier flags, quality review and VERIFY/REJECT/REGENERATE actions. The PRD asks for two panels on smaller screens.
- The PRD separately describes an Admin/analytics screen covering run durations, generated/prechecked/verified/rejected counts, rejection reasons, reviewer workload, role distribution, source coverage and model/prompt version. Its release priority and backlog acceptance mapping are unresolved. Preserve it in traceability and obtain Product Owner scope direction.
- PRD hard process gates are 100% source traceability, 100% authorized human verification coverage, and 100% length compliance for verified items. Initial support-precision/recall/atomicity/numeric-faithfulness figures are pilot targets, not validated results. The 5,000-word/two-minute figure is a benchmark goal, not a guarantee. AS-OD-16/17 govern metric/release use.
- Preserve security/access control by role and paper/project, encryption per platform policy, restricted-content telemetry safeguards, structured run observability, paragraph-level resilience, reproducibility, and accessible keyboard navigation.
- Source retention, external/cloud-provider handling, and the exact authentication provider are not settled by the 17-decision set or the existing technical design. Obtain Security/Platform guidance before operational use.

## Conditional treatment of all 17 product decisions

Every item remains OPEN. The candidate option is carried forward for review only; the authorized outcome must be recorded in the QA-04 register.

| Decision | Candidate disposition for review | Approval route / affected contract |
|---|---|---|
| AS-OD-01 | One trusted operational reviewer per item, with any second-review exception set defined in advance; gold-set review remains separate. | Product Owner; Research Lead consultation. Review quorum, audit and library. |
| AS-OD-02 | Follow reject-with-reason and regenerate as a new ID; no separate request-revision state initially. | Product Owner. Lifecycle, lineage and API/UI. |
| AS-OD-03 | Use only four PRD roles, map by function, keep origin separate, and flag ambiguous cases. | Product Owner; Research Lead mapping review requested, co-approval authority unresolved. |
| AS-OD-04 | Preserve uncertainty/modality/negation/scope semantically; defer separate classifier, cue and cue-scope outputs from MVP. | Product Owner. QA-01 differs; see divergence section. |
| AS-OD-05 | Defer separate sentence-uncertainty labels; distinguish uncertain meaning from unresolved annotation if later included. | Product Owner; Research Lead if the label enters scope. |
| AS-OD-06 | Defer Hyland stance/engagement labels from MVP. | Product Owner; Research consultation if reconsidered. |
| AS-OD-07 | Defer metadiscourse annotation from MVP. | Product Owner. |
| AS-OD-08 | Defer lens/method with metadiscourse; if later in scope, decide interactive/reflexive separately from thin/thick. | Product Owner; Research advice for future work. |
| AS-OD-09 | Obtain Appendix 1 or approve a rubric-versioned manual fallback; no invented dimensions, weights or official automated score. | Product Owner + Research Lead review/approval requested. SPS, data, UI and export. |
| AS-OD-10 | Allow multiple exact spans and distinguish primary support from context spans. | Product Owner; technical feasibility review. Data, source index, AI and UI. |
| AS-OD-11 | Consider an English-only pilot using the PRD count/tokenizer convention; flag other languages unsupported until specified/evaluated. | Product Owner; technical feasibility and Research Lead corpus-language consultation. |
| AS-OD-12 | Require a trusted server-side reviewer principal and authorization. | Product Owner; technical/security feasibility. Verification, audit, access and export. |
| AS-OD-13 | Consider labeled/filterable inclusion of focal-paper reports of prior work; exclude them from primary-finding views. | Product Owner; Research consultation on interpretation. Library and export. |
| AS-OD-14 | Bind to PDF/mapping/text/segmenter identity; mark affected items stale on change, preserve history, require a new version and review for re-anchoring. | Product Owner; technical feasibility. Data, verification and library. |
| AS-OD-15 | Stratified launch-domain gold set, two annotators plus adjudication, paper-level split, sample size reviewed with Research Lead. | Product Owner + Research Lead review/approval requested. Gold set and evaluation. |
| AS-OD-16 | Preserve PRD process gates; define denominators, then set model thresholds after pilot rather than inventing them. | Product Owner release decision + Research Lead metrics/protocol review requested. |
| AS-OD-17 | Measure PRD model targets/runtime provisionally; do not use them as release gates until approved. | Product Owner; Technical Lead benchmark review and Research Lead metric review. |

## Documentation inconsistencies and controlled resolution

### Hedge-scope divergence

QA-01 AS-OD-04 allows a broader three-part hedge capability if the requested QA-01 capability is approved. QA-02/04 recommend semantic preservation only and deferral of sentence-level uncertainty classification, cue detection and cue-linked scope. The PRD requires semantic preservation but does not list these three annotation products as P0 functional fields. Carry the QA-02/04 recommendation as PROPOSED — PENDING APPROVAL, retain the PRD meaning-preservation rule unchanged, and require an explicit Product Owner outcome for OD-04 and related OD-05–08. If separate annotations are approved, treat them as scope expansion with separate gold data, metrics and the deferred canonical tickets AS-AI-005 / AS-QA-007; do not silently edit the PRD.

### Other resolution rules

- Treat QA-01 “Proposed” recommendation labels separately from QA-04/05 approval status OPEN.
- Treat PRD UX as explicit content, but do not infer P0 priority for Admin/analytics where the PRD does not label it.
- Preserve the PRD-supported structured paper JSON input alongside JSON/CSV output; these are different requirements.
- Keep the exact PDF highlight limitation visible. A text quote/page match is not proof of glyph-level alignment; missing/ambiguous anchors block verification under the applicable evidence policy.
- Preserve canonical ticket IDs and QA-03 historical crosswalk. Resolve dependency wording rather than renaming or recreating tickets.

## Readiness boundary

The baseline and ticket matrix are READY FOR REVIEW. Non-mutating repository/source inspection, fixture design, identity/provider feasibility, PDF-anchor coverage analysis, API/component alternatives, and additive data alternatives can proceed as READY FOR REVIEW.

AS-GOV-002 remains BLOCKED — PRODUCT DECISION until the Product Owner records all 17 outcomes and the required consistency checks pass. AS-OD-09/15/16 additionally remain BLOCKED — RESEARCH REVIEW pending the requested Research Lead review/approval; OD-03 review is requested. Persistence, source index, API, AI, verification, library, export and release implementation remain blocked by their listed Product/Research/Technical dependencies. The ticket matrix maps individual requirements and the dependency-resolution note proposes a non-circular sequence.

This document does not assert that Atomic Sentence is approved or implemented. No code, database, migration, or PRD change is authorized by this conditional baseline.
