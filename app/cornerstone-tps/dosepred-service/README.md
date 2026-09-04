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
