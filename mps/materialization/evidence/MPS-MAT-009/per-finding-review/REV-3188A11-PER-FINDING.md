# REV-3188A11-PER-FINDING

Historical per-finding independent review of six findings at exact repository object
`3188a11443e33c8c4f68933cf73282108957f356`.

- **Review identifier:** REV-3188A11-PER-FINDING
- **Reviewed object:** `3188a11443e33c8c4f68933cf73282108957f356`
- **Review date:** 2026-08-25
- **Findings adjudicated:** NF-01, NF-05, NF-06, NF-10, NF-11, NF-12
- **Verdict scope:** repair support only. This review determines **repair support**, not lifecycle
  disposition. It states no finding to be CLOSED.

---

## 1. Reviewer independence statement

Against the six disclosure items required of this review, the reviewer:

- did **not** author any of C1-C9;
- did **not** transport findings or reviews in this remediation sequence;
- did **not** author `REV-C5-CUMULATIVE`;
- did **not** author `verified_repairs_of`;
- did **not** author the finding-side `independent_review_support` records;
- **DID perform the earlier C7, C8 and C9 independent reviews.**

The last item is disclosed as a material limitation. The stop condition in the governing brief is
participation *in creating the historical assertions being verified*. The reviewer created none of
them; the reviewer is the actor who repeatedly found them unsupported and returned INDETERMINATE for
exactly these six findings at C7, C8 and C9. Stopping would therefore have left permanently unfilled
the evidentiary gap the reviewer itself identified.

The bias risk runs in a specific and stateable direction. In the C7 report the reviewer recorded
having re-verified several of these mechanisms **at `2f10b3e`**, and therefore arrives with a prior
expectation that they hold. Two mitigations were applied and are auditable in this report:

1. every proposition was derived from `3188a11` alone, by reading that object's source and executing
   that object's observers, with no reliance on the reviewer's prior text;
2. the review sought falsification actively, and did find residuals in NF-01, NF-06, NF-10 and
   NF-12, and one material divergence from later remediation metadata concerning NF-05.

**A reviewer with no prior role in this remediation sequence would still be preferable.** This
artifact's own provenance is a limitation and is recorded as such. Independence is asserted on
participation and disclosed where partial; it is not inferred from Git author metadata. The Git
author identity on every commit in this lineage is `ArmorBearerSlave <ArmorBearerSlave@gmail.com>`,
the same account that owns the workstation, and no account-level separation is claimed.

This review does not register itself, creates no `verified_repairs_of`, creates no closure warrant,
and moves no lifecycle state.

---

## 2. Review workspace and starting state

A new clone was created with an independent object store, outside the remediation repository and
outside every prior review workspace:

    git clone --no-local C:\src\gcpl-stage-a-repair C:\src\gcpl-3188a11-per-finding-review
    git switch --detach 3188a11443e33c8c4f68933cf73282108957f356

| property | value |
|---|---|
| repository root | `C:\src\gcpl-3188a11-per-finding-review` |
| HEAD | `3188a11443e33c8c4f68933cf73282108957f356` |
| detached | yes |
| origin | `C:/src/gcpl-stage-a-repair` |
| reflog | two entries: `clone`, then `checkout ... to 3188a11` |
| `git fsck` | clean |
| `git status --porcelain` | empty |

**Object-store independence.** One freshly written pack (inode `6192449489277582`, link count **1**);
no `objects/info/alternates`; no object file with link count greater than 1. That is the `--no-local`
signature: objects arrived through the transport rather than by hardlink from the source.

**Execution-cold state, enumerated before anything was executed.** `__pycache__` 0, `*.pyc` 0,
`.pytest_cache` 0, `source_gen` 0, `source_gen.caches` 0, `classes_gen` 0, `test_gen` 0,
`test_gen.caches` 0, `*.class` 0, `*.jar` 0, `build/work` **absent**, ignored files present 0.
`build/` contains only 3 tracked source files. No warm remediation tree was used as evidence.

At the time of review the source repository's branch tip had advanced to `3b74bdb`. The review was
performed detached at `3188a11`; `3b74bdb`, C9 and the current branch were not substituted for the
reviewed object at any point.

---

## 3. Method and evidence rules

The core question adjudicated for each finding was:

> At exact object `3188a11`, is the repair proposition represented by this finding actually present
> and independently demonstrated?

Rules observed:

- `REV-C5-CUMULATIVE.verified_repairs_of` was **not** used as evidence.
- Remediation-authored `independent_review_support` was **not** used as evidence.
- Later objects were consulted only for Git ancestry, for locating original repair-introduction
  commits, and for identifying later changes bearing on whether a historical repair was incomplete.
  Every such use is explicitly labelled **LATER-HISTORY EVIDENCE** below.
- All mutations were performed on in-memory deep copies of the loaded records, or in a separate
  disposable clone. **No controlled file in the primary historical checkout was written at any
  point.**

### Population and mechanism baseline at 3188a11

| property | value at 3188a11 |
|---|---|
| findings in register | 42 |
| canonical-state findings | 17 |
| state-debt exceptions | 25 |
| canonical + debt = total | 17 + 25 = 42, disjoint, exhaustive, no orphan exceptions |
| canonical field | `state` |
| canonical states | `OPEN`, `CLOSED`, `ACCEPTED` |
| declared legacy fields | `status`, `disposition` |
| canonical CLOSED population | `RT-F-03`, `RT-F-04`, `RT-F-05`, `RT-F-06` |
| closure rule | applies to CLOSED, requires `closure_review`, closing verdicts `['INDEPENDENTLY VERIFIED']` |

All six findings are `state: OPEN` at `3188a11`. All six carry a **deictic prose** `repair` value of
the form "this checkpoint, commit CN". None carries `repair_introduced_object` (that field did not
exist yet) and none declares `repair_completion_object`. The repair objects resolve by commit subject
to: NF-01 -> C2 `5fe5b69`; NF-05 -> C1 `63694e5`; NF-06 -> C1 `63694e5`; NF-10 -> C3 `1db9948`;
NF-11 -> C4 `c2175bb`; NF-12 -> C4 `c2175bb`. All are ancestors of `3188a11`.

### Observers present at 3188a11

`tests/test_closure_warrant.py` (673 lines) defines `legacy_value_digest`, `reviewed_sha`,
`state_completeness_problems`, `register_integrity_problems`, `closure_problems`, and the classes
`TheRecordAsCommitted`, `StateCompletenessMutations`, `ClosureWarrantMutations`,
`RegistrationDoesNotConferAuthority`. The `if __name__ == "__main__"` guard is at line 672 of 673,
i.e. the last statement, so the module has no split-collection defect at this object.

### Mandatory execution path

`.github/workflows/controlled-spec-gates.yml` runs `python -m unittest discover -s tests -v` at
**step 4** of job `structural-gates`, with no `continue-on-error` and no `if` condition. The evidence
reconciler, which stands substantively nonzero, is at **step 13**. Step 4 therefore precedes the
standing blocker, and the observers relied on by all six findings are on the mandatory execution
path at this object.

---

## 4. Per-finding determinations

### Finding: NF-01

**Determination: SUPPORTED**

**Reviewed object:** `3188a11443e33c8c4f68933cf73282108957f356`

**Claim reviewed.** CLAUDE.md recorded that `check_path_citations.scanned_files()` resolves a
105-file population. The number was manually maintained and had already stopped describing what a
clone resolves. The repair proposition is that the fragile literal was *removed* rather than
corrected, that the authoritative population is the function, and that a derived statement cannot go
stale the way a transcribed number does.

**Evidence.**

- A search of CLAUDE.md at `3188a11` for any numeric scanned-population claim (regex over two-or-more
  digit numbers adjacent to `file|path|member|record|scanned`) returns **nothing**.
- The literal `105` does not occur in CLAUDE.md, `tools/`, `tests/` or `spec/`.
- The replacement text names the function and states a membership property:
  "`check_path_citations.scanned_files()` resolves a population that contains all nine of them ...
  That function is the authoritative definition of the scanned population - run it rather than
  quoting a number, because a transcribed cardinality goes stale the moment the tree changes and it
  will not announce that it has."
- The function was executed in this cold clone rather than quoted. `scanned_files()` resolves
  **104** files. That number appears nowhere in CLAUDE.md.
- The load-bearing membership claim was measured: of the 9 files in
  `mps/materialization/mps-mat-009/`, **9 of 9** are members of the resolved population; none
  missing.
- The finding's own historical measurements are object-scoped by key name:
  `independently_measured` carries `cold_clone_at_58d18db` and `working_tree_at_58d18db`;
  `confirmed_after_repair` carries `cold_clone_at_63694e5` and `working_tree_at_63694e5`. No
  measurement is presented as an evergreen fact.
- `tools/spec/check_path_citations.py` exits **0** at this object (132 distinct cited paths, 5
  declared absent with a recorded status).

**Counterexample / mutation result.** The adversarial question put was whether an equivalent unscoped
live count had simply moved elsewhere inside NF-01's repaired proposition. The candidate is the
phrase "all nine of them", which is a transcribed membership cardinality that no control checks. It
was tested by measurement and by history:

- at `3188a11` it is accurate: 9 records, 9 members;
- **LATER-HISTORY EVIDENCE**, used only to test whether the repair was incomplete: the
  `mps/materialization/mps-mat-009` record count is **9 at every object from `3188a11` through
  `5ec6b5f`**, and CLAUDE.md continues to say "all nine of them" at each. The fragility is therefore
  unrealized across the entire subsequent history examined.

The distinction that decides the determination is that the withdrawn literal described a *scanned
population* whose size varies with tree state and derived output (measured at 103, 104, 105 and 106
across clones and working trees), whereas the surviving phrase describes *membership of an
enumerable controlled set* that changes only by deliberate addition of a controlled record.

**Residual:** The phrase "all nine of them" in CLAUDE.md is a transcribed membership cardinality that
no control verifies. It is accurate at `3188a11` and remained accurate at every later object
examined, so the residual is latent rather than realized. It is a weaker instance of the class NF-01
records, and is noted so that a later actor adding a tenth controlled record to
`mps/materialization/mps-mat-009/` knows the sentence must be revisited.

**Closure implication:** REPAIR SUPPORTED BUT RESIDUAL REMAINS.

---

### Finding: NF-05

**Determination: SUPPORTED**

**Reviewed object:** `3188a11443e33c8c4f68933cf73282108957f356`

**Claim reviewed.** `closed_by` held the warrant for a finding's closure as a sentence describing an
independent review. Nothing read it. No instrument checked that the review it named existed, that it
had reviewed the object the finding claimed as its repair, or that it had returned a passing verdict.
The repair proposition is that this is replaced by a typed `closure_review` reference resolved
against the controlled review register, with the prose retained as `closure_note` and explicitly
non-authoritative, parsed by no observer.

**Evidence.**

- `closure_problems` at `3188a11` reads `required_field` from the register's own `closure_rule`
  (`closure_review`) rather than carrying its own copy of the rule, and for every canonically CLOSED
  finding without that field emits: *"is CLOSED with no closure_review; prose cannot constitute
  closure warrant"*.
- `closure_note` is carried by 9 findings (`MI-R-01`..`MI-R-05`, `RT-F-03`..`RT-F-06`) and the string
  `closure_note` does **not** occur in the source of `closure_problems`. No observer parses it.
- Over the record as committed, `closure_problems` returns **clean**.

**Counterexample / mutation result.** Three mutations, all on in-memory copies, targeting `RT-F-03`:

| mutation | result |
|---|---|
| typed `closure_review` removed, replaced by a deliberately convincing `closure_note` ("Independently reviewed and verified by the MPS-MAT-009 reviewer on 2026-08-20.") | **REFUSED** |
| typed field present but empty string | **REFUSED** |
| typed field present but null | **REFUSED** |

Prose does not close a finding, and an empty or null typed field is treated as no warrant rather than
as a satisfied one.

**Residual: NONE.**

This requires an explicit statement, because it is the one point at which this review materially
diverges from later remediation-authored metadata, and the governing brief specifically directed that
prior summaries not be assumed correct on this question.

**At `3188a11`, NF-05 carries no residual and makes no claim about the 25-record state-debt
population.** Its key set is exactly `[acceptance_blocking, claim, disposition, id, locus, origin,
primary_artifact_retention, repair, reviewed_object, state, title]` - there is **no `residual`
key**. A text scan of the entire NF-05 record finds no occurrence of `25`, `state debt`,
`state-debt`, `queue`, `adjudicat`, or `NF-09`. NF-05's whole proposition is the typed-reference
replacement quoted above.

The 25-record queue belongs to **NF-09**, and the register says so in NF-10's own residual at this
object: *"it does not reduce the 25-record state debt by one. NF-09 still carries that queue."*
Later `independent_review_support` prose attributing a 25-record residual to NF-05 does not reflect
NF-05's proposition as it stands at the reviewed object.

**Closure implication:** NOT ASSESSED BY THIS REVIEW. The repair proposition is supported and no
residual attaches to it; whether the finding is disposed of is a governance act outside this review.

---

### Finding: NF-06

**Determination: SUPPORTED**

**Reviewed object:** `3188a11443e33c8c4f68933cf73282108957f356`

**Claim reviewed.** Because closure warrant was unresolved prose, a finding could be closed by
asserting that a review had occurred; the assertion did not have to be true and nothing in the
repository could tell the two cases apart. The repair proposition is a population-driven
closure-warrant observer requiring, for every finding in canonical CLOSED state, exactly one
registered review whose reviewed object equals the finding's repair object and whose verdict is in
the controlled closing set, with mutation controls proving each failure mode.

**Evidence.**

- The four canonically CLOSED findings at this object each resolve: `closure_review`
  `REV-RT-F-CLOSURE`, repair `7ad9b81e3bd7...`, reviewed object `7ad9b81e3bd7...`, exact match true,
  verdict `INDEPENDENTLY VERIFIED`, declared reviewable unit true, retention `external_not_retained`.
- `closure_problems` compares `reviewed_sha(review)` against `finding.get("repair")` with a plain
  `!=`. There is no ancestry test, no prefix comparison, no case folding, and no selection among
  multiple reviews.
- `register_integrity_problems` and `state_completeness_problems` both return clean over the record
  as committed.
- The observer's population is every finding whose canonical state equals the rule's applicable
  state, read from the register rather than hard-coded.

**Counterexample / mutation result.** Fifteen mutations, all refused:

| mutation | result |
|---|---|
| dangling reference to a review not in the register | REFUSED |
| reviewed object != repair object: parent commit | REFUSED |
| reviewed object != repair object: descendant commit | REFUSED |
| reviewed object != repair object: 12-character abbreviation | REFUSED |
| reviewed object != repair object: 7-character abbreviation | REFUSED |
| reviewed object != repair object: uppercase SHA | REFUSED |
| reviewed object != repair object: unknown object (40 zeros) | REFUSED |
| verdict `FAIL` | REFUSED |
| verdict `PENDING` | REFUSED |
| verdict `PASSED` (near-miss synonym) | REFUSED |
| verdict `INDEPENDENTLY  VERIFIED` (double space, near-miss) | REFUSED |
| duplicate review id in the register | REFUSED - surfaced as ambiguity, not resolved by choosing |
| review entry present but not a declared reviewable unit | REFUSED |
| invalid evidence retention status | REFUSED |
| finding names no repair object at all | REFUSED |

The abbreviated and uppercase cases matter because they are the forms under which an approximate
match would most plausibly be mistaken for an exact one. Both fail. The duplicate-id case is refused
by surfacing the ambiguity rather than by selecting a first or latest match.

**Residual:** Two, both material to a later disposition decision.

1. **A disclosed instance of NF-06's own condition stands in the committed record.** The finding's
   `note_on_rt_f_06` records that `RT-F-06` was moved to CLOSED at `7ad9b81`, the same commit that
   repaired it, and therefore before any independent review of that commit existed; its warrant was
   bound afterwards to the review that did review `7ad9b81`. The warrant resolves correctly under
   the mechanism, but the closure preceded the warrant in time. The observer compares object
   identity and verdict; it has no temporal input and cannot detect closure-before-warrant. The
   record discloses this rather than smoothing it over, which is the correct handling, but it
   remains an unrepaired condition of the kind NF-06 names.
2. **NF-06's support at this object is conditional on NF-10 and NF-11** - see section 5.

**Closure implication:** REPAIR SUPPORTED BUT RESIDUAL REMAINS.

---

### Finding: NF-10

**Determination: SUPPORTED**

**Reviewed object:** `3188a11443e33c8c4f68933cf73282108957f356`

**Claim reviewed.** C1 declared each state exception with `observed_state: absent` and nothing
checked that assertion against the record it exempted, so a legacy closure claim could sit inside
declared state debt, invisible both to the state layer and to the closure layer. The repair
proposition is that each exception now declares, per legacy field, whether it is present and the
sha256 of its exact value, and that the observer checks the declaration against the record.

**Evidence.**

- `state_completeness_problems` at `3188a11` iterates the declared `legacy_fields` (`status`,
  `disposition`) for every exception, requires a `legacy_representation` dict, requires each field's
  claim to carry a `present` key, and compares a declared `sha256` against `legacy_value_digest` of
  the record's actual value.
- **All 50 declarations (25 exceptions x 2 legacy fields) were independently recomputed** using a
  re-implementation of the declared encoding written for this review rather than by calling the
  repository's function. **Zero mismatches** in presence or digest.
- 11 legacy fields are declared present across the population; each digest matches.
- The specific counterexample NF-10 names is now truthfully declared: `MI-R-01` through `MI-R-05`
  each carry `disposition: closed` and each is declared `present: true` with a matching digest;
  `F5-FU-02` carries a prose disposition and is likewise truthfully declared.
- **Legacy values confer no lifecycle state.** The canonical CLOSED population is
  `{RT-F-03, RT-F-04, RT-F-05, RT-F-06}`; the records carrying legacy `disposition: closed` are
  `{MI-R-01..MI-R-05}`; the intersection is **empty**. No legacy closure claim was promoted into
  canonical CLOSED to make an observer pass, which is what the finding's
  `what_was_deliberately_not_done` undertakes.

**Counterexample / mutation result.** Seven mutations, all refused:

| mutation | result |
|---|---|
| declare `disposition` absent while the record carries `closed` | REFUSED |
| declare present with a wrong digest (64 zeros) | REFUSED |
| exception with no `legacy_representation` at all | REFUSED |
| `legacy_representation` silent about `disposition` | REFUSED |
| exception with an empty `reason` | REFUSED |
| exception declared for a finding id that does not exist | REFUSED |
| record both canonically stated and declared a state exception | REFUSED |

**Residual:** The observer establishes that an exception describes its record truthfully. It does not
establish that the reason given is a good one, and it does not reduce the state-debt population by
one record. **25 records remain state debt at this object**, including the five carrying
`disposition: closed`, and their adjudication is unperformed. The finding's own residual states this
and assigns the queue to NF-09.

**Closure implication:** REPAIR SUPPORTED BUT RESIDUAL REMAINS.

---

### Finding: NF-11

**Determination: SUPPORTED**

**Reviewed object:** `3188a11443e33c8c4f68933cf73282108957f356`

**Claim reviewed.** `finding_state_control` declares whether each legacy field is present, and
`state_completeness_problems` determined that with `finding.get(field)`. A field written as
`disposition:` with no value is physically present and reads as `None`, so a declaration of absent
satisfied it. The repair proposition is that presence is determined by **key membership**, with the
value encoding declared once so both sides agree on what is hashed, and exact digest comparison
preserved for every field declared present.

**Evidence.**

- The observer computes `actual_present = legacy in finding` - key membership - and separately
  `actual = finding.get(legacy)` for the value. The two questions are decided by different
  expressions.
- `legacy_value_digest` encodes `None` as the literal four characters `null`. Verified numerically:
  `legacy_value_digest(None)` equals `sha256(b"null")` and does **not** equal `sha256(b"None")`, so
  Python's `str(None)` spelling has not leaked into the controlled record as the canonical spelling
  of nothing.

**Counterexample / mutation result.** The decisive matrix was run against `F1`, a record whose
exception declares `disposition` absent. The brief's four required cases were exercised and two
further falsy values were added by this reviewer:

| record state | observer result |
|---|---|
| key **absent** (baseline) | passes - correct |
| key present, value `null` | **CAUGHT** - "the record carries the key (null)" |
| key present, value `""` | **CAUGHT** |
| key present, ordinary value `closed` | **CAUGHT** |
| key present, value `0` (added by reviewer) | **CAUGHT** |
| key present, value `false` (added by reviewer) | **CAUGHT** |

A present null is **not** treated as absent, which is the precise defect NF-11 names.

The reverse direction was also tested: declaring `disposition` **present** for `MI-R-01` while
deleting the key from the record is **REFUSED** ("exception declares 'disposition' present, but the
record does not carry the key").

Finally, present-null was tested as an expressible controlled state in its own right: a record
carrying `disposition: null` with a truthful declaration of `present: true` and
`sha256 = sha256("null")` is **accepted**, while the same record declared with the `None` spelling is
**refused**. Presence, value and encoding are three separate and separately enforced questions.

**Residual: NONE.**

**Closure implication:** NOT ASSESSED BY THIS REVIEW.

---

### Finding: NF-12

**Determination: SUPPORTED**

**Reviewed object:** `3188a11443e33c8c4f68933cf73282108957f356`

**Claim reviewed.** Two statements in the controlled record had stopped being true: NF-09's residual
said "25 of 34 records remain state debt" while the population had become 39 records, 14 canonical
and 25 in debt; and `finding_state_control` described the historical heterogeneity as "two field
names" when three relevant representations existed. The repair proposition has three parts: the
NF-09 residual gives the state-debt count without a denominator and names its derivation; the
three-representation description replaces the two-field-name one; and the frozen `58d18db` discovery
baseline is preserved as measured, with an added statement of which fields it counted.

**Evidence.** Each of the three parts was checked separately, and frozen statements were
distinguished from live ones as the brief requires.

1. **NF-09 residual.** At `3188a11` it reads: *"Open. 25 records remain state debt, and that
   population is derived from `finding_state_control.exceptions` rather than transcribed here."* It
   names its derivation, gives no denominator, and quotes `"25 of 34"` only as the explicitly
   withdrawn earlier wording. The string `25 of 39` does not occur.
2. **Three-representation description.** `finding_state_control.purpose` now reads: *"Three relevant
   representations existed, not two: the canonical `state` field, a legacy `status` field, and a
   legacy `disposition` field."*
3. **Frozen baseline.** `observed_baseline` declares `measured_at: 58d18db` and states that the
   figures *"deliberately do not track the current file ... frozen rather than refreshed"*. Every
   declared figure was recomputed against its declared object `58d18db` and reproduces **exactly**:

   | declared | value | recomputed at 58d18db | match |
   |---|---|---|---|
   | `finding_records` | 34 | 34 | yes |
   | `canonical_state_records` | 9 | 9 | yes |
   | `records_with_neither_state_nor_status` | 20 | 20 | yes |
   | `legacy_lowercase_status_records` + `legacy_prose_status_records` | 3 + 2 = 5 | 5 carrying `status` | yes |

   The added `fields_counted` clarification states that the original measurement bucketed two fields
   only and that the 20 recorded as carrying neither *"in fact included six that carried a
   disposition - five of them reading closed"*. Recomputed at `58d18db`: of the 20 carrying neither
   `state` nor `status`, **6 carry a `disposition`**, and **5 of those read `closed`**
   (`MI-R-01`..`MI-R-05`). Exact match, including the disclosed limitation of the baseline's own
   scope.

**Counterexample / mutation result.** The adversarial question put was whether any stale statement
survives. A full-register search for the literal `"two field names"` returns **exactly one
occurrence**, at line 1729. Its owning record was resolved programmatically: it lies inside
**NF-12's own `claim`**, quoting the wording NF-12 records as having been stale. That is a correct
historical quotation of withdrawn text, not a live description, and the same is true of the
`"25 of 34"` occurrences. Applying the brief's rule - a frozen historical statement is not stale
merely because today's population differs - neither occurrence falsifies the repair.

A second adversarial probe examined NF-12's own claim for the defect class NF-12 is about. The claim
asserts *"the population had become 39 records, 14 canonical and 25 in debt"*. Measured across
ancestors:

| object | total | canonical | state debt |
|---|---|---|---|
| `58d18db` | 34 | (no `finding_state_control` yet) | - |
| `63694e5` (C1) | 38 | 13 | 25 |
| `5fe5b69` (C2) | 38 | 13 | 25 |
| `1db9948` (C3) | 39 | 14 | 25 |
| `c2175bb` (C4, NF-12's repair object) | 41 | 16 | 25 |
| `3188a11` (reviewed object) | 42 | 17 | 25 |

The figure `39 / 14 / 25` reproduces **exactly and only at `1db9948` (C3)** - the population at the
moment the staleness was observed, not at NF-12's own repair object and not at the reviewed object.
The claim is past-tense, which scopes it temporally, but it names no object, so a reader cannot
reproduce it without independently locating C3.

**Residual:** NF-12's `claim` carries an unscoped historical cardinality (`39 records, 14 canonical
and 25 in debt`) that reproduces only at `1db9948` and is not tied to that object in the record.
This is a weaker instance of the class NF-12 itself records and NF-01 records more generally: a
narrative cardinality without an explicit object. It does not falsify the three-part repair
proposition, each part of which was verified above, but it means the finding that corrects unscoped
narrative counts contains one.

**Closure implication:** REPAIR SUPPORTED BUT RESIDUAL REMAINS.

---

## 5. Cross-finding dependency analysis

Three dependencies were identified. None was allowed to transfer a determination.

### 5.1 NF-06 depends materially on NF-10 and NF-11

This is the significant dependency, and it was demonstrated rather than asserted.

NF-06's mechanism ranges over *"every finding in canonical CLOSED state"*. That is sound only if the
partition between canonical state and declared state debt is itself trustworthy - otherwise the rule
is, in NF-09's phrasing, a correct rule applied to an accidentally incomplete population.

A disposable clone was created and detached at **C1 `63694e5`**, the object at which NF-05 and NF-06's
mechanism landed. At that object:

- 25 exceptions existed, all in the C1-era shape `observed_state: absent`;
- **6 of them falsely declared absence while the record carried a legacy field**: `MI-R-01` through
  `MI-R-05` each carrying `disposition: closed`, and `F5-FU-02` carrying a prose disposition;
- C1's own `tests/test_closure_warrant.py` ran **28 tests and reported OK**, detecting none of it.

So at its own repair object, NF-06's closure rule was correct in form while five records asserting
their own closure in a legacy field were concealed from it by false exception declarations. The
population guarantee NF-06 depends on was established only by **NF-10** at C3 (declarations checked
against the record, per field, by digest) and refined by **NF-11** at C4 (presence decided by key
membership).

At `3188a11` all three repairs are present and were independently verified above, and the population
was measured as exhaustive, disjoint, orphan-free and truthfully declared with zero digest
mismatches across all 50 declarations. NF-06 is therefore SUPPORTED **at the reviewed object**. It
would **not** have been supportable at `63694e5`, and any future actor tempted to treat NF-06's
repair as established by its own repair-introduction commit should not do so.

### 5.2 NF-11 depends on NF-10

NF-11 refines the mechanism NF-10 introduced: NF-10 made the exception describe its record at all,
NF-11 corrected how *presence* is decided within that description. NF-10 is the substrate; NF-11 is
not independently meaningful without it. Both are present and separately verified at `3188a11`.

### 5.3 NF-12 part (c) depends on NF-10

The `fields_counted` clarification attached to the frozen baseline exists because NF-10 exposed that
the 20 records bucketed as carrying neither `state` nor `status` in fact included six carrying a
`disposition`. NF-12's third correction is downstream of NF-10's discovery and was verified against
`58d18db` above.

### 5.4 NF-01 is independent

NF-01 concerns a cardinality in CLAUDE.md and the path-citation population. It shares no mechanism
with the state or closure machinery and its determination stands alone.

---

## 6. Tests and controls executed at 3188a11

All executed from the cold clone, using repository paths as they exist at the reviewed object.

### Focused controls

| module | discovered | executed | failures | errors | result |
|---|---|---|---|---|---|
| `tests/test_closure_warrant.py` | 40 | 40 | 0 | 0 | OK |
| `tests/test_review_records.py` | 34 | 34 | 0 | 0 | OK |
| `tests/test_path_citations.py` | 4 | 4 | 0 | 0 | OK |

### Full regression

`python -m unittest discover -s tests` - **488 discovered, 488 executed, 0 failures, 0 errors,
0 skips, 0 load failures, 49.2 s, process exit 0.** The test population was derived by independent
loader enumeration rather than taken from any report.

### Controls, with source-defined exit semantics

| control | exit | interpretation |
|---|---|---|
| `tools/spec/check_path_citations.py` | 0 | valid PASS |
| `tools/repo/check_repository_hygiene.py` | 0 | valid PASS |
| `tools/spec/check_session_controls.py` | 0 | valid PASS |
| `tools/spec/report_assurance_metrics.py --check` | 0 | valid PASS |
| `tools/repo/check_workspace_location.py --enforce` | 0 | valid PASS |
| `tools/mps/check_evidence_reconciliation.py` | 1 | **valid FAIL** - substantive verdict |

The reconciler's exit semantics were read from its source rather than assumed: `return 2` is emitted
only after `MEASUREMENT INVALID` ("No verdict about the evidence is available"), `return 1` on
substantive non-reconciliation, `return 0` on success. The observed run emitted **zero** occurrences
of `MEASUREMENT INVALID` and reported *"17 of 25 declared obligations are DISCHARGED; states: OPEN=7
ATTESTED=0 OBSERVED=1 DISCHARGED=17."* This is a **valid substantive failure**, not an unavailable
measurement, and it is unrelated to the six findings adjudicated here - the seven open obligations
concern named-reviewer authority, per-link read-back, model-checker demonstrations and importer
behaviour. No malformed invocation was treated as a system verdict.

---

## 7. Summary table

| Finding | Determination | Residual | Evidence sufficient? |
|---------|---------------|----------|----------------------|
| NF-01 | SUPPORTED | Latent: "all nine of them" in CLAUDE.md is a transcribed membership cardinality no control verifies; accurate at 3188a11 and at every later object examined | yes |
| NF-05 | SUPPORTED | NONE - and specifically, NF-05 carries no state-debt residual at this object; the 25-record queue belongs to NF-09 | yes |
| NF-06 | SUPPORTED | RT-F-06's closure predates its warrant (disclosed, undetectable by the mechanism); support is conditional on NF-10 and NF-11 | yes |
| NF-10 | SUPPORTED | 25 records remain state debt and are unadjudicated; the observer does not judge the quality of an exception's reason | yes |
| NF-11 | SUPPORTED | NONE | yes |
| NF-12 | SUPPORTED | NF-12's own claim carries an unscoped historical cardinality (39/14/25) reproducing only at 1db9948 | yes |

**No finding is stated to be CLOSED. This review determines repair support only.**

Four of the six carry residuals that a later disposition actor must weigh. NF-06's residual is of a
different character from the others: it is partly a dependency statement, and partly a disclosed
standing instance of the very condition NF-06 names.

---

## 8. Context note on later remediation metadata

Per the governing rule, `REV-C5-CUMULATIVE.verified_repairs_of` and the finding-side
`independent_review_support` records were not consulted as evidence and played no part in reaching
the six determinations above. Inspected afterwards for context only, one divergence is material and
is recorded here for the transporting actor:

- Later `independent_review_support` prose attributes a **25-record state-debt residual to NF-05**.
  At the reviewed object, NF-05 has no residual key and makes no reference to that population in any
  field. The queue belongs to NF-09, as NF-10's residual states in the same register. A disposition
  actor relying on the later prose would be applying a residual to NF-05 that NF-05 does not carry.

This review makes no change to any such record and creates no replacement assertion inside the
repository.

---

## 9. Limitations

1. **Reviewer independence is partial.** The reviewer performed the C7, C8 and C9 independent
   reviews and arrives with prior expectations about several of these mechanisms, formed at a later
   object. Disclosed in full in section 1. A reviewer with no prior role in this sequence remains
   preferable.
2. **Account-level separation is not demonstrable.** All commits carry the same Git author identity
   as the workstation owner.
3. **Deictic repair values.** All six findings carry prose `repair` values ("this checkpoint, commit
   CN") that do not resolve mechanically at `3188a11`. Their objects were derived from commit
   subjects and ancestry. This review verified the *mechanisms* at `3188a11` and did not rely on the
   prose resolving.
4. **No MPS IDE was running.** No claim in this review depends on live-model read-back; none of the
   six findings concerns MPS model content.
5. **CI behaviour is derived from the workflow file** and documented GitHub Actions semantics; no
   runner was executed.
6. **Temporal ordering is unverifiable by the mechanism.** NF-06's residual (1) concerns closure
   preceding a warrant in time. The observer has no timestamp input, and this review did not attempt
   to establish commit-time ordering as a substitute.
7. **Scope.** This review adjudicates repair support at one object for six findings. It is not a
   checkpoint verdict, not a disposition, and not a review of any later object.

---

## 10. Final cleanliness

Primary historical checkout, after all work:

    HEAD                           3188a11443e33c8c4f68933cf73282108957f356  (detached)
    git status --porcelain         (empty)
    git diff --exit-code           clean, exit 0
    git diff --cached --exit-code  clean, exit 0

All record mutations were performed on **in-memory deep copies** of the loaded YAML; no controlled
file in the primary checkout was written at any point, so no restoration was required. The single
disposable clone (detached at `63694e5`, used for the section 5.1 dependency demonstration) was
verified unmodified and then removed.

Pre-execution derived state: zero of every probed kind, `build/work` absent.
Post-execution derived state, created by this review and all gitignored: 4 `__pycache__` directories,
45 `.pyc` files; `build/work` still absent; no MPS generated output created.

---

## 11. Retention

This report is retained outside the controlled repository, at:

    C:\src\nltps-independent-review-evidence\REV-3188A11-PER-FINDING.md

The next actor should transport it by exact artifact path and SHA-256, and should not infer
per-finding determinations from generic prose. The six determinations in section 7 are the output of
this review; the substance supporting each is in section 4.
