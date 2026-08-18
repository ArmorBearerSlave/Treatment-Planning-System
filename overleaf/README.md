# NL-TPS Overleaf sources

This directory contains seven independent LaTeX documents derived from the
controlled requirements artifacts in the repository:

- `NL_TPS_ConOps.tex` - Concept of Operations
- `NL_TPS_High_Level_Requirements.tex` - High-Level Requirements
- `NL_TPS_High_Level_Interface_Requirements.tex` - High-Level Interface Requirements
- `NL_TPS_Sub_Interface_Requirements.tex` - Sub-Interface Requirements
- `NL_TPS_Interface_Component_Realization.tex` - Interface Component and Team Realization
- `NL_TPS_Detailed_Requirements.tex` - Detailed and Subsystem Requirements
- `NL_TPS_Component_Realization.tex` - Functional Component Realization and Team-of-Teams Allocation

All seven documents use `nl_tps_common.sty`. The ConOps also uses the images in
`figures/`. For reliable compilation from the repository root, use these
top-level Overleaf entry points:

- `main.tex` - default combined review copy containing all seven documents
- `NL_TPS_Document_Suite_Overleaf.tex` - explicit entry point for the combined review copy
- `NL_TPS_ConOps_Overleaf.tex`
- `NL_TPS_High_Level_Requirements_Overleaf.tex`
- `NL_TPS_High_Level_Interface_Requirements_Overleaf.tex`
- `NL_TPS_Sub_Interface_Requirements_Overleaf.tex`
- `NL_TPS_Interface_Component_Realization_Overleaf.tex`
- `NL_TPS_Detailed_Requirements_Overleaf.tex`
- `NL_TPS_Component_Realization_Overleaf.tex`

## Import from GitHub

1. In the connected Overleaf project, open **Integrations -> GitHub** and pull
   the latest GitHub changes.
2. The default `main.tex` compiles all seven documents in trace order: ConOps,
   High-Level Requirements, High-Level Interface Requirements, Sub-Interface
   Requirements, Interface Component and Team Realization, Detailed Functional
   Sub-Requirements, and Functional Component Realization. To compile one controlled document by itself, open
   **Settings -> Compiler -> Main document** and select
   `NL_TPS_ConOps_Overleaf.tex`,
   `NL_TPS_High_Level_Requirements_Overleaf.tex`,
   `NL_TPS_High_Level_Interface_Requirements_Overleaf.tex`,
   `NL_TPS_Sub_Interface_Requirements_Overleaf.tex`,
   `NL_TPS_Interface_Component_Realization_Overleaf.tex`,
   `NL_TPS_Detailed_Requirements_Overleaf.tex`, or
   `NL_TPS_Component_Realization_Overleaf.tex`.
3. Use pdfLaTeX as the compiler.
4. Recompile twice after changing headings, page counts, or the table of
   contents.

The seven files remain separate controlled documents. The combined suite is a
review convenience and does not merge their document-control identities. The
`.docx` files remain the source artifacts used for the initial conversion;
future substantive changes should be reconciled through document control so
the Word and LaTeX versions do not silently drift.
