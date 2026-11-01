# ADR 0001: Use OpenAlex Topics for canonical Repository filters

## Status

Accepted

## Context

Paper Fetcher needs per-paper term and taxonomy data. SAFFRON produces evidence-linked term candidates, but its TAXO pipeline requires a compatible trained SVM model. Training that model requires reviewed gold `.taxo` hierarchies plus term and document-term data; this project does not have that labeled set yet.

SLR-BE already stores OpenAlex classification IDs on Research Works and uses those IDs in Repository filters. Its analysis-run intake previously did not accept and persist that existing classification field.

## Decision

During per-paper analysis, Fetcher looks up an OpenAlex Work using the paper's exact DOI (or its known OpenAlex Work ID). For a matching Work, it stores primary topic, topic labels/scores, hierarchy labels, IDs, and provenance in the analysis artifact as `openalex_classification`, separate from SAFFRON candidates. On upload, it sends the canonical primary topic, assigned topic IDs, and hierarchy IDs through the existing `classification` metadata field.

SAFFRON term candidates and any future SAFFRON taxonomy remain a separate, evidence-linked analysis result. OpenAlex IDs are not inferred by matching SAFFRON labels. SLR-BE only validates and persists the existing classification field; it does not run either classifier or introduce a new filter endpoint.

## Alternatives considered

- Train SAFFRON TAXO immediately: deferred until a reviewed domain training set with term/document-term mappings and gold hierarchy labels exists.
- Convert SAFFRON term strings to OpenAlex IDs by label similarity: rejected because label overlap does not establish a stable taxonomy identity.
- Add term extraction or classification logic to SLR-BE: rejected; analysis remains Fetcher-owned and BE stays the store/API surface.
- Keep Repository filters without per-paper classifications: rejected because OpenAlex Work classification is already supported and can be attached through the existing metadata contract.

## Consequences

- Uploaded papers can use existing domain/field/subfield/topic filters when OpenAlex returns an exact DOI match.
- Missing or mismatched OpenAlex records do not fail the paper or analysis upload; classification is omitted.
- OpenAlex taxonomy provenance and scores remain distinguishable from SAFFRON candidates.
- SAFFRON TAXO is still incomplete until a compatible model trained on reviewed, representative data is supplied.

## References

- [OpenAlex Topics and Work classification](https://help.openalex.org/data/topics/)
- SLR-BE existing classification fields: sibling checkout `../slr-system/slr-be/src/modules/research-repository/repository.types.ts`
- SLR-BE analysis intake contract: sibling checkout `../slr-system/slr-be/src/modules/paper-analysis/paper-analysis.schemas.ts`
