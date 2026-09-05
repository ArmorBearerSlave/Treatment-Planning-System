"""Command-line interface.

    python -m pytps phantom  --out work/case.npz
    python -m pytps inspect  work/case.npz
    python -m pytps template --out work/request.json
    python -m pytps plan     --case work/case.npz --request work/request.json --out work/plan
    python -m pytps report   work/plan
    python -m pytps verify   work/plan --case work/case.npz
    python -m pytps selftest
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

    selftest = subparsers.add_parser("selftest", help="run a small end-to-end planning check")
    selftest.add_argument("--verbose", action="store_true")
    selftest.set_defaults(handler=command_selftest)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (ValueError, KeyError, FileNotFoundError, MemoryError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
