# Hyland / Atomic Sentence pilot review

This folder contains one end-to-end analysis and a blinded reviewer sample for
the IoT federated-learning article. The model output is a prediction snapshot,
not gold data.

## Pilot snapshot

- Scope version: `hyland_prose_scope.2`
- Saved Hyland prompt: `hyland_fulltext_stance_engagement.1`
- Denominator: 6,727 whitespace-tokenized prose words
- Eligible sentences: 363
- Full-text Hyland annotations: 153
- Atomic Sentence candidates: 313; all remain pending human review
- Model: `gpt-oss:120b-cloud` via Ollama
- PDF SHA-256: `4deb303956b41055980c855b6924d3fade3ac84ad5200147640019fc5155b40c`
- Extracted text SHA-256: `f9956e251b0f118d98db1df7950de878f761b87d000773017fec4431d1814bfe`

The denominator includes the Abstract and article prose through Conclusion,
including appendices and prose citations. It excludes headings, references,
author/declaration metadata, table and figure captions/cells, footnotes,
standalone equations, algorithm listings, and short heading fragments. See
the analysis JSON for excluded-block counts and prompt/scope versions.

The current code is at Hyland prompt version `.2`, which adds a rationale
repair pass and rejects category-only function notes. The saved live snapshot
above used prompt `.1`. A fresh `.2` run could not complete because Ollama
returned HTTP 429 (monthly usage limit); no Gemini key is configured. The saved
snapshot remains usable for the pilot review, but it does not verify the new
rationale repair behavior. In this older snapshot, 113 of 153 rationale fields
are shorter than four words or repeat only a label, so use it as a table/pipeline
demonstration, not as a rationale-quality result.

## Files

- `analysis-10.33969-j-nana-2025-050103-snapshot-hyland-v1.json`: complete analysis, table, source
  annotations, offsets, sentence inventory, and provenance.
- `reviewer-1.jsonl` and `reviewer-2.jsonl`: the same 60 source sentences with
  no model labels. They are still `UNREVIEWED` and are ready to assign to two
  independent reviewers.

Reviewers should follow [`../../docs/atomic-sentence/hyland-review-guide.md`](../../docs/atomic-sentence/hyland-review-guide.md).
After both reviewers finish, create an adjudicated `gold.jsonl` with one row per
sampled sentence, including empty annotation arrays for reviewed sentences with
no markers. Then run:

```powershell
python tools/hyland_eval.py `
  --system reports/atomic-sentence-review/analysis-10.33969-j-nana-2025-050103-snapshot-hyland-v1.json `
  --reviewer-one reports/atomic-sentence-review/reviewer-1.jsonl `
  --reviewer-two reports/atomic-sentence-review/reviewer-2.jsonl `
  --gold reports/atomic-sentence-review/gold.jsonl `
  --out reports/atomic-sentence-review/hyland-metrics.json
```

No reviewer F1 is reported yet because the reviewer files contain no human
labels. The evaluator only scores system annotations whose sentence IDs are in
the reviewed sample and reports Precision, Recall, and F1 for each of the nine
Hyland categories.

