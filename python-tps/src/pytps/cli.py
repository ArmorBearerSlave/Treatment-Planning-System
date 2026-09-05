"""Command-line interface.

    python -m pytps phantom  --out work/case.npz
    python -m pytps inspect  work/case.npz
    python -m pytps template --out work/request.json
    python -m pytps plan     --case work/case.npz --request work/request.json --out work/plan
    python -m pytps report   work/plan
    python -m pytps verify   work/plan --case work/case.npz
    python -m pytps selftest

External research codes, each a separately installed MATLAB dependency:

    python -m pytps tools
    python -m pytps matrad  --case work/case.npz --request work/request.json --out work/plan-matrad
    python -m pytps cerr    --plan work/plan --case work/case.npz
    python -m pytps compare --reference work/plan --evaluation work/plan-matrad --case work/case.npz
    python -m pytps engines --case work/case.npz --out work/engines.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from . import ENGINE_ID, INTENDED_USE, __version__
from .case import PlanningCase
from .dose import PencilBeamSettings
from .phantom import build_phantom_case
from .plan import PlanRequest, PlanResult, default_objectives, run_plan
from .provenance import sha256_array, sha256_file, sha256_json


def _progress(verbose: bool):
    if not verbose:
        return None

    start = time.perf_counter()

    def emit(message: str) -> None:
        print(f"[{time.perf_counter() - start:6.2f}s] {message}", file=sys.stderr)

    return emit


def _write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def command_phantom(args: argparse.Namespace) -> int:
    case = build_phantom_case(
        case_id=args.case_id,
        dimensions=tuple(args.dimensions),
        spacing=tuple(args.spacing),
        seed=args.seed,
        noise_hu=args.noise,
    )
    path = case.save_npz(args.out)
    print(f"wrote {path} ({path.stat().st_size / 1e6:.2f} MB)")
    print(json.dumps(case.summary(), indent=2))
    return 0


def command_inspect(args: argparse.Namespace) -> int:
    case = PlanningCase.load(args.case)
    summary = case.summary()
    summary["ctDigest"] = sha256_array(case.ct_hu)
    summary["labelDigest"] = sha256_array(case.labels)
    summary["ctHURange"] = [round(float(case.ct_hu.min()), 2), round(float(case.ct_hu.max()), 2)]
    summary["provenance"] = case.provenance
    print(json.dumps(summary, indent=2))
    return 0


def command_template(args: argparse.Namespace) -> int:
    case = PlanningCase.load(args.case) if args.case else None
    target = args.target
    prescription = float(args.prescription)
    if case is not None:
        objectives = [item.to_dict() for item in default_objectives(case, target, prescription)]
    else:
        objectives = [
            {"type": "target_dose", "structure": target, "doseGy": prescription, "weight": 100.0},
            {"type": "max_dose", "structure": "BLADDER", "doseGy": prescription * 0.70, "weight": 20.0},
            {"type": "max_dose", "structure": "RECTUM", "doseGy": prescription * 0.65, "weight": 20.0},
        ]
    payload = {
        "requestVersion": 1,
        "planLabel": "research plan",
        "_notice": INTENDED_USE,
        "_doseConvention": "All doses are total-course physical Gy.",
        "_objectiveNotice": (
            "The objective doses below are placeholders for a synthetic phantom. "
            "They are not protocol constraints and must be reviewed before any study use."
        ),
        "target": target,
        "prescriptionGy": prescription,
        "fractions": int(args.fractions),
        "gantryAnglesDeg": [float(angle) for angle in args.angles],
        "bixelWidthMM": float(args.bixel_width),
        "fieldMarginMM": float(args.margin),
        "sadMM": 1000.0,
        "isocenterMM": None,
        "objectives": objectives,
        "kernelOverrides": {},
        "optimizerOverrides": {},
    }
    path = _write_json(Path(args.out), payload)
    print(f"wrote {path}")
    return 0


def command_plan(args: argparse.Namespace) -> int:
    case = PlanningCase.load(args.case)
    if args.request:
        request = PlanRequest.load(args.request)
    else:
        if args.target is None or args.prescription is None or args.fractions is None:
            raise SystemExit(
                "without --request you must give --target, --prescription and --fractions"
            )
        request = PlanRequest(
            target=args.target,
            prescription_gy=float(args.prescription),
            fractions=int(args.fractions),
            gantry_angles=tuple(float(angle) for angle in args.angles),
            bixel_width_mm=float(args.bixel_width),
            field_margin_mm=float(args.margin),
            plan_label=args.label,
        )
    result = run_plan(case, request, case_path=args.case, progress=_progress(args.verbose))
    directory = result.save(args.out)
    print((directory / "report.txt").read_text(encoding="utf-8"))
    print(f"artifact written to {directory}")
    for name in sorted(path.name for path in directory.iterdir()):
        print(f"  {name}")
    return 0 if result.optimization.converged and not _blocking(result) else 2


def _blocking(result: PlanResult) -> bool:
    """A non-zero exit for anything a caller should not quietly build on."""
    return not result.optimization.converged


def command_report(args: argparse.Namespace) -> int:
    path = Path(args.plan)
    report = path / "report.txt" if path.is_dir() else path
    if not report.exists():
        raise SystemExit(f"no report at {report}")
    print(report.read_text(encoding="utf-8"))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    directory = Path(args.plan)
    plan_path = directory / "plan.json"
    if not plan_path.exists():
        raise SystemExit(f"no plan.json in {directory}")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    problems: list[str] = []
    checks: list[str] = []

    stored_request = plan.get("request", {})
    if sha256_json(stored_request) != plan.get("requestDigest"):
        problems.append("request.json does not match the recorded request digest")
    else:
        checks.append("frozen request matches its digest")

    with np.load(directory / "dose.npz", allow_pickle=False) as payload:
        dose = payload["dose"]
    if sha256_array(dose.reshape(-1)) != plan["dose"]["digest"]:
        problems.append("dose.npz does not match the recorded dose digest")
    else:
        checks.append("dose volume matches its digest")

    if args.case:
        case = PlanningCase.load(args.case)
        inputs = plan["provenance"]["inputs"]
        if sha256_array(case.ct_hu) != inputs["caseCTDigest"]:
            problems.append(f"{Path(args.case).name} CT does not match the CT this plan was computed from")
        elif sha256_array(case.labels) != inputs["caseLabelDigest"]:
            problems.append(f"{Path(args.case).name} labels do not match the labels this plan was computed from")
        else:
            checks.append(f"{Path(args.case).name} matches the plan's recorded case digests")

    if plan.get("clinicalUsePermitted") is not False:
        problems.append("artifact does not carry clinicalUsePermitted=false")
    else:
        checks.append("artifact is flagged nonclinical")

    for check in checks:
        print(f"PASS: {check}")
    for problem in problems:
        print(f"FAIL: {problem}", file=sys.stderr)
    if problems:
        print(f"\n{len(problems)} integrity check(s) failed", file=sys.stderr)
        return 1
    print(
        "\nAll recorded digests are internally consistent. This is a local integrity check only: "
        "it is not an approval, a verification of the dose model, or evidence of clinical validity."
    )
    return 0


def command_selftest(args: argparse.Namespace) -> int:
    """End-to-end smoke run on a small phantom, with physics spot checks."""
    print(f"{ENGINE_ID} self-test")
    case = build_phantom_case(dimensions=(48, 40, 32), spacing=(6.0, 6.0, 6.0), noise_hu=0.0)
    request = PlanRequest(
        target="PROSTATE",
        prescription_gy=60.0,
        fractions=20,
        gantry_angles=(0.0, 90.0, 180.0, 270.0),
        bixel_width_mm=10.0,
        field_margin_mm=10.0,
        plan_label="self-test",
    )
    result = run_plan(case, request, progress=_progress(args.verbose))
    target = result.dvhs["PROSTATE"].metrics
    print(f"  target mean {target['meanGy']:.2f} Gy, D95 {target['D95Gy']:.2f} Gy, V95% {target['V95pct']:.1%}")
    print(f"  optimiser: {result.optimization.iterations} iterations, {result.optimization.reason}")
    settings = PencilBeamSettings()
    print(f"  kernel d_max in water: {settings.dmax_mm():.2f} mm")
    ratio = target["meanGy"] / request.prescription_gy
    if not 0.9 <= ratio <= 1.1:
        print(f"FAIL: target mean is {ratio:.2f} x prescription", file=sys.stderr)
        return 1
    print("PASS: end-to-end planning run completed and reached the prescription in the target")
    return 0


# --- external research codes ------------------------------------------------

def _load_plan_dose(directory: Path) -> tuple[np.ndarray, dict[str, Any]]:
    """Read a plan artifact's dose and its plan.json."""
    plan_path = directory / "plan.json"
    if not plan_path.exists():
        raise SystemExit(f"no plan.json in {directory}")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    with np.load(directory / "dose.npz", allow_pickle=False) as payload:
        dose = payload["dose"]
    if sha256_array(dose.reshape(-1)) != plan["dose"]["digest"]:
        raise SystemExit(f"{directory}/dose.npz does not match its recorded digest; refusing to use it")
    return dose.reshape(-1).astype(np.float32), plan


def command_tools(args: argparse.Namespace) -> int:
    """Report which external installations were found, without running them."""
    from .external.matlab import find_library, find_matlab

    found: dict[str, Any] = {}
    problems = 0
    for name, resolve in (
        ("matlab", lambda: find_matlab(args.matlab)),
        ("matrad", lambda: find_library("matrad", args.matrad)),
        ("cerr", lambda: find_library("cerr", args.cerr)),
    ):
        try:
            found[name] = str(resolve())
        except Exception as exc:  # noqa: BLE001 - the message is the output
            found[name] = f"NOT FOUND: {exc}"
            problems += 1
    for name, value in found.items():
        print(f"{name:8s}: {value}")
    if args.version and "NOT FOUND" not in found["matlab"]:
        from .external.matlab import MatlabRunner

        print(f"{'version':8s}: {MatlabRunner(args.matlab).version()}")
    print(
        "\nmatRad and CERR are separately installed MATLAB codes used under their own licences. "
        "This package bundles neither and writes to neither checkout."
    )
    return 1 if problems else 0


def command_matrad(args: argparse.Namespace) -> int:
    from .external.matrad import MatRadSettings, run_matrad_plan

    case = PlanningCase.load(args.case)
    request = _request_from_args(args)
    settings = MatRadSettings(
        matlab=args.matlab,
        library=args.matrad,
        timeout_s=args.timeout,
        max_iterations=args.matrad_iterations,
    )
    result, job = run_matrad_plan(
        case, request, args.jobs, settings, case_path=args.case, progress=_progress(True)
    )
    directory = result.save(args.out)
    print((directory / "report.txt").read_text(encoding="utf-8"))
    print(f"artifact written to {directory}")
    print(f"matRad job retained at {job.path}")
    return 0


def command_cerr(args: argparse.Namespace) -> int:
    from .external.cerr import CerrSettings, run_cerr_analysis

    case = PlanningCase.load(args.case)
    dose, _ = _load_plan_dose(Path(args.plan))
    settings = CerrSettings(
        matlab=args.matlab, library=args.cerr, timeout_s=args.timeout, bin_width_gy=args.bin_width
    )
    analysis, job = run_cerr_analysis(case, dose, args.jobs, settings, progress=_progress(True))

    print(f"\nCERR cross-check of {args.plan}")
    print(f"  geometry round trip : {'exact' if analysis.sampling_is_voxel_exact else 'FAILED'}")
    print(f"  metric agreement    : {'within tolerance' if analysis.agrees else 'DISCREPANT'}")
    header = f"{'structure':12s} {'metric':6s} {'pytps':>10s} {'CERR':>10s} {'difference':>12s}"
    print("\n" + header)
    print("-" * len(header))
    for item in analysis.comparisons:
        for name, row in item.metrics.items():
            print(
                f"{item.structure:12s} {name:6s} {row['pytps']:10.4f} {row['cerr']:10.4f} "
                f"{row['difference']:+12.2e}"
            )
    for warning in analysis.warnings:
        print(f"WARNING: {warning}")
    output = Path(args.out) if args.out else Path(args.plan) / "cerr-analysis.json"
    _write_json(output, analysis.to_dict())
    print(f"\nwrote {output}")
    print(f"CERR job retained at {job.path}")
    return 0 if analysis.agrees else 2


def command_compare(args: argparse.Namespace) -> int:
    from .compare import compare_doses

    case = PlanningCase.load(args.case)
    reference, reference_plan = _load_plan_dose(Path(args.reference))
    evaluation, evaluation_plan = _load_plan_dose(Path(args.evaluation))

    left = reference_plan["provenance"]["inputs"]["caseCTDigest"]
    right = evaluation_plan["provenance"]["inputs"]["caseCTDigest"]
    if left != right:
        raise SystemExit(
            "the two plans were computed on different cases "
            f"({left[:12]} vs {right[:12]}); they cannot be compared"
        )
    if sha256_array(case.ct_hu) != left:
        raise SystemExit(f"{args.case} is not the case these plans were computed from")

    request = PlanRequest.from_dict(reference_plan["request"])
    comparison = compare_doses(
        case,
        reference,
        evaluation,
        reference_label=reference_plan.get("provider", "reference"),
        evaluation_label=evaluation_plan.get("provider", "evaluation"),
        request=request,
        gamma_criteria=(args.gamma_dose, args.gamma_distance) if not args.no_gamma else None,
    )
    print(f"reference : {comparison.reference_label}  ({args.reference})")
    print(f"evaluation: {comparison.evaluation_label}  ({args.evaluation})")
    header = f"\n{'structure':12s} {'metric':8s} {'reference':>10s} {'evaluation':>11s} {'difference':>11s}"
    print(header)
    print("-" * (len(header) - 1))
    for name, metrics in comparison.structures.items():
        for key, row in metrics.items():
            print(
                f"{name:12s} {key:8s} {row['reference']:10.3f} {row['evaluation']:11.3f} "
                f"{row['difference']:+11.3f}"
            )
    if comparison.objective_values:
        print("\nObjective value of the shared objective set, evaluated on each dose:")
        for label, value in comparison.objective_values.items():
            print(f"  {label:22s} {value:12.4f}")
        print("  (lower is better; this says which plan better satisfies what was asked)")
    print("\nVoxel difference:")
    for key, value in comparison.difference.items():
        print(f"  {key:26s} {value:10.4f}")
    if comparison.gamma:
        gamma = comparison.gamma
        print(f"\nGamma {gamma.criterion}: {gamma.pass_rate:.1%} pass over {gamma.evaluated_voxels:,} voxels")
        print(f"  mean {gamma.mean_gamma:.3f}, max {gamma.max_gamma:.3f}, {gamma.normalization}")
    for warning in comparison.warnings:
        print(f"\nWARNING: {warning}")
    if args.out:
        _write_json(Path(args.out), comparison.to_dict())
        print(f"\nwrote {args.out}")
    return 0


def command_engines(args: argparse.Namespace) -> int:
    from .external.matrad import MatRadSettings, compare_engines

    case = PlanningCase.load(args.case)
    request = _request_from_args(args)
    settings = MatRadSettings(matlab=args.matlab, library=args.matrad, timeout_s=args.timeout)
    comparison, job = compare_engines(
        case,
        request,
        args.jobs,
        settings,
        gamma_criteria=(args.gamma_dose, args.gamma_distance),
        progress=_progress(True),
    )
    print("\nDose-engine comparison on one uniform open field (no optimisation involved).")
    print("Both doses normalised to their own mean in a 10 mm sphere at the isocentre.\n")
    for key, value in comparison.difference.items():
        print(f"  {key:26s} {value:10.4f}")
    gamma = comparison.gamma
    if gamma:
        print(f"\nGamma {gamma.criterion}: {gamma.pass_rate:.1%} pass over {gamma.evaluated_voxels:,} voxels")
        print(f"  mean {gamma.mean_gamma:.3f}, max {gamma.max_gamma:.3f}")
    for warning in comparison.warnings:
        print(f"\nWARNING: {warning}")
    output = Path(args.out)
    _write_json(output, comparison.to_dict())
    print(f"\nwrote {output}")
    print(f"matRad job retained at {job.path}")
    return 0


def _request_from_args(args: argparse.Namespace) -> PlanRequest:
    """A plan request from --request, or from the inline options."""
    if getattr(args, "request", None):
        return PlanRequest.load(args.request)
    if args.target is None or args.prescription is None or args.fractions is None:
        raise SystemExit("without --request you must give --target, --prescription and --fractions")
    return PlanRequest(
        target=args.target,
        prescription_gy=float(args.prescription),
        fractions=int(args.fractions),
        gantry_angles=tuple(float(angle) for angle in args.angles),
        bixel_width_mm=float(args.bixel_width),
        field_margin_mm=float(args.margin),
        plan_label=getattr(args, "label", "research plan"),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pytps",
        description=f"pytps {__version__} - nonclinical photon planning research engine. {INTENDED_USE}",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=ENGINE_ID)
    subparsers = parser.add_subparsers(dest="command", required=True)

    phantom = subparsers.add_parser("phantom", help="write a synthetic phantom case")
    phantom.add_argument("--out", default="work/case.npz")
    phantom.add_argument("--case-id", default="PYTPS-PELVIS-001")
    phantom.add_argument("--dimensions", type=int, nargs=3, default=[72, 60, 48], metavar=("NX", "NY", "NZ"))
    phantom.add_argument("--spacing", type=float, nargs=3, default=[4.0, 4.0, 4.0], metavar=("SX", "SY", "SZ"))
    phantom.add_argument("--seed", type=int, default=20260905)
    phantom.add_argument("--noise", type=float, default=8.0, help="CT noise standard deviation in HU")
    phantom.set_defaults(handler=command_phantom)

    inspect = subparsers.add_parser("inspect", help="print a case summary and its digests")
    inspect.add_argument("case")
    inspect.set_defaults(handler=command_inspect)

    template = subparsers.add_parser("template", help="write a starter plan request")
    template.add_argument("--out", default="work/request.json")
    template.add_argument("--case", default=None, help="derive placeholder objectives from this case")
    template.add_argument("--target", default="PROSTATE")
    template.add_argument("--prescription", type=float, default=60.0, help="total-course Gy")
    template.add_argument("--fractions", type=int, default=20)
    template.add_argument("--angles", type=float, nargs="+", default=[0, 72, 144, 216, 288])
    template.add_argument("--bixel-width", type=float, default=6.0)
    template.add_argument("--margin", type=float, default=10.0)
    template.set_defaults(handler=command_template)

    plan = subparsers.add_parser("plan", help="compute dose and optimise fluence")
    plan.add_argument("--case", required=True)
    plan.add_argument("--request", default=None, help="a request JSON; overrides the inline options")
    plan.add_argument("--out", default="work/plan")
    plan.add_argument("--target", default=None)
    plan.add_argument("--prescription", type=float, default=None, help="total-course Gy")
    plan.add_argument("--fractions", type=int, default=None)
    plan.add_argument("--angles", type=float, nargs="+", default=[0, 72, 144, 216, 288])
    plan.add_argument("--bixel-width", type=float, default=6.0)
    plan.add_argument("--margin", type=float, default=10.0)
    plan.add_argument("--label", default="research plan")
    plan.add_argument("--verbose", action="store_true")
    plan.set_defaults(handler=command_plan)

    report = subparsers.add_parser("report", help="print the report from a plan artifact")
    report.add_argument("plan")
    report.set_defaults(handler=command_report)

    verify = subparsers.add_parser("verify", help="re-check a plan artifact's recorded digests")
    verify.add_argument("plan")
    verify.add_argument("--case", default=None, help="also check the artifact against this case file")
    verify.set_defaults(handler=command_verify)

    def add_external_options(parser: argparse.ArgumentParser, tools: str = "both") -> None:
        parser.add_argument("--matlab", default=None, help="MATLAB launcher (else $PYTPS_MATLAB, else discovery)")
        if tools in ("matrad", "both"):
            parser.add_argument("--matrad", default=None, help="matRad checkout (else $PYTPS_MATRAD)")
        if tools in ("cerr", "both"):
            parser.add_argument("--cerr", default=None, help="CERR checkout (else $PYTPS_CERR)")
        parser.add_argument("--jobs", default="work/jobs", help="where to keep external job folders")
        parser.add_argument("--timeout", type=int, default=3600, help="MATLAB timeout in seconds")

    tools = subparsers.add_parser("tools", help="report which external installations were found")
    tools.add_argument("--matlab", default=None)
    tools.add_argument("--matrad", default=None)
    tools.add_argument("--cerr", default=None)
    tools.add_argument("--version", action="store_true", help="also start MATLAB to read its version")
    tools.set_defaults(handler=command_tools)

    matrad = subparsers.add_parser("matrad", help="plan with matRad through a bridge")
    matrad.add_argument("--case", required=True)
    matrad.add_argument("--request", default=None)
    matrad.add_argument("--out", default="work/plan-matrad")
    matrad.add_argument("--target", default=None)
    matrad.add_argument("--prescription", type=float, default=None, help="total-course Gy")
    matrad.add_argument("--fractions", type=int, default=None)
    matrad.add_argument("--angles", type=float, nargs="+", default=[0, 72, 144, 216, 288])
    matrad.add_argument("--bixel-width", type=float, default=6.0)
    matrad.add_argument("--margin", type=float, default=10.0)
    matrad.add_argument("--label", default="matRad research plan")
    matrad.add_argument(
        "--matrad-iterations", type=int, default=3000,
        help="matRad's own optimiser iteration cap; its default of 500 often fails to converge",
    )
    add_external_options(matrad, "matrad")
    matrad.set_defaults(handler=command_matrad)

    cerr = subparsers.add_parser("cerr", help="cross-check a plan's DVHs with CERR")
    cerr.add_argument("--plan", required=True, help="a plan artifact directory")
    cerr.add_argument("--case", required=True)
    cerr.add_argument("--out", default=None, help="where to write the analysis JSON")
    cerr.add_argument("--bin-width", type=float, default=0.1, help="CERR histogram bin width in Gy")
    add_external_options(cerr, "cerr")
    cerr.set_defaults(handler=command_cerr)

    compare = subparsers.add_parser("compare", help="compare two plan artifacts on one case")
    compare.add_argument("--reference", required=True)
    compare.add_argument("--evaluation", required=True)
    compare.add_argument("--case", required=True)
    compare.add_argument("--out", default=None)
    compare.add_argument("--gamma-dose", type=float, default=3.0, help="gamma dose criterion, percent")
    compare.add_argument("--gamma-distance", type=float, default=3.0, help="gamma distance criterion, mm")
    compare.add_argument("--no-gamma", action="store_true")
    compare.set_defaults(handler=command_compare)

    engines = subparsers.add_parser(
        "engines", help="compare this dose engine against matRad's on one open field"
    )
    engines.add_argument("--case", required=True)
    engines.add_argument("--request", default=None)
    engines.add_argument("--out", default="work/engine-comparison.json")
    engines.add_argument("--target", default=None)
    engines.add_argument("--prescription", type=float, default=None)
    engines.add_argument("--fractions", type=int, default=None)
    engines.add_argument("--angles", type=float, nargs="+", default=[0])
    engines.add_argument("--bixel-width", type=float, default=6.0)
    engines.add_argument("--margin", type=float, default=10.0)
    engines.add_argument("--gamma-dose", type=float, default=3.0)
    engines.add_argument("--gamma-distance", type=float, default=3.0)
    add_external_options(engines, "matrad")
    engines.set_defaults(handler=command_engines)

    selftest = subparsers.add_parser("selftest", help="run a small end-to-end planning check")
    selftest.add_argument("--verbose", action="store_true")
    selftest.set_defaults(handler=command_selftest)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (ValueError, KeyError, FileNotFoundError, MemoryError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
