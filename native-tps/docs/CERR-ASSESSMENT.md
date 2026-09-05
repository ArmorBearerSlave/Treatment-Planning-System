# CERR integration assessment — 2026-09-05

**Historical assessment. CERR is now connected to the desktop through the CT/label/dose analysis bridge. See [CERR integration](CERR.md) for current capabilities and verification. The findings below describe the pre-integration probe.**

## Installation and existing code

The checked installation is:

`/Users/ericbrass/Documents/medical-physics-mbse/CERR/CERR-master`

The other project also contains CERR container installation/check scripts. Those scripts are not the native TPS adapter, were not executed, and do not establish a working desktop integration. No CERR/planC adapter was found in `native-tps` sources, scripts, configuration or existing documentation before this assessment. The separate `python-tps` work was not modified.

A read-only Spark search under `/home/armorbearer`, limited to five directory levels and common CERR installation names, found no matching installation. This does not establish absence elsewhere on Spark.

## Runtime verification

Ran the installed MATLAB R2025b in a separate batch process, adding the local CERR directory only to that process's MATLAB path:

- MATLAB reported Apple Silicon platform `MACA64`.
- `initializeCERR` returned a 25-cell planC skeleton.
- `CERRImportDICOM`, `getDVH`, and `accumulate` resolved from the checked CERR installation.
- `doseHist([0 1 2 3],[1 1 1 1],1)` returned the expected four bins and unit volume in each bin. Assertions passed.

Log: `native-tps/build/cerr-check/runtime.log`.

This test used only synthetic numeric arrays. It did not load the DICOM examples in the other project, launch CERR's viewer, exercise full structure rasterization or `getDVH`, import a DICOM study, run radiomics, or validate optional MEX/Python/deep-learning dependencies. Function discovery is not execution verification. Full compatibility with MATLAB R2025b remains feature-specific.

## Role in the governed TPS

CERR's documented capabilities include radiotherapy/radiology data access, import, contouring, radiomics, segmentation and outcomes research. Its planC container is a potential interchange layer for scans, structures and dose. These complement matRad planning and OpenTOPAS transport. [Official CERR repository](https://github.com/cerr/CERR)

Recommended first integration: a local MATLAB analysis/import adapter for the CT-only workflow, followed by a checked comparison of native and CERR dose-volume metrics. It does not require MR.

1. Pin the CERR source revision or capture its source fingerprint; use isolated jobs and MATLAB processes to avoid path conflicts with matRad.
2. Import an explicitly selected CT/RTSTRUCT/RTDOSE study into planC, preserving source identifiers and provenance. The inspected legacy `CERRImportDICOM` documents single-study batch input and first-object selection; do not apply it blindly to a multi-study cohort. Select and validate the appropriate importer.
3. Validate CERR-to-native array orientation, physical coordinates, length units, CT offsets, dose units, frame identity and structure-to-scan references using an asymmetric synthetic fixture.
4. Compare dose-volume measurements with matching sampling, interpolation, binning and percentile definitions. CERR's `doseHist` uses bins; the native D95 implementation uses sorted voxel samples. Apparent discrepancies must not be treated as physics errors without reconciling those definitions.
5. Return provenance-bound analysis results for research review. CERR analysis does not automatically certify matRad plans, OpenTOPAS dose normalization or training labels.

No application behavior or dataset was changed by this assessment. The next executable milestone is a synthetic CT/structure/dose round trip and full DVH comparison, before adding a CERR workspace to the app.
