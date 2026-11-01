# SAFFRON per-paper integration plan

## Goal and boundaries

Integrate SAFFRON 4.0 into SLR Paper Fetcher as an independent enrichment stage for each paper. Fetcher owns input validation, SAFFRON invocation, normalized output, local persistence, and upload. SLR-BE remains the artifact store and API surface; no SAFFRON runtime, extraction, or taxonomy logic is added to BE.

The service contract is additive: save the versioned `saffron_analysis` and `openalex_classification` objects inside the existing Fetcher analysis JSON envelope. OpenAlex classification is resolved per paper using an exact DOI match and shown separately from SAFFRON candidates. SLR-BE stores the analysis artifact unchanged and receives the canonical topic IDs through the existing analysis-run metadata field for Repository filters; BE validates and merges those IDs into the existing Work classification without adding extraction logic or a new endpoint.

## Architecture

```text
PDF -> GROBID full-text mapping + checksum
    -> Fetcher analysis worker (one paper/run)
    -> Fetcher-owned HTTP runner in Docker Compose
       POST one-paper text -> SAFFRON Term Extraction module REST API -> normalized terms
       if a compatible trained taxonomy model exists -> SAFFRON taxonomy pipeline -> taxonomy JSON
    -> normalize/validate, attach source text spans, persist with the paper run
    -> existing SLR-BE analysis-runs API stores the additive artifact field
DOI -> OpenAlex primary_topic/topics -> per-paper analysis draft + existing Work classification IDs -> Repository filters
```

The runner wraps SAFFRON with a small HTTP boundary (`GET /health`, `POST /analyze`) and starts the upstream Term Extraction module REST application inside its isolated container. When a compatible taxonomy model is available, the runner invokes the documented `-k TAXO` pipeline; without that model, it returns verified term candidates and `PARTIAL` status with taxonomy marked `UNAVAILABLE_MODEL`. Separately, OpenAlex primary and top topics provide canonical filter IDs for exact DOI matches; they complement SAFFRON term candidates and retain OpenAlex scores/provenance. Compose starts the runner for container deployments. Native Fetcher startup checks the runner and asks Docker Compose to start the SAFFRON service if it is not ready. Failure to start SAFFRON must not prevent the Fetcher UI or existing AI analysis from working; the term/taxonomy stage records explicit status and can be retried.

## Phases and acceptance criteria

### Implementation status (2026-11-01)

| Phase | State | Evidence / remaining gate |
|---|---|---|
| 0 · checkpoint | Done | Commit `d061fb8`; local `.env` remains uncommitted. |
| 1 · runtime | Rebuilt and verified 2026-11-01 | Rebuilt the pinned image from `bcf009f176713ced1d707324043124670827125b`, recreated the runner, and confirmed `GET /health` returns 200 with the term module ready. |
| 2 · extraction | Terms verified; taxonomy prerequisite missing | The direct runner check returned 200 candidates with 177 evidence-resolved; a checksum-pinned saved-paper retry returned 200 with 175 evidence-resolved. Both report `PARTIAL` and `UNAVAILABLE_MODEL`; the mounted `/opt/saffron/models/default.json` is absent. TAXO requires a reviewed compatible trained model; no substitute was used. |
| 3 - Fetcher and SLR API | Implemented; live upload pending | Added a SAFFRON-only retry for completed analyses. It verifies the current PDF and mapping checksums and updates only `saffron_analysis`; a saved-paper retry returned `PARTIAL`, 200 terms, and 175 evidence spans. Headless Chromium confirmed the tab displays the result and its retry button completes successfully. A legacy mapping without checksum pinning is rejected. Static contract review confirmed the upload request fields, idempotency header, and expected HTTP 201 against SLR-BE source and docs; no live write was made. |
| 4 ? docs and verification | Partial | Docker health, the real-paper term path, saved-result rendering, and the UI retry path were verified after rebuilding. Successful SAFFRON taxonomy and live API upload remain unverified; OpenAlex classification is best-effort and omitted without an exact DOI match. |

### OpenAlex Paper Library implementation (2026-11-01)

The Paper Library now exposes Domain → Field → Subfield → Topic filters and an explicit taxonomy sort. It uses `primary_topic` by default to avoid duplicate paper rows and can include secondary topics when requested. A local background backfill stores the classification on paper metadata and mirrors it into completed analysis drafts without rerunning AI/SAFFRON or uploading to SLR-BE. The backfill remains user-triggered; exact DOI matches are required, and unmatched/unavailable states remain visible. Runtime backfill against the current local library was not triggered during implementation.

### Phase 0 — Safe checkpoint

- Commit the current reviewed work before integration changes.
- Keep local `.env` out of Git; preserve it on disk.
- Evidence: checkpoint commit `d061fb8` exists and the local `.env` stays uncommitted.

### Phase 1 — Runtime and service lifecycle

- Add a dedicated SAFFRON CLI image and Compose service, pin/configure the upstream source ref, and provide a health check.
- Add Fetcher settings for service URL, auto-start behavior, startup timeout, and run timeout.
- On Fetcher startup, perform a non-blocking readiness check; in native mode, start the Compose service if needed. In Compose mode, let Compose start the dependency and check readiness without Docker socket access from the web container.
- Acceptance: Compose configuration parses; unavailable Docker/SAFFRON yields a clear diagnostic and does not prevent normal Fetcher startup.

### Phase 2 — Per-paper extraction

- Submit only the current paper as one document to the upstream Term Extraction module REST endpoint, based on the validated full-text mapping and stable paper/run identity.
- Run Term Extraction and the taxonomy pipeline (`-k TAXO`) with bounded timeouts; set `minTermFreq=1` and a bounded `maxTerms=200` so one-paper candidates seen once are not discarded by the corpus default.
- Normalize into a versioned schema with input hashes, extractor/config identity, language, raw score/method, counts, taxonomy links, and review state `candidate`.
- Resolve term mentions to exact offsets/quotes and section IDs in the same mapping; reject stale/mismatched mapping evidence. Preserve raw SAFFRON responses.
- Keep AI analysis successful if only the SAFFRON stage fails.
- Acceptance: term candidates are stored per paper with input hashes and evidence quality metrics; empty/unsupported/failed cases have explicit states and candidates never become accepted filter terms automatically. **Open prerequisite:** provide a reviewed Saffron 4 compatible taxonomy SVM model at `/opt/saffron/models/default.json`. Inspection of the pinned runtime found no model at that path; the [official v4.0 release API](https://api.github.com/repos/insight-centre/saffron/releases/tags/v4.0) lists no uploaded assets. The source's taxonomy pipeline reads the configured file directly, and `taxonomy/train` requires document-term mappings, terms, and gold `.taxo` hierarchy labels. The checkout includes a matched `food_en` benchmark bundle, but it is not a reviewed fit for this SLR domain; the Science gold taxonomies lack matching term/document-term inputs. No project-domain labeled training set has been supplied.

### Phase 3 — Fetcher API and UI

- Expose the SAFFRON stage status/result from the existing local analysis detail endpoint.
- Provide a SAFFRON-only retry for completed AI analyses. Reuse the saved mapping, verify it still matches the current PDF, and update only the SAFFRON artifact without replacing the AI draft.
- Add a Terms & Taxonomy view to the paper detail screen with counts, score context, hierarchy, and source snippets; identify the result as machine-generated candidates.
- Include the versioned result in existing SLR-BE analysis JSON uploads and preserve retry/idempotency behavior.
- During per-paper analysis, resolve OpenAlex metadata by exact DOI (or known OpenAlex work ID) and store primary topic, topic labels/scores, hierarchy labels, and provenance separately from SAFFRON. On upload, pass `classification.primaryTopicId`, top `topicIds`, and associated `subfieldIds`/`fieldIds`/`domainIds` through existing analysis-run metadata. Never infer canonical IDs by string-matching SAFFRON terms.
- Acceptance: each displayed term and taxonomy result belongs to the selected DOI and source checksum; failed SAFFRON runs remain distinguishable from failed AI runs.

### Phase 4 — Deployment guidance and verification

- Document build/start, native versus Compose behavior, version pinning, service diagnostics, and the API envelope extension.
- Run the project's relevant static/build checks and, when Docker Engine is available, verify service health and a representative English paper end to end.
- Acceptance: schema/contract checks pass, status behavior is documented, and runtime evidence is clearly separated from static evidence.

## Decisions and risks

- The OpenAlex filter bridge is recorded in [ADR 0001](../adr/0001-openalex-filter-taxonomy-bridge.md): use canonical OpenAlex IDs from an exact DOI match for existing Repository filters, and keep them separate from SAFFRON term/taxonomy output.
- Paper-level scores are local to that paper and must not be compared across papers as confidence values.
- SAFFRON is English-focused; explicitly non-English papers are marked unsupported. Missing language metadata is recorded as unknown rather than silently inferred.
- Taxonomy on a single paper may be sparse or unhelpful; keep it optional in UI when no valid tree is returned.
- OpenAlex Topics are the canonical IDs for existing Repository filters; they remain separate from SAFFRON term candidates and any SAFFRON hierarchy. Fetcher sends them only after DOI validation, and SLR-BE adds no classifier.
- The upstream repository documents the CLI and Docker modules, but does not provide a stable prebuilt deployment image in the reviewed materials. The service image is built from source; set `SAFFRON_GIT_REF` to a reviewed commit SHA before production use.
- The upstream default term-scoring feature `weirdness` needs a reference corpus, so it is disabled for per-paper runs; other configured document-local features remain enabled.
- The upstream TAXO pipeline requires a trained SVM model at `models/default.json`; the source checkout and clean named volume do not provide one. Do not manufacture a taxonomy or mark it empty when this prerequisite is missing.
