#!/usr/bin/env python3
"""Enforce the frozen MPS-2 role and authorization ontology.

The profession-to-function mapping is derived from RoleCapability nodes owned by
AuthorityPolicy, never stored on ProfessionalRole. Written as prose that rule survives
only as long as whoever drafts mps2-concept-features.yaml remembers it, and the drafting
pass is exactly where the convenient shortcut -- give ProfessionalRole a list of
operational roles -- looks harmless.

Two things are checked, and they become active at different times:

  now      the blueprint carries the concepts the frozen shape needs, and none of the
           superseded ones it replaces
  later    once mps2-concept-features.yaml exists, the specification obeys the
           normalization rule and the atomic tuple shape

Until that file exists the specification checks report as not yet drafted. They do not
silently pass, because a gate that reports success over a file that does not exist is
indistinguishable from one that checked nothing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
FREEZE_PATH = REPO_ROOT / "mps" / "bootstrap" / "mps2-role-ontology.yaml"
BLUEPRINT_PATH = REPO_ROOT / "mps" / "bootstrap" / "language-skeleton.json"
FEATURES_PATH = REPO_ROOT / "mps" / "bootstrap" / "mps2-concept-features.yaml"

SUPERSEDED = {
    "Role": "ProfessionalRole and OperationalRole",
    "Permission": "RoleCapability",
}


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def check_blueprint(freeze: dict, blueprint: dict) -> list[str]:
    errors: list[str] = []
    clinical = next(
        (e for e in blueprint["languages"] if e["name"] == "nltps.clinicalintent"), None
    )
    if clinical is None:
        return ["nltps.clinicalintent is not declared in the blueprint"]
    names = set(clinical["root_concepts"]) | set(clinical["non_root_concepts"])

    for required in ("AuthorityPolicy", "RoleCapability", "ProfessionalRole",
                     "OperationalRole", "AuthorizedActor"):
        if required not in names:
            errors.append(f"nltps.clinicalintent does not declare {required}")

    for superseded, replacement in SUPERSEDED.items():
        if superseded in names:
            errors.append(
                f"nltps.clinicalintent still declares {superseded}, which {replacement} "
                f"supersedes; a concept with no remaining semantics inflates the ceiling"
            )

    # Every reference target the frozen tuple names must be a real declared concept.
    declared = {
        name
        for entry in blueprint["languages"]
        for name in entry["root_concepts"] + entry["non_root_concepts"]
    }
    for concept, shape in freeze["frozen_shape"].items():
        for link in list(shape.get("references", [])) + list(shape.get("children", [])):
            if link["target"] not in declared:
                errors.append(
                    f"{concept}.{link['name']} targets {link['target']}, which no "
                    f"language declares"
                )

    expected = freeze["inventory_impact"]["clinicalintent_concepts"]
    if len(names) != expected:
        errors.append(
            f"nltps.clinicalintent declares {len(names)} concepts, but the freeze record "
            f"states {expected}"
        )
    return errors


def check_specification(freeze: dict) -> tuple[list[str], bool]:
    """Enforce the normalization rule once the MPS-2 feature specification exists."""
    if not FEATURES_PATH.exists():
        return [], False

    errors: list[str] = []
    features = load(FEATURES_PATH)
    concepts: dict[str, dict] = {}
    for body in features.get("languages", {}).values():
        for concept in body.get("concepts", []):
            concepts[concept["name"]] = concept

    professional = concepts.get("ProfessionalRole")
    if professional is None:
        errors.append("the specification declares no ProfessionalRole")
    else:
        # The whole point of the freeze: a credential must not carry authorization.
        for kind in ("children", "references"):
            for link in professional.get(kind, []):
                if link.get("target") == "OperationalRole":
                    errors.append(
                        f"ProfessionalRole.{link.get('name')} links to OperationalRole; "
                        f"the profession-to-function mapping is derived from "
                        f"RoleCapability nodes owned by AuthorityPolicy, never stored on "
                        f"the credential"
                    )

    capability = concepts.get("RoleCapability")
    if capability is None:
        errors.append("the specification declares no RoleCapability")
    else:
        frozen = {
            link["name"]: link
            for link in freeze["frozen_shape"]["RoleCapability"]["references"]
        }
        actual = {link["name"]: link for link in capability.get("references", [])}
        for name, link in frozen.items():
            found = actual.get(name)
            if found is None:
                errors.append(f"RoleCapability does not reference {name}")
                continue
            if found.get("target") != link["target"]:
                errors.append(
                    f"RoleCapability.{name} targets {found.get('target')}, frozen as "
                    f"{link['target']}"
                )
            if found.get("cardinality") != link["cardinality"]:
                errors.append(
                    f"RoleCapability.{name} has cardinality {found.get('cardinality')}, "
                    f"frozen as {link['cardinality']}; the tuple is atomic"
                )
        for name in sorted(set(actual) - set(frozen)):
            errors.append(
                f"RoleCapability.{name} is not part of the frozen atomic tuple"
            )
        if capability.get("children"):
            errors.append(
                "RoleCapability declares children; an atomic authorization tuple holds "
                "scalar references only, and multiplicity lives in the collection of "
                "capability nodes under AuthorityPolicy"
            )

    # Without an autonomy discriminator the GOV-C-007 predicate has nothing to read, and
    # its deferral reactivates at MPS-2 into a constraint nobody could satisfy.
    autonomy = next(
        (d for d in freeze["datatypes"] if d["name"] == "AutonomyLevelEnum"), None
    )
    declared_types = {d["name"] for d in features.get("datatypes", [])}
    if autonomy and "AutonomyLevelEnum" not in declared_types:
        errors.append(
            "the specification declares no AutonomyLevelEnum; GOV-C-007 turns on "
            "action.autonomyLevel and AuthorityClassEnum carries no autonomy semantics"
        )
    action = concepts.get("ActionDefinition")
    if action is not None:
        carried = {
            prop["name"]: prop for prop in action.get("properties", [])
        }.get("autonomyLevel")
        if carried is None:
            errors.append(
                "ActionDefinition does not carry autonomyLevel; the GOV-C-007 "
                "discriminator would be unreadable"
            )
        elif carried.get("type") != "AutonomyLevelEnum":
            errors.append(
                f"ActionDefinition.autonomyLevel is typed {carried.get('type')}, frozen "
                f"as AutonomyLevelEnum"
            )
    for concept in concepts.values():
        for prop in concept.get("properties", []):
            if prop.get("name") == "autonomyLevel" and prop.get("type") == "AuthorityClassEnum":
                errors.append(
                    f"{concept['name']}.autonomyLevel is typed AuthorityClassEnum; the "
                    f"evidence precedence tier and the autonomy ladder are different axes"
                )

    # targetScope names a concept whose instances the capability points at. If nothing
    # can host a ClinicalObjectType, PrescriptionIntent and CandidatePlan cannot exist and
    # the reference is to a concept that can never have an instance.
    import check_concept_features as cf

    scope_target = next(
        (link["target"]
         for link in freeze["frozen_shape"]["RoleCapability"]["references"]
         if link["name"] == "targetScope"),
        None,
    )
    if scope_target is not None:
        unreachable = set(cf.compute_reachability()["unreachable"])
        if scope_target in unreachable:
            errors.append(
                f"RoleCapability.targetScope references {scope_target}, which no legal "
                f"containment path reaches; its instances could never exist, so the "
                f"reference would point at an uninstantiable concept"
            )

    actor = concepts.get("AuthorizedActor")
    if actor is not None:
        for link in actor.get("references", []):
            if link.get("target") in ("ProfessionalRole", "OperationalRole"):
                if link.get("cardinality") not in ("1", "0..1"):
                    errors.append(
                        f"AuthorizedActor.{link.get('name')} is multi-valued; an actor "
                        f"node is one authorization context, and a second operational "
                        f"role is a second context instance"
                    )
    return errors, True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    if not FREEZE_PATH.exists():
        print(f"ERROR: frozen role ontology is missing: {FREEZE_PATH}", file=sys.stderr)
        return 1
    freeze = load(FREEZE_PATH)
    blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))

    errors = check_blueprint(freeze, blueprint)
    spec_errors, spec_present = check_specification(freeze)
    errors.extend(spec_errors)

    if errors:
        print("ERROR: role ontology gate failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    status = freeze["status"]
    print(
        f"PASS: role ontology {status}; clinicalintent declares "
        f"{freeze['inventory_impact']['clinicalintent_concepts']} concepts; "
        f"profession-to-function mapping is derived from RoleCapability; "
        f"GOV-C-007 reads action.autonomyLevel"
    )
    if spec_present:
        print("       mps2-concept-features.yaml obeys the normalization rule")
    else:
        print(
            "       mps2-concept-features.yaml not yet drafted; the specification "
            "checks are inactive, not passing"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
