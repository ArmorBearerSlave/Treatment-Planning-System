# AI dose-prediction feasibility spike

Trains and serves a small 3D U-Net that predicts a dose distribution
from a CT + RTSTRUCT, on a severely small (10-case) synthetic XCAT
prostate dataset. A technical feasibility/architecture demonstration --
not a validated clinical model. See spec/application_realizations.yaml
for the governance status.

## Build the dataset (once, on a machine with access to the source DICOM data)

```
python3 prepare_training_data.py
```

## Train

```
python3 train.py
```

Writes `dose_model.pt` next to this README.

## Serve (on a machine with an NVIDIA GPU, e.g. the DGX Spark)

```
pip install torch  # install the CUDA build matching your platform first
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8101
```

`POST /predict_dose` with `multipart/form-data` fields `ct_files`
(the CT DICOM slices) and `rtstruct_file` (the RTSTRUCT). Returns a raw
float32 binary buffer of predicted dose in Gy, in the CT volume's native
(frame, row, col) voxel order.

## Exploratory radiobiology

`radiobiology.py` applies explicitly supplied parameters for the linear-
quadratic survival model, Poisson TCP, generalized EUD, and LKB-style NTCP.
It accepts a `.npy` dose array plus named `.npz` masks and normalizes TOPAS'
`(x, y, z)` array convention to the XCAT mask `(z, y, x)` convention when
needed.

`radiobiology-parameters.synthetic-prostate.json` provides a documented,
literature-informed placeholder profile with sensitivity ranges. It is a
synthetic calibration profile, not a validated clinical parameter set.

Example:

```bash
python3 radiobiology.py \
	--dose combined_dose.npy \
	--masks case_masks.npz \
	--config radiobiology-parameters.json \
	--output endpoints.json
```

This is an exploratory synthetic calculation only. Dose must be normalized
to a declared total-course prescription before interpreting survival, TCP, or
NTCP; the declared fraction count is used to derive per-fraction tumor dose
for the LQ calculation. RBE,
alpha/beta, clonogen, TD50, slope, and volume parameters are inputs, not
validated defaults. The tool makes no clinical cancer-kill, tumor-control,
OAR-sparing, or patient-specific RBE claim.
