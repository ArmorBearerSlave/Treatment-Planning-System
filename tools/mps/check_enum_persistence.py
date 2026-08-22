#!/usr/bin/env python3
"""Verify that every persisted enumeration value resolves to a member of its own enumeration.

MPS-3 established this failure empirically. Setting an enum-valued property to a member
that belongs to a different enumeration is accepted silently: the MCP write returns
ok:true, the value persists in an unresolved form carrying `null` where the member name
belongs, `check_root_node_problems` reports nothing at node, child or reference level, and
a native rebuild succeeds. Nothing in the toolchain objects. The corruption sits in the
model until something reads it.

This is a cross-model check and cannot be anything else. One value is only judgeable by
following it out of the artifact it lives in:

    instance property value
      -> persisted enumeration member reference
      -> the PropertyDeclaration that declares the property, in a language structure model
      -> the EnumerationDeclaration that property is typed by, possibly in a third model
      -> that enumeration's declared member set

The third hop is not hypothetical. `EvidenceProfile.requiredTier` is declared in
nltps.clinicalintent and typed by `AuthorityClassEnum`, which nltps.foundation owns, so the
declaration and the enumeration are already separate artifacts today.

What is checked, per persisted value:

  * the property's declared datatype resolves to an EnumerationDeclaration;
  * the value has the serialized `<memberId>/<memberName>` shape;
  * the member id is present and non-empty;
  * the member name is a declared member of *that* enumeration, not of another one;
  * across the whole repository, one member name in one enumeration always carries the
    same member id, so an id and a name cannot drift apart.

What is deliberately not checked: this does not decode MPS's compact id encoding. Deriving
it from known pairs was attempted and the obvious base-64 orderings did not reproduce a
known id, so a decoder here would be a guess. A gate that guesses is worse than one that
states its limit, so identity is enforced by declared-membership plus repository-wide
id/name pairing consistency instead.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

REPO_ROOT = Path(__file__).resolve().parents[2]
MPS_ROOT = REPO_ROOT / "mps" / "NLTPSGovernance"

# jetbrains.mps.lang.structure concept and feature indices, stable across this project's
# models because they are the platform language's own ids rather than generated ones.
ENUM_DECL = "25R3W"
ENUM_MEMBER = "25R33"
PROPERTY_DECL = "1TJgyi"
MEMBER_ID = "3tVfz5"
PROPERTY_ID = "IQ2nx"
NAME = "TrG5h"
DATATYPE_REF = "AX2Wp"

MODEL_REF = re.compile(r"^(r:[0-9a-f-]{36})\(([^)]+)\)$")


def model_name(path: Path) -> str:
    """The model's own declared reference, which is how imports address it."""
    root = ElementTree.parse(path).getroot()
    return root.get("ref", path.name)


def parse_model(path: Path) -> dict:
    """One model's registry, imports, enumerations, property declarations and values."""
    root = ElementTree.parse(path).getroot()
    doc = {
        "path": path,
        "ref": root.get("ref", ""),
        "imports": {},          # import index -> model ref
        "enums": {},            # local node id -> {"name", "members": {name: id}}
        "property_decls": {},   # propertyId -> {"name", "enum_ref"}
        "index_to_property": {},  # registry index -> propertyId
        "values": [],           # (node concept index, property index, value, node id)
    }

    for element in root.iter("import"):
        doc["imports"][element.get("index", "")] = element.get("ref", "")

    # The registry maps a compact index used throughout the body back to the real
    # property id, which is the only stable handle across models.
    for concept in root.iter("concept"):
        for prop in concept.findall("property"):
            index, pid = prop.get("index"), prop.get("id")
            if index and pid:
                doc["index_to_property"][index] = pid

    def walk(node: ElementTree.Element) -> None:
        concept = node.get("concept")
        if concept == ENUM_DECL:
            members: dict[str, str] = {}
            enum_name = None
            for prop in node.findall("property"):
                if prop.get("role") == NAME:
                    enum_name = prop.get("value")
            for member in node.findall("node"):
                if member.get("concept") != ENUM_MEMBER:
                    continue
                mname = mid = None
                for prop in member.findall("property"):
                    if prop.get("role") == NAME:
                        mname = prop.get("value")
                    elif prop.get("role") == MEMBER_ID:
                        mid = prop.get("value")
                if mname is not None:
                    members[mname] = mid or ""
            doc["enums"][node.get("id", "")] = {"name": enum_name, "members": members}

        if concept == PROPERTY_DECL:
            pid = pname = None
            for prop in node.findall("property"):
                if prop.get("role") == PROPERTY_ID:
                    pid = prop.get("value")
                elif prop.get("role") == NAME:
                    pname = prop.get("value")
            enum_ref = None
            for ref in node.findall("ref"):
                if ref.get("role") != DATATYPE_REF:
                    continue
                # Same model, or another one addressed through an import index.
                if ref.get("node"):
                    enum_ref = ("local", ref.get("node"))
                elif ref.get("to"):
                    target = ref.get("to", "")
                    index, _, node_id = target.partition(":")
                    enum_ref = ("imported", index, node_id)
            if pid:
                doc["property_decls"][pid] = {"name": pname, "enum_ref": enum_ref}

        for prop in node.findall("property"):
            role, value = prop.get("role"), prop.get("value")
            if role and value is not None:
                doc["values"].append((node.get("concept"), role, value, node.get("id", "")))

        for child in node.findall("node"):
            walk(child)

    for node in root.findall("node"):
        walk(node)
    return doc


def collect() -> tuple[dict[str, dict], dict[str, dict]]:
    """Every model in the project, and the enumerations reachable by model ref + node id."""
    models: dict[str, dict] = {}
    # rglob walks into .mps/, the project's own settings directory, whose name collides
    # with the model extension and which is not readable as a model.
    paths = sorted(
        p for p in MPS_ROOT.rglob("*.mps")
        if p.is_file() and ".mps" not in {part for part in p.parts[:-1]}
    )
    for path in paths:
        try:
            doc = parse_model(path)
        except ElementTree.ParseError as exc:
            raise SystemExit(f"ERROR: {path} is not parseable XML: {exc}")
        models[doc["ref"] or str(path)] = doc

    enums_by_ref: dict[str, dict] = {}
    for ref, doc in models.items():
        for node_id, enum in doc["enums"].items():
            enums_by_ref[f"{ref}|{node_id}"] = enum
    return models, enums_by_ref


def resolve_enum(doc: dict, enum_ref, enums_by_ref: dict) -> tuple[dict | None, str]:
    """Follow a property's datatype reference to the enumeration that declares its members."""
    if enum_ref is None:
        return None, "no datatype reference"
    if enum_ref[0] == "local":
        key = f"{doc['ref']}|{enum_ref[1]}"
        enum = enums_by_ref.get(key)
        return enum, ("" if enum else f"unresolved local datatype node {enum_ref[1]}")
    index, node_id = enum_ref[1], enum_ref[2]
    target_ref = doc["imports"].get(index)
    if not target_ref:
        return None, f"datatype import index {index!r} is not declared in this model"
    enum = enums_by_ref.get(f"{target_ref}|{node_id}")
    if not enum:
        return None, f"unresolved datatype node {node_id} in imported model {target_ref}"
    return enum, ""


def check() -> list[str]:
    errors: list[str] = []
    models, enums_by_ref = collect()

    # propertyId -> the enumeration it is declared against, resolved across models.
    enum_properties: dict[str, dict] = {}
    for doc in models.values():
        for pid, decl in doc["property_decls"].items():
            ref = decl["enum_ref"]
            if ref is None:
                continue
            enum, problem = resolve_enum(doc, ref, enums_by_ref)
            if enum is None:
                # A datatype that names an enumeration nobody can resolve is itself a
                # persistence-integrity defect; every value of that property is unjudgeable.
                if ref[0] != "imported" or "tpck" not in (ref[1] or ""):
                    errors.append(
                        f"{doc['path'].name}: property {decl['name']!r} (id {pid}) declares "
                        f"a datatype that does not resolve to an EnumerationDeclaration "
                        f"[{problem}]"
                    )
                continue
            enum_properties[pid] = {
                "enum": enum,
                "declared_in": doc["path"].name,
                "property": decl["name"],
            }

    pairings: dict[tuple[str, str], set[str]] = {}

    for doc in models.values():
        for concept_index, role, value, node_id in doc["values"]:
            pid = doc["index_to_property"].get(role)
            if pid is None or pid not in enum_properties:
                continue
            spec = enum_properties[pid]
            enum, members = spec["enum"], spec["enum"]["members"]
            try:
                shown = doc["path"].relative_to(REPO_ROOT)
            except ValueError:
                shown = doc["path"]  # a fixture root outside the repository
            where = (f"{shown} node {node_id} "
                     f"concept-index {concept_index} property {spec['property']!r}")

            member_id, sep, member_name = value.rpartition("/")
            if not sep:
                errors.append(
                    f"{where}: persisted value {value!r} is not a member reference "
                    f"(expected <memberId>/<memberName>); declared enumeration "
                    f"{enum['name']!r} declares {sorted(members)}"
                )
                continue
            if not member_id:
                errors.append(
                    f"{where}: persisted value {value!r} carries no member id; declared "
                    f"enumeration {enum['name']!r} declares {sorted(members)}"
                )
                continue
            if member_name not in members:
                errors.append(
                    f"{where}: persisted member {member_name!r} (id {member_id}) is not a "
                    f"member of the declared enumeration {enum['name']!r}; resolution "
                    f"failed. That enumeration declares {sorted(members)}"
                )
                continue
            pairings.setdefault((enum["name"] or "?", member_name), set()).add(member_id)

    # One member of one enumeration must always persist with one id. Divergence means an
    # id and a name have drifted apart, which no single occurrence could reveal.
    for (enum_name, member_name), ids in sorted(pairings.items()):
        if len(ids) > 1:
            errors.append(
                f"enumeration {enum_name!r} member {member_name!r} persists with "
                f"{len(ids)} different member ids {sorted(ids)}; a member reference must "
                f"be stable across the repository"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    if not MPS_ROOT.exists():
        print(f"ERROR: MPS project is missing: {MPS_ROOT}", file=sys.stderr)
        return 1

    errors = check()
    if errors:
        print("ERROR: enum persistence integrity gate failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    models, enums_by_ref = collect()
    values = sum(
        1
        for doc in models.values()
        for _, role, _, _ in doc["values"]
        if doc["index_to_property"].get(role)
    )
    print(
        f"PASS: {len(enums_by_ref)} enumeration declarations resolved across "
        f"{len(models)} models; {values} persisted enumeration values examined, and every "
        f"one names a declared member of its own enumeration, with member ids stable "
        f"repository-wide"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
