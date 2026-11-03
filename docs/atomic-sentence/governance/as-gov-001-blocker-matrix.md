# AS-GOV-001 — Decision and Blocker Matrix

**Approval state:** AS-OD-01–17 are OPEN. This matrix does not approve, reject, defer, or select any option.
**Recommendation basis:** QA-02 product-decision proposal and QA-04 decision register, reconciled against the PRD and QA-05.
**Authority:** Product Owner outcomes are requested for all 17; specified Research Lead review is recorded separately below.

## Decision-by-decision review

| ID | Decision and candidate option for approval review | Product Owner | Research Lead | Principal blocker / downstream effect | Status |
|---|---|---|---|---|---|
| AS-OD-01 | One trusted operational verifier per item; a second reviewer only for an explicitly defined disputed/high-risk subset. Keep two independent annotators plus adjudication for the gold set. | Approval requested | Consultation on separating product quorum from gold-set protocol | Blocks verify transition, quorum, audit and library eligibility; must be consistent with OD-12 and OD-15. | OPEN |
| AS-OD-02 | Follow PRD reject-with-reason and regenerate as a new candidate ID; do not add a separate REQUEST_REVISION state initially. | Approval requested | No required review recorded | Blocks lifecycle/API/UI/history and invalidation of prior prechecks. | OPEN |
| AS-OD-03 | Keep only the four PRD roles; map by function, keep origin separate, and flag ambiguous cases for review. | Approval requested | Mapping-guide review requested; whether formal co-approval is required is unresolved | Blocks reliable labeling, annotation instructions, filters and evaluation. QA-01 wording also needs reconciliation with QA-02's narrower MVP. | OPEN |
| AS-OD-04 | Preserve uncertainty, modality, negation and scope semantically in every atom; defer the distinct sentence classifier, hedge cue spans and cue-linked scope spans from MVP. | Approval requested | Consultation if separate research outputs are reconsidered | Scope blocker. QA-01 offers a broader conditional path; QA-02/04 recommend the candidate above. Must be decided with OD-05. | OPEN |
| AS-OD-05 | Defer a separate sentence-uncertainty label from MVP. If later included, distinguish uncertainty of meaning from unresolved annotation. | Approval requested | Approval/review only if this research label is brought into scope | Blocks its own schema/evaluation only; once explicitly deferred, not a source-index/MVP blocker. | OPEN |
| AS-OD-06 | Defer Hyland stance/engagement labels from MVP. If reconsidered later, pilot contextual multi-label spans and overlap. | Approval requested | Consultation for any future taxonomy | Blocks only the deferred extension if approved; accidental schema/UI inclusion would expand MVP. | OPEN |
| AS-OD-07 | Defer metadiscourse annotation from MVP. | Approval requested | Consultation if reconsidered | Blocks only metadiscourse scope; must not be inferred from supplied theory papers. | OPEN |
| AS-OD-08 | Defer metadiscourse lens and method with the feature; if later approved, choose interactive/reflexive and thin/thick separately. | Approval requested for deferral | Advice for future work; final research authority is unresolved | Blocks the future framework/output contract, not MVP after explicit deferral. | OPEN |
| AS-OD-09 | Retrieve Appendix 1 if possible; otherwise consider a manual rubric-versioned fallback with five generic slots/notes and an optional human-entered total. No invented dimensions, weights, or official auto-score. | Approval requested | Approval requested jointly for rubric/fallback; joint-signoff process to confirm | Hard blocker for FR-10 persistence/UI/export and final data design. | OPEN |
| AS-OD-10 | Allow multiple exact evidence spans; distinguish primary claim support from context support. | Approval requested | No required review recorded | Hard blocker for source-link schema, context completion, display, validation and export. | OPEN |
| AS-OD-11 | English-only source/output pilot using PRD's whitespace-delimited English count and recorded tokenizer version; other languages flagged unsupported pending a separate specification/evaluation. | Approval requested | Corpus-language consultation requested | Hard blocker for source eligibility, segmentation and ≤25-word validation. | OPEN |
| AS-OD-12 | Require a trusted server-side reviewer principal for every verification event; do not treat a client-entered display name or current local-user fallback as authorization. | Approval requested | No required review recorded | Hard blocker for verify/reject authorization, audit, multi-user access and verified library. Technical/Security identity feasibility is separate. | OPEN |
| AS-OD-13 | Include a verified report of prior work only as a focal-paper report, with prominent REPORTED_PRIOR_WORK label and citation marker; provide origin filtering and exclude it from primary-findings views. | Approval requested | Consultation on downstream evidence meaning | Blocks origin-aware library, search and export semantics; cannot relabel a reported claim as the focal paper's finding. | OPEN |
| AS-OD-14 | Bind records to PDF, mapping/text and segmenter identity. Mark affected outputs stale on change; preserve history; require new candidate/version and fresh review for re-anchoring. | Approval requested | No required review recorded | Hard blocker for source snapshots, verification validity and current library eligibility. Technical feasibility review is required. | OPEN |
| AS-OD-15 | Stratified sample in intended launch domain; two independent annotators plus adjudication; split development/test by paper; Research Lead confirms sample size. | Approval requested | Approval requested jointly | Blocks gold-set work, evaluation and validated AI/release claims; keep separate from operational OD-01 quorum. | OPEN |
| AS-OD-16 | Preserve PRD 100% traceability, human-review and length process gates; define denominators before evaluation; set model thresholds after pilot rather than inventing them. | Approval requested for release gates | Approval requested for metric definitions, denominators and protocol; formal co-signature needs confirmation | Blocks evaluation contract and release-readiness decisions; reconcile with OD-15 and OD-17. | OPEN |
| AS-OD-17 | Treat initial precision/recall/atomicity/numeric targets and 5,000-word/two-minute goal as provisional pilot measurements until explicitly approved as gates. | Approval requested | Metric interpretation review requested; no joint sign-off formally recorded | Blocks claims that targets are approved/achieved and affects AS-QA-002/003 and AS-API-003 benchmarking. | OPEN |

## Approval routing summary

- **Product Owner approval requested for all 17 decisions.** No Product Owner identity or authority is inferred here.
- **Joint Product Owner and Research Lead approval requested:** AS-OD-09, AS-OD-15, AS-OD-16. Keep each OPEN until both requested outcomes and the joint-signoff process are recorded.
- **Research Lead review requested, co-approval uncertain:** AS-OD-03.
- **Research Lead consultation/review, not documented as mandatory co-approval:** AS-OD-01 (gold-set distinction), AS-OD-04 and OD-05–08 if related research annotations are reconsidered, AS-OD-11 (corpus language), AS-OD-13 (evidence interpretation), AS-OD-17 (metric review). QA-04/05 have exact notes for each.
- **Research Lead-only decision:** None.
- **Technical/Security Lead:** Feasibility confirmation for evidence storage/display (OD-10), tokenizer/segmenter (OD-11), identity (OD-12), source-version invalidation (OD-14), SPS representation (OD-09), and benchmark conditions (OD-17). Such confirmation cannot select product policy.

## Technical decisions the developer can safely finalize

These are implementation-internal choices that preserve established requirements and do not change OPEN policy:

| Technical choice | Safe boundary |
|---|---|
| FastAPI module decomposition | Keep Atomic routes/services/repository isolated from existing Analysis semantics; route names and payload/state meanings still require the approved API contract. |
| Reuse adapters | Reuse the existing paper key, validated source loader, and PDF.js viewer through narrow interfaces; do not duplicate paper/PDF data or reuse Toulmin/AIF records. |
| Offset and source validation mechanics | Implement exact source-slice/hash checks and Unicode offset conversions with tests; the approved source/span contract and eligible source types remain governance inputs. |
| Evidence-anchor failure behavior | Return explicit missing/ambiguous/unavailable states and never guess a PDF anchor; verification eligibility and library rules remain subject to approved policy. |
| AI/human separation | Enforce technically that provider output cannot create a human review event or set VERIFIED. The authorized reviewer, quorum and transitions remain owner decisions. |
| Regression strategy | Plan fixture, API, UI, persistence-integrity and existing-workflow tests; this does not approve thresholds or acceptance of a release. |

The developer must not independently finalize the API/state contract, data schema, identity provider, launch-language/tokenizer policy, SPS scoring fields, evidence cardinality, stale-source publication policy, reported-prior default library treatment, model release gates, PDF retention policy, or provider data-sharing policy.

## Cross-decision consistency gates

| Related decisions / requirement | Required check before baseline |
|---|---|
| OD-01 and OD-15 | Operational publication quorum does not replace independent gold annotation/adjudication. |
| OD-02 and OD-14 | Rejection, regeneration, stale source and re-anchoring preserve immutable history and invalidate old prechecks when required. |
| OD-03 and OD-13 | Functional role and evidence origin are separate; reported prior work is never a focal-paper primary finding. |
| OD-04 and OD-05–08 | Semantic uncertainty preservation remains in the MVP even if separate linguistic annotations are deferred. |
| OD-09 and PRD FR-10 | Preserve the P0 quality-review requirement without inventing SPS dimensions/weights or silently omitting fields. |
| OD-10, OD-11 and OD-14 | Evidence spans use the approved source representation, language/segmenter version and stale-source policy. |
| OD-11 and PRD BR-02 | Supported language, tokenizer version and 25-word rule agree. |
| OD-12 and OD-01 | Reviewer quorum is enforceable with distinct trusted principals and authorization. |
| OD-13 and PRD FR-11/13 | Origin is preserved through default search, filters, primary-finding view and JSON/CSV export. |
| OD-15–17 and PRD §12 | Sample, annotators, metric definitions/denominators, target status and release claims are aligned. |

## Cross-cutting blockers outside the 17 options

| Blocker | Evidence / owner | Effect and safe action |
|---|---|---|
| No authorized approval record | QA-04 register and QA-05 approval verification: 17 OPEN, zero approved. | Complete owner review; proposed options cannot be used as defaults. |
| PRD formal status | PRD header labels v1.0 “Proposed MVP specification.” | Product Owner should confirm whether this is the controlling baseline source and approve any interpretation needed for AS-GOV-002. |
| SPS appendix missing | PRD §3/FR-10 and QA-02/04; Research Lead + Product Owner. | Retrieve Appendix 1 or approve a rubric-versioned manual fallback before final data/UI contracts. |
| Individual reviewer identity absent | AS-TECH-01 current architecture; Technical/Security + Product Owner. | Identify trusted server-side identity and project/paper authorization; verification stays disabled until then. |
| Structured JSON input path | PRD §5.1 and MVP proposal allow it; AS-TECH-01 focuses on GROBID mapping; AS-API-002 already mentions supported JSON. | Add explicit source-adapter/readiness acceptance or obtain approved scope change; preserve source identity and original PDF verification. |
| PDF anchor coverage | PRD §6/§11 requires source verification; PDF.js highlights by quote/page and GROBID offsets do not guarantee glyph mapping. | Test anchor coverage and specify unavailable/ambiguous behavior; do not verify an unanchored item. |
| Library/navigation coverage | PRD FR-11/§11 requires cross-paper library search; AS-TECH-01 tab is per-paper and list mode stays unchanged. | Add an entry to the library inside the same Analysis workspace and map it to AS-LIB-001; no standalone app. |
| Admin/analytics UI mapping | PRD §11 includes admin/analytics; no explicit canonical UI acceptance identified. | Decide its release scope and map it to an existing canonical ticket or approved scope record. |
| Source retention and provider handling | PRD §18 asks if the PDF is retained; current code exposes local/cloud provider config; no retention/data-sharing policy found in the baseline. | Obtain platform/security owner requirements before launch; do not assume local storage or cloud processing policy. |
| Optional SLR System sync | QA-03 retains AS-INT-001 as optional and dependent on a destination contract; no Atomic destination contract was found. | Keep local Atomic workflow independent; do not sync/export externally until the destination owner confirms the contract and access rules. |
| Dependency cycle | AS-DATA-002, AS-SRC-001 and AS-API-002 depend on each other as written in QA-03. | Backlog Owner refines dependency semantics without changing IDs; define contracts/fixtures separately from implementation completion. |
| Historical task-ID conflicts | Original implementation plan vs QA-02 review labels and AI/FE stage labels; QA-03 reconciliation maps them. | Use canonical AS-AREA-### IDs; have Backlog Owner accept the crosswalk before external tracker use. |
| First-code ordering inconsistency | AS-TECH-01 suggests AS-DATA-002; QA-03 dependencies place AS-API-001 before API-002 and DATA-002. | Keep all code tickets blocked now; after gates, approve a non-circular ordering, with AS-API-001 a possible first ticket if its contract prerequisites are satisfied. |

## Status preservation

This matrix preserves the QA-04/QA-05 approval statuses. It does not alter the QA-03 backlog: AS-GOV-001 remains READY FOR REVIEW, the other 27 canonical tickets remain BLOCKED, and none is READY FOR IMPLEMENTATION.
