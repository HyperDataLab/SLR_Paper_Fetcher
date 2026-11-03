# AS-GOV-002 — Requirement-to-Ticket Matrix

**Status:** READY FOR REVIEW
**Baseline:** Conditional; no product decisions are approved
**Ticket namespace:** Canonical AS-AREA-### IDs from QA-03 are preserved

## How to read this matrix

CONFIRMED BY PRD means the requirement is explicitly stated in the supplied PRD, not that a Product Owner approved it. PROPOSED — PENDING APPROVAL identifies a QA/technical interpretation. A row may also show one or more blockers. READY FOR REVIEW identifies nonbinding preparation only. Ticket mappings use canonical IDs; unmatched acceptance/screen requirements are called out rather than assigned invented ticket IDs.

The PRD labels FR-01–FR-13 P0 and FR-14–FR-16 P1. The PRD itself is still a Proposed MVP specification. AS-OD statuses remain OPEN.

## P0 functional requirements FR-01–FR-13

| PRD requirement | Required behavior | Canonical ticket mapping | Status and remaining gate |
|---|---|---|---|
| FR-01 Paper intake and traceable segmentation | Stable paragraph IDs, exact source text and structural/source offsets; source identity and warnings. PRD 5.1 also allows structured paper JSON with original-PDF verification. | AS-API-002, AS-SRC-001, AS-DATA-002, AS-QA-004 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-11/14); BLOCKED — TECHNICAL DEPENDENCY (structured-JSON adapter and validated source fixtures). |
| FR-02 Candidate claim detection | Zero-to-many research-relevant claim candidates per paragraph, with location and no quota. | AS-AI-001, AS-SRC-001, AS-QA-001/003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-03/04/11/13); BLOCKED — RESEARCH REVIEW (OD-15 and approved annotation guide). |
| FR-03 One-to-many atomization | Distinct AS IDs; one candidate can produce multiple AS; each approvable AS is at most 25 words and expresses one main claim. | AS-AI-002, AS-DATA-003, AS-QA-001/003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-04/11); BLOCKED — RESEARCH REVIEW for evaluated acceptance (OD-15/16). |
| FR-04 Context completion and ambiguity flags | Resolve only source-supported referents/implicit entities; unresolved references receive NEEDS_CONTEXT or the approved equivalent. | AS-AI-003, AS-SRC-001, AS-QA-001/003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-02/10/14); BLOCKED — RESEARCH REVIEW for gold examples/evaluation (OD-15/16). |
| FR-05 Four-role classification | Use only BACKGROUND, METHOD, FINDING, LIMITATION. Keep role distinct from evidence origin. | AS-GOV-002, AS-AI-002, AS-UI-002, AS-QA-001 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-03/13); BLOCKED — RESEARCH REVIEW (OD-03 mapping-guide review requested; co-approval unresolved). |
| FR-06 Source-anchor and metadata capture | Exact supporting span plus paper/section/page or best available locator and required metadata. | AS-SRC-001, AS-DATA-002, AS-API-002, AS-UI-002, AS-QA-004 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-10/11/14); BLOCKED — TECHNICAL DEPENDENCY (GROBID-to-PDF anchor coverage and structured-JSON source identity). |
| FR-07 Support and consistency precheck | Save source-only support verdict/explanation; flag inconsistencies; advisory output never verifies. | AS-AI-004, AS-API-003, AS-DATA-003, AS-QA-001/002/003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-04/10/11/14/16/17); BLOCKED — RESEARCH REVIEW for evaluated claims (OD-15/16). |
| FR-08 Human verification workflow | Authorized human checks original source/evidence and records decision; AI cannot set VERIFIED. | AS-API-004, AS-UI-003, AS-DATA-003, AS-QA-005/006 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-01/09/10/11/12/14); BLOCKED — TECHNICAL DEPENDENCY (trusted reviewer principal and anchor bridge). |
| FR-09 Discard-not-edit and regeneration | Rejected candidate is immutable; replacement has a new ID and lineage; verified text/evidence changes require fresh review. | AS-AI-003, AS-DATA-003, AS-API-004, AS-UI-003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-02/14); BLOCKED — TECHNICAL DEPENDENCY (append-only events/versioning contract). |
| FR-10 Quality review and SPS fields | Store five dimension reviews and optional reviewer-supplied 0–9 SPS; do not invent rubric or calculate official score. | AS-DATA-001/003, AS-UI-003, AS-LIB-002, AS-QA-002 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION and BLOCKED — RESEARCH REVIEW (OD-09, Appendix 1 or approved fallback). |
| FR-11 Verified library with search/filter | Cross-paper verified-by-default retrieval by claim, paper, author/year, section, role, origin, reviewer and date; drafts/history separately inspectable. | AS-LIB-001, AS-API-004, AS-DATA-003, AS-UI-001, AS-QA-005/006 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-01/09/12/13/14); BLOCKED — TECHNICAL DEPENDENCY (navigation from per-paper tab to cross-paper library). |
| FR-12 Audit and extraction provenance | Retain reviewer, model/prompt version, source checksum and events; repeat runs without overwriting decisions. | AS-DATA-002/003, AS-API-003/004, AS-QA-004/005 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-02/12/14); BLOCKED — TECHNICAL DEPENDENCY (identity and durable audit implementation). |
| FR-13 Structured JSON / CSV export | Export all verified claims with source/evidence IDs and required review provenance in both formats. | AS-LIB-002, AS-LIB-001, AS-API-001/004, AS-DATA-003, AS-QA-005 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-09/10/12/13/14); API example only shows JSON, so CSV contract, encoding and access details are TECHNICALLY UNRESOLVED. |

## PRD business rules BR-01–BR-10

| Rule | Requirement | Canonical ticket mapping | Status and remaining gate |
|---|---|---|---|
| BR-01 Source-only generation | Generator receives only authorized source text; no external search or unsourced claim generation. | AS-AI-001/002, AS-API-003, AS-QA-003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION for authorization/data policy and provider handling; cloud-provider source handling is TECHNICALLY UNRESOLVED. |
| BR-02 Word limit | At most 25 whitespace-delimited English tokens, terminal punctuation convention, stored tokenizer version; overlength flagged. | AS-AI-002/004, AS-DATA-002, AS-SRC-001, AS-LIB-002, AS-QA-001/002 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-11); tokenizer/segmenter feasibility is TECHNICALLY UNRESOLVED. |
| BR-03 Semantic preservation | No change to population, time, sample size, condition, comparison, metric, direction, negation, uncertainty or quantification. | AS-AI-002/003/004, AS-UI-002, AS-QA-001/003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-04); BLOCKED — RESEARCH REVIEW for task-specific gold/evaluation (OD-15/16). |
| BR-04 One main claim | Do not fuse independently verifiable propositions; keep linked numerator/denominator/percentage together. | AS-AI-002, AS-AI-004, AS-QA-001/003 | CONFIRMED BY PRD; evaluation thresholds remain BLOCKED — RESEARCH REVIEW (OD-15/16). |
| BR-05 Evidence support | Every accepted AS has at least one exact original-source evidence span; page-only citation is insufficient for trusted retrieval. | AS-SRC-001, AS-DATA-002/003, AS-UI-002, AS-API-004, AS-QA-004 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-10/14); BLOCKED — TECHNICAL DEPENDENCY (PDF anchor mapping). |
| BR-06 Manual decision | No generated/prechecked state can become VERIFIED without a recorded human action. | AS-API-004, AS-UI-003, AS-DATA-003, AS-QA-005 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-01/12); BLOCKED — TECHNICAL DEPENDENCY (trusted identity). |
| BR-07 Reject, do not overwrite | Reject unsupported/ambiguous items; regeneration links a new candidate to its parent. | AS-DATA-003, AS-AI-003, AS-API-004, AS-UI-003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-02); exact state transitions await lifecycle contract. |
| BR-08 Source-reported vs primary | Do not call a cited prior study’s reported claim a focal-paper primary finding. | AS-AI-001/002, AS-LIB-001/002, AS-QA-001 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-03/13); Research interpretation consultation requested for OD-13. |
| BR-09 Immutable verification | Change to verified text/evidence invalidates or supersedes prior approval and requires fresh human verification. | AS-DATA-002/003, AS-API-004, AS-LIB-001, AS-QA-004 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-14); version/invalidation design remains a technical dependency. |
| BR-10 SPS provenance | No assumed official weighting; store human-entered score only with rubric provenance and five separate assessments/notes. | AS-DATA-001/003, AS-UI-003, AS-LIB-002, AS-QA-002 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION and BLOCKED — RESEARCH REVIEW (OD-09). |

## PRD inputs, outputs, pipeline, and information model

| PRD section/item | Requirement / mapping | Canonical ticket(s) | Status |
|---|---|---|---|
| §2.4 MVP non-goals | No multi-paper synthesis, Toulmin/AIF construction, rhetorical writing, automatic writing citations, external-paper fact-checking, hallucination-free guarantee, replacement of human review, or misuse of workshop κ as model accuracy. | AS-GOV-002, AS-AI-001–004, AS-QA-002/003 | CONFIRMED BY PRD; preserve these boundaries in the approved contract and prompts. |
| §3 scientific criteria | Semantic completeness, independent readability (accurate paraphrase within 30 seconds), recomposability, ≤25 words, author/year/page/role, four roles, SPS provenance, source anchoring and discard-not-edit. | AS-GOV-002, AS-AI-002/003, AS-DATA-002/003, AS-UI-002/003, AS-QA-001/003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION where affected by OD-03/04/09/10/11/14; SPS also BLOCKED — RESEARCH REVIEW (OD-09). |
| §4 users and jobs | Researcher/reviewer inspects, verifies, searches/exports; annotator triggers/triages; administrator configures/monitors; downstream system reads VERIFIED data only. | AS-UI-001/003, AS-API-001/004, AS-LIB-001/002, AS-QA-006 | CONFIRMED BY PRD; identity, roles, admin screen scope, and downstream access contract remain BLOCKED — PRODUCT DECISION / TECHNICAL DEPENDENCY. |
| Goals G1–G7 | Candidate detection, atomization, meaning preservation, exact evidence, roles, human review, verified search/export. | AS-SRC-001, AS-AI-001–004, AS-API-004, AS-UI-001–003, AS-LIB-001/002 | CONFIRMED BY PRD; downstream implementation remains BLOCKED by relevant OD and predecessor tickets. |
| Input: structured paper JSON | Preserve paper/source identity and original PDF verification path. | AS-API-002, AS-DATA-002, AS-SRC-001, AS-QA-004 | CONFIRMED BY PRD; BLOCKED — TECHNICAL DEPENDENCY (adapter/schema/anchor tests); do not narrow to GROBID-only. |
| Output: candidates, verified items, rejected log | Include extraction metadata, anchors, quality/review provenance and replacement lineage. | AS-DATA-003, AS-API-003/004, AS-UI-002/003, AS-LIB-001 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (lifecycle/identity/SPS/source policy). |
| P1 paper ingestion/segmentation | Hierarchy, source offsets, tables/captions and checksums. | AS-API-002, AS-SRC-001, AS-DATA-002, AS-QA-004 | CONFIRMED BY PRD; table/figure alignment is P1, not an MVP expansion. |
| P2 candidate detection | Paragraph/context input, no quota, claim-vs-boilerplate distinctions. | AS-AI-001, AS-QA-001/003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-03/04/11/13) and RESEARCH REVIEW (OD-15). |
| P3 semantic atomization | Split compound claims while preserving the proposition and all essential numerical/scope details. | AS-AI-002, AS-QA-001/003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-04/11), RESEARCH REVIEW for evaluation. |
| P4 context completion | Complete only source-supported referents; otherwise flag ambiguity. | AS-AI-003, AS-SRC-001, AS-QA-001/003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-02/10/14). |
| P5 metadata/origin | Four roles, four origins, citation marker and exact spans. | AS-AI-001/002, AS-DATA-003, AS-LIB-001/002 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-03/13). |
| P6 preliminary validation | Deterministic checks and advisory support result with mismatch flags. | AS-AI-004, AS-API-003, AS-DATA-003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-10/11/14) and RESEARCH REVIEW for evaluation metrics. |
| P7 human cross-reference review | Original PDF, evidence excerpt/context, human VERIFY/REJECT, reason and new-ID regeneration. | AS-API-004, AS-UI-002/003, AS-DATA-003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-01/02/09/10/12/14) and technical identity/anchor dependencies. |
| P8 library indexing | Verified-only default; reviewer history remains inspectable. | AS-API-004, AS-LIB-001/002, AS-DATA-003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-01/09/12/13/14). |
| Core entities and state machine | Paper, section, paragraph, evidence span, run, AS, support, quality assessment and verification event; AI cannot verify; immutable rejected/verified lineage. | AS-DATA-001/002/003, AS-API-003/004 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-01/02/09/10/12/14); exact schema awaits AS-DATA-001. |

## PRD proposed REST API and response requirements

The PRD calls this API contract Proposed. The route names below are not approved; canonical ticket ownership is mapped here.

| PRD API operation | Canonical mapping | Status / contract note |
|---|---|---|
| Start extraction and return run ID | AS-API-001/003, AS-DATA-003 | CONFIRMED BY PRD; PROPOSED — PENDING APPROVAL for exact path/payload/idempotency. |
| Read run progress/counts | AS-API-003, AS-DATA-003 | CONFIRMED BY PRD; PROPOSED — PENDING APPROVAL for state vocabulary/recovery. |
| List/filter/sort/page per-paper AS | AS-API-004, AS-LIB-001 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION for statuses, role/origin and access. |
| Get AS detail/anchors/quality/history | AS-API-004, AS-UI-002, AS-DATA-003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION for evidence/SPS fields and identity. |
| Run precheck | AS-AI-004, AS-API-003 | CONFIRMED BY PRD; advisory-only invariant is mandatory. |
| Verify/reject/regenerate | AS-API-004, AS-UI-003, AS-DATA-003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-01/02/12/14) and trusted identity/anchor dependencies. |
| Save quality assessment | AS-DATA-003, AS-UI-003, AS-LIB-002 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION and RESEARCH REVIEW (OD-09). |
| Search verified library | AS-LIB-001, AS-API-004 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-01/12/13/14). |
| Export verified AS | AS-LIB-002, AS-API-001/004 | CONFIRMED BY PRD for JSON and CSV; exact API example in PRD only illustrates JSON, so CSV and shared-field contract are TECHNICALLY UNRESOLVED. |
| 400/403/409/422/202 errors, idempotency, paper access | AS-API-001/003/004, AS-QA-005 | CONFIRMED BY PRD as proposed behavior; PROPOSED — PENDING APPROVAL for exact error envelope and authorization integration. |

## PRD UX requirements

| PRD UX item | Canonical mapping | Status / gap |
|---|---|---|
| Explorer paper-navigation section tree, paragraph counts, statuses, role/origin filters | AS-UI-002, AS-UI-001 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION for approved labels/filters. |
| Queue with AS ID, status, role, word count, support flag and snippet | AS-UI-002 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION for lifecycle and word-count language. |
| Evidence/verification original PDF, exact highlight, excerpt, numeric/qualifier flags, SPS and review actions | AS-UI-002/003 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-01/09/10/12/14) and TECHNICAL DEPENDENCY (anchor mapping and trusted identity). |
| Synchronized navigation: queue selection scrolls PDF; highlighted span selects AS; paragraph context opens | AS-UI-002, AS-SRC-001 | CONFIRMED BY PRD; technical anchor coverage remains unresolved. |
| Smaller-screen two-panel arrangement and keyboard/accessibility behavior | AS-UI-002, AS-QA-006 | CONFIRMED BY PRD; acceptance awaits UI implementation and usability review. |
| Cross-paper Library with claim search and paper/role/section/origin/reviewer/date filters; verified-only default; draft/rejected history toggle | AS-LIB-001/002, AS-UI-001, AS-API-004 | CONFIRMED BY PRD; AS-TECH-01 needs an explicit in-workspace library entry in addition to the per-paper tab. |
| Admin/analytics screen with run, status, rejection, reviewer, role, source-coverage and model/prompt measures | AS-QA-002/003 and AS-QA-006 cover metric/evaluation work; no dedicated screen ticket is identified | CONFIRMED BY PRD that screen/content is described; priority and canonical implementation mapping are PROPOSED — PENDING APPROVAL / BLOCKED — PRODUCT DECISION. Do not silently omit or promote to P0. |

## PRD metrics and nonfunctional requirements

| PRD item | Canonical mapping | Status / gate |
|---|---|---|
| 100% source traceability, authorized human verification coverage and length compliance process gates | AS-QA-002/003/006, AS-API-004, AS-QA-004 | CONFIRMED BY PRD; Product Owner/Research Lead alignment under OD-16 required before release contract. |
| Support precision ≥90%, candidate recall ≥80%, atomicity ≥90%, numeric faithfulness ≥99% | AS-QA-001/002/003 | CONFIRMED BY PRD as initial internal targets only; BLOCKED — RESEARCH REVIEW (OD-15/16) and BLOCKED — PRODUCT DECISION (OD-16/17) before formal gates/claims. |
| Two-annotator stratified pilot and paper-level evaluation | AS-QA-001/002/003/006 | CONFIRMED BY PRD as pilot protocol; BLOCKED — RESEARCH REVIEW and PRODUCT DECISION (OD-15/16). |
| Integrity, checksums, immutable history, prompt/source versions | AS-DATA-002/003, AS-SRC-001, AS-QA-004 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-14) and technical versioning design. |
| Role-based verification and paper-level access | AS-API-001/004, AS-UI-003, AS-QA-005 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-12) and TECHNICAL DEPENDENCY for trusted principal/access provider. |
| Observability without copying restricted full text into telemetry | AS-API-003, AS-QA-003/005 | CONFIRMED BY PRD; provider/logging policy remains TECHNICALLY UNRESOLVED. |
| Paragraph-level retries and explicit failures | AS-API-003, AS-AI-004, AS-QA-003 | CONFIRMED BY PRD; queue/recovery architecture remains a technical dependency. |
| Reproducibility and no overwrite of reviewer decisions | AS-DATA-002/003, AS-API-003/004, AS-QA-004 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION (OD-02/14). |
| 5,000-word/two-minute performance goal | AS-API-003, AS-QA-002/003 | CONFIRMED BY PRD as proposed benchmark, not guarantee; BLOCKED — PRODUCT DECISION (OD-17) and Technical Lead measurement conditions. |
| Accessibility and semantic status labels | AS-UI-001/002/003, AS-QA-006 | CONFIRMED BY PRD; usability/accessibility acceptance is later QA work. |
| §14 release gates | Pass P0 acceptance; no VERIFIED item without anchored evidence and human event; no approved AS over 25 words; export provenance complete; pilot results reported with denominators/failures. | AS-QA-002/003/005/006, AS-API-004, AS-LIB-002 | CONFIRMED BY PRD; release claims remain BLOCKED — PRODUCT DECISION / RESEARCH REVIEW (OD-15/16/17) until defined and evaluated. |
| §18 explicit open decisions | Parser/highlight choice, reviewer count, PDF retention, reported-prior library policy, and official/manual SPS route. | AS-OD-01/09/10/12/13/14, AS-API-002/004, AS-DATA-001/002, AS-LIB-001 | CONFIRMED BY PRD as open questions; resolutions remain PROPOSED — PENDING APPROVAL and assigned to Product/Research/Technical owners in the AS-OD matrix. |
| §19 done definition | Authorized user opens imported paper, generates candidates, views source evidence, verifies/rejects immutably, inspects quality/provenance, then searches/exports verified items. | AS-API-002/004, AS-AI-001–004, AS-UI-001–003, AS-LIB-001/002, AS-QA-005/006 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION and technical dependencies until approved contract and release gates are satisfied. |

## PRD acceptance scenarios AT-01–AT-14

| Scenario | Expected outcome (PRD) | Canonical ticket mapping | Status / validation gate |
|---|---|---|---|
| AT-01 Compound results | Split into two separately supported AS, not one fused claim. | AS-AI-002, AS-QA-001/003 | CONFIRMED BY PRD; evaluation needs gold set and metrics. |
| AT-02 Numerator/denominator | Keep 11 of 18 and 61% together. | AS-AI-002/004, AS-QA-001/003 | CONFIRMED BY PRD; numerical-faithfulness evaluation pending OD-15/16. |
| AT-03 Association | Do not strengthen “associated with” to “caused.” | AS-AI-002/004, AS-QA-001/003 | CONFIRMED BY PRD; semantic preservation under OD-04. |
| AT-04 Negation | Preserve “did not assess” negation. | AS-AI-002/004, AS-QA-001/003 | CONFIRMED BY PRD; semantic preservation under OD-04. |
| AT-05 Ambiguous referent | Flag NEEDS_CONTEXT; do not fabricate a subject. | AS-AI-003, AS-UI-002, AS-QA-001/003 | CONFIRMED BY PRD; lifecycle label/transition under OD-02. |
| AT-06 More than 25 words | Cannot become VERIFIED; request re-atomization. | AS-AI-002/004, AS-API-004, AS-QA-001 | CONFIRMED BY PRD; tokenizer/language rule under OD-11. |
| AT-07 No resolvable span | Block verification with MISSING_SOURCE_ANCHOR. | AS-SRC-001, AS-API-004, AS-UI-002, AS-QA-004 | CONFIRMED BY PRD; TECHNICAL DEPENDENCY for PDF anchor coverage and OD-10/14 policy. |
| AT-08 AI supported, reviewer rejects | Preserve REJECTED; never mark VERIFIED from model support. | AS-AI-004, AS-DATA-003, AS-API-004, AS-QA-005 | CONFIRMED BY PRD. |
| AT-09 Regenerate after rejection | Create a new AS ID and preserve rejection/lineage. | AS-AI-003, AS-DATA-003, AS-API-004, AS-UI-003 | CONFIRMED BY PRD; exact revision policy under OD-02. |
| AT-10 Cited prior-study claim | Label REPORTED_PRIOR_WORK, not PRIMARY_FINDING. | AS-AI-001/002, AS-LIB-001, AS-QA-001 | CONFIRMED BY PRD; library treatment under OD-13. |
| AT-11 Overwrite verified item | Reject overwrite; require a new version and fresh review. | AS-DATA-003, AS-API-004, AS-QA-004 | CONFIRMED BY PRD; stale/reverification policy under OD-14. |
| AT-12 No status filter | Return VERIFIED records only. | AS-LIB-001, AS-API-004, AS-QA-005 | CONFIRMED BY PRD; library eligibility under OD-01/12/13/14. |
| AT-13 PDF checksum changes | Mark pending candidates stale and block verify until re-anchored. | AS-DATA-002, AS-SRC-001, AS-API-002/004, AS-QA-004 | CONFIRMED BY PRD; implementation rule under OD-14 and technical hash/version contract. |
| AT-14 SPS without exact rubric | Store manual score with rubric version; do not call auto-score official. | AS-DATA-003, AS-UI-003, AS-LIB-002, AS-QA-002 | CONFIRMED BY PRD; BLOCKED — PRODUCT DECISION and BLOCKED — RESEARCH REVIEW (OD-09). |

## Explicit MVP boundary

PRD FR-14 re-extraction/deduplication, FR-15 batch review/shortcuts, and FR-16 table/figure region alignment are P1, not P0. Do not implement them as MVP requirements without an approved scope change. QA-03 preserves advanced hedge/stance/metadiscourse work as AS-AI-005 / AS-QA-007, outside the proposed MVP; semantic preservation required by the PRD remains in MVP regardless.

AS-INT-001 is optional SLR System synchronization and depends on an external destination contract; it is not required for the local PRD MVP. No new canonical ticket ID is introduced by this matrix.
