#!/usr/bin/env python3
"""Score Atomic Sentence pipeline output against independent human labels.

Gold JSONL has one row per paper:
  {"paper_id":"p1","gold_candidates":[{"gold_id":"G1","section":"Results",
   "atomic_sentence":"...","evidence":[{"quote":"exact source text"}]}],
   "hyland_reviewers":[{"reviewer_id":"R1","independent":true,"annotations":[...]}],
   "adjudication":{"adjudicated":true,"adjudicator_id":"R3"},
   "hyland":[{"section":"Results","category":"Hedges","marker":"may",
   "source_quote":"exact source sentence","source_sentence":"...",
   "sentence_start_offset":100,"start_offset":104,"end_offset":107}]}

Review JSONL has one row per predicted candidate:
  {"paper_id":"p1","as_id":"AS-0001","match_status":"MATCH",
   "matched_gold_id":"G1","atomicity_pass":true,"meaning_preserved":true,
   "human_support_status":"SUPPORTED"}

MATCH means the same proposition with material qualifiers preserved;
PARTIAL_MATCH means the core proposition is the same but a material element is
missing; NO_MATCH means a different proposition or unsupported content. Exact
extraction precision/recall count only MATCH; the separate detection metric
counts MATCH and PARTIAL_MATCH as detected candidates. Hyland is matched by
category + exact source offsets; exact-marker multiset scores are also reported
as relaxed diagnostics for boundary differences.
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


SUPPORT_LABELS = {"SUPPORTED", "PARTIAL", "CONTRADICTED", "UNDETERMINED"}
MATCH_LABELS = {"MATCH", "PARTIAL_MATCH", "NO_MATCH"}
STANCE = {"Hedges", "Boosters", "Attitude Markers", "Self Mention"}
ENGAGEMENT = {"Reader Pronouns", "Directives", "Questions", "Knowledge Reference", "Asides"}
CATEGORIES = STANCE | ENGAGEMENT


def _read_jsonl(path):
    rows = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{number}: each JSONL row must be an object")
        rows.append(value)
    return rows


def _read_system(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list) or any(not isinstance(row, dict) for row in payload):
        raise ValueError("System output must be one analysis object or an array of analysis objects.")
    result = {}
    for paper in payload:
        paper_id = str(paper.get("paper_id") or "")
        if not paper_id or paper_id in result:
            raise ValueError(f"Missing or duplicate paper_id in system output: {paper_id!r}")
        result[paper_id] = paper
    return result


def _f1(tp, fp, fn):
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
    return {"precision": round(precision, 4) if precision is not None else None,
            "recall": round(recall, 4) if recall is not None else None,
            "f1": round(f1, 4) if f1 is not None else None,
            "tp": tp, "fp": fp, "fn": fn}


def _candidate_section(candidate):
    return str(candidate.get("section") or "Unspecified")


def _paper_hyland(paper, paper_id, exact_span=True):
    if paper and "hyland_annotations" not in paper:
        raise ValueError(f"System output for {paper_id} is missing full-text hyland_annotations.")
    records = []
    for annotation in paper.get("hyland_annotations") or []:
        category, marker = annotation.get("category"), annotation.get("marker")
        section = str(annotation.get("section") or "Unspecified")
        start, end = annotation.get("start_offset"), annotation.get("end_offset")
        sentence_start = annotation.get("sentence_start_offset")
        source_sentence = annotation.get("source_sentence")
        if (category not in CATEGORIES or not isinstance(marker, str) or not marker
                or not isinstance(start, int) or not isinstance(end, int) or end - start != len(marker)
                or not isinstance(sentence_start, int) or not isinstance(source_sentence, str)
                or start < sentence_start or end > sentence_start + len(source_sentence)
                or source_sentence[start - sentence_start:end - sentence_start] != marker):
            raise ValueError(f"Invalid system Hyland annotation span in paper {paper.get('paper_id')}.")
        records.append((category, paper_id, section, start, end) if exact_span
                       else (category, paper_id, section, marker))
    return Counter(records)


def _gold_hyland(rows, paper_id, exact_span=True):
    records = []
    for item in rows or []:
        category, marker = item.get("category"), item.get("marker")
        source_quote = item.get("source_quote")
        start, end = item.get("start_offset"), item.get("end_offset")
        sentence_start = item.get("sentence_start_offset")
        source_sentence = item.get("source_sentence")
        if (category not in CATEGORIES or not isinstance(marker, str) or not marker
                or not isinstance(source_quote, str) or marker not in source_quote
                or not isinstance(start, int) or not isinstance(end, int) or end - start != len(marker)
                or not isinstance(sentence_start, int) or not isinstance(source_sentence, str)
                or start < sentence_start or end > sentence_start + len(source_sentence)
                or source_sentence[start - sentence_start:end - sentence_start] != marker):
            raise ValueError(f"Invalid Hyland gold annotation in {paper_id}: {item!r}")
        section = str(item.get("section") or "Unspecified")
        records.append((category, paper_id, section, start, end) if exact_span
                       else (category, paper_id, section, marker))
    return Counter(records)


def _aggregate_hyland(system, gold, exact_span=True):
    result = Counter()
    for paper_id in gold:
        result.update(_paper_hyland(system.get(paper_id, {}), paper_id, exact_span=exact_span))
    return result


def _aggregate_gold_hyland(gold, exact_span=True):
    result = Counter()
    for paper_id, paper in gold.items():
        result.update(_gold_hyland(paper.get("hyland") or [], paper_id, exact_span=exact_span))
    return result


def _reviewer_agreement(gold):
    pairs = []
    for paper_id, paper in gold.items():
        reviewers = paper.get("hyland_reviewers") or []
        reviewer_ids = [str(item.get("reviewer_id") or "") for item in reviewers]
        if (len(reviewers) < 2 or any(not item.get("independent") for item in reviewers)
                or "" in reviewer_ids or len(set(reviewer_ids)) != len(reviewer_ids)):
            raise ValueError(f"Gold labels for {paper_id} need at least two distinct independent reviewer annotations.")
        adjudication = paper.get("adjudication") or {}
        if adjudication.get("adjudicated") is not True or not str(adjudication.get("adjudicator_id") or "").strip():
            raise ValueError(f"Gold labels for {paper_id} need a recorded adjudication and adjudicator_id.")
        parsed = []
        for reviewer in reviewers:
            rows = reviewer.get("annotations") or []
            records = _gold_hyland(rows, paper_id)
            parsed.append((reviewer["reviewer_id"], Counter(
                (category, start, end) for category, _pid, _section, start, end in records)))
        for left_index in range(len(parsed)):
            for right_index in range(left_index + 1, len(parsed)):
                left_id, left = parsed[left_index]
                right_id, right = parsed[right_index]
                pairs.append({"paper_id": paper_id, "reviewers": [left_id, right_id],
                    "exact_span_f1_by_category": _hyland_metrics(left, right)["by_category"]})
    return pairs


def _hyland_metrics(predicted, expected):
    per_category = {}
    counts = defaultdict(lambda: [0, 0, 0])
    for key in set(predicted) | set(expected):
        category = key[0]
        tp = min(predicted[key], expected[key])
        counts[category][0] += tp
        counts[category][1] += predicted[key] - tp
        counts[category][2] += expected[key] - tp
    for category in sorted(CATEGORIES):
        per_category[category] = _f1(*counts[category])
    defined = [row["f1"] for row in per_category.values() if row["f1"] is not None]
    macro_f1 = sum(defined) / len(defined) if defined else None
    return {"by_category": per_category, "macro_f1": round(macro_f1, 4) if macro_f1 is not None else None}


def _candidate_result(tp, fp, fn, partial, no_match, detection_tp, detection_fp, detection_fn):
    return {"exact_match": _f1(tp, fp, fn),
            "detection_including_partial": _f1(detection_tp, detection_fp, detection_fn),
            "reviewed_match_counts": {"MATCH": tp, "PARTIAL_MATCH": partial, "NO_MATCH": no_match}}


def _positive_precision(tp, fp):
    return {"precision": round(tp / (tp + fp), 4) if tp + fp else None, "tp": tp, "fp": fp}


def score(system, gold_rows, review_rows):
    gold = {str(row.get("paper_id") or ""): row for row in gold_rows}
    if "" in gold or len(gold) != len(gold_rows):
        raise ValueError("Gold set contains a missing or duplicate paper_id.")
    reviewer_agreement = _reviewer_agreement(gold)
    review = {}
    for row in review_rows:
        key = (str(row.get("paper_id") or ""), str(row.get("as_id") or ""))
        if not all(key) or key in review:
            raise ValueError(f"Missing or duplicate review key: {key!r}")
        if row.get("match_status") not in MATCH_LABELS:
            raise ValueError(f"Invalid match_status for {key!r}")
        matched_id = row.get("matched_gold_id")
        if row["match_status"] == "NO_MATCH" and matched_id is not None:
            raise ValueError(f"NO_MATCH must have matched_gold_id=null: {key!r}")
        if row["match_status"] != "NO_MATCH" and not isinstance(matched_id, str):
            raise ValueError(f"MATCH/PARTIAL_MATCH must identify matched_gold_id: {key!r}")
        for field in ("atomicity_pass", "meaning_preserved"):
            if not isinstance(row.get(field), bool):
                raise ValueError(f"{field} must be a reviewer-labeled boolean: {key!r}")
        status = str(row.get("human_support_status") or "").upper()
        if status not in SUPPORT_LABELS:
            raise ValueError(f"Invalid human_support_status for {key!r}")
        review[key] = row

    missing_papers = sorted(set(gold) - set(system))
    extra_papers = sorted(set(system) - set(gold))
    strict_tp = strict_fp = strict_fn = partial = no_match = 0
    detection_tp = detection_fp = detection_fn = 0
    atomicity_passes = meaning_passes = support_correct = support_total = 0
    supported_tp = supported_fp = 0
    confusion = {actual: {predicted: 0 for predicted in sorted(SUPPORT_LABELS)} for actual in sorted(SUPPORT_LABELS)}
    by_paper, by_section = {}, defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "partial": 0, "no_match": 0,
        "detection_tp": 0, "detection_fp": 0, "detection_fn": 0,
        "atomicity_passes": 0, "meaning_passes": 0, "reviewed": 0, "hyland_pred": Counter(), "hyland_gold": Counter()})

    for paper_id, gold_paper in gold.items():
        paper = system.get(paper_id, {})
        expected_hash = gold_paper.get("source_sha256")
        actual_hash = paper.get("source_sha256")
        if expected_hash and actual_hash and expected_hash != actual_hash:
            raise ValueError(f"Source hash differs between system output and gold labels for {paper_id}")
        gold_candidates = gold_paper.get("gold_candidates") or []
        for item in gold_candidates:
            evidence = item.get("evidence")
            if (not isinstance(item.get("atomic_sentence"), str) or not item["atomic_sentence"].strip()
                    or not isinstance(evidence, list) or not evidence
                    or any(not isinstance(span, dict) or not isinstance(span.get("quote"), str)
                           or not span["quote"].strip() for span in evidence)):
                raise ValueError(f"Gold candidate needs an atomic_sentence and exact evidence quotes in {paper_id}")
        gold_by_id = {str(item.get("gold_id") or ""): item for item in gold_candidates}
        if "" in gold_by_id or len(gold_by_id) != len(gold_candidates):
            raise ValueError(f"Missing or duplicate gold_id in {paper_id}")
        matched_gold, detected_gold, paper_tp = set(), set(), 0
        paper_fp = paper_partial = paper_no_match = 0
        candidates = paper.get("candidates") or []
        for candidate in candidates:
            as_id = str(candidate.get("as_id") or "")
            key = (paper_id, as_id)
            human = review.get(key)
            if not as_id or human is None:
                raise ValueError(f"No human review row for predicted candidate {paper_id}/{as_id}")
            match_status, matched_id = human["match_status"], human.get("matched_gold_id")
            if matched_id is not None and matched_id not in gold_by_id:
                raise ValueError(f"Unknown matched_gold_id {matched_id!r} for {paper_id}/{as_id}")
            section = _candidate_section(candidate)
            section_row = by_section[section]
            section_row["reviewed"] += 1
            section_row["atomicity_passes"] += human["atomicity_pass"]
            section_row["meaning_passes"] += human["meaning_preserved"]
            atomicity_passes += human["atomicity_pass"]
            meaning_passes += human["meaning_preserved"]
            actual = human["human_support_status"]
            predicted = str((candidate.get("support_precheck") or {}).get("status") or "UNDETERMINED").upper()
            if predicted not in SUPPORT_LABELS:
                predicted = "UNDETERMINED"
            confusion[actual][predicted] += 1
            support_total += 1
            support_correct += predicted == actual
            if actual == "SUPPORTED" and predicted == "SUPPORTED":
                supported_tp += 1
            elif actual != "SUPPORTED" and predicted == "SUPPORTED":
                supported_fp += 1

            if match_status == "MATCH" and matched_id not in matched_gold:
                strict_tp += 1
                paper_tp += 1
                section_row["tp"] += 1
                matched_gold.add(matched_id)
                if matched_id not in detected_gold:
                    detection_tp += 1
                    section_row["detection_tp"] += 1
                    detected_gold.add(matched_id)
                else:
                    detection_fp += 1
                    section_row["detection_fp"] += 1
            elif match_status == "PARTIAL_MATCH":
                strict_fp += 1
                partial += 1
                paper_partial += 1
                paper_fp += 1
                section_row["fp"] += 1
                section_row["partial"] += 1
                if matched_id not in detected_gold:
                    detection_tp += 1
                    section_row["detection_tp"] += 1
                    detected_gold.add(matched_id)
                else:
                    detection_fp += 1
                    section_row["detection_fp"] += 1
            else:
                strict_fp += 1
                detection_fp += 1
                paper_fp += 1
                section_row["fp"] += 1
                if match_status == "NO_MATCH":
                    no_match += 1
                    paper_no_match += 1
                    section_row["no_match"] += 1

        paper_gold_ids = set(gold_by_id)
        paper_fn = len(paper_gold_ids - matched_gold)
        strict_fn += paper_fn
        for gold_id in paper_gold_ids - matched_gold:
            gold_section = str(gold_by_id[gold_id].get("section") or "Unspecified")
            by_section[gold_section]["fn"] += 1
        paper_detection_fn = len(paper_gold_ids - detected_gold)
        detection_fn += paper_detection_fn
        for gold_id in paper_gold_ids - detected_gold:
            gold_section = str(gold_by_id[gold_id].get("section") or "Unspecified")
            by_section[gold_section]["detection_fn"] += 1

        predicted_hyland = _paper_hyland(paper, paper_id)
        expected_hyland = _gold_hyland(gold_paper.get("hyland") or [], paper_id)
        by_paper[paper_id] = {"gold_candidates": len(gold_by_id), "predicted_candidates": len(candidates),
            "candidate_tp": paper_tp, "candidate_fp": paper_fp, "candidate_fn": paper_fn,
            "candidate_detection_fn": paper_detection_fn,
            "partial_matches": paper_partial, "no_matches": paper_no_match,
            "hyland": _hyland_metrics(predicted_hyland, expected_hyland)}
        for category, item_paper_id, section, start, end in predicted_hyland:
            by_section[section]["hyland_pred"][(category, item_paper_id, start, end)] += predicted_hyland[(category, item_paper_id, section, start, end)]
        for category, item_paper_id, section, start, end in expected_hyland:
            by_section[section]["hyland_gold"][(category, item_paper_id, start, end)] += expected_hyland[(category, item_paper_id, section, start, end)]

    expected_review_keys = {(paper_id, str(candidate.get("as_id") or ""))
                            for paper_id in gold for candidate in ((system.get(paper_id) or {}).get("candidates") or [])}
    if set(review) != expected_review_keys:
        missing = sorted(expected_review_keys - set(review))
        extra = sorted(set(review) - expected_review_keys)
        raise ValueError(f"Reviewer rows do not match system candidates; missing={missing}, extra={extra}")

    total_predictions = sum(len((system.get(pid) or {}).get("candidates") or []) for pid in gold)
    exact_candidates = _candidate_result(strict_tp, strict_fp, strict_fn, partial, no_match,
        detection_tp, detection_fp, detection_fn)
    sections = {}
    for section, values in sorted(by_section.items()):
        section_tp, section_fp, section_fn = values["tp"], values["fp"], values["fn"]
        section_partial, section_no_match = values["partial"], values["no_match"]
        sections[section] = {
            "candidate_extraction": _candidate_result(section_tp, section_fp, section_fn,
                section_partial, section_no_match, values["detection_tp"], values["detection_fp"], values["detection_fn"]),
            "atomicity_pass_rate": round(values["atomicity_passes"] / values["reviewed"], 4) if values["reviewed"] else None,
            "meaning_preservation_rate": round(values["meaning_passes"] / values["reviewed"], 4) if values["reviewed"] else None,
            "hyland": _hyland_metrics(values["hyland_pred"], values["hyland_gold"]),
        }
    return {
        "paper_count": len(gold), "papers_missing_system_output": missing_papers,
        "system_papers_without_gold": extra_papers,
        "candidate_extraction": exact_candidates,
        "atomicity_pass_rate": round(atomicity_passes / total_predictions, 4) if total_predictions else None,
        "meaning_preservation_rate": round(meaning_passes / total_predictions, 4) if total_predictions else None,
        "source_support": {"classification_accuracy": round(support_correct / support_total, 4) if support_total else None,
            "confusion_matrix": confusion, "supported_precision": _positive_precision(supported_tp, supported_fp)},
        "hyland": _hyland_metrics(_aggregate_hyland(system, gold), _aggregate_gold_hyland(gold)),
        "hyland_relaxed_marker_match": _hyland_metrics(_aggregate_hyland(system, gold, exact_span=False),
            _aggregate_gold_hyland(gold, exact_span=False)),
        "hyland_match_policy": "strict: exact category + source offsets; relaxed diagnostic: category + exact marker text multiset",
        "hyland_reviewer_agreement": reviewer_agreement,
        "by_paper": by_paper, "by_section": sections,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system", required=True, help="JSON file containing one or more analysis outputs")
    parser.add_argument("--gold", required=True, help="Adjudicated paper-level JSONL")
    parser.add_argument("--review", required=True, help="Human review JSONL, one row per system candidate")
    parser.add_argument("--out", help="Optional path for metrics JSON; defaults to stdout")
    args = parser.parse_args(argv)
    try:
        result = score(_read_system(args.system), _read_jsonl(args.gold), _read_jsonl(args.review))
    except (OSError, ValueError, TypeError) as exc:
        parser.error(str(exc))
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)


if __name__ == "__main__":
    main()
