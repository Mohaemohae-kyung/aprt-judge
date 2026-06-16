# APRT Judge/QC v0 아키텍처

이 문서는 APRT Judge/QC v0 스켈레톤의 작업 초안이다. 현재 설계는 확정
명세가 아니며, calibration 데이터와 review 결과가 쌓이면 교체하거나 조정할 수
있어야 한다.

## 목표

Judge/QC는 target response를 평가해 `JudgeResult`를 생성한다. 공격 생성,
target 실행, archive 관리, evolution loop 실행은 Judge/QC의 책임이 아니다.

## 파이프라인

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

## 책임 분리

Judge들은 evidence producer이다. seeded marker, canary-like marker, regex
match, 기타 signal을 탐지할 수 있지만 최종 fitness나 최종 decision을 직접
계산하지 않는다.

`EvidenceValidator`는 evidence를 검증, 정규화, redaction, 중복 제거한다.
이 계층은 secret-safe storage를 포함한 evidence contract를 강제해야 한다.

`RubricEvaluator`는 검증된 evidence를 rubric 기반 raw score로 변환한다.

`FitnessCalculator`는 raw score를 fitness로 변환한다.

`DecisionRouter`는 threshold, decision cap, 정책 제약을 적용해 최종 decision을
생성한다.

## 외부 경계

`AttackGenome`, `RunObservation`, `ArchiveEntry`는 이 패키지 밖에서 소유하는
공유 APRT 객체다. 이 저장소는 최소 참조 타입을 정의할 수 있지만, attack,
harness, archive, descriptor, evolution 동작 전체를 소유하면 안 된다.

## v0 비목표

- CanaryJudge 전체 구현
- RegexJudge 전체 구현
- Pydantic schema 완성
- ClassifierJudge 구현
- LLMJudge 구현
- TraceCheckJudge 구현
- attack generation, harness execution, archive mutation

## 열려 있는 설계 지점

- evidence schema 필드와 redaction 보장 방식
- 기본 rubric threshold와 decision cap
- model-assisted verification hook
- calibration protocol과 human-label workflow
- reward-hacking review workflow

## 현재 협업 상태

현재 저장소에는 Judge/QC v0 skeleton과 최소 contract 모델이 있다. 실제
CanaryJudge/RegexJudge 탐지 로직, scoring 로직, fitness 계산, decision routing은
아직 구현하지 않았다.

다음 작업자는 `docs/architecture/contracts_v0.md`의 contract 모델을 기준으로
`JudgeDispatcher`, `EvidenceValidator`, `RubricEvaluator`, `FitnessCalculator`,
`DecisionRouter` 순서로 pipeline을 채워 나가면 된다.
