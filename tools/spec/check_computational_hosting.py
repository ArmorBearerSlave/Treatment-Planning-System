#!/usr/bin/env python3
"""ARCH-DGX-01: structural controls over governed computational hosting.

Every control here is derived from structured records and their relationships. None is
satisfied by a sentence appearing somewhere, because a prose prohibition and an enforced
one are indistinguishable to a reader and only one of them survives a rewrite.

What this gate does NOT establish, stated so it is not read as stronger than it is. It
inspects a controlled architecture record. It does not observe a running system, a
dispatched workload, a returned result, a trained model, or a compute provider. Passing
establishes that ARCH-DGX-01 is structurally represented and allocated; it establishes
nothing about whether any of it is implemented, verified, qualified or commissioned. The
record itself carries that distinction in proposition_states and claim_boundary, and this
gate enforces that the record cannot quietly claim more.

The self-referential half is load-bearing. The architecture declares the control
identifiers it expects to be enforced, and this file declares the ones it implements. A
difference in either direction fails: a control cannot be declared without existing, and
one cannot exist without being declared. Without that, deleting a check here would leave
the architecture still advertising it.

Exit codes follow the convention the currency gate established:

    0   verdict-pass, the controls ran and found nothing
    1   verdict-fail, at least one control established a finding
    2   measurement-invalid, the controls could not be run at all

The third is not a finding about the architecture. A record that cannot be parsed has not
been shown to be wrong.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = REPO_ROOT / "spec" / "architecture.yaml"
DECISIONS = REPO_ROOT / "spec" / "decisions.yaml"
SECTION_KEY = "governed_computational_hosting"
SESSION_CONTROLS = REPO_ROOT / "CLAUDE.md"
# CLAUDE.md states these counts in prose, and prose drifts silently. The session-controls
# gate cannot know what they should be, so they are checked here against the populations
# they describe rather than left to be noticed by a person re-reading the file.
# The semantics a deployment profile may never vary. This is set membership over a
# controlled list, not a search for a sentence: dropping "model identity" from the
# declared set is the realistic failure, and it leaves prose about profiles intact.
PROFILE_INVARIANT_SEMANTICS = frozenset({
    "clinical intent",
    "authorization semantics",
    "model identity",
    "workload semantics",
    "acceptance criteria",
    "evidence obligations",
    "external TPS authority",
})
SESSION_COUNTS = (
    (re.compile(r"enforces (\d+) structural controls"), "structural controls"),
    (re.compile(r"(\d+) of the (\d+) propositions are structurally inspectable"),
     "propositions"),
)

VERDICT_PASS = 0
SUBSTANTIVE_FINDING = 1
MEASUREMENT_INVALID = 2
MARKER = "MEASUREMENT INVALID"


class MeasurementInvalid(Exception):
    """The controls could not be run. Not a finding about the architecture."""


def load(path: Path) -> dict:
    if not path.is_file():
        raise MeasurementInvalid(f"{path} is missing")
    try:
        with io.open(path, encoding="utf-8") as handle:
            document = yaml.safe_load(handle.read())
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise MeasurementInvalid(f"{path} could not be read: {exc}") from exc
    if not isinstance(document, dict):
        raise MeasurementInvalid(f"{path} is not a mapping")
    return document


def names(entries, key: str = "name") -> list:
    """Field names out of a list of {name, authorization_relevant, in_digest} records."""
    return [entry.get(key) for entry in entries or [] if isinstance(entry, dict)]


def authorization_relevant_fields(section: dict) -> set:
    """Every authorization-relevant field name, common core plus every workload class."""
    found = {
        entry["name"]
        for entry in section["governed_workload"]["canonical_fields"]
        if entry.get("authorization_relevant")
    }
    for workload_class in section["workload_classes"]["classes"]:
        found |= {
            entry["name"]
            for entry in workload_class.get("additional_canonical_fields") or []
            if entry.get("authorization_relevant")
        }
    return found


def all_declared_fields(section: dict) -> list:
    """Every field name the envelope or any class declares, in declaration order."""
    found = names(section["governed_workload"]["canonical_fields"])
    found += names(section["governed_workload"]["transport_fields"])
    for workload_class in section["workload_classes"]["classes"]:
        found += names(workload_class.get("additional_canonical_fields"))
    return found


def digest_field(section: dict):
    """The integrity-binding field name, or None.

    Absent is a substantive finding owned by CDH-01, not an unmeasurable record. The
    controls that depend on it therefore skip their digest comparison rather than raising,
    so one missing key does not convert a finding this gate can state into a measurement
    it claims it could not perform.
    """
    return (section.get("governed_workload", {}).get("integrity_binding") or {}).get("field")


def class_by_id(section: dict, identifier: str) -> dict:
    for workload_class in section["workload_classes"]["classes"]:
        if workload_class.get("id") == identifier:
            return workload_class
    raise MeasurementInvalid(f"workload class {identifier} is not declared")


def development_class(section: dict) -> dict:
    """The class that produces a model artifact. Located by what it produces."""
    found = [
        workload_class
        for workload_class in section["workload_classes"]["classes"]
        if "ModelArtifact" in (workload_class.get("produces") or [])
    ]
    if len(found) != 1:
        raise MeasurementInvalid(
            f"expected exactly one workload class producing a ModelArtifact, found {len(found)}"
        )
    return found[0]


# --------------------------------------------------------------------------
# The controls. Each takes (section, architecture, decisions) and returns findings.
# --------------------------------------------------------------------------


def cdh_01(section, architecture, decisions):
    """A governed workload exists but has no canonical digest binding."""
    findings = []
    workload = section["governed_workload"]
    binding = workload.get("integrity_binding") or {}
    if not binding.get("field"):
        findings.append("the governed workload declares no integrity-binding field")
    if not binding.get("computed_over"):
        findings.append("the integrity binding names no canonical basis to be computed over")
    canonical = workload.get("canonical_fields") or []
    if not canonical:
        findings.append("the governed workload declares no canonical fields")
    outside = [entry["name"] for entry in canonical if not entry.get("in_digest")]
    if outside:
        findings.append(f"canonical fields sit outside the digest: {sorted(outside)}")
    if section.get("canonicalization", {}).get("rule") is None:
        findings.append("no canonicalization rule accompanies the digest")
    return findings


def cdh_02(section, architecture, decisions):
    """An authorization decision is not bound to the workload digest."""
    findings = []
    digest = digest_field(section)
    contract = section["contracts"].get("AuthorizationDecision")
    if contract is None:
        return ["no AuthorizationDecision contract is declared"]
    if digest is not None and digest not in (contract.get("binds") or []):
        findings.append(f"AuthorizationDecision does not bind {digest}")
    kernels = [
        item["id"]
        for item in section["responsibility_boundary"]["responsibilities"]
        if item.get("role") == "authorization_kernel"
    ]
    if contract.get("produced_by") not in kernels:
        findings.append(
            f"AuthorizationDecision is produced by {contract.get('produced_by')}, "
            f"which is not an authorization kernel"
        )
    return findings


def cdh_03(section, architecture, decisions):
    """A dispatch contract permits an authorization-relevant field to mutate."""
    findings = []
    dispatch = section["contracts"].get("DispatchContract")
    if dispatch is None:
        return ["no DispatchContract is declared"]
    protected = authorization_relevant_fields(section)
    mutable = set(dispatch.get("mutable_fields") or [])
    leaked = sorted(mutable & protected)
    if leaked:
        findings.append(f"dispatch may mutate authorization-relevant fields: {leaked}")
    if dispatch.get("immutable_field_class") != "authorization_relevant":
        findings.append("dispatch does not declare the authorization-relevant field class immutable")
    transport = set(names(section["governed_workload"]["transport_fields"]))
    undeclared = sorted(mutable - transport)
    if undeclared:
        findings.append(f"dispatch declares mutable fields that are not transport fields: {undeclared}")
    scale_out = section.get("scale_out_invariance") or {}
    may_alter = set(scale_out.get("may_alter") or [])
    may_not = set(scale_out.get("may_not_alter") or [])
    if not may_not:
        findings.append("scale-out declares nothing it may not alter")
    if may_alter & may_not:
        findings.append(f"scale-out both permits and prohibits altering {sorted(may_alter & may_not)}")
    return findings


def cdh_04(section, architecture, decisions):
    """A result does not carry or bind the authorized workload digest."""
    findings = []
    digest = digest_field(section)
    if digest is None:
        return []
    required = {
        "ResultContract": {digest, "run_identity", "output_artifact_digests",
                           "execution_attestation_identity"},
        "ExecutionAttestation": {digest, "run_identity", "execution_attestation_identity"},
    }
    for name, expected in required.items():
        contract = section["contracts"].get(name)
        if contract is None:
            findings.append(f"no {name} is declared")
            continue
        absent = sorted(expected - set(contract.get("binds") or []))
        if absent:
            findings.append(f"{name} does not bind {absent}")
    for workload_class in section["workload_classes"]["classes"]:
        if digest not in (workload_class.get("result_binds") or []):
            findings.append(f"{workload_class['id']} results do not bind {digest}")
    chain = [tuple(pair) for pair in section["reconciliation"].get("required_equalities") or []]
    expected_chain = [
        (f"AuthorizationDecision.{digest}", f"DispatchContract.{digest}"),
        (f"DispatchContract.{digest}", f"ExecutionAttestation.{digest}"),
        (f"ExecutionAttestation.{digest}", f"ResultContract.{digest}"),
    ]
    if chain != expected_chain:
        findings.append("the reconciliation chain does not run authorization to dispatch to attestation to result")
    return findings


def cdh_05(section, architecture, decisions):
    """Provider-specific fields leak into the provider-neutral workload envelope."""
    findings = []
    neutrality = section["provider_neutrality"]
    tokens = [str(token).lower() for token in neutrality.get("provider_specific_tokens") or []]
    if not tokens:
        return ["no provider-specific tokens are declared, so neutrality cannot be checked"]
    surfaces = list(all_declared_fields(section))
    for contract in section["contracts"].values():
        surfaces += list(contract.get("binds") or [])
        surfaces += list(contract.get("mutable_fields") or [])
    for workload_class in section["workload_classes"]["classes"]:
        surfaces += list(workload_class.get("result_binds") or [])
    leaked = sorted({
        name for name in surfaces
        if name and any(token in str(name).lower() for token in tokens)
    })
    if leaked:
        findings.append(f"provider-specific names appear in the governed envelope: {leaked}")
    if not section["governed_workload"].get("provider_neutral"):
        findings.append("the governed workload does not declare itself provider-neutral")
    if section["governed_workload"].get("format_owner_is_a_provider"):
        findings.append("the workload format is owned by a provider")
    if section["compute_provider_abstraction"].get("knows_provider_api_mechanics"):
        findings.append("the compute-provider abstraction is declared to know provider API mechanics")
    return findings


def cdh_06(section, architecture, decisions):
    """A compute provider or dispatcher is assigned authorization authority."""
    findings = []
    responsibilities = section["responsibility_boundary"]["responsibilities"]
    kernels = [item for item in responsibilities if item.get("role") == "authorization_kernel"]
    if len(kernels) != 1:
        findings.append(f"expected exactly one authorization kernel, found {len(kernels)}")
    for kernel in kernels:
        if kernel.get("may_select_compute_provider"):
            findings.append(f"{kernel['id']} both authorizes and selects the compute provider")
    for item in responsibilities:
        if item.get("role") == "authorization_kernel":
            continue
        if item.get("authority") != "none":
            findings.append(f"{item['id']} holds authority {item.get('authority')!r}, expected none")
        if item.get("may_set_authorization_relevant_fields"):
            findings.append(f"{item['id']} may set authorization-relevant fields")
    producers = [
        item["id"] for item in responsibilities
        if "AuthorizationDecision" in (item.get("produces") or [])
    ]
    if producers != [kernel["id"] for kernel in kernels]:
        findings.append(
            f"AuthorizationDecision is produced by {producers}, not by the authorization kernel alone"
        )
    if section["compute_provider_abstraction"].get("authority") != "none":
        findings.append("the compute-provider abstraction holds authority")
    for profile in section["compute_provider_profiles"]:
        if profile.get("authority") != "none":
            findings.append(f"{profile['id']} holds authority {profile.get('authority')!r}, expected none")
    return findings


def cdh_07(section, architecture, decisions):
    """External TPS or professional authority is reassigned to a compute host."""
    findings = []
    abstraction = section["compute_provider_abstraction"]
    hosts = {profile["id"] for profile in section["compute_provider_profiles"]}
    hosts.add(abstraction["id"])
    hosts |= {adapter["id"] for adapter in abstraction.get("adapters") or []}
    retention = section["authority_retention"]
    subjects = retention.get("subjects") or []
    if not subjects:
        return ["no retained authority subjects are declared"]
    for subject in subjects:
        if subject.get("may_be_reassigned_to_compute_host"):
            findings.append(f"{subject['subject']} may be reassigned to a compute host")
        if subject.get("retained_by") in hosts:
            findings.append(
                f"{subject['subject']} is retained by the compute host {subject['retained_by']}"
            )
    if not retention.get("downstream_controls_unchanged"):
        findings.append("no downstream controls are declared unchanged")
    return findings


def cdh_08(section, architecture, decisions):
    """A DGX profile is present but no common scale-out interface exists."""
    findings = []
    profiles = section["compute_provider_profiles"]
    reference = [
        p for p in profiles
        if p.get("role") == "first_reference_complete_computational_host"
    ]
    if not reference:
        return []
    if len(reference) != 1:
        findings.append(f"expected one reference host profile, found {len(reference)}")
    others = [p for p in profiles if p.get("id") != reference[0].get("id")]
    if not others:
        findings.append("a reference host is declared with no scale-out target profile")
        return findings
    for profile in others:
        for key in ("abstraction", "workload_envelope"):
            if profile.get(key) != reference[0].get(key):
                findings.append(
                    f"{profile['id']} and {reference[0]['id']} do not share {key}, "
                    f"so scale-out does not run through one abstraction"
                )
        if profile.get("locality") == reference[0].get("locality"):
            findings.append(f"{profile['id']} has the same locality as the reference host")
    abstraction = section["compute_provider_abstraction"]
    if abstraction.get("workload_format_owner") != section["governed_workload"]["id"]:
        findings.append("the compute-provider abstraction does not carry the governed workload envelope")
    adapted = {adapter.get("provider_profile") for adapter in abstraction.get("adapters") or []}
    unadapted = sorted({p["id"] for p in profiles} - adapted)
    if unadapted:
        findings.append(f"profiles with no declared adapter: {unadapted}")
    for profile in profiles:
        if profile.get("semantic_owner_of_workload_format"):
            findings.append(f"{profile['id']} is declared the semantic owner of the workload format")
    return findings


def cdh_09(section, architecture, decisions):
    """Returned artifacts are never checked against the contracts the workload declared."""
    findings = []
    conformance = section.get("output_contract_conformance")
    if conformance is None:
        return ["no output-contract conformance step is declared"]
    steps = section["result_acceptance"].get("steps") or []
    if conformance["id"] not in {step.get("mechanism") for step in steps}:
        findings.append("output-contract conformance is not an acceptance step")
    for step in steps:
        if not step.get("required"):
            findings.append(f"{step['id']} is an acceptance step that is not required")
        if step.get("mechanism") == conformance["id"] and not step.get(
            "independently_establishable_by_nltps"
        ):
            findings.append(f"{step['id']} is not independently establishable, so it rests on the executor")
    distinct = set(conformance.get("distinct_from") or [])
    for other in (section["reconciliation"]["id"], section["provenance"]["id"]):
        if other not in distinct:
            findings.append(f"conformance is not declared distinct from {other}")
    checked = conformance.get("checked_against") or []
    if not checked:
        findings.append("conformance names nothing to check against")
    absent = sorted(set(checked) - set(all_declared_fields(section)))
    if absent:
        findings.append(f"conformance is checked against fields the workload does not declare: {absent}")
    return findings


def cdh_10(section, architecture, decisions):
    """The record claims the digest chain establishes what actually executed."""
    findings = []
    reconciliation = section["reconciliation"]
    if reconciliation.get("sufficiency") != "necessary_not_sufficient":
        findings.append(
            f"the reconciliation chain declares sufficiency {reconciliation.get('sufficiency')!r}; "
            f"the digest is a label the executing host copies back"
        )
    if not reconciliation.get("does_not_establish"):
        findings.append("the reconciliation chain declares nothing it does not establish")
    required_steps = [s for s in section["result_acceptance"].get("steps") or [] if s.get("required")]
    if len(required_steps) < 2:
        findings.append("the digest chain is the only required acceptance step")
    boundary = section["claim_boundary"]
    overlap = sorted(set(boundary.get("may_claim") or []) & set(boundary.get("may_not_claim") or []))
    if overlap:
        findings.append(f"the claim boundary both permits and forbids: {overlap}")
    if not boundary.get("may_not_claim"):
        findings.append("the claim boundary forbids nothing")
    return findings


def cdh_11(section, architecture, decisions):
    """A workload class defines its own mechanism, or the lifecycles are collapsed."""
    findings = []
    classes = section["workload_classes"]
    envelope = section["governed_workload"].get("id")
    digest = digest_field(section)
    if classes.get("common_mechanism") != envelope:
        findings.append("the workload classes do not share the governed workload envelope")
    if digest is not None and classes.get("common_integrity_binding") != digest:
        findings.append("the workload classes do not share the common integrity binding")
    members = classes.get("classes") or []
    if len(members) < 2:
        findings.append("model development and inference are not represented as distinct classes")
    identifiers = [member.get("id") for member in members]
    if len(identifiers) != len(set(identifiers)):
        findings.append("workload class identifiers are not unique")
    for member in members:
        if member.get("common_mechanism") != envelope:
            findings.append(f"{member['id']} declares its own integrity or dispatch mechanism")
        if not member.get("additional_canonical_fields"):
            findings.append(f"{member['id']} binds no class-specific semantic inputs")
        if member.get("confers_authorization_for_use"):
            findings.append(f"{member['id']} is declared to confer authorization for use")
        produces_model = "ModelArtifact" in (member.get("produces") or [])
        consumes_model = any(
            entry.get("name") == "qualified_model_digest"
            for entry in member.get("additional_canonical_fields") or []
        )
        if produces_model and consumes_model:
            findings.append(
                f"{member['id']} both produces a model and executes a qualified model, "
                f"which collapses development and inference into one lifecycle"
            )
    return findings


def cdh_12(section, architecture, decisions):
    """A dataset is identified by a path, or its manifest binds no integrity digest."""
    findings = []
    governance = section["dataset_governance"]
    if governance.get("identity_by_path_or_directory_name") != "prohibited":
        findings.append("dataset identity by path or directory name is not prohibited")
    if not governance.get("effective_change_produces_new_identity"):
        findings.append("an effective dataset change is not declared to produce a new identity")
    if not governance.get("dataset_is_a_first_class_governed_asset"):
        findings.append("a dataset is not declared a first-class governed asset")
    expected = {
        "constituent_data_identities", "dataset_version_identity", "provenance_and_source",
        "labeling_provenance", "permitted_use", "preprocessing_state",
        "inclusion_exclusion_criteria", "partition_assignment", "integrity_digest",
    }
    absent = sorted(expected - set(governance.get("required_bindings") or []))
    if absent:
        findings.append(f"the dataset manifest binds none of {absent}")
    fields = {entry["name"] for entry in development_class(section).get("additional_canonical_fields") or []}
    for required in ("dataset_identity", "dataset_manifest_digest"):
        if required not in fields:
            findings.append(f"the model-development workload does not bind {required}")
    return findings


def cdh_13(section, architecture, decisions):
    """Partition identity is absent from the model-development workload identity."""
    findings = []
    partitions = section["partition_integrity"]
    expected = {"training", "validation", "test", "external_independent_test"}
    absent = sorted(expected - set(partitions.get("partitions") or []))
    if absent:
        findings.append(f"populations that are not explicitly identifiable: {absent}")
    if not partitions.get("participates_in_workload_identity"):
        findings.append("partition identity does not participate in the workload identity")
    if partitions.get("silent_movement_after_freeze") != "prohibited":
        findings.append("silent movement between partitions after freeze is not prohibited")
    field = partitions.get("partition_identity_field")
    development = development_class(section)
    carried = {
        entry["name"]: entry
        for entry in development.get("additional_canonical_fields") or []
    }
    if field not in carried:
        findings.append(f"{field} is not a field of the model-development workload")
    elif not (carried[field].get("in_digest") and carried[field].get("authorization_relevant")):
        findings.append(f"{field} is declared but sits outside the authorization-bound digest")
    return findings


def cdh_14(section, architecture, decisions):
    """A model artifact is identified by filename, or is not bound to its origin."""
    findings = []
    artifact = section["model_artifact"]
    if artifact.get("identity_basis") != "immutable_content_identity":
        findings.append("a model artifact is not identified by immutable content identity")
    if artifact.get("identity_by_filename") != "prohibited":
        findings.append("identifying a model artifact by filename is not prohibited")
    expected = {
        "resulting_model_digest", "originating_training_workload_digest",
        "training_dataset_manifest_digest", "partition_identity", "training_code_identity",
        "runtime_container_digest", "evaluation_outputs",
    }
    absent = sorted(expected - set(artifact.get("required_bindings") or []))
    if absent:
        findings.append(
            f"the model record does not bind {absent}, so which data and which process "
            f"produced this model is not answerable from the record"
        )
    if "model_artifact_digest" not in (development_class(section).get("result_binds") or []):
        findings.append("the model-development result does not bind a model artifact digest")
    return findings


def cdh_15(section, architecture, decisions):
    """A computational or evaluation result is treated as conferring authorization."""
    findings = []
    promotion = section["model_promotion"]
    expected = ["training_success", "validation_success", "qualification", "clinical_authorization"]
    if promotion.get("ordered_distinctions") != expected:
        findings.append(f"the promotion distinctions are not {expected}")
    declared = {
        (pair.get("from"), pair.get("to"))
        for pair in promotion.get("non_implication") or []
    }
    for earlier, later in zip(expected, expected[1:]):
        if (earlier, later) not in declared:
            findings.append(f"{earlier} is not declared to fall short of {later}")
    stages = promotion.get("stages") or []
    authoritative = [stage for stage in stages if stage.get("authority") != "none"]
    if len(authoritative) != 1:
        findings.append(
            f"expected exactly one promotion stage carrying authority, found {len(authoritative)}"
        )
    for stage in authoritative:
        if stage.get("conferred_by") != "ProfessionalDecision":
            findings.append(
                f"{stage['id']} carries authority conferred by {stage.get('conferred_by')!r}, "
                f"not by a ProfessionalDecision"
            )
    if promotion.get("parallel_approval_mechanism") != "prohibited":
        findings.append("a parallel approval mechanism for models is not prohibited")
    if promotion.get("ai_may_promote_a_model"):
        findings.append("AI is permitted to promote a model")
    reused = promotion.get("reuses_existing_authority_structures") or []
    if not reused:
        findings.append("promotion reuses no existing authority structure")
    known = {item["id"] for item in architecture["architecture_decisions"]}
    known |= {record["id"] for record in decisions["decisions"]}
    unknown = sorted(set(reused) - known)
    if unknown:
        findings.append(f"promotion cites authority structures that do not exist: {unknown}")
    return findings


def cdh_16(section, architecture, decisions):
    """A model identity field sits outside the authorization-bound digest."""
    findings = []
    substitution = section["model_substitution"]
    if not substitution.get("model_identity_in_authorization_bound_digest"):
        findings.append("model identity is not declared part of the authorization-bound digest")
    if not substitution.get("prohibited_silent_substitutions"):
        findings.append("no silent substitution is prohibited")
    if substitution.get("permitted_only_when") != "explicitly_authorized_by_the_governed_workload_contract":
        findings.append("substitution is permitted without explicit contract authorization")
    bound = {}
    for member in section["workload_classes"]["classes"]:
        for entry in member.get("additional_canonical_fields") or []:
            bound[entry["name"]] = entry
    for field in substitution.get("identity_fields") or []:
        entry = bound.get(field)
        if entry is None:
            findings.append(f"{field} is a model identity field no workload class binds")
        elif not (entry.get("authorization_relevant") and entry.get("in_digest")):
            findings.append(f"{field} is bound but sits outside the authorization-bound digest")
    return findings


def cdh_17(section, architecture, decisions):
    """A combined training population erases its constituent dataset identities."""
    findings = []
    multi = section["multi_dataset_development"]
    if not multi.get("constituent_identity_retained"):
        findings.append("contributing datasets do not retain independent identity")
    composite = multi.get("composite_identity") or {}
    if composite.get("erases_constituent_identity"):
        findings.append("the composite identity erases the identity of its constituents")
    if not composite.get("reproducible"):
        findings.append("the composite identity is not reproducible")
    if not composite.get("derived_from"):
        findings.append("the composite identity is not derived from its constituents")
    sources = multi.get("supported_source_classes") or []
    if len(sources) < 3:
        findings.append(f"only {len(sources)} dataset source classes are supported")
    field = composite.get("field")
    fields = {entry["name"] for entry in development_class(section).get("additional_canonical_fields") or []}
    if field not in fields:
        findings.append(f"the composite identity field {field!r} is not bound by the model-development workload")
    return findings


def cdh_18(section, architecture, decisions):
    """Bitwise output identity is required of a nondeterministic training workload."""
    findings = []
    repro = section["reproducibility"]
    if repro.get("bitwise_identical_trained_weights_required"):
        findings.append("bitwise identical trained weights are required of a nondeterministic process")
    if not repro.get("required_evidence"):
        findings.append("no reproducibility evidence is required")
    members = {member["id"]: member for member in section["workload_classes"]["classes"]}
    acceptance = {entry["id"] for entry in section["cross_host_equivalence"]["acceptance_classes"]}
    bindings = repro.get("class_bindings") or []
    bound = {binding.get("workload_class") for binding in bindings}
    unbound = sorted(set(members) - bound)
    if unbound:
        findings.append(f"workload classes with no declared reproducibility expectation: {unbound}")
    for binding in bindings:
        identifier = binding.get("workload_class")
        if identifier not in members:
            findings.append(f"a reproducibility binding names the unknown workload class {identifier}")
            continue
        if binding.get("equivalence_acceptance_class") not in acceptance:
            findings.append(
                f"{identifier} is bound to an equivalence class that is not declared"
            )
        if binding.get("bitwise_output_identity_required") != members[identifier].get(
            "bitwise_output_identity_required"
        ):
            findings.append(f"{identifier} declares two different bitwise-identity expectations")
    for member in members.values():
        if not member.get("reproducibility_class"):
            findings.append(f"{member['id']} declares no reproducibility class")
    return findings


def cdh_19(section, architecture, decisions):
    """A language service is assigned authority, or is permitted to decide."""
    findings = []
    hosting = section["language_service_hosting"]
    if hosting.get("authority") != "none":
        findings.append(f"language-service hosting holds authority {hosting.get('authority')!r}")
    services = hosting.get("services") or []
    if not services:
        findings.append("no language services are declared")
    for service in services:
        if service.get("authority") != "none":
            findings.append(f"{service['id']} holds authority {service.get('authority')!r}, expected none")
    subordination = hosting.get("subordination") or {}
    for key in (
        "may_produce_authorization_decision",
        "may_produce_execution_capability",
        "may_satisfy_professional_decision",
    ):
        if subordination.get(key) is not False:
            findings.append(f"language-service output {key} is not denied")
    if subordination.get("output_class") != "untrusted_candidate":
        findings.append("language-service output is not classed as an untrusted candidate")

    zones = {}
    for decision in architecture["architecture_decisions"]:
        for zone in decision.get("zones") or []:
            zones[zone["id"]] = zone
    zone_id = hosting.get("trust_zone")
    if zone_id not in zones:
        findings.append(f"language services are placed in trust zone {zone_id!r}, which does not exist")
    elif zones[zone_id].get("authority") != "none":
        findings.append(f"language services are placed in {zone_id}, which holds authority")

    invariants = {item["id"] for item in architecture["invariants"]}
    unaffected = hosting.get("invariant_unaffected")
    if unaffected not in invariants:
        findings.append(f"the invariant declared unaffected, {unaffected!r}, does not exist")

    profiles = {profile["id"] for profile in section["compute_provider_profiles"]}
    if hosting.get("reference_host") not in profiles:
        findings.append(f"the language-service reference host {hosting.get('reference_host')!r} is not a declared profile")

    workload_class = class_by_id(section, hosting["workload_class"])
    if workload_class.get("authority") != "none":
        findings.append(f"{workload_class['id']} holds authority")
    if workload_class.get("trust_zone") != zone_id:
        findings.append(f"{workload_class['id']} is not placed in the same trust zone as its services")
    return findings


def cdh_20(section, architecture, decisions):
    """A deployment profile forks the product or lets an invariant semantic vary."""
    findings = []
    deployment = section["deployment_profiles"]
    profiles = deployment.get("profiles") or []
    if len(profiles) < 3:
        findings.append(f"only {len(profiles)} deployment profiles are declared")
    may_vary = set(deployment.get("may_vary") or [])
    may_not_vary = set(deployment.get("may_not_vary") or [])
    if not may_vary:
        findings.append("no deployment-specific configuration is declared variable")
    if not may_not_vary:
        findings.append("no semantics are declared invariant across profiles")
    dropped = sorted(PROFILE_INVARIANT_SEMANTICS - may_not_vary)
    if dropped:
        findings.append(
            f"semantics that may not vary by profile have been dropped from the "
            f"declared set: {dropped}"
        )
    both = sorted(may_vary & may_not_vary)
    if both:
        findings.append(f"deployment configuration is both variable and invariant: {both}")
    if deployment.get("silent_variation") != "prohibited":
        findings.append("silent variation between deployment profiles is not prohibited")
    preserved = set(deployment.get("preserved_across_profiles") or [])
    if not preserved:
        findings.append("nothing is declared preserved across profiles")
    leaked = sorted(preserved & may_vary)
    if leaked:
        findings.append(f"declared preserved across profiles yet variable by profile: {leaked}")

    runtime = deployment.get("runtime")
    envelope = section["governed_workload"].get("id")
    abstraction = section["compute_provider_abstraction"].get("id")
    compute = {profile["id"] for profile in section["compute_provider_profiles"]}
    identifiers = []
    for profile in profiles:
        identifiers.append(profile.get("id"))
        if profile.get("runtime") != runtime:
            findings.append(f"{profile['id']} runs a different runtime, which forks the product")
        if profile.get("workload_envelope") != envelope:
            findings.append(f"{profile['id']} carries its own workload envelope")
        if profile.get("abstraction") != abstraction:
            findings.append(f"{profile['id']} carries its own compute abstraction")
        for key in ("reference_compute_profile", "remote_compute_profile"):
            target = profile.get(key)
            if target is not None and target not in compute:
                findings.append(f"{profile['id']} names the undeclared compute profile {target}")
    if len(identifiers) != len(set(identifiers)):
        findings.append("deployment profile identifiers are not unique")

    invariant = section["product_invariant"]
    if invariant.get("dgx_is_a_special_case_product_architecture"):
        findings.append("the reference host is declared a special-case product architecture")
    if invariant.get("shared_abstraction") != abstraction:
        findings.append("the product invariant does not rest on the compute-provider abstraction")
    if invariant.get("shared_envelope") != envelope:
        findings.append("the product invariant does not rest on the governed workload envelope")
    if invariant.get("reference_profile") not in set(identifiers):
        findings.append("the product invariant names a reference profile that is not declared")
    return findings


def cdh_21(section, architecture, decisions):
    """Data locality decided by scheduling or capacity rather than by policy."""
    findings = []
    locality = section["workload_locality"]
    if not locality.get("policy_controlled"):
        findings.append("workload locality is not declared policy-controlled")
    if locality.get("capacity_may_override_locality"):
        findings.append("available capacity may override a locality classification")
    if locality.get("crossing_institutional_boundary_by_scheduling") != "prohibited":
        findings.append("data may cross the institutional boundary as a consequence of scheduling")
    classes = locality.get("classes") or []
    if not classes:
        findings.append("no locality classes are declared")
    identifiers = [entry.get("id") for entry in classes]
    if len(identifiers) != len(set(identifiers)):
        findings.append("locality class identifiers are not unique")
    if not any(entry.get("may_leave_institutional_boundary") is False for entry in classes):
        findings.append("no locality class keeps a workload inside the institutional boundary")

    name = locality.get("classification_field")
    common = {entry["name"]: entry for entry in section["governed_workload"]["canonical_fields"]}
    entry = common.get(name)
    if entry is None:
        findings.append(f"the locality field {name!r} is not part of the common governed workload")
    elif not (entry.get("authorization_relevant") and entry.get("in_digest")):
        findings.append(f"the locality field {name!r} sits outside the authorization-bound digest")
    if name in (section["contracts"]["DispatchContract"].get("mutable_fields") or []):
        findings.append(f"dispatch may change {name!r}, so a scheduler can choose a locality")
    return findings

def cdh_22(section, architecture, decisions):
    """Tenant isolation recorded as implemented or qualified, or permitting leakage."""
    findings = []
    tenancy = section["tenant_isolation"]
    profiles = {profile["id"] for profile in section["deployment_profiles"].get("profiles") or []}
    if tenancy.get("applies_to") not in profiles:
        findings.append(
            f"tenant isolation applies to {tenancy.get('applies_to')!r}, which is not a declared profile"
        )
    subjects = tenancy.get("isolated_subjects") or []
    if len(subjects) < 6:
        findings.append(f"only {len(subjects)} tenant subjects are isolated")
    if tenancy.get("cross_tenant_context_access") != "prohibited":
        findings.append("cross-tenant context access is not prohibited")
    if tenancy.get("implementation_state") == "implemented":
        findings.append(
            "tenant isolation is recorded as implemented; this section represents it and builds nothing"
        )
    if tenancy.get("qualification_state") == "qualified":
        findings.append("tenant isolation is recorded as qualified; representation is not qualification")
    if tenancy.get("claimable_now") is not False:
        findings.append("tenant isolation is declared claimable from this section")
    return findings


def cdh_23(section, architecture, decisions):
    """Profiles delivered as separately maintained product forms."""
    findings = []
    packaging = section["runtime_packaging"]
    if packaging.get("package_identity_basis") != "immutable_content_identity":
        findings.append("the runtime package is not identified by immutable content identity")
    if packaging.get("product_forks") != "prohibited":
        findings.append("separately maintained product forks are not prohibited")
    if packaging.get("reproducible_deployment") != "required":
        findings.append("reproducible deployment is not required")
    runtime = section["deployment_profiles"].get("runtime")
    if packaging.get("runtime") != runtime:
        findings.append("the packaged runtime is not the runtime the profiles deploy")
    if section["standalone_runtime_services"].get("id") != runtime:
        findings.append("the hosted runtime service set is not the runtime the profiles deploy")
    bound = {entry["name"]: entry for entry in section["governed_workload"]["canonical_fields"]}
    for workload_class in section["workload_classes"]["classes"]:
        for entry in workload_class.get("additional_canonical_fields") or []:
            bound[entry["name"]] = entry
    for name in packaging.get("identity_fields") or []:
        entry = bound.get(name)
        if entry is None:
            findings.append(f"the package identity field {name!r} is bound by no workload class")
        elif not (entry.get("authorization_relevant") and entry.get("in_digest")):
            findings.append(
                f"the package identity field {name!r} sits outside the authorization-bound digest"
            )
    return findings

def cdh_24(section, architecture, decisions):
    """A runtime or clinical model that may advance because a newer version exists."""
    findings = []
    release = section["release_and_rollback"]
    expected = {
        "versioned_release_identity", "controlled_upgrade", "model_version_control",
        "rollback", "configuration_provenance", "evidence_continuity",
    }
    absent = sorted(expected - set(release.get("required_capabilities") or []))
    if absent:
        findings.append(f"release control does not require {absent}")
    for key in ("silent_runtime_advance", "silent_clinical_model_advance"):
        if release.get(key) != "prohibited":
            findings.append(f"{key} is not prohibited")
    declared = {profile["id"] for profile in section["deployment_profiles"].get("profiles") or []}
    covered = set(release.get("applies_to_profiles") or [])
    uncovered = sorted(declared - covered)
    if uncovered:
        findings.append(f"deployment profiles outside release and rollback control: {uncovered}")
    unknown = sorted(covered - declared)
    if unknown:
        findings.append(f"release control names undeclared profiles: {unknown}")
    if release.get("exemptions"):
        findings.append(f"profiles exempted from release control: {release['exemptions']}")
    return findings


def cdh_25(section, architecture, decisions):
    """A hosted runtime service holds more authority than its trust zone."""
    findings = []
    runtime = section["standalone_runtime_services"]
    zones = {}
    for decision in architecture["architecture_decisions"]:
        for zone in decision.get("zones") or []:
            zones[zone["id"]] = zone
    prohibited = runtime.get("prohibited_zone")
    if prohibited not in zones:
        findings.append(f"the prohibited zone {prohibited!r} is not a declared trust zone")
    services = runtime.get("services") or []
    if not services:
        findings.append("the runtime declares no services")
    identifiers = [service.get("id") for service in services]
    if len(identifiers) != len(set(identifiers)):
        findings.append("runtime service identifiers are not unique")
    for service in services:
        zone_id = service.get("trust_zone")
        zone = zones.get(zone_id)
        if zone is None:
            findings.append(f"{service['id']} is placed in {zone_id!r}, which is not a declared trust zone")
            continue
        if zone_id == prohibited:
            findings.append(
                f"{service['id']} is hosted in {zone_id}, the system-of-record zone; that would make "
                f"the appliance the authoritative clinical system rather than a host for it"
            )
        if service.get("authority") not in ("none", zone.get("authority")):
            findings.append(
                f"{service['id']} holds {service.get('authority')!r}, which is neither none nor the "
                f"authority {zone_id} already holds"
            )
    if not runtime.get("external_authoritative_systems_remain_external"):
        findings.append("external authoritative systems are not declared to remain external")
    for profile in section["deployment_profiles"].get("profiles") or []:
        if not profile.get("external_authoritative_systems_remain_external"):
            findings.append(f"{profile['id']} does not keep external authoritative systems external")
    compute = {profile["id"] for profile in section["compute_provider_profiles"]}
    if runtime.get("reference_appliance") not in compute:
        findings.append("the runtime reference appliance is not a declared compute profile")
    return findings

CONTROLS = {
    "CDH-01": cdh_01, "CDH-02": cdh_02, "CDH-03": cdh_03, "CDH-04": cdh_04,
    "CDH-05": cdh_05, "CDH-06": cdh_06, "CDH-07": cdh_07, "CDH-08": cdh_08,
    "CDH-09": cdh_09, "CDH-10": cdh_10, "CDH-11": cdh_11, "CDH-12": cdh_12,
    "CDH-13": cdh_13, "CDH-14": cdh_14, "CDH-15": cdh_15, "CDH-16": cdh_16,
    "CDH-17": cdh_17, "CDH-18": cdh_18, "CDH-19": cdh_19, "CDH-20": cdh_20,
    "CDH-21": cdh_21, "CDH-22": cdh_22, "CDH-23": cdh_23, "CDH-24": cdh_24,
    "CDH-25": cdh_25,
}


def registry_findings(section, architecture, decisions):
    """The record and this file must agree about which controls exist.

    Without this, deleting a check here leaves the architecture still advertising it, and
    a reader has no way to tell an enforced control from a described one.
    """
    findings = []
    declared = [entry["id"] for entry in section["structural_controls"]["controls"]]
    if len(declared) != len(set(declared)):
        findings.append("the declared control identifiers are not unique")
    undeclared = sorted(set(CONTROLS) - set(declared))
    unimplemented = sorted(set(declared) - set(CONTROLS))
    if undeclared:
        findings.append(f"controls implemented here but not declared in the architecture: {undeclared}")
    if unimplemented:
        findings.append(f"controls declared in the architecture but not implemented here: {unimplemented}")
    gate = section["structural_controls"].get("gate")
    if gate != str(Path(__file__).resolve().relative_to(REPO_ROOT)).replace("\\", "/"):
        findings.append(f"the architecture names {gate!r} as its gate, which is not this file")

    states = section["proposition_states"]["ordered"]
    ceiling = states.index(section["proposition_states"]["max_state_at_this_checkpoint"])
    identifiers = []
    for proposition in section["acceptance_propositions"]:
        identifier = proposition["id"]
        identifiers.append(identifier)
        state = proposition["verification_state"]
        if state not in states:
            findings.append(f"{identifier} carries the unknown verification state {state!r}")
        elif states.index(state) > ceiling:
            findings.append(
                f"{identifier} is recorded {state}, above the {states[ceiling]} ceiling this "
                f"checkpoint may reach; presence in a controlled record is not verification"
            )
        control = proposition.get("structural_control")
        if proposition["class"] == "structural":
            if control not in CONTROLS:
                findings.append(f"{identifier} is structural but names no implemented control")
            if state != "ALLOCATED":
                findings.append(f"{identifier} is structural but is not ALLOCATED")
        else:
            if control is not None:
                findings.append(f"{identifier} is a design proposition but names control {control}")
            if state != "REPRESENTED":
                findings.append(f"{identifier} is a design proposition but is not REPRESENTED")
        if not proposition.get("future_verification_obligation"):
            findings.append(f"{identifier} records no future verification obligation")
    if len(identifiers) != len(set(identifiers)):
        findings.append("acceptance proposition identifiers are not unique")
    findings += session_control_findings(section)
    return findings


def session_control_findings(section):
    """CLAUDE.md must not misstate the size of what this gate enforces."""
    if not SESSION_CONTROLS.is_file():
        return []
    with io.open(SESSION_CONTROLS, encoding='utf-8') as handle:
        # Matched against whitespace-normalized text. CLAUDE.md is hard-wrapped, so a
        # line-local pattern would be defeated by a rewrap rather than by a real change.
        text = ' '.join(handle.read().split())
    propositions = section['acceptance_propositions']
    structural = [item for item in propositions if item['class'] == 'structural']
    expected = {
        'structural controls': (str(len(CONTROLS)),),
        'propositions': (str(len(structural)), str(len(propositions))),
    }
    findings = []
    for pattern, label in SESSION_COUNTS:
        match = pattern.search(text)
        if match is None:
            findings.append(
                f'CLAUDE.md no longer states the {label} this gate enforces, so it cannot go stale visibly'
            )
        elif match.groups() != expected[label]:
            findings.append(
                f'CLAUDE.md states {match.groups()} for {label}; the record and this gate carry '
                f'{expected[label]}'
            )
    return findings


def cross_reference_findings(section, architecture, decisions):
    """The amendment must be anchored in the objects that already carry authority."""
    findings = []
    amendment = section["amendment_id"]
    decision_id = section["decision_record"]

    baselines = {item["id"]: item for item in architecture["architecture_decisions"]}
    baseline = baselines.get(section["architecture_decision"])
    if baseline is None:
        findings.append(f"{section['architecture_decision']} is not a declared architecture decision")
    else:
        if baseline.get("decision_record") != decision_id:
            findings.append(f"{baseline['id']} does not cite {decision_id}")
        if baseline.get("structure") != SECTION_KEY:
            findings.append(f"{baseline['id']} does not point at this structure")

    invariants = {item["id"]: item for item in architecture["invariants"]}
    invariant = invariants.get(section["invariant"])
    if invariant is None:
        findings.append(f"{section['invariant']} is not a declared invariant")
    elif invariant.get("amendment") != amendment:
        findings.append(f"{section['invariant']} is not attributed to {amendment}")

    records = {record["id"]: record for record in decisions["decisions"]}
    record = records.get(decision_id)
    if record is None:
        findings.append(f"{decision_id} is not in the controlled decision register")
        return findings
    if record.get("architecture_amendment") != amendment:
        findings.append(f"{decision_id} is not attributed to {amendment}")
    prohibitions = record.get("does_not_permit") or []
    if not prohibitions:
        findings.append(f"{decision_id} records no structural prohibition")
    overlap = sorted(set(prohibitions) & set(record.get("permits_now") or []))
    if overlap:
        findings.append(f"{decision_id} both permits and prohibits: {overlap}")
    if record.get("authority_cutover_status") == "approved":
        findings.append(f"{decision_id} records an approved authority cutover")
    return findings


def check(architecture, decisions):
    """Every finding, as (control, message). Registry findings carry no control id."""
    section = architecture.get(SECTION_KEY)
    if not isinstance(section, dict):
        raise MeasurementInvalid(f"spec/architecture.yaml declares no {SECTION_KEY} section")
    for required in ("structural_controls", "acceptance_propositions", "governed_workload",
                     "workload_classes", "contracts", "responsibility_boundary"):
        if required not in section:
            raise MeasurementInvalid(f"{SECTION_KEY} is missing {required}; nothing to measure")

    findings = [("registry", message) for message in registry_findings(section, architecture, decisions)]
    findings += [("cross-reference", message)
                 for message in cross_reference_findings(section, architecture, decisions)]
    for identifier in sorted(CONTROLS):
        try:
            for message in CONTROLS[identifier](section, architecture, decisions):
                findings.append((identifier, message))
        except (KeyError, TypeError, IndexError, ValueError) as exc:
            raise MeasurementInvalid(
                f"{identifier} could not be evaluated against the record: {exc!r}"
            ) from exc
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--list", action="store_true", help="print the controls and exit")
    args = parser.parse_args(argv)

    if args.list:
        for identifier in sorted(CONTROLS):
            summary = (CONTROLS[identifier].__doc__ or "").strip().splitlines()[0]
            print(f"{identifier}  {summary}")
        return VERDICT_PASS

    try:
        architecture = load(ARCHITECTURE)
        decisions = load(DECISIONS)
        findings = check(architecture, decisions)
    except MeasurementInvalid as exc:
        print(f"{MARKER}: {exc}", file=sys.stderr)
        return MEASUREMENT_INVALID

    section = architecture[SECTION_KEY]
    if findings:
        print("FAIL: governed computational hosting\n", file=sys.stderr)
        for identifier, message in findings:
            print(f"  - [{identifier}] {message}", file=sys.stderr)
        print("", file=sys.stderr)
        return SUBSTANTIVE_FINDING

    propositions = section["acceptance_propositions"]
    structural = [p for p in propositions if p["class"] == "structural"]
    print(
        f"PASS: {section['amendment_id']} is structurally represented and allocated. "
        f"{len(CONTROLS)} structural controls over "
        f"{len(section['workload_classes']['classes'])} governed workload classes, "
        f"{len(section['deployment_profiles']['profiles'])} deployment profiles and "
        f"{len(section['compute_provider_profiles'])} compute-provider profiles; "
        f"{len(structural)} of {len(propositions)} acceptance propositions are ALLOCATED and "
        f"{len(propositions) - len(structural)} are REPRESENTED with a future verification "
        f"obligation. This inspects a controlled record, not a running system: nothing here "
        f"is verified, qualified, or commissioned."
    )
    return VERDICT_PASS


if __name__ == "__main__":
    sys.exit(main())
