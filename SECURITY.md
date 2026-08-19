# Security policy

## Nonclinical repository

This repository is not authorized to receive or process protected health
information, patient DICOM objects, clinical credentials, signing keys,
production secrets, or identifiable clinical evidence. Use synthetic or
appropriately authorized de-identified fixtures only.

## Reporting a vulnerability

Do not place vulnerability details, credentials, patient information, local
environment paths, or exploitable clinical-system information in a public
issue. Use GitHub's private vulnerability-reporting or Security Advisory
channel when available. Otherwise contact the repository owner through an
approved private institutional channel and provide only the minimum necessary
information.

Include the affected commit, component, configuration, reproducible nonclinical
steps, expected and observed behavior, potential safety or security impact, and
suggested containment. Do not test against a clinical system or patient data
without explicit authorization.

## Supported state

The repository remains a Stage A, nonclinical engineering mirror. No branch,
PDF, model, generated bundle, or passing structural check should be interpreted
as a supported clinical release.

## Historical path disclosure

Earlier Git history contains committed LaTeX build logs that disclosed a local
Windows user and OneDrive path. Current source removes those files from the
index and CI rejects recurrence. History has not been rewritten because doing
so would change commit hashes and may affect controlled trace references. The
repository owner must approve any later history-rewrite decision after impact
analysis and coordination with all clones and integrations.
