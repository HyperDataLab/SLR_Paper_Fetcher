# QA-04 Approval Responsibility Matrix

**Status:** Proposed routing only. No approval or delegation is recorded here.  
**Approval statuses:** The decision register remains OPEN for all 17 decisions.

## Authority boundary

QA-04 explicitly asks the Product Owner and Research Lead to review and explicitly approve, reject, or request changes. QA-02's decision proposal requests Product Owner approval across AS-OD-01–17 and calls out Research Lead review/approval for selected research and evaluation decisions.

The existing documents do not identify the named individuals, specify a formal delegation policy, or assign the backlog/technical lead roles. Therefore:

- Product Owner is the requested decision authority for all 17 product choices, subject to confirming the person's identity.
- Research Lead co-approval is explicitly requested by QA-02 for AS-OD-09, AS-OD-15, and AS-OD-16. AS-OD-03 has Research Lead review recommended, but co-approval authority is not explicit.
- No decision is Research Lead-only; the choices define product scope or workflow.
- Backlog Owner acceptance applies to adopting the canonical AS-AREA-### identifiers, not to the 17 product decisions.
- Technical Lead confirmation is a feasibility/impact review, not authority to approve product policy.
- Where the responsible role or required co-signature is unclear, the matrix says NEEDS OWNER CONFIRMATION.

## Responsibility by decision

| Decision | Product Owner | Research Lead | Technical Lead confirmation | Responsibility note |
|---|---|---|---|---|
| AS-OD-01 Reviewer count | Approval requested | Consult on gold-set distinction; not operational quorum unless delegated | No | Confirm whether operational quorum is Product Owner-only. |
| AS-OD-02 Revision action | Approval requested | No | Review lifecycle/API consequences if assigned | Technical review does not choose the product action. |
| AS-OD-03 Role mapping | Approval requested | Annotation-guide review requested | No | Research Lead co-approval authority: NEEDS OWNER CONFIRMATION. |
| AS-OD-04 Hedge scope | Approval requested | Consult if a separate research task is considered | Review scope impacts if assigned | Approval needed to preserve the MVP boundary; full detector can be deferred. |
| AS-OD-05 Sentence uncertainty | Approval requested | Consult only if classification is brought into scope | No | Product Owner may explicitly defer the label. |
| AS-OD-06 Stance/engagement | Approval requested | Consult on any future taxonomy | No | Research Lead authority for a future extension: NEEDS OWNER CONFIRMATION. |
| AS-OD-07 Metadiscourse scope | Approval requested | Consult on future research-only use | No | Product scope decision; no framework is selected if deferred. |
| AS-OD-08 Metadiscourse lens/method | Approval requested for deferral/scope | Recommend future lens/method if feature is approved | No | Final framework authority for future work: NEEDS OWNER CONFIRMATION. |
| AS-OD-09 SPS | Approval requested | Rubric/fallback approval requested | Confirm implementation feasibility if assigned | QA-02 requests both for an approved rubric/fallback; exact joint-signoff process should be confirmed. |
| AS-OD-10 Evidence cardinality | Approval requested | No | Confirm persistence/display feasibility | Technical Lead confirms consequences, not the allowed evidence policy. |
| AS-OD-11 Language/tokenizer | Approval requested | Consult on research corpus language | Confirm tokenizer/segmenter feasibility | Confirm Technical Lead identity/authority; Product Owner selects launch scope. |
| AS-OD-12 Reviewer identity | Approval requested | No | Confirm existing auth/identity feasibility and security implications | Security/Technical Lead authority is NEEDS OWNER CONFIRMATION. |
| AS-OD-13 Reported prior work | Approval requested | Consult on evidence interpretation | No | Product Owner decides library/search semantics. |
| AS-OD-14 Stale source | Approval requested | No | Confirm source-version and invalidation feasibility | Technical Lead confirms integrity mechanics. |
| AS-OD-15 Gold set | Approval requested | Approval requested | Confirm technical availability of source/mapping fixtures if assigned | QA-02 requests both Product Owner and Research Lead approval. |
| AS-OD-16 Metrics/thresholds | Approval requested for release gates | Approval requested for metric definitions/protocol | Confirm feasibility/observability if assigned | QA-02 requests Product Owner and Research Lead decisions; formal co-signature rule should be confirmed. |
| AS-OD-17 PRD targets/runtime | Approval requested for gate status | Review metric interpretation | Confirm benchmark conditions/runtime feasibility | Product Owner decides whether targets gate release; technical review cannot certify unmeasured performance. |

## Responsibility groupings

### Product Owner approval requested

All decisions AS-OD-01 through AS-OD-17 require an explicit Product Owner outcome under the QA-02 approval checklist and this task's objective. No approval is assumed until the Product Owner identity is confirmed and an outcome is recorded.

### Product Owner and Research Lead approval requested

- **AS-OD-09:** SPS rubric/fallback, because field meaning and scoring provenance must not be invented.
- **AS-OD-15:** Gold-set composition, annotation staffing, and adjudication protocol.
- **AS-OD-16:** Evaluation definitions and release thresholds.

QA-02 also requests Research Lead review for AS-OD-03. Whether that review is a formal co-approval is **NEEDS OWNER CONFIRMATION**.

### Research Lead approval only

None of the 17 decisions is Research Lead-only under the available documents. Product scope, release policy, and publication rules remain Product Owner decisions.

### Backlog Owner acceptance

The Backlog Owner should accept the proposed AS-AREA-### format and crosswalk in qa03-task-id-reconciliation.md before tickets are copied into a planning system. This is not one of AS-OD-01–17. The Backlog Owner identity and whether this role can accept the namespace are **NEEDS OWNER CONFIRMATION**.

### Technical Lead confirmation

Request feasibility review for:

- AS-OD-02 state and lineage implications.
- AS-OD-09 manual quality-field representation and score provenance.
- AS-OD-10 multi-span persistence/display.
- AS-OD-11 tokenizer and segmentation feasibility.
- AS-OD-12 available trusted identity boundary.
- AS-OD-14 PDF/mapping/segmenter version invalidation.
- AS-OD-17 benchmark conditions and instrumentation.

These checks can identify cost, risk, or infeasibility; they do not approve a product choice. The Technical Lead's identity and decision authority are **NEEDS OWNER CONFIRMATION**.

## Approval record responsibilities

- The approver records their own identity and timestamp; an editor may transcribe an explicit human response but must not infer either.
- If both Product Owner and Research Lead approvals are required, record separate identities/timestamps and the selected option. Do not mark APPROVED until both required outcomes agree.
- If approvers disagree, record NEEDS REVISION or keep OPEN pending resolution; do not select an option on their behalf.
- A Backlog Owner can accept identifier mapping only; a Technical Lead can confirm feasibility only unless an explicit delegation is recorded.
