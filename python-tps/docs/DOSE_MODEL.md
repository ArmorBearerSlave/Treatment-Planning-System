# Dose model

Everything here is a generic research kernel. No parameter below was measured
on a treatment machine, and no part of it has been commissioned.

## Coordinates

World coordinates are patient LPS millimetres: `+x` left, `+y` posterior,
`+z` superior. Grids are axis-aligned; a non-identity direction cosine matrix
is rejected rather than resampled. In memory a volume is `array[i, j, k]` with
shape `(nx, ny, nz)`. On disk, flat value lists are X-fastest XYZ so that files
interoperate with the other implementations in this repository.

## Beam geometry

For gantry angle `phi` (IEC 61217, head-first supine, couch and collimator 0):

```
source    = isocentre + SAD * ( sin phi, -cos phi, 0 )
beam axis = ( -sin phi,  cos phi, 0 )        source -> isocentre
u axis    = (  cos phi,  sin phi, 0 )        in-plane lateral
v axis    = (  0, 0, 1 )                     patient superior
```

so gantry 0 puts the source anterior to the patient and the beam travels
posteriorly, and gantry 90 puts it at the patient's left.

Lateral coordinates are always projected back to the isocentre plane:

```
r     = (P - source) . beam_axis
u_iso = (P - source) . u_axis * SAD / r
v_iso = (P - source) . v_axis * SAD / r
```

A bixel therefore keeps one `(u, v)` pair at every depth, and the divergence
appears as one explicit inverse-square factor rather than being smeared through
the kernel.

## Radiological depth

For each beam a beam's-eye-view lattice is marched outward from the source in
steps of `depth_step_mm` along the ray. Relative mass density is trilinearly
sampled at each lattice point and integrated trapezoidally:

```
z(d) = integral of rho along the ray from the source to distance d
```

Because the lattice depth axis *is* the along-ray distance, the path increment
is the step size and no obliquity correction is needed. The resulting field is
then trilinearly interpolated back onto the CT voxels. In water this reproduces
the geometric path length; a slab of density `rho` and thickness `t` reduces all
downstream depths by exactly `(1 - rho) * t`. Both are asserted in
`tests/test_dose.py`.

Density comes from a generic piecewise-linear HU lookup
(`pytps.materials.DEFAULT_HU_TO_DENSITY`), anchored at air 0.0012, water 1.000
and cortical bone 1.61. **It is not a scanner-specific calibration curve.**

## Dose kernel

For bixel `b` and voxel `i`:

```
D[i, b] = (SAD / r_i)^2 * T(z_i) * B(u_i - u_b; s_i) * B(v_i - v_b; s_i)

T(z) = (1 - exp(-beta z)) * exp(-mu z)                 depth dose
s(z) = sqrt(s0^2 + (a z)^2) * SAD / r                  lateral spread at isocentre
B(x; s) = 0.5 * [ erf((x + w/2) / (s sqrt2)) - erf((x - w/2) / (s sqrt2)) ]
```

`B` is the integral of a unit Gaussian across the bixel's width `w`, not the
Gaussian sampled at the bixel centre. This matters: sampling makes the dose
depend strongly on the bixel width whenever the bixel is wider than the lateral
spread, which is the usual case near the surface. Integrating makes the bixel
weights over a full field sum to one for any width, so the plan does not depend
on a discretisation choice. Measured across a 6x change in bixel width
(4 mm to 24 mm) the central-axis dose moves by about 1%.

numpy has no error function and this package takes no scipy dependency, so
`erf` is the Abramowitz & Stegun 7.1.26 approximation (`pytps.special`), with
about 1.5e-7 absolute error — far below the modelling error.

### Default parameters

| symbol | value | meaning |
| --- | --- | --- |
| `mu` | 0.0045 /mm | effective attenuation in water, 6 MV-like |
| `beta` | 0.27 /mm | build-up rate; with this `mu` it puts `d_max` at 15.2 mm |
| `s0` | 3.0 mm | lateral spread at the surface (source size and penumbra) |
| `a` | 0.055 | growth of lateral spread per mm of radiological depth |
| SAD | 1000 mm | source-axis distance |

These are plausible generic photon values chosen so the model behaves sensibly.
They are **not** derived from any measured beam.

## Sparse influence matrix

Entries are kept only where a voxel is inside the patient (relative density
above 0.05) or carries a structure label, and only for bixels within
`cutoff_sigmas` standard deviations plus half a bixel. Entries below
`kernel_threshold` times the beam's peak factor are dropped. The matrix is
stored as parallel row/column/value arrays; `np.bincount` provides both `D w`
and `D^T y`, which is what lets the whole solver run on numpy.

`max_entries` (default 40 million) stops a request that would exhaust memory,
and the error names the four things that reduce it.

## Optimisation

```
minimise  F(w) = sum_c f_c(D w)     subject to   w >= 0
```

with `f_c` drawn from `target_dose` (two-sided squared deviation), `max_dose`
and `min_dose` (one-sided), and `mean_dose` (one-sided on the structure mean).
Each is normalised by its structure's voxel count so weights are comparable
between a 36 cm3 target and a 5000 cm3 body contour.

The problem is convex, so the solver reaches a global minimum *of this
objective*. That is a numerical statement, not a clinical one.

The solver is FISTA with adaptive restart, nonnegativity projection and a
backtracking line search. It works in scaled variables `w = S v` with
`S = diag(1 / ||D[:, b]||)`: field-edge bixels deposit far less dose than
central ones, and without that scaling the iteration crawls. Because `S` is
positive and diagonal, `w >= 0` and `v >= 0` are the same constraint, so the
solution is unchanged — only the path to it is shorter. On a deliberately
ill-conditioned test problem the preconditioned solver reaches an objective
more than a hundred times lower within the same iteration budget.

The step size starts at `1 / L` with `L` estimated by power iteration on
`(D S)^T (D S)` times an upper bound on the objective curvature, then adapts.

## Known approximations, in order of importance

1. No commissioned beam model and no absolute calibration. Gy values are set by
   the optimiser matching the prescription.
2. The lateral kernel uses the *central-ray* radiological depth for its whole
   neighbourhood, so lateral electronic disequilibrium at density interfaces —
   the classic lung-tissue interface error — is not modelled.
3. One Gaussian, not the two or three that a tuned pencil-beam model uses, so
   the low-dose scatter tail is underestimated.
4. No head scatter, contaminant electrons, beam hardening or backscatter, so
   field-size and surface-dose behaviour is only qualitatively right.
5. Fluence is optimised, but nothing converts it into deliverable segments, so
   the plan is not achievable on a machine even in principle.
