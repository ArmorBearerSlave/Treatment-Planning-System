import importlib.util
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_xcat2_container as launcher


class XCATLauncherTests(unittest.TestCase):
    def config(self):
        return dict(runtime_directory="/runtime", anatomy_directory="/anatomy",
                    image="example/xcat@sha256:" + "a" * 64, parameter_file="general.samp.par",
                    xcat_arguments=["-example", "value with spaces"],
                    supported_recipe=dict(anatomyID="A", seed=42, bodyScale=1, targetRadiusMM=18, motionPhase=0, nBioProfile="unbound"),
                    converter_argv=["/converter", "{raw_prefix}", "{recipe}", "{output}"])

    def test_preserves_mounts_platform_and_argv_boundaries(self):
        config = self.config()
        command = launcher.docker_argv(config, "/tmp/job")
        self.assertEqual(command[:5], ["docker", "run", "--rm", "--platform", "linux/amd64"])
        for value in ["/runtime:/w:ro", "/anatomy:/anatomy:ro", "/tmp/job:/out", "value with spaces"]:
            self.assertIn(value, command)
        self.assertEqual(command[-1], "/out/case_name")

    def test_incomplete_image_and_arguments_fail_closed(self):
        for key, value in [("image", "xcat:latest"), ("image", None), ("xcat_arguments", None)]:
            config = self.config(); config[key] = value
            with self.assertRaises(ValueError):
                launcher.validate_config(config, config["supported_recipe"])

    def test_changed_recipe_is_not_silently_ignored(self):
        config = self.config(); recipe = dict(config["supported_recipe"], seed=99)
        with self.assertRaises(ValueError):
            launcher.validate_config(config, recipe)

    def test_explicit_empty_arguments_permitted(self):
        config = self.config(); config["xcat_arguments"] = []
        launcher.validate_config(config, config["supported_recipe"])

    def test_mount_options_cannot_be_injected(self):
        config = self.config(); config["runtime_directory"] = "/runtime:/other:rw"
        with self.assertRaises(ValueError):
            launcher.validate_config(config, config["supported_recipe"])

    def test_parameter_cannot_escape_runtime(self):
        config = self.config(); config["parameter_file"] = "../outside.par"
        with self.assertRaises(ValueError):
            launcher.validate_config(config, config["supported_recipe"])

    def test_pipeline_reference_cannot_be_previewed_as_single_job(self):
        config = json.loads((ROOT / "config/spark-xcat2.example.json").read_text())
        with self.assertRaisesRegex(ValueError, "multi-stage Spark pipeline reference"):
            launcher.docker_argv(config, "/tmp/job")
        with self.assertRaisesRegex(ValueError, "multi-stage Spark pipeline reference"):
            launcher.validate_config(config, self.config()["supported_recipe"])

    def test_launcher_example_preserves_pin_but_requires_mapping(self):
        config = json.loads((ROOT / "config/spark-xcat2-launcher.example.json").read_text())
        reference = json.loads((ROOT / "config/spark-xcat2.example.json").read_text())
        self.assertEqual(config["image"], reference["image"])
        self.assertIn(config["image"], launcher.docker_argv(config, "/tmp/job"))
        with self.assertRaisesRegex(ValueError, "verified XCAT arguments"):
            launcher.validate_config(config, self.config()["supported_recipe"])

    def test_platform_is_not_silently_overridden(self):
        config = self.config(); config["platform"] = "linux/arm64"
        with self.assertRaisesRegex(ValueError, "linux/amd64"):
            launcher.docker_argv(config, "/tmp/job")


if __name__ == "__main__":
    unittest.main()
