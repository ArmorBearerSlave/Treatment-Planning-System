"""F1: the retention policy and the hygiene policy are compatible, as policies.

MPS-MAT-009 F1 exposed a defect class the suite had no way to see: two controls can each be
locally correct while their conjunction is unsatisfiable. At 1b58895 the currency mechanism
required the runner's retained artifacts and the hygiene gate rejected exactly those
artifacts, so no repository state could satisfy both, and every gate's own tests passed
throughout because each was validated only against the artifacts it reads.

Observing one repaired state where both gates are green does not repair that. It establishes

    there EXISTS a state S with CurrencyPass(S) and HygienePass(S)

which is weaker than the property F1 is about: that the two policies agree over the whole
class of artifacts the currency mechanism requires. So this drives every member of that class
through both policies in canonical and deliberately non-canonical form and requires all four
cells:

                          canonical form      non-canonical form
    hygiene accepts             yes                   no
    currency accepts            yes                   no

The positive cells prove joint satisfiability. The negative cells prove the result is not
vacuous -- a hygiene gate that accepts everything, or a currency gate that accepts raw
retained evidence, would satisfy the positive cells while being no repair at all.

The non-canonical member is the SAME declared type and still parses. Rejection therefore has
to be attributable to canonicality and disclosure policy, not to the file having been broken.
"""
from __future__ import annotations

import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools" / "mps"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "repo"))

import canonicalize_evidence as canon  # noqa: E402
import check_headless_build_currency as currency  # noqa: E402
import check_repository_hygiene as hygiene  # noqa: E402

EVIDENCE = REPO_ROOT / "mps" / "materialization" / "headless-acceptance-evidence.json"
ALLOWLIST = REPO_ROOT / "mps" / "materialization" / "evidence-allowlist.yaml"

# A host-profile path, assembled rather than written literally so this test file does not
# itself trip the disclosure scan it is exercising.
DISCLOSURE = "C:" + chr(92) + "Users" + chr(92) + "someone"


def required_population() -> list[tuple[str, str, str]]:
    """(label, relative path, recorded sha256) for every artifact currency requires."""
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    holders = {
        "build log": ((evidence.get("build") or {}), "log"),
        "model-test report": ((evidence.get("model_tests") or {}), "report"),
    }
    for name, control in sorted((evidence.get("controls") or {}).items()):
        for kind in ("report", "patch"):
            holders[f"{name} {kind}"] = (control, kind)
    population = []
    for label, (holder, key) in holders.items():
        reference = holder.get(key)
        if reference:
            population.append((label, reference, holder.get(key + "_sha256")))
    return population


def non_canonical_variant(raw: bytes, suffix: str) -> bytes:
    """A same-type, still-parseable, demonstrably non-canonical form of the artifact.

    Not "some malformed file": the point is that rejection must be attributable to the
    canonicality and disclosure policies rather than to a syntax error, so the variant has to
    survive its own type validation.
    """
    text = raw.decode("utf-8", errors="replace")
    if suffix.casefold() == ".xml":
        # A comment keeps the document well-formed while carrying prohibited content.
        marker = "<!-- retained from " + DISCLOSURE + " -->"
        head, sep, tail = text.partition(">")
        return (head + sep + marker + tail).encode("utf-8")
    return (text + "retained from " + DISCLOSURE + chr(10)).encode("utf-8")


class RequiredPopulation(unittest.TestCase):

    def test_the_population_is_enumerated_mechanically_and_is_not_empty(self):
        population = required_population()
        self.assertTrue(population, "an empty class makes the four-cell contract vacuous")
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        # The same enumeration the gate itself uses, so the control cannot test a subset.
        self.assertEqual(
            sorted(reference for _, reference, _ in population),
            sorted(reference for _, reference in currency.required_artifacts(evidence)))

    def test_every_required_artifact_exists_and_is_retained_in_the_evidence_tree(self):
        for label, reference, _ in required_population():
            self.assertTrue(reference.startswith("mps/materialization/evidence/"), label)
            self.assertTrue((REPO_ROOT / reference).is_file(), f"{label}: {reference}")


class FourCellContract(unittest.TestCase):
    """Both policies, over every member of the required class, in both forms."""

    def setUp(self):
        self.allowlist, problems = hygiene.load_generated_type_allowlist()
        self.assertEqual([], problems, "the allowlist must itself be valid")
        self.population = required_population()

    def test_cell_1_hygiene_accepts_every_canonical_required_artifact(self):
        for label, reference, _ in self.population:
            with self.subTest(artifact=reference):
                errors, crlf = hygiene.file_problems(reference, REPO_ROOT / reference,
                                                     self.allowlist)
                self.assertEqual([], errors, f"{label}: {errors}")
                self.assertFalse(crlf)

    def test_cell_2_currency_accepts_every_canonical_required_artifact(self):
        for label, reference, digest in self.population:
            with self.subTest(artifact=reference):
                self.assertEqual([], currency.artifact_problems(label, reference, digest))

    def test_cell_3_hygiene_rejects_every_non_canonical_required_artifact(self):
        """Same type, still parses, and still refused."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for label, reference, _ in self.population:
                with self.subTest(artifact=reference):
                    source = REPO_ROOT / reference
                    variant = non_canonical_variant(source.read_bytes(), source.suffix)
                    # It must genuinely be non-canonical, and genuinely still its own type.
                    self.assertNotEqual(canon.canonicalize_bytes(variant), variant)
                    intact, why = canon.structurally_intact(variant, source.suffix)
                    self.assertTrue(intact, f"{label}: variant must stay parse-valid: {why}")

                    target = root / Path(reference).name
                    target.write_bytes(variant)
                    errors, _ = hygiene.file_problems(reference, target, self.allowlist)
                    self.assertTrue(errors, f"{label}: hygiene accepted a non-canonical form")
                    self.assertTrue(any("user-profile" in e for e in errors),
                                    f"{label}: rejection must be attributable to disclosure, "
                                    f"got {errors}")

    def test_cell_4_currency_rejects_every_non_canonical_required_artifact(self):
        """Rejected on canonicality, with the hash deliberately made to agree.

        The variant's own digest is passed in, so the hash check cannot be what fires. If it
        were, this cell would prove only that currency notices changed bytes -- which it
        already did before F1 -- rather than that it enforces canonical form.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "mps" / "materialization" / "evidence"
            for label, reference, _ in self.population:
                with self.subTest(artifact=reference):
                    source = REPO_ROOT / reference
                    variant = non_canonical_variant(source.read_bytes(), source.suffix)
                    target = Path(tmp) / reference
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(variant)
                    digest = hashlib.sha256(variant).hexdigest()
                    problems = currency.artifact_problems(label, reference, digest,
                                                          root=Path(tmp))
                    self.assertTrue(problems,
                                    f"{label}: currency accepted a non-canonical artifact")
                    self.assertTrue(any("canonical form" in p for p in problems),
                                    f"{label}: rejection must be attributable to "
                                    f"canonicality, got {problems}")


class SameStateCoIdentity(unittest.TestCase):
    """Both gates must have inspected the same state, not two states in sequence."""

    @staticmethod
    def state_manifest() -> str:
        """A digest over everything both policies depend on."""
        parts = []
        for label, reference, digest in sorted(required_population()):
            path = REPO_ROOT / reference
            actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""
            parts.append(f"{reference}|{digest}|{actual}")
        parts.append("record|" + hashlib.sha256(EVIDENCE.read_bytes()).hexdigest())
        parts.append("allowlist|" + hashlib.sha256(ALLOWLIST.read_bytes()).hexdigest())
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        parts.append("model_tree|" + str(evidence.get("model_tree_sha256")))
        return hashlib.sha256(chr(10).join(parts).encode("utf-8")).hexdigest()

    def test_both_policies_pass_on_one_state_whose_identity_did_not_move(self):
        before = self.state_manifest()

        allowlist, problems = hygiene.load_generated_type_allowlist()
        self.assertEqual([], problems)
        currency_verdict = []
        for label, reference, digest in required_population():
            currency_verdict.extend(currency.artifact_problems(label, reference, digest))

        between = self.state_manifest()

        hygiene_verdict = []
        for label, reference, _ in required_population():
            errors, crlf = hygiene.file_problems(reference, REPO_ROOT / reference, allowlist)
            hygiene_verdict.extend(errors)
            if crlf:
                hygiene_verdict.append(f"{reference} carries CRLF")

        after = self.state_manifest()

        self.assertEqual([], currency_verdict)
        self.assertEqual([], hygiene_verdict)
        # Without this, the result would be "some state satisfied currency and some state
        # satisfied hygiene", which is the execution/state co-identity defect recorded
        # elsewhere in this programme, committed here.
        self.assertEqual(before, between, "state moved between the two policy evaluations")
        self.assertEqual(between, after, "state moved during the second evaluation")


if __name__ == "__main__":
    unittest.main()
