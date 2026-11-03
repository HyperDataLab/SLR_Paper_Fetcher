# QA-04 Approval Dependency Analysis

**Status:** Readiness analysis only. All AS-OD decisions remain OPEN.  
**MVP:** Unchanged from QA-02 and the QA-03 roadmap.

## How to read blockers

- **Hard decision blocker:** A dependent contract, implementation stage, or publication gate cannot safely proceed until the decision is resolved.
- **Deferrable decision:** The Product Owner may explicitly choose DEFERRED for a capability outside MVP. That removes the capability from the MVP contract; it does not authorize implementing the deferred feature.
- **OPEN is not DEFERRED:** Until an authorized human records an outcome, dependent work remains blocked.
- **Governance gate:** QA-03 places approved requirements and evaluation design before DB-01. A choice may not change a database field directly but can still block roadmap entry until the gate is satisfied.

## Stage-by-stage decision dependencies

### Canonical sentence source indexing — AS-SRC-001

- **Hard blockers:** AS-OD-10 evidence/source-span contract; AS-OD-11 language and segmentation boundary; AS-OD-14 source/mapping/segmenter identity and stale rules.
- **Contract dependency:** AS-OD-04 must retain uncertainty preservation in downstream content rules. Its separate classifier/cue/scope outputs are not source-index requirements.
- **Deferrable:** AS-OD-05–08 can be explicitly DEFERRED without violating the source-index MVP. Their annotation outputs must then stay out of this stage.
- **Why:** Source units, text representation, token/segment boundaries, and stale invalidation need stable meaning before candidate IDs or offsets exist.
- **Canonical tickets:** AS-GOV-002, AS-DATA-001/002, AS-API-002, AS-SRC-001, AS-QA-004.

### Candidate extraction and atomization — AS-AI-001/002

- **Hard blockers:** AS-OD-03 role mapping; AS-OD-04 uncertainty-preservation versus separate task boundary; AS-OD-10 evidence cardinality; AS-OD-11 language/tokenizer; AS-OD-13 origin policy for reported prior work.
- **Model evaluation blockers:** AS-OD-15 gold-set plan and AS-OD-16/17 metric/target status before quality claims or release.
- **Deferrable:** AS-OD-05–08 can be explicitly DEFERRED; no sentence uncertainty, cue/scope, stance/engagement, or metadiscourse labels should be emitted in MVP.
- **Why:** Extraction needs inclusion/role/origin rules; atomization needs a stable 25-word convention and evidence/context representation. Full linguistic annotations are not prerequisites for preserving uncertainty in generated text.
- **Canonical tickets:** AS-AI-001/002, AS-SRC-001, AS-QA-001/002/003.

### Context completion and precheck — AS-AI-003/004

- **Hard blockers:** AS-OD-02 lifecycle after failure; AS-OD-03 allowed role/origin values; AS-OD-04 semantic-preservation behavior; AS-OD-10 context-evidence links; AS-OD-11 word counting; AS-OD-14 invalidation when the item/source changes.
- **Human handoff dependency:** AS-OD-01/12 are hard before verification actions can be offered, but not before a non-publishing precheck can run.
- **Deferrable:** AS-OD-05–08 can be explicitly DEFERRED; precheck still needs to flag changed or dropped uncertainty as a meaning-preservation error.
- **Why:** Model findings must attach to an exact item/source version and cannot become verification.
- **Canonical tickets:** AS-AI-003/004, AS-DATA-003, AS-API-003/004, AS-QA-001/002/003.

### Human verification — AS-API-004 and AS-UI-003

- **Hard blockers:** AS-OD-01 reviewer count; AS-OD-02 actions/lineage; AS-OD-09 quality/SPS behavior; AS-OD-10 evidence presentation; AS-OD-11 length rule; AS-OD-12 trusted identity; AS-OD-14 stale-source validity.
- **Required content rules:** AS-OD-03 role mapping and AS-OD-04 uncertainty preservation must be reviewable; AS-OD-13 source-origin meaning must be visible.
- **Deferrable:** AS-OD-05–08 may be DEFERRED; the reviewer workspace must not suggest those annotations exist.
- **Why:** Verification is a human publication gate and must identify who reviewed which item against which source version.
- **Canonical tickets:** AS-API-004, AS-UI-002/003, AS-DATA-003, AS-QA-005/006.

### Verified library publication — AS-LIB-001

- **Hard blockers:** AS-OD-01 verifier policy; AS-OD-09 required quality fields/fallback; AS-OD-10 evidence; AS-OD-11 length/language eligibility; AS-OD-12 identity; AS-OD-13 reported-prior treatment; AS-OD-14 stale/superseded eligibility.
- **Required content rules:** AS-OD-03 and AS-OD-04 determine correct visible role/origin and semantic fidelity.
- **Deferrable:** AS-OD-05–08 can be DEFERRED; no library filters/counts for those labels are required.
- **Why:** A default verified result must mean a human-approved item linked to current evidence, with its evidence origin correctly represented.
- **Canonical tickets:** AS-API-004, AS-DATA-003, AS-LIB-001, AS-QA-005/006.

### Search and JSON/CSV export — AS-LIB-001/002

- **Hard blockers:** AS-OD-10 source/evidence links; AS-OD-11 language/tokenizer representation; AS-OD-12 access; AS-OD-13 origin display/filter; AS-OD-14 current/stale rules.
- **Additional contract dependency:** AS-OD-09 determines whether manual quality review data/score appears in export. AS-OD-03 fixes role values.
- **Deferrable:** AS-OD-05–08 may be DEFERRED; do not export unimplemented advanced labels.
- **Why:** Exports are PRD P0 and must not strip evidence, source origin, source version, or reviewer provenance.
- **Canonical tickets:** AS-LIB-001/002, AS-API-004, AS-DATA-003, AS-QA-005.

### Gold-set construction and evaluation — AS-QA-001/002/003

- **Hard blockers:** AS-OD-03 role mapping; AS-OD-04 semantic-preservation scope; AS-OD-10 evidence rules; AS-OD-11 language; AS-OD-15 sample/adjudication plan; AS-OD-16 metric definitions and threshold policy; AS-OD-17 status of PRD targets/runtime.
- **Conditionally relevant:** AS-OD-05–08 are only required if their label families are approved for evaluation. If DEFERRED, they are excluded from the MVP gold set.
- **Why:** Annotators cannot create consistent references while labels, sample, language, or denominators are unsettled. Model release claims need held-out human references.
- **Canonical tickets:** AS-QA-001/002/003; AS-AI-001–004.

### DB-01 database design — AS-DATA-001

- **Hard data-contract blockers:** AS-OD-01 reviewer/quorum fields; AS-OD-02 lifecycle/lineage; AS-OD-03 roles; AS-OD-09 FR-10 quality/SPS representation; AS-OD-10 evidence cardinality; AS-OD-11 tokenizer/language metadata; AS-OD-12 identity; AS-OD-14 source-version/stale rules.
- **Library-related blocker in the QA-03 backlog:** AS-OD-13 reported-prior behavior must be resolved enough to design origin-aware retrieval/export; the PRD's origin field itself remains mandatory regardless.
- **Scope gate:** Explicitly resolve AS-OD-04–08 as included or DEFERRED so optional annotation fields are not accidentally built into the MVP.
- **Roadmap/governance gate:** QA-03 M1 places approved evaluation design and target status before M2/DB-01. AS-OD-15–17 therefore require an explicit outcome for roadmap entry, even where they do not determine a core table field.
- **Why:** The existing SQLite store is reusable, but the data meaning for review, evidence, SPS, versioning, and library membership is not settled.
- **Canonical tickets:** AS-GOV-001/002, AS-DATA-001, AS-QA-001/002.

## Hard blockers vs decisions safely deferred from MVP

| Decision(s) | Can be DEFERRED without violating MVP? | Required effect if deferred |
|---|---|---|
| AS-OD-01 reviewer count | No, not for publication | Select an operational review rule before verification/library release. Gold-set double annotation remains separate. |
| AS-OD-02 revision action | A separate revision action can be deferred | Approve PRD reject-and-regenerate behavior before review workflow. |
| AS-OD-03 role mapping | No, not for role-labeled MVP outputs | Use only four PRD roles and approve their mapping examples. |
| AS-OD-04 hedge scope | Full sentence/cue/scope subsystem can be deferred | Preserve uncertainty/modality semantically in all atoms and precheck; approve that boundary. |
| AS-OD-05 sentence uncertainty | Yes | No sentence classifier or uncertainty filter in MVP. |
| AS-OD-06 stance/engagement | Yes | No Hyland label family in MVP. |
| AS-OD-07 metadiscourse scope | Yes | No metadiscourse annotation in MVP. |
| AS-OD-08 metadiscourse lens/method | Yes, with OD-07 | No model/method selection or related output in MVP. |
| AS-OD-09 SPS | No, not without handling FR-10 | Obtain appendix or approve manual/versioned fields; do not invent rubric or omit P0 silently. |
| AS-OD-10 evidence cardinality | No, not for data/review design | Approve one or multiple spans and context support semantics. |
| AS-OD-11 language/tokenizer | No, not for source index/length gate | Approve launch language and the exact 25-word convention. |
| AS-OD-12 reviewer identity | No, not for human verification | Select a trusted identity and authorization source. |
| AS-OD-13 reported-prior policy | Can be deferred until library design, not lost | The evidence-origin value is still stored; resolve default inclusion/filter behavior before LIB/search/export. |
| AS-OD-14 stale source | No, not for current-source verification | Define version identity, invalidation, and re-review behavior. |
| AS-OD-15 gold set | Can be deferred for non-evaluated source-index work | Must be resolved before gold annotation and validated AI release. QA-03 roadmap includes its protocol in M1. |
| AS-OD-16 thresholds | Pilot thresholds can be deferred as release gates | Define metrics/denominators before model evaluation; retain PRD process gates. |
| AS-OD-17 target status | Yes for DB schema; no for target claims | Measure provisionally; do not claim approval/achievement or use as gates without approval. QA-03 M1 still requires explicit status before roadmap entry. |

## Current readiness implications

- All decisions are OPEN, so AS-GOV-002 cannot be completed.
- The QA-03 backlog remains correct: AS-GOV-001 is READY FOR REVIEW; all other tickets remain BLOCKED; none is READY FOR IMPLEMENTATION.
- DB-01 remains blocked by open data-contract choices and the QA-03 M1 governance gate.
- A decision may be marked DEFERRED only after an authorized human explicitly selects that status. A draft recommendation to defer OD-05–08 is not enough.
