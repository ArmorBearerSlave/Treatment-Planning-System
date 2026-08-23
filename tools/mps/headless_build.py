"""Build the controlled MPS project from a fresh process, outside the interactive IDE.

MPS-MAT-008 asks for a build that does not go through the experimental agent toolkit. The
distinction it is drawing is not cosmetic: every native build up to that point was a
whole-project rebuild issued by `mps_mcp_alter_nodes MAKE` into an already-running IDE, and
a rebuild that succeeds inside the IDE is not evidence that one succeeds without it.

What this runs is MPS's own headless machinery. The pinned installation ships Apache Ant
(lib/ant), a JDK (jbr), and the MPS Ant task library (lib/ant/lib/ant-mps.jar). The build
file drives <mps.make>, which forks jetbrains.mps.tool.builder.CoreWorker into a separate
JVM. Nothing in the path opens a socket to the IDE, and the IDE need not be running.

The toolchain is taken entirely from the pinned installation. A system Ant or an ambient
JAVA_HOME would make the result depend on whatever the host happens to have, which is the
opposite of the reproducibility this item is about, so neither is consulted. The MPS build
number is read from <MPS_HOME>/build.txt and compared with the pinned value in
mps/materialization/stage-a-checklist.yaml; a mismatch is refused rather than reported,
because a build produced by a different MPS is a different qualification question.

What this does NOT do is evaluate the languages' checking rules. That was established
empirically, not assumed: a VerificationClaim violating REA-C-002 and REA-C-003 was placed
in nltps.proof.cases, confirmed to be rejected by the model checker, and the headless build
then completed successfully with exit code 0. Generation and compilation are not checking.
The limitation is recorded against MPS-MAT-008 rather than papered over.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_FILE = REPO_ROOT / "build" / "nltps-headless-build.xml"
PROJECT_DIR = REPO_ROOT / "mps" / "NLTPSGovernance"
PLAN_PATH = REPO_ROOT / "mps" / "materialization" / "stage-a-checklist.yaml"
PROVENANCE = REPO_ROOT / "mps" / "materialization" / "headless-build-provenance.json"
DEFAULT_MPS_HOME = Path(r"C:\Program Files\JetBrains\MPS 2026.1")

# Derived output. Excluded from the model-tree hash because regenerating it must not make
# the recorded build evidence look stale, and included in .gitignore for the same reason.
DERIVED_DIRS = {"source_gen", "source_gen.caches", "classes_gen", "test_gen",
                "test_gen.caches", "work"}
DERIVED_FILES = {"workspace.xml", "tasks.xml", "tasks.ids", "usageStatistics.xml"}

# The generated-output directories a cold run must remove from the project. "work" is
# excluded deliberately: the worker's system/config/log tree lives under build/work, outside
# the project, and is handled separately.
GENERATED_DIRS = {"source_gen", "source_gen.caches", "classes_gen", "test_gen",
                  "test_gen.caches"}


def generated_directories(project_dir: Path) -> list[Path]:
    """Every generated-output directory currently present under the project.

    This is the population a cold run must empty, and the population a receipt reports on.
    It is computed by walking the tree rather than by trusting a previous run's record,
    because the whole point of the observation is that the previous run's record is what is
    in doubt.
    """
    found: list[Path] = []
    for path in sorted(project_dir.rglob("*")):
        if path.is_dir() and path.name in GENERATED_DIRS:
            # A nested match inside an already-matched directory is part of that directory,
            # not a second one; counting it would inflate the population.
            if any(parent in found for parent in path.parents):
                continue
            found.append(path)
    return found


def make_cold(project_dir: Path) -> dict:
    """Delete every generated-output directory, then observe that none remains.

    Coldness has been the single most load-bearing premise in this programme and the one
    nothing measured: the recorder wrote `cold: true` as a literal, and a build log declaring
    itself a warm incremental build recorded cold anyway. POST-MPS4-01 exists because four
    checkpoints stayed green on stale output. So coldness is established here by removing the
    output and then looking, and the looking is what is reported -- an emptied tree that still
    contains a generated directory is refused rather than recorded.
    """
    import shutil

    before = generated_directories(project_dir)
    for path in before:
        shutil.rmtree(path, ignore_errors=True)
    remaining = generated_directories(project_dir)
    if remaining:
        raise ToolchainError(
            f"cold run requested but {len(remaining)} generated directories survived "
            f"deletion (first: {remaining[0]}). Refusing to build: a run that calls itself "
            f"cold over a tree that is not empty is the exact claim this observation exists "
            f"to prevent.")
    return {
        "requested": True,
        "observed_cold": True,
        "generated_directories_before": len(before),
        "generated_directories_deleted": len(before),
        "generated_directories_remaining": 0,
    }


def observe_warm(project_dir: Path) -> dict:
    """The same observation for a run that was not asked to be cold.

    Recorded rather than omitted, because "cold was not requested" and "cold was requested
    and achieved" must be distinguishable in the receipt without reading the invocation.
    """
    present = generated_directories(project_dir)
    return {
        "requested": False,
        "observed_cold": not present,
        "generated_directories_before": len(present),
        "generated_directories_deleted": 0,
        "generated_directories_remaining": len(present),
    }


class ToolchainError(Exception):
    """The build environment is not the pinned one. Refused, not worked around."""


def pinned_build() -> str:
    import yaml

    with io.open(PLAN_PATH, encoding="utf-8") as handle:
        plan = yaml.safe_load(handle.read())
    return plan["pinned_toolchain"]["build"]


def mps_home() -> Path:
    raw = os.environ.get("MPS_HOME")
    return Path(raw) if raw else DEFAULT_MPS_HOME


def validate_toolchain(home: Path) -> dict:
    """Everything the build needs, checked before anything is generated."""
    if not home.is_dir():
        raise ToolchainError(
            f"MPS installation not found at {home}. Set MPS_HOME to the pinned "
            f"installation, or install it.")

    build_txt = home / "build.txt"
    if not build_txt.is_file():
        raise ToolchainError(f"{home} has no build.txt; it does not look like an MPS "
                             f"installation")
    with io.open(build_txt, encoding="utf-8") as handle:
        actual = handle.read().strip()
    expected = pinned_build()
    if actual != expected:
        raise ToolchainError(
            f"MPS build {actual!r} at {home} is not the pinned build {expected!r}. A "
            f"different build is a separate qualification decision, not a substitution "
            f"this build may make.")

    java = home / "jbr" / "bin" / ("java.exe" if os.name == "nt" else "java")
    ant = home / "lib" / "ant" / "lib" / "ant.jar"
    launcher = home / "lib" / "ant" / "lib" / "ant-launcher.jar"
    tasks = home / "lib" / "ant" / "lib" / "ant-mps.jar"
    for path, what in ((java, "bundled JDK"), (ant, "bundled Ant"),
                       (launcher, "bundled Ant launcher"), (tasks, "MPS Ant tasks")):
        if not path.is_file():
            raise ToolchainError(f"{what} is missing at {path}")

    if not BUILD_FILE.is_file():
        raise ToolchainError(f"build descriptor is missing: {BUILD_FILE}")
    if not PROJECT_DIR.is_dir():
        raise ToolchainError(f"MPS project is missing: {PROJECT_DIR}")

    return {"mps_home": str(home), "mps_build": actual, "java": str(java),
            "ant": str(ant), "launcher": str(launcher)}


def java_identity(java: Path) -> str:
    result = subprocess.run([str(java), "-version"], capture_output=True, text=True)
    return (result.stderr or result.stdout).strip().splitlines()[0] if (
        result.stderr or result.stdout) else "unknown"


def controlled_files(project_dir: Path) -> list[Path]:
    """The build's semantic inputs: everything MPS reads, minus what MPS writes."""
    found = []
    for path in project_dir.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.parts)
        if DERIVED_DIRS & parts or path.name in DERIVED_FILES:
            continue
        found.append(path)
    return sorted(found)


def model_tree_hash(project_dir: Path) -> str:
    """A deterministic fingerprint of the build's inputs.

    The currency question is whether the model changed since the recorded build, so this
    covers the models, module descriptors and project module registry, and nothing that a
    build produces. A documentation commit elsewhere in the repository does not move it,
    which is why staleness is keyed on this rather than on a commit sha.

    Line endings are normalised before hashing, and that is a correctness requirement
    rather than a convenience. MPS writes CRLF; .gitattributes declares `* text=auto eol=lf`
    so the repository stores LF; git therefore reports a clean tree while 184 of the 185
    controlled files differ byte-for-byte from what a clone receives. Hashing raw bytes
    produced a currency key that verified on the machine that computed it and on no other --
    the same defect as a retained report stored CRLF, at the centre of the package instead of
    at its edge.

    This does not relax a determinism gate. The byte-exact corpus and trace gates are
    unchanged; what changes is a key whose job is to answer "is this the same model", and
    line endings are not part of model identity -- git itself treats the two forms as the
    same content. Normalising makes the key equal to what the repository stores, which is
    what a reviewer can actually reproduce.
    """
    if not project_dir.is_dir():
        raise ToolchainError(
            f"cannot compute a model tree hash: {project_dir} is not a directory. This is a "
            f"measurement failure, not a result. Returning a hash here would report the "
            f"digest of an empty corpus -- e3b0c44298fc..., the SHA-256 of the empty string -- "
            f"which a caller would compare against a recorded value and report as staleness: "
            f"a specific, confident, wrong finding about the model.")
    if not (project_dir / ".mps" / "modules.xml").is_file():
        raise ToolchainError(
            f"cannot compute a model tree hash: {project_dir} has no .mps/modules.xml, so it "
            f"is not an MPS project root. A directory that merely contains files will hash "
            f"successfully and produce a plausible answer to a question about a different "
            f"corpus -- the failure mode is a confident result, not an error.")
    files = controlled_files(project_dir)
    if not files:
        raise ToolchainError(
            f"cannot compute a model tree hash: {project_dir} resolved to zero controlled "
            f"files. An empty population must refuse rather than hash, for the same reason a "
            f"test task over zero discovered tests is not a pass.")

    digest = hashlib.sha256()
    for path in files:
        digest.update(str(path.relative_to(project_dir)).replace("\\", "/").encode())
        digest.update(b"\0")
        with io.open(path, "rb") as handle:
            digest.update(hashlib.sha256(handle.read().replace(b"\r\n", b"\n")).digest())
    return digest.hexdigest()


def receipt_path(log_path: Path) -> Path:
    """The receipt that describes one run, beside the log that run produced."""
    return log_path.with_suffix(log_path.suffix + ".receipt.json")


def run_build(toolchain: dict, log_path: Path, heap: str, target: str,
              project_dir: Path, cold: bool) -> dict:
    """Run one Ant target and write a receipt describing what was actually observed.

    The receipt exists because the currency recorder used to derive the run's properties
    from the log TEXT: exit_code came from whether "BUILD SUCCESSFUL" appeared in it, and
    coldness came from a literal. Both are properties of the RUN, and a run can report them
    directly. What a downstream recorder must never do is infer them, so this writes them
    down at the only point where they are observable.
    """
    classpath = os.pathsep.join([toolchain["ant"], toolchain["launcher"]])
    coldness = make_cold(project_dir) if cold else observe_warm(project_dir)
    command = [
        toolchain["java"], "-cp", classpath, "org.apache.tools.ant.launch.Launcher",
        "-f", str(BUILD_FILE),
        f"-Dmps.home={toolchain['mps_home']}",
        f"-Dproject.dir={project_dir}",
        f"-Dbuild.heap={heap}",
        target,
    ]
    started = time.monotonic()
    # No shell, no inherited Ant, no ambient JAVA_HOME: the executable is the pinned JDK.
    result = subprocess.run(command, capture_output=True, text=True,
                            cwd=str(REPO_ROOT))
    elapsed = time.monotonic() - started
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with io.open(log_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(" ".join(command) + "\n\n")
        handle.write(result.stdout)
        handle.write(result.stderr)

    receipt = {
        "receipt_version": 1,
        "target": target,
        "exit_code": result.returncode,
        "elapsed_seconds": round(elapsed, 1),
        "cold": coldness,
        "mps_build": toolchain["mps_build"],
        "java": toolchain.get("java_version", ""),
        "model_tree_sha256": model_tree_hash(project_dir),
        # Binds this receipt to the log it describes. Without it a receipt from one run can
        # be presented alongside the log of another, which is the same dangling-reference
        # defect the retained-artifact rule exists to prevent, moved one level up.
        "log_sha256": hashlib.sha256(log_path.read_bytes()).hexdigest(),
        "log": log_path.name,
    }
    with io.open(receipt_path(log_path), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--log", type=Path,
                        default=REPO_ROOT / "build" / "work" / "headless-build.log")
    parser.add_argument("--heap", default="4g")
    parser.add_argument("--record", action="store_true",
                        help="write the build provenance record on success")
    parser.add_argument("--validate-only", action="store_true",
                        help="check the toolchain and inputs, build nothing")
    # MPS-MAT-009 F4: the make target had a controlled entry point carrying the pinned-build
    # and JDK validation, and the test target had none at all -- half of the MPS-MAT-008
    # acceptance wording was produced by an invocation that was not retained anywhere. The
    # target is a parameter so both halves run through the same validation rather than one
    # of them being reconstructed by hand.
    parser.add_argument("--target", default="make",
                        help="Ant target to invoke: make (generation) or test (model tests)")
    # MPS-MAT-009 F3: coldness must be observed by the runner, because nothing else is in a
    # position to observe it.
    parser.add_argument("--cold", action="store_true",
                        help="delete every generated directory under the project first, and "
                             "verify none remains, before building")
    parser.add_argument("--project-dir", type=Path, default=PROJECT_DIR,
                        help="the MPS project to build; defaults to this repository's")
    args = parser.parse_args()

    try:
        toolchain = validate_toolchain(mps_home())
    except ToolchainError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    toolchain["java_version"] = java_identity(Path(toolchain["java"]))
    try:
        tree_hash = model_tree_hash(args.project_dir)
    except ToolchainError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if args.validate_only:
        print(f"PASS: toolchain validated; MPS {toolchain['mps_build']} at "
              f"{toolchain['mps_home']}; {toolchain['java_version']}; "
              f"model tree {tree_hash[:16]}")
        return 0

    try:
        receipt = run_build(toolchain, args.log, args.heap, args.target,
                            args.project_dir, args.cold)
    except ToolchainError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    code, elapsed = receipt["exit_code"], receipt["elapsed_seconds"]
    cold_state = ("cold, " + str(receipt["cold"]["generated_directories_deleted"])
                  + " generated directories deleted"
                  if receipt["cold"]["requested"]
                  else "not cold-requested, "
                       + str(receipt["cold"]["generated_directories_before"])
                       + " generated directories present")
    print(f"receipt: target={receipt['target']}, exit_code={code}, {cold_state}; "
          f"{receipt_path(args.log).name}")
    if code != 0:
        print(f"ERROR: headless {args.target} failed with exit code {code}; see {args.log}",
              file=sys.stderr)
        return 1

    log_shown = args.log.resolve()
    try:
        log_shown = log_shown.relative_to(REPO_ROOT)
    except ValueError:
        pass
    print(f"PASS: headless build succeeded in {elapsed:.0f}s using MPS "
          f"{toolchain['mps_build']} outside the IDE; log at {log_shown}")

    if args.record:
        record = {
            "build_descriptor": str(BUILD_FILE.relative_to(REPO_ROOT)).replace("\\", "/"),
            "mps_build": toolchain["mps_build"],
            "java": toolchain["java_version"],
            "ant": "bundled with the pinned MPS installation, lib/ant",
            "host": platform.system(),
            "model_tree_sha256": tree_hash,
            "modules_built": module_list(),
            "verdict": "success",
            "covers": "generation, text generation and compilation of the nine languages",
            "does_not_cover": ("evaluation of the languages' own checking rules; proven by "
                               "a deliberate REA-C-002/REA-C-003 violation that the model "
                               "checker rejects and this build completes over"),
        }
        with io.open(PROVENANCE, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, indent=2, sort_keys=True) + "\n")
        print(f"recorded {PROVENANCE.relative_to(REPO_ROOT)}")
    return 0


def module_list() -> list[str]:
    """The modules the make target names, in the order it names them.

    Scoped to that one target on purpose. <module file="..."/> is also the shape of an
    entry inside the <repository> element the test target uses to supply support modules,
    and harvesting the whole document once silently reported nltps.proof three times --
    a provenance record that would have looked deliberate.
    """
    from xml.etree import ElementTree

    root = ElementTree.parse(BUILD_FILE).getroot()
    make = [t for t in root.iter("target") if t.get("name") == "make"]
    if len(make) != 1:
        raise ToolchainError(f"expected exactly one make target, found {len(make)}")
    names = []
    for element in make[0].iter("module"):
        value = element.get("file")
        if value:
            names.append(Path(value).name)
    return names


if __name__ == "__main__":
    sys.exit(main())
