# NL-TPS Overleaf sources

This directory contains two independent LaTeX documents derived from the
controlled Word artifacts in the repository root:

- `NL_TPS_ConOps.tex` - Concept of Operations
- `NL_TPS_High_Level_Requirements.tex` - High-Level Requirements

Both documents use `nl_tps_common.sty`. The ConOps also uses the images in
`figures/`.

## Import from GitHub

1. In Overleaf, create or open a project connected to this GitHub repository.
2. Pull the repository content.
3. Open **Menu -> Main document**.
4. Select either `overleaf/NL_TPS_ConOps.tex` or
   `overleaf/NL_TPS_High_Level_Requirements.tex`.
5. Use pdfLaTeX as the compiler.
6. Recompile twice after changing headings, page counts, or the table of
   contents.

The two files are intentionally separate controlled documents. Select one as
the main document at a time. The `.docx` files remain the source artifacts used
for the initial conversion; future substantive changes should be reconciled
through document control so the Word and LaTeX versions do not silently drift.
