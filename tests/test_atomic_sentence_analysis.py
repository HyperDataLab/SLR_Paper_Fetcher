import unittest

from unittest.mock import patch

from atomic_sentence import (_annotate_fulltext_hyland, _hyland_scope_passages, _hyland_sentence_records,
    _document_passages, _markdown_passages, _marker_positions, _sentence_spans, _source_preservation_warnings,
    _statistics, _word_count, analyze_atomic_sentences)


class AtomicSentenceTextTests(unittest.TestCase):
    def test_markdown_paragraph_parser_keeps_full_wrapped_lines_and_offsets(self):
        markdown = (
            "# Abstract\r\n\r\n"
            "The device may improve recall,\r\n"
            "but the effect was not significant.\r\n\r\n"
            "# Results\r\n\r\n"
            "We observed a 12% increase.\r\n"
        )

        passages = _markdown_passages(markdown)

        self.assertEqual(len(passages), 2)
        self.assertEqual(passages[0]["text"], "The device may improve recall,\r\nbut the effect was not significant.")
        self.assertEqual(passages[0]["section"], "Abstract")
        self.assertEqual(markdown[passages[0]["start_offset"]:passages[0]["end_offset"]], passages[0]["text"])
        self.assertEqual(passages[1]["text"], "We observed a 12% increase.")
        self.assertEqual(passages[1]["section"], "Results")

    def test_statistics_use_whitespace_words_and_group_percentages(self):
        annotations = [
            {"category": "Hedges"}, {"category": "Hedges"}, {"category": "Self Mention"},
            {"category": "Questions"}, {"category": "Boosters"}, {"category": "Asides"},
        ]

        stats = _statistics(annotations, _word_count("The model may not improve outcomes."))

        self.assertEqual(stats["source_word_count"], 6)
        self.assertEqual(stats["stance"][-1]["count"], 4)
        self.assertEqual(stats["stance"][-1]["percentage"], 100.0)
        self.assertEqual(stats["stance"][0]["count"], 2)
        self.assertEqual(stats["stance"][0]["per_1000_words"], 333.33)
        self.assertEqual(stats["engagement"][-1]["count"], 2)
        self.assertEqual(stats["engagement"][-1]["percentage"], 100.0)

    def test_hyland_scope_includes_abstract_and_body_but_excludes_references_and_captions(self):
        markdown = ("# Abstract\n\nThe model may improve results.\n\n"
                    "# Results\n\nWe observed an effect.\n\n"
                    "Figure 1. A diagram of the system.\n"
                    "| Group | Value |\n|---|---|\n| A | 2 |\n\n"
                    "# 4 References\n\nSmith et al. may have reported a result.\n")
        passages, excluded = _hyland_scope_passages(_markdown_passages(markdown, keep_non_content=True))
        self.assertEqual([item["section"] for item in passages], ["Abstract", "Results"])
        self.assertEqual(sum(_word_count(item["text"]) for item in passages), 9)
        self.assertGreaterEqual(excluded["caption_or_table"], 4)
        self.assertEqual(excluded["non_content_section"], 1)
        self.assertTrue(all(markdown[item["start_offset"]:item["end_offset"]] == item["text"] for item in passages))

    def test_hyland_scope_excludes_metadata_and_acknowledgements_but_counts_abstract(self):
        markdown = ("# Article title\n\nAuthors: A. Researcher; B. Scholar\n\n"
                    "# Abstract\n\nThe intervention may reduce admissions.\n\n"
                    "# Acknowledgements\n\nWe thank the team.\n\n"
                    "# Funding\n\nThis study received support.\n")
        raw_passages = _markdown_passages(markdown, keep_non_content=True)
        passages, excluded = _hyland_scope_passages(raw_passages)
        self.assertEqual([item["section"] for item in passages], ["Abstract"])
        self.assertEqual(sum(_word_count(item["text"]) for item in passages), 5)
        self.assertEqual(excluded["document_metadata"], 1)
        self.assertGreaterEqual(excluded["non_content_section"], 2)

    def test_legacy_front_matter_mapping_excludes_authors_and_index_terms_but_keeps_abstract(self):
        paragraphs = [
            "Hui Cheng, Qiao Xue, Youwen Zhu College of Computer Science and Technology, Nanjing University.",
            "Federated learning may improve privacy for edge devices by keeping raw data local.",
            "Index Terms-Asynchronous federated learning, Internet of Things, differential privacy.",
        ]
        source = "\n\n".join(paragraphs + ["Introduction text begins here."])
        section_start = 0
        section_paragraphs = []
        for index, paragraph in enumerate(paragraphs):
            start = source.find(paragraph, section_start)
            section_paragraphs.append({"id": f"p{index}", "text": paragraph,
                "start_offset": start, "end_offset": start + len(paragraph)})
            section_start = start + len(paragraph)
        intro = "Introduction text begins here."
        intro_start = source.find(intro)
        document = {"text": source, "sections": [
            {"id": "title", "heading": "Heterogeneous IoT Devices", "section_type": "other",
             "structural_kind": "body", "paragraphs": section_paragraphs},
            {"id": "intro", "heading": "I. Introduction", "section_type": "introduction",
             "structural_kind": "body", "paragraphs": [{"id": "intro-p", "text": intro,
                 "start_offset": intro_start, "end_offset": intro_start + len(intro)}]},
        ]}

        included, excluded = _hyland_scope_passages(_document_passages(document, keep_non_content=True))

        self.assertEqual([item["section"] for item in included], ["Abstract", "I. Introduction"])
        self.assertEqual([item["text"] for item in included], [paragraphs[1], intro])
        self.assertEqual(sum(_word_count(item["text"]) for item in included), 17)
        self.assertEqual(excluded["non_body_structure"], 1)

    def test_mapped_inline_headings_tables_and_algorithm_blocks_are_not_prose(self):
        paragraphs = [
            "We may see improvements.",
            "The results may vary. TABLE I: Experimental Environment Configuration Windows 10 Python 3.12.3 "
            "f) Sensitivity Analysis.: We could estimate the effect.",
            "for h = 0 to H - 1 do ← update values end for for k = 1 to n do ← send updates end for",
            "Gradient Clipping:",
        ]
        source = "\n\n".join(paragraphs)
        items = []
        cursor = 0
        for index, paragraph in enumerate(paragraphs):
            start = source.find(paragraph, cursor)
            items.append({"id": f"p{index}", "text": paragraph,
                "start_offset": start, "end_offset": start + len(paragraph)})
            cursor = start + len(paragraph)
        document = {"text": source, "sections": [{"id": "results", "heading": "Results",
            "section_type": "results", "structural_kind": "body", "paragraphs": items}]}

        included, excluded = _hyland_scope_passages(_document_passages(document, keep_non_content=True))

        self.assertEqual([item["text"] for item in included],
            [paragraphs[0], "The results may vary.", "We could estimate the effect."])
        self.assertEqual(sum(_word_count(item["text"]) for item in included), 13)
        self.assertEqual(excluded["caption_or_table"], 2)
        self.assertEqual(excluded["heading_or_label"], 1)
        self.assertEqual(excluded["algorithmic_block"], 1)
        self.assertTrue(all(source[item["start_offset"]:item["end_offset"]] == item["text"] for item in included))

    def test_sentence_spans_keep_abbreviations_and_source_offsets(self):
        text = "For example, e.g. this may help. It could improve results."
        spans = _sentence_spans(text)
        self.assertEqual([item["text"] for item in spans], ["For example, e.g. this may help.", "It could improve results."])
        for item in spans:
            self.assertEqual(text[item["start"]:item["end"]], item["text"])

    def test_marker_occurrence_uses_exact_text_and_lexical_boundaries(self):
        sentence = "We may improve; maybe we may not."
        positions = _marker_positions(sentence, "may")
        self.assertEqual([sentence[start:end] for start, end in positions], ["may", "may"])
        self.assertEqual([sentence[start:end] for start, end in _marker_positions(sentence, "We")], ["We"])
        self.assertEqual([sentence[start:end] for start, end in _marker_positions(sentence, "we")], ["we"])
        self.assertEqual(_marker_positions(sentence, "may be"), [])

    def test_fulltext_hyland_annotation_spans_are_source_validated(self):
        source = "# Results\n\nWe may improve, and we may report results.\n"
        passages = _hyland_scope_passages(_markdown_passages(source))[0]
        records, missing = _hyland_sentence_records(passages, source)
        self.assertEqual(missing, 0)
        sentence_id = records[0]["sentence_id"]
        response = {"annotations": [{"sentence_id": sentence_id, "annotations": [
            {"category": "Hedges", "marker": "may", "marker_occurrence": 1, "function": "Marks the claim as possible."},
            {"category": "Hedges", "marker": "may", "marker_occurrence": 2, "function": "Qualifies the reporting claim."},
            {"category": "Boosters", "marker": "may", "marker_occurrence": 3, "function": "Invalid occurrence should be dropped."},
        ]}]}
        with patch("atomic_sentence._provider_json", return_value=(response, "mock-model")):
            annotations, models, diagnostics, _ = _annotate_fulltext_hyland(passages, source, "ollama")
        self.assertEqual(models, ["mock-model"])
        self.assertEqual(len(annotations), 2)
        self.assertEqual(diagnostics["invalid_model_annotations_dropped"], 1)
        self.assertEqual([source[item["start_offset"]:item["end_offset"]] for item in annotations], ["may", "may"])
        self.assertEqual([item["marker_occurrence"] for item in annotations], [1, 2])

    def test_fulltext_hyland_repairs_category_only_function_notes(self):
        source = "# Results\n\nThe method may improve outcomes.\n"
        passages = _hyland_scope_passages(_markdown_passages(source))[0]
        records, _ = _hyland_sentence_records(passages, source)
        sentence_id = records[0]["sentence_id"]
        first_response = {"annotations": [{"sentence_id": sentence_id, "annotations": [
            {"category": "Hedges", "marker": "may", "marker_occurrence": 1, "function": "Hedges"}]}]}
        rationale_response = {"annotations": [{"sentence_id": sentence_id, "annotations": [
            {"category": "Hedges", "marker": "may", "marker_occurrence": 1,
             "function": "Limits the author's commitment to the predicted effect."}]}]}
        with patch("atomic_sentence._provider_json", side_effect=[
                (first_response, "mock-model"), (rationale_response, "mock-model")]) as provider_call:
            annotations, models, diagnostics, _ = _annotate_fulltext_hyland(passages, source, "ollama")
        self.assertEqual(len(annotations), 1)
        self.assertIn("commitment", annotations[0]["function"])
        self.assertEqual(diagnostics["hyland_rationales_repaired"], 1)
        self.assertEqual(diagnostics["hyland_rationales_unresolved"], 0)
        self.assertEqual(provider_call.call_count, 2)
        self.assertEqual(len(models), 2)

    def test_fulltext_hyland_drops_annotation_if_rationale_cannot_be_repaired(self):
        source = "# Results\n\nThe method may improve outcomes.\n"
        passages = _hyland_scope_passages(_markdown_passages(source))[0]
        sentence_id = _hyland_sentence_records(passages, source)[0][0]["sentence_id"]
        short_response = {"annotations": [{"sentence_id": sentence_id, "annotations": [
            {"category": "Hedges", "marker": "may", "marker_occurrence": 1, "function": "Hedges"}]}]}
        with patch("atomic_sentence._provider_json", side_effect=[
                (short_response, "mock-model"), (short_response, "mock-model")]):
            annotations, _, diagnostics, _ = _annotate_fulltext_hyland(passages, source, "ollama")
        self.assertEqual(annotations, [])
        self.assertEqual(diagnostics["hyland_rationales_unresolved"], 1)
        self.assertEqual(diagnostics["invalid_model_annotations_dropped"], 1)

    def test_pipeline_hyland_stats_scan_fulltext_even_without_atomic_candidates(self):
        source = "# Abstract\n\nThe model may improve results. We may observe an effect.\n"
        extraction = ({"candidates": []}, "mock-extractor")
        hyland = ({"annotations": [
            {"sentence_id": "HY-S000001", "annotations": [
                {"category": "Hedges", "marker": "may", "marker_occurrence": 1, "function": "Qualifies the research claim."}]},
            {"sentence_id": "HY-S000002", "annotations": [
                {"category": "Hedges", "marker": "may", "marker_occurrence": 1, "function": "Qualifies the observed effect."}]},
        ]}, "mock-hyland")
        with patch("atomic_sentence._provider_json", side_effect=[extraction, hyland]):
            result = analyze_atomic_sentences({"text": source,
                "metadata": {"source_kind": "markdown"}, "sections": []}, "paper-1", "ollama")
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["statistics"]["source_word_count"], 10)
        self.assertEqual(result["statistics"]["stance"][0]["count"], 2)
        self.assertEqual(result["statistics"]["stance"][0]["per_1000_words"], 200.0)
        self.assertEqual(len(result["hyland_annotations"]), 2)
        self.assertEqual(len(result["hyland_sentence_inventory"]), 2)
        for annotation in result["hyland_annotations"]:
            self.assertEqual(source[annotation["start_offset"]:annotation["end_offset"]], annotation["marker"])
        self.assertEqual(result["analysis"]["hyland_scope_version"], "hyland_prose_scope.2")

    def test_source_preservation_guard_flags_added_numbers_and_math_symbols(self):
        candidate = {
            "atomic_sentence": "MNIST contains 60,000 training images of digits 0-9 (10 classes).",
            "evidence": [{"quote": "MNIST contains 60,000 training and 10,000 testing images."}],
        }

        warnings = _source_preservation_warnings(candidate)

        self.assertTrue(any("number" in warning for warning in warnings))

        formula = {
            "atomic_sentence": "Noise has variance σ² where σ ≥ Δf·√(2 ln(1.25/δ))/ε.",
            "evidence": [{"quote": "Noise has variance σ 2 where σ ≥ ∆f • 2 ln(1.25/δ) ϵ."}],
        }
        warnings = _source_preservation_warnings(formula)
        self.assertTrue(any("mathematical symbol" in warning for warning in warnings))

    def test_source_preservation_guard_splits_comma_separated_number_sets(self):
        candidate = {
            "atomic_sentence": "S includes {1, 0.75, 0.5, 0.25} and p ranges over {1, 2, 3, 4}.",
            "evidence": [{"quote": "S = {1, 0.75, 0.5, 0.25} and p ∈ {1, 2, 3, 4}."}],
        }

        self.assertEqual(_source_preservation_warnings(candidate), [])


if __name__ == "__main__":
    unittest.main()
