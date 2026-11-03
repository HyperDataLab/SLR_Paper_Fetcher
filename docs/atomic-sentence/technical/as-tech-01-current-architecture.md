# AS-TECH-01 — Current Architecture Inspection

**Status:** Read-only technical inspection, 2026-11-03.
**Decision status:** This document is descriptive. It does not approve a product, research, schema, API, or implementation decision.
**Scope:** Existing Paper Analysis route, UI, source evidence, storage, providers, identity boundary, and tests.

## Summary

Atomic Sentences can be integrated into the existing paper-detail Analysis workspace. The application already has the target route, a detail-mode tab strip, a PDF.js viewer with text-layer highlighting, a paper catalog, and a validated GROBID full-text mapping. These are reuse points, not evidence that Atomic behavior exists.

The current PaperStore tables and review flow model the existing argumentation and analysis features. They do not provide the required Atomic source-version, evidence-link, review-history, or trusted-reviewer semantics. Atomic should therefore be isolated behind additive storage and service boundaries after the product contract is approved.

## Existing route and page

| Concern | Current implementation | Reuse or extension |
|---|---|---|
| Paper-detail route | `app.py`: `_analysis_paper_id` accepts normalized DOI values and `slrwork_…` work IDs; `paper_analysis_page` serves `templates/analysis.html` at `/analysis/paper/{doi:path}`. | Reuse the route and template context. Keep the existing paper identity; do not create a second catalog. |
| Return path | `templates/analysis.html`: `paperUrl()` generates `/analysis/paper/{paper}?from=/analysis`; `navigatePaper()` uses it. | Preserve this navigation convention. An Atomic tab remains on the same detail route. |
| Analysis landing page | `/analysis` also renders `analysis.html`, with detail mode disabled. | Add the Atomic tab only when `paper_detail_mode` is true unless a later approved product requirement says otherwise. |
| Workspace access gate | `app.py` middleware checks configured `SLR_API_KEY` for GET workspace pages, including `/analysis/paper/…`. | This is a page access gate; it does not identify an individual reviewer for a verification event. |

The `papers.doi` primary-key column is also used for `slrwork_…` keys. The name is legacy; Atomic adapters must accept the same key forms and reference the existing row.

## Existing tabs and layout

`templates/analysis.html` contains the existing detail-mode tab strip and panels in the draft modal. Current tabs include Overview, IMRaD, Paper Blueprint, Toulmin Model, Craft of Research, AIF Graph, Scientific Types, Terms & Taxonomy, Sources, and Citation & Rubric. `analysisTabs` maps tab keys to button IDs; `selectDraftTab()` updates selection and visible panel; click and arrow/Home/End keyboard handlers are registered later in the template.

The detail route styles `#draftViewArea` as a resizable analysis/PDF split. Existing elements include `#paperWorkspace`, `#paperSplitHandle`, `#pdfPane`, `#pdfViewerScroll`, and `#pdfPages`. On narrow screens, the analysis and PDF regions stack vertically. The shared source inspector is currently described as a proposition inspector and is coupled to argumentation data; it is not an Atomic data store or lifecycle component.

The template has substantial inline CSS and JavaScript. `static/css/product-ui.css` and `static/js/sidebar.js` provide shared styling and navigation. There is no separate Atomic frontend package today. A small dedicated Atomic JavaScript/CSS module can be proposed while preserving the template's existing tab registration, accessibility, and route behavior.

## PDF viewer and evidence highlighting

The current viewer is implemented in `templates/analysis.html`:

- `loadPdfViewer()` selects the saved PDF or Markdown source path for the current paper.
- `performPdfViewerLoad()` fetches the existing PDF through `/api/analysis/pdf/{doi}`, uses the locally hosted PDF.js vendor bundle and worker, renders pages, and creates selectable text-layer spans.
- `highlightQuoteOnPage()` finds normalized quote text in the rendered PDF text layer and overlays a highlight.
- `selectPdfSource()` locates a source quote, optionally narrowed by a source page, then asks the viewer to highlight it.
- `selectMarkdownSource()` validates source text and character offsets for Markdown-backed papers.

The PDF highlight path currently matches normalized quote text and page hints; it does not translate GROBID document character offsets directly into PDF.js glyph coordinates. Page spans are helpful but may be absent or coarse. Atomic must therefore validate its exact quote and mapping offsets server-side, pass the paper/source identity and best available page/quote to a small viewer bridge, and display an explicit “PDF anchor unavailable” or ambiguous-match state when it cannot establish a reliable highlight. It must not guess a page or claim an exact PDF anchor from character offsets alone.

GROBID/Python offsets count Python string characters (Unicode code points in normal use); JavaScript string and DOM range indices use UTF-16 code units. If offsets cross the browser boundary, the contract must define the conversion and test supplementary Unicode characters. Prefer returning a verified quote/page anchor from the server and let the existing viewer perform quote matching rather than treating raw offsets as browser indices.

## GROBID full-text mapping

`ai_analysis.py` owns the current extraction and mapping logic:

- `_grobid_extract()` extracts document structure from GROBID.
- `_write_fulltext_mapping()` writes a neighboring `.fulltext.json` mapping with schema version, source PDF filename/SHA-256/size, full text and character length, structural hierarchy, sections, paragraphs, offsets, page and page spans.
- `_load_and_validate_fulltext_mapping()` verifies JSON/schema version, source PDF presence and identity, full-text reconstruction and character count, exact section/paragraph ranges and substrings, hierarchy, and full-text completeness. Partial/abstract-only mappings are rejected.

The existing validator is the preferred source adapter. Atomic should consume its validated result without rewriting the mapping. Preserve the PDF checksum, mapping schema version, exact text/offsets, paragraph order, available page spans, and extraction warnings. Any future Atomic source snapshot should also identify its own segmenter/tokenizer version; the current mapping does not define an Atomic segmentation version.

Inspection of a repository mapping confirmed this shape in practice (schema v2, sections and paragraph ranges round-trip to the corresponding full-text substring). That observation is not a guarantee that every paper has a complete mapping or a usable PDF anchor.

## Paper catalog and SQLite store

`paper_store.py` defines `PaperStore`; `get_store()` returns the store at configured `settings.DB_PATH`. Existing tables include `papers`, `events`, `paper_analyses`, `analysis_runs`, `source_sections`, `scientific_propositions`, `argument_relations`, `aif_nodes`, `aif_edges`, `review_decisions`, `rubric_reviews`, `citation_reviews`, and cross-paper analysis/review tables.

These records support the current paper analysis and Toulmin/AIF meanings. In particular, `scientific_propositions` has existing `proposition_type`, `argumentative_roles`, inferred/origin fields, and `review_status`; `review_decisions` is scoped to existing analysis runs. They are not Atomic Sentence entities and must not be repurposed or reinterpreted. Atomic needs additive records referencing the existing paper key and immutable source identity. The design proposal is in `as-tech-01-database-design-proposal.md`; this task creates no schema or migration.

## API and service patterns

`app.py` registers routes directly on the FastAPI app. Existing paper-analysis routes include `/api/analysis/papers`, `/api/analysis/config`, `/api/analysis/pdf/{doi}`, `/api/analysis/source/{paper_id}`, `/api/analysis/draft/{doi}`, `/api/analysis/argumentation/{doi}`, `/api/analysis/review/{doi}`, and `/api/analysis/enqueue`.

Handlers generally normalize paper IDs, use `get_store()`, move synchronous store work to `asyncio.to_thread`, and return JSON or a file response. There is no Atomic router or service package. A separately mounted Atomic `APIRouter` plus repository, source adapter, application service, and schemas would reduce coupling to the large `app.py` module and keep existing endpoint payloads and business logic unchanged.

## AI providers

`config.py` exposes the configured GROBID endpoint, Ollama URL/model, default provider, Gemini model, and an in-memory Gemini API key setting. `ai_analysis.py:_provider_json()` provides Ollama `/api/chat` and Gemini `generateContent` JSON calls and returns the model identifier. This is a transport capability that an Atomic-specific adapter may call after review; existing prompts, output schemas, run records, and Toulmin/AIF semantics must not be reused as Atomic policy. New prompts and schemas require their own version, strict validation, source provenance, and run metadata. Secrets must not be copied into documents or responses.

## Reviewer identity and current review behavior

The workspace page gate is based on a configured API key. In the examined review path, `/api/analysis/review/{doi}` does not resolve a named human principal; it calls `PaperStore.review_analysis_item()` without a reviewer value. That method defaults the attribution to `local-user`. This fallback is not suitable evidence of individual identity, authorization, or audit attribution for Atomic verification.

Before a verification endpoint can publish an item, the team must select and implement a trusted server-side identity/authorization source and align it with AS-OD-12. A browser-supplied name or the legacy `local-user` default must not authorize verification. AI outputs and prechecks must never create a human verification event.

## Existing test inventory

The repository has `tests/test_outline_analysis.py`, a Python `unittest` suite covering GROBID hierarchy, paragraph IDs and offsets, mapping round-trip/validation, quote spans, source evidence, and persistence remapping. `tests/test_research_results_table.mjs` exercises UI row rendering and actions using a fake DOM. `package.json` defines build, typecheck, and dev scripts, but no npm test script. Playwright is listed in Python requirements, but this inspection found no dedicated Atomic or current analysis-page browser suite under `tests/`.

These existing tests are reuse/regression targets, not tests of an Atomic module. AS-TECH-01 is documentation-only; no tests were run or added.

## Reuse boundary

**Reuse:** paper-detail route and paper key normalization; existing paper catalog and saved PDF; `/api/analysis/pdf/{doi}`; validated GROBID mapping loader; PDF.js viewer and quote-highlight capability; configured AI provider transport; shared visual tokens/accessibility patterns; existing test fixtures where relevant.

**Do not reuse as Atomic semantics:** proposition/argument relation tables; Toulmin/AIF role mapping; current analysis run status; current review decisions; current `local-user` identity fallback; existing analysis prompts or generated conclusions. A viewer bridge may reuse rendering and scrolling while keeping Atomic evidence IDs and lifecycle data isolated.
