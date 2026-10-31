# Outline Analysis Audit and Output Contract

## Root cause found in the current SPA-AFRL run

The latest saved run for `10.2139/ssrn.7192454` contains 58 outline rows, 9 thematic groups, and 48 group-member references. Before the fix, only 1 of those 48 references resolved to an outline row; the other 47 were stale. `PaperStore.save_argumentation()` run-scoped scalar `section_id` values but did not remap IDs inside the `section_ids` arrays. The Outline UI then looked up those stale IDs and reported the number of rows it could resolve as “original section headings.” That number was neither the number of original headings nor the number of content sections.

The parser already read nested GROBID TEI `<div>`/`<head>` structure and retained heading-only nodes, but it did not preserve paragraph-level IDs. The AI result mixed GROBID-derived structure and inferred summaries in `paper_profile.outline`; grouping was over those rows, including heading-only structure nodes. The frontend rendered the structural rows beneath inferred groups, obscuring the difference between source structure and AI interpretation.

No corresponding Outline Analysis implementation was found in the sibling `slr-system` repository during this audit.

## Output contract

`paper_profile.outline` remains as a backward-compatible flat representation. New runs also emit `paper_profile.outline_layers` with three independent views:

```json
{
  "structural": {
    "source_of_truth": "grobid_tei",
    "hierarchy_status": "verified",
    "nodes": [{
      "structure_id": "structure-0002",
      "section_id": "run-id:sec_0002",
      "parent_structure_id": "structure-0001",
      "original_heading": "1.1 Research gap",
      "heading_number": "1.1",
      "heading_level": 2,
      "source_order": 2,
      "paragraph_ids": ["run-id:p_0002_001"],
      "paragraphs": [{"id": "run-id:p_0002_001", "text": "...", "start_offset": 120, "end_offset": 160, "page": 2}],
      "origin": "grobid_tei",
      "hierarchy_status": "verified",
      "content_status": "has_content",
      "source_location": {"start_offset": 120, "end_offset": 160}
    }]
  },
  "semantic": {
    "groups": [{"group_id": "outline-group-01", "title": "...", "title_origin": "inferred",
      "source_section_ids": ["run-id:sec_0002"], "idea_ids": ["idea:run-id:sec_0002:main"],
      "membership_status": "membership_verified", "verification_status": "needs_review"}],
    "ideas": [{"idea_id": "idea:run-id:sec_0002:main", "idea_type": "main", "title": "...",
      "description": "...", "parent_idea_id": null, "source_section_ids": ["run-id:sec_0002"],
      "source_paragraph_ids": ["run-id:p_0002_001"], "evidence_spans": [{"quote": "...", "start_offset": 120, "end_offset": 140}],
      "verification_status": "needs_review"}],
    "section_statuses": [{"section_id": "run-id:sec_0002", "status": "inferred_pending_review"}]
  },
  "rhetorical": {
    "moves": [{"move_id": "move:run-id:sec_0002", "role": "research_gap",
      "source_section_ids": ["run-id:sec_0002"], "source_paragraph_ids": ["run-id:p_0002_001"],
      "evidence": [{"quote": "...", "start_offset": 120, "end_offset": 140}],
      "classification_status": "inferred", "verification_status": "needs_review"}],
    "section_statuses": [{"section_id": "run-id:sec_0002", "status": "insufficient_evidence"}]
  }
}
```

IDs and text spans are deterministic source mappings. Quote validation permits whitespace normalization while preserving the matched span in the source text. AI idea titles, summaries, group labels, and rhetorical roles remain explicitly inferred and pending researcher review. A semantic or rhetorical item without a validated quote linked to the same source section is omitted. Sections with insufficient evidence are represented in `section_statuses`; no rhetorical role is forced. Group membership is checked against the exact eligible source section sequence. Failed AI chunks are reported with chunk, section, and paragraph IDs, and coverage reports paragraphs that were not fully processed.

## Before / after on the saved SPA-AFRL analysis

| Measure | Before | After compatibility adapter |
|---|---:|---:|
| Structural rows | 58 | 58 |
| Content-bearing source sections | not separately counted | 51 |
| Heading-only structure nodes | mixed into group counts | 7 |
| Thematic groups | 9 | 9 |
| Group member references resolving to source rows | 1 / 48 | 48 / 48 |
| Semantic ideas exposed from stored, quote-validated output | not separated | 68 |
| Rhetorical moves exposed from stored, quote-validated output | not separated | 30 |

The before state was read from the saved SQLite payload without mutation. The after state is produced at read time by the legacy adapter; it repairs run-scoped group references and separates the already saved evidence into the new UI layers. It does not call the AI again. That old run predates paragraph IDs, so the UI exposes its saved section text and offsets and labels paragraph mapping as unavailable instead of inventing paragraph IDs. Reanalysis creates paragraph-level mappings and coverage data.

## Normalized outline for readers

The Semantic view now offers a compact conventional scaffold: Title, Abstract, explicitly reported Keywords, and only the evidence-backed major sections found in the paper. It can include Introduction, Literature Review, Methods, Results, Discussion, Conclusion, References, and appendices when the source supports them. Missing sections stay omitted; the view does not manufacture headings or placeholder content. AI group labels and ideas remain nested beneath the normalized section and are marked as inferred, with their source sections and evidence available for review.

For the saved SPA-AFRL run above, the normalized view contains Title, Abstract, Introduction, Methods, Results, Conclusion, and Appendices. It has no explicit keyword list in GROBID metadata, so the 264 text-mined terms are not shown as paper Keywords. No separate Discussion or References heading was identified in the saved outline. The saved legacy structure has 58 flat rows with no parent links, including 20 recognizable page/footer artifacts and 20 unverified heading candidates; the adapter filters these artifacts from the article tree but cannot recover hierarchy that the saved run did not retain. The Semantic view has 9 groups, 69 quote-validated ideas, and 30 rhetorical moves; group membership resolves to the saved source rows. This saved run is displayed through a read-time adapter and is not re-analyzed by the model.

The normalized JSON adds `semantic.normalized_outline`:

```json
{
  "title": {"text": "Paper title", "origin": "grobid_metadata"},
  "abstract": {"subsections": [], "source_section_ids": ["run-id:sec_0001"]},
  "keywords": [{"term": "explicit author keyword", "source_type": "author_reported"}],
  "sections": [{
    "section_id": "methods",
    "title": "Methods",
    "title_origin": "normalized",
    "subsections": [{
      "group_id": "outline-group-01",
      "title": "System design",
      "title_origin": "inferred",
      "original_headings": ["3. System Modeling"],
      "source_section_ids": ["run-id:sec_0003"],
      "ideas": [],
      "verification_status": "needs_review"
    }],
    "source_section_ids": ["run-id:sec_0003"],
    "verification_status": "needs_review"
  }],
  "references": {"subsections": [], "source_section_ids": [], "original_headings": []},
  "missing_conventional_sections": ["Discussion"]
}
```

Only keywords with `author_reported` or `grobid_reported` provenance appear in this scaffold. Phrase candidates mined from article text remain in the separate keyword analysis and are not mislabeled as author keywords.

## Compatibility and verification

- No SQL table or Cloudinary schema change is required. New fields are added within the versioned JSON `paper_profile`; the old `outline` and `outline_groups` fields remain available.
- New saves remap scalar and array section references and paragraph references into run-scoped IDs. Existing saves are repaired on read without rewriting historical rows.
- Stable extraction IDs use section/structure/paragraph order within a document; persisted section and paragraph IDs are additionally scoped to an analysis run.
- Automated coverage is in `tests/test_outline_analysis.py` and is run with `python -m unittest discover -s tests -v`.
