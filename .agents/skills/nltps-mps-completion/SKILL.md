---
name: nltps-mps-completion
description: Govern completion of the GCPL/NL-TPS MPS project by coordinating model-aware implementation, independent verification, retained evidence, engineering decisions, and human review boundaries.
type: workflow
---

# NL-TPS MPS Completion Orchestrator

Use this skill for any request to finish, close, remediate, verify, or assess the
controlled `NLTPSGovernance` MPS project.

## Required context

Read these controlled sources before selecting work:

- `CLAUDE.md`
- `mps/materialization/stage-a-checklist.yaml`
- `mps/materialization/evidence-obligations.yaml`
- `mps/materialization/mps-mat-009/findings.yaml`
- `mps/materialization/mps-mat-009/independent-reviews.yaml`
- `mps/materialization/mps-mat-009/f2-observation.yaml`
- `mps/materialization/mps-mat-009/adjudication.yaml`

Also load `mps-mcp-workflow` and the aspect-specific MPS skills needed for the
selected operation.

## Authority boundaries

The coordinator may:

- inspect the live MPS project and controlled records;
- implement an already-authorized repair through `mps_mcp_*`;
- run mechanical gates, model checks, cold builds, and model tests;
- retain attributable observations and report their exact result;
- prepare decision and review packets.

The coordinator must not:

- edit `.mps`, `.mpl`, `.msd`, or `.mpr` files as text;
- invent a human reviewer identity or sign an independent review;
- treat its own review as independent human approval;
- change a frozen obligation merely because it is difficult to satisfy;
- infer semantic validity from generation success;
- turn an observation into `DISCHARGED` without the required authority;
- declare Stage A closed or authorize Stage C.

## Operating cycle

1. **Workspace gate**
   - Run `python tools/repo/check_workspace_location.py --enforce`.
   - Call `mps_mcp_list_open_projects`.
   - Refuse model writes if the open project is not the compliant checkout.
2. **Establish baseline**
   - Require a clean or explicitly characterized Git state.
   - Record the selected commit and MPS build.
   - Run the currency and structural gates relevant to the item.
3. **Classify the obligation**
   - `EXECUTABLE`: an authorized model change or reproducible observation.
   - `DECISION`: two or more defensible acceptance interpretations exist.
   - `HUMAN_REVIEW`: a named independent human judgement is required.
   - Never convert one class into another for convenience.
4. **Plan one increment**
   - Name one acceptance item and its evidence population.
   - State the expected red and green observations.
   - Stop at checkpoint or review boundaries.
5. **Implement model-aware work**
   - Use surgical MPS MCP operations.
   - Preserve node IDs.
   - Follow the structure-to-build-to-descriptor chain.
   - Validate changed roots and reload compiled aspects when required.
6. **Verify independently**
   - Run generation and semantic tests separately.
   - Require nonzero authored, discovered, and executed test populations.
   - Use a separate read-only agent/session for review where independence is
     claimed.
7. **Check restoration and persistence**
   - Inspect the complete Git diff and status.
   - Distinguish normalized repository identity from working-tree line endings.
   - Do not erase unexplained residual state.
8. **Report**
   - Record observed facts, hashes, tool versions, and unresolved questions.
   - Route decisions to the engineering owner and named-review obligations to a
     human reviewer.

## Current completion boundary

Stage A is materially implemented. The main remaining closure work is assurance,
not speculative language construction. In particular:

- `MPS-MAT-009` requires a named independent human reviewer.
- Open evidence obligations must be re-observed rather than inferred.
- ADJ-F2-002 authorizes repository/index content identity as the restoration
  criterion; equivalent MPS line-ending differences need not produce empty
  working-tree status.
- ADJ-TEST-FAMILY-001 through ADJ-TEST-FAMILY-003 require three distinct
  executable families that are authorized but not yet materialized.
- ADJ-MAT008-001 authorized a controlled-history inspection; it returned
  NOT_ESTABLISHED because MPS-0 lacks explicit MCP-authoring evidence, so
  MPS-MAT-008#1 remains open.

The first completion pass is assessment-only: produce a ledger separating
executable observations, decisions, and human-review obligations before changing
the model.

## Verification commands

Use the smallest controls covering the selected item. The complete local
verification sequence is:

```text
python tools/repo/check_workspace_location.py --enforce
python tools/mps/headless_build.py --validate-only
python tools/mps/headless_build.py --cold --target make
python tools/mps/headless_build.py --target test --log build/work/headless-test.log
python -m unittest discover -s tests -v
```

Do not use a green headless generation result as a substitute for model checking
or semantic model-test execution.
