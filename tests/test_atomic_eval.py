import json
import unittest
from pathlib import Path

from tools.atomic_eval import score


FIXTURES = Path(__file__).parent / "fixtures" / "atomic_eval"


def read_jsonl(name):
    return [json.loads(line) for line in (FIXTURES / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def read_system():
    return {"demo-paper": json.loads((FIXTURES / "system.json").read_text(encoding="utf-8"))}


def reviewer_provenance(annotations):
    return {"hyland_reviewers": [
        {"reviewer_id": "r1", "independent": True, "annotations": annotations},
        {"reviewer_id": "r2", "independent": True, "annotations": annotations},
    ], "adjudication": {"adjudicated": True, "adjudicator_id": "r3"}}


class AtomicEvalTests(unittest.TestCase):
    def test_known_metrics_and_hyland_multiset(self):
        result = score(read_system(), read_jsonl("gold.jsonl"), read_jsonl("review.jsonl"))
        expected = json.loads((FIXTURES / "expected_metrics.json").read_text(encoding="utf-8"))
        self.assertEqual(result["candidate_extraction"], expected["candidate_extraction"])
        self.assertEqual(result["atomicity_pass_rate"], expected["atomicity_pass_rate"])
        self.assertEqual(result["meaning_preservation_rate"], expected["meaning_preservation_rate"])
        self.assertEqual(result["source_support"]["classification_accuracy"],
                         expected["source_support"]["classification_accuracy"])
        self.assertEqual(result["source_support"]["supported_precision"],
                         expected["source_support"]["supported_precision"])
        self.assertEqual(result["hyland"]["by_category"]["Hedges"], expected["hyland"]["Hedges"])
        self.assertEqual(result["hyland"]["by_category"]["Self Mention"], expected["hyland"]["Self Mention"])
        self.assertEqual(result["hyland_reviewer_agreement"][0]["exact_span_f1_by_category"]["Hedges"]["f1"], 1.0)
        # Two model "may" markers in Results compete for one gold occurrence.
        self.assertEqual(result["by_section"]["Results"]["hyland"]["by_category"]["Hedges"]["fp"], 1)

    def test_missing_system_prediction_is_a_false_negative(self):
        could_gold = {"section": "Results", "category": "Hedges", "marker": "could",
                      "source_quote": "The result could improve.", "source_sentence": "The result could improve.",
                      "sentence_start_offset": 0, "start_offset": 11, "end_offset": 16}
        result = score({}, [{"paper_id": "p", "gold_candidates": [{"gold_id": "g", "section": "Results",
                            "atomic_sentence": "The result could improve.", "evidence": [{"quote": "The result could improve."}]}],
                            **reviewer_provenance([could_gold]), "hyland": [could_gold]}], [])
        exact = result["candidate_extraction"]["exact_match"]
        self.assertEqual((exact["tp"], exact["fp"], exact["fn"]), (0, 0, 1))
        self.assertEqual(result["hyland"]["by_category"]["Hedges"]["fn"], 1)
        self.assertEqual(result["papers_missing_system_output"], ["p"])

    def test_duplicate_predictions_cannot_claim_one_gold_twice(self):
        system = {"p": {"paper_id": "p", "candidates": [
            {"as_id": "A", "section": "Results", "stance": [], "engagement": [], "support_precheck": {"status": "SUPPORTED"}},
            {"as_id": "B", "section": "Results", "stance": [], "engagement": [], "support_precheck": {"status": "SUPPORTED"}},
        ], "hyland_annotations": []}}
        gold = [{"paper_id": "p", "gold_candidates": [{"gold_id": "g", "section": "Results",
                  "atomic_sentence": "A result.", "evidence": [{"quote": "A result."}]}],
                 **reviewer_provenance([]), "hyland": []}]
        review = [
            {"paper_id": "p", "as_id": "A", "match_status": "MATCH", "matched_gold_id": "g",
             "atomicity_pass": True, "meaning_preserved": True, "human_support_status": "SUPPORTED"},
            {"paper_id": "p", "as_id": "B", "match_status": "MATCH", "matched_gold_id": "g",
             "atomicity_pass": True, "meaning_preserved": True, "human_support_status": "SUPPORTED"},
        ]
        result = score(system, gold, review)
        exact = result["candidate_extraction"]["exact_match"]
        detection = result["candidate_extraction"]["detection_including_partial"]
        self.assertEqual((exact["tp"], exact["fp"], exact["fn"]), (1, 1, 0))
        self.assertEqual((detection["tp"], detection["fp"], detection["fn"]), (1, 1, 0))

    def test_duplicate_review_rows_are_rejected(self):
        system = read_system()
        gold = read_jsonl("gold.jsonl")
        review = read_jsonl("review.jsonl")
        with self.assertRaisesRegex(ValueError, "duplicate review key"):
            score(system, gold, review + [review[0]])

    def test_gold_requires_independent_review_and_adjudication(self):
        gold = read_jsonl("gold.jsonl")
        gold[0]["hyland_reviewers"] = gold[0]["hyland_reviewers"][:1]
        with self.assertRaisesRegex(ValueError, "at least two distinct independent"):
            score(read_system(), gold, read_jsonl("review.jsonl"))

    def test_offsets_from_different_papers_are_never_matched(self):
        source_hash = "same-length-source-hash"
        sentence = "May improve results."
        base = {"paper_id": "p1", "source_sha256": source_hash, "candidates": [],
                "hyland_annotations": [{"section": "Results", "category": "Hedges", "marker": "May",
                    "function": "Hedge.", "start_offset": 0, "end_offset": 3,
                    "sentence_start_offset": 0, "source_sentence": sentence}]}
        empty_review = reviewer_provenance([])
        gold = [
            {"paper_id": "p1", "source_sha256": source_hash, "gold_candidates": [],
             **empty_review, "hyland": []},
            {"paper_id": "p2", "source_sha256": "other-hash", "gold_candidates": [],
             **reviewer_provenance([{"section": "Results", "category": "Hedges", "marker": "May",
                 "source_quote": sentence, "source_sentence": sentence, "sentence_start_offset": 0,
                 "start_offset": 0, "end_offset": 3}]),
             "hyland": [{"section": "Results", "category": "Hedges", "marker": "May",
                 "source_quote": sentence, "source_sentence": sentence, "sentence_start_offset": 0,
                 "start_offset": 0, "end_offset": 3}]},
        ]
        result = score({"p1": base}, gold, [])
        hedges = result["hyland"]["by_category"]["Hedges"]
        self.assertEqual((hedges["tp"], hedges["fp"], hedges["fn"]), (0, 1, 1))


if __name__ == "__main__":
    unittest.main()
