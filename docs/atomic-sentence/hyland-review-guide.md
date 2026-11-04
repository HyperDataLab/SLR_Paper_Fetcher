# Hyland Stance and Engagement Review Guide

Use this guide to label the blinded sample created by `tools/atomic_review_pack.py`.
The unit is one marker-function occurrence in the supplied sentence. Use the
previous and next sentences only to resolve discourse function and addressee.
Do not inspect or copy the AI annotations. Two reviewers complete the same
sample independently before discussing disagreements.

Create two identical, blinded, section-stratified review files from an analysis
JSON:

```powershell
python tools/atomic_review_pack.py --system analysis.json --sample-size 60 --seed 42 `
  --reviewer-one reviewer1.jsonl --reviewer-two reviewer2.jsonl
```

## Labels

### Stance

- **Hedges:** the writer limits commitment or presents a proposition as
  plausible rather than certain (for example, epistemic `may`, `might`,
  `perhaps`, or `suggest`). A date such as “May 2025” is not a hedge.
- **Boosters:** the writer strengthens commitment or presents a proposition as
  certain (for example, `clearly`, `obviously`, or a reporting verb such as
  `demonstrate` when it asserts strong support). A method that works
  “efficiently” is not automatically a booster.
- **Attitude Markers:** the writer explicitly evaluates or expresses affect
  toward a proposition (for example, `important`, `surprisingly`, or
  `unfortunately`). A measured technical property is not automatically an
  attitude marker.
- **Self Mention:** an explicit first-person form refers to the paper's author
  or authors (`I`, authorial `we`, `our`). Do not label a pronoun that refers
  to a real-world group as authorial presence.

### Engagement

- **Reader Pronouns:** the writer explicitly addresses or includes readers
  (`you`, `your`, or inclusive `we/us`). Distinguish inclusive writer-reader
  `we` from author-only `we` and from a real-world group.
- **Directives:** the writer guides readers to perform, notice, consider,
  interpret, or navigate something. `Should` is a directive only when it
  directs the reader; a statement about what a method or system should do is
  not enough. Record whether it is textual, physical, or cognitive in the
  function note.
- **Questions:** a genuine or rhetorical question that positions the reader
  in the discourse. Do not infer a question from a question mark inside a
  title, citation, or quoted source that is not functioning as writer-reader
  interaction.
- **Knowledge Reference:** an explicit appeal to shared or accepted
  disciplinary knowledge that asks readers to recognize common ground (for
  example, `of course` or `as is well known`). A citation, technical fact, or
  familiar term alone is not enough.
- **Asides:** a brief, interruptive and removable comment that connects with
  the reader or reveals writer intervention, often parenthetical or
  dash-delimited. Do not label a necessary definition, explanation, method
  step, or citation as an aside just because it is parenthetical.

## Annotation procedure

1. Read the sentence and its neighboring context. Label only clear functions
   supported by wording in the sentence.
2. Include every distinct marker-function occurrence. Repeated occurrences
   need separate records. A single occurrence may receive more than one
   category only when it clearly performs both functions.
3. For each record, enter the category, exact marker text, absolute
   `start_offset` and `end_offset`, and a short explanation of its function.
   Offsets refer to character positions in the full extracted source text; the
   start is inclusive and the end is exclusive. Copy marker case and
   punctuation exactly.
4. Leave `annotations` empty when the sentence has no clear Hyland marker.
   Mark every completed row `annotation_status: "REVIEWED"`, including rows
   with no markers. Use `UNREVIEWED` only until that sentence has been assessed.
5. Do not infer the author's intent beyond the source context. If an item is
   genuinely ambiguous, record the best-supported label and explain the
   ambiguity in the function note for adjudication.

Example annotation:

```json
{
  "category": "Hedges",
  "marker": "may",
  "start_offset": 4182,
  "end_offset": 4185,
  "function": "Limits commitment to the predicted effect."
}
```

## Adjudicated gold row

After both reviewers finish, a named adjudicator resolves disagreements and
creates one row per sampled sentence in `gold.jsonl`. Preserve the sentence
and offsets from the review packet, add the adjudicated `annotations`, and set
`adjudicated: true` plus `adjudicator_id`. Keep the original reviewer files
unchanged so agreement can be calculated independently of adjudication.

Each adjudicated row has this shape (the annotation list may be empty):

```json
{
  "paper_id": "paper-id",
  "source_sha256": "same hash as the analysis and review packets",
  "source_text_sha256": "same extracted-text hash as the analysis and review packets",
  "sentence_id": "HY-S000001",
  "section": "Results",
  "source_sentence": "The method may improve outcomes.",
  "sentence_start_offset": 100,
  "sentence_end_offset": 132,
  "annotations": [
    {"category": "Hedges", "marker": "may", "start_offset": 111,
     "end_offset": 114, "function": "Limits commitment to the effect."}
  ],
  "adjudicated": true,
  "adjudicator_id": "reviewer-3"
}
```

The gold offsets are absolute offsets into the same extracted source text
(Markdown or full-text mapping). Run the
sample evaluator after adjudication:

```powershell
python tools/hyland_eval.py --system analysis.json `
  --reviewer-one reviewer1.jsonl --reviewer-two reviewer2.jsonl `
  --gold gold.jsonl --out hyland-metrics.json
```
