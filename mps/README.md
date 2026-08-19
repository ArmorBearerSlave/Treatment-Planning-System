# GCPL / NL-TPS MPS governance compiler

This directory implements the repository-side bootstrap for ADR-001 and the
naming hierarchy in ADR-002. Governed Clinical Planning Language (GCPL) names
the technology; NL-TPS remains the implementation and namespace alias.
JetBrains MPS is the proposed offline governance compiler. It is not a clinical runtime
dependency, a patient-data store, a dose engine, an approval authority, or a
system of record.

Current authority stage: **Stage A - mirror**. The existing controlled source
documents remain authoritative. Nothing under this directory completes the
Stage C governance cutover.

Current engineering baseline: **ENG-PKG-01 v0.6**. Its machine-readable
constraints come from `spec/architecture.yaml` and `spec/terminology.yaml`;
the import and skeleton checkers reject a baseline mismatch.

## Contents

- `bootstrap/language-skeleton.json` defines the four initial language modules,
  dependency direction, disjoint root/non-root concept collections, generators,
  and model tests.
- `bootstrap/language-skeleton.schema.json` enforces the unambiguous blueprint
  collection contract.
- `bootstrap/agent-materialization.md` is the controlled procedure for creating
  the skeleton through the live MPS AST. It expressly prohibits hand-editing
  `.mps` persistence XML.
- `import/hlr-baseline.schema.json` defines the neutral import-bundle contract.
- `import/hlr-baseline.json` is generated from the controlled 119-HLR LaTeX
  source by `tools/mps/build_hlr_import_bundle.py`.
- `import/README.md` defines the MPS-side import and equivalence behavior.
- `materialization/` defines the pending managed-worktree procedure and Stage A
  evidence checklist; it is not live MPS serialization.

The bootstrap JSON is an implementation specification, not MPS serialization.
The live MPS project must be materialized by MPS itself, using its UI or
model-aware tools, and then reviewed. This avoids brittle direct edits to MPS
persistence.

## Local checks

The checkers require Python and the PyYAML version locked in
`requirements-ci.txt`. The active development environment already provides
that dependency; no installation was performed for this corrective action.

```powershell
python tools/mps/check_language_skeleton.py
python tools/mps/build_hlr_import_bundle.py --check
python tools/spec/check_controlled_specs.py
```

To regenerate the deterministic mirror after an approved source change:

```powershell
python tools/mps/build_hlr_import_bundle.py
python tools/mps/build_hlr_import_bundle.py --check
```

Regeneration is not authority migration. Review the source change, generated
diff, import report, and ADR-001 transition controls.

## MPS agent-tooling constraint

The MPS 2026.1 Projectional Agent Toolkit is experimental and currently fails
when any open project path contains a space. This repository path contains
spaces. Agent-assisted live-model work therefore requires the managed,
space-free Git worktree created by `scripts/create_mps_worktree.ps1`. Do not
create an unmanaged copy and do not place patient data or clinical credentials
in the MPS workspace.
