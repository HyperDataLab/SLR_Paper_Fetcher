# AS-GOV-001 — Proposed Approval Baseline

**Version:** Candidate 0.1 for authorized review
**Status:** PROPOSED; not an approved requirements baseline
**Approval state:** AS-OD-01–17 remain OPEN; zero approvals recorded
**Purpose:** Give AS-GOV-002 a traceable candidate baseline without selecting options on behalf of Product Owner or Research Lead.

## How to use this recommendation

This document assembles PRD requirements and QA-02/QA-04 recommendations into a reviewable option set. It is not an approval record. The Product Owner must explicitly decide all 17 AS-OD entries; the Research Lead must provide the requested co-approval/review for the specified research/evaluation decisions. If an option is changed, rejected, or deferred, record that outcome and update the downstream contract. Do not infer acceptance from this document, developer preference, or a completed technical design.

The PRD v1.0 is currently the project requirements source and explicitly labels itself a **Proposed MVP specification**. The Product Owner should confirm that it is the controlling input for the versioned baseline and approve any selected interpretation. The candidate below retains its P0 requirements; it makes no silent scope reduction.

## Candidate core baseline — preserve PRD P0 requirements

Subject to Product Owner approval, carry forward all PRD FR-01 through FR-13 and their process invariants:

1. Reuse an existing paper record and original source; preserve source identity, checksum, sections, paragraphs and exact text offsets. Do not duplicate the paper catalog or PDF.
2. Accept the PRD's stated supported source paths: selectable-text PDF and already-parsed structured paper JSON when source identity and original-PDF verification are preserved. Flag unsupported, partial, unaligned, unreliable, or stale source; never silently promote it.
3. Allow zero-to-many research-relevant candidates per paragraph and one-to-many Atomic statements per candidate where supported.
4. Keep source wording, AI-proposed wording, primary support evidence and context evidence distinct; link each statement to exact evidence and provenance.
5. Preserve one main independently verifiable proposition, source meaning, actors, quantities, denominators, units, comparisons, direction, negation, conditions, uncertainty and modality. Do not add claims from general knowledge.
6. Use only the four PRD functional roles and four evidence origins, with role separate from origin; the mapping guide remains subject to AS-OD-03/13 approval.
7. Apply the PRD ≤25-word constraint using the approved language/tokenizer convention; AI support findings remain advisory.
8. Require authorized human verification. AI cannot set VERIFIED. Rejection is preserved; regeneration creates a new linked identity; material change requires a fresh review.
9. Preserve PRD FR-10 quality-review fields without invented SPS dimensions, weights, or official calculations. The fallback must be approved under AS-OD-09.
10. Provide the PRD verified library/search and JSON/CSV export with paper/source/evidence, role/origin and review provenance. Default and reported-prior behavior remain subject to OD-13 and the approved library contract.
11. Preserve the separate PRD process gates: 100% source traceability, 100% authorized human verification coverage and 100% length compliance for verified items. Do not turn its pilot model targets or runtime goal into release gates unless approved under OD-16/17.
12. Keep all existing SLR Paper Fetcher analysis, Toulmin/AIF, catalog, downloader, PDF, review, export and optional integration semantics unchanged.

This candidate retains the QA-02 MVP proposal's boundary: uncertainty/modality preservation is required; separate uncertainty classification, full hedge cue/scope extraction, Hyland stance/engagement, and metadiscourse remain outside the proposed MVP unless formally approved. Multilingual processing, OCR, table/figure-region alignment, batch review and external SLR synchronization remain optional/deferred as documented in the PRD/QA-02 proposal, subject to confirming source eligibility and scope.

## Candidate outcomes for the 17 open decisions

These are **options recommended for approval review**, not chosen outcomes. Approval routing is summarized in [the blocker matrix](as-gov-001-blocker-matrix.md).

| Decision | Candidate baseline option to review | Approval state and condition |
|---|---|---|
| AS-OD-01 | One trusted operational verifier per AS, with any second-review exception subset defined in advance. Gold-set annotation remains two independent annotators plus adjudication. | OPEN; Product Owner decision; Research Lead consultation for separation from research protocol. |
| AS-OD-02 | Reject with reason and regenerate under a new linked candidate/AS ID; no separate request-revision state in the first release. | OPEN; Product Owner decision; technical consequences can be reviewed. |
| AS-OD-03 | Four PRD roles only, mapped by communicative function; keep origin orthogonal; ambiguous labels go to review. | OPEN; Product Owner decision; Research Lead mapping-guide review requested, co-approval authority unresolved. |
| AS-OD-04 | Preserve uncertainty, modality, negation and scope in all atoms; defer separate sentence uncertainty classification, cue detection and scope spans. | OPEN; Product Owner scope decision. This is the QA-02/04 candidate response to QA-01's broader conditional wording. |
| AS-OD-05 | Defer a separate sentence uncertainty label; if later scoped in, define uncertainty vs annotation-unresolved distinctly. | OPEN; Product Owner decision; Research Lead if research label is added. |
| AS-OD-06 | Defer Hyland stance/engagement; if later approved, pilot contextual multi-label annotations with evidence and overlap evaluation. | OPEN; Product Owner decision; Research consultation for future taxonomy. |
| AS-OD-07 | Defer metadiscourse from MVP. | OPEN; Product Owner decision. |
| AS-OD-08 | Defer metadiscourse lens/method; if later included, decide interactive/reflexive separately from thin/thick. | OPEN; Product Owner decision; Research Lead advice for future work, final authority unresolved. |
| AS-OD-09 | Obtain Appendix 1 if possible. Otherwise consider a manual, rubric-versioned fallback using five generic slots/notes and optional human-entered 0–9 total; no invented dimensions/weights or auto-score. | OPEN; Product Owner and Research Lead review/approval requested. Confirm joint sign-off. |
| AS-OD-10 | Permit multiple exact source spans, distinguishing primary claim support from supporting context; require at least one exact source span. | OPEN; Product Owner decision; Technical Lead can confirm feasibility. |
| AS-OD-11 | English-only pilot source/output; version the PRD English whitespace word-count convention; flag other languages unsupported pending segmentation/tokenizer/evaluation. | OPEN; Product Owner decision; Technical Lead feasibility and Research Lead corpus-language consultation. |
| AS-OD-12 | Require a server-trusted reviewer ID and server-side authorization; do not authorize from editable client names or the current local-user fallback. | OPEN; Product Owner decision; Technical/Security identity feasibility required. |
| AS-OD-13 | Include reported prior work only as a verified report from the focal paper, with a prominent origin/citation marker; provide filters and exclude it from primary-findings views. | OPEN; Product Owner decision; Research consultation on downstream interpretation. |
| AS-OD-14 | Bind to PDF/mapping/text/segmenter identity; mark dependent items stale on change; preserve history; re-anchor only through a new version/candidate and fresh human review. | OPEN; Product Owner decision; Technical Lead source-version feasibility. |
| AS-OD-15 | Stratified launch-domain gold set, two independent annotators plus adjudication, paper-level development/test split, sample size confirmed with Research Lead. | OPEN; Product Owner and Research Lead review/approval requested. |
| AS-OD-16 | Retain the PRD 100% process gates; establish task metrics/denominators before evaluation; set numeric model thresholds after pilot; no advanced-label thresholds for deferred families. | OPEN; Product Owner release decision and Research Lead metric/protocol review requested. Formal co-signature to confirm. |
| AS-OD-17 | Measure initial PRD targets and the 5,000-word/two-minute goal provisionally during pilot; do not make them gates until measurement definition and applicability are approved. | OPEN; Product Owner decision; Technical Lead benchmark review and Research Lead metric review. |

## Candidate technical baseline

These technical choices preserve current application boundaries and may be used as review assumptions. They do not approve product behavior or a database schema.

- Keep Atomic inside the existing Analysis workspace. Add the per-paper tab at /analysis/paper/{paper_id}?from=/analysis and provide an in-workspace path to the cross-paper verified library required by FR-11.
- Reuse the existing paper key/catalog, saved source files, validated GROBID mapping, PDF.js viewer/highlight functions, and configured provider transport behind Atomic-specific adapters.
- Keep Atomic storage, run lifecycle, provider prompts/schemas, reviewer events, and API contracts separate from Toulmin/AIF and current mutable analysis records.
- Treat source text, generated statement, exact evidence, context, advisory precheck and human review event as distinct typed data.
- Preserve the current mapping SHA-256/offset validation; add an Atomic snapshot for mapping/text/segmenter/tokenizer identity only after approved contracts.
- Use deterministic validation plus versioned advisory model output. No AI or precheck path can append a human verification event or set VERIFIED.
- On unresolvable PDF anchor, incomplete mapping, unsupported input/language, stale source or absent authorized reviewer, return an explicit non-reviewable state. Do not guess.
- Propose a dedicated Atomic router/service/repository/source adapter and frontend module; finalize internal module boundaries after requirements/API contracts are approved.

No SQL table names or migration shape are approved by this candidate. AS-DATA-001 remains the gate for choosing the additive logical/physical persistence model.

## Remaining baseline clauses for explicit resolution

Before AS-GOV-002 is approved, the Product Owner/Research Lead and relevant technical/security owners should resolve or assign:

1. Whether PRD v1.0 is the controlling approved source and how §11 Admin/analytics UX is scoped and mapped to a canonical ticket.
2. A global library entry in the existing Analysis UI in addition to the per-paper detail tab.
3. Structured paper JSON eligibility/source adapter acceptance, preserving original PDF verification.
4. Original-PDF retention guarantees and what happens if the artifact is removed or replaced.
5. Trusted reviewer identity, paper/project access, and provider data-handling rules, especially if a configured cloud provider receives source text.
6. A tested PDF evidence-anchor contract and required behavior when a quote/page cannot map unambiguously.
7. SPS appendix/fallback and its exact review/export fields.
8. Gold-set sampling, annotator/adjudication process, evaluation metric definitions, denominators, target status, and pilot benchmark conditions.
9. Non-circular dependency meaning/order for AS-DATA-002, AS-SRC-001, and AS-API-002; confirm whether AS-API-001 is the first code ticket after the approved API/state contract.
10. Backlog Owner acceptance of the AS-AREA-### crosswalk before external tracker or branch use; canonical IDs remain unchanged in this proposal.

## AS-GOV-002 readiness

This recommendation can serve as a structured input to a **draft** AS-GOV-002 requirements contract. The normative approved baseline must remain blocked until every required human decision is recorded and the consistency checks pass. Record selected option, decision status, approver identity, timestamp with timezone, conditions/rationale, and any required co-approval in the QA-04 register. Keep AS-OD status OPEN until the authorized evidence exists.
