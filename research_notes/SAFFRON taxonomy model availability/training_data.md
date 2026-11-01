# SAFFRON taxonomy training data and datasets

## What public benchmark and training data exist?

### Takeaway
TExEval provides useful gold taxonomies and term lists for broad benchmark domains, including Science, but it was designed primarily for taxonomy evaluation and does not provide a ready-made corpus of Saffron `doc-terms` features. The pinned Saffron checkout has one fully matched training bundle for Food; neither it nor the official TExEval packages establish a reviewed research-paper-domain training set or an immediately usable pretrained `default.json`.

### Cited Findings
- The official TExEval-2 page lists English test term lists for Environment, Food, and Science, and separately lists trial gold taxonomies such as AI, plants, and vehicles; it describes the task as unsupervised and says no training data would be provided. [SemEval-2016 Task 13 data and tools](https://alt.qcri.org/semeval2016/task13/index.php?id=data-and-tools)
- The Task 13 page explicitly tells participants not to use the resources that were used to construct the gold standards, reinforcing that those taxonomies are held-out evaluation material in the shared task rather than its training set. [SemEval-2016 Task 13](https://alt.qcri.org/semeval2016/task13/)
- TExEval-2 states that participants could use Wikipedia XML dumps and that the task starts from terms extracted from existing taxonomies; its gold taxonomies include a Science taxonomy sourced from the Taxonomy of Fields and their Subfields, alongside WordNet, EuroVoc, and Wikipedia-derived resources. [TExEval-2 paper](https://research.universityofgalway.ie/ws/portalfiles/portal/25823847/texeval2.pdf)
- The TExEval-2015 shared task supplied domain term lists and gold taxonomies for Chemicals, Equipment, Food, and Science, but its paper says no corpus was provided. [TExEval-2015 paper](https://aclanthology.org/S15-2151/)
- In the pinned Saffron checkout, the only matched term + document-term + gold-taxonomy training bundle is `food_en`: the repository contains `food_en-topics.json`, `food_en-doc-topics.json`, and `food_en.taxo`. It also contains separate `science_en.taxo`, `science_eurovoc_en.taxo`, and `science_wordnet_en.taxo` label files, but no matching `science_en-topics.json` or `science_en-doc-topics.json` in that checkout. [Pinned Saffron `food_en` terms](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/benchmarks/data/texeval/food_en-topics.json); [document terms](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/benchmarks/data/texeval/food_en-doc-topics.json); [gold taxonomy](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/benchmarks/data/texeval/food_en.taxo); [Science gold taxonomy](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/benchmarks/data/texeval/science_en.taxo)

### Inferences
- TExEval Science labels could support an exploratory benchmark or a broad-discipline baseline after the required document-term inputs are generated and vocabulary overlap is checked. The benchmark is not evidence that a model trained on it will produce useful taxonomies for this SLR corpus.
- TExEval's test/evaluation materials should not be treated as a production training set without a deliberate train/test protocol; reusing test gold labels for training would invalidate comparison against those same labels.

### Gaps
- The SemEval data page does not present a clear license for each bundled taxonomy or the source taxonomies it incorporates. Availability of a download is not enough to establish redistribution rights; verify the individual source terms before bundling or publishing derived model weights.
- ACL Anthology states that SemEval proceedings materials prior to 2016 are CC BY-NC-SA 3.0, but this does not itself establish a license for the separate TExEval dataset files or each underlying source taxonomy. [SemEval-2016 proceedings](https://aclanthology.org/S16-1000/); [Task 13 data page](https://alt.qcri.org/semeval2016/task13/index.php?id=data-and-tools)
- I found no official Saffron-hosted, research-paper-domain `default.json` model or explicit stable download for one. This is a bounded search result, not proof that no separately distributed model exists.

## What does Saffron require to train its taxonomy classifier?

### Takeaway
The pinned Saffron trainer is supervised: it consumes a configuration, a term list, document-term mappings, and one or more gold `.taxo` files, then serializes a classifier model. The most direct missing input for this SLR project is representative reviewed child–parent labels over terms that overlap the term/document corpus.

### Cited Findings
- The pinned `taxonomy/train` script launches `org.insightcentre.nlp.saffron.taxonomy.supervised.Train`; the trainer options are `-c` for config, `-p` for terms, `-d` for document-term connections, and `-t` for taxonomy label files. Its usage example names the matched food benchmark files. [Pinned trainer script](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/taxonomy/train); [pinned Train.java](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/taxonomy/src/main/java/org/insightcentre/nlp/saffron/taxonomy/supervised/Train.java)
- The trainer reads `.taxo` lines as tab-separated relation pairs and builds model features from the supplied term map and indexed document-term mappings before training the SVM. The `.taxo` format therefore supplies gold hypernym relations, while `doc-terms` supplies corpus context for features; neither alone is the full training input. [Pinned Train.java](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/taxonomy/src/main/java/org/insightcentre/nlp/saffron/taxonomy/supervised/Train.java)
- The pinned CLI pipeline defaults `taxonomy.modelFile` to `${saffron.home}/models/default.json` and reads that configured file when building TAXO; it does not train the model as part of an ordinary paper run. [Pinned SaffronPipeline.java](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/run/src/main/java/org/insightcentre/nlp/saffron/run/SaffronPipeline.java)
- The pinned taxonomy configuration describes the model file as the model to be trained, with the default path `${saffron.models}/default.json`. [Pinned FORMATS.md](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/FORMATS.md)

### Inferences
- A valid project training package needs all three aligned artifacts: term entries, document-term links from a representative corpus, and reviewed `.taxo` edges over the same vocabulary. A gold hierarchy over unrelated terms cannot by itself yield a defensible SLR-domain model.
- A user-provided model can be consumed without retraining only after checking its Saffron version/config compatibility, model JSON schema, training-domain provenance, and evaluation on held-out reviewed SLR-domain relations.

### Gaps
- The pinned source does not document a single universally acceptable minimum corpus size or number of reviewed relations for a good classifier. Quality must be measured with held-out labels and expert review.
- The exact licensing and provenance of the benchmark artifacts are not resolved by the Saffron source license or the general README.

## Are other public resources suitable enough to remove the user-data gate?

### Takeaway
The public science taxonomy resources are promising as evaluation references or an exploratory broad-discipline baseline, but the available evidence does not make them a reviewed, sufficiently relevant production training set for paper-level SLR terms. No public dataset found here removes the need for project-domain labels or a reviewed compatible model.

### Cited Findings
- TExEval-2's task authors describe Science as a hierarchy of fields and subfields rooted at “science,” with gold structures assembled from WordNet, EuroVoc, Wikipedia Bitaxonomy, and a domain-specific taxonomy. This is a broad field taxonomy, not a labeled taxonomy of arbitrary extracted terms from this SLR's papers. [TExEval-2 paper](https://research.universityofgalway.ie/ws/portalfiles/portal/25823847/texeval2.pdf)
- The official TExEval page identifies the test term archives as taxonomy-construction evaluation data and separately lists trial resources; it does not list aligned document-term mappings for Science. [SemEval-2016 Task 13 data and tools](https://alt.qcri.org/semeval2016/task13/index.php?id=data-and-tools)
- The Saffron README's note that first execution downloads “all the models needed” is generic; in the pinned image the models directory contained the English POS tagger and lemmatizer files but no taxonomy `default.json`. The taxonomy pipeline's source reads its configured model file directly. [Pinned Saffron README](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/README.md); [pinned SaffronPipeline.java](https://github.com/insight-centre/saffron/blob/bcf009f176713ced1d707324043124670827125b/run/src/main/java/org/insightcentre/nlp/saffron/run/SaffronPipeline.java)

### Inferences
- Do not train the production SLR model from the Food benchmark. The Science taxonomies might be used for a clearly labeled proof-of-concept only if the team accepts the broad-discipline mismatch and provides matching document-term features; evaluate on separate, reviewed relations before enabling it as a completed result.
- A practical next input is either (a) a reviewed Saffron 4 `default.json` with training/evaluation provenance, or (b) representative SLR-domain term lists, document-term mappings from the intended corpus, and gold `.taxo` relations reviewed by domain experts. OpenAlex topic IDs remain a separate enrichment path and do not constitute Saffron classifier training evidence.

### Gaps
- The exact corpus and research subdomain in which a future SLR model would be used were not specified in this research task, so no single external taxonomy can be judged fully relevant.
- No model was downloaded or trained, and no external dataset's license was independently cleared for deployment.
