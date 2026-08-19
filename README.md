# Governed Clinical Planning Language / NL-TPS

**Governed Clinical Planning Language (GCPL)** is the governed semantic and
orchestration method. **Natural-Language Treatment Planning System (NL-TPS)**
is its current implementation, repository, namespace, and historical trace
alias. The preferred descriptive title is *Governed Clinical Language for
AI-Assisted Radiation Treatment Planning: A Model-Based, Safety-Constrained
Orchestration Framework*.

This repository is a controlled, nonclinical engineering workspace. It does
not provide an autonomous treatment planner, a commissioned dose authority, a
clinical approval mechanism, or authorization for patient use. Qualified
radiation oncologists, medical physicists, dosimetrists, therapists, and other
assigned professionals retain their institutional authority.

## Current authority and implementation stage

- ADR-001 places JetBrains MPS in an **offline governance-compiler** role.
- The project remains at **Stage A - mirror**. The controlled human-readable
  documents remain authoritative.
- ENG-PKG-01 is a frozen nonclinical implementation baseline with
  `approval_state: pending_named_approval` and no recorded approvals.
- MPS is not in the clinical runtime path and may not contain patient data,
  clinical credentials, signing keys, or approval records.
- Stage C authority cutover and every clinical or governed release remain
  blocked until their named approvals and evidence exist.

## Repository map

- `overleaf/` - editable controlled LaTeX documents.
- root `*_Overleaf.tex` files - standalone Overleaf entry points.
- `main.tex` - combined nineteen-document review suite.
- `spec/` - machine-readable Stage A specifications, policies, schemas, risks,
  traces, quality targets, and defect dispositions.
- `mps/` - ADR-001 MPS blueprint, deterministic mirrors, and materialization
  handoff. It is not live MPS serialization.
- `tools/` and `scripts/` - deterministic generation, checking, compilation,
  migration, and manifest utilities.
- `tests/` - tooling regression tests.
- `archive/legacy-docx/` - non-authoritative historical Word inputs.
- `tmp/` and `output/` - ignored local build products.

## Local structural checks

The Python checkers require the dependency locked in `requirements-ci.txt`.
The current development environment already contains it.

```powershell
python -m unittest discover -s tests -v
python tools/mps/build_hlr_import_bundle.py --check
python tools/mps/check_language_skeleton.py
python tools/spec/build_trace_graph.py --check
python tools/spec/build_risk_register.py --check --gate 0
python tools/spec/check_controlled_specs.py
python tools/spec/check_approval_state.py --stage A
python tools/repo/check_repository_hygiene.py
scripts/generate_vv_check_matrix.ps1 -Check
```

Gate 1 is expected to fail until the 119 HLR risk scores and applicable
quantitative quality targets receive accountable approval. Stage C and release
approval checks are also expected to fail while approval arrays are empty.

## Document builds and artifacts

With pdfLaTeX and Poppler available:

```powershell
python tools/docs/compile_controlled_docs.py
python tools/release/build_pdf_manifest.py --release-status review
```

Generated PDFs are not source-controlled. CI compiles the nineteen standalone
documents and combined suite, creates a provenance manifest, and publishes them
as an explicit review artifact. A governed release requires a clean commit,
approved release state, independent verification, and an approved release
decision.

## MPS worktree requirement

Do not materialize MPS inside the active OneDrive checkout or any path with
whitespace. After committing or stashing all work, create a managed Git
worktree on the dedicated materialization branch:

```powershell
scripts/create_mps_worktree.ps1 -Destination C:\src\gcpl-mps
```

The script preserves the controlling Git history, verifies that the worktree
shares the same Git common directory, and does not delete the original checkout.

## Data and security boundary

Do not commit or process protected health information, patient DICOM objects,
credentials, private keys, tokens, or identifiable local build logs. Use only
approved synthetic or de-identified nonclinical fixtures under an authorized
protocol. See `SECURITY.md`.

## Licensing status

No open-source or other reuse license has been granted. See `NOTICE.md`. A
license must be selected explicitly by the repository owner before downstream
reuse or distribution is represented as authorized.
