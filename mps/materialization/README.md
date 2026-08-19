# Stage A MPS materialization handoff

This directory is a controlled handoff for creating the live JetBrains MPS
project. It is not MPS persistence and does not claim that the four languages,
importer, generators, constraints, editors, or model tests exist.

## Preconditions

1. Commit or stash the current repository work and pass all structural gates.
2. Create the managed, space-free, non-OneDrive worktree with
   `scripts/create_mps_worktree.ps1`.
3. Pin the approved MPS 2026.1 build and plugin set for the experiment.
4. Use synthetic nonclinical content only. No patient data, clinical
   credentials, signing keys, or production endpoints are permitted.
5. Confirm ENG-PKG-01, ADR-001, and ADR-002 remain at explicit Stage A approval
   state. Stage A work does not require or imply Stage C approval.

## Materialization sequence

1. Create `NLTPSGovernance` through the MPS UI or model-aware API. Never author
   MPS persistence XML as text.
2. Create the four language modules in controlled order:
   `nltps.foundation`, `nltps.governance`, `nltps.clinicalintent`, and
   `nltps.realization`.
3. Apply the exact dependency graph, root concepts, non-root concepts,
   constraints, typesystems, editors, and generator boundaries defined in
   `mps/bootstrap/language-skeleton.json`.
4. Configure file-per-root persistence for normative root models.
5. Implement the neutral HLR importer against
   `mps/import/hlr-baseline.schema.json`; import all 119 HLR roots without
   normalizing or rewriting their normative text.
6. Add negative model tests for invalid trace direction, incompatible units,
   duplicate ownership, missing authority, unsupported release scope, and A4
   authority encoded in AI-creatable intent.
7. Add deterministic neutral export and compare it with the controlled input by
   ID, exact text, domain count, source hash, record hash, and approval state.
8. Run model validation and the headless build without the experimental agent
   toolkit, retain the evidence, and submit the Stage B equivalence report.

## Acceptance boundary

The materialization is complete only when every item in
`stage-a-checklist.yaml` has attributable evidence and independent review. It
does not move authority from the controlled documents. Stage C remains blocked
until its separately approved cutover record and named approvals exist.
