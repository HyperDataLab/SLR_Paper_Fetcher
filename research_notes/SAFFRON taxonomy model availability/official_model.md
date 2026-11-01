# Official SAFFRON taxonomy model availability

## Does the pinned release publish or automatically obtain a compatible model?

### Takeaway
The pinned SAFFRON checkout and the running image do not provide `/opt/saffron/models/default.json`. The upstream README's statement that first use downloads models is generic: it names no taxonomy classifier artifact or download URL, while the TAXO pipeline directly reads the configured model file.

### Cited Findings
- The pinned README says that the first pipeline run downloads “all the models needed,” but does not identify a taxonomy SVM model, a `default.json` URL, or a taxonomy-model acquisition procedure. [Pinned README](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/README.md)
- In the pinned `SaffronPipeline`, TAXO sets the default model path to `${saffron.home}/models/default.json` when no path is configured, then deserializes that file as `Model`. [SaffronPipeline.java](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/run/src/main/java/org/insightcentre/nlp/saffron/run/SaffronPipeline.java)
- Runtime inspection of the image built from that revision found only `en-pos-maxent.bin` and `en-lemmatizer.dict.txt` in `/opt/saffron/models`; `default.json` was absent. This is evidence about the inspected image, not a claim that every deployment state is identical.
- A follow-up GET of GitHub's official release API for tag `v4.0` returned an empty uploaded `assets` array. It exposes `zipball_url` and `tarball_url` for the source snapshot; no separately uploaded model asset is listed. [SAFFRON v4.0 release API](https://api.github.com/repos/insight-centre/saffron/releases/tags/v4.0)
- The GitHub release page shows “Assets 2”; matched with the API's empty uploaded-assets array and source archive URLs, those are the automatically generated source ZIP and tarball links, not named manually uploaded classifier assets. [SAFFRON v4.0 release page](https://github.com/insight-centre/saffron/releases/tag/v4.0), [GitHub Releases API documentation](https://docs.github.com/en/rest/releases/releases?apiVersion=latest)

### Inferences
- The README's blanket first-run download note is insufficient evidence that TAXO's trained classifier is obtained automatically. The pinned TAXO source requires a readable model file at the configured path, and the inspected image had none.
- No stable official URL for a pretrained taxonomy `default.json` was found in the inspected README or pinned source/config paths.

### Gaps
- The two source archive contents were not downloaded. The v4.0 release API lists no uploaded assets, and the pinned build itself did not contain the classifier file.
- The README does not identify which particular model files its generic first-run download note refers to.

## What model format and training inputs does TAXO require?

### Takeaway
The pinned pipeline reads `default.json` into SAFFRON's `Model` class. The upstream trainer produces that model from a configuration plus term data, document-term mappings, and reviewed `.taxo` hierarchy labels; it is not shown as a zero-shot or self-training step.

### Cited Findings
- The TAXO pipeline loads `config.taxonomy.modelFile` as `org.insightcentre.nlp.saffron.data.Model`, defaulting to `${saffron.home}/models/default.json`. [SaffronPipeline.java](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/run/src/main/java/org/insightcentre/nlp/saffron/run/SaffronPipeline.java)
- The pinned `taxonomy/train` entry point invokes the supervised `Train` class. Its options include `-d` for document-term connections, `-p` for terms, `-t` for one or more taxonomies, and `-c` for configuration. Its documented example uses `food_en-doc-topics.json`, `food_en-topics.json`, and `food_en.taxo`; it serializes the resulting `Model` to the configured model path. [Train.java](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/taxonomy/src/main/java/org/insightcentre/nlp/saffron/taxonomy/supervised/Train.java), [taxonomy/train](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/taxonomy/train)
- The inspected pinned checkout contains matched `food_en` corpus, terms, document-term, and `.taxo` benchmark files; it also contains some additional `.taxo` files without a corresponding matched terms/doc-term training bundle in the listed directory. [TexEval benchmark directory](https://github.com/insight-centre/saffron/tree/bcf009f176713ced1d707324043124670827125b/benchmarks/data/texeval)
- The Fetcher runner's local validation requires the configured JSON model to contain a non-empty `classifierData` string before invoking TAXO. [Fetcher runner.py](/E:/Project%20SWP/SLR_Paper_Fetcher/docker/saffron/runner.py)

### Inferences
- The bundled `food_en` training bundle can likely produce a technically compatible SAFFRON model, but it is food-domain supervision and is not evidence of suitability for this systematic-review paper corpus. A domain fit and quality review would still be needed before using it as the product taxonomy model.
- The custom runner's `classifierData` check is a minimal structural validation; it does not prove model compatibility, domain fit, or taxonomy quality.

### Gaps
- The inspected README/release materials do not publish a taxonomy-model benchmark or suitability claim for research-paper corpora.
- No project-domain gold `.taxo` labels and matching terms/document-term files were present in the Fetcher repository during the audit.

## Do official releases or install scripts provide this classifier?

### Takeaway
The official docs inspected describe the TAXO mode and generic first-run model downloads, but do not document a taxonomy-specific downloadable classifier. The official v4.0 release API returns no uploaded release assets; its two visible links are the source ZIP and tarball, not a separate model asset.

### Cited Findings
- The pinned README documents `-k TAXO` as the option to generate a taxonomy and says first-run execution downloads required models, without naming the taxonomy model or a link for it. [Pinned README](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/README.md)
- The v4.0 release API response for `v4.0` has `assets: []`, `zipball_url: https://api.github.com/repos/insight-centre/saffron/zipball/v4.0`, and `tarball_url: https://api.github.com/repos/insight-centre/saffron/tarball/v4.0`. The release page's two “Assets” are these generated source archives; there is no named uploaded model asset. [Release API response](https://api.github.com/repos/insight-centre/saffron/releases/tags/v4.0), [Release page](https://github.com/insight-centre/saffron/releases/tag/v4.0)
- The taxonomy trainer's documented usage is the provided route for producing a model and explicitly takes the terms, document-term mapping, taxonomy labels, and configuration as inputs. [Train.java](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/taxonomy/src/main/java/org/insightcentre/nlp/saffron/taxonomy/supervised/Train.java)

### Inferences
- There is no verified official shortcut that avoids labeled training inputs for a compatible model at this pinned revision.

### Gaps
- The source archive files themselves were not downloaded or inspected; no downloadable model asset is listed in the release API.
