# APRT Judge/QC v0 Contract 모델

이 문서는 v0 초기 협업을 위해 추가한 최소 contract 모델을 설명한다. 현재 모델은
pipeline 구현을 고정하기 위한 것이 아니라, Judge/QC 경계를 팀원이 같은 방식으로
이해하도록 돕기 위한 출발점이다.

## 구현 방향

현재 contract는 `frozen dataclass` 기반이다.

Pydantic 전체 schema는 아직 도입하지 않았다. v0 초반에는 모델의 책임 경계와
불변성, secret-safe evidence 규칙을 먼저 확인하고, 입출력 검증 요구가 구체화되면
Pydantic으로 확장할 수 있다.

## 주요 모델

### `JudgeSpec`

교체 가능한 judge의 최소 설정 단위다.

- `judge_id`
- `judge_type`
- `enabled`
- `weight`
- `config`

Judge 활성화 여부와 세부 설정은 코드에 하드코딩하지 않고 spec 또는 rubric 계층에서
조정할 수 있어야 한다.

### `Evidence`

Judge가 생성하는 secret-safe signal이다.

- `evidence_id`
- `kind`
- `judge_id`
- `detector_mode`
- `confidence`
- `verification_class`
- `matched_ref`
- `locator`
- `redacted_summary`
- `metadata`

`Evidence`는 최종 decision이나 fitness를 담지 않는다. 또한 plaintext secret,
raw canary value처럼 원문 민감값을 저장하지 않는다.

### `EvidenceContract`

Evidence validation 정책의 최소 단위다. 현재는 raw secret/canary 저장을 막기 위한
forbidden metadata key 목록과 redacted summary 요구 여부를 담는다.

### `SuccessRubric`

rubric 기반 평가와 routing을 위한 설정 단위다.

- `rubric_id`
- `version`
- `goal`
- `score_weights`
- `thresholds`
- `decision_caps`
- `enabled_judges`

threshold와 decision cap은 하드코딩하지 않고 rubric에서 조정할 수 있어야 한다.

### `RawScores`

`RubricEvaluator`가 생성하고 `FitnessCalculator`가 소비하는 raw score 묶음이다.
fitness 계산 전 단계이므로 최종 decision을 담지 않는다.

### `JudgeResult`

Judge/QC pipeline의 최종 출력이다.

- `result_id`
- `observation_ref`
- `rubric_id`
- `decision`
- `fitness`
- `raw_scores`
- `evidence`
- `reasons`
- `metadata`

`JudgeResult`는 `raw_scores.rubric_id`와 자신의 `rubric_id`가 일치해야 한다.

## 현재 테스트

`tests/contracts/test_contracts.py`는 다음을 검증한다.

- Evidence metadata가 불변으로 저장되는지
- raw secret/canary key가 거부되는지
- JudgeSpec이 교체 가능한 judge 설정을 담는지
- SuccessRubric, RawScores, JudgeResult가 rubric id 기준으로 연결되는지
- JudgeResult가 rubric mismatch를 거부하는지

## 다음 작업

다음 단계는 contract를 소비하는 pipeline skeleton을 작은 단위로 채우는 것이다.

권장 순서:

1. `Judge` interface와 judge output 타입 정리
2. `JudgeDispatcher`가 enabled judge를 호출하는 최소 흐름 구현
3. `EvidenceValidator`가 `EvidenceContract`를 사용해 evidence를 검증
4. `RubricEvaluator`가 evidence를 `RawScores`로 변환
5. `FitnessCalculator`와 `DecisionRouter`는 최소 정책만 둔 뒤 calibration 결과에 맞춰 확장
