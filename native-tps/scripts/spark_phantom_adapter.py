"""Loopback-only XCAT2/OpenTOPAS-nBio adapter, intended to run on the DGX Spark.

Runs ONLY a locally configured command array, never a command from a request.
The command must write a native synthetic-case JSON at {output} using the
validated recipe at {recipe}. No XCAT executable or biological model is bundled.
Use an SSH tunnel from the Mac. Long-running production jobs need a durable queue.
"""
import argparse
import json
import math
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import subprocess
import tempfile


def validate_recipe(recipe):
    fields = {"anatomyID", "seed", "bodyScale", "targetRadiusMM", "motionPhase", "nBioProfile"}
    if not isinstance(recipe, dict) or set(recipe) != fields:
        raise ValueError("Invalid recipe fields")
    if not isinstance(recipe["anatomyID"], str) or not recipe["anatomyID"].strip() or len(recipe["anatomyID"]) > 100:
        raise ValueError("Invalid anatomy identifier")
    if type(recipe["seed"]) is not int or not 0 <= recipe["seed"] <= 1_000_000:
        raise ValueError("Invalid seed")
    for key, bounds in {"bodyScale": (0.7, 1.3), "targetRadiusMM": (8, 30), "motionPhase": (0, 1)}.items():
        value = recipe[key]
        if type(value) not in (int, float) or not math.isfinite(value) or not bounds[0] <= value <= bounds[1]:
            raise ValueError(f"Invalid {key}")
    if not isinstance(recipe["nBioProfile"], str) or not recipe["nBioProfile"].strip() or len(recipe["nBioProfile"]) > 200:
        raise ValueError("Invalid nBio profile")
    return recipe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command-file", required=True, type=Path, help="JSON argv array; fixed local command with {recipe} and {output} placeholders")
    parser.add_argument("--port", type=int, default=8105)
    args = parser.parse_args()
    command = json.loads(args.command_file.read_text())
    if not isinstance(command, list) or not command or not all(isinstance(s, str) for s in command):
        raise ValueError("Command must be a JSON string array")
    if not Path(command[0]).is_absolute() or not Path(command[0]).is_file():
        raise ValueError("Executable must be an existing absolute file")
    if not any("{recipe}" in s for s in command) or not any("{output}" in s for s in command):
        raise ValueError("Command requires recipe and output placeholders")

    class Handler(BaseHTTPRequestHandler):
        def send_json(self, status, value):
            data = json.dumps(value, allow_nan=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health":
                self.send_json(200, {"status": "adapter-configured", "engineVerified": False})
            else:
                self.send_json(404, {"error": "Not found"})

        def do_POST(self):
            if self.path != "/v1/phantoms":
                return self.send_json(404, {"error": "Not found"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 16_384:
                    return self.send_json(413, {"error": "Recipe size invalid"})
                recipe = validate_recipe(json.loads(self.rfile.read(length)))
                with tempfile.TemporaryDirectory(prefix="tps-phantom-") as directory:
                    folder = Path(directory)
                    recipe_path, output_path = folder / "recipe.json", folder / "case.json"
                    recipe_path.write_text(json.dumps(recipe, allow_nan=False))
                    argv = [part.replace("{recipe}", str(recipe_path)).replace("{output}", str(output_path)) for part in command]
                    with (folder / "run.log").open("wb") as log:
                        subprocess.run(argv, cwd=folder, stdin=subprocess.DEVNULL, stdout=log, stderr=log, check=True, timeout=150)
                    if output_path.is_symlink() or not output_path.is_file() or output_path.stat().st_size > 96_000_000:
                        raise ValueError("Generator output is missing, oversized or a symbolic link")
                    result = json.loads(output_path.read_bytes())
                    if result.get("syntheticOnly") is not True or result.get("schemaVersion") != 1 or result.get("recipe") != recipe:
                        raise ValueError("Generator output identity mismatch")
                    self.send_json(200, result)  # Mac validates full volume geometry and evidence.
            except (ValueError, KeyError, TypeError):
                self.send_json(400, {"error": "Recipe or generator result failed validation"})
            except subprocess.TimeoutExpired:
                self.send_json(504, {"error": "Generator exceeded 150 seconds; use a precomputed case or a future queued adapter"})
            except (OSError, subprocess.CalledProcessError):
                self.send_json(502, {"error": "Configured generator failed; inspect the local generator installation"})

        def log_message(self, *_):
            pass  # No case metadata in access logs.

    server = HTTPServer(("127.0.0.1", args.port), Handler)
    server.timeout = 10
    print(f"Phantom adapter listening on loopback port {args.port}; use SSH forwarding from the Mac.")
    server.serve_forever()


if __name__ == "__main__":
    main()
