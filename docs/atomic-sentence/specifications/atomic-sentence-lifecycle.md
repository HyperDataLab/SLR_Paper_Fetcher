# Atomic Sentence Candidate Lifecycle

**Contract version:** 0.1.0 (proposed)  
**Status:** Draft for product review; no decision here is approved.  
**Date:** 2026-11-03  
**Primary source:** [Atomic Sentence PRD v1.0](../research/PRD_Atomic_Sentence_Paper_Understanding_v1.0.md)  
**Related contract:** [Annotation contract](atomic-sentence-annotation-contract.md)

## 1. Lifecycle scope

This document distinguishes:

- **Processing stages:** operations performed for a paper/run, such as extraction and source validation.
- **Candidate states:** the review state of an individual Atomic Sentence candidate.
- **Precheck verdicts:** machine findings about support and consistency; these do not change a candidate into a human-verified item.
- **Library eligibility:** a derived condition requiring current source evidence and the required human verification.

The PRD’s candidate state path is `DRAFT → PRECHECKED → PENDING_REVIEW → VERIFIED`, with `NEEDS_CONTEXT`, `REJECTED`, and `SUPERSEDED` paths. The PRD treats regeneration as a **new ID**, not as undoing a rejection. Where it does not define transitions or reviewer policy, this document marks them open rather than assuming a product rule.

## 2. Paper/run processing stages

| Stage | Operation | Required result or exception |
|---|---|---|
| P1 — Intake and segmentation | Receive `paper_id` and authorized source content; parse paper/section/paragraph/sentence structure and stable offsets. | Store source identity/checksum and extraction warnings. Missing or unreliable provenance is flagged; it cannot silently become verified evidence. |
| P2 — Candidate detection | Scan paragraph text with section heading and immediate neighboring context; find zero or more research-relevant claims. | Each candidate has an exact supporting source span and extraction provenance. Questions, references-only lines, boilerplate, and headings alone are excluded under the PRD. |
| P3 — Semantic atomization | Propose one or more short, independently intelligible statements from supported source claims. | One source sentence may produce multiple AS IDs. Keep one main testable/reusable proposition and preserve quantities, qualifiers, comparisons, uncertainty, and study context. |
| P4 — Context completion | Resolve source-supported pronouns or implicit entities needed for standalone reading. | Store completion separately from source text; unresolved ambiguity becomes `NEEDS_CONTEXT`. No external facts are added. |
| P5 — Metadata and source origin | Attach functional role, evidence origin, paper metadata, source span, and citation marker(s). | Only the four PRD roles and four PRD evidence origins are used unless a later decision expands them. |
| P6 — Preliminary precheck | Check length, schema, source span, checksum, role, and support/consistency against supplied source. | Save `SUPPORTED`, `PARTIAL`, `CONTRADICTED`, or `UNDETERMINED` with explanation. Precheck is advisory; it cannot approve. |
| P7 — Human cross-reference review | Show AS beside exact source text and original PDF; reviewer checks claim support and quality. | Record reviewer action, identity, time, and rationale where required. Verification is a human action. |
| P8 — Library indexing | Index current verified entries for search/filter/export. | Candidates and rejected history remain available for review but are excluded from trusted retrieval by default. |

The stages belong to an extraction run. A run can be partial or failed without changing a prior run’s candidate decisions. Re-extraction records new run provenance and preserves review history. The PRD requires repeatability and historical decisions to remain intact, but does not specify the run-level state enum; implementation of that enum is a separate decision.

## 3. Candidate states

| State | Meaning | Allowed actions / constraints | Source basis |
|---|---|---|---|
| `DRAFT` | Candidate or atom was generated and has not completed precheck. | Continue automated validation; may be regenerated as a distinct candidate. Not searchable as trusted output. | PRD §9.2. |
| `PRECHECKED` | Machine precheck has produced results. | Show verdicts/warnings and submit for review if required source/evidence is available. Never mark verified automatically. | PRD §6 P6; §9.2. |
| `NEEDS_CONTEXT` | Context required for independent readability cannot yet be resolved, or additional source context is required. | Attach supported context or regenerate a new candidate. It is not eligible for verification while ambiguity remains. A direct reviewer transition into this state is not explicitly specified. | PRD §6 P4; §9.2. |
| `PENDING_REVIEW` | Candidate is ready for a human source check. | Reviewer may verify only after confirming exact source and support; may reject with a mandatory reason. | PRD §6 P7; §9.2. |
| `VERIFIED` | Authorized reviewer has confirmed source existence/support and quality criteria. | Immutable: no in-place changes to text or evidence. Remains eligible only while its source version is current. | PRD §6 P7; §8 BR-06, BR-09. |
| `REJECTED` | Candidate failed support, source, context, or quality review. | Record reason. Candidate remains immutable; regeneration creates a new ID linked to the rejected item. It cannot be changed to verified in place. | PRD §6 P7; §8 BR-07; §9.2. |
| `SUPERSEDED` | A verified version has been replaced by a separately generated and separately reviewed version. | Retain the old record and decision history; a superseded item is excluded from current trusted results unless the user explicitly requests historical entries. | PRD §9.2; §8 BR-09. |

### Precheck results are not states

Precheck stores one of `SUPPORTED`, `PARTIAL`, `CONTRADICTED`, or `UNDETERMINED`. These describe a machine assessment of source support and consistency. They are not equivalents of `VERIFIED`, `REJECTED`, or `NEEDS_CONTEXT`. A `SUPPORTED` result cannot create a verification event. A reviewer may reject an item despite a `SUPPORTED` precheck result.

### Regeneration is new lineage

The PRD names `REGENERATED_AS_NEW_ID` in the state-machine section but also says the rejected candidate is not reversed. This contract proposes representing regeneration as an audit event (`regenerated_from`) plus a new child candidate in `DRAFT`, while the parent stays `REJECTED`. This is a **proposed representation**, not an approved lifecycle detail.

## 4. State transition diagram

```mermaid
stateDiagram-v2
  [*] --> DRAFT
  DRAFT --> PRECHECKED: precheck completed
  DRAFT --> NEEDS_CONTEXT: source context unresolved
  PRECHECKED --> NEEDS_CONTEXT: context unresolved
  NEEDS_CONTEXT --> PENDING_REVIEW: context resolved; source is reviewable
  NEEDS_CONTEXT -.-> PRECHECKED: proposed rerun checks after context
  PRECHECKED --> PENDING_REVIEW: ready for human source check
  DRAFT --> REJECTED: human rejects candidate
  PRECHECKED --> REJECTED: human rejects candidate
  PENDING_REVIEW --> REJECTED: human rejects with reason
  PENDING_REVIEW --> VERIFIED: human verifies exact source and support
  VERIFIED --> SUPERSEDED: separately reviewed replacement exists
  REJECTED -.-> NEW_DRAFT: proposed regeneration representation; new ID
  state "New candidate (new ID)" as NEW_DRAFT
  NEW_DRAFT --> PRECHECKED

  PENDING_REVIEW --> REQUEST_REVISION: proposed action; policy open
  state "Request revision? (not in PRD)" as REQUEST_REVISION
  REQUEST_REVISION --> NEW_DRAFT: proposed new ID; policy open
```

Solid transitions represent paths stated in the PRD. Dashed transitions are proposed representations: rerunning checks after context is supplied, representing regeneration as a new child candidate, and the optional request-revision action. The PRD specifies reject-and-regenerate, not a distinct revision action/state. **[Open decision AS-OD-02]**

## 5. Human verification workflow

### 5.1 Review presentation

Present, together:

- the proposed AS and word count;
- exact source excerpt and source page/highlight in the original PDF where available;
- surrounding paragraph/section context;
- author, year, page or best available locator, functional role, and evidence origin;
- source hash/run provenance and precheck findings;
- comparisons of numeric values, conditions, uncertainty, negation, and omitted/additional text where detectable.

The reviewer must be able to open the broader source paragraph. A machine precheck is clearly labeled as preliminary and advisory. A page label without source text is not sufficient evidence.

### 5.2 Verify

`VERIFY` is allowed only if the reviewer confirms that:

1. The candidate refers to an exact source span in the original paper.
2. The evidence supports the complete AS, including actors, conditions, comparison, numbers, units, timeframe, negation, modality, and uncertainty.
3. The AS is independently intelligible, recomposable, has one main proposition under the proposed operational rule, and has no more than 25 words.
4. Functional role and evidence origin are appropriate under the approved annotation policy.
5. All context-completion wording is supported by linked source spans.

On verification, persist reviewer identity, action, timestamp, source/document version checked, and optional rationale; the PRD requires approval identity/time and an audit trail. The verified text/evidence pair becomes immutable. A subsequent substantive edit requires a new candidate and review.

**Reviewer count remains open.** The PRD describes a human reviewer and asks whether one or two are required. Until decided, the system can record one or more reviewer events but must not claim the review policy is satisfied based on an assumed count. **[AS-OD-01]**

### 5.3 Reject

`REJECT` requires a reason. Reasons may describe missing/incorrect evidence, contradiction, unsupported context, overbroad scope, loss of uncertainty/qualification, numeric mismatch, multiple claims, or length/quality failure. Store the reviewer and timestamp. Do not repair a rejected AS by overwriting it.

### 5.4 Regenerate

`REGENERATE` creates a new candidate ID linked to its rejected parent. Preserve the old rejected text, evidence, reason, and decision. The new candidate must pass precheck and human review independently. The PRD does not require a replacement to be generated automatically after every rejection.

### 5.5 Request revision

The PRD’s explicit recovery policy is reject and regenerate. It does not define a `REQUEST_REVISION` state or reviewer action. A product owner must decide whether reviewers need a separate nonterminal action, whether it creates a new version immediately, and whether the current candidate may be edited before review. Until decided, do not silently treat `NEEDS_CONTEXT` or `REJECTED` as equivalent to a general revision request.

## 6. Verified library publication conditions

An item may be returned by default trusted search only if all of the following are true:

- current workflow state is `VERIFIED`;
- a required human verification event exists and satisfies the eventually approved reviewer policy;
- `word_count <= 25` under the recorded tokenizer version;
- at least one exact source evidence span resolves to the recorded document version;
- the source hash has not changed since verification;
- functional role and evidence origin are valid under the approved scheme;
- any context completion is supported and no unresolved referent/condition remains;
- no later edit or source replacement has invalidated the verification.

These conditions derive from PRD §6 P7–P8, §8 BR-02–BR-09, §14 AT-06–AT-13, and §14 release gates. The PRD explicitly excludes drafts and rejected records from trusted search by default. Historical entries may be inspectable through a separate filter but must remain visibly non-current.

## 7. Audit events

At minimum, retain an append-only event for:

| Event | Required information |
|---|---|
| Candidate generated | Candidate ID, parent/source sentence IDs, evidence spans, source hash, run/parser/model/prompt versions. |
| Precheck completed | Check version, result per check, support status, explanation, source version. |
| Context completed or unresolved | Before/after candidate IDs or values, context evidence spans, completion provenance, unresolved reason. |
| Submitted for review | Candidate version and source version shown. |
| Verified | Reviewer identity, timestamp, exact item/source version, decision, optional rationale. |
| Rejected | Reviewer identity, timestamp, mandatory reason, exact item/source version. |
| Regenerated | Rejected parent ID, new candidate ID, timestamp, new source spans/version, regeneration provenance. |
| Superseded | Previous verified ID, replacement ID, reviewer event for replacement, reason/time. |

The PRD requires extraction provenance and audit history; the precise storage representation is a later data-model decision. This lifecycle does not prescribe a database schema.

## 8. Traceability

| Lifecycle rule | Source |
|---|---|
| Candidate/run stages P1–P8 | PRD §6. |
| State names and paths | PRD §9.2. |
| Four roles, evidence origins, support results | PRD §6 P5–P6; §9.1. |
| Human source check, mandatory reject reason, new ID on regeneration | PRD §6 P7; §7 FR-08–09; §8 BR-06–09. |
| Verified library and default search behavior | PRD §6 P8; §7 FR-11, FR-13; §14 AT-12 and release gates. |
| Reviewer count unresolved | PRD §18 decision 2. |
| Exact source/page/quote review | PRD §5.1–5.2; §11 UX; §14 AT-07, AT-13. |
| Prior research on cue/scope separation | CoNLL-2010, supplied PDF pp. 1–5. |

## 9. Unresolved lifecycle decisions

See [open-decisions.md](open-decisions.md) for stable IDs and impact. The lifecycle-specific open items are reviewer count/identity, a separate request-revision action, edits before verification, the representation of regeneration as an event versus named status, and how a verified record is superseded when its source PDF changes.
