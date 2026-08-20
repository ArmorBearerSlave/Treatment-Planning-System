# Stage A MPS materialization handoff

This directory is a controlled handoff for creating the live JetBrains MPS
project. It is not MPS persistence and does not claim that the four languages,
importer, generators, constraints, editors, or model tests exist.

## Preconditions

1. Commit the current repository work and pass all structural gates.
2. Work from the independent clone at a space-free path outside any
   file-synchronization root, with its Git common directory inside the clone.
   This supersedes the earlier linked-worktree procedure: a linked worktree
   relocates the working tree only, leaving the object database, refs, worktree
   metadata, locks, and index state under the controlling common directory.
   See `spec/relocation_verification.yaml`.
3. Use the pinned build recorded in `stage-a-checklist.yaml`
   (`pinned_toolchain`). A different build is a separate qualification decision.
4. Use synthetic nonclinical content only. No patient data, clinical
   credentials, signing keys, or production endpoints are permitted.
5. Confirm ENG-PKG-01, ADR-001, and ADR-002 remain at explicit Stage A approval
   state. Stage A work does not require or imply Stage C approval.

## Model-aware tooling

MPS persistence is created by MPS. From MPS 2026.1 the bundled Projectional Agent
Toolkit exposes an MCP server inside the running IDE, so an agent can create and
modify the live model through model-aware operations instead of editing XML. That
is the only sanctioned agent route; direct edits to `.mps`, `.mpl`, `.mpr`, or
`.msd` remain prohibited by ADR-001 and ADR1-R-05 whether or not the toolkit is
connected.

Preconditions, all of which must hold at the same time:

1. MPS is running with `mps/NLTPSGovernance` open. The server lives inside the
   MPS process and operates on the live repository, so a closed IDE means no
   endpoint.
2. **Settings -> Tools -> MCP Server** is enabled. Note the port it reports.
3. No modal MPS dialog is open. A modal dialog blocks the IDE thread and write
   operations cannot obtain the model lock.
4. The endpoint is registered with the agent client and the client session has
   been restarted; MCP servers are loaded at session start.

`.mcp.json` at the repository root registers the endpoint in project scope, so it
is version controlled and travels with the clone rather than living in per-user
state. Verify the endpoint before relying on it:

```
curl -s -X POST http://127.0.0.1:<PORT>/stream   -H "Content-Type: application/json"   -H "Accept: application/json, text/event-stream"   -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}'
```

A live server answers with `serverInfo.name` of `JetBrains MPS MCP Server`. A
listening socket alone is not evidence; check the handshake. Note that `GET` on
`/sse` deliberately hangs, because it is a streaming endpoint.

**The port is assigned per machine.** The committed value is the one observed on
the workstation that created MPS-0; on another machine, read the port from the
MPS settings dialog and update `.mcp.json` locally. A wrong port fails as a
connection error, not as a missing tool.

## Checkpoints

Materialization runs as four checkpoints, each with a commit and review
boundary, rather than one construction. The boundary matters: it lets us decide
whether the metamodel is correct before asking whether the migration is correct.

| Checkpoint | Scope | HLR roots |
| --- | --- | --- |
| MPS-0 | Project and four language modules; dependency graph and persistence policy only | no |
| MPS-1 | Foundation and governance metamodel, with deliberate invalid nodes proven rejected | no |
| MPS-2 | Clinical intent and realization metamodel, negative examples first | no |
| MPS-3 | 119-HLR import, then neutral export and Stage B equivalence | yes |

**The first live-MPS commit shall not contain the 119 HLRs.**

Materializing an entity in MPS does not increase the source-explicit hazard
count. Structural representation and hazard-specific engineering review are
different claims; only the second moves that metric.

## Materialization sequence

1. Create `NLTPSGovernance` through the MPS UI or model-aware API. Never author
   MPS persistence XML as text.
2. Create the four language modules in controlled order:
   `nltps.foundation`, `nltps.governance`, `nltps.clinicalintent`, and
   `nltps.realization`.
3. Apply the exact dependency graph, root concepts, non-root concepts,
   constraints, typesystems, editors, and generator boundaries defined in
   `mps/bootstrap/language-skeleton.json`.
4. Configure file-per-root persistence for normative root models.
5. Implement the neutral HLR importer against
   `mps/import/hlr-baseline.schema.json`; import all 119 HLR roots without
   normalizing or rewriting their normative text.
6. Add negative model tests for invalid trace direction, incompatible units,
   duplicate ownership, missing authority, unsupported release scope, and A4
   authority encoded in AI-creatable intent.
7. Add deterministic neutral export and compare it with the controlled input by
   ID, exact text, domain count, source hash, record hash, and approval state.
8. Run model validation and the headless build without the experimental agent
   toolkit, retain the evidence, and submit the Stage B equivalence report.

## Acceptance boundary

The materialization is complete only when every item in
`stage-a-checklist.yaml` has attributable evidence and independent review. It
does not move authority from the controlled documents. Stage C remains blocked
until its separately approved cutover record and named approvals exist.
