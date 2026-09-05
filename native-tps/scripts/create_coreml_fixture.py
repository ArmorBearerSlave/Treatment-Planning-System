"""Build an untrained identity network to test the native Core ML tensor contract.
This is explicitly a fixture; its output is NOT a meaningful synthetic CT.
Requires Apple's coremltools. It downloads no model weights.
"""
import argparse
import hashlib
import json
from pathlib import Path
from coremltools.models import datatypes
from coremltools.models.neural_network import NeuralNetworkBuilder
from coremltools.models.utils import save_spec

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
shape = datatypes.Array(1, 1, 32, 32, 32)
builder = NeuralNetworkBuilder([("image", shape)], [("output", shape)], disable_rank5_shape_mapping=True, use_float_arraytype=True)
builder.add_activation(name="identity_fixture", non_linearity="LINEAR", input_name="image", output_name="output", params=[1, 0])
path = args.output / "identity-fixture.mlmodel"
save_spec(builder.spec, str(path))
manifest = dict(schemaVersion=1, modelID="test-only/identity-contract", version="1.0", operation="syntheticCT",
                modelFile=path.name, modelSHA256=hashlib.sha256(path.read_bytes()).hexdigest(),
                dimensions=[32, 32, 32], inputOffset=0, inputScale=1, inputClip=[-2000, 2000],
                outputScale=1, outputOffset=0, structures=[], intendedUse="synthetic-research-only", isFixture=True)
(args.output / "manifest.json").write_text(json.dumps(manifest, indent=2))
print("Created untrained Core ML identity fixture; not an image-prediction model.")
