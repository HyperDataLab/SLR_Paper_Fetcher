#!/usr/bin/env python3
"""Create blinded, section-stratified Hyland review files from an analysis JSON.

The two output JSONL files contain the same sampled source sentences and no AI
annotations. Reviewers fill each row's ``annotations`` list independently with
objects containing category, exact marker, absolute source offsets, and a short
function note. They must set ``annotation_status`` to ``REVIEWED`` after
completing a sentence, including sentences with no annotations. See
``docs/atomic-sentence/hyland-review-guide.md``.
"""

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path


CATEGORIES = ["Hedges", "Boosters", "Attitude Markers", "Self Mention", "Reader Pronouns",
              "Directives", "Questions", "Knowledge Reference", "Asides"]


def make_review_rows(analyses, sample_size=60, seed=42, reviewer_id="reviewer-1"):
    pools = defaultdict(list)
    source_by_paper = {}
    source_text_by_paper = {}
    for paper in analyses:
        paper_id = str(paper.get("paper_id") or "")
        if not paper_id:
            raise ValueError("Every analysis needs a paper_id.")
        source_by_paper[paper_id] = paper.get("source_sha256")
        source_text_by_paper[paper_id] = paper.get("source_text_sha256")
        inventory = paper.get("hyland_sentence_inventory")
        if not isinstance(inventory, list):
            raise ValueError(f"Analysis {paper_id} has no full-text Hyland sentence inventory.")
        for item in inventory:
            sentence = item.get("sentence")
            start, end = item.get("start_offset"), item.get("end_offset")
            if (not isinstance(sentence, str) or not sentence.strip() or not isinstance(start, int)
                    or not isinstance(end, int) or end - start != len(sentence)):
                raise ValueError(f"Invalid sentence source span in {paper_id}: {item!r}")
            key = (paper_id, str(item.get("section") or "Unsectioned"))
            pools[key].append(item)
    available = sum(len(items) for items in pools.values())
    if not available:
        raise ValueError("No source sentences are available for reviewer sampling.")
    target = min(max(1, int(sample_size)), available)
    rng = random.Random(seed)
    keys = list(pools)
    rng.shuffle(keys)
    for items in pools.values():
        rng.shuffle(items)
    selected = []
    while len(selected) < target:
        progressed = False
        for key in keys:
            if pools[key] and len(selected) < target:
                paper_id, section = key
                selected.append((paper_id, section, pools[key].pop()))
                progressed = True
        if not progressed:
            break
    selected.sort(key=lambda row: (row[0], row[1], row[2]["start_offset"]))
    rows = []
    for paper_id, section, item in selected:
        rows.append({"paper_id": paper_id, "source_sha256": source_by_paper[paper_id],
            "source_text_sha256": source_text_by_paper[paper_id],
            "reviewer_id": reviewer_id, "independent": True, "sample_seed": seed,
            "sentence_id": item["sentence_id"], "section": section,
            "source_sentence": item["sentence"],
            "previous_sentence": item.get("previous_sentence", ""),
            "next_sentence": item.get("next_sentence", ""),
            "sentence_start_offset": item["start_offset"], "sentence_end_offset": item["end_offset"],
            "marker_offset_mode": "absolute_source_character_offsets",
            "allowed_categories": CATEGORIES, "annotations": [], "annotation_status": "UNREVIEWED"})
    return rows


def _load_analyses(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list) or any(not isinstance(item, dict) for item in payload):
        raise ValueError("System JSON must contain an analysis object or an array of analysis objects.")
    return payload


def _write_jsonl(path, rows):
    contents = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    Path(path).write_text(contents, encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system", required=True, help="Saved Atomic analysis JSON")
    parser.add_argument("--sample-size", type=int, default=60)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--reviewer-one", required=True, help="Output JSONL path for reviewer one")
    parser.add_argument("--reviewer-two", required=True, help="Output JSONL path for reviewer two")
    args = parser.parse_args(argv)
    try:
        analyses = _load_analyses(args.system)
        rows_one = make_review_rows(analyses, args.sample_size, args.seed, "reviewer-1")
        rows_two = make_review_rows(analyses, args.sample_size, args.seed, "reviewer-2")
        _write_jsonl(args.reviewer_one, rows_one)
        _write_jsonl(args.reviewer_two, rows_two)
    except (OSError, ValueError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps({"sampled_sentences": len(rows_one), "papers": len({row["paper_id"] for row in rows_one}),
        "sections": sorted({row["section"] for row in rows_one}),
        "reviewer_one": args.reviewer_one, "reviewer_two": args.reviewer_two}, ensure_ascii=False))


if __name__ == "__main__":
    main()
