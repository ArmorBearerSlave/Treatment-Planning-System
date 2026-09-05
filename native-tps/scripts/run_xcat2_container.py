"""Spark-side wrapper for the user-supplied XCAT2 Docker launch template.

No image, XCAT flags, recipe mapping or output conversion is guessed. A complete
local configuration is required. The HTTP adapter can invoke this script with
--config, --recipe and --output. Use --print-template for a nonexecuting preview.
"""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import time
import uuid

from spark_phantom_adapter import validate_recipe


def mount_path(value):
    if not isinstance(value, str) or not value.startswith("/") or any(c in value for c in ":\r\n\0"):
        raise ValueError("Mount paths must be absolute and contain no colon or control characters")
    return value


def validate_launcher_format(config):
    if not isinstance(config, dict):
        raise ValueError("Launcher configuration must be a JSON object")
    if any(isinstance(config.get(key), dict) for key in ["xcat_arguments", "converter_argv"]):
        raise ValueError("This is a multi-stage Spark pipeline reference, not a single-job launcher config. "
                         "Use spark-xcat2-launcher.example.json; a native case converter and exact recipe mapping are still required.")
    if config.get("platform", "linux/amd64") != "linux/amd64":
        raise ValueError("XCAT2 launcher requires platform linux/amd64")


def validate_config(config, recipe):
    validate_launcher_format(config)
    for key in ["runtime_directory", "anatomy_directory"]:
        mount_path(config[key])
    image = config.get("image")
    if not isinstance(image, str) or not re.fullmatch(r"[^\s<>@]+@sha256:[0-9a-f]{64}", image):
        raise ValueError("Supply the exact image reference pinned as repository@sha256:<64 hex digits>")
    parameter = config.get("parameter_file")
    if not isinstance(parameter, str) or PurePosixPath(parameter).is_absolute() or ".." in PurePosixPath(parameter).parts or not parameter:
        raise ValueError("Parameter file must be a relative file inside the runtime mount")
    arguments = config.get("xcat_arguments")
    if not isinstance(arguments, list) or not all(isinstance(v, str) and not any(c in v for c in "\0\r\n<>") for v in arguments):
        raise ValueError("Supply verified XCAT arguments as a JSON argv array (or explicitly [] if none)")
    # Until a real parameter mapper is supplied, accept only a reviewed fixed recipe.
    supported = config.get("supported_recipe")
    validate_recipe(recipe)
    if supported is None or validate_recipe(supported) != recipe:
        raise ValueError("Recipe must exactly match supported_recipe; no XCAT parameter mapping has been inferred")
    converter = config.get("converter_argv")
    if not isinstance(converter, list) or not converter or not all(isinstance(v, str) and v and "\0" not in v for v in converter):
        raise ValueError("Supply a converter argv array for real XCAT output → native case JSON")
    if not Path(converter[0]).is_absolute():
        raise ValueError("Converter executable must be an absolute path")
    for placeholder in ["{raw_prefix}", "{recipe}", "{output}"]:
        if not any(placeholder in part for part in converter):
            raise ValueError(f"Converter argv must include {placeholder}")


def docker_argv(config, output_directory, image=None, arguments=None, name=None):
    validate_launcher_format(config)
    if arguments is not None and not isinstance(arguments, list):
        raise ValueError("Preview arguments must be an argv array")
    command = ["docker", "run", "--rm", "--platform", "linux/amd64"]
    if name:
        command += ["--name", name]
    command += [
        "-v", mount_path(config["runtime_directory"]) + ":/w:ro",
        "-v", mount_path(config["anatomy_directory"]) + ":/anatomy:ro",
        "-v", mount_path(str(output_directory)) + ":/out",
        "-w", "/w", image or config.get("image") or "<pinned-image>",
        "./dxcat2_linux_64bit", config["parameter_file"],
    ]
    command += arguments if arguments is not None else config.get("xcat_arguments") or []
    return command + ["/out/case_name"]


def run(config, recipe_path, output_path):
    recipe = json.loads(recipe_path.read_text())
    validate_config(config, recipe)
    for key in ["runtime_directory", "anatomy_directory"]:
        if not Path(config[key]).is_dir():
            raise ValueError(f"{key} is not present on this host; run the wrapper on the Spark")
    runtime = Path(config["runtime_directory"])
    for path in [runtime / "dxcat2_linux_64bit", runtime / config["parameter_file"]]:
        if not path.is_file():
            raise ValueError(f"Required runtime file is missing: {path.name}")
    if not shutil.which("docker") or not Path(config["converter_argv"][0]).is_file():
        raise ValueError("Docker or the configured converter is unavailable")
    if output_path.exists():
        raise ValueError("Output already exists; choose a new case output")
    # Keep each request's mount isolated; no user-provided recipe text becomes argv.
    deadline = time.monotonic() + 130
    name = "tps-xcat-" + uuid.uuid4().hex
    with tempfile.TemporaryDirectory(prefix="xcat-", dir=output_path.parent) as directory:
        raw = Path(directory)
        command = docker_argv(config, raw, name=name)
        try:
            subprocess.run(command, check=True, stdin=subprocess.DEVNULL, timeout=110)
            converted = raw / "converted.json"
            replacements = {"{raw_prefix}": str(raw / "case_name"), "{recipe}": str(recipe_path), "{output}": str(converted)}
            argv = list(config["converter_argv"])
            for key, value in replacements.items():
                argv = [part.replace(key, value) for part in argv]
            subprocess.run(argv, check=True, stdin=subprocess.DEVNULL, timeout=max(1, deadline-time.monotonic()))
            if converted.is_symlink() or not converted.is_file() or converted.stat().st_size > 96_000_000:
                raise ValueError("Converter output is missing, oversized or a symlink")
            result = json.loads(converted.read_bytes())
            if result.get("schemaVersion") != 1 or result.get("syntheticOnly") is not True or result.get("recipe") != recipe:
                raise ValueError("Converter output has the wrong case contract or recipe")
            converted.rename(output_path)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            # Kill only the uniquely named container belonging to this request.
            subprocess.run(["docker", "rm", "-f", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, check=False)
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--recipe", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--print-template", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    if args.print_template:
        # JSON argv preserves token boundaries; this is not an executable shell string.
        placeholder_args = ["<XCAT2 arguments>"] if config.get("xcat_arguments") is None else config["xcat_arguments"]
        print(json.dumps(docker_argv(config, "/output/path", arguments=placeholder_args), indent=2))
        return
    if args.recipe is None or args.output is None:
        parser.error("Execution requires --recipe and --output")
    run(config, args.recipe.resolve(), args.output.absolute())


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        raise SystemExit(f"XCAT2 adapter stopped: {error}")
