# GCPL / NL-TPS Overleaf sources

The preferred program title is **Governed Clinical Language for AI-Assisted
Radiation Treatment Planning**, with the subtitle **A Model-Based,
Safety-Constrained Orchestration Framework**. **Governed Clinical Planning
Language (GCPL)** names the technology; **Natural-Language Treatment Planning
System (NL-TPS)** remains the implementation, repository, namespace, and legacy
trace alias. ADR-002 controls this hierarchy and prohibits an uncontrolled bulk
rename.

This directory contains eighteen independent LaTeX documents derived from the
controlled requirements artifacts in the repository:

- `NL_TPS_ConOps.tex` - Concept of Operations
- `NL_TPS_ACR_APEx_Applicability_Traceability_Matrix.tex` - controlled ACR ROPA and ASTRO APEx applicability, traceability, and proton implementation profile
- `NL_TPS_High_Level_Requirements.tex` - High-Level Requirements
- `NL_TPS_High_Level_Functional_Non_Functional_Operational_Requirements.tex` - categorized High-Level Functional, Non-Functional, and Operational Requirements
- `NL_TPS_High_Level_Interface_Requirements.tex` - High-Level Interface Requirements
- `NL_TPS_Sub_Interface_Requirements.tex` - Sub-Interface Requirements
- `NL_TPS_Interface_Component_Realization.tex` - Interface Component and Team Realization
- `NL_TPS_Functional_Non_Functional_Operational_Sub_Requirements.tex` - Functional, Non-Functional, and Operational Sub-Requirements
- `NL_TPS_Functional_Non_Functional_Operational_Component_Realization.tex` - Functional, Non-Functional, and Operational Component Realization
- `NL_TPS_Detailed_Requirements.tex` - Detailed and Subsystem Requirements
- `NL_TPS_Component_Realization.tex` - Functional Component Realization and Team-of-Teams Allocation
- `NL_TPS_Risk_and_Mitigation_Register.tex` - requirement- and component-level Risk and Mitigation Register
- `NL_TPS_Trade_Off_Analysis_Matrices.tex` - requirement- and component-level Trade-Off Analysis Matrices
- `NL_TPS_Monthly_QA_Integration_Profile.tex` - Machine QA Evidence and Readiness Integration Profile
- `NL_TPS_Verification_Validation_Check_Matrix.tex` - exhaustive requirement-, interface-, component-, and machine-QA V&V check specification
- `NL_TPS_Engineering_Architecture_and_MVP_Implementation_Plan.tex` - frozen nonclinical four-zone architecture baseline, separate typed-intent and professional-decision contracts, signed execution capability, specification-as-data migration, V&V execution model, Platform Slice 0, and staged patient-planning implementation
- `NL_TPS_ADR_001_MPS_Authority_Scope_and_Runtime_Boundary.tex` - controlled decision selecting MPS as the offline governance compiler, preserving current document authority through mirror/equivalence, excluding MPS from clinical runtime, and defining cutover and release-bundle controls
- `NL_TPS_ADR_002_Program_Identity_and_Naming_Hierarchy.tex` - controlled GCPL / NL-TPS program identity, terminology interpretation, compatibility policy, and naming propagation plan

The corresponding machine-readable architecture constraints are maintained in
`../spec/architecture.yaml` and the corresponding ADR record in
`../spec/decisions.yaml`, with controlled naming in `../spec/terminology.yaml`.
These YAML files constrain implementation and change
impact analysis; they do not supersede the controlled source requirements or
the human-reviewable engineering-plan document.

All eighteen documents use `nl_tps_common.sty`. The ConOps also uses the images in
`figures/`. For reliable compilation from the repository root, use these
top-level Overleaf entry points:

- `main.tex` - default combined review copy containing all eighteen documents
- `NL_TPS_Document_Suite_Overleaf.tex` - explicit entry point for the combined review copy
- `NL_TPS_ConOps_Overleaf.tex`
- `NL_TPS_ACR_APEx_Applicability_Traceability_Matrix_Overleaf.tex`
- `NL_TPS_High_Level_Requirements_Overleaf.tex`
- `NL_TPS_High_Level_Functional_Non_Functional_Operational_Requirements_Overleaf.tex`
- `NL_TPS_High_Level_Interface_Requirements_Overleaf.tex`
- `NL_TPS_Sub_Interface_Requirements_Overleaf.tex`
- `NL_TPS_Interface_Component_Realization_Overleaf.tex`
- `NL_TPS_Functional_Non_Functional_Operational_Sub_Requirements_Overleaf.tex`
- `NL_TPS_Functional_Non_Functional_Operational_Component_Realization_Overleaf.tex`
- `NL_TPS_Detailed_Requirements_Overleaf.tex`
- `NL_TPS_Component_Realization_Overleaf.tex`
- `NL_TPS_Risk_and_Mitigation_Register_Overleaf.tex`
- `NL_TPS_Trade_Off_Analysis_Matrices_Overleaf.tex`
- `NL_TPS_Monthly_QA_Integration_Profile_Overleaf.tex`
- `NL_TPS_Verification_Validation_Check_Matrix_Overleaf.tex`
- `NL_TPS_Engineering_Architecture_and_MVP_Implementation_Plan_Overleaf.tex`
- `NL_TPS_ADR_001_MPS_Authority_Scope_and_Runtime_Boundary_Overleaf.tex`
- `NL_TPS_ADR_002_Program_Identity_and_Naming_Hierarchy_Overleaf.tex`

## Import from GitHub

1. In the connected Overleaf project, open **Integrations -> GitHub** and pull
   the latest GitHub changes.
2. The default `main.tex` compiles all eighteen documents in trace order: ConOps,
   the controlled ACR ROPA and ASTRO APEx applicability and traceability profile,
   High-Level Requirements, categorized High-Level Functional, Non-Functional,
   and Operational Requirements, High-Level Interface Requirements, Sub-Interface
   Requirements, Interface Component and Team Realization, categorized Functional,
   Non-Functional, and Operational Sub-Requirements and Component Realization,
   Detailed Functional Sub-Requirements, Functional Component Realization,
   the Risk and Mitigation Register, the Trade-Off Analysis Matrices, the Machine
   QA Evidence and Readiness Integration Profile, the Verification and
   Validation Check Matrix, and the Engineering Architecture and Minimum Viable
   Clinical Slice Implementation Plan, ADR-001 for the MPS Authority, Scope,
   and Runtime Boundary, and ADR-002 for Program Identity and Naming Hierarchy.
   To compile one controlled document by itself, open
   **Settings -> Compiler -> Main document** and select
   `NL_TPS_ConOps_Overleaf.tex`,
   `NL_TPS_ACR_APEx_Applicability_Traceability_Matrix_Overleaf.tex`,
   `NL_TPS_High_Level_Requirements_Overleaf.tex`,
   `NL_TPS_High_Level_Functional_Non_Functional_Operational_Requirements_Overleaf.tex`,
   `NL_TPS_High_Level_Interface_Requirements_Overleaf.tex`,
   `NL_TPS_Sub_Interface_Requirements_Overleaf.tex`,
   `NL_TPS_Interface_Component_Realization_Overleaf.tex`,
   `NL_TPS_Functional_Non_Functional_Operational_Sub_Requirements_Overleaf.tex`,
   `NL_TPS_Functional_Non_Functional_Operational_Component_Realization_Overleaf.tex`,
   `NL_TPS_Detailed_Requirements_Overleaf.tex`,
   `NL_TPS_Component_Realization_Overleaf.tex`,
   `NL_TPS_Risk_and_Mitigation_Register_Overleaf.tex`,
   `NL_TPS_Trade_Off_Analysis_Matrices_Overleaf.tex`,
   `NL_TPS_Monthly_QA_Integration_Profile_Overleaf.tex`,
   `NL_TPS_Verification_Validation_Check_Matrix_Overleaf.tex`,
   `NL_TPS_Engineering_Architecture_and_MVP_Implementation_Plan_Overleaf.tex`,
   `NL_TPS_ADR_001_MPS_Authority_Scope_and_Runtime_Boundary_Overleaf.tex`, or
   `NL_TPS_ADR_002_Program_Identity_and_Naming_Hierarchy_Overleaf.tex`.
3. Use pdfLaTeX as the compiler.
4. Recompile twice after changing headings, page counts, or the table of
   contents.

The eighteen files remain separate controlled documents. The combined suite is a
review convenience and does not merge their document-control identities. The
`.docx` files remain the source artifacts used for the initial conversion;
future substantive changes should be reconciled through document control so
the Word and LaTeX versions do not silently drift.
