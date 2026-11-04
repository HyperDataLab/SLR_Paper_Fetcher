import unittest

from tools.atomic_review_pack import make_review_rows


class AtomicReviewPackTests(unittest.TestCase):
    def setUp(self):
        self.analysis = [{"paper_id": "p1", "source_sha256": "abc", "hyland_sentence_inventory": [
            {"sentence_id": "s1", "section": "Abstract", "sentence": "We may improve.",
             "start_offset": 0, "end_offset": 15, "previous_sentence": "", "next_sentence": "It helps."},
            {"sentence_id": "s2", "section": "Results", "sentence": "It helps.",
             "start_offset": 16, "end_offset": 25, "previous_sentence": "We may improve.", "next_sentence": ""},
            {"sentence_id": "s3", "section": "Results", "sentence": "We observed change.",
             "start_offset": 26, "end_offset": 45, "previous_sentence": "It helps.", "next_sentence": ""},
        ]}]

    def test_blinded_reviewers_receive_same_section_stratified_sample(self):
        first = make_review_rows(self.analysis, sample_size=2, seed=7, reviewer_id="R1")
        second = make_review_rows(self.analysis, sample_size=2, seed=7, reviewer_id="R2")
        self.assertEqual([row["sentence_id"] for row in first], [row["sentence_id"] for row in second])
        self.assertEqual({row["section"] for row in first}, {"Abstract", "Results"})
        self.assertTrue(all(row["annotations"] == [] and row["annotation_status"] == "UNREVIEWED" for row in first))
        self.assertNotIn("hyland_annotations", first[0])
        self.assertEqual({row["reviewer_id"] for row in first}, {"R1"})
        self.assertEqual({row["reviewer_id"] for row in second}, {"R2"})

    def test_invalid_source_offsets_are_rejected(self):
        invalid = [{"paper_id": "p", "hyland_sentence_inventory": [
            {"sentence_id": "s", "section": "Results", "sentence": "A sentence.",
             "start_offset": 0, "end_offset": 2}]}]
        with self.assertRaisesRegex(ValueError, "Invalid sentence source span"):
            make_review_rows(invalid)


if __name__ == "__main__":
    unittest.main()
