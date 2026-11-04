#!/usr/bin/env python3
"""Evaluate full-text Hyland annotations on a blinded, independently reviewed sample.

Reviewer JSONL files are the outputs of ``atomic_review_pack.py`` after each
reviewer has completed every sampled sentence. The adjudicated JSONL has one
row per sampled sentence with an ``annotations`` array and explicit
``adjudicated``/``adjudicator_id`` fields. Predictions outside the sample are
excluded from the confusion counts.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


CATEGORIES = ("Hedges", "Boosters", "Attitude Markers", "Self Mention", "Reader Pronouns",
              "Directives", "Questions", "Knowledge Reference", "Asides")


def _read_jsonl(path):
    rows = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_number}: row must be a JSON object")
        rows.append(row)
    return rows


def _f1(predicted, gold):
    counts = {category: [0, 0, 0] for category in CATEGORIES}
    for key in set(predicted) | set(gold):
        category = key[0]
        if category not in counts:
            raise ValueError(f"Unknown Hyland category: {category!r}")
        tp = min(predicted[key], gold[key])
        counts[category][0] += tp
        counts[category][1] += predicted[key] - tp
        counts[category][2] += gold[key] - tp
    result = {}
    for category, (tp, fp, fn) in counts.items():
        precision = tp / (tp + fp) if tp + fp else None
        recall = tp / (tp + fn) if tp + fn else None
        f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
        result[category] = {"precision": round(precision, 4) if precision is not None else None,
            "recall": round(recall, 4) if recall is not None else None,
            "f1": round(f1, 4) if f1 is not None else None, "tp": tp, "fp": fp, "fn": fn}
    defined = [item["f1"] for item in result.values() if item["f1"] is not None]
    result["macro_f1"] = round(sum(defined) / len(defined), 4) if defined else None
    return result


def _sample_index(rows, label, require_adjudication=False):
    indexed = {}
    for row in rows:
        key = (str(row.get("paper_id") or ""), str(row.get("sentence_id") or ""))
        if not all(key) or key in indexed:
            raise ValueError(f"{label} has a missing or duplicate paper/sentence ID: {key!r}")
        if row.get("annotation_status") != "REVIEWED" and not require_adjudication:
            raise ValueError(f"{label} has an unreviewed sentence: {key!r}")
        if require_adjudication and (row.get("adjudicated") is not True
                or not str(row.get("adjudicator_id") or "").strip()):
            raise ValueError(f"Adjudication is missing for sentence {key!r}")
        sentence = row.get("source_sentence")
        start, end = row.get("sentence_start_offset"), row.get("sentence_end_offset")
        if (not isinstance(sentence, str) or not sentence.strip() or not isinstance(start, int)
                or not isinstance(end, int) or end - start != len(sentence)):
            raise ValueError(f"Invalid source sentence span for {key!r}")
        indexed[key] = row
    return indexed


def _annotation_counter(rows, paper_id, source_row):
    sentence = source_row["source_sentence"]
    sentence_start = source_row["sentence_start_offset"]
    records = Counter()
    for annotation in rows or []:
        category, marker = annotation.get("category"), annotation.get("marker")
        start, end = annotation.get("start_offset"), annotation.get("end_offset")
        if (category not in CATEGORIES or not isinstance(marker, str) or not marker
                or not isinstance(start, int) or not isinstance(end, int) or end - start != len(marker)
                or start < sentence_start or end > sentence_start + len(sentence)
                or sentence[start - sentence_start:end - sentence_start] != marker):
            raise ValueError(f"Invalid exact marker span for {paper_id}/{source_row.get('sentence_id')}: {annotation!r}")
        records[(category, start, end)] += 1
    return records


def score_hyland_sample(system, reviewer_one, reviewer_two, adjudicated_rows):
    """Score model predictions only where both reviewers independently labeled."""
    system = [system] if isinstance(system, dict) else system
    system_by_paper = {str(item.get("paper_id") or ""): item for item in system}
    if "" in system_by_paper or len(system_by_paper) != len(system):
        raise ValueError("System analysis has a missing or duplicate paper_id.")
    first = _sample_index(reviewer_one, "Reviewer one")
    second = _sample_index(reviewer_two, "Reviewer two")
    gold = _sample_index(adjudicated_rows, "Adjudicated sample", require_adjudication=True)
    if not first or set(first) != set(second) or set(first) != set(gold):
        raise ValueError("Both reviewers and adjudicated gold must cover the same non-empty sample.")
    if any(not row.get("independent") for row in reviewer_one + reviewer_two):
        raise ValueError("Reviewer rows must record independent=true.")
    reviewer_one_ids = {str(row.get("reviewer_id") or "") for row in reviewer_one}
    reviewer_two_ids = {str(row.get("reviewer_id") or "") for row in reviewer_two}
    if len(reviewer_one_ids) != 1 or len(reviewer_two_ids) != 1 or reviewer_one_ids == reviewer_two_ids:
        raise ValueError("Reviewer files must each identify one distinct reviewer.")
    adjudicator_ids = {str(row.get("adjudicator_id") or "") for row in adjudicated_rows}
    if len(adjudicator_ids) != 1 or "" in adjudicator_ids or adjudicator_ids & (reviewer_one_ids | reviewer_two_ids):
        raise ValueError("Adjudication must name one adjudicator distinct from both reviewers.")

    reviewer_one_annotations = Counter()
    reviewer_two_annotations = Counter()
    gold_annotations = Counter()
    for key, left in first.items():
        right, gold_row = second[key], gold[key]
        for field in ("source_sha256", "section", "source_sentence", "sentence_start_offset", "sentence_end_offset"):
            if left.get(field) != right.get(field) or left.get(field) != gold_row.get(field):
                raise ValueError(f"Reviewer source mismatch for {key!r} in field {field!r}.")
        for field in ("source_sha256", "source_text_sha256"):
            if (left.get(field) != right.get(field) or left.get(field) != gold_row.get(field)
                    or left.get(field) != system_by_paper.get(key[0], {}).get(field)):
                raise ValueError(f"{field} differs between analysis and review sample for {key[0]}.")
        reviewer_one_annotations.update(_annotation_counter(left.get("annotations"), key[0], left))
        reviewer_two_annotations.update(_annotation_counter(right.get("annotations"), key[0], right))
        gold_annotations.update(_annotation_counter(gold_row.get("annotations"), key[0], gold_row))

    predictions = Counter()
    total_system_annotations = 0
    for paper_id in {key[0] for key in first}:
        paper = system_by_paper.get(paper_id)
        if not paper:
            raise ValueError(f"No system output for reviewed paper {paper_id}.")
        for annotation in paper.get("hyland_annotations") or []:
            key = (paper_id, str(annotation.get("sentence_id") or ""))
            if key in first:
                source_row = first[key]
                predictions.update(_annotation_counter([annotation], paper_id, source_row))
                total_system_annotations += 1

    return {"paper_count": len({key[0] for key in first}), "sampled_sentence_count": len(first),
        "reviewer_one_annotation_count": sum(len(row.get("annotations") or []) for row in first.values()),
        "reviewer_two_annotation_count": sum(len(row.get("annotations") or []) for row in second.values()),
        "adjudicated_annotation_count": sum(gold_annotations.values()),
        "system_annotations_in_sample": total_system_annotations,
        "system_annotations_outside_sample_excluded": sum(len((system_by_paper[paper_id].get("hyland_annotations") or []))
            for paper_id in {key[0] for key in first}) - total_system_annotations,
        "hyland": _f1(predictions, gold_annotations),
        "reviewer_agreement": _f1(reviewer_one_annotations, reviewer_two_annotations)}


def _read_system(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if isinstance(payload, dict):
        return [payload]
    if not isinstance(payload, list) or any(not isinstance(item, dict) for item in payload):
        raise ValueError("System JSON must contain an analysis object or an array of analysis objects.")
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system", required=True)
    parser.add_argument("--reviewer-one", required=True)
    parser.add_argument("--reviewer-two", required=True)
    parser.add_argument("--gold", required=True, help="Adjudicated JSONL, one row per sampled sentence")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    try:
        metrics = score_hyland_sample(_read_system(args.system), _read_jsonl(args.reviewer_one),
            _read_jsonl(args.reviewer_two), _read_jsonl(args.gold))
    except (OSError, ValueError, TypeError) as exc:
        parser.error(str(exc))
    output = json.dumps(metrics, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
