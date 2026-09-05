"""Locating and running a batch MATLAB process.

The bridge never embeds a machine-specific path in source. A MATLAB, matRad or
CERR location comes from an explicit argument, then an environment variable,
then discovery relative to the current user's home and the standard application
directory, in that order. Whatever is found is recorded in the job's provenance
so a result can be traced to the installation that produced it.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

#: Environment variables consulted, in order, before discovery.
MATLAB_ENV = "PYTPS_MATLAB"
MATRAD_ENV = "PYTPS_MATRAD"
CERR_ENV = "PYTPS_CERR"

DEFAULT_TIMEOUT_S = 3600


class MatlabError(RuntimeError):
    """Raised when MATLAB cannot be located, started, or finished badly."""


def _candidate_matlab_paths() -> list[Path]:
    """Plausible MATLAB launchers, newest-looking first."""
    candidates: list[Path] = []
    which = shutil.which("matlab")
    if which:
        candidates.append(Path(which))
    applications = Path("/Applications")
    if applications.is_dir():
        for app in sorted(applications.glob("MATLAB_R*.app"), reverse=True):
            candidates.append(app / "bin" / "matlab")
    for root in (Path("/usr/local/MATLAB"), Path("/opt/MATLAB")):
        if root.is_dir():
            for release in sorted(root.glob("R*"), reverse=True):
                candidates.append(release / "bin" / "matlab")
    return candidates


def find_matlab(explicit: str | Path | None = None) -> Path:
    """Resolve the MATLAB launcher, or explain what to set."""
    if explicit:
        path = Path(explicit).expanduser()
        if not path.exists():
            raise MatlabError(f"MATLAB launcher not found at {path}")
        return path.resolve()
    from_env = os.environ.get(MATLAB_ENV)
    if from_env:
        path = Path(from_env).expanduser()
        if not path.exists():
            raise MatlabError(f"{MATLAB_ENV} points at {path}, which does not exist")
        return path.resolve()
    for candidate in _candidate_matlab_paths():
        if candidate.exists():
            return candidate.resolve()
    raise MatlabError(
        "no MATLAB installation was found. Pass --matlab /path/to/bin/matlab, "
        f"or set {MATLAB_ENV}. Both matRad and CERR are MATLAB codes; there is no "
        "MATLAB-free path for either bridge."
    )


def _candidate_library_paths(name: str, markers: Sequence[str]) -> list[Path]:
    """Plausible checkout locations for an external MATLAB library."""
    home = Path.home()
    roots = [
        home / "Documents",
        home / "Documents" / "GitHub",
        home / "GitHub",
        home / "src",
        home,
    ]
    found: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for depth in ("", "*/", "*/*/"):
            for candidate in sorted(root.glob(f"{depth}{name}*")):
                if candidate.is_dir() and all((candidate / marker).exists() for marker in markers):
                    found.append(candidate)
    return found


def find_library(kind: str, explicit: str | Path | None = None) -> Path:
    """Resolve a matRad or CERR checkout.

    ``kind`` is ``"matrad"`` or ``"cerr"``. Discovery requires a marker file, so
    an unrelated directory whose name happens to match is not accepted.
    """
    settings = {
        "matrad": (MATRAD_ENV, "matRad", ("matRad_rc.m",), "https://github.com/e0404/matRad"),
        "cerr": (CERR_ENV, "CERR", ("getCERRPath.m",), "https://github.com/cerr/CERR"),
    }
    if kind not in settings:
        raise MatlabError(f"unknown external library {kind!r}")
    env_name, glob_name, markers, url = settings[kind]

    if explicit:
        path = Path(explicit).expanduser()
    elif os.environ.get(env_name):
        path = Path(os.environ[env_name]).expanduser()
    else:
        candidates = _candidate_library_paths(glob_name, markers)
        if not candidates:
            raise MatlabError(
                f"no {kind} installation was found. Pass --{kind} /path/to/checkout or set "
                f"{env_name}. This package does not bundle {kind}; install it from {url}."
            )
        path = candidates[0]
    if not path.is_dir():
        raise MatlabError(f"{kind} path {path} is not a directory")
    missing = [marker for marker in markers if not (path / marker).exists()]
    if missing:
        raise MatlabError(
            f"{path} does not look like a {kind} checkout: {missing} not found. "
            f"Point --{kind} at the repository root."
        )
    return path.resolve()


@dataclass
class MatlabResult:
    """What a batch MATLAB process did."""

    exit_code: int
    duration_s: float
    log_path: Path
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    def to_dict(self) -> dict[str, Any]:
        return {
            "exitCode": self.exit_code,
            "durationSeconds": round(self.duration_s, 2),
            "timedOut": self.timed_out,
            "log": self.log_path.name,
        }


def quote_for_matlab(value: str | Path) -> str:
    """Single-quote a path for a MATLAB command, refusing what cannot be quoted.

    MATLAB escapes a single quote by doubling it, but a path containing one is
    far more likely to be a mistake than an intent, and this string is being
    handed to a process launcher. Refuse it instead.
    """
    text = str(value)
    if "'" in text or "\n" in text:
        raise MatlabError(f"path contains a quote or newline and cannot be passed to MATLAB: {text!r}")
    return f"'{text}'"


class MatlabRunner:
    """Runs one adapter function in a batch MATLAB process."""

    def __init__(self, matlab: str | Path | None = None, timeout_s: int = DEFAULT_TIMEOUT_S) -> None:
        self.matlab = find_matlab(matlab)
        if timeout_s <= 0:
            raise MatlabError("timeout must be > 0 seconds")
        self.timeout_s = int(timeout_s)

    def version(self) -> str:
        """Ask MATLAB what it is. Used once, for the provenance record."""
        result = subprocess.run(
            [str(self.matlab), "-batch", "fprintf('%s|%s', version, computer);"],
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
        if result.returncode != 0:
            raise MatlabError(f"MATLAB did not start (exit {result.returncode}): {result.stderr.strip()[:400]}")
        return result.stdout.strip().splitlines()[-1] if result.stdout.strip() else "unknown"

    def run_function(
        self,
        adapter_dir: Path,
        function: str,
        arguments: Sequence[str | Path],
        working_dir: Path,
        log_path: Path,
    ) -> MatlabResult:
        """Call ``function(arguments...)`` with ``adapter_dir`` on the path."""
        if not function.isidentifier():
            raise MatlabError(f"adapter function name is not a valid identifier: {function!r}")
        # Absolute paths only. MATLAB starts in the job folder, so a relative
        # path would resolve against the job folder rather than the caller's
        # working directory and silently address the wrong place.
        call = ", ".join(
            quote_for_matlab(Path(argument).resolve() if isinstance(argument, Path) else argument)
            for argument in arguments
        )
        command = (
            f"addpath({quote_for_matlab(Path(adapter_dir).resolve())}); "
            f"{function}({call});"
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        started = time.perf_counter()
        timed_out = False
        try:
            completed = subprocess.run(
                [str(self.matlab), "-batch", command],
                cwd=str(Path(working_dir).resolve()),
                capture_output=True,
                text=True,
                timeout=self.timeout_s,
                check=False,
            )
            output = completed.stdout + ("\n" + completed.stderr if completed.stderr else "")
            exit_code = completed.returncode
        except subprocess.TimeoutExpired as expired:
            timed_out = True
            exit_code = 124
            output = (expired.stdout or "") + "\n" + (expired.stderr or "")
            if isinstance(output, bytes):  # pragma: no cover - platform dependent
                output = output.decode("utf-8", errors="replace")
            output += f"\n[pytps] MATLAB exceeded the {self.timeout_s}s timeout and was terminated.\n"
        duration = time.perf_counter() - started
        header = (
            f"[pytps] matlab: {self.matlab}\n"
            f"[pytps] command: {command}\n"
            f"[pytps] cwd: {working_dir}\n"
        )
        log_path.write_text(header + output, encoding="utf-8", errors="replace")
        return MatlabResult(exit_code=exit_code, duration_s=duration, log_path=log_path, timed_out=timed_out)
