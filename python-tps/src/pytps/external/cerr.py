"""CERR bridge: independent dose-volume analysis and a geometry round trip.

Why this exists
---------------
Two different questions can be asked of a dose distribution, and they fail in
different ways.

*Did the geometry survive?* A planning system that quietly transposes an axis,
flips a slice order, or loses a half-voxel offset will still produce
plausible-looking DVHs. The adapter therefore rebuilds this package's CT,
labels and dose inside a CERR ``planC`` - a completely different coordinate
convention, ``[L, -P, -S]`` in centimetres with reversed slices - and then
reads every axis and every voxel back out through CERR's own accessors and
compares them to what was sent. Nothing is analysed unless that round trip is
exact.

*Is the dose-volume measurement right?* CERR samples structures and builds
histograms with its own long-standing code. Running it over the same dose gives
an independent measurement of the same quantities :mod:`pytps.dvh` computes.

Reconciling the definitions
---------------------------
An apparent disagreement is usually a definition mismatch, not a defect. CERR's
``doseHist`` bins; this package interpolates a cumulative histogram. So the
comparison recomputes this package's metrics using CERR's own nearest-rank
definition and reports that alongside the interpolated value, and it treats
only the like-for-like pair as a discrepancy.

No patient DICOM is read, no CERR source is copied, and the CERR checkout is
not written to. CERR analysis certifies nothing about a plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np

from ..case import PlanningCase
from ..dvh import nearest_rank_dose
from ..plan import structure_voxels
from .jobs import JobError, JobFolder, job_summary
from .matlab import MatlabRunner, find_library

PROVIDER = "cerr"
ADAPTER = "pytps_cerr_analyze.m"
ADAPTER_FUNCTION = "pytps_cerr_analyze"

DEFAULT_BIN_WIDTH_GY = 0.1

#: Volume fractions compared against CERR, using CERR's nearest-rank definition.
COMPARED_FRACTIONS = ((0.02, "D2"), (0.50, "D50"), (0.95, "D95"), (0.98, "D98"))

#: Multiple of float32 epsilon allowed on a sampled dose value. The dose makes
#: two float32 round trips through the job folder and MATLAB's double
#: arithmetic, so the tolerable difference scales with the dose magnitude: an
#: absolute threshold would pass at 60 Gy and cry geometry fault at 80 Gy.
SAMPLING_EPSILON_MULTIPLE = 16.0


def sampling_tolerance_gy_for(dose: np.ndarray) -> float:
    """Largest sampled-dose difference explainable by float32 round-tripping."""
    peak = float(np.abs(np.asarray(dose, dtype=np.float32)).max())
    return float(SAMPLING_EPSILON_MULTIPLE * np.finfo(np.float32).eps * max(peak, 1.0))


def adapter_dir() -> Path:
    path = Path(__file__).resolve().parent.parent / "matlab"
    if not (path / ADAPTER).exists():
        raise JobError(
            f"MATLAB adapter {ADAPTER} not found under {path}. The adapters ship inside the "
            "package; a checkout missing them cannot run this bridge."
        )
    return path


@dataclass(frozen=True)
class CerrSettings:
    """Where CERR and MATLAB live, and how finely to bin."""

    matlab: str | Path | None = None
    library: str | Path | None = None
    timeout_s: int = 3600
    bin_width_gy: float = DEFAULT_BIN_WIDTH_GY
    #: Largest tolerated disagreement, in Gy, on a like-for-like metric before
    #: the comparison is reported as a discrepancy.
    tolerance_gy: float = 1e-3

    def __post_init__(self) -> None:
        if self.bin_width_gy <= 0.0:
            raise ValueError("bin_width_gy must be > 0")
        if self.tolerance_gy < 0.0:
            raise ValueError("tolerance_gy must be >= 0")


@dataclass
class StructureComparison:
    """One structure, measured by both packages."""

    structure: str
    voxels_pytps: int
    voxels_cerr: int
    max_sample_difference_gy: float
    metrics: dict[str, dict[str, float]] = field(default_factory=dict)

    @property
    def worst_difference_gy(self) -> float:
        if not self.metrics:
            return 0.0
        return max(abs(row["difference"]) for row in self.metrics.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "structure": self.structure,
            "voxelsPytps": self.voxels_pytps,
            "voxelsCERR": self.voxels_cerr,
            "maxSampleDifferenceGy": round(self.max_sample_difference_gy, 9),
            "metrics": {
                name: {key: round(float(value), 6) for key, value in row.items()}
                for name, row in self.metrics.items()
            },
            "worstDifferenceGy": round(self.worst_difference_gy, 6),
        }


@dataclass
class CerrAnalysis:
    """What the CERR run established."""

    comparisons: list[StructureComparison]
    evidence: dict[str, Any]
    external: dict[str, Any]
    tolerance_gy: float
    #: Threshold below which a sampled-dose difference is float32 noise.
    sampling_tolerance_gy: float = 1e-5
    warnings: list[str] = field(default_factory=list)

    @property
    def sampling_is_voxel_exact(self) -> bool:
        """Whether CERR sampled this package's dose values to float32 precision."""
        return all(
            item.max_sample_difference_gy <= self.sampling_tolerance_gy for item in self.comparisons
        )

    @property
    def agrees(self) -> bool:
        return self.sampling_is_voxel_exact and all(
            item.worst_difference_gy <= self.tolerance_gy for item in self.comparisons
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": PROVIDER,
            "toleranceGy": self.tolerance_gy,
            "samplingToleranceGy": self.sampling_tolerance_gy,
            "samplingIsVoxelExact": self.sampling_is_voxel_exact,
            "agrees": self.agrees,
            "structures": [item.to_dict() for item in self.comparisons],
            "evidence": self.evidence,
            "external": self.external,
            "warnings": self.warnings,
            "note": (
                "An independent dose-volume measurement and a geometry round trip. "
                "Not an approval, and not evidence that either dose is correct."
            ),
        }


def export_job(
    case: PlanningCase,
    dose: np.ndarray,
    root: str | Path,
    tools: dict[str, Any],
    bin_width_gy: float = DEFAULT_BIN_WIDTH_GY,
) -> JobFolder:
    """Write a frozen, hashed CERR job folder."""
    dose_volume = np.asarray(dose, dtype=np.float32).reshape(case.grid.dimensions)
    if not np.all(np.isfinite(dose_volume)) or float(dose_volume.min()) < 0.0:
        raise JobError("dose must be finite and non-negative before it can be analysed")
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
    job.add_volume("dose.f32", case.grid, dose_volume, "float32")
    job.add_json(
        "request.json",
        {
            "analysis": "dose-volume histogram and geometry round trip",
            "binWidthGy": float(bin_width_gy),
            "doseUnits": "total-course physical Gy",
            "dxDefinition": "nearest rank ceil(fraction * N) on descending samples",
        },
    )
    job.add_adapter(adapter_dir() / ADAPTER)
    for helper in ("pytps_filehash.m", "pytps_readvolume.m", "pytps_writejson.m"):
        job.add_adapter(adapter_dir() / helper)
    job.freeze(
        tools=tools,
        notes={
            "geometry": "LPS mm is converted to CERR [L,-P,-S] cm with reversed slices; the "
            "adapter reads every axis and voxel back and compares before analysing.",
            "structures": "Label masks are rasterised exactly as row runs. No polygon is "
            "reconstructed, so CERR analyses the same voxels pytps does.",
            "boundary": "Analysis only. CERR does not recalculate dose here and certifies nothing.",
        },
    )
    return job


def import_report(job: JobFolder) -> dict[str, Any]:
    """Load CERR's report after checking it binds to this job."""
    job.check_inputs_unchanged()
    record = job.record()
    bindings = {entry["file"]: entry["sha256"] for entry in record["inputs"]}
    return job.load_result(
        "report.json",
        {
            "jobID": record["jobID"],
            "sourceDigest": bindings["source.json"],
            "requestDigest": bindings["request.json"],
            "doseDigest": bindings["dose.f32"],
        },
    )


def reconcile(
    case: PlanningCase,
    dose: np.ndarray,
    records: Sequence[dict[str, Any]],
    tolerance_gy: float,
    sampling_tolerance_gy: float | None = None,
) -> tuple[list[StructureComparison], list[str]]:
    """Compare CERR's measurements against this package's, definition by definition."""
    flat = np.asarray(dose, dtype=np.float32).reshape(-1)
    if sampling_tolerance_gy is None:
        sampling_tolerance_gy = sampling_tolerance_gy_for(flat)
    voxels = structure_voxels(case)
    comparisons: list[StructureComparison] = []
    warnings: list[str] = []

    for record in records:
        name = str(record["name"])
        indices = voxels.get(name)
        if indices is None:
            warnings.append(f"CERR reported structure {name!r}, which this case no longer defines")
            continue
        values = flat[indices]
        comparison = StructureComparison(
            structure=name,
            voxels_pytps=int(indices.size),
            voxels_cerr=int(record["sampleCount"]),
            max_sample_difference_gy=float(record.get("maxSampleDifferenceGy", float("nan"))),
        )
        if comparison.voxels_cerr != comparison.voxels_pytps:
            warnings.append(
                f"{name}: CERR sampled {comparison.voxels_cerr} voxels, this case has "
                f"{comparison.voxels_pytps}. The comparison for this structure is not like-for-like."
            )

        pytps_mean = float(values.mean())
        cerr_mean = float(record["meanGy"])
        comparison.metrics["mean"] = {
            "pytps": pytps_mean,
            "cerr": cerr_mean,
            "difference": pytps_mean - cerr_mean,
        }
        for key, label in ((("maxGy"), "max"), (("minGy"), "min")):
            cerr_value = float(record[key])
            own = float(values.max() if label == "max" else values.min())
            comparison.metrics[label] = {
                "pytps": own,
                "cerr": cerr_value,
                "difference": own - cerr_value,
            }
        for fraction, label in COMPARED_FRACTIONS:
            cerr_key = f"d{round(fraction * 100):02d}Gy"
            if cerr_key not in record:
                continue
            own = nearest_rank_dose(values, fraction)
            cerr_value = float(record[cerr_key])
            comparison.metrics[label] = {
                "pytps": own,
                "cerr": cerr_value,
                "difference": own - cerr_value,
            }
        comparisons.append(comparison)

        if comparison.max_sample_difference_gy > sampling_tolerance_gy:
            warnings.append(
                f"{name}: CERR's sampled dose differs from this package's by up to "
                f"{comparison.max_sample_difference_gy:.4g} Gy, above the "
                f"{sampling_tolerance_gy:.3g} Gy explainable by float32 round-tripping. The two "
                "are not reading the same voxels; investigate the geometry before trusting any "
                "metric."
            )
        elif comparison.worst_difference_gy > tolerance_gy:
            warnings.append(
                f"{name}: CERR samples the identical voxels, but a dose-volume metric differs by "
                f"{comparison.worst_difference_gy:.4g} Gy. That is a metric-definition difference, "
                "not a dose difference."
            )
    return comparisons, warnings


def run_cerr_analysis(
    case: PlanningCase,
    dose: np.ndarray,
    jobs_root: str | Path,
    settings: CerrSettings | None = None,
    progress: Callable[[str], None] | None = None,
) -> tuple[CerrAnalysis, JobFolder]:
    """Analyse a dose with CERR and reconcile it against this package's metrics."""
    settings = settings or CerrSettings()

    def announce(message: str) -> None:
        if progress is not None:
            progress(message)

    runner = MatlabRunner(settings.matlab, timeout_s=settings.timeout_s)
    library = find_library("cerr", settings.library)
    announce(f"matlab: {runner.matlab}")
    announce(f"CERR: {library}")

    job = export_job(
        case,
        dose,
        jobs_root,
        tools={
            "matlab": str(runner.matlab),
            "CERR": str(library),
            "adapter": ADAPTER,
            "timeoutSeconds": settings.timeout_s,
        },
        bin_width_gy=settings.bin_width_gy,
    )
    announce(f"job folder: {job.path}")
    announce("running CERR in a batch MATLAB process")

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
        tail = "\n".join(job.file("matlab.log").read_text(encoding="utf-8").splitlines()[-15:])
        raise JobError(
            f"CERR analysis did not complete (MATLAB exit {matlab_result.exit_code}"
            f"{', timed out' if matlab_result.timed_out else ''}). "
            f"Job retained at {job.path}.\nLast log lines:\n{tail}"
        )

    payload = import_report(job)
    records = payload.get("records") or []
    if not records:
        raise JobError("CERR returned no structure records")
    sampling_tolerance = sampling_tolerance_gy_for(dose)
    comparisons, warnings = reconcile(
        case, dose, records, settings.tolerance_gy, sampling_tolerance
    )
    external = job_summary(
        job.record(),
        matlab_result.to_dict(),
        extra=(("provider", PROVIDER), ("evidence", payload.get("evidence", {}))),
    )
    return (
        CerrAnalysis(
            comparisons=comparisons,
            evidence=payload.get("evidence", {}),
            external=external,
            tolerance_gy=settings.tolerance_gy,
            sampling_tolerance_gy=sampling_tolerance,
            warnings=warnings,
        ),
        job,
    )
