#!/usr/bin/env python3
"""Validate the Stage A MPS materialization plan and its checkpoint discipline.

The plan's value is the review boundary between checkpoints. This gate keeps that
boundary enforceable rather than aspirational:

  * every acceptance item belongs to exactly one checkpoint and is referenced only by it;
  * the package status follows from acceptance-item state rather than being asserted;
  * only the final checkpoint may contain HLR roots, so the first live-MPS commit
    cannot carry the corpus import;
  * the workspace requirement matches the relocation decision;
  * the pinned toolchain build is recorded;
  * prohibitions on patient data, credentials, and signing keys stay false.

It checks the plan, not the MPS project. MPS creates its own persistence and no
text tool authors it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

# Reachability is owned by the feature-spec gate; importing it keeps a single
# definition of "can this concept hold an instance" rather than two that can drift.
from check_concept_features import compute_reachability, load_features


REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = REPO_ROOT / "mps" / "materialization" / "stage-a-checklist.yaml"
SKELETON_PATH = REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.json"

EXPECTED_CHECKPOINTS = ["MPS-0", "MPS-1", "MPS-2", "MPS-3", "MPS-4"]
PROHIBITED_FLAGS = (
    "patient_data_permitted",
    "clinical_credentials_permitted",
    "signing_keys_permitted",
)


def collect_declared_links() -> set[tuple[str, str]]:
    """(owning concept, target concept) for every declared child and reference.

    Read across every feature specification present, for the same reason
    compute_reachability is: a link added at a later checkpoint has to be seen by a
    deferral written at an earlier one.
    """
    links: set[tuple[str, str]] = set()
    features = load_features()
    for body in features.get("languages", {}).values():
        for concept in body.get("concepts", []):
            owner = concept["name"]
            for kind in ("children", "references"):
                for feature in concept.get(kind) or []:
                    target = feature.get("target")
                    if target:
                        links.add((owner, target))
    return links


def check() -> list[str]:
    errors: list[str] = []
    plan = yaml.safe_load(PLAN_PATH.read_text(encoding="utf-8"))

    for flag in PROHIBITED_FLAGS:
        if plan.get(flag) is not False:
            errors.append(f"{flag} must be false")

    workspace = plan.get("workspace", {})
    if workspace.get("kind") != "independent_clone":
        errors.append(
            "workspace kind must be independent_clone; a linked worktree leaves the "
            "Git common directory outside the relocated tree"
        )
    if workspace.get("synchronized_directory_permitted") is not False:
        errors.append("workspace must prohibit synchronized directories")
    if workspace.get("whitespace_in_path_permitted") is not False:
        errors.append("workspace must prohibit whitespace in the path")

    pinned = plan.get("pinned_toolchain", {})
    if not pinned.get("build"):
        errors.append("pinned_toolchain.build must record the exact MPS build")

    statuses = {item.get("status") for item in plan.get("acceptance_items", [])}
    complete_count = sum(
        1 for item in plan.get("acceptance_items", []) if item.get("status") == "complete"
    )
    total_count = len(plan.get("acceptance_items", []))
    if total_count and complete_count == total_count:
        expected_status = "complete"
    elif complete_count or statuses - {"pending"}:
        expected_status = "in_progress"
    else:
        expected_status = "not_started"
    if plan.get("status") != expected_status:
        errors.append(
            f"package status is {plan.get('status')!r} but acceptance-item state implies "
            f"{expected_status!r} ({complete_count} of {total_count} complete)"
        )

    checkpoints = plan.get("checkpoints", [])
    ids = [entry["id"] for entry in checkpoints]
    if ids != EXPECTED_CHECKPOINTS:
        errors.append(f"checkpoints must be {EXPECTED_CHECKPOINTS} in order, found {ids}")

    for entry in checkpoints:
        if entry.get("commit_boundary") is not True:
            errors.append(f"{entry['id']} must be a commit boundary")

    carrying = [entry["id"] for entry in checkpoints if entry.get("contains_hlr_roots")]
    if carrying != [EXPECTED_CHECKPOINTS[-1]]:
        errors.append(
            f"only {EXPECTED_CHECKPOINTS[-1]} may contain HLR roots, found {carrying}; "
            "the first live-MPS commit shall not contain the 119 HLRs"
        )

    items = plan.get("acceptance_items", [])
    item_ids = {item["id"] for item in items}
    if len(item_ids) != len(items):
        errors.append("duplicate acceptance item identifier")

    referenced: dict[str, list[str]] = {}
    for entry in checkpoints:
        for item_id in entry.get("acceptance_items", []):
            referenced.setdefault(item_id, []).append(entry["id"])
            if item_id not in item_ids:
                errors.append(f"{entry['id']} references unknown acceptance item {item_id}")

    for item in items:
        item_id = item["id"]
        checkpoint = item.get("checkpoint")
        owners = referenced.get(item_id, [])
        if checkpoint not in EXPECTED_CHECKPOINTS:
            errors.append(f"{item_id} declares unknown checkpoint {checkpoint!r}")
        if not owners:
            errors.append(f"{item_id} is not referenced by any checkpoint")
        elif len(owners) > 1:
            # Shared ownership means neither checkpoint can be closed on its own,
            # which removes the review boundary the checkpoints exist to create.
            errors.append(
                f"{item_id} is referenced by {sorted(owners)}; an acceptance item belongs "
                f"to exactly one checkpoint"
            )
        elif owners[0] != checkpoint:
            errors.append(
                f"{item_id} declares checkpoint {checkpoint} but is referenced by "
                f"{owners[0]}"
            )
        if item.get("status") not in {"pending", "complete", "blocked"}:
            errors.append(f"{item_id} has unsupported status {item.get('status')!r}")
        if item.get("status") == "complete" and not item.get("evidence"):
            errors.append(f"{item_id} is complete without attributable evidence")

    # A proof deferral justified by non-instantiability is only honest while no instance
    # of the affected concept can exist. Once some checkpoint makes one possible, the
    # deferral has to expire and the deferred negative example has to be run, so the gate
    # fails until the record is cleared.
    #
    # This keys on instantiability, not on the orphan report. An abstract concept never
    # appears in the orphan report because it is never instantiated directly, so reading
    # the report here would call every deferral over an abstract concept stale on the day
    # it was written. An abstract concept becomes instantiable when a concrete subconcept
    # of it becomes reachable -- which for the roles.common bases is exactly MPS-3.
    reach = compute_reachability()
    not_instantiable = set(reach["concepts"]) - set(reach["instantiable"])
    known_items = {entry["id"] for entry in items}
    # Every concept any specification declares, used to detect that a semantic dependency
    # has arrived even though nothing lapses automatically on it.
    declared_concepts = set(reach["concepts"])
    declared_links = collect_declared_links()

    for item in items:
        for deferral in item.get("scoped_exclusions", []) or []:
            label = deferral.get("constraint") or deferral.get("representation_proof")
            klass = deferral.get("deferral_class")

            if klass == "non_instantiability":
                concept = deferral.get("affected_concept")
                lapsed = deferral.get("lapsed_at")
                carried = deferral.get("carried_to")
                if not concept:
                    errors.append(
                        f"{item['id']}: non-instantiability deferral {label!r} does not name "
                        f"an affected_concept; the lapse rule cannot be evaluated"
                    )
                elif lapsed:
                    # A lapse is an auditable transition, never a deletion: the obligation
                    # has to land somewhere, and it must not be declared before it is true.
                    if concept in not_instantiable:
                        errors.append(
                            f"{item['id']}: deferral {label!r} is recorded as lapsed at "
                            f"{lapsed}, but no instance of {concept} can exist yet; a "
                            f"deferral may not lapse before its affected concept is "
                            f"instantiable"
                        )
                    if not carried:
                        errors.append(
                            f"{item['id']}: deferral {label!r} lapsed at {lapsed} without a "
                            f"carried_to acceptance item; a lapsed obligation must land on a "
                            f"named checkpoint, not simply disappear"
                        )
                    elif carried not in known_items:
                        errors.append(
                            f"{item['id']}: deferral {label!r} is carried to {carried}, "
                            f"which is not an acceptance item"
                        )
                elif concept not in not_instantiable:
                    errors.append(
                        f"{item['id']}: deferral {label!r} is still active but its affected "
                        f"concept {concept} can now be instantiated; run the deferred "
                        f"negative example and clear the deferral"
                    )

            elif klass == "semantic_model_absence":
                # This class never lapses on reachability, which is exactly why it can rot
                # unnoticed. The gate cannot make the transition, but it can refuse to stay
                # quiet once the missing semantics have arrived.
                needed = deferral.get("reactivation_concept")
                watch = deferral.get("reactivation_reference")
                reactivated = deferral.get("status", "").startswith("reactivated")
                if not needed and not watch:
                    errors.append(
                        f"{item['id']}: deferral {label!r} names neither a "
                        f"reactivation_concept nor a reactivation_reference. This class does "
                        f"not lapse on reachability, so a deferral with nothing to watch "
                        f"fails by never firing, which is indistinguishable from compliance"
                    )
                if needed and needed in declared_concepts and not reactivated:
                    errors.append(
                        f"{item['id']}: deferral {label!r} was justified by the absence of "
                        f"{needed}, which is now declared. This class does not lapse "
                        f"automatically: reclassify it deliberately as an active obligation "
                        f"and name what realizes it"
                    )
                if watch and not reactivated:
                    # The missing semantics is a link, not a concept: some object has to
                    # start carrying claims into a gating decision before the control has
                    # anything to reject.
                    target = watch.get("to")
                    excluded = set(watch.get("excluding_owners") or [])
                    arrived = sorted(owner for owner, to in declared_links
                                     if to == target and owner not in excluded)
                    if arrived:
                        errors.append(
                            f"{item['id']}: deferral {label!r} was justified by nothing "
                            f"referencing {target} outside {sorted(excluded)}, but "
                            f"{arrived} now does. This class does not lapse automatically: "
                            f"reclassify it deliberately as an active obligation and name "
                            f"what realizes it"
                        )
                if reactivated:
                    if not deferral.get("realized_by"):
                        errors.append(
                            f"{item['id']}: deferral {label!r} is reactivated without naming "
                            f"realized_by; an active obligation must say what discharges it"
                        )
                    carried = deferral.get("carried_to")
                    if carried and carried not in known_items:
                        errors.append(
                            f"{item['id']}: deferral {label!r} is carried to {carried}, "
                            f"which is not an acceptance item"
                        )

    for path in plan.get("controlled_inputs", []):
        if not (REPO_ROOT / path).exists():
            errors.append(f"controlled input is missing: {path}")

    if not SKELETON_PATH.exists():
        errors.append("language skeleton blueprint is missing")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    errors = check()
    if errors:
        print("ERROR: MPS materialization plan gate failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    plan = yaml.safe_load(PLAN_PATH.read_text(encoding="utf-8"))
    complete = sum(1 for item in plan["acceptance_items"] if item["status"] == "complete")
    total = len(plan["acceptance_items"])
    print(
        f"PASS: {len(plan['checkpoints'])} checkpoints, {total} acceptance items, "
        f"{complete} complete; HLR import confined to {EXPECTED_CHECKPOINTS[-1]}; "
        f"pinned build {plan['pinned_toolchain']['build']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
