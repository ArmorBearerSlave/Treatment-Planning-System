# Desktop OpenTOPAS integration

The Mac app's **OpenTOPAS** workspace controls the installed Spark engine over SSH. ML and local LLM inference remain on the Mac. This integration is contained in `native-tps`; remote job storage is separate from existing simulation batches.

## Workflow

1. Open OpenTOPAS and check the `spark-wired` connection. Existing SSH keys/configuration must already work; the app does not request or save passwords.
2. Enter a remote folder of prepared TOPAS inputs. List each input filename (comma separated), including macros, included material files, and referenced volumes. Enter the macros in execution order.
3. **Prepare input snapshot** creates a unique job under `/home/armorbearer/.local/share/governed-tps/topas-jobs/<UUID>`. No transport runs at this point. Review the displayed parameters and hashes, including source histories, geometry, physics and scoring.
4. Check the review box and **Submit reviewed simulation**. TOPAS runs sequential macros in that job's private `work` folder. A duplicate submission is rejected. Engine, launcher, worker and input hashes must match preparation. This checkbox is an operator workflow control, not an authenticated clinical signature.
5. **Refresh job** retrieves status and the last 24 KB of logs. The job survives closing the app or SSH. The last job ID is retained locally; other job IDs can be entered. A stale worker lock/state is reported as interrupted after 15 seconds. There is no automatic retry, scheduler, cancellation UI or batch concurrency manager.
6. **Download results** saves a tar.gz containing input snapshot, manifest, status, worker, full log, raw outputs and output hashes. Downloads are limited to 512 MiB of uncompressed job files. Larger jobs require a separate transfer. Verify output files against `outputs.json` after extraction.

The UI's default case-001 paths are examples from the existing exploratory batch, not a prescription to rerun it. Preparation copies only the listed files and does not invoke `run_case_mc.py`, which writes into shared batch case folders. No cohort batch was launched during integration.

## Supported inputs and scope

Python 3 is required on Spark. The launcher is `/home/armorbearer/hupci-sim/opentopas/run-topas.sh`; the executable is `/home/armorbearer/hupci-sim/opentopas/topas-install/bin/topas`. Their SHA-256 digests are captured, not inferred versions. The engine log is the version evidence.

Inputs must be explicit regular files, up to 1 GiB total, with `.txt` macros. Include files and `InputFile` references must be listed; `InputDirectory` must be `./`. Parent traversal, symlinks, quoted absolute paths, and output names colliding with input names are rejected. This is a restricted bridge for trusted prepared parameters, not a complete TOPAS parser or an OS sandbox. Custom extensions and dynamic file parameters require separate inspection; do not feed arbitrary untrusted macros to a privileged SSH account.

Runtime libraries, environment, Geant4 datasets and built-in default parameters are not snapshotted. The hashes provide provenance and change detection, not a hermetic runtime or an externally anchored audit. Remote account owners can modify job records. Preparation can leave an incomplete folder if interrupted; it cannot be submitted without a complete manifest and prepared status. SSH requests have a 120-second desktop watchdog, while detached simulations have no artificial runtime cap. After uncertain submission, refresh the existing job ID before doing anything else.

## CT and training handoff

Downloaded scorer output is **raw transport evidence**, not an automatically aligned or calibrated training target. This version does not automatically combine fields, normalize to a course, resample, convert DICOM, or attach dose to a selected case. The existing `scripts/convert_spark_case.py` remains a separate, case-specific conversion step. Check its geometry assumptions and normalization limitations in INTEGRATION.md before use. Import its validated native CT case through **Import case…**; confirm reference provenance and anatomy grouping in **Dataset & learning** before splitting.

No MR is generated. XCAT2 phantom generation is a separate stage; these macros consume already prepared geometry. nBio endpoints are only available if the engine actually includes the required components/scorers; an nBio source tree on disk is not evidence that the running binary has them.

## Verified on 2026-09-05

- Xcode desktop build succeeded; six Python bridge tests cover isolation, missing references, traversal/symlink rejection, output collisions, tampering, duplicate submission, worker success/failure and stale status.
- Desktop UI restored and submitted job `2f895f30-96c7-4810-913d-01feda7325f8`, refreshed completion, and downloaded the result archive. Ten 5 MeV proton histories in a water box completed; `WaterDose.csv` SHA-256 is `69ff3445e5c38f2f8d5a8cfb5e101ab7e7a17b6a264177db63df844fc53bb4f8`. This tests plumbing, not statistical precision or physical commissioning. Input source is `config/topas-water-smoke.txt`.
- The installed binary reported TOPAS 4.2.p3 and Geant4 11.04 patch 02. Its SHA-256 was `c7056408b78866a002cc1a8de075fc451c40ac10c4eabd451925c84618131ee7`.
- Existing nBio spherical-cell test, copied to isolated job `fec23385-f659-4ae5-bdbf-58a830d84df6`, failed with **unsupported Component Type: TsSphericalCell**. Failure status and log retrieval worked. The shared installation was not rebuilt or changed. Resolve component registration/build compatibility before claiming nBio cell-scoring support.

## Development

Edit `scripts/topas_jobs.py`, then run `python3 scripts/generate_topas_bridge.py` to regenerate the embedded Swift source. Run `python3 scripts/generate_xcode_project.py` after adding Swift files. The app sends the bridge over SSH and persists the exact worker in each prepared job; no HTTP daemon, tunnel or system service installation is required.

Tests: `python3 -m unittest discover -s Tests/Python -v` from `native-tps`.
