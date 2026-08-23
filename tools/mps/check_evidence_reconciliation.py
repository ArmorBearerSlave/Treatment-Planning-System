#!/usr/bin/env python3
"""Reconcile declared evidence obligations against observed evidence, per acceptance item.

MPS-MAT-009 F2. `acceptance_mapping.<item>.evidence_required` declared what each acceptance
item's own freeze requires, and nothing in the repository read it -- not one tool, not one
test. An acceptance item could therefore be recorded complete while an obligation its own
freeze called mandatory was absent, which is exactly what happened to MPS-MAT-005D and the
GOV-C-004 literal example. The omission was predicted in writing at the freeze and then
occurred anyway, because a prediction is not an instrument.

The rule this enforces is that a declaration does not satisfy another declaration. A
sentence in an item's `evidence` list is not evidence merely because it repeats or
paraphrases the requirement, so the chain runs all the way to bytes:

    structured evidence_required declaration
      -> named acceptance item
      -> named retained evidence record
      -> artifact exists
      -> artifact content hash matches the declared digest
      -> obligation satisfied

Where the observer is a gate rather than a retained artifact, the binding is still
falsifiable: the gate file must exist and must be a declared step of the gate population, so
naming a gate that does not exist, or one nothing runs, fails here rather than passing on the
strength of having been named.

Failure modes, each independently non-passing:

    declaration with no observer            nothing watches it
    ambiguous multiple candidate records    surfaced, never resolved by choosing
    retained record absent                  the observer names a record that does not exist
    artifact absent                         the record names a file that does not exist
    hash absent                             the record names a file but declares no digest
    hash mismatch                           the artifact is not the one the record describes
    evidence belongs to wrong item          the record discharges a different item

Exit codes follow the convention the currency gate established: 0 verdict-pass,
1 verdict-fail, 2 measurement-invalid. The distinction matters here more than most places,
because a register that cannot be read is not a finding about the evidence.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import io
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTER = REPO_ROOT / "mps" / "materialization" / "evidence-obligations.yaml"
ATTESTATIONS = REPO_ROOT / "mps" / "materialization" / "process-attestations.yaml"

# The five controlled obligation states. They are DERIVED per obligation, never declared,
# because a state a record asserts about itself is the thing under repair.
DECLARED = "DECLARED"
OPEN = "OPEN"
ATTESTED = "ATTESTED"
OBSERVED = "OBSERVED"
DISCHARGED = "DISCHARGED"
# Only this one closes anything. ATTESTED and OBSERVED are both genuine states that are
# still short of satisfaction: an authority may acknowledge an obligation without
# establishing it, and an artifact may be correctly bound and still show the obligation
# unmet.
CLOSING_STATES = frozenset({DISCHARGED})
FEATURES = REPO_ROOT / "mps" / "bootstrap"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "controlled-spec-gates.yml"
SESSION_CONTROLS = REPO_ROOT / "CLAUDE.md"


class MeasurementInvalid(Exception):
    """The reconciliation could not be performed. Not a finding about the evidence."""


def load_yaml(path: Path):
    if not path.is_file():
        raise MeasurementInvalid(f"{path} is missing")
    with io.open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle.read())


def declared_obligations() -> dict[str, list[str]]:
    """Every evidence_required line, per acceptance item, across every feature freeze.

    Read across all of them rather than the latest, for the same reason reachability is:
    an obligation declared at one checkpoint is still owed at a later one.
    """
    found: dict[str, list[str]] = {}
    paths = sorted(glob.glob(str(FEATURES / "mps*-concept-features.yaml")))
    if not paths:
        raise MeasurementInvalid("no mps*-concept-features.yaml found; nothing to reconcile")
    for path in paths:
        body = load_yaml(Path(path)) or {}
        for item, mapping in (body.get("acceptance_mapping") or {}).items():
            for line in (mapping or {}).get("evidence_required") or []:
                found.setdefault(item, []).append(" ".join(str(line).split()))
    return found


def declared_gate_population() -> set[str]:
    """The gates the project declares it RUNS -- invocations, not mentions.

    The first version of this scanned both documents for any token ending in .py, which
    quietly made every script named anywhere in the session controls a member. CLAUDE.md
    discusses tools in prose -- mps_layout.py appears in a paragraph about model layout, and
    was never a gate -- so naming such a file as an obligation's observer passed. That is the
    same defect this whole reconciler exists to correct, committed by the reconciler: a check
    crediting itself with a discrimination it does not perform.

    So the population is derived from invocation shapes only: a workflow step that runs the
    script, or a `python <script>` line in the session controls' verification block. A file
    that is merely discussed is not an observer of anything.
    """
    population: set[str] = set()
    invocation = re.compile(r"python\s+(?:-m\s+\S+\s+)?([A-Za-z0-9_./-]+\.py)")
    for path in (WORKFLOW, SESSION_CONTROLS):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace").replace("\\", "/")
        for match in invocation.finditer(text):
            population.add(match.group(1))
    return population


def normalize(text: str) -> str:
    return " ".join(str(text).split())


def attestations_for(obligation_id: str) -> list[dict]:
    """Named-authority assertions about one obligation, if any exist.

    Separate from the evidence register on purpose. An attestation is governance evidence
    about who accepted what; evidence is technical evidence about what the system does. The
    two are retained apart so that neither can quietly stand in for the other.
    """
    if not ATTESTATIONS.is_file():
        return []
    body = load_yaml(ATTESTATIONS) or {}
    if body.get("attestation_discharges_obligations") is not False:
        raise MeasurementInvalid(
            "the process attestation register does not declare "
            "attestation_discharges_obligations = false. Reading it while that invariant is "
            "unstated would risk treating an acknowledgement as a discharge.")
    return [a for a in (body.get("attestations") or [])
            if a.get("obligation_id") == obligation_id]


def record_status(name: str, expected_item: str,
                  register: dict | None = None) -> tuple[bool, str]:
    """Whether one named retained record discharges one named acceptance item.

    Exposed separately because the deferral gate needs the same question answered, and two
    implementations of "is this evidence real" would drift apart -- which is the defect that
    put a substring test and a real check on the same field in the currency gate.
    """
    if register is None:
        register = load_yaml(REGISTER) or {}
    records = register.get("records") or {}
    pending = register.get("records_pending") or {}
    if name in pending and name not in records:
        return False, f"record {name!r} is declared pending and carries no artifacts"
    record = records.get(name)
    if record is None:
        return False, f"retained record absent: {name!r} is not defined in the register"
    owner = record.get("acceptance_item")
    if owner != expected_item:
        return False, (f"evidence belongs to wrong item: record {name!r} discharges "
                       f"{owner!r}, not {expected_item!r}")
    artifacts = record.get("artifacts") or []
    if not artifacts:
        return False, f"record {name!r} names no artifacts"
    for artifact in artifacts:
        relative = artifact.get("path")
        if not relative:
            return False, f"record {name!r} has an artifact with no path"
        path = REPO_ROOT / relative
        if not path.is_file():
            return False, f"artifact absent: {relative}"
        digest = artifact.get("sha256")
        if not digest:
            return False, f"hash absent: {relative} carries no declared digest"
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            return False, (f"hash mismatch: {relative} is {actual[:16]}, the record "
                           f"declares {str(digest)[:16]}")
    return True, ""



def obligation_state(item: str, index: int, entry: dict | None,
                     register: dict) -> tuple[str, str]:
    """Derive one obligation's controlled state, and the reason for it.

    Derived, never read from the record. The whole finding was that the record asserted a
    completion state it could not substantiate, so a state field the register declared about
    itself would reproduce the defect in a new place.

    The order below is the precedence: an artifact that binds AND satisfies is DISCHARGED; an
    artifact that binds without satisfying is OBSERVED and stops there; a named authority
    without an artifact is ATTESTED; anything else is OPEN. DECLARED is the floor -- every
    obligation the contract names is at least that.
    """
    obligation_id = f"{item}#{index}"
    if entry is None:
        return OPEN, "no register entry names an observer for this declaration"

    observer = entry.get("observer")

    if observer == "retained_artifact":
        name = entry.get("record")
        if not name:
            return OPEN, "observer is retained_artifact but no record is named"
        bound, why = record_status(name, item, register)
        if not bound:
            return OPEN, why
        # Bound and hash-matched. Whether it SATISFIES is a separate question, and the
        # register must say so explicitly rather than have satisfaction inferred from the
        # existence of a file.
        record = (register.get("records") or {}).get(name) or {}
        if record.get("satisfies_obligation") is True:
            return DISCHARGED, f"record {name} is bound and satisfies the obligation"
        return OBSERVED, (f"record {name} is bound and hash-matched, but is not declared to "
                          f"satisfy the obligation; binding is not satisfaction")

    if observer == "gate":
        gate = entry.get("gate")
        if not gate:
            return OPEN, "observer is gate but no gate is named"
        if not (REPO_ROOT / gate).is_file():
            return OPEN, f"named gate {gate} does not exist"
        if gate not in declared_gate_population():
            return OPEN, (f"named gate {gate} is not a declared invocation; a gate nothing "
                          f"runs observes nothing")
        return DISCHARGED, f"observed on every run by {gate}"

    # No qualifying artifact. A named authority may still have spoken.
    attestations = attestations_for(obligation_id)
    if attestations:
        who = ", ".join(sorted(a.get("authority", "<unnamed>") for a in attestations))
        return ATTESTED, (f"no qualifying artifact; asserted by {who}. An attestation is "
                          f"attributable governance evidence and is not a discharge")
    if observer == "unobserved":
        return OPEN, normalize(entry.get("why", "declared unobserved"))
    return OPEN, f"unknown observer {observer!r}"


def check() -> tuple[list[tuple[str, str]], dict]:
    """Every unreconciled obligation, as (acceptance item, why).

    Problems carry their item so a caller can ask the completion question -- does THIS item
    have unresolved required evidence -- without re-deriving the answer from message text.
    """
    problems: list[tuple[str, str]] = []
    register = load_yaml(REGISTER) or {}
    records = register.get("records") or {}
    pending = register.get("records_pending") or {}
    entries_by_item = register.get("obligations") or {}
    declared = declared_obligations()
    gates = declared_gate_population()

    tally = {"declarations": 0, "satisfied": 0, "unobserved": 0, "by_gate": 0,
             "by_artifact": 0,
             DECLARED: 0, OPEN: 0, ATTESTED: 0, OBSERVED: 0, DISCHARGED: 0}

    for item in sorted(declared):
        entries = entries_by_item.get(item) or []
        for declaration in declared[item]:
            tally["declarations"] += 1
            candidates = [e for e in entries
                          if normalize(e.get("declaration", "")) == declaration]

            if not candidates:
                tally[DECLARED] += 1
                tally[OPEN] += 1
                problems.append((item, f"declaration with no observer -- nothing in the "
                                       f"register watches {declaration!r}. An obligation no "
                                       f"instrument reads is a sentence."))
                continue
            if len(candidates) > 1:
                tally[DECLARED] += 1
                tally[OPEN] += 1
                # Surfaced, never resolved by choosing: picking one would make the
                # reconciliation depend on register ordering, and the ambiguity is the defect.
                problems.append((item, f"ambiguous multiple candidate register entries for "
                                       f"{declaration!r} ({len(candidates)} matched). Not "
                                       f"resolved here; the register must name one observer "
                                       f"per declaration."))
                continue

            entry = candidates[0]
            observer = entry.get("observer")
            state, _why = obligation_state(item, declared[item].index(declaration),
                                           entry, register)
            tally[DECLARED] += 1
            tally[state] += 1

            if observer == "unobserved":
                tally["unobserved"] += 1
                problems.append((item, f"{declaration!r} is declared required and is "
                                       f"explicitly unobserved. Reason recorded: "
                                       f"{normalize(entry.get('why', 'none given'))[:150]}"))
                continue

            if observer == "gate":
                gate = entry.get("gate")
                if not gate:
                    problems.append((item, f"{declaration!r} names observer 'gate' with no "
                                           f"gate named"))
                    continue
                if not (REPO_ROOT / gate).is_file():
                    problems.append((item, f"{declaration!r} names gate {gate}, which does "
                                           f"not exist"))
                    continue
                if gate not in gates:
                    problems.append((item, f"{declaration!r} names gate {gate}, which is not "
                                           f"a declared step of the gate population. A gate "
                                           f"nothing runs does not observe anything."))
                    continue
                tally["by_gate"] += 1
                tally["satisfied"] += 1
                continue

            if observer == "retained_artifact":
                name = entry.get("record")
                if not name:
                    problems.append((item, f"{declaration!r} names observer "
                                           f"'retained_artifact' with no record"))
                    continue
                ok, why = record_status(name, item, register)
                if not ok:
                    problems.append((item, f"{declaration!r}: {why}"))
                    continue
                tally["by_artifact"] += 1
                tally["satisfied"] += 1
                continue

            problems.append((item, f"{declaration!r} names unknown observer {observer!r}"))

    # A register entry for a declaration that no freeze declares is stale, and a stale entry
    # is how a register drifts into describing a document that no longer exists.
    for item, entries in entries_by_item.items():
        for entry in entries:
            text = normalize(entry.get("declaration", ""))
            if text not in (declared.get(item) or []):
                problems.append((item, f"register entry {text[:70]!r} matches no "
                                       f"evidence_required declaration for that item"))

    return problems, tally


def states() -> dict[str, tuple[str, str]]:
    """Every declared obligation's derived state, keyed by obligation id.

    The metrics reporter reads this rather than counting problems, because "how many are
    discharged" and "how many produced a message" are different questions and conflating
    them is how an aggregate stops describing its own population.
    """
    register = load_yaml(REGISTER) or {}
    entries_by_item = register.get("obligations") or {}
    declared = declared_obligations()
    result: dict[str, tuple[str, str]] = {}
    for item in sorted(declared):
        entries = entries_by_item.get(item) or []
        for index, declaration in enumerate(declared[item]):
            candidates = [e for e in entries
                          if normalize(e.get("declaration", "")) == declaration]
            entry = candidates[0] if len(candidates) == 1 else None
            result[f"{item}#{index}"] = obligation_state(item, index, entry, register)
    return result


def unresolved_by_item() -> dict[str, list[str]]:
    """Unreconciled obligations grouped by the acceptance item that carries them.

    MPS-MAT-009 F2, completion consequence: an item cannot be mechanically complete while an
    obligation its own freeze declares required is unresolved. The plan gate asks this
    question; it is answered here so that the definition of "unresolved" cannot differ
    between the two.
    """
    problems, _ = check()
    grouped: dict[str, list[str]] = {}
    for item, message in problems:
        grouped.setdefault(item, []).append(message)
    return grouped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args()
    try:
        problems, tally = check()
    except MeasurementInvalid as error:
        print(f"MEASUREMENT INVALID: {error}. No verdict about the evidence is available; "
              f"this is not a finding about the record.", file=sys.stderr)
        return 2

    if problems:
        print("FAIL: declared evidence obligations are not reconciled\n", file=sys.stderr)
        for item, message in problems:
            print(f"  - {item}: {message}\n", file=sys.stderr)
        print(f"{tally[DISCHARGED]} of {tally[DECLARED]} declared obligations are "
              f"DISCHARGED; states: OPEN={tally[OPEN]} ATTESTED={tally[ATTESTED]} "
              f"OBSERVED={tally[OBSERVED]} DISCHARGED={tally[DISCHARGED]}. "
              f"{len(problems)} problems. Only DISCHARGED satisfies a closure condition.",
              file=sys.stderr)
        return 1

    print(f"PASS: {tally['satisfied']}/{tally['declarations']} declared evidence obligations "
          f"reconciled -- {tally['by_artifact']} by retained artifact with matching content "
          f"hashes, {tally['by_gate']} by a declared gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
