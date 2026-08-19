# Controlled MPS materialization procedure

This procedure converts `language-skeleton.json` into a live MPS project. It is
an engineering procedure under ADR-001, not a clinical-use authorization.

## Preconditions

1. Use the pinned MPS version named in the approved work record.
2. Use an approved space-free project path when the Projectional Agent Toolkit
   is involved. The current repository path contains spaces and cannot be used
   directly with the documented MPS 2026.1 toolkit limitation.
3. Use synthetic, non-patient content only. Do not expose clinical credentials,
   signing keys, or production endpoints.
4. Start from a reviewed Git branch and record the baseline commit.

## Structural actions

Perform these operations through the MPS UI or model-aware `mps_mcp_*` tools:

1. Create project `NLTPSGovernance`.
2. Create languages, in order:
   `nltps.foundation`, `nltps.governance`, `nltps.clinicalintent`, and
   `nltps.realization`.
3. Configure dependencies exactly as stated in `language-skeleton.json`.
4. Create only the initial concepts, root concepts, constrained data types,
   enumerations, and references allocated to each language.
5. Create the minimum editors needed to review identifiers, normative text,
   relationship endpoints, status, version, rationale, and provenance.
6. Add constraints and typesystem rules before generators.
7. Set normative instance models to file-per-root persistence.
8. Add node/constraint, typesystem, generator, and migration test models.
9. Add a solution for the HLR importer and import the generated
   `../import/hlr-baseline.json` as non-authoritative Stage A mirror roots.
10. Generate, check models, run tests, and record the complete result.

## Prohibited actions

- Do not create or modify `.mps`, `.mpl`, `.msd`, `.mpr`, or related MPS
  persistence XML with a text editor or patch tool.
- Do not import patient data or patient-specific PlanIntent instances.
- Do not make the imported mirror authoritative.
- Do not generate or publish a clinical release bundle.
- Do not let an agent approve, suppress, or disposition its own findings.

## Review evidence

Capture the MPS/toolchain versions, model/module inventory, dependency report,
model-check output, test results, generated-artifact diff, import counts,
source hash, and Git diff. A reviewer must compare these with ADR-001 and the
bootstrap manifest before accepting the live skeleton.
