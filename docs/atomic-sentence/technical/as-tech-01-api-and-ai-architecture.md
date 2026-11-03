# AS-TECH-01 — API and AI Architecture Proposal

**Status:** Service and contract proposal for review. Routes, state transitions, schemas, and release behavior are not approved.
**Integration target:** Existing FastAPI application and existing paper/source artifacts.
**Constraint:** Do not change existing `/api/analysis` behavior or Toulmin/AIF semantics.

## Backend boundaries

`app.py` currently registers routes directly and is already a large module. Add an Atomic boundary as a separately defined and mounted FastAPI `APIRouter` only in a later implementation ticket:

```text
app.py (composition only)
└── atomic_sentences.router
    ├── schemas.py             request/response validation
    ├── service.py             use cases and lifecycle guards
    ├── repository.py          additive Atomic persistence
    ├── source_adapter.py      PaperStore + PDF/GROBID mapping validation
    ├── viewer_anchor.py       verified quote/page anchor response
    ├── pipeline.py            run orchestration and stage provenance
    ├── providers.py           Atomic-specific provider adapter
    └── review_identity.py     trusted principal/authorization integration
```

The router should validate inputs and resolve a server principal, then delegate to services. The source adapter may call the existing paper lookup, PDF validation, and `ai_analysis._load_and_validate_fulltext_mapping()` behavior through a stable adapter. Avoid making Atomic depend on private extraction internals without an adapter boundary. The Atomic repository uses new records after AS-DATA-001 approval; it does not reuse analysis-run or proposition tables.

## Proposed endpoint surface

Paths below are options for contract review. Exact routes, response fields, statuses, filters, and authorization rules remain subject to AS-API-001, AS-API-002, AS-API-004 and the approved product contract. Existing routes are not altered.

| Proposed endpoint | Purpose | Key response/guard |
|---|---|---|
| `GET /api/atomic/papers/{paper_id}/readiness` | Check that the existing paper, saved PDF, mapping, source completeness and compatible versions are available. | Paper key, source hash/version, mapping schema, warnings and explicit states such as ready/partial/missing/stale/unsupported. Never starts a run. |
| `GET /api/atomic/papers/{paper_id}/source-index` | Read section/paragraph/sentence units and counts for the selected Atomic source version. | Exact source text, IDs/order/offset/page spans and version IDs, with access controls and bounded pagination. |
| `POST /api/atomic/papers/{paper_id}/runs` | Request an Atomic run for the current validated source version. | Idempotent run ID and accepted/current source version. Must not create a duplicate paper or overwrite analysis runs. |
| `GET /api/atomic/runs/{run_id}` | Read stage/status/error/provenance. | Only Atomic run state and version information. |
| `GET /api/atomic/runs/{run_id}/candidates` | List candidate/AS proposals for the run with filters and pagination. | Never implies verification; include status, role/origin proposal, word count and support state as allowed by the contract. |
| `GET /api/atomic/sentences/{as_id}` | Read one AS version with source and context evidence details. | AS text and source text remain separate; includes source version and anchor resolvability. |
| `POST /api/atomic/sentences/{as_id}/precheck` | Run or refresh deterministic and advisory checks. | Versioned findings only. Must not append a review event or set VERIFIED. |
| `POST /api/atomic/sentences/{as_id}/verify` | Record authorized human verification. | Requires trusted principal, authorization, current source, required evidence and valid lifecycle transition; append-only event; rejected on missing prerequisites. |
| `POST /api/atomic/sentences/{as_id}/reject` | Record authorized human rejection. | Requires trusted principal and approved transition; preserves original record and reason/history. |
| `POST /api/atomic/sentences/{as_id}/regenerate` | Create a linked proposal from a new run/context. | Creates a new candidate/version; cannot mutate rejected/verified history in place. |
| `GET /api/atomic/library` | Search/filter Atomic records under approved library eligibility rules. | Verified-only default if retained in the approved contract; explicit origin, source, role and verification fields. |
| `GET /api/atomic/export?format=json|csv` | Export records matching approved filters. | Consistent snapshot, provenance and evidence links; enforce user/project scope. |

Use structured errors for invalid paper IDs, missing paper/source, invalid or partial mappings, hash mismatch, unsupported language, stale source, invalid lifecycle transition, missing reviewer identity/authorization, rate/queue limits, and provider errors. Error details should not expose credentials or local filesystem paths.

## Request flow and source-to-anchor mapping

1. Resolve the existing paper key with the same DOI/`slrwork_…` validation used by the Analysis application.
2. Load its saved file from `PaperStore`; require the expected valid source type and preserve the existing file.
3. For PDF processing, load and validate the corresponding `.fulltext.json` through the current GROBID mapping validator. Check full-text completeness and PDF SHA-256/size, exact section/paragraph ranges, and hierarchy.
4. Snapshot a version identity for the PDF, mapping schema/artifact content, extracted text, and later Atomic segmenter/tokenizer versions. Report mapping/page coverage gaps; do not fabricate anchors.
5. Build section/paragraph/source-sentence units under an approved language/segmentation contract. Every unit's text must round-trip to its canonical full-text span.
6. Give the source-only context to the Atomic pipeline. Candidate extraction returns zero or more source-grounded candidates; atomization may produce zero or more proposed AS records per candidate. Preserve exact source quote separately from generated text.
7. Persist run provenance, candidate lineage, source evidence links, and deterministic/advisory prechecks. A failed output is visible as a failed stage, not as a partially verified record.
8. Return source excerpt/context and a best available page+quote anchor to the frontend adapter. The adapter calls the existing PDF.js viewer and quote-highlighting function. If quote matching is ambiguous or unavailable, leave the text evidence visible and show the anchor limitation; do not claim a successful exact highlight.
9. A later authorized human review request re-checks the current source version and state transition inside the service/transaction, resolves identity from the server's trusted authentication context, and appends a review event.

This design does not assume PDF text layer and GROBID text have a one-to-one character-coordinate map. Exact offsets in the GROBID canonical full text and PDF highlight geometry are different locator systems; an explicit validated bridge is required.

## AI pipeline proposal

| Stage | Work | Non-negotiable boundary |
|---|---|---|
| Readiness and source capture | Validate paper/PDF/mapping identity, completeness, extraction warnings, language eligibility, and source version. | Source-only; no external web/general-knowledge evidence. |
| Structure and sentence index | Preserve section/paragraph order, exact offsets and page spans where present; run a versioned deterministic segmenter. | Do not change source text; unresolved language/segmentation policy remains blocked. |
| Candidate extraction | Identify research-relevant candidate passages with zero/one/many results per paragraph. | Every candidate points to exact source evidence. |
| Atomization | Produce one or more proposed concise, independently verifiable statements from a candidate where justified. | Preserve quantities, units, comparison/direction, population, time, negation, uncertainty, modality and causal limits; do not infer from general knowledge. |
| Context linking | Attach source context for supported referent completion or necessary conditions. | Ambiguous referent/condition remains NEEDS_CONTEXT or an equivalent approved state; no invented context. |
| Deterministic precheck | Validate schema, source identity, exact quote/offset, evidence link, tokenizer word count, required fields and obvious numeric/unit/negation mismatch. | Version the rules. A deterministic pass is not human verification. |
| Advisory model precheck | Ask the provider to flag possible support, qualifier, comparison, numeric or context mismatch with evidence-linked explanation. | Advisory only. It cannot set status, create verification events, or overrule source text. |
| Human review | Present source/proposal together; record verify/reject and reviewer attribution. | Requires approved lifecycle and trusted human identity. Only the service accepting an authorized human action may create a VERIFIED transition. |

For the MVP proposal, roles are the PRD's `BACKGROUND`, `METHOD`, `FINDING`, `LIMITATION`; evidence origins are `PRIMARY_FINDING`, `REPORTED_PRIOR_WORK`, `AUTHOR_INTERPRETATION`, `METHOD_DESCRIPTION`. Store these separately. They remain pending AS-OD-03/13 approval. Keep full hedge cue/scope extraction, sentence-level uncertainty classification, Hyland stance/engagement, and metadiscourse outside the proposed MVP unless formally approved. Semantic preservation of uncertainty is still required by the PRD proposal and must not be weakened by omitting those annotation systems.

## Provider adapter and provenance

The existing `_provider_json()` transport can inform a new Atomic adapter for Ollama and Gemini. The adapter must select a configured provider, construct an Atomic-specific prompt/schema, apply local schema and business validation, record the model and prompt/schema version, bound request size/time, surface provider failure, and avoid sending unsupported source content. Provider configuration is not approval of a model, prompt, quality threshold, or data-sharing policy. Store provider/model versions, prompt and schema IDs, run settings and output hash/lineage. Never log API keys or place secrets in client-visible configuration.

Do not reuse existing Toulmin/AIF prompts, `analysis_runs`, proposition types, relation types, or reviewer states. Atomic generation is a distinct contract. A provider returning a field named `verified` must be rejected or ignored by the Atomic response validator.

## Run orchestration

The app currently uses an in-process analysis queue with a single worker. Atomic run orchestration should have an independent state namespace and worker/service boundary so it cannot overwrite or block the current analysis lifecycle. Durable queueing, restart recovery, concurrency, retries, cancellation, idempotency, and resource limits need an explicit later design. For the inspection phase, document the current limitation; do not assume the existing queue is durable or suitable for Atomic load.

## Review and authorization lifecycle

The present workspace API-key gate and `local-user` review default do not establish an individual reviewer identity. The Atomic API must resolve a principal from an approved server-side authentication integration and authorize the paper/project action on the server. If none is available, read-only design/proposal work can proceed but VERIFY must remain disabled and the endpoint must reject verification.

The approved lifecycle will determine whether verification is one or two reviewers, how request-revision is handled, and how edits/regeneration affect prior decisions. Until then:

- No action is recorded as authorized by a named human unless authentication establishes that principal.
- No system or AI event can write a human VERIFY event.
- Reject and regenerate preserve lineage and prior events.
- A source change invalidates or revalidation-gates the prior review according to the still-open AS-OD-14 decision.

## Search and JSON/CSV export

Search reads the existing paper metadata through its paper key and joins it with Atomic AS/evidence/review records. The MVP search proposal covers text, paper, author/year, section, role, origin and verification status. Library eligibility and reported-prior-work treatment remain conditional on AS-OD-13 and the approved requirements. JSON and CSV exports should include exact source quote/locator and source checksum/version, AS/candidate lineage, review identity/time, role/origin, and any approved rubric provenance. Exports must distinguish source text and AI statement and must not label an AI precheck as verification.

## API/AI approval dependencies

- **Product approval:** All AS-OD-01–17 remain OPEN; AS-GOV-002 has no approved baseline. Route semantics, source policy, role/origin, review transitions, language/tokenizer, evidence cardinality, stale-source behavior, library/search and export are not final.
- **Research approval:** AS-OD-09, AS-OD-15 and AS-OD-16 remain OPEN pending Research Lead review and Product Owner approval. AS-OD-03 role mapping has Research Lead review requested; QA-04 says whether that is mandatory co-approval needs confirmation.
- **Technical/security review:** Identity provider, source anchor coverage, segmentation, persistence alternatives and orchestration feasibility may be prepared for review. They do not substitute for product or research approval.

Decision-level impact map (all rows remain OPEN):

| Decision | API, data, UI, or evaluation impact | Requested approval/review |
|---|---|---|
| AS-OD-01 | Review quorum and who can make the verification transition | Product Owner; Research Lead consultation on operational vs gold-set review |
| AS-OD-02 | Whether a separate request-revision action and corresponding endpoint/state are required | Product Owner |
| AS-OD-03 | PRD role mapping, AI output schema, filters, and annotation guide | Product Owner; Research Lead review requested, co-approval authority unresolved |
| AS-OD-04 | Preserve uncertainty semantics vs add separate hedge annotations | Product Owner |
| AS-OD-05 | Whether sentence uncertainty labels and label semantics exist | Product Owner; Research Lead if research label is included |
| AS-OD-06 | Whether stance/engagement fields and overlap rules enter scope | Product Owner; Research Lead consultation for future taxonomy |
| AS-OD-07 | Whether metadiscourse is in MVP | Product Owner |
| AS-OD-08 | Framework lens and analysis method if metadiscourse is included later | Product Owner; Research Lead advice requested, final future authority unresolved |
| AS-OD-09 | SPS fields, rubric version, scoring and review UI | Product Owner and Research Lead review/approval requested |
| AS-OD-10 | Number/type of evidence links and primary/context semantics | Product Owner |
| AS-OD-11 | Supported languages, segmenter, tokenizer, and hard word-count behavior | Product Owner; Technical Lead feasibility; Research Lead corpus-language consultation |
| AS-OD-12 | Trusted principal, authorization, reviewer ID and verification endpoint guard | Product Owner; Technical/Security feasibility review |
| AS-OD-13 | `REPORTED_PRIOR_WORK` citation treatment, search and export visibility | Product Owner; Research Lead consultation requested |
| AS-OD-14 | Source-version invalidation, stale state, re-anchoring and library eligibility | Product Owner; Technical Lead feasibility review |
| AS-OD-15 | Gold-set sample, annotators, split and adjudication records | Product Owner and Research Lead review/approval requested |
| AS-OD-16 | Evaluation metrics, denominators, thresholds and release gates | Product Owner and Research Lead review/approval requested |
| AS-OD-17 | Pilot-target vs release-gate treatment and runtime benchmark conditions | Product Owner; Technical Lead benchmark review; Research Lead metric review |

No endpoint, prompt, schema, queue, migration, or application behavior is implemented by this proposal.
