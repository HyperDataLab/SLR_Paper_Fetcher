import unittest
import json
import hashlib
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from ai_analysis import (
    FULLTEXT_MAPPING_SCHEMA_VERSION,
    _pdf_artifact_identity,
    _extract_tei_document,
    _fallback_outline_groups,
    _group_outline_sections,
    _load_and_validate_fulltext_mapping,
    _has_reported_profile_keywords,
    _outline_evidence_records,
    _preferred_profile_keywords,
    _quote_span,
    _retrieve_profile_evidence,
    _section_chunks,
    _verify_text_chunk_coverage,
    _write_fulltext_mapping,
    build_outline_layers,
)
from automatic_sources import fetch_openalex_classification
from paper_store import PaperStore, remap_outline_source_ids, repair_legacy_outline_group_references


def _attach_valid_ollama_sidecar(metadata, pdf_path):
    markdown_path = pdf_path.with_suffix(".ollama.md")
    markdown_path.write_text("# Extracted PDF source\n", encoding="utf-8")
    metadata["extraction_artifacts"] = {
        "engine": "ollama_vision_api",
        "markdown_file": markdown_path.name,
        "markdown_sha256": hashlib.sha256(markdown_path.read_bytes()).hexdigest(),
    }


class OutlineParserTests(unittest.TestCase):
    def test_quote_offsets_use_whitespace_normalized_source_span(self):
        source = "First sentence.\n\nSecond sentence."
        quote = "First sentence. Second sentence."
        start, end = _quote_span(source, quote)
        self.assertEqual(source[start:end], "First sentence.\n\nSecond sentence.")

    def test_grobid_hierarchy_heading_only_paragraph_ids_and_numbering(self):
        tei = b'''<TEI><teiHeader><fileDesc><titleStmt><title>Sample</title></titleStmt>
          <sourceDesc><biblStruct/></sourceDesc></fileDesc></teiHeader><text><body>
          <div><head>1 Introduction</head><p>Context paragraph.</p>
            <div><head>1.1 Research gap</head><p>A gap is stated.</p></div>
            <div><head>1.2 Contribution</head></div>
          </div><div><p>1. A numbered list item, not a heading.</p></div>
          </body></text></TEI>'''
        document, _ = _extract_tei_document(tei)
        nodes = document["structure"]
        self.assertEqual([node["heading"] for node in nodes], ["1 Introduction", "1.1 Research gap", "1.2 Contribution", ""])
        self.assertEqual(nodes[1]["parent_structure_id"], nodes[0]["id"])
        self.assertEqual(nodes[2]["parent_structure_id"], nodes[0]["id"])
        self.assertEqual(nodes[0]["heading_number"], "1")
        self.assertEqual(nodes[1]["heading_number"], "1.1")
        self.assertIsNone(nodes[2]["section_id"])
        self.assertTrue(all(p["id"].startswith("p_") for section in document["sections"] for p in section["paragraphs"]))
        self.assertEqual(document["sections"][-1]["heading"], "")
        self.assertIn("1. A numbered list item", document["sections"][-1]["text"])

    def test_tei_paragraph_offsets_survive_fulltext_mapping_roundtrip(self):
        first = "A source paragraph with enough scientific detail. " * 15
        second = "A second paragraph preserves its own source identity. " * 12
        tei = ("<TEI><teiHeader><fileDesc><titleStmt><title>Sample</title></titleStmt>"
               "<sourceDesc><biblStruct/></sourceDesc></fileDesc></teiHeader><text><body><div>"
               "<head>2 Results</head><p>" + first + "</p><p>" + second + "</p>"
               "</div></body></text></TEI>").encode()
        document, _ = _extract_tei_document(tei)
        self.assertEqual(len(document["sections"][0]["paragraphs"]), 2)
        with tempfile.TemporaryDirectory() as directory:
            pdf_path = Path(directory) / "paper.pdf"
            pdf_path.write_bytes(b"%PDF test artifact")
            _attach_valid_ollama_sidecar(document["metadata"], pdf_path)
            mapping_path = _write_fulltext_mapping(pdf_path, document, _pdf_artifact_identity(pdf_path))
            loaded = _load_and_validate_fulltext_mapping(mapping_path)
        paragraphs = loaded["sections"][0]["paragraphs"]
        self.assertEqual([item["text"] for item in paragraphs], [first.strip(), second.strip()])
        self.assertTrue(all(loaded["text"][item["start_offset"]:item["end_offset"]] == item["text"] for item in paragraphs))

    def test_openalex_keyword_list_is_preserved_even_when_work_has_no_topics(self):
        response = MagicMock()
        response.__enter__.return_value.status_code = 200
        response.__enter__.return_value.json.return_value = {
            "id": "https://openalex.org/W123",
            "doi": "https://doi.org/10.1234/example",
            "keywords": [
                {"id": "https://openalex.org/keywords/federated-learning", "display_name": "Federated learning", "score": 0.91},
                {"id": "https://openalex.org/keywords/edge-computing", "display_name": "Edge computing", "score": 0.83},
            ],
            "topics": [],
        }
        with patch("automatic_sources.polite_get", return_value=response):
            result = fetch_openalex_classification("10.1234/example")
        self.assertEqual(result["status"], "NOT_FOUND")
        self.assertEqual([item["display_name"] for item in result["keywords"]], ["Federated learning", "Edge computing"])
        self.assertEqual(result["keywords"][0]["score"], 0.91)


class OutlineLayersTests(unittest.TestCase):
    def test_openalex_keywords_take_precedence_over_article_and_ai_keywords(self):
        openalex = [{"term": "federated learning", "source_type": "openalex_reported"}]
        author = [{"term": "distributed learning", "source_type": "author_reported"}]
        ai = [{"term": "edge systems", "source_type": "text_extracted"}]
        self.assertEqual(_preferred_profile_keywords(openalex, author, [], ai), openalex)
        self.assertTrue(_has_reported_profile_keywords([{"display_name": "federated learning"}], author, []))

    def test_reported_article_keywords_precede_ai_keyword_fallback(self):
        author = [{"term": "distributed learning", "source_type": "author_reported"}]
        grobid = [{"term": "wireless networks", "source_type": "grobid_reported"}]
        ai = [{"term": "edge systems", "source_type": "text_extracted"}]
        self.assertEqual(_preferred_profile_keywords([], author, grobid, ai), author + grobid)

    def test_ai_keywords_are_used_only_when_no_reported_source_has_any(self):
        ai = [{"term": "edge systems", "source_type": "text_extracted"}]
        self.assertEqual(_preferred_profile_keywords([], [], [], ai), ai)
        self.assertFalse(_has_reported_profile_keywords([], [], []))

    def test_grouping_counts_only_content_sections_and_preserves_heading_only_nodes(self):
        outline = [
            {"section_id": "sec_1", "structure_id": "str_1", "order": 1, "heading": "Intro", "analysis_status": "analyzed"},
            {"section_id": None, "structure_id": "str_2", "order": 2, "heading": "1.1 Subsection", "analysis_status": "structural_only"},
            {"section_id": "sec_2", "structure_id": "str_3", "order": 3, "heading": "Method", "analysis_status": "analyzed"},
        ]
        groups, status, _ = _group_outline_sections(outline, "ollama")
        self.assertEqual(status, "not_needed")
        self.assertEqual([group["source_section_ids"] for group in groups], [["sec_1"], ["sec_2"]])

    def test_invalid_model_group_ids_fall_back_to_verified_source_sequence(self):
        outline = [{"section_id": f"sec_{i}", "structure_id": f"str_{i}", "order": i,
                    "heading": f"Section {i}", "analysis_status": "analyzed"} for i in range(1, 11)]
        with patch("ai_analysis._provider_json", return_value=({"groups": [{"label": "All", "section_ids": ["ghost"]}]}, "mock")):
            groups, status, _ = _group_outline_sections(outline, "ollama")
        self.assertEqual(status, "fallback_needs_review")
        flattened = [section_id for group in groups for section_id in group["source_section_ids"]]
        self.assertEqual(flattened, [item["section_id"] for item in outline])

    def test_duplicate_group_references_fall_back_without_losing_source_sections(self):
        outline = [{"section_id": f"sec_{i}", "structure_id": f"str_{i}", "order": i,
                    "heading": f"Section {i}", "analysis_status": "analyzed"} for i in range(1, 11)]
        with patch("ai_analysis._provider_json", return_value=({"groups": [{"label": "Repeated", "section_ids": ["sec_1", "sec_1"]}]}, "mock")):
            groups, status, _ = _group_outline_sections(outline, "ollama")
        self.assertEqual(status, "fallback_needs_review")
        self.assertEqual([sid for group in groups for sid in group["source_section_ids"]], [item["section_id"] for item in outline])

    def test_semantic_and_rhetorical_items_keep_evidence_and_remain_pending(self):
        outline = [{"section_id": "run:sec_0001", "structure_id": "structure-1", "order": 1,
            "heading": "Introduction", "heading_source": "grobid_tei", "hierarchy_status": "verified",
            "paragraphs": [{"id": "run:p_1", "text": "Evidence", "start_offset": 0, "end_offset": 8}],
            "purpose": "Frames the problem.",
            "purpose_source": {"section_id": "run:sec_0001", "paragraph_ids": ["run:p_1"], "quote": "Evidence", "start_offset": 0, "end_offset": 8},
            "role": "problem_statement", "role_source": {"section_id": "run:sec_0001", "paragraph_ids": ["run:p_1"], "quote": "Evidence"},
            "key_points": [{"text": "The study identifies a gap.", "source": {"section_id": "run:sec_0001", "paragraph_ids": ["run:p_1"], "quote": "Evidence"}}]}]
        layers = build_outline_layers(outline)
        self.assertEqual(layers["structural"]["nodes"][0]["original_heading"], "Introduction")
        self.assertEqual(layers["semantic"]["ideas"][0]["verification_status"], "needs_review")
        self.assertEqual(layers["semantic"]["ideas"][1]["parent_idea_id"], layers["semantic"]["ideas"][0]["idea_id"])
        self.assertEqual(layers["rhetorical"]["moves"][0]["verification_status"], "needs_review")

    def test_unverified_heading_candidate_is_not_called_an_original_heading(self):
        outline = [{"section_id": "sec_page", "structure_id": "str_page", "order": 8,
            "heading": "Page 8 of 20", "heading_source": "unknown", "structural_kind": "body",
            "analysis_status": "insufficient_evidence"}]
        node = build_outline_layers(outline)["structural"]["nodes"][0]
        self.assertIsNone(node["original_heading"])
        self.assertEqual(node["unverified_heading_candidate"], "Page 8 of 20")

    def test_semantic_idea_without_mapped_quote_is_not_exposed(self):
        outline = [{"section_id": "sec_1", "structure_id": "str_1", "heading": "Results",
            "purpose": "Unsupported purpose", "purpose_source": None,
            "key_points": [{"text": "Unsupported idea", "source": {"section_id": "missing", "quote": "not here"}}]}]
        layers = build_outline_layers(outline)
        self.assertEqual(layers["semantic"]["ideas"], [])

    def test_semantic_idea_is_not_blocked_by_missing_rhetorical_move(self):
        outline = [{"section_id": "sec_1", "structure_id": "str_1", "heading": "Introduction",
            "purpose": "Frames the question.", "purpose_source": {"section_id": "sec_1", "quote": "The question"},
            "role": "unknown", "role_source": None, "key_points": []}]
        layers = build_outline_layers(outline)
        self.assertEqual(len(layers["semantic"]["ideas"]), 1)
        self.assertEqual(layers["rhetorical"]["moves"], [])
        self.assertEqual(layers["rhetorical"]["section_statuses"][0]["status"], "insufficient_evidence")

    def test_page_artifacts_remain_structural_and_are_excluded_from_ai_layers(self):
        outline = [{"section_id": "sec_page", "structure_id": "str_page", "order": 4,
            "heading": "Page 8 of 20", "source_content": "Page 8 of 20", "structural_kind": "page_artifact",
            "purpose": "A made-up summary.", "purpose_source": {"section_id": "sec_page", "quote": "Page 8 of 20"},
            "role": "finding", "role_source": {"section_id": "sec_page", "quote": "Page 8 of 20"}, "key_points": []}]
        layers = build_outline_layers(outline, [{"id": "group-1", "section_ids": ["sec_page"]}])
        self.assertEqual(len(layers["structural"]["nodes"]), 1)
        self.assertIsNone(layers["structural"]["nodes"][0]["original_heading"])
        self.assertEqual(layers["structural"]["nodes"][0]["unverified_heading_candidate"], "Page 8 of 20")
        self.assertEqual(layers["semantic"]["ideas"], [])
        self.assertEqual(layers["semantic"]["groups"][0]["source_section_ids"], [])
        self.assertEqual(layers["rhetorical"]["moves"], [])

    def test_legacy_page_number_heading_is_reclassified_as_artifact(self):
        layers = build_outline_layers([{
            "section_id": "sec_page", "structure_id": "str_page", "order": 1,
            "heading": "Page 15 of 20", "heading_source": "unknown",
            "analysis_status": "analyzed",
        }])
        node = layers["structural"]["nodes"][0]
        self.assertEqual(node["structural_kind"], "page_artifact")
        self.assertIsNone(node["original_heading"])
        self.assertEqual(node["unverified_heading_candidate"], "Page 15 of 20")
        self.assertEqual(layers["semantic"]["ideas"], [])

    def test_normalized_outline_uses_only_present_sections_and_keeps_group_evidence_links(self):
        outline = [
            {"section_id": "sec_abs", "structure_id": "str_abs", "order": 1, "heading": "Abstract",
             "section_type": "abstract", "heading_source": "grobid_tei", "analysis_status": "analyzed"},
            {"section_id": "sec_intro", "structure_id": "str_intro", "order": 2, "heading": "Introduction",
             "heading_source": "grobid_tei", "role": "research_gap", "analysis_status": "analyzed"},
            {"section_id": "sec_method", "structure_id": "str_method", "order": 3, "heading": "System Modeling",
             "heading_source": "grobid_tei", "role": "model_or_framework", "analysis_status": "analyzed"},
            {"section_id": "sec_app", "structure_id": "str_app", "order": 4, "heading": "A. Appendix",
             "heading_source": "grobid_tei", "role": "theoretical_background", "analysis_status": "analyzed"},
        ]
        groups = [
            {"id": "g-abs", "label": "Abstract", "label_origin": "source_heading", "verification_status": "membership_verified", "source_section_ids": ["sec_abs"], "section_ids": ["sec_abs"]},
            {"id": "g-intro", "label": "Introduction", "label_origin": "source_heading", "verification_status": "membership_verified", "source_section_ids": ["sec_intro"], "section_ids": ["sec_intro"]},
            {"id": "g-method", "label": "System Modeling", "label_origin": "inferred", "verification_status": "membership_verified", "source_section_ids": ["sec_method"], "section_ids": ["sec_method"]},
            {"id": "g-app", "label": "Appendices", "label_origin": "inferred", "verification_status": "membership_verified", "source_section_ids": ["sec_app"], "section_ids": ["sec_app"]},
        ]
        normalized = build_outline_layers(outline, groups, {"title": "Sample article"}, [
            {"term": "microgrid", "source_type": "author_reported"},
            {"term": "federated reinforcement learning", "source_type": "text_extracted"},
        ])["semantic"]["normalized_outline"]
        self.assertEqual(normalized["title"]["text"], "Sample article")
        self.assertEqual(normalized["abstract"]["source_section_ids"], ["sec_abs"])
        self.assertEqual(normalized["keywords"][0]["term"], "microgrid")
        self.assertEqual([item["term"] for item in normalized["keywords"]], ["microgrid"])
        section_titles = [section["title"] for section in normalized["sections"]]
        self.assertIn("Introduction", section_titles)
        self.assertIn("Methods", section_titles)
        self.assertIn("Appendices", section_titles)
        self.assertNotIn("Literature Review", section_titles)
        self.assertNotIn("Discussion", section_titles)
        method = next(section for section in normalized["sections"] if section["title"] == "Methods")
        self.assertEqual(method["subsections"][0]["source_section_ids"], ["sec_method"])
        self.assertEqual(normalized["missing_conventional_sections"], ["Results", "Discussion", "Conclusion"])

    def test_theoretical_foundations_group_maps_to_introduction_background(self):
        outline = [
            {"section_id": "sec_foundations", "order": 1, "heading": "Foundations",
             "heading_source": "grobid_tei", "role": "theoretical_background", "analysis_status": "analyzed"},
            {"section_id": "sec_mdp", "order": 2, "heading": "Markov decision process",
             "heading_source": "grobid_tei", "role": "model_or_framework", "analysis_status": "analyzed"},
        ]
        groups = [{"id": "g-foundations", "label": "Theoretical Foundations",
            "source_section_ids": ["sec_foundations", "sec_mdp"], "section_ids": ["sec_foundations", "sec_mdp"]}]
        normalized = build_outline_layers(outline, groups)["semantic"]["normalized_outline"]
        introduction = next(section for section in normalized["sections"] if section["title"] == "Introduction")
        self.assertEqual(introduction["subsections"][0]["title"], "Theoretical Foundations")
        self.assertNotIn("Methods", [section["title"] for section in normalized["sections"]])

        analysis = build_outline_layers([{
            "section_id": "sec_theory_analysis", "order": 1, "heading": "Theoretical Analysis",
            "heading_source": "grobid_tei", "role": "theoretical_background", "analysis_status": "analyzed",
        }], [{"id": "g-theory-analysis", "label": "Theoretical Analysis",
            "source_section_ids": ["sec_theory_analysis"], "section_ids": ["sec_theory_analysis"]}])["semantic"]["normalized_outline"]
        self.assertIn("Methods", [section["title"] for section in analysis["sections"]])
        self.assertNotIn("Introduction", [section["title"] for section in analysis["sections"]])

    def test_long_section_chunks_keep_paragraph_source_ids(self):
        text = "Alpha sentence.\n\nBeta sentence.\n\nGamma sentence."
        paragraphs = [
            {"id": "p1", "text": "Alpha sentence.", "start_offset": 0, "end_offset": 15},
            {"id": "p2", "text": "Beta sentence.", "start_offset": 17, "end_offset": 31},
            {"id": "p3", "text": "Gamma sentence.", "start_offset": 33, "end_offset": len(text)},
        ]
        document = {"sections": [{"id": "sec_1", "heading": "Results", "text": text,
            "start_offset": 0, "end_offset": len(text), "paragraphs": paragraphs}]}
        chunks, excluded = _outline_evidence_records(document, chunk_characters=20)
        self.assertFalse(excluded)
        self.assertGreater(len(chunks), 1)
        self.assertEqual({pid for chunk in chunks for pid in chunk["paragraph_ids"]}, {"p1", "p2", "p3"})
        self.assertTrue(all(chunk["chunk_id"] for chunk in chunks))

    def test_profile_and_outline_send_every_eligible_body_character(self):
        text = "x" * 18001
        document = {"text": text, "metadata": {}, "sections": [{"id": "sec_results",
            "heading": "Results", "section_type": "results", "text": text,
            "start_offset": 0, "end_offset": len(text), "paragraphs": [], "provenance": {}}]}
        outline_chunks, excluded = _outline_evidence_records(document)
        profile_chunks = _retrieve_profile_evidence(document)
        self.assertFalse(excluded)
        self.assertGreater(len(outline_chunks), 1)
        self.assertEqual("".join(item["text"] for item in outline_chunks), text)
        self.assertEqual("".join(item["passages"][0]["quote"] for item in profile_chunks), text)

    def test_full_text_chunks_must_reconstruct_exact_source_order(self):
        first, second = "first source section\n\n", "second source section"
        full_text = first + second
        document = {"text": full_text, "metadata": {"source_kind": "markdown"}, "sections": [
            {"id": "sec_1", "text": first}, {"id": "sec_2", "text": second}]}
        chunks = _section_chunks(document, max_chars=8)
        coverage = _verify_text_chunk_coverage(full_text, chunks, "test")
        self.assertEqual(coverage["characters_submitted"], len(full_text))
        self.assertTrue(coverage["all_mapped_text_submitted"])
        with self.assertRaisesRegex(ValueError, "exactly cover"):
            _verify_text_chunk_coverage(full_text, chunks[:-1], "test")


class OutlinePersistenceTests(unittest.TestCase):
    def test_recursive_storage_remap_covers_arrays_and_paragraph_ids(self):
        payload = {"outline_groups": [{"section_ids": ["sec_1"], "source_headings": [{"section_id": "sec_1"}]}],
                   "outline_layers": {"structural": {"nodes": [{"section_id": "sec_1", "paragraphs": [{"id": "p_1"}]}]},
                                      "semantic": {"ideas": [{"source_section_ids": ["sec_1"], "source_paragraph_ids": ["p_1"]}]}}}
        mapped = remap_outline_source_ids(payload, {"sec_1": "run:sec_1"}, {"p_1": "run:p_1"})
        self.assertEqual(mapped["outline_groups"][0]["section_ids"], ["run:sec_1"])
        idea = mapped["outline_layers"]["semantic"]["ideas"][0]
        self.assertEqual(idea["source_section_ids"], ["run:sec_1"])
        self.assertEqual(idea["source_paragraph_ids"], ["run:p_1"])
        self.assertEqual(mapped["outline_layers"]["structural"]["nodes"][0]["paragraphs"][0]["id"], "run:p_1")

    def test_legacy_group_ids_are_repaired_for_existing_runs(self):
        profile = {"outline": [{"section_id": "run-1:sec_0001", "structure_id": "structure-1", "heading": "Intro"}],
                   "outline_groups": [{"section_ids": ["sec_0001"], "source_headings": [{"section_id": "sec_0001"}]}]}
        result = repair_legacy_outline_group_references(profile, "run-1")
        self.assertEqual(result["outline_groups"][0]["section_ids"], ["run-1:sec_0001"])
        self.assertIn("outline_layers", result)

    def test_fulltext_mapping_rejects_invalid_paragraph_offsets(self):
        text = "Sample full text"
        mapping = {"schema_version": FULLTEXT_MAPPING_SCHEMA_VERSION, "full_text": text, "full_text_characters": len(text),
            "metadata": {"completeness": "full_text_candidate"}, "structure": [{"id": "structure-1", "section_id": "sec_1",
            "parent_structure_id": None}], "sections": [{"section_id": "sec_1", "ordinal": 1, "section_type": "other",
            "heading": "Results", "text": text, "start_offset": 0, "end_offset": len(text),
            "paragraphs": [{"id": "p_1", "text": text, "start_offset": 1, "end_offset": len(text) + 1}]}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mapping.json"
            source_pdf = Path(directory) / "source.pdf"
            source_pdf.write_bytes(b"%PDF test artifact")
            identity = _pdf_artifact_identity(source_pdf)
            _attach_valid_ollama_sidecar(mapping["metadata"], source_pdf)
            mapping.update({"source_pdf": source_pdf.name, "source_pdf_sha256": identity["sha256"],
                "source_pdf_size_bytes": identity["size_bytes"]})
            path.write_text(json.dumps(mapping), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "paragraph/source offset"):
                _load_and_validate_fulltext_mapping(path)

    def test_store_scopes_group_evidence_and_paragraph_objects_to_analysis_run(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PaperStore(Path(directory) / "outline.sqlite3")
            doi = "10.5555/outline-test"
            with store.connect() as db:
                db.execute("INSERT INTO papers(doi,status,updated_at) VALUES(?,?,?)", (doi, "DOWNLOADED", "now"))
            paragraph = {"id": "p_0001_001", "text": "Evidence", "start_offset": 0, "end_offset": 8, "page": 1}
            profile = {"schema_version": 3,
                "outline": [{"section_id": "sec_0001", "structure_id": "structure-0001", "heading": "Results",
                    "paragraphs": [paragraph], "paragraph_ids": [paragraph["id"]],
                    "role_source": {"section_id": "sec_0001", "paragraph_ids": [paragraph["id"]], "quote": "Evidence"}}],
                "outline_groups": [{"section_ids": ["sec_0001"], "source_section_ids": ["sec_0001"],
                    "source_headings": [{"section_id": "sec_0001", "heading": "Results"}]}],
                "outline_layers": {"structural": {"nodes": [{"section_id": "sec_0001", "paragraphs": [paragraph]}]},
                    "semantic": {"ideas": [{"source_section_ids": ["sec_0001"], "source_paragraph_ids": [paragraph["id"]],
                        "evidence_spans": [{"section_id": "sec_0001", "paragraph_ids": [paragraph["id"]], "quote": "Evidence"}]}]}}}
            run = {"id": "run-1", "status": "DONE", "provider": "ollama", "model": "test", "prompt_versions": {},
                "document": {"metadata": {}, "sections": [{"id": "sec_0001", "section_type": "results", "heading": "Results",
                    "text": "Evidence", "start_offset": 0, "end_offset": 8, "provenance": {}, "paragraphs": [paragraph]}]},
                "validation": {}, "analysis_payload": {"paper_profile": profile}, "propositions": [], "relations": [],
                "graph": {"nodes": [], "edges": []}}
            store.save_argumentation(doi, run)
            with store.connect() as db:
                saved = json.loads(db.execute("SELECT analysis_payload FROM analysis_runs WHERE id='run-1'").fetchone()[0])
            saved_profile = saved["paper_profile"]
            self.assertEqual(saved_profile["outline_groups"][0]["section_ids"], ["run-1:sec_0001"])
            self.assertEqual(saved_profile["outline_layers"]["structural"]["nodes"][0]["paragraphs"][0]["id"], "run-1:p_0001_001")
            evidence = saved_profile["outline_layers"]["semantic"]["ideas"][0]["evidence_spans"][0]
            self.assertEqual(evidence["section_id"], "run-1:sec_0001")
            self.assertEqual(evidence["paragraph_ids"], ["run-1:p_0001_001"])


if __name__ == "__main__":
    unittest.main()
