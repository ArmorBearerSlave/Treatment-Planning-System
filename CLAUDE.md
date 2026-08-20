# GCPL / NL-TPS — session controls

Controls that must survive a session boundary. The gate suite enforces most structure
mechanically; what follows is what a gate cannot check.

## Workspace

This repository is the engineering workspace: a space-free path outside any
file-synchronization root, with its Git common directory inside the clone. A prior
checkout under OneDrive is retained read-only and is **not** an engineering workspace;
no authoring or generation happens there. `tools/repo/check_workspace_location.py
--enforce` must pass from wherever work is done. See `spec/relocation_verification.yaml`.

## MPS persistence is written by MPS, never by a text tool

**Never create, edit, or patch `.mps`, `.mpl`, `.mpr`, or `.msd` files.** ADR-001 and
risk ADR1-R-05 prohibit it outright. This holds regardless of convenience and regardless
of whether the model-aware tooling is available.

The only sanctioned agent route is the MPS Projectional Agent Toolkit over MCP
(`mps_mcp_*` tools), which operates on the live model inside the running IDE.
Registration is project-scoped in `.mcp.json`; MCP servers load at session start, so a
newly registered endpoint needs a session restart.

**If `mps_mcp_*` tools are absent, that is an integration failure to diagnose — not a
reason to proceed by editing files.** Stop and report. Likeliest causes, in order: the
project-scope approval prompt was dismissed; the session root is not this repository;
MPS is not running with `mps/NLTPSGovernance` open; a modal MPS dialog is holding the
IDE thread and blocking the model write lock; the MCP port changed (it is assigned per
process — verify by handshake, not by a listening socket).

## Checkpoint discipline

Materialization runs as `MPS-0 → MPS-1 → MPS-2 → MPS-3`, each a commit and review
boundary. **Stop at the boundary; never roll one checkpoint into the next.** The
boundary exists so it can be determined whether the metamodel is correct before asking
whether the migration is correct.

- Scope, acceptance items, and native check results: `mps/materialization/stage-a-checklist.yaml`
- Concept design that MPS-1 and MPS-2 transcribe: `mps/bootstrap/mps1-concept-features.yaml`
- Module graph and relation kinds: `mps/bootstrap/language-skeleton.json`

`--max-concepts` on `tools/mps/check_module_graph.py` bounds each checkpoint. The first
live-MPS commit shall not contain the 119 HLR roots; only MPS-3 may.

A concept may take a superconcept only from its own language or from a language declared
`EXTENDS`. Changing a dependency kind is a controlled blueprint change, not an IDE
convenience.

## Evidence before acceptance

Negative examples are created and shown to be rejected before the corresponding positive
content is added. An acceptance item is `complete` only with attributable evidence, and
completing it is a claim about what was demonstrated, not about what was created.

## Tool success is not evidence

An MCP call returning `ok: true` is not evidence that MPS persisted the requested
semantics. A model-aware write can be accepted, report success, and still drop the part
that mattered: a mistyped feature key is silently ignored and the property falls back to
a default, and an omitted cardinality is silently replaced by the metamodel default.
Checkers disagree with each other, too -- a model-scope check can report clean while a
node-scope check on the same tree reports errors, and a missing mandatory child can pass
both and surface only when the language is built.

**Every model-aware mutation that affects controlled semantics is read back from the MPS
model or runtime representation before it is accepted.** Read-back means comparing the
persisted or runtime state against the controlled source, feature by feature -- not
re-reading the tool's own response.

A passing `check_root_node_problems` is not sufficient acceptance evidence by itself.
Acceptance requires read-back, plus the applicable node-scope and model-scope checks,
plus a native build or check result. No single checker is sufficient.

## Metric integrity

`76 / 2,144` entities carry a source-explicit hazard set. **Materializing an entity in
MPS does not increase that numerator.** Structural representation and hazard-specific
engineering review are different claims; only a named reviewer replacing a derived
hazard set with one determined for that specific entity moves it. See
`spec/construction_policy.yaml`, `progress_metric.numerator_integrity`.

## What passing gates does and does not mean

Every gate here is structural. Passing proves internal consistency and nothing else — no
clinical correctness, no risk acceptability, no executed V&V claim, no approval, no
authority cutover. Approval is recorded by governance; an artifact never asserts its own.

## Verifying

```
python -m unittest discover -s tests
python tools/mps/check_module_graph.py --max-concepts <checkpoint bound>
python tools/spec/build_trace_graph.py --check
```

The full suite is `.github/workflows/controlled-spec-gates.yml`; run every step listed
there before a commit that closes a checkpoint.
