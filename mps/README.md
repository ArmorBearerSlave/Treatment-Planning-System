# NL-TPS MPS governance compiler

This directory implements the repository-side bootstrap for ADR-001. JetBrains
MPS is the proposed offline governance compiler. It is not a clinical runtime
dependency, a patient-data store, a dose engine, an approval authority, or a
system of record.

Current authority stage: **Stage A - mirror**. The existing controlled source
documents remain authoritative. Nothing under this directory completes the
Stage C governance cutover.

## Contents

- `bootstrap/language-skeleton.json` defines the four initial language modules,
  dependency direction, first concepts, generators, and model tests.
- `bootstrap/agent-materialization.md` is the controlled procedure for creating
  the skeleton through the live MPS AST. It expressly prohibits hand-editing
  `.mps` persistence XML.
- `import/hlr-baseline.schema.json` defines the neutral import-bundle contract.
- `import/hlr-baseline.json` is generated from the controlled 119-HLR LaTeX
  source by `tools/mps/build_hlr_import_bundle.py`.
- `import/README.md` defines the MPS-side import and equivalence behavior.

The bootstrap JSON is an implementation specification, not MPS serialization.
The live MPS project must be materialized by MPS itself, using its UI or
model-aware tools, and then reviewed. This avoids brittle direct edits to MPS
persistence.

## Local checks

No third-party Python package is required.

```powershell
python tools/mps/check_language_skeleton.py
python tools/mps/build_hlr_import_bundle.py --check
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
spaces. Agent-assisted live-model work therefore requires an approved,
space-free working path that preserves this Git history. Do not create an
unmanaged copy and do not place patient data or clinical credentials in the
MPS workspace.
