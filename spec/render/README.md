# Controlled render inputs

Rendered LaTeX tables and reports are derived views. The structured sources in
`spec/` and materialized mirrors in `mps/import/` are checked before rendering.
Generated clinical evidence, approvals, scores, or PASS results are prohibited.

ART-POL-001 in `spec/artifacts.yaml` controls PDF naming, provenance manifests,
source-control exclusion, CI review artifacts, and governed-release blocking.
