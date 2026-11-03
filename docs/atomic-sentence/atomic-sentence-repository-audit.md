# Atomic Sentence Integration — Repository Audit

**Scope:** Read-only audit of the existing SLR Paper Fetcher and its potential fit for an Atomic Sentence module. No application code or database schema was changed for this audit.

## Executive summary

SLR Paper Fetcher is an existing FastAPI application for collecting research papers, managing a local PDF library, analyzing papers, reviewing source-grounded claims, and optionally synchronizing papers and analysis artifacts with an external SLR System. It already provides most of the infrastructure Atomic Sentence needs: DOI-based paper identity, validated local PDF files, GROBID extraction, checksum-pinned full-text mappings, AI provider adapters, asynchronous analysis status, a PDF review interface, and persisted human decisions.

Atomic Sentence should be added as a new workflow within this application. It should consume the existing paper and full-text artifacts and save its own versioned results and review history. It should not replace paper analysis, Toulmin/AIF graphs, SAFFRON enrichment, OpenAlex classification, or download behavior. The current schema and business logic remain unchanged during this analysis task.

## What exists and how it works

### User-facing functions

- **Search and acquisition:** DOI input and batch inputs are normalized and resolved; the downloader checks public sources and, where configured, authorized institutional access. PDF responses are validated before they are accepted. The application also handles retry/status feedback, filename safety, and RIS export.
- **Local paper library:** downloaded files are registered by DOI in SQLite, with metadata, provider/source, file path, status, and status events. The analysis library only exposes saved valid PDF or Markdown inputs.
- **Paper analysis:** a background queue accepts selected papers. The worker invokes the existing AI pipeline and stores a draft and structured analysis. The pipeline includes paper profiles, outline and writing-style analysis, propositions, argumentative roles and relations, Toulmin structures, and an AIF graph. SAFFRON term/taxonomy results and OpenAlex classification are separate enrichments.
- **Human review:** reviewers can inspect analysis alongside the source PDF, follow evidence back to quotes/pages, edit supported analysis items, record decisions, and review argument graphs. Existing workflows consistently label AI output as a draft and do not treat machine validation as scientific validation.
- **Optional SLR System integration:** the Fetcher can list configured projects and push papers and completed analysis artifacts to an external SLR System API. That system is a separate destination; it is not the Fetcher’s local database.

### Runtime and component communication

The backend is **FastAPI**, defined in [`app.py`](../app.py). It serves Jinja templates and static files and exposes JSON endpoints used by browser-side JavaScript. The main workspace is split among pages such as `/`, `/upload`, `/repository`, `/analysis`, and `/settings`. Most page behavior is implemented in the templates and their JavaScript; `static/js/` contains shared scripts. The `frontend/` TypeScript/React code is specifically used for Toulmin and AIF graph widgets, built by Vite into `static/build/` and mounted in the existing pages. It is not a separate frontend application.

Paper acquisition is coordinated by the FastAPI routes and modules including [`doi_resolver.py`](../doi_resolver.py), [`automatic_sources.py`](../automatic_sources.py), [`downloader_engine.py`](../downloader_engine.py), [`browser_session.py`](../browser_session.py), [`browser_pdf.py`](../browser_pdf.py), and [`paper_io.py`](../paper_io.py). These modules cover DOI normalization, source discovery, public/institutional download paths, browser-captured PDFs, safe local paths, and PDF validation.

The analysis path is:

```text
saved paper/PDF
  -> FastAPI analysis enqueue endpoint
  -> in-process async queue and worker
  -> ai_analysis.py
  -> GROBID TEI extraction and validation
  -> checksum-pinned .fulltext.json mapping
  -> Ollama or Gemini structured AI calls
  -> persisted analysis run and review UI
```

GROBID output is converted into document metadata, sections, paragraphs, offsets, and page spans. The mapping is written beside the PDF as `.fulltext.json`, carries a schema version and source-PDF SHA-256, and is validated before analysis. The PDF itself is served back to the browser for review; `pdf.js` is vendored for the current PDF viewer. `pypdf` is also used in the AI pipeline for page-level source checking. No dedicated OCR service is configured in the repository.

The main service modules are:

| Area | Existing implementation | Relevance to Atomic Sentence |
|---|---|---|
| Web app and API | [`app.py`](../app.py), FastAPI, in-process async queues | Host new pages/endpoints in the same app. Prefer a small Atomic router/service package mounted from `app.py` over extending the already large route module with all logic. |
| Paper identity and files | [`paper_io.py`](../paper_io.py), [`paper_store.py`](../paper_store.py), `downloads/` or configured download directory | Reuse DOI normalization, saved paper records, validated files, and metadata. |
| PDF acquisition | `automatic_sources.py`, `downloader_engine.py`, `browser_session.py`, `browser_pdf.py`, `institutional_auth.py` | Reuse for acquisition; do not build a second downloader or duplicate the PDF library. |
| Extraction and evidence | [`ai_analysis.py`](../ai_analysis.py), GROBID, `.fulltext.json`, PDF.js viewer | Reuse mapping, checksums, section/paragraph anchors, PDF display, and source quote validation; add a deterministic sentence index over the existing text. |
| AI calls | `ai_analysis.py` provider JSON helper, configured Ollama/Gemini endpoints | Reuse provider/configuration and structured-output conventions, while keeping Atomic prompts, schemas, versions, and stage status independent. |
| Persistence | [`paper_store.py`](../paper_store.py), SQLite with foreign keys and WAL | Reuse the same database file and transaction conventions. A later additive Atomic schema is preferable to overloading proposition/relation tables. |
| Review interface | `templates/analysis.html`, shared sidebar, JavaScript review controls, graph components | Reuse page layout, source display, review interaction patterns, status labels, and audit conventions. |
| Graphs | `frontend/toulmin-graph/`, `frontend/aif-graph/` | Keep existing graph contracts and views. Atomic Sentence is sentence-centered and does not require a third graph in its initial scope. |
| Deployment | [`compose.yaml`](../compose.yaml), [`Dockerfile`](../Dockerfile) | Reuse current app image and named data/download volumes. Existing GROBID and AI services are already defined. |

### Persistence and external services

The local database is SQLite, configured through `settings.DB_PATH` in [`config.py`](../config.py) and stored by default at `data/papers.sqlite3`. [`paper_store.py`](../paper_store.py) owns database initialization and access. Its current schema includes `papers`, `events`, `paper_analyses`, `analysis_runs`, `source_sections`, `scientific_propositions`, `argument_relations`, AIF graph records, and multiple review tables. Analysis JSON and nested provenance are stored alongside normalized rows. PDF files and full-text mapping JSON are filesystem artifacts, not BLOBs in SQLite. Docker Compose persists app data and downloads through named volumes.

AI uses Ollama or Gemini through existing HTTP/structured-JSON code. GROBID is an external service. SAFFRON is an existing isolated Compose service accessed through `saffron_client.py`. No Atomic Sentence API, Atomic-specific tables, or Atomic-specific AI pipeline was found.

## Atomic Sentence requirements and available source material

The requested capabilities are: paper management, PDF ingestion and extraction, provenance, candidate sentence extraction, hedge detection/scope, stance, engagement, metadiscourse, semantic atomization, context completion/validation, AI precheck, human verification, and a verified sentence library.

No Atomic Sentence PRD or Atomic-specific academic research pack was found in the repository’s tracked documentation, source tree, tests, `docs/`, `research_notes/`, or `reports/`. Existing research notes primarily document SAFFRON integration and model availability. Existing blueprints and the data inventory are useful architectural evidence, but are not an Atomic Sentence specification. In particular, [`current-analysis-data-inventory.md`](blueprints/current-analysis-data-inventory.md) records source-grounded propositions, offsets, writing-style metrics (including a hedging-marker count), provenance, pending review states, and reviewer history; it does not define the Atomic Sentence label set or adjudication rules.

Therefore, this proposal treats the numbered requirements in the task as the capability scope. Detailed definitions—especially “atomic,” hedge scope, stance/engagement categories, context completion policy, and verification thresholds—must be agreed from the PRD/research foundation before implementation. The implementation plan includes that contract work as a prerequisite.

## Current behavior to preserve

An Atomic Sentence entry point must not disrupt:

- DOI/batch search, public and institutional retrieval, PDF validation, retry and download-state reporting.
- The existing paper library, file paths, RIS export, and optional SLR System upload/sync.
- The analysis queue and saved drafts, GROBID extraction/mapping, provider settings, SAFFRON and OpenAlex enrichment.
- Current paper-profile/outline, propositions, evidence, Toulmin, AIF, cross-paper, citation, and rubric review workflows.
- Existing PDF display, source highlights, status recovery, and stored run history.

Atomic output must not overwrite a source quote with an atomized rewrite, mutate existing analysis drafts, or imply scientific validity because it passed an automated check.

## Integration findings

1. **Reuse the paper as the canonical management object.** The existing `papers` record and valid saved file are the paper library. Atomic should attach to that record and its optional project/work identifiers, not create another independent paper catalog.
2. **Reuse extraction artifacts.** Read the saved checksum-pinned full-text mapping. Add sentence segmentation/indexing as an additive layer tied to that exact mapping and PDF hash. Keep source offsets in the mapping’s declared text representation and keep page spans where available.
3. **Keep analysis runs separate by purpose.** Atomic analysis has distinct outputs and lifecycle from current proposition/argument analysis. It should have its own run identity, stages, versioned annotations, and review state, while sharing the PDF and mapping.
4. **Reuse the application boundary and configuration.** Add Atomic API routes and services to FastAPI. Reuse the existing configured AI providers, GROBID endpoint, SQLite file, downloads volume, and PDF viewer. Avoid a second application, second paper store, or new infrastructure service for the first version.
5. **Add persistence only after the data contract is agreed.** Current SQLite tables contain useful patterns, but sentence annotations and scope links do not have equivalent semantics in `scientific_propositions`. Plan additive Atomic-specific tables or artifacts later; no schema change is part of this audit.
6. **Treat verification as a human decision.** AI precheck can flag span mismatches, unresolved context, ambiguous scope, or schema issues. It cannot mark an item verified. Only a recorded reviewer decision can publish an entry to the Verified Atomic Sentence Library.
7. **Confirm external synchronization separately.** The existing SLR System integration uploads papers, the full-text mapping, and current analysis JSON. No Atomic-specific remote API contract was found. Local Atomic operation should not depend on remote support; add synchronization only after the destination’s contract is confirmed.

## Risks and open questions

- The missing Atomic PRD and academic foundation leave labels, definitions, and acceptance thresholds unspecified.
- Sentence splitting and offset preservation can diverge from PDF layout, especially with hyphenation, equations, tables, references, or OCR-like extraction errors.
- Hedge scope often extends beyond the marker phrase; clause-level, sentence-level, and discourse-level scope need distinct rules and review affordances.
- Context completion and semantic atomization can introduce claims or certainty absent from the paper. The design must preserve original text and source anchors and label every inferred addition.
- Stance, engagement, and metadiscourse labels may overlap or be discipline-specific. Versioned annotation guidance and a reviewed gold set are needed before quality thresholds are meaningful.
- GROBID does not provide a repository-configured OCR fallback. Scanned/poor-quality PDFs need explicit partial or unsupported statuses rather than fabricated sentences.
- The local app uses one workspace and a local SQLite database. Multi-user identity, reviewer attribution, shared libraries, and project-level permissions require confirmation before a collaborative deployment.
- External SLR System support for Atomic data is unknown; do not infer it from the generic analysis upload route.
- Large corpus review and repeated LLM calls may outgrow the current simple in-process queue. Measure pilot volume and reliability before adding queue infrastructure.

## Source files reviewed

The audit covered the repository README/product description, FastAPI app and API routes, configuration, paper storage and IO, analysis and provider code, acquisition/browser modules, Saffron adapter and deployment, templates/static scripts, React graph sources, package/dependency declarations, Docker configuration, existing blueprint/ADR/research notes, and current tests. References: [`README.md`](../README.md), [`PRODUCT.md`](../PRODUCT.md), [`app.py`](../app.py), [`ai_analysis.py`](../ai_analysis.py), [`paper_store.py`](../paper_store.py), [`paper_io.py`](../paper_io.py), [`browser_pdf.py`](../browser_pdf.py), [`compose.yaml`](../compose.yaml), [`current-analysis-data-inventory.md`](blueprints/current-analysis-data-inventory.md), and [`ai-to-scientific-paper-blueprint-roadmap.md`](blueprints/ai-to-scientific-paper-blueprint-roadmap.md).
