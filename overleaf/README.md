# NL-TPS Overleaf sources

This directory contains two independent LaTeX documents derived from the
controlled Word artifacts in the repository root:

- `NL_TPS_ConOps.tex` - Concept of Operations
- `NL_TPS_High_Level_Requirements.tex` - High-Level Requirements

Both documents use `nl_tps_common.sty`. The ConOps also uses the images in
`figures/`. For reliable compilation from the repository root, use these
top-level Overleaf entry points:

- `main.tex` - default entry point for the ConOps
- `NL_TPS_ConOps_Overleaf.tex`
- `NL_TPS_High_Level_Requirements_Overleaf.tex`

## Import from GitHub

1. In the connected Overleaf project, open **Integrations -> GitHub** and pull
   the latest GitHub changes.
2. The default `main.tex` compiles the ConOps. To compile the requirements
   baseline, open **Settings -> Compiler -> Main document** and select
   `NL_TPS_High_Level_Requirements_Overleaf.tex`.
3. Use pdfLaTeX as the compiler.
4. Recompile twice after changing headings, page counts, or the table of
   contents.

The two files are intentionally separate controlled documents. Select one as
the main document at a time. The `.docx` files remain the source artifacts used
for the initial conversion; future substantive changes should be reconciled
through document control so the Word and LaTeX versions do not silently drift.
