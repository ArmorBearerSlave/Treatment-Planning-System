import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


dataset = module("prepare_dataset")
adapter = module("spark_phantom_adapter")


def bundle():
    grid = dict(dimensions=[2, 2, 2], spacing=[1, 1, 1], origin=[0, 0, 0], direction=[1, 0, 0, 0, 1, 0, 0, 0, 1], frameID="fixture")
    def volume(modality, units, value):
        return dict(grid=grid.copy(), modality=modality, units=units, values=[value] * 8)
    return dict(schemaVersion=1, clinicalUsePermitted=False, intendedUse="synthetic-research-only", source=dict(
        syntheticOnly=True, generator="Analytic pelvis fixture", ct=volume("ct", "HU", 30),
        mr=volume("mr", "a.u.", 100), truth=volume("labels", "label", 1)))


class DatasetTests(unittest.TestCase):
    def test_placeholder_mr_never_enters_sct_training(self):
        for marker in ["flag", "note", "zeros"]:
            value = bundle()
            if marker == "flag": value["source"]["mrIsPlaceholder"] = True
            if marker == "note": value["source"]["sourceNotes"] = {"mr": "Synthetic zero placeholder"}
            if marker == "zeros": value["source"]["mr"]["values"] = [0] * 8
            with self.assertRaisesRegex(ValueError, "Placeholder MR"):
                dataset.training_pair(value, "syntheticCT", True)
            dataset.training_pair(value, "contour", True)

    def test_fixture_rejected_by_default(self):
        with self.assertRaises(ValueError):
            dataset.training_pair(bundle(), "contour")

    def test_fixture_can_exercise_contour_pair(self):
        image, target, _ = dataset.training_pair(bundle(), "contour", True)
        self.assertEqual(image.shape, (2, 2, 2))
        self.assertTrue((target == 1).all())

    def test_sct_pairs_mr_with_source_ct(self):
        image, target, _ = dataset.training_pair(bundle(), "syntheticCT", True)
        self.assertTrue((image == 100).all())
        self.assertTrue((target == 30).all())

    def test_prediction_is_never_dose_truth(self):
        value = bundle()
        value["artifacts"] = [{"operation": "predictDose", "volume": value["source"]["ct"]}]
        with self.assertRaises(ValueError):
            dataset.training_pair(value, "predictDose", True)

    def test_geometry_mismatch_rejected(self):
        value = bundle()
        value["source"]["mr"]["grid"]["frameID"] = "other"
        with self.assertRaises(ValueError):
            dataset.training_pair(value, "syntheticCT", True)

    def test_shape_and_nan_rejected(self):
        for values in [[1], [float("nan")] * 8]:
            value = bundle()
            value["source"]["ct"]["values"] = values
            with self.assertRaises(ValueError):
                dataset.training_pair(value, "contour", True)

    def test_anatomy_split_is_stable(self):
        self.assertEqual(dataset.split_for("ANATOMY-001"), dataset.split_for("ANATOMY-001"))
        self.assertIn(dataset.split_for("ANATOMY-001"), ["train", "validation", "test"])


class AdapterTests(unittest.TestCase):
    def recipe(self):
        return dict(anatomyID="A", seed=42, bodyScale=1, targetRadiusMM=18, motionPhase=0, nBioProfile="unbound")

    def test_recipe_accepts_bounded_parameters(self):
        self.assertEqual(adapter.validate_recipe(self.recipe())["seed"], 42)

    def test_rejects_extra_command_fields(self):
        recipe = self.recipe()
        recipe["command"] = "anything"
        with self.assertRaises(ValueError):
            adapter.validate_recipe(recipe)

    def test_rejects_nan_and_boolean_numeric_parameters(self):
        for invalid in [float("nan"), True, "1"]:
            recipe = self.recipe()
            recipe["bodyScale"] = invalid
            with self.assertRaises(ValueError):
                adapter.validate_recipe(recipe)


if __name__ == "__main__":
    unittest.main()
