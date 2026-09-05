"""matRad bridge: an independent photon dose engine and fluence optimiser.

Why this exists
---------------
pytps's own dose engine is a single-Gaussian pencil beam written for this
package. On its own there is nothing to check it against. matRad is an
established open research planning system with its own dose calculation,
its own optimiser and its own machine data, so planning the *same case* with
the *same objectives* through both gives an independent reference.

The comparison is meaningful because the objective functions are the same
function. matRad's squared dose objectives evaluate
``1/numel(dose) * sum(residual^2)`` scaled by a penalty, which is exactly the
form :mod:`pytps.objectives` uses. Given identical weights and dose levels the
two codes minimise the same quantity, so a difference in the result is a
difference in the dose engine, not in what was asked for.

What this bridge does not do
----------------------------
It does not make matRad's dose a reference standard: matRad's generic photon
machine is itself uncommissioned. It does not validate either engine, and
agreement between them is not evidence of correctness — two pencil-beam codes
can share an approximation. It performs no MLC sequencing or deliverability
check, so neither plan is deliverable.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable

import numpy as np

from ..case import PlanningCase
from ..objectives import Objective
from ..plan import (
    PlanRequest,
    PlanRequestError,
    PlanResult,
    default_objectives,
    evaluate_dose,
    plan_provenance,
    target_centroid,
)
from .jobs import JobError, JobFolder, job_summary, read_volume
from .matlab import MatlabRunner, find_library

PROVIDER = "matrad"
ADAPTER = "pytps_matrad_plan.m"
ADAPTER_FUNCTION = "pytps_matrad_plan"

#: pytps objective types that map onto an identical matRad objective.
OBJECTIVE_MAP = {
    "target_dose": "DoseObjectives.matRad_SquaredDeviation",
    "max_dose": "DoseObjectives.matRad_SquaredOverdosing",
    "min_dose": "DoseObjectives.matRad_SquaredUnderdosing",
}

#: How far matRad's own isocentre may sit from the requested one before the
#: run is rejected. matRad computes the target centre of gravity itself; a
#: larger disagreement means the two codes are not planning the same geometry.
DEFAULT_ISOCENTER_TOLERANCE_MM = 2.0


def adapter_dir() -> Path:
    """The directory holding this package's MATLAB adapters.

    The adapters live inside the package (``pytps/matlab``) so they travel with
    an install rather than only existing in a source checkout.
    """
    path = Path(__file__).resolve().parent.parent / "matlab"
    if not (path / ADAPTER).exists():
        raise JobError(
            f"MATLAB adapter {ADAPTER} not found under {path}. The adapters ship inside the "
            "package; a checkout missing them cannot run this bridge."
        )
    return path


@dataclass(frozen=True)
class MatRadSettings:
    """Where matRad and MATLAB live, and how long to wait."""

    matlab: str | Path | None = None
    library: str | Path | None = None
    timeout_s: int = 3600
    isocenter_tolerance_mm: float = DEFAULT_ISOCENTER_TOLERANCE_MM
    #: matRad's own optimiser iteration cap. Its default of 500 is often too
    #: low for a multi-beam fluence problem, and matRad then stops without
    #: converging, which this bridge refuses to import.
    max_iterations: int = 3000
    #: "optimize" runs matRad's fluence optimisation. "forward" skips it and
    #: returns the dose of a uniform open field, which isolates the dose engine.
    mode: str = "optimize"

    def __post_init__(self) -> None:
        if self.mode not in {"optimize", "forward"}:
            raise ValueError(f"mode must be 'optimize' or 'forward', got {self.mode!r}")
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")
        if self.isocenter_tolerance_mm < 0.0:
            raise ValueError("isocenter_tolerance_mm must be >= 0")


def check_objectives(objectives: tuple[Objective, ...]) -> None:
    """Refuse an objective set that matRad cannot express identically."""
    unsupported = sorted({item.kind() for item in objectives if item.kind() not in OBJECTIVE_MAP})
    if unsupported:
        raise PlanRequestError(
            f"matRad has no identical objective for {unsupported}. matRad's mean-dose objective "
            "uses a different difference function, so mapping it would make the comparison "
            f"invalid rather than merely approximate. Supported: {sorted(OBJECTIVE_MAP)}."
        )
    if not any(item.kind() == "target_dose" for item in objectives):
        raise PlanRequestError("matRad needs at least one target_dose objective to define the target")


def prepare_request(case: PlanningCase, request: PlanRequest) -> PlanRequest:
    """Fill in defaults and validate everything matRad will need."""
    known = {structure.name for structure in case.structures}
    if request.target not in known:
        raise PlanRequestError(
            f"target {request.target!r} is not a structure in case {case.case_id}. "
            f"Available: {', '.join(sorted(known)) or '(none)'}"
        )
    objectives = request.objectives
    if not objectives:
        objectives = default_objectives(case, request.target, request.prescription_gy)
        request = replace(request, objectives=objectives, objectives_were_defaulted=True)
    missing = sorted({item.structure for item in objectives} - known)
    if missing:
        raise PlanRequestError(f"objectives reference structures not in the case: {missing}")
    check_objectives(objectives)
    for name in {item.structure for item in objectives}:
        if not case.mask(name).any():
            raise PlanRequestError(f"objective structure {name!r} is empty in this case")
    if request.isocenter is None:
        request = replace(
            request,
            isocenter=tuple(round(value, 4) for value in target_centroid(case, request.target)),
        )
    return request


def export_job(
    case: PlanningCase,
    request: PlanRequest,
    root: str | Path,
    tools: dict[str, Any],
    isocenter_tolerance_mm: float = DEFAULT_ISOCENTER_TOLERANCE_MM,
    max_iterations: int = 3000,
    mode: str = "optimize",
) -> JobFolder:
    """Write a frozen, hashed matRad job folder."""
    job = JobFolder.create(root, PROVIDER)
    job.add_json(
        "source.json",
        {
            "caseID": case.case_id,
            "name": case.name,
            "syntheticOnly": bool(case.synthetic_only),
            "clinicalUsePermitted": False,
            "grid": case.grid.to_dict(),
            "structures": [
                {"label": int(item.label), "name": item.name, "color": list(item.color)}
                for item in case.structures
            ],
        },
    )
    job.add_volume("ct.f32", case.grid, case.ct_hu, "float32")
    job.add_volume("labels.i16", case.grid, case.labels, "int16")
    job.add_json(
        "request.json",
        {
            "target": request.target,
            "prescriptionGy": float(request.prescription_gy),
            "fractions": int(request.fractions),
            "doseConvention": "total-course physical Gy",
            "gantryAnglesDeg": [float(angle) for angle in request.gantry_angles],
            "bixelWidthMM": float(request.bixel_width_mm),
            "isocenterMM": [float(value) for value in (request.isocenter or (0.0, 0.0, 0.0))],
            "isocenterToleranceMM": float(isocenter_tolerance_mm),
            "maxIterations": int(max_iterations),
            "mode": mode,
            "objectives": [item.to_dict() for item in request.objectives],
            "requestDigest": request.digest(),
        },
    )
    job.add_adapter(adapter_dir() / ADAPTER)
    for helper in ("pytps_filehash.m", "pytps_readvolume.m", "pytps_writejson.m"):
        job.add_adapter(adapter_dir() / helper)
    job.freeze(
        tools=tools,
        notes={
            "doseConvention": "matRad returns per-fraction dose; the adapter multiplies by the "
            "fraction count exactly once and emits total-course physical Gy.",
            "objectiveEquivalence": "matRad squared objectives use the same 1/N sum-of-squares "
            "normalisation as pytps, so identical weights describe identical functions.",
            "boundary": "matRad's Generic photon machine is uncommissioned. This is not a "
            "reference dose and confers no approval.",
        },
    )
    return job


def import_result(case: PlanningCase, job: JobFolder) -> tuple[np.ndarray, dict[str, Any]]:
    """Load the dose matRad produced, after checking it binds to this job."""
    job.check_inputs_unchanged()
    record = job.record()
    bindings = {entry["file"]: entry["sha256"] for entry in record["inputs"]}
    payload = job.load_result(
        "result.json",
        {
            "jobID": record["jobID"],
            "sourceDigest": bindings["source.json"],
            "requestDigest": bindings["request.json"],
        },
    )
    basis = payload.get("doseBasis")
    if basis not in {"total-course-physical-Gy", "relative-uniform-fluence"}:
        raise JobError(
            f"result.json declares an unknown dose basis {basis!r}; refusing to import a dose "
            "whose units are not stated."
        )
    dose = read_volume(
        job.file(payload["doseFile"]), case.grid, "float32", expected_digest=payload["doseDigest"]
    )
    if not np.all(np.isfinite(dose)) or float(dose.min()) < 0.0 or float(dose.max()) <= 0.0:
        raise JobError("the imported dose is not a finite, non-negative, non-zero distribution")
    if not payload.get("evidence", {}).get("optimizerConverged", False):
        raise JobError("matRad reported a non-converged optimisation; the result is not importable")
    if basis == "total-course-physical-Gy" and payload.get("evidence", {}).get("mode") == "forward":
        raise JobError("a forward-dose run may not claim total-course Gy; its scale is arbitrary")
    return dose, payload


def submit(
    case: PlanningCase,
    request: PlanRequest,
    jobs_root: str | Path,
    settings: MatRadSettings,
    progress: Callable[[str], None] | None = None,
) -> tuple[np.ndarray, dict[str, Any], JobFolder, dict[str, Any]]:
    """Freeze a job, run matRad, and import the dose it produced.

    Shared by the planning and forward-dose entry points so both go through the
    same freezing, hashing and result-binding path.
    """
    def announce(message: str) -> None:
        if progress is not None:
            progress(message)

    runner = MatlabRunner(settings.matlab, timeout_s=settings.timeout_s)
    library = find_library("matrad", settings.library)
    announce(f"matlab: {runner.matlab}")
    announce(f"matRad: {library} (mode: {settings.mode})")

    job = export_job(
        case,
        request,
        jobs_root,
        tools={
            "matlab": str(runner.matlab),
            "matRad": str(library),
            "adapter": ADAPTER,
            "timeoutSeconds": settings.timeout_s,
            "maxIterations": settings.max_iterations,
            "mode": settings.mode,
        },
        isocenter_tolerance_mm=settings.isocenter_tolerance_mm,
        max_iterations=settings.max_iterations,
        mode=settings.mode,
    )
    announce(f"job folder: {job.path}")
    announce("running matRad in a batch MATLAB process (this takes minutes)")

    matlab_result = runner.run_function(
        adapter_dir=job.path,
        function=ADAPTER_FUNCTION,
        arguments=[job.path, library],
        working_dir=job.path,
        log_path=job.file("matlab.log"),
    )
    job.file("exit-code.txt").write_text(f"{matlab_result.exit_code}\n", encoding="utf-8")
    announce(f"MATLAB exit {matlab_result.exit_code} after {matlab_result.duration_s:.0f}s")
    if not matlab_result.ok:
        log = job.file("matlab.log").read_text(encoding="utf-8")
        tail = "\n".join(log.splitlines()[-15:])
        hint = ""
        if "exceeded the iteration limit" in log or "pytps:converged" in log:
            hint = (
                f"\nmatRad stopped at its {settings.max_iterations} iteration limit without "
                "converging, so no dose was emitted. Raise MatRadSettings.max_iterations "
                "(--matrad-iterations) if the objective was still improving."
            )
        raise JobError(
            f"matRad did not complete (MATLAB exit {matlab_result.exit_code}"
            f"{', timed out' if matlab_result.timed_out else ''}). "
            f"Job retained at {job.path}.{hint}\nLast log lines:\n{tail}"
        )

    dose_volume, payload = import_result(case, job)
    evidence = payload.get("evidence", {})
    external = job_summary(
        job.record(),
        matlab_result.to_dict(),
        extra=(
            ("provider", PROVIDER),
            ("evidence", evidence),
            ("doseBasis", payload["doseBasis"]),
            ("doseDigest", payload["doseDigest"]),
            ("optimizerConverged", bool(evidence.get("optimizerConverged", False))),
        ),
    )
    return dose_volume, payload, job, external


def run_matrad_forward(
    case: PlanningCase,
    request: PlanRequest,
    jobs_root: str | Path,
    settings: MatRadSettings | None = None,
    progress: Callable[[str], None] | None = None,
) -> tuple[np.ndarray, dict[str, Any], JobFolder]:
    """Dose of a uniform open field, on an arbitrary scale.

    Nothing is optimised, so comparing this against the same open field
    computed by pytps isolates the two dose engines from the two optimisers.
    """
    settings = replace(settings or MatRadSettings(), mode="forward")
    request = prepare_request(case, request)
    dose_volume, _, job, external = submit(case, request, jobs_root, settings, progress)
    return dose_volume, external, job


def run_matrad_plan(
    case: PlanningCase,
    request: PlanRequest,
    jobs_root: str | Path,
    settings: MatRadSettings | None = None,
    case_path: str | Path | None = None,
    progress: Callable[[str], None] | None = None,
) -> tuple[PlanResult, JobFolder]:
    """Plan a case with matRad and return it as an ordinary pytps plan result."""
    settings = settings or MatRadSettings()
    if settings.mode != "optimize":
        raise PlanRequestError("run_matrad_plan needs mode 'optimize'; use run_matrad_forward instead")
    request = prepare_request(case, request)
    dose_volume, payload, job, external = submit(case, request, jobs_root, settings, progress)

    dose = dose_volume.reshape(-1).astype(np.float32)
    dvhs, warnings = evaluate_dose(case, request, dose)
    warnings.append(
        "Dose computed by matRad through a pytps bridge. matRad's Generic photon machine is "
        "uncommissioned; this is not a reference dose and carries no approval from either project."
    )
    if request.objectives_were_defaulted:
        warnings.append(
            "No objectives were supplied; a placeholder set was generated. "
            "Placeholder objectives are not clinical constraints."
        )

    provenance = plan_provenance(case, request, case_path)
    provenance["inputs"]["externalProvider"] = PROVIDER
    provenance["inputs"]["externalJob"] = job.path.name

    weights = np.asarray(payload.get("weights", []), dtype=np.float32).reshape(-1)
    result = PlanResult(
        case=case,
        request=request,
        beams=[],
        dose=dose,
        dvhs=dvhs,
        provenance=provenance,
        warnings=warnings,
        provider=PROVIDER,
        external=external,
        weights=weights,
    )
    return result, job


def compare_engines(
    case: PlanningCase,
    request: PlanRequest,
    jobs_root: str | Path,
    settings: MatRadSettings | None = None,
    gamma_criteria: tuple[float, float] | None = (3.0, 3.0),
    progress: Callable[[str], None] | None = None,
) -> tuple[Any, JobFolder]:
    """Compare this package's dose engine against matRad's, optimisers excluded.

    Both codes compute the dose of the *same* uniform open field on the same
    case, so nothing is optimised and no fluence choice enters. Neither dose has
    an absolute calibration, so both are normalised to their own mean dose in a
    small sphere at the isocentre before they are compared. What remains is the
    difference between two pencil-beam implementations.
    """
    from ..compare import compare_doses, normalize_to_isocenter
    from ..plan import forward_dose

    settings = replace(settings or MatRadSettings(), mode="forward")
    request = prepare_request(case, request)

    matrad_volume, external, job = run_matrad_forward(case, request, jobs_root, settings, progress)
    if progress is not None:
        progress("computing the same open field with the pytps engine")
    own_dose, beams = forward_dose(case, request)

    isocenter = request.isocenter or (0.0, 0.0, 0.0)
    reference = normalize_to_isocenter(case.grid, own_dose, isocenter)
    evaluation = normalize_to_isocenter(case.grid, matrad_volume, isocenter)

    comparison = compare_doses(
        case,
        reference,
        evaluation,
        reference_label="pytps-pencilbeam",
        evaluation_label=PROVIDER,
        request=None,
        gamma_criteria=gamma_criteria,
        kind="engines",
    )
    comparison.warnings.append(
        "Uniform open field, both doses normalised to the mean in a 10 mm sphere at the "
        "isocentre. The bixel grids are each code's own, so a residual difference at the field "
        "edge reflects field shaping as well as the kernel."
    )
    comparison.warnings.append(
        f"pytps used {sum(beam.bixels.count for beam in beams)} bixels; matRad used "
        f"{external.get('evidence', {}).get('bixelCount', 'an unrecorded number')}."
    )
    return comparison, job
