# 119-HLR Stage A mirror import

`hlr-baseline.json` is a deterministic, non-authoritative import bundle derived
from `overleaf/NL_TPS_High_Level_Requirements.tex`. It preserves each exact
LaTeX normative field and adds normalized review text, source location,
verification methods, and SHA-256 integrity values.

## Import behavior in MPS

The MPS-side importer must:

1. Validate the bundle contract, source hash, record hash, expected count, and
   domain distribution before opening a write command.
2. Execute one repository write command for the complete baseline or roll back
   the command on any error.
3. Create one `Requirement` root per HLR under file-per-root persistence.
4. Preserve the exact stable ID and `normative_text_latex`; show
   `normative_text_plain` as a review projection, not a replacement authority.
5. Set mirror provenance, source line, source hash, record hash, domain,
   source/hazard field, and verification methods.
6. Reject duplicates, missing fields, unexpected domains, non-sequential IDs,
   unsupported methods, or an existing root with different normative content.
7. Be idempotent: re-importing the identical bundle makes no semantic change.
8. Report conflicts; never resolve or overwrite them silently.
9. Create no HLIR, SIR, risk, component, allocation, or V&V child merely from
   this HLR import. Those enter through later controlled increments.

## Equivalence export

After import, generate a neutral JSON export ordered by HLR ID. The Stage B
comparison must prove equality of record count, IDs, exact LaTeX normative
text, domain, source/hazard field, and verification methods. It must also show
all import and export tool versions, model baseline, and hashes.

The imported model remains a mirror until the Stage C authority decision is
approved and effective.
