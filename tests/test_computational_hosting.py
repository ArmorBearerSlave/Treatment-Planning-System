"""ARCH-DGX-01: every structural control is driven with the defect it exists to catch.

A control that has only ever seen a valid record is not evidence that it works. Each test
below perturbs one property of the live architecture and requires the control that owns it
to fire; the perturbations are in-memory, minimal, and leave the record otherwise
well-formed, so a rejection is attributable to the defect rather than to having broken the
document.

The non-vacuity half is the unperturbed record producing zero findings. Without it a gate
that rejected everything would pass every test here and be no control at all.

Exit codes are observed as real process exit codes rather than as exception types, because
the defect class the repository already recorded lived exactly at that boundary: internal
state right, externally observable verdict wrong. Where a branch needs a different record,
a disposable wrapper injects it and exits with the return code the measurement produced.
"""
from __future__ import annotations

import copy
import io
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools" / "spec"))

import check_computational_hosting as gate  # noqa: E402

VERDICT_PASS = 0
SUBSTANTIVE_FINDING = 1
MEASUREMENT_INVALID = 2


def load(path: Path) -> dict:
    with io.open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle.read())


ARCHITECTURE = load(REPO_ROOT / "spec" / "architecture.yaml")
DECISIONS = load(REPO_ROOT / "spec" / "decisions.yaml")


def field(entries: list, name: str) -> dict:
    for entry in entries:
        if entry.get("name") == name:
            return entry
    raise AssertionError(f"the live record no longer declares the field {name!r}")


def member(entries: list, identifier: str) -> dict:
    for entry in entries:
        if entry.get("id") == identifier:
            return entry
    raise AssertionError(f"the live record no longer declares {identifier!r}")


class ControlHarness(unittest.TestCase):
    """Perturb one property, require one named control to report it."""

    def perturb(self, mutate, *, decisions_mutate=None):
        architecture = copy.deepcopy(ARCHITECTURE)
        decisions = copy.deepcopy(DECISIONS)
        mutate(architecture[gate.SECTION_KEY], architecture)
        if decisions_mutate is not None:
            decisions_mutate(decisions)
        return gate.check(architecture, decisions)

    def assertFires(self, control: str, mutate, *, decisions_mutate=None):
        findings = self.perturb(mutate, decisions_mutate=decisions_mutate)
        fired = sorted({identifier for identifier, _ in findings})
        self.assertIn(
            control,
            fired,
            f"{control} did not fire for its own defect; findings were {fired or 'none'}",
        )
        return findings


class NonVacuity(ControlHarness):
    def test_live_record_produces_no_findings(self):
        """Every negative result below is worthless if the positive case fails too."""
        findings = gate.check(copy.deepcopy(ARCHITECTURE), copy.deepcopy(DECISIONS))
        self.assertEqual(findings, [], f"the live architecture reports {findings}")

    def test_every_implemented_control_is_declared_and_reachable(self):
        declared = [
            entry["id"]
            for entry in ARCHITECTURE[gate.SECTION_KEY]["structural_controls"]["controls"]
        ]
        self.assertEqual(sorted(declared), sorted(gate.CONTROLS))
        self.assertEqual(len(declared), len(set(declared)))


class WorkloadIntegrity(ControlHarness):
    def test_cdh_01_workload_without_a_digest_binding(self):
        def mutate(section, _architecture):
            section["governed_workload"]["integrity_binding"].pop("field")
        self.assertFires("CDH-01", mutate)

    def test_cdh_01_canonical_field_outside_the_digest(self):
        def mutate(section, _architecture):
            field(section["governed_workload"]["canonical_fields"], "policy_identity")["in_digest"] = False
        self.assertFires("CDH-01", mutate)

    def test_cdh_02_authorization_not_bound_to_the_digest(self):
        def mutate(section, _architecture):
            binds = section["contracts"]["AuthorizationDecision"]["binds"]
            binds.remove(section["governed_workload"]["integrity_binding"]["field"])
        self.assertFires("CDH-02", mutate)

    def test_cdh_02_authorization_produced_outside_the_kernel(self):
        def mutate(section, _architecture):
            section["contracts"]["AuthorizationDecision"]["produced_by"] = "RB-DISPATCH-01"
        self.assertFires("CDH-02", mutate)

    def test_cdh_03_dispatch_may_mutate_an_authorization_relevant_field(self):
        def mutate(section, _architecture):
            section["contracts"]["DispatchContract"]["mutable_fields"].append("hyperparameters")
        self.assertFires("CDH-03", mutate)

    def test_cdh_03_scale_out_both_permits_and_prohibits(self):
        def mutate(section, _architecture):
            section["scale_out_invariance"]["may_alter"].append("hyperparameters")
            section["scale_out_invariance"]["may_not_alter"].append("hyperparameters")
        self.assertFires("CDH-03", mutate)

    def test_cdh_04_result_does_not_bind_the_authorized_digest(self):
        def mutate(section, _architecture):
            binds = section["contracts"]["ResultContract"]["binds"]
            binds.remove(section["governed_workload"]["integrity_binding"]["field"])
        self.assertFires("CDH-04", mutate)

    def test_cdh_04_reconciliation_chain_broken(self):
        def mutate(section, _architecture):
            section["reconciliation"]["required_equalities"].pop()
        self.assertFires("CDH-04", mutate)

    def test_cdh_05_provider_token_leaks_into_the_envelope(self):
        def mutate(section, _architecture):
            field(section["governed_workload"]["canonical_fields"], "typed_intent")["name"] = "dgx_typed_intent"
        self.assertFires("CDH-05", mutate)

    def test_cdh_05_provider_token_leaks_into_a_contract(self):
        def mutate(section, _architecture):
            section["contracts"]["ResultContract"]["binds"].append("nvidia_run_receipt")
        self.assertFires("CDH-05", mutate)


class AuthorityBoundary(ControlHarness):
    def test_cdh_06_dispatcher_given_authorization_authority(self):
        def mutate(section, _architecture):
            item = member(section["responsibility_boundary"]["responsibilities"], "RB-DISPATCH-01")
            item["authority"] = "deterministic_eligibility_decision"
        self.assertFires("CDH-06", mutate)

    def test_cdh_06_provider_may_set_authorization_relevant_fields(self):
        def mutate(section, _architecture):
            item = member(section["responsibility_boundary"]["responsibilities"], "RB-PROVIDER-01")
            item["may_set_authorization_relevant_fields"] = True
        self.assertFires("CDH-06", mutate)

    def test_cdh_06_kernel_also_selects_the_provider(self):
        def mutate(section, _architecture):
            item = member(section["responsibility_boundary"]["responsibilities"], "RB-AUTHZ-01")
            item["may_select_compute_provider"] = True
        self.assertFires("CDH-06", mutate)

    def test_cdh_06_compute_profile_holds_authority(self):
        def mutate(section, _architecture):
            section["compute_provider_profiles"][0]["authority"] = "token_scoped_execution_only"
        self.assertFires("CDH-06", mutate)

    def test_cdh_07_external_tps_authority_moved_to_the_compute_host(self):
        def mutate(section, _architecture):
            subject = section["authority_retention"]["subjects"][0]
            subject["retained_by"] = "PLAT-DGX-SPARK-01"
        self.assertFires("CDH-07", mutate)

    def test_cdh_07_authority_declared_reassignable(self):
        def mutate(section, _architecture):
            section["authority_retention"]["subjects"][1]["may_be_reassigned_to_compute_host"] = True
        self.assertFires("CDH-07", mutate)

    def test_cdh_08_reference_host_with_no_scale_out_profile(self):
        def mutate(section, _architecture):
            section["compute_provider_profiles"] = [
                p for p in section["compute_provider_profiles"]
                if p["role"] == "first_reference_complete_computational_host"
            ]
        self.assertFires("CDH-08", mutate)

    def test_cdh_08_scale_out_profile_on_a_different_abstraction(self):
        def mutate(section, _architecture):
            member(section["compute_provider_profiles"], "PLAT-REMOTE-QUALIFIED-01")["abstraction"] = "CP-OTHER-01"
        self.assertFires("CDH-08", mutate)

    def test_cdh_08_reference_host_owns_the_workload_format(self):
        def mutate(section, _architecture):
            member(section["compute_provider_profiles"], "PLAT-DGX-SPARK-01")["semantic_owner_of_workload_format"] = True
        self.assertFires("CDH-08", mutate)


class ResultAcceptance(ControlHarness):
    """The correction that mattered: a digest match is necessary and not sufficient."""

    def test_cdh_09_conformance_removed_from_acceptance(self):
        def mutate(section, _architecture):
            conformance = section["output_contract_conformance"]["id"]
            section["result_acceptance"]["steps"] = [
                step for step in section["result_acceptance"]["steps"]
                if step["mechanism"] != conformance
            ]
        self.assertFires("CDH-09", mutate)

    def test_cdh_09_conformance_made_optional(self):
        def mutate(section, _architecture):
            conformance = section["output_contract_conformance"]["id"]
            for step in section["result_acceptance"]["steps"]:
                if step["mechanism"] == conformance:
                    step["required"] = False
        self.assertFires("CDH-09", mutate)

    def test_cdh_09_conformance_folded_into_provenance(self):
        def mutate(section, _architecture):
            section["output_contract_conformance"]["distinct_from"] = [section["reconciliation"]["id"]]
        self.assertFires("CDH-09", mutate)

    def test_cdh_09_conformance_checked_against_an_undeclared_contract(self):
        def mutate(section, _architecture):
            section["output_contract_conformance"]["checked_against"].append("whatever_the_host_returned")
        self.assertFires("CDH-09", mutate)

    def test_cdh_09_conformance_delegated_to_the_executor(self):
        def mutate(section, _architecture):
            conformance = section["output_contract_conformance"]["id"]
            for step in section["result_acceptance"]["steps"]:
                if step["mechanism"] == conformance:
                    step["independently_establishable_by_nltps"] = False
        self.assertFires("CDH-09", mutate)

    def test_cdh_10_digest_chain_declared_sufficient(self):
        """The exact overclaim: a label the executor copies back cannot prove what ran."""
        def mutate(section, _architecture):
            section["reconciliation"]["sufficiency"] = "sufficient"
        self.assertFires("CDH-10", mutate)

    def test_cdh_10_record_stops_saying_what_the_chain_does_not_establish(self):
        def mutate(section, _architecture):
            section["reconciliation"]["does_not_establish"] = []
        self.assertFires("CDH-10", mutate)

    def test_cdh_10_digest_chain_as_the_only_required_step(self):
        def mutate(section, _architecture):
            reconciliation = section["reconciliation"]["id"]
            section["result_acceptance"]["steps"] = [
                step for step in section["result_acceptance"]["steps"]
                if step["mechanism"] == reconciliation
            ]
        self.assertFires("CDH-10", mutate)

    def test_cdh_10_claim_boundary_permits_what_it_forbids(self):
        def mutate(section, _architecture):
            forbidden = section["claim_boundary"]["may_not_claim"][0]
            section["claim_boundary"]["may_claim"].append(forbidden)
        self.assertFires("CDH-10", mutate)


class ModelDevelopmentGovernance(ControlHarness):
    def test_cdh_11_class_defines_its_own_integrity_mechanism(self):
        def mutate(section, _architecture):
            member(section["workload_classes"]["classes"], "WLC-INFERENCE-01")["common_mechanism"] = "GW-INFERENCE-ONLY"
        self.assertFires("CDH-11", mutate)

    def test_cdh_11_development_and_inference_collapsed_into_one_class(self):
        def mutate(section, _architecture):
            development = member(section["workload_classes"]["classes"], "WLC-MODELDEV-01")
            development["additional_canonical_fields"].append(
                {"name": "qualified_model_digest", "authorization_relevant": True, "in_digest": True}
            )
        self.assertFires("CDH-11", mutate)

    def test_cdh_11_class_declared_to_confer_authorization(self):
        def mutate(section, _architecture):
            member(section["workload_classes"]["classes"], "WLC-INFERENCE-01")["confers_authorization_for_use"] = True
        self.assertFires("CDH-11", mutate)

    def test_cdh_12_dataset_identified_by_directory(self):
        def mutate(section, _architecture):
            section["dataset_governance"]["identity_by_path_or_directory_name"] = "permitted"
        self.assertFires("CDH-12", mutate)

    def test_cdh_12_dataset_manifest_binds_no_integrity_digest(self):
        def mutate(section, _architecture):
            section["dataset_governance"]["required_bindings"].remove("integrity_digest")
        self.assertFires("CDH-12", mutate)

    def test_cdh_12_effective_change_leaves_identity_unchanged(self):
        def mutate(section, _architecture):
            section["dataset_governance"]["effective_change_produces_new_identity"] = False
        self.assertFires("CDH-12", mutate)

    def test_cdh_13_test_population_not_separately_identifiable(self):
        def mutate(section, _architecture):
            section["partition_integrity"]["partitions"].remove("external_independent_test")
        self.assertFires("CDH-13", mutate)

    def test_cdh_13_cases_may_move_between_partitions_after_freeze(self):
        def mutate(section, _architecture):
            section["partition_integrity"]["silent_movement_after_freeze"] = "permitted"
        self.assertFires("CDH-13", mutate)

    def test_cdh_13_partition_identity_outside_the_workload_digest(self):
        def mutate(section, _architecture):
            development = member(section["workload_classes"]["classes"], "WLC-MODELDEV-01")
            field(development["additional_canonical_fields"], "partition_identity")["in_digest"] = False
        self.assertFires("CDH-13", mutate)

    def test_cdh_14_model_identified_by_filename(self):
        def mutate(section, _architecture):
            section["model_artifact"]["identity_by_filename"] = "permitted"
        self.assertFires("CDH-14", mutate)

    def test_cdh_14_model_not_bound_to_the_training_workload(self):
        def mutate(section, _architecture):
            section["model_artifact"]["required_bindings"].remove("originating_training_workload_digest")
        self.assertFires("CDH-14", mutate)

    def test_cdh_14_development_result_carries_no_model_digest(self):
        def mutate(section, _architecture):
            development = member(section["workload_classes"]["classes"], "WLC-MODELDEV-01")
            development["result_binds"].remove("model_artifact_digest")
        self.assertFires("CDH-14", mutate)


class PromotionAndSubstitution(ControlHarness):
    def test_cdh_15_evaluation_success_given_authority(self):
        def mutate(section, _architecture):
            member(section["model_promotion"]["stages"], "PROMO-STAGE-02")["authority"] = "release_authority"
        self.assertFires("CDH-15", mutate)

    def test_cdh_15_authorization_conferred_without_a_professional_decision(self):
        def mutate(section, _architecture):
            member(section["model_promotion"]["stages"], "PROMO-STAGE-04")["conferred_by"] = "evaluation_suite"
        self.assertFires("CDH-15", mutate)

    def test_cdh_15_validation_declared_to_imply_qualification(self):
        def mutate(section, _architecture):
            section["model_promotion"]["non_implication"] = [
                pair for pair in section["model_promotion"]["non_implication"]
                if pair["from"] != "validation_success"
            ]
        self.assertFires("CDH-15", mutate)

    def test_cdh_15_parallel_approval_mechanism_permitted(self):
        def mutate(section, _architecture):
            section["model_promotion"]["parallel_approval_mechanism"] = "permitted"
        self.assertFires("CDH-15", mutate)

    def test_cdh_15_promotion_cites_an_authority_structure_that_does_not_exist(self):
        def mutate(section, _architecture):
            section["model_promotion"]["reuses_existing_authority_structures"].append("AB-099")
        self.assertFires("CDH-15", mutate)

    def test_cdh_16_model_identity_outside_the_authorization_digest(self):
        def mutate(section, _architecture):
            inference = member(section["workload_classes"]["classes"], "WLC-INFERENCE-01")
            field(inference["additional_canonical_fields"], "qualified_model_digest")["in_digest"] = False
        self.assertFires("CDH-16", mutate)

    def test_cdh_16_substitution_permitted_without_contract_authorization(self):
        def mutate(section, _architecture):
            section["model_substitution"]["permitted_only_when"] = "capacity_constrained_dispatch"
        self.assertFires("CDH-16", mutate)

    def test_cdh_16_model_identity_not_declared_digest_bound(self):
        def mutate(section, _architecture):
            section["model_substitution"]["model_identity_in_authorization_bound_digest"] = False
        self.assertFires("CDH-16", mutate)

    def test_cdh_17_composite_identity_erases_its_constituents(self):
        def mutate(section, _architecture):
            section["multi_dataset_development"]["composite_identity"]["erases_constituent_identity"] = True
        self.assertFires("CDH-17", mutate)

    def test_cdh_17_constituent_identity_not_retained(self):
        def mutate(section, _architecture):
            section["multi_dataset_development"]["constituent_identity_retained"] = False
        self.assertFires("CDH-17", mutate)

    def test_cdh_18_bitwise_weights_required_of_nondeterministic_training(self):
        def mutate(section, _architecture):
            section["reproducibility"]["bitwise_identical_trained_weights_required"] = True
        self.assertFires("CDH-18", mutate)

    def test_cdh_18_workload_class_with_no_reproducibility_expectation(self):
        def mutate(section, _architecture):
            section["reproducibility"]["class_bindings"] = [
                binding for binding in section["reproducibility"]["class_bindings"]
                if binding["workload_class"] != "WLC-LANGSVC-01"
            ]
        self.assertFires("CDH-18", mutate)

    def test_cdh_18_equivalence_class_that_is_not_declared(self):
        def mutate(section, _architecture):
            section["reproducibility"]["class_bindings"][0]["equivalence_acceptance_class"] = "EQ-WHATEVER-01"
        self.assertFires("CDH-18", mutate)


class LanguageServiceSubordination(ControlHarness):
    def test_cdh_19_service_given_authority(self):
        def mutate(section, _architecture):
            section["language_service_hosting"]["services"][0]["authority"] = "clinical_decision"
        self.assertFires("CDH-19", mutate)

    def test_cdh_19_output_permitted_to_authorize(self):
        def mutate(section, _architecture):
            section["language_service_hosting"]["subordination"]["may_produce_authorization_decision"] = True
        self.assertFires("CDH-19", mutate)

    def test_cdh_19_output_permitted_to_satisfy_a_professional_decision(self):
        def mutate(section, _architecture):
            section["language_service_hosting"]["subordination"]["may_satisfy_professional_decision"] = True
        self.assertFires("CDH-19", mutate)

    def test_cdh_19_services_moved_out_of_the_zero_authority_zone(self):
        def mutate(section, _architecture):
            section["language_service_hosting"]["trust_zone"] = "Z1-KERNEL"
        self.assertFires("CDH-19", mutate)

    def test_cdh_19_services_placed_in_a_zone_that_does_not_exist(self):
        def mutate(section, _architecture):
            section["language_service_hosting"]["trust_zone"] = "Z9-LLM"
        self.assertFires("CDH-19", mutate)

    def test_cdh_19_unaffected_invariant_does_not_exist(self):
        def mutate(section, _architecture):
            section["language_service_hosting"]["invariant_unaffected"] = "ARCH-INVARIANT-404"
        self.assertFires("CDH-19", mutate)

    def test_cdh_19_language_workload_class_holds_authority(self):
        def mutate(section, _architecture):
            member(section["workload_classes"]["classes"], "WLC-LANGSVC-01")["authority"] = "eligibility"
        self.assertFires("CDH-19", mutate)


class RecordIntegrity(ControlHarness):
    def test_declared_control_that_is_not_implemented(self):
        def mutate(section, _architecture):
            section["structural_controls"]["controls"].append(
                {"id": "CDH-99", "name": "imaginary", "detects": "nothing, because it does not exist"}
            )
        self.assertFires("registry", mutate)

    def test_implemented_control_that_the_record_stops_declaring(self):
        def mutate(section, _architecture):
            section["structural_controls"]["controls"] = [
                entry for entry in section["structural_controls"]["controls"]
                if entry["id"] != "CDH-09"
            ]
        self.assertFires("registry", mutate)

    def test_proposition_recorded_above_the_checkpoint_ceiling(self):
        """Presence in a controlled record is not verification."""
        def mutate(section, _architecture):
            member(section["acceptance_propositions"], "ARCH-DGX-01-A3")["verification_state"] = "VERIFIED"
        findings = self.assertFires("registry", mutate)
        self.assertTrue(any("ceiling" in message for _, message in findings))

    def test_design_proposition_promoted_to_allocated(self):
        def mutate(section, _architecture):
            member(section["acceptance_propositions"], "ARCH-DGX-01-A5")["verification_state"] = "ALLOCATED"
        self.assertFires("registry", mutate)

    def test_structural_proposition_with_no_control(self):
        def mutate(section, _architecture):
            member(section["acceptance_propositions"], "ARCH-DGX-01-A4")["structural_control"] = None
        self.assertFires("registry", mutate)

    def test_proposition_without_a_future_obligation(self):
        def mutate(section, _architecture):
            member(section["acceptance_propositions"], "ARCH-DGX-01-A9")["future_verification_obligation"] = ""
        self.assertFires("registry", mutate)


class CrossReference(ControlHarness):
    def test_decision_record_missing_from_the_register(self):
        def mutate(section, _architecture):
            return None

        def drop(decisions):
            decisions["decisions"] = [
                record for record in decisions["decisions"] if record["id"] != "ADR-003"
            ]
        self.assertFires("cross-reference", mutate, decisions_mutate=drop)

    def test_decision_record_claims_an_approved_authority_cutover(self):
        def mutate(section, _architecture):
            return None

        def approve(decisions):
            for record in decisions["decisions"]:
                if record["id"] == "ADR-003":
                    record["authority_cutover_status"] = "approved"
        self.assertFires("cross-reference", mutate, decisions_mutate=approve)

    def test_decision_record_both_permits_and_prohibits(self):
        def mutate(section, _architecture):
            return None

        def contradict(decisions):
            for record in decisions["decisions"]:
                if record["id"] == "ADR-003":
                    record["permits_now"].append(record["does_not_permit"][0])
        self.assertFires("cross-reference", mutate, decisions_mutate=contradict)

    def test_architecture_decision_stops_pointing_at_this_structure(self):
        def mutate(section, architecture):
            member(architecture["architecture_decisions"], "AB-013")["structure"] = "somewhere_else"
        self.assertFires("cross-reference", mutate)

    def test_invariant_not_attributed_to_the_amendment(self):
        def mutate(section, architecture):
            member(architecture["invariants"], "ARCH-INVARIANT-002").pop("amendment")
        self.assertFires("cross-reference", mutate)


class ProcessVerdict(unittest.TestCase):
    """The exit code is observed as a process exit code, never as an exception type."""

    def run_against(self, architecture: dict, decisions: dict) -> int:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            arch_path = root / "architecture.yaml"
            dec_path = root / "decisions.yaml"
            with io.open(arch_path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(yaml.safe_dump(architecture, sort_keys=False, allow_unicode=True))
            with io.open(dec_path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(yaml.safe_dump(decisions, sort_keys=False, allow_unicode=True))
            wrapper = root / "wrapper.py"
            with io.open(wrapper, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(textwrap.dedent(f"""
                    import sys
                    from pathlib import Path
                    sys.path.insert(0, {str(REPO_ROOT / "tools" / "spec")!r})
                    import check_computational_hosting as gate
                    gate.ARCHITECTURE = Path({str(arch_path)!r})
                    gate.DECISIONS = Path({str(dec_path)!r})
                    sys.exit(gate.main([]))
                """).strip())
            result = subprocess.run(
                [sys.executable, str(wrapper)], capture_output=True, text=True, cwd=str(REPO_ROOT)
            )
            self.last = result
            return result.returncode

    def test_live_record_exits_zero(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "spec" / "check_computational_hosting.py")],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        self.assertEqual(result.returncode, VERDICT_PASS, result.stderr)
        self.assertIn("PASS", result.stdout)
        self.assertIn("not a running system", result.stdout)

    def test_substantive_finding_exits_one(self):
        architecture = copy.deepcopy(ARCHITECTURE)
        architecture[gate.SECTION_KEY]["reconciliation"]["sufficiency"] = "sufficient"
        self.assertEqual(self.run_against(architecture, copy.deepcopy(DECISIONS)), SUBSTANTIVE_FINDING)
        self.assertIn("CDH-10", self.last.stderr)
        self.assertNotIn(gate.MARKER, self.last.stderr)

    def test_unmeasurable_record_exits_two(self):
        architecture = copy.deepcopy(ARCHITECTURE)
        architecture.pop(gate.SECTION_KEY)
        self.assertEqual(self.run_against(architecture, copy.deepcopy(DECISIONS)), MEASUREMENT_INVALID)
        self.assertIn(gate.MARKER, self.last.stderr)

    def test_hollowed_section_is_unmeasurable_not_compliant(self):
        architecture = copy.deepcopy(ARCHITECTURE)
        architecture[gate.SECTION_KEY] = {"amendment_id": "ARCH-DGX-01"}
        self.assertEqual(self.run_against(architecture, copy.deepcopy(DECISIONS)), MEASUREMENT_INVALID)
        self.assertIn(gate.MARKER, self.last.stderr)


if __name__ == "__main__":
    unittest.main()


class DeploymentProfiles(ControlHarness):
    def test_cdh_20_profile_running_a_different_runtime(self):
        def mutate(section, _architecture):
            member(section["deployment_profiles"]["profiles"], "DEPL-MANAGED-CLOUD-01")["runtime"] = "RT-CLOUD-02"
        self.assertFires("CDH-20", mutate)

    def test_cdh_20_profile_carrying_its_own_workload_envelope(self):
        def mutate(section, _architecture):
            member(section["deployment_profiles"]["profiles"], "DEPL-HYBRID-01")["workload_envelope"] = "GW-HYBRID-02"
        self.assertFires("CDH-20", mutate)

    def test_cdh_20_invariant_semantic_declared_variable_by_profile(self):
        def mutate(section, _architecture):
            section["deployment_profiles"]["may_vary"].append("authorization semantics")
            section["deployment_profiles"]["may_not_vary"].append("authorization semantics")
        self.assertFires("CDH-20", mutate)

    def test_cdh_20_preserved_semantics_made_profile_specific(self):
        def mutate(section, _architecture):
            preserved = section["deployment_profiles"]["preserved_across_profiles"][0]
            section["deployment_profiles"]["may_vary"].append(preserved)
        self.assertFires("CDH-20", mutate)

    def test_cdh_20_reference_host_declared_a_special_case_architecture(self):
        def mutate(section, _architecture):
            section["product_invariant"]["dgx_is_a_special_case_product_architecture"] = True
        self.assertFires("CDH-20", mutate)

    def test_cdh_20_invariant_semantic_dropped_from_the_declared_set(self):
        """Dropping one entry leaves every sentence about profiles intact."""
        def mutate(section, _architecture):
            section["deployment_profiles"]["may_not_vary"].remove("model identity")
        findings = self.assertFires("CDH-20", mutate)
        self.assertTrue(any("model identity" in message for _, message in findings))

    def test_cdh_21_capacity_may_override_locality(self):
        def mutate(section, _architecture):
            section["workload_locality"]["capacity_may_override_locality"] = True
        self.assertFires("CDH-21", mutate)

    def test_cdh_21_scheduling_may_cross_the_institutional_boundary(self):
        def mutate(section, _architecture):
            section["workload_locality"]["crossing_institutional_boundary_by_scheduling"] = "permitted"
        self.assertFires("CDH-21", mutate)

    def test_cdh_21_locality_outside_the_authorization_digest(self):
        def mutate(section, _architecture):
            field(section["governed_workload"]["canonical_fields"], "data_locality_classification")["in_digest"] = False
        self.assertFires("CDH-21", mutate)

    def test_cdh_21_dispatch_may_choose_a_locality(self):
        def mutate(section, _architecture):
            section["contracts"]["DispatchContract"]["mutable_fields"].append("data_locality_classification")
        self.assertFires("CDH-21", mutate)

    def test_cdh_21_no_class_keeps_a_workload_inside_the_boundary(self):
        def mutate(section, _architecture):
            for entry in section["workload_locality"]["classes"]:
                entry["may_leave_institutional_boundary"] = True
        self.assertFires("CDH-21", mutate)


class ProductDelivery(ControlHarness):
    def test_cdh_22_tenant_isolation_recorded_as_implemented(self):
        def mutate(section, _architecture):
            section["tenant_isolation"]["implementation_state"] = "implemented"
        self.assertFires("CDH-22", mutate)

    def test_cdh_22_tenant_isolation_recorded_as_qualified(self):
        def mutate(section, _architecture):
            section["tenant_isolation"]["qualification_state"] = "qualified"
        self.assertFires("CDH-22", mutate)

    def test_cdh_22_cross_tenant_context_access_permitted(self):
        def mutate(section, _architecture):
            section["tenant_isolation"]["cross_tenant_context_access"] = "permitted_for_shared_models"
        self.assertFires("CDH-22", mutate)

    def test_cdh_22_isolation_declared_claimable_now(self):
        def mutate(section, _architecture):
            section["tenant_isolation"]["claimable_now"] = True
        self.assertFires("CDH-22", mutate)

    def test_cdh_23_product_forks_permitted(self):
        def mutate(section, _architecture):
            section["runtime_packaging"]["product_forks"] = "permitted_per_profile"
        self.assertFires("CDH-23", mutate)

    def test_cdh_23_package_identity_not_content_derived(self):
        def mutate(section, _architecture):
            section["runtime_packaging"]["package_identity_basis"] = "release_tag"
        self.assertFires("CDH-23", mutate)

    def test_cdh_23_package_identity_field_outside_the_digest(self):
        def mutate(section, _architecture):
            field(section["governed_workload"]["canonical_fields"], "software_runtime_identity")["in_digest"] = False
        self.assertFires("CDH-23", mutate)

    def test_cdh_23_packaged_runtime_is_not_the_deployed_runtime(self):
        def mutate(section, _architecture):
            section["runtime_packaging"]["runtime"] = "RT-SOMETHING-ELSE"
        self.assertFires("CDH-23", mutate)

    def test_cdh_24_runtime_may_advance_silently(self):
        def mutate(section, _architecture):
            section["release_and_rollback"]["silent_runtime_advance"] = "permitted"
        self.assertFires("CDH-24", mutate)

    def test_cdh_24_clinical_model_may_advance_silently(self):
        def mutate(section, _architecture):
            section["release_and_rollback"]["silent_clinical_model_advance"] = "permitted_when_newer"
        self.assertFires("CDH-24", mutate)

    def test_cdh_24_cloud_profile_exempted_from_release_control(self):
        def mutate(section, _architecture):
            section["release_and_rollback"]["applies_to_profiles"].remove("DEPL-MANAGED-CLOUD-01")
        self.assertFires("CDH-24", mutate)

    def test_cdh_24_explicit_exemption_recorded(self):
        def mutate(section, _architecture):
            section["release_and_rollback"]["exemptions"].append("DEPL-MANAGED-CLOUD-01")
        self.assertFires("CDH-24", mutate)

    def test_cdh_24_rollback_dropped_from_required_capabilities(self):
        def mutate(section, _architecture):
            section["release_and_rollback"]["required_capabilities"].remove("rollback")
        self.assertFires("CDH-24", mutate)

    def test_cdh_25_service_hosted_in_the_system_of_record_zone(self):
        def mutate(section, _architecture):
            member(section["standalone_runtime_services"]["services"], "SVC-DICOM-01")["trust_zone"] = "Z3-SOR"
        self.assertFires("CDH-25", mutate)

    def test_cdh_25_service_holding_more_authority_than_its_zone(self):
        def mutate(section, _architecture):
            member(section["standalone_runtime_services"]["services"], "SVC-INFER-01")["authority"] = "commissioned_or_system_of_record_authority"
        self.assertFires("CDH-25", mutate)

    def test_cdh_25_external_systems_no_longer_external(self):
        def mutate(section, _architecture):
            section["standalone_runtime_services"]["external_authoritative_systems_remain_external"] = False
        self.assertFires("CDH-25", mutate)

    def test_cdh_25_profile_absorbs_the_external_authoritative_system(self):
        def mutate(section, _architecture):
            member(section["deployment_profiles"]["profiles"], "DEPL-STANDALONE-01")["external_authoritative_systems_remain_external"] = False
        self.assertFires("CDH-25", mutate)


class SessionControlDrift(ControlHarness):
    def test_stated_control_count_is_checked_against_the_population(self):
        """A number in prose goes stale in silence, so it is derived and compared."""
        findings = gate.session_control_findings(ARCHITECTURE[gate.SECTION_KEY])
        self.assertEqual(findings, [], findings)

    def test_drifted_count_is_reported(self):
        section = copy.deepcopy(ARCHITECTURE[gate.SECTION_KEY])
        section["acceptance_propositions"].append(
            {"id": "ARCH-DGX-01-A99", "class": "structural", "verification_state": "ALLOCATED"}
        )
        findings = gate.session_control_findings(section)
        self.assertTrue(findings, "an added proposition did not make the stated count stale")
