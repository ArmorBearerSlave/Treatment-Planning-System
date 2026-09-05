# MRiLab integration assessment — 2026-09-05

Status: **not integrated; runtime not verified**. This assessment does not add an MR channel or change the CT-only dataset.

## Local findings

- No MRiLab references or adapter were found in the native TPS sources, scripts or configuration. The desktop currently exposes matRad planning and OpenTOPAS, but no MRiLab workspace.
- No matching installation was found in the searched Mac Documents, relevant Dropbox/project, MATLAB, Downloads or Desktop paths, or in Spotlight filename results. This is not an exhaustive search of every volume or ignored directory.
- A read-only search under `/home/armorbearer` on `spark-wired`, limited to five directory levels, found no MRiLab-named installation. Other locations remain unverified.
- MATLAB R2025b exists on the Mac and was successfully exercised for matRad earlier in this session. That verifies MATLAB, not MRiLab or its compiled kernels.
- The shared core can represent optional MR volumes and rejects absent/placeholder MR for synthetic-CT inference. It has no structured MR acquisition/simulation evidence contract yet.

## What MRiLab could add

MRiLab models signal formation, k-space acquisition and reconstruction, with pulse-sequence, coil and field configuration. Its upstream README identifies batch simulation support in v1.3. This suggests a separate MATLAB process adapter is feasible in principle; it is not proof that the current release runs here. [Official repository](https://github.com/leoliuf/MRiLab)

Its documented virtual object includes proton density, T1, T2, T2*, spin species and geometry. Property arrays use Y × X × Z × species, relaxation times use seconds, and voxel dimensions use metres. A future XCAT2 adapter must attach documented tissue-property assumptions and convert the TPS's millimetre/LPS grid explicitly. CT HU and anatomical labels alone do not specify those MR properties. [Virtual-object specification](https://mrilab.sourceforge.net/manual/MRiLab_User_Guide_v1_3/MRiLab_User_Guidech3.html)

## Compatibility work required

Upstream documentation describes MATLAB/GUI code plus compiled MEX kernels, OpenMP CPU execution and NVIDIA CUDA acceleration, with historically tested Windows/Linux MATLAB versions. It does not establish compatibility with this Mac's Apple Silicon MATLAB R2025b. Assess the CPU build first for Mac execution; the existing CUDA implementation is not an Apple GPU/Metal backend. A Spark deployment also needs architecture-compatible MATLAB/MEX/CUDA dependencies rather than assuming older Linux binaries work on ARM64. No compilation or simulation was performed in this check. [Installation and dependencies](https://mrilab.sourceforge.net/manual/MRiLab_User_Guide_v1_3/MRiLab_User_Guidech1.html)

## Proposed integration boundary

1. Pin an upstream version and prove a small documented sequence works on the chosen runtime.
2. Define and review an XCAT-label-to-MR-property manifest with units, provenance and supported tissue model.
3. Store independent job snapshots containing object maps, sequence, coil/field settings, random seeds and engine hashes.
4. Retain raw k-space and reconstruction settings; validate array ordering, orientation and geometry with an asymmetric fixture before attaching reconstructed MR.
5. Represent the output as an explicitly simulated, separately versioned MR research case. Preserve the CT-only source case and prohibit automatic promotion to an acquired MR or validated training reference.

For the current request, the concrete next step is an isolated runtime/build feasibility test. Application wiring and MR dataset generation have not been implemented or executed.
