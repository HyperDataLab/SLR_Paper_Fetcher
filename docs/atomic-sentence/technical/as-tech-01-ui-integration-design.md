# AS-TECH-01 — Atomic Sentences UI Integration Design

**Status:** UI proposal for review; no workflow or product decision is approved.
**Target:** Existing Paper Analysis detail page, e.g. `/analysis/paper/{paper_id}?from=/analysis`.
**MVP boundary:** Follows PRD v1.0 and the current MVP proposal. It does not expand the MVP or settle OPEN decisions.

## Entry point and navigation

Add a visible **Atomic Sentences** tab to the existing `analysis.html` tablist on the paper-detail route. The entry is available for the currently selected paper, so it uses that existing paper record and route; it does not open a standalone application or create another paper catalog. Keep the `/analysis` list/overview unchanged unless a separate approved decision requests an entry there.

Implementation touchpoints to consider later:

- Add a `draftTabAtomic` button and `draftAtomicView` panel in `templates/analysis.html`, visible in detail mode.
- Add one `atomic` entry to `analysisTabs` and use the existing `selectDraftTab()` and arrow/Home/End keyboard behavior.
- Provide a dedicated `static/js/atomic-sentences.js` module and `static/css/atomic-sentences.css`, loaded by the existing template. The module owns Atomic state/rendering and communicates through an API client; it does not edit the Toulmin/AIF state.
- Keep `paperUrl()`, the current paper key, and `?from=/analysis` navigation intact.

These are design touchpoints, not code changes made by AS-TECH-01.

## Desktop workspace

Use three synchronized regions on the same detail page:

```text
Existing Analysis tabs: Overview | … | Atomic Sentences
┌────────────────────┬─────────────────────────┬──────────────────────────────┐
│ Paper Navigation   │ Atomic Sentence Queue   │ Evidence & Verification      │
│ section tree       │ AS ID and proposed text │ Existing PDF.js viewer       │
│ counts and filters │ status, role, word count│ exact highlight when resolvable│
│                    │ support indicator       │ excerpt, context, warnings   │
│                    │                         │ review controls              │
└────────────────────┴─────────────────────────┴──────────────────────────────┘
```

The current detail page already places a resizable analysis pane beside `#pdfPane`. Keep that PDF pane and viewer as the third region. Inside the Atomic tab's analysis pane, use a narrower Paper Navigation rail next to a flexible queue. Within the existing `#pdfPane`, expose a bounded Evidence & Verification inspector alongside/under the PDF.js scroll area; keep PDF controls and viewer ownership with the existing code. The existing vertical splitter remains the boundary between the left navigation/queue workspace and the source/PDF workspace. Do not render another PDF.js instance.

Proposed content:

| Region | Contents | Synchronization |
|---|---|---|
| Paper Navigation | GROBID section hierarchy; per-section paragraph and candidate counts; role filter; evidence-origin filter; candidate/review status filters. | Selecting a section narrows the queue and scrolls the source excerpt/view to the corresponding verified source location. Counts reflect the returned Atomic run/library scope and label that scope. |
| Atomic Sentence Queue | Stable AS ID; proposed or reviewed text; explicit lifecycle status; role; approved word-count convention; evidence-support summary. Rows are keyboard navigable. | Selecting a row loads the matching source quote/context and asks the existing viewer bridge to highlight the best verified PDF anchor. |
| Evidence & Verification | Original PDF viewer; exact extracted source excerpt; context; source page/section and available offsets; quote/anchor status; qualifier, negation, numeric/unit and comparison consistency findings; VERIFY, REJECT, REGENERATE controls subject to permissions. | A changed row, evidence span, or source version refreshes all three regions. A failed or ambiguous PDF anchor remains visible as a warning; it is not silently dropped. |

The Atomic queue should not silently default to “verified only” in a review workflow. The verified-only default applies to the library/search surface when approved by the requirements contract. Candidate status names and transitions remain conditional on the approved lifecycle.

## Evidence display and source distinction

Render the extracted source excerpt in a neutral “Source text” block, preserving original wording and line breaks where feasible. Render an AI proposal in a separate “AI-proposed” block with a persistent label, distinct border/background and its candidate/run identifier. Avoid color as the only distinction and never rewrite the source quote to resemble the proposal. Show context spans separately from the primary evidence span and retain an origin badge when the applicable policy is approved.

Use warnings with scope and provenance, for example: “Numeric value differs from source,” “Qualifier or negation may be missing,” “Comparison direction differs,” “Evidence is partial,” or “PDF highlight could not be anchored.” These findings are precheck/reviewer aids, not a hidden pass/fail policy until the relevant thresholds are approved. Deterministic comparisons can flag mismatches; model commentary remains advisory.

## Review controls and safeguards

- **VERIFY** is enabled only when the item is reviewable, its source version is current, required evidence is resolvable, and a trusted authenticated reviewer identity is available. It records a human event through the server; no AI response can set VERIFIED.
- **REJECT** records the authorized review event and reason under the approved lifecycle. Preserve the rejected record.
- **REGENERATE** creates a new linked candidate/AS version; it does not overwrite the rejected text, evidence, or history.
- Disable review controls with a clear explanation when identity, source freshness, required evidence, or required contract configuration is missing.
- No name typed into the browser can substitute for a trusted server identity. The existing `local-user` fallback must not be used for Atomic verification.
- Quality review follows PRD FR-10 only when the SPS dimensions/rules are provided and AS-OD-09 has the required approvals. The screen must not invent score fields or weights.

The lifecycle and labels above are a proposed mapping to the PRD/QA specifications, not an approval of any OPEN AS-OD decision.

## Responsive and accessible behavior

On narrow screens, preserve the current page's stacked layout. Present Navigation, Queue, and Evidence as labeled collapsible/stacked regions with the selected item and source location retained as the user moves between them. The PDF remains the existing viewer. Ensure the panel can be reached without horizontal page overflow and provide a clear “Return to sentence” path after navigating the excerpt/view.

Use the existing tab roles and keyboard handling; give each new tab/panel unique IDs, accessible names, focus-visible styles, and live status announcements for loading, stale-source, and anchor failures. Queue filters must have labels; status and evidence states need text labels in addition to color. Respect PDF zoom, splitter interactions, reduced motion, and current modal behavior.

## Frontend component proposal

```text
Analysis page (existing template and route)
└── AtomicSentencesTab
    ├── AtomicPaperNavigation
    │   ├── AtomicSectionTree
    │   └── AtomicFilters
    ├── AtomicSentenceQueue
    │   └── AtomicSentenceRow
    └── AtomicEvidenceBridge (inside existing #pdfPane boundary)
        ├── Existing PDF.js viewer and toolbar (reused)
        ├── AtomicEvidenceInspector
        ├── AtomicPrecheckWarnings
        └── AtomicReviewActions
```

The `AtomicEvidenceBridge` receives only a paper/source identity, verified quote, available page hint, and selected Atomic evidence ID; it calls existing viewer functions through a narrow adapter. The source inspector for Toulmin/AIF propositions remains separate.

## Proposed visual status vocabulary

Show server-returned state explicitly. The final labels and transitions require an approved lifecycle contract. Until then, design mocks may use neutral labels such as “Candidate,” “Needs review,” “Verified by reviewer,” “Rejected,” “Stale source,” and “Needs context,” clearly marked as proposal data. Do not display AI precheck “supported” as verification.

## UI integration acceptance outline for a later implementation ticket

1. The tab is visible on the existing paper detail route and absent from list mode unless approved otherwise.
2. Selecting the tab preserves the paper key, `from` navigation, current detail route, and current viewer instance.
3. Section selection, filters, queue selection, excerpt, context, and PDF highlight remain synchronized to a versioned evidence record.
4. Source text and AI-proposed text are visibly and accessibly distinct.
5. Anchor failure, partial source, stale source, and unavailable reviewer identity are explicit states.
6. VERIFY cannot be called as an AI/system action and cannot publish without trusted reviewer identity and required evidence.
7. Existing Analysis, Toulmin/AIF, proposition inspector, PDF zoom/highlighting, and mobile behavior retain their current semantics.

No UI component or application behavior was changed in this document task.
