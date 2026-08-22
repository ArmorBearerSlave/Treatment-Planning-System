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

Materialization runs as `MPS-0 → MPS-1 → MPS-2 → MPS-3 → MPS-4`, each a commit and
review boundary. **Stop at the boundary; never roll one checkpoint into the next.** The
boundary exists so it can be determined whether the metamodel is correct before asking
whether the migration is correct.

    MPS-0  project and the four language modules          closed
    MPS-1  foundation + governance                        closed
    MPS-2  clinical intent + roles.common                closed
    MPS-3  the four professional role projections        closed
    MPS-4  realization + the 119-HLR import               materialized; one item open

**Stage A is materially complete but not formally closed.** The metamodel, the four
professional projections, the corpus mirror, its provenance, the source-explicit hazard
links and Stage-B equivalence are all present; no metamodel or corpus-content gap remains.
One acceptance item remains, and it is not domain modelling:

    MPS-MAT-009   independent review of the completed Stage A evidence   assurance

`MPS-MAT-008` closed at 15/16 on a cold headless build, an independent repeat build with
zero drift, and native `launchtests` model tests with `authored = discovered = executed = 2`
carrying both exact identities. `MPS-MAT-009` is not the implementer's to record at all, and
that is the point of it: the closure record names what a reviewer should challenge --
population completeness, whether the cold runs were genuinely cold, specificity versus
inference, byte-identical restoration, disposal of the stale-state confound, and the
enforced separation of generation success from semantic-test success. Re-running the gates
green establishes currency, not warrant. `MPS-MAT-004B` closed once the corpus was converted
and the layout observed.

Two test-family populations exist and their correspondence is now controlled:
`initial_test_families` in the blueprint, declared at MPS-0, and the operational ledger
enumerated at closure from the mechanisms MPS provides. Every blueprint family carries
exactly one disposition and every operational family is either a disposition target or
declared newly introduced, so nothing crosses by silence. Three dispositions are
deliberately `undecided` pending an engineering decision and are named on every run --
`ARCH-INVARIANT-001-no-language-equivalence` most of all, because dropping an architectural
invariant from a *test taxonomy* may be correct while dropping it from *controlled scope* is
not.

## The headless build, and what it proved about the ones before it

`build/nltps-headless-build.xml` drives MPS's own `<mps.make>`, run by
`python tools/mps/headless_build.py`. The toolchain is entirely the pinned installation:
Ant from `MPS_HOME/lib/ant`, the JDK from `MPS_HOME/jbr`, tasks from
`lib/ant/lib/ant-mps.jar`. A system Ant or an ambient `JAVA_HOME` would make the result
depend on the host, so neither is consulted, and `MPS_HOME/build.txt` is compared with
the pinned build number and a mismatch refused. Two things are not optional:
`ant-mps.jar` needs `org.jdom` from `lib/util-8.jar` **on the taskdef classpath rather
than Ant's own**, and the worker needs its own `idea.system`/`config`/`log` paths or it
tries to write into Program Files. `autoPluginDiscovery="true"` crashes CoreWorker in
this build and is left off.

It runs, and `MPS-MAT-008` is still open, for two reasons worth carrying forward.

**Generation is not checking.** A `VerificationClaim` violating REA-C-002 and REA-C-003
was placed in the proof sandbox, confirmed rejected by the model checker, and the
headless build then completed over it with exit code 0. **A reproducible headless
generator is not a reproducible headless validator.** Never present build success as
evidence that the model is valid; the acceptance wording asks for model tests as a
separate clause precisely because they are a separate thing, and the project declares
none.

**The project had never built from a clean state, and now does.** `nltps.foundation
.behavior` held one root, a baseLanguage `ClassConcept`, and no `ConceptBehavior`; MPS
still generated `Language.java` referencing a `BehaviorAspectDescriptor` the aspect
generator never emits. Deleting every `source_gen` and `classes_gen` made the interactive
IDE fail exactly as the headless build did — four checkpoints had stayed green on output
generated before that aspect took its current shape. **A long-lived IDE with a warm output
tree will keep a project green that cannot be built at all.** `POST-MPS4-01`, corrected by
moving the utility into `nltps.foundation.typesystem` where its three callers live; the
behaviour aspect is left present and empty, which is sufficient — its existence does not
trigger the reference, its having content does.

**Retargeting a cross-model reference does not withdraw the import the old target
required.** Pointing a test's expected-rule reference at another language and back left
`<import index="xv4b" ref="...(nltps.governance.typesystem)"/>` behind with nothing
referencing it. The cold build passed 2/2 with it present and no gate mentioned it; only a
byte-for-byte diff against the pre-change commit found it. **Verify a restoration by an
empty `git diff`, never by re-reading the field you changed** -- a reformat, a residual
import or a reordered element is invisible to read-back and produces a fourth state nobody
has run.

**A warm `idea.system` can make a working configuration look broken, and the false repair
will appear to succeed.** A stale worker system directory produced
`NoClassDefFoundError: org.jetbrains.mps.openapi.model.SNodeReference`, which reads exactly
like a missing module dependency; a later run over the same tree passed with no
configuration change. Adding the dependency "worked" only because the next run had a fresh
cache, and controlled removal later showed it was never needed. The `source_gen` lesson
inverted: a warm tree keeps a broken project green, a warm system directory makes a green
one look broken. **Delete `build/work/system`, `config` and `log` before diagnosing any
class-loading failure, and prove a dependency is load-bearing by removing it and running
cold -- not by adding it and seeing the symptom go.**

**Node identity, reference integrity and semantic behaviour are three separate
properties, and preserving one proves nothing about the other two.** The `CalendarDates`
move demonstrated all three at once: `MOVE_NODE_TO_PARENT` with a `modelReference` kept the
node id, every incoming reference broke, `check_root_node_problems` reported no problems,
and only the usage index showed the damage — three call sites still addressing the vacated
model, printing `null.null`. `FIX_REFERENCES` per affected root repaired them.

So after any cross-model move, all three are checked separately: read the id back, re-run
`FIND_USAGES`, and re-run the behavioural control that established the semantics in the
first place. A fix count is a claim about what the tool did, not about what the model now
says, and compiling is not behaving — this utility once returned false for every input and
produced a false calendar PASS that only read-back caught.

- Scope, acceptance items, deferrals, and native check results: `mps/materialization/stage-a-checklist.yaml`
- Concept design that MPS-1 transcribed: `mps/bootstrap/mps1-concept-features.yaml`
- Concept design that MPS-2 transcribed: `mps/bootstrap/mps2-concept-features.yaml`
- Concept design frozen for MPS-3: `mps/bootstrap/mps3-concept-features.yaml`
- Concept design frozen for MPS-4: `mps/bootstrap/mps4-concept-features.yaml`, which also
  carries the 119-HLR import, neutral export and Stage-B equivalence contracts
- Role and authorization ontology frozen for MPS-2: `mps/bootstrap/mps2-role-ontology.yaml`
- Module graph, dependency kinds, per-checkpoint inventories: `mps/bootstrap/language-skeleton.json`

The 119 imported HLRs are **instances of `ImportedHLR`, not concepts**. They persist in
the import model and never under `languages/*/models/*.structure.mps`, because the module
graph gate derives the concept inventory from exactly those files: a root landing there
would be counted as a concept and the MPS-4 ceiling would read 215 instead of 96. That is
the most expensive way this checkpoint can fail, because the number would still look
deliberate.

`--checkpoint MPS-N` on `tools/mps/check_module_graph.py` derives the expected language
set and concept ceiling from the blueprint. Do not reintroduce a hard-coded ceiling;
`--max-concepts` survives only as a diagnostic override and the two are mutually
exclusive. `--explain` prints the derivation without asserting module presence, which is
the only way to review a ceiling before its checkpoint arrives. The first live-MPS commit
shall not contain the 119 HLR roots; only MPS-4 may.

Each language declares `materialized_at` (when the module exists) separately from
`concepts_materialized_at` (when its inventory lands), and `external_explicit`, the
non-NL-TPS dependencies it may carry. MPS adds such dependencies on its own; every one
observed so far was unnecessary and was removed through model-aware tooling, never by
editing `.mpl`. MPS-4 saw two more -- `jetbrains.mps.lang.core` when a property was
added, and `JDK` when a checking rule called `String.equals`. Both were removed and the
language still builds; `nltps.clinicalintent` has used `String.equals` since MPS-2 with
no module-level JDK dependency, which is what made the second one recognisable as
unnecessary rather than required. MPS also re-adds a `DEFAULT` companion to every
`EXTENDS` edge on rebuild; `DELETE` removes both, so re-add `EXTENDS` afterwards and
re-check the module graph.

A concept may take a superconcept only from its own language or from a language declared
`EXTENDS`. A concept may *contain* only what its own language or a transitive `EXTENDS`
ancestor owns — and never what a *different semantic-core language* owns unless the pair
is in `semantic_core_containment_whitelist` in the blueprint. MPS-4 gives
`nltps.realization` `EXTENDS nltps.governance` for one narrow reason, so `ImportedHLR` can
inherit `Requirement`; that must not become permission to contain `Hazard`, `Decision`,
`RiskControl` or any other governed state. **EXTENDS grants superconcept visibility, never
containment ownership.** A concept may *reference* anything its language declares, `EXTENDS` or
`DEFAULT` -- but not a language it declares no dependency on at all; that reference would
fail to resolve during materialization, and since MPS-3 the specification gate rejects it.
Changing a dependency kind is a controlled blueprint change, not an IDE convenience.

## The projection layer owns no authority

The four professional languages are projections, not semantic languages. They present
authoritative state through one profession's lens and own none of it: there is exactly one
`CandidatePlan`, one approval state, one workflow state, and a projection reaches them by
reference through a `roles.common` holder. A profession-owned copy is the failure this
layer exists to prevent.

Authority is never expressed here. A professional task names an interaction with an
enumeration its own language owns and names an action by referencing an `ActionDefinition`;
whether an actor may perform it is decided by `AuthorityPolicy`, `RoleCapability` and the
CLI-C-005 predicate that discharged GOV-C-007 at MPS-2. **Seeing a command in an editor is
not permission to run it.** `tools/mps/check_role_ontology.py` refuses a projection concept
that references `RoleCapability`, `AuthorityPolicy` or `AuthorizedActor`, that carries an
enumeration owned by a semantic-core language, that makes a review surface actionable, or
that lets one profession express another's interaction. The four task-kind enumerations
share no member, which is what makes clinical approval, technical release review, planning
interaction and readiness verification structurally distinct rather than distinct by
convention.

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

The converse also holds: a property absent from the persisted form is not evidence the
write was dropped. MPS omits any property equal to its declared default, so a boolean
false never appears. Distinguish the two by writing the non-default value and reading it
back -- at MPS-4, setting `authoritative` true on one root made it appear in both the
runtime and the file, which is what proved the other 118 absences meant false.

Three failures observed so far, each silent in every checker that ran before it:

- **A `cardinality` key on a link in `CREATE_CONCEPTS` is ignored.** 34 of 37 links at
  MPS-2, then 16 of 16 at MPS-3, were created with the metamodel default `0..1` instead of
  the specified `1` or `0..n`, with `ok: true` throughout and a clean model check. Assume
  every link is wrong until read back. Set `sourceCardinality` explicitly; `0..1` is
  serialized as absent, so absent means default, not unset.
- **`check_root_node_problems` reports obligatory-role violations on the feature
  descriptor, not in the node-level `problems` array.** A missing mandatory child appears
  under `children[].problems` and a missing mandatory reference under
  `references[].problems`. A reader that prints only node-level `problems` discards both
  and sees a clean result. Neither is caught by file inspection or by a native build.
- `mps_mcp_scaffold_editor` leaves the inline display property of every reference cell
  unresolved. The model check reports nothing; the Java compiler reports `variable
  property might not have been initialized`. Point each one at a real property of the
  concept it displays. **A diagnostic count is not a defect population.** A compiler
  stops at the first failing unit, so when it reports N instances of a repeated defect,
  enumerate the whole population rather than treating N as exhaustive. At MPS-4 it named
  two, in one file, and stopped; the editor model actually held 45 across all eighteen
  editors. Count them by walking the model for a `CellModel_Property` with no
  `relationDeclaration`.
- **A newly built checking rule is not live for instance models until modules are
  reloaded.** After REA-C-002 was built, `check_root_node_problems` reported "no problems
  found" on a model holding the rule's own negative example. `mps_mcp_reload_all` made it
  fire immediately. A clean check taken between building a rule and reloading is
  meaningless and looks exactly like a passing one. **Reload after creating or changing
  any checking rule, before attempting behavioural proof** -- and re-run the negative
  example after every later rebuild, because a rebuild can quietly leave it stale again.
- **An enumeration property set to a member that does not belong to its enumeration is
  accepted silently.** The write returns `ok: true`, the value persists unresolvable with
  `null` where the member id belongs, and no checker or build reports it. A resolved
  member reads back as `<memberId>/<name>`; a corrupt one reads back as
  `<fragment>/null`. Read enum properties back and check for the id.
  `tools/mps/check_enum_persistence.py` now gates this mechanically: it follows every
  persisted value out to the `EnumerationDeclaration` its property is declared against --
  across models, since a property and its enumeration may live in different languages --
  and rejects a value naming anything the declared enumeration does not declare. It does
  not decode MPS's compact id encoding, so it enforces identity by declared membership
  plus repository-wide id/name pairing stability. **Run it after any session that writes
  enum values.**

MPS-2 recorded a fourth, that MPS does not enforce cardinality `1` on a reference. **That
was wrong and is withdrawn.** An MPS-3 experiment on one concept -- one probe missing a
mandatory child, one missing a mandatory reference -- produced `No child in the obligatory
role 'version'` and `No reference in the obligatory role 'lifecycleState'`. Children and
references behave identically and both are enforced. The defect was the reader. Structural
cardinality is a proven presence mechanism; what it needs is a read-back that looks in the
right place.

## Deferrals are conditional, not permanent

A constraint whose concept cannot be instantiated cannot be behaviourally proven. Such a
proof is deferred against a named `affected_concept` in `stage-a-checklist.yaml`, never
waived and never relabelled PASS. `check_concept_features.compute_reachability` computes,
across **every** `mps*-concept-features.yaml` present, which non-rootable concrete
concepts no containment path reaches; `check_materialization_plan` imports it and fails
while a deferral is still active for a concept that has since become reachable.

The consequence for whoever adds a container: **giving a deferred concept a host makes
its deferred negative example mandatory at that checkpoint.** Reachability is cumulative
by design, so a container added later is seen.

Three deferral classes exist and **only the first lapses automatically**:

- `non_instantiability` -- the rule is written and correct, but no legal host exists yet.
  Giving the affected concept a container expires the deferral, and the gate enforces it.
- `semantic_model_absence` -- the discriminator itself does not exist, as with GOV-C-007
  before `AuthorizedActor`. Introducing that semantics makes the constraint *implementable*,
  not *active*. Nothing will notice; the checkpoint that adds it must reclassify it
  deliberately.
- `literal_example_substitution` -- the mechanism is proven, but the frozen negative example
  named a concept allocated to a later checkpoint, so an equivalent was substituted. The
  literal example must be re-run against the unchanged mechanism when that concept lands.

The second and third fail by not firing, which is indistinguishable from compliance. A
deferral that has outlived its justification leaves every gate green.

## Reaching a control the toolkit does not expose

`project.default_model_persistence` has been declared `file-per-root` since MPS-0, and
no model in the project has ever used it. `check_language_skeleton` compares that
declaration against `spec/architecture.yaml` and never observes the layout on disk, so
four checkpoints closed green on a constraint that was never in force. **A gate that
compares two declarations with each other verifies neither.**

It could not be fixed from here. `mps_mcp_update_model` supports only `RENAME` and
`DELETE`, and `mps_mcp_create_model` takes no persistence argument; MPS does it in one
IDE action, `Convert to File-Per-Root Format`, which a person invokes. **A control the
sanctioned route cannot reach is an integration deficiency to report, with the action
that would fix it named — not a thing to reach around.** The corpus was converted that
way and `MPS-MAT-004B` closed on the observed layout.

The durable fix is the gate, not the conversion. `tools/mps/check_model_persistence.py`
observes what MPS wrote and fails on any model a controlled contract binds, reporting the
rest; `tests/test_model_persistence.py` ties its verdict to the acceptance item in both
directions. **Whenever a control compares one declaration with another, it is verifying
that someone wrote the same word twice.**

**The absence of an IDE action is not evidence about state.** MPS hides `Convert to
File-Per-Root Format` when the model is already per-root, but equally when the selection
is not a model or the model is read-only. Observe the layout; do not read the menu.

MPS writes a converted model as a folder: `.model` carries `content="header"` with the
used languages and imports and no registry, and each root is a `<nodeId>.mpsr` carrying
`content="root"` and its own registry. **The root extension is `.mpsr`, not `.mps`.**
Anything that finds models by globbing `*.mps` sees a converted model as empty —
`tools/mps/mps_layout.py` is the one place that knows this, and every corpus reader goes
through it.

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
python tools/mps/check_module_graph.py --checkpoint MPS-N
python tools/mps/check_enum_persistence.py
python tools/mps/check_concept_features.py
python tools/mps/check_role_ontology.py
python tools/mps/check_materialization_plan.py
python tools/mps/check_hlr_root_placement.py
python tools/mps/check_model_persistence.py
python tools/mps/headless_build.py --validate-only
python tools/mps/check_headless_coverage.py
python tools/mps/check_headless_build_currency.py
python tools/mps/check_test_family_reconciliation.py
python tools/mps/derive_probe_target.py --check
python tools/mps/export_hlr_corpus.py --check
python tools/mps/check_stage_b_equivalence.py
python tools/spec/build_trace_graph.py --check
python tools/spec/check_path_citations.py
```

The full suite is `.github/workflows/controlled-spec-gates.yml`; run every step listed
there before a commit that closes a checkpoint.
