# NL-TPS Overleaf sources

This directory contains thirteen independent LaTeX documents derived from the
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

All thirteen documents use `nl_tps_common.sty`. The ConOps also uses the images in
`figures/`. For reliable compilation from the repository root, use these
top-level Overleaf entry points:

- `main.tex` - default combined review copy containing all thirteen documents
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

## Import from GitHub

1. In the connected Overleaf project, open **Integrations -> GitHub** and pull
   the latest GitHub changes.
2. The default `main.tex` compiles all thirteen documents in trace order: ConOps,
   the controlled ACR ROPA and ASTRO APEx applicability and traceability profile,
   High-Level Requirements, categorized High-Level Functional, Non-Functional,
   and Operational Requirements, High-Level Interface Requirements, Sub-Interface
   Requirements, Interface Component and Team Realization, categorized Functional,
   Non-Functional, and Operational Sub-Requirements and Component Realization,
   Detailed Functional Sub-Requirements, Functional Component Realization,
   the Risk and Mitigation Register, and the Trade-Off Analysis Matrices.
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
   `NL_TPS_Risk_and_Mitigation_Register_Overleaf.tex`, or
   `NL_TPS_Trade_Off_Analysis_Matrices_Overleaf.tex`.
3. Use pdfLaTeX as the compiler.
4. Recompile twice after changing headings, page counts, or the table of
   contents.

The thirteen files remain separate controlled documents. The combined suite is a
review convenience and does not merge their document-control identities. The
`.docx` files remain the source artifacts used for the initial conversion;
future substantive changes should be reconciled through document control so
the Word and LaTeX versions do not silently drift.
