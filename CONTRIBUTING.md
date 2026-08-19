# Contributing

Contributions must preserve the GCPL / NL-TPS authority boundary, stable
identifiers, traceability, and nonclinical status.

1. Work on a focused branch or managed worktree. MPS materialization uses the
   dedicated space-free worktree procedure in `README.md`.
2. Do not add PHI, patient DICOM, production credentials, tokens, signing keys,
   identifiable logs, or local user-profile paths.
3. Do not bulk-rename `NL_TPS_*` files, `nltps.*` namespaces, requirement IDs,
   or historical trace identifiers. ADR-002 preserves them.
4. Do not hand-edit MPS persistence XML. Use the MPS AST and retain model
   validation, migration, generator, and headless-build evidence.
5. Update controlled specifications, human-readable documents, traces, risks,
   and checks together when a change affects their meaning.
6. Run the structural gates and document build described in `README.md`.
7. Do not claim a V&V PASS, clinical approval, commissioning, accreditation,
   risk acceptance, or release without the required attributable evidence and
   approvals.
8. Do not commit `tmp/`, `output/`, PDFs, or LaTeX intermediates. Review PDFs
   are produced by CI under ART-POL-001.

Pull requests should describe the problem, authority and intended-use impact,
affected IDs and hazards, verification performed, residual risks, generated
diffs, and required reviewers. A passing CI run is necessary but not sufficient
for clinical, safety, quality, or release acceptance.
