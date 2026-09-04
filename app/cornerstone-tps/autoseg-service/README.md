# Auto-segmentation inference service

Runs TotalSegmentator against an uploaded CT DICOM series and returns
per-structure contour polygons in DICOM patient (LPS) coordinates. A
technical feasibility spike -- results are unreviewed AI proposals, not a
validated clinical component.

## Run (on a machine with an NVIDIA GPU, e.g. the DGX Spark)

```
python3 -m venv venv
source venv/bin/activate
pip install torch  # install the CUDA build matching your platform first
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8100
```

`POST /segment` with `multipart/form-data` field `files` containing the CT
DICOM slice files. Returns `{ rois: [{ name, color, contours }], model,
unverified }`.
