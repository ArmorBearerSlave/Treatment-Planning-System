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
    """
    digest = hashlib.sha256()
    for path in controlled_files(project_dir):
        digest.update(str(path.relative_to(project_dir)).replace("\\", "/").encode())
        digest.update(b"\0")
        with io.open(path, "rb") as handle:
            digest.update(hashlib.sha256(handle.read()).digest())
    return digest.hexdigest()


def run_build(toolchain: dict, log_path: Path, heap: str) -> tuple[int, float]:
    classpath = os.pathsep.join([toolchain["ant"], toolchain["launcher"]])
    command = [
        toolchain["java"], "-cp", classpath, "org.apache.tools.ant.launch.Launcher",
        "-f", str(BUILD_FILE),
        f"-Dmps.home={toolchain['mps_home']}",
        f"-Dproject.dir={PROJECT_DIR}",
        f"-Dbuild.heap={heap}",
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
    return result.returncode, elapsed


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
    args = parser.parse_args()

    try:
        toolchain = validate_toolchain(mps_home())
    except ToolchainError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    toolchain["java_version"] = java_identity(Path(toolchain["java"]))
    tree_hash = model_tree_hash(PROJECT_DIR)

    if args.validate_only:
        print(f"PASS: toolchain validated; MPS {toolchain['mps_build']} at "
              f"{toolchain['mps_home']}; {toolchain['java_version']}; "
              f"model tree {tree_hash[:16]}")
        return 0

    code, elapsed = run_build(toolchain, args.log, args.heap)
    if code != 0:
        print(f"ERROR: headless build failed with exit code {code}; see {args.log}",
              file=sys.stderr)
        return 1

    print(f"PASS: headless build succeeded in {elapsed:.0f}s using MPS "
          f"{toolchain['mps_build']} outside the IDE; log at "
          f"{args.log.relative_to(REPO_ROOT)}")

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
    """The modules the build descriptor names, in the order it names them."""
    from xml.etree import ElementTree

    root = ElementTree.parse(BUILD_FILE).getroot()
    names = []
    for element in root.iter("module"):
        value = element.get("file")
        if value:
            names.append(Path(value).name)
    return names


if __name__ == "__main__":
    sys.exit(main())
