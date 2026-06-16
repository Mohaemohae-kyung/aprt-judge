# APRT Judge/QC v0 Architecture

This document is a working draft for the APRT Judge/QC v0 skeleton. The design
is not final and should remain easy to replace as calibration data and review
results improve.

## Goal

Judge/QC evaluates target responses and produces a `JudgeResult`. It is not
responsible for generating attacks, executing targets, managing the archive, or
running the evolution loop.

## Pipeline

```text
RunObservation
-> JudgeService
-> GoalRubricResolver
-> JudgeDispatcher
-> CanaryJudge / RegexJudge
-> EvidenceValidator
-> RubricEvaluator
-> FitnessCalculator
-> DecisionRouter
-> JudgeResult
```

## Responsibility Split

Judges are evidence producers. They may detect seeded markers, canary-like
markers, regex matches, or other signals, but they do not compute final fitness
or final decisions.

`EvidenceValidator` validates, normalizes, redacts, and deduplicates evidence.
It should enforce the evidence contract, including secret-safe storage.

`RubricEvaluator` converts validated evidence into raw rubric scores.

`FitnessCalculator` converts raw scores into fitness.

`DecisionRouter` applies thresholds, decision caps, and policy constraints to
produce the final decision.

## External Boundaries

`AttackGenome`, `RunObservation`, and `ArchiveEntry` are shared APRT objects
owned outside this package. This repository may define minimal reference types,
but it should not take ownership of full attack, harness, archive, descriptor,
or evolution behavior.

## v0 Non-Goals

- full CanaryJudge implementation
- full RegexJudge implementation
- Pydantic schema completion
- ClassifierJudge implementation
- LLMJudge implementation
- TraceCheckJudge implementation
- attack generation, harness execution, or archive mutation

## Open Design Points

- evidence schema fields and redaction guarantees
- default rubric thresholds and decision caps
- model-assisted verification hooks
- calibration protocol and human-label workflow
- reward-hacking review workflow
