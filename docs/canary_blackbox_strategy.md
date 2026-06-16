# Canary Black-Box Strategy

This document describes the initial CanaryJudge design boundary for APRT
Judge/QC v0. It is a draft and should evolve with calibration and review data.

## Principle

CanaryJudge should detect seeded markers or canary-like markers in target
responses and emit evidence. It should not directly decide that a response is a
confirmed finding.

In black-box settings, a string match does not always prove that protected
system text, internal policy, or sensitive data was leaked. The marker may be
synthetic, seeded, transformed, quoted, or unrelated to the active attack goal.

## Evidence Role

Canary evidence should capture safe metadata such as:

- matched reference identifier
- response locator
- detector mode
- confidence
- verification class
- redacted match summary

Evidence must not store plaintext secrets or raw canary values.

## Deferred Judgment

The following questions belong outside the low-level detector or in a later
model-assisted verification layer:

- whether the marker is actually protected material
- whether the exposure is relevant to the current attack goal
- whether the result can be promoted to a finding candidate
- whether semantic review or human review is required

## v0 Direction

For v0, CanaryJudge should remain a replaceable detector that can support exact
matches, prefix or pattern matches, and synthetic marker references. Final
scoring, fitness, and decisions must remain in the rubric and routing pipeline.
