import unittest

from tools.hyland_eval import score_hyland_sample


class HylandEvalTests(unittest.TestCase):
    def setUp(self):
        self.paper_id = "paper-1"
        self.sentence = "The method may improve outcomes."
        self.sentence_start = 100
        self.source_hash = "abc123"
        self.source_text_hash = "text-sha256"
        self.review_row = {"paper_id": self.paper_id, "source_sha256": self.source_hash,
            "source_text_sha256": self.source_text_hash,
            "reviewer_id": "R1", "independent": True, "sentence_id": "HY-S000001",
            "section": "Results", "source_sentence": self.sentence,
            "sentence_start_offset": self.sentence_start,
            "sentence_end_offset": self.sentence_start + len(self.sentence),
            "annotation_status": "REVIEWED", "annotations": [{"category": "Hedges",
                "marker": "may", "start_offset": self.sentence_start + 11,
                "end_offset": self.sentence_start + 14,
                "function": "Limits commitment to the effect."}]}

    def test_scores_only_reviewed_sentences_and_reports_each_hyland_label(self):
        left = dict(self.review_row)
        right = {**self.review_row, "reviewer_id": "R2"}
        gold = {**self.review_row, "annotations": list(self.review_row["annotations"]),
            "adjudicated": True, "adjudicator_id": "R3"}
        system = {"paper_id": self.paper_id, "source_sha256": self.source_hash,
            "source_text_sha256": self.source_text_hash,
            "hyland_annotations": [
                {"sentence_id": "HY-S000001", "category": "Hedges", "marker": "may",
                 "start_offset": self.sentence_start + 11, "end_offset": self.sentence_start + 14},
                {"sentence_id": "HY-S000099", "category": "Self Mention", "marker": "We",
                 "start_offset": 999, "end_offset": 1001},
            ]}

        metrics = score_hyland_sample(system, [left], [right], [gold])

        self.assertEqual(metrics["sampled_sentence_count"], 1)
        self.assertEqual(metrics["system_annotations_in_sample"], 1)
        self.assertEqual(metrics["system_annotations_outside_sample_excluded"], 1)
        self.assertEqual(metrics["hyland"]["Hedges"]["f1"], 1.0)
        self.assertEqual(metrics["hyland"]["Self Mention"]["f1"], None)
        self.assertEqual(metrics["reviewer_agreement"]["Hedges"]["f1"], 1.0)

    def test_requires_both_reviewers_to_complete_same_sample(self):
        left = dict(self.review_row)
        right = {**self.review_row, "reviewer_id": "R2", "annotation_status": "UNREVIEWED"}
        gold = {**self.review_row, "adjudicated": True, "adjudicator_id": "R3"}
        with self.assertRaisesRegex(ValueError, "unreviewed"):
            score_hyland_sample({"paper_id": self.paper_id, "source_sha256": self.source_hash,
                "source_text_sha256": self.source_text_hash,
                "hyland_annotations": []}, [left], [right], [gold])


if __name__ == "__main__":
    unittest.main()
