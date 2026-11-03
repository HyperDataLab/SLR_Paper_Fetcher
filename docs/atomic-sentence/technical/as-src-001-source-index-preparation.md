# AS-SRC-001 — Source Index Preparation

**Status:** READY FOR REVIEW — nonbinding technical preparation only  
**Canonical ticket:** AS-SRC-001 (unchanged)  
**Implementation status:** BLOCKED under the current QA-03 dependency graph and approval record  
**Scope:** Source identity, exact source offsets, page/section mapping, provenance, stale detection, and fixture preparation.

This note records current repository behavior and a proposed contract for review. It does not approve product behavior, resolve a ticket dependency, authorize a migration, or implement an indexer.

## Current source-mapping behavior

The existing PDF/GROBID path in `ai_analysis.py` writes a `.fulltext.json` mapping with schema version, PDF filename, PDF SHA-256 and size, full text and character count, structure, sections, paragraphs, and section page spans. `_load_and_validate_fulltext_mapping()` checks the mapping schema version, current PDF hash and size, full-text reconstruction, and exact section/paragraph slices.

The current Python validator treats `start_offset` as inclusive and `end_offset` as exclusive: it checks `end - start == len(text)` and `full_text[start:end] == text`. These offsets are Python string indexes. Any API or JavaScript consumer must explicitly preserve/convert this unit; they must not treat these values as PDF.js character offsets or byte offsets.

The existing mapping pins the source PDF, but the mapping schema version is not a sentence-segmenter version. The top-level format does not define dedicated canonical fields for a mapping-artifact digest, normalized-text digest, or Atomic segmenter identity. The Atomic source version should therefore fingerprint these inputs without rewriting the existing artifact.

GROBID `page` and `page_spans` are retained as provenance in the current mapping. Their presence does not by itself prove a PDF.js physical-page mapping or an exact PDF text-layer position. Existing UI section navigation separately matches text against the rendered PDF.js text layer and can fall back to a page-only location. AS-SRC-001 must preserve unavailable or ambiguous anchors rather than inventing a page or coordinate.

The Markdown source path preserves CRLF/LF in the source string and records a source-file hash, but it has no PDF page spans. Structured paper JSON is separately named in AS-API-002 requirements and needs an explicit adapter/contract; it must not be assumed equivalent to the current GROBID mapping format.

## Proposed source-unit contract (pending approval)

The proposed implementation boundary is a deterministic, side-effect-free transformation from a validated source mapping plus an explicit segmenter identity to ordered source units. Persistence, paper lookup, and API readiness remain owned by their existing canonical tickets.

Each proposed sentence source unit should retain:

- Existing paper key and source kind, without creating a duplicate paper record.
- Source PDF SHA-256 and size when a PDF is the source.
- Mapping schema version plus a digest of the exact mapping artifact or its canonical content.
- A digest and character length for the exact full-text representation consumed by the segmenter.
- Segmenter name/version and the declared offset unit.
- Section and paragraph identifiers, stable order, exact start/end offsets, and exact text copied from the mapped full text.
- Zero or more original page-span records and an explicit page-anchor state (for example, exact, page-only, ambiguous, or unavailable); no inferred physical page.

Candidate identity can be stable within an immutable source/index version and include the parent paragraph, exact span, and segmenter version. The exact ID algorithm, offset field names, persisted representation, and whether source text is copied or reconstructed are contract decisions for AS-DATA-001/002 and the shared source/API review; this note does not freeze them.

For every produced unit, the invariant is:

```text
unit.text == full_text[unit.start_offset:unit.end_offset]
```

Units must preserve source order, must not cross a paragraph boundary unless an approved rule explicitly permits it, and must surface unsupported segmentation or missing/ambiguous page evidence. Sentence offsets must never be converted into PDF.js positions by arithmetic alone.

### Evidence-link semantics still open

AS-OD-10 remains OPEN. A source sentence unit can serve as an input to later evidence links, but this work must not decide the permitted number of evidence spans, whether every item requires a primary span, or the product meaning of primary evidence versus supporting context. Preserve source type and span provenance so the approved contract can distinguish those concepts later.

AS-OD-14 remains OPEN. The technical fingerprint should make changes detectable; whether a changed source invalidates, supersedes, or permits re-anchoring of reviewed Atomic items is an approval decision. Detection and lifecycle policy must remain separate.

## Proposed freshness/provenance inputs

For reproducible indexing, compare the current inputs against the version used to build each source unit:

1. Source PDF SHA-256 and size, when applicable.
2. Mapping schema version and mapping-artifact digest.
3. Exact source-text digest and declared text representation.
4. Segmenter identity/version and segmentation configuration that affects boundaries.
5. Stable section/paragraph references and exact source slice.

A difference should produce a detectable source/index-version mismatch. The specific status name, automatic invalidation behavior, review transfer, and re-anchoring rules remain subject to AS-OD-14 and the approved lifecycle contract. Do not mutate the source mapping to add Atomic state.

## Fixture preparation matrix

These are proposed, non-mutating fixture cases for AS-SRC-001 and AS-QA-004. Expected results below describe technical invariants, not product approval.

| Fixture | Expected technical result |
|---|---|
| One sentence with ordinary punctuation | Exact substring round-trip; stable order and offsets for a fixed source/segmenter version. |
| Abbreviations, initials, decimal numbers, and punctuation inside parentheses/quotes | Boundaries follow the selected segmenter; source text remains byte-for-byte/string-for-string unnormalized in the emitted quote. |
| Unicode combining marks, accented characters, and non-BMP characters | Round-trip remains exact in the declared Python-string offset unit; conversion tests are required at any JavaScript/API boundary. |
| CRLF and LF source text | Existing source representation and offsets are preserved; no implicit newline normalization. |
| Hyphenation or line-break artifacts | Preserve the mapped text as received; flag unsupported repair rather than silently changing source text. |
| Adjacent paragraphs and section boundaries | No accidental cross-boundary sentence; section/paragraph ancestry is retained. |
| Valid, missing, coarse, overlapping, or multi-page page spans | Preserve supplied spans; report missing/ambiguous mapping; never guess a page or exact highlight. |
| Duplicate quote on one or more pages | Keep source offsets authoritative; page/text-layer matching is marked ambiguous where uniqueness is not proven. |
| Negative, reversed, out-of-range, overlapping, or quote-mismatched offsets | Reject or mark the mapping invalid before indexing; do not emit source units from invalid ranges. |
| PDF hash/size mismatch | Mapping is stale/invalid under the existing validator; no source units are emitted. |
| Same PDF but changed mapping/text digest | Produce a distinct detectable source/index version; lifecycle consequences remain pending AS-OD-14. |
| Same source but changed segmenter version/configuration | Produce a distinct index identity; do not silently replace old unit identities. |
| Partial/abstract-only or unsupported structured input | Preserve an explicit unsupported/partial readiness result; do not present it as a complete source index. |

Existing tests in `tests/test_outline_analysis.py` already cover mapping round-trip and malformed paragraph offsets. They are precedent, not sufficient AS-SRC-001 acceptance. The future Atomic fixture suite should live alongside Atomic source-index code and include the cases above after the shared contract is approved.

## Approval and dependency gates

AS-SRC-001 remains **BLOCKED — TECHNICAL DEPENDENCY**. Current QA-03 dependencies are AS-GOV-002, AS-DATA-001/002, AS-API-002, and AS-OD-10/11/14. AS-GOV-002 proposes a non-circular sequence, but that proposal has not been accepted by the Backlog Owner; current dependency edges remain authoritative.

Before production indexer code begins, the record needs:

1. Authorized Product Owner outcomes and a versioned, internally consistent AS-GOV-002 baseline.
2. Product decisions for evidence cardinality/primary-context semantics (AS-OD-10), supported languages and segmentation/tokenization (AS-OD-11), and source invalidation/re-anchoring behavior (AS-OD-14).
3. AS-DATA-001 approval of the additive source/version data model and source-unit interface.
4. A reviewed shared source/API boundary, including source types, source identity, offset units, mapping fingerprint, and page-anchor states.
5. Validated fixtures for the accepted input formats.
6. Backlog Owner acceptance of a dependency refinement before removing the AS-DATA-002 / AS-API-002 cycle.

The current governance record also has unresolved Product Owner outcomes and required Research Lead actions for the wider AS-GOV-002 baseline. AS-OD-03 role-mapping review is pending, and the record does not define it as co-approval. AS-OD-09/15/16 remain pending Research Lead review/approval. No approver identity or approval timestamp is inferred here.

## Safe next step

Review this proposed contract and fixture matrix with the source/API and data owners. Until the stated gates are recorded, continue only read-only inventory and fixture design. Do not add a production indexer, API route, migration, database table, source-artifact rewrite, or change to existing analysis semantics under this preparation note.

## Repository references

- `ai_analysis.py`: `_write_fulltext_mapping()`, `_load_and_validate_fulltext_mapping()`, `_pdf_artifact_identity()`, and the Markdown source mapping path.
- `paper_store.py`: existing analysis/source persistence and PDF-hash validation conventions; not an Atomic persistence contract.
- `tests/test_outline_analysis.py`: current mapping round-trip and malformed-offset coverage.
- `docs/atomic-sentence/qa03/qa03-development-backlog.md`: canonical AS-SRC-001 scope and current dependencies.
- `docs/atomic-sentence/governance/as-gov-002-dependency-resolution.md`: proposed dependency refinement; not accepted by the Backlog Owner.
- `docs/atomic-sentence/governance/as-gov-003-implementation-readiness.md`: current implementation gates and safe preparation boundary.
- `docs/atomic-sentence/technical/as-tech-01-database-design-proposal.md`: prior nonbinding source/version and evidence design alternatives.
