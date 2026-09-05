# Model choices — 2026-09-04

These are engineering candidates, not clinical suitability rankings. No local
benchmark can establish professional replacement or treatment authority.

## Local language models

The inspected Mac reports 128 GiB unified memory. Ollama reports the following
already installed models relevant to this project:

| Model | Assigned use | Reason |
|---|---|---|
| `qwen3-coder:30b` | Default bounded workflow/tool orchestration | Existing local installation and tool-oriented model family; avoids a new download |
| `qwen3:4b` | Fast fallback, short request routing | Smaller installed option for structured proposals |
| `qwen3.5:9b` | Future compact replacement candidate | Compare task adherence and latency with installed models |
| `qwen3.5:35b` | Future larger replacement candidate | Fits an evaluation profile on this Mac, subject to actual memory/latency measurement |

Qwen3 Coder is selected for compiling allowed operations, not for diagnosing,
selecting prescriptions, judging plan safety or providing independent physics
QA. Its code focus is useful only within that narrow orchestration role. The
same underlying model can serve all four assistants; their authority comes
from deterministic application checks, not from the prompt persona.

Ollama's Qwen3.5 catalog lists approximately 6.6 GB for 9B and 24 GB for 35B
weights. Runtime/KV-cache requirements are additional. This app caps the context
request at 8192 and output at 1024 tokens. It requests non-streaming JSON schema
output and disables thinking for the bounded planner request. It does not pull,
fine-tune or replace model weights.

Primary sources checked:

- [Qwen3 official repository](https://github.com/QwenLM/Qwen3)
- [Qwen3 Coder official repository](https://github.com/QwenLM/Qwen3-Coder)
- [Qwen3.5 9B model card](https://huggingface.co/Qwen/Qwen3.5-9B)
- [Qwen3.5 35B-A3B model card](https://huggingface.co/Qwen/Qwen3.5-35B-A3B)
- [Ollama Qwen3.5 catalog](https://ollama.com/library/qwen3.5)
- [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs)
- [Ollama chat contract](https://docs.ollama.com/api/chat)

## Image-model candidates

**Contouring:** nnU-Net is the initial task-specific training framework candidate.
TotalSegmentator is an external baseline for its supported structures and
modalities. Its native CLI/model does not directly satisfy this app's Core ML
contract: conversion, preprocessing, output labels and held-out geometry/accuracy
tests are required. License conditions differ by TotalSegmentator task.

**Dose prediction:** use a CT-and-structure-conditioned 3D regression U-Net as
the baseline architecture, trained on independently normalized reference dose
from the actual transport workflow. There is no universally suitable pretrained
checkpoint for the user's unprovided beam/site/protocol combination. No weights
are selected or fabricated. The synthetic demo's analytic dose is never a
permitted target in the dataset converter.

**Synthetic CT:** use a paired MR-to-CT 3D regression baseline with explicit HU
normalization. The source acquisition/modality and intended anatomy must be
fixed before selecting an actual checkpoint. The current contract targets MR
input; CBCT-to-CT needs a distinct versioned modality contract and dataset.
This is a proposed training architecture, not a bundled pretrained model.

Primary sources:

- [nnU-Net official repository](https://github.com/MIC-DKFZ/nnUNet)
- [TotalSegmentator official repository and task licenses](https://github.com/wasserth/TotalSegmentator)

## XCAT2 and OpenTOPAS/nBio

XCAT2 phantom generation belongs on the user's licensed Spark installation.
OpenTOPAS/nBio provides transport and microscopic biological scorer evidence,
which must retain the actual physics configuration, parameter digest, histories,
normalization and scorer units/uncertainty. Scorer results are not automatically
converted to TCP, NTCP, clinical RBE or tumor-control claims.

- [Duke XCAT phantom program](https://cvit.duke.edu/resource/xcat-phantom-program/)
- [TOPAS-nBio installation and OpenTOPAS compatibility](https://nbio.readthedocs.io/en/latest/getting-started/HowToInstall.html)
- [TOPAS-nBio introduction](https://nbio.readthedocs.io/en/latest/getting-started/Introduction.html)
- [OpenTOPAS documentation](https://opentopas.readthedocs.io/en/stable/index.html)

## Candidate promotion experiments

Language-model comparisons should measure valid-schema rate, negation handling,
refusal/out-of-scope behavior, task completion, unnecessary operations, memory,
latency and repeatability against a fixed adversarial request set. Log model
digests and runtime versions. Passing a smoke prompt is only connectivity and
contract evidence.

Image-model work requires anatomy-level held-out datasets, synthetic-to-real
domain-shift analysis, segmentation boundary errors, sCT HU/geometry errors,
and independent dose/QA endpoints with institution-approved tolerances. Synthetic
labels must be reviewed for generator errors. Data approval, model approval and
clinical release are three different decisions; this build grants none of them.
