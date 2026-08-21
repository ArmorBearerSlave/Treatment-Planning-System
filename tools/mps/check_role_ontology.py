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

MPS-3 adds a third group, on the same activation rule. The professional projection
languages consume the authorization model and must not restate it, so the projection
checks refuse a projection concept that references RoleCapability, AuthorityPolicy or
AuthorizedActor, that carries an enumeration owned by a semantic-core language, that makes
a review surface actionable, or that lets one profession express another profession's
interaction. Those are architectural invariants: they belong to the blueprint and the
specification, not to an MPS checking rule written after the fact.
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
PROJECTION_PATH = REPO_ROOT / "mps" / "bootstrap" / "mps3-concept-features.yaml"

# The projection layer references governed state; it never restates who may act on it.
AUTHORIZATION_CONCEPTS = {"RoleCapability", "AuthorityPolicy", "AuthorizedActor"}
# A professional projection names its context with the credential concept. OperationalRole
# is the workflow function and RoleCapability is the authorized binding; using either here
# would collapse the separation mps2-role-ontology.yaml exists to preserve.
CONTEXT_TARGET = "ProfessionalRole"
PRIMITIVES = {"string", "integer", "boolean"}
# Approval and release are decided by the governed workflow. A profession whose surface
# has no business expressing them must not have a member that says otherwise.
FORBIDDEN_KIND_SUBSTRINGS = {
    "nltps.roles.dosimetry": ("approval", "approve", "release", "authorize"),
    "nltps.roles.therapy": ("approval", "approve", "release", "authorize"),
}

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


def check_projection_languages() -> tuple[list[str], bool]:
    """Architectural invariants for the MPS-3 professional projection languages.

    Inactive until mps3-concept-features.yaml exists, for the same reason as the MPS-2
    specification checks: a gate reporting success over an absent file has checked nothing.
    """
    if not PROJECTION_PATH.exists():
        return [], False

    spec = load(PROJECTION_PATH)
    errors: list[str] = []
    languages = spec.get("languages", {})
    own_types = {t["name"]: t.get("owner") for t in spec.get("datatypes", [])}

    kind_members: dict[str, set[str]] = {}
    for datatype in spec.get("datatypes", []):
        kind_members[datatype["name"]] = set(datatype.get("values", []))

    # Each profession's interaction vocabulary must be its own. Sharing a member would
    # make the boundary between clinical approval and technical release a convention.
    names = list(kind_members)
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            shared = kind_members[left] & kind_members[right]
            if shared:
                errors.append(
                    f"{left} and {right} share interaction kinds {sorted(shared)}; the "
                    f"professional surfaces would no longer be structurally distinct"
                )

    for language, body in languages.items():
        rootable = [c["name"] for c in body.get("concepts", []) if c.get("rootable")]
        if len(rootable) != 1:
            errors.append(
                f"{language} declares {len(rootable)} rootable concepts {sorted(rootable)}; "
                f"a professional language provides exactly one concrete projection root"
            )
        for concept in body.get("concepts", []):
            label = f"{language}.{concept['name']}"
            if concept.get("rootable") and concept.get("abstract"):
                errors.append(
                    f"{label} is both abstract and rootable; that advertises a root "
                    f"nobody can instantiate"
                )

            for link in concept.get("references", []) or []:
                if link.get("target") in AUTHORIZATION_CONCEPTS:
                    errors.append(
                        f"{label}.{link.get('name')} references "
                        f"{link.get('target')}, an authorization concept. The projection "
                        f"layer consumes authorization decisions and never restates the "
                        f"policy model; seeing a command is not permission to run it"
                    )
                if link.get("name") == "intendedRole" and link.get("target") != CONTEXT_TARGET:
                    errors.append(
                        f"{label}.intendedRole targets {link.get('target')!r}, not "
                        f"{CONTEXT_TARGET}; professional context is a credential, not a "
                        f"workflow function or an authorized binding"
                    )

            for prop in concept.get("properties", []) or []:
                declared = prop.get("type")
                if declared in PRIMITIVES:
                    continue
                owner = own_types.get(declared)
                if owner is None:
                    errors.append(
                        f"{label}.{prop.get('name')} is typed {declared!r}, an enumeration "
                        f"this specification does not own. A projection concept may carry "
                        f"only a primitive or its own language's enumeration; carrying a "
                        f"semantic-core enumeration would re-express authority in the "
                        f"projection layer"
                    )
                elif owner != language:
                    errors.append(
                        f"{label}.{prop.get('name')} is typed {declared!r}, owned by "
                        f"{owner}; one profession would be expressing another's "
                        f"interaction vocabulary"
                    )

            # A review surface is read-only by construction, not by a flag an instance
            # could flip.
            if concept["name"].endswith("View"):
                for child in concept.get("children", []) or []:
                    if child.get("target") == "ActionRef":
                        errors.append(
                            f"{label} contains ActionRef; a professional view is a "
                            f"read-only review surface and carries no action"
                        )

        forbidden = FORBIDDEN_KIND_SUBSTRINGS.get(language)
        if forbidden:
            for concept in body.get("concepts", []):
                for prop in concept.get("properties", []) or []:
                    for member in kind_members.get(prop.get("type"), set()):
                        if any(word in member for word in forbidden):
                            errors.append(
                                f"{language} interaction kind {member!r} reads as an "
                                f"approval or release; this surface prepares and verifies "
                                f"work, it does not authorize it"
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
    projection_errors, projection_present = check_projection_languages()
    errors.extend(projection_errors)

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
    if projection_present:
        print(
            "       mps3-concept-features.yaml keeps the projection layer free of "
            "authorization features, and the four professional surfaces disjoint"
        )
    else:
        print(
            "       mps3-concept-features.yaml not yet drafted; the projection "
            "checks are inactive, not passing"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
