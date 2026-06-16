# APRT Judge/QC v0

APRT Judge/QC는 APRT(Automated Progressive Red Teaming) 구조에서 target
response를 평가해 `JudgeResult`를 생성하는 평가 모듈이다.

현재 저장소는 v0 초기 협업을 위한 skeleton과 최소 contract 모델을 포함한다.
설계는 아직 확정 명세가 아니며, calibration 데이터와 review 결과에 따라 교체
가능해야 한다.

## v0 목표

Judge/QC의 기본 흐름은 다음과 같다.

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

Judge/QC가 담당하는 범위:

- target response 평가
- evidence 생성, 검증, 정규화, 중복 제거
- rubric 기반 raw score 계산
- fitness 계산
- decision routing
- `JudgeResult` 생성
- calibration 및 reward-hacking review 문서화

Judge/QC가 담당하지 않는 범위:

- 공격 생성 또는 mutation operator 구현
- target 실행 또는 harness 구현
- archive add/sample 구현
- descriptor 분류
- evolution loop 또는 champion selection
- TraceCheckJudge 전체 구현

`AttackGenome`, `RunObservation`, `ArchiveEntry`는 APRT의 공유 객체다. 이
저장소에서는 해당 객체를 완전히 소유하지 않고, 필요할 때 최소 참조 타입만 둔다.

## 현재 포함된 것

- `aprt_judge/contracts/`: 최소 contract 모델
  - `Evidence`
  - `EvidenceContract`
  - `JudgeSpec`
  - `SuccessRubric`
  - `RawScores`
  - `JudgeResult`
- `aprt_judge/judge/`: pipeline 구성요소 placeholder
- `aprt_judge/judge/judges/`: Canary/Regex/Classifier/LLM judge placeholder
- `docs/architecture/judge_v0.md`: Judge/QC 책임 경계와 파이프라인 초안
- `docs/architecture/contracts_v0.md`: 최소 contract 모델 설명
- `docs/canary_blackbox_strategy.md`: CanaryJudge black-box 전략과 한계
- `tests/contracts/`: 최소 contract 검증 테스트

## 설계 원칙

- Judge는 Evidence만 생성한다.
- Fitness는 `FitnessCalculator`가 계산한다.
- Decision은 `DecisionRouter`가 생성한다.
- threshold, decision cap, judge 활성화 여부는 config/rubric/contract 기반으로
  조정 가능해야 한다.
- CanaryJudge를 단순 exact-match 최종 판정기로 고정하지 않는다.
- Evidence에는 plaintext secret 또는 raw canary value를 저장하지 않는다.
- Attack/Harness/Archive 책임을 Judge/QC 모듈로 끌어오지 않는다.

## 현재 구현하지 않은 것

- CanaryJudge / RegexJudge 실제 탐지 로직
- Pydantic 기반 전체 schema
- EvidenceValidator / RubricEvaluator 실제 로직
- FitnessCalculator / DecisionRouter 실제 로직
- ClassifierJudge / LLMJudge / TraceCheckJudge 구현
- Attack/Harness/Archive 객체의 완전 구현

## 검증

현재 `pytest`는 dev dependency로 선언되어 있지만 로컬 venv에 설치되어 있지 않을 수
있다. 최소 검증은 표준 라이브러리 기반으로 실행할 수 있다.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
.\.venv\Scripts\python.exe -m compileall aprt_judge tests
git diff --check
```

## 협업 규칙

- 공유 문서와 PR 설명은 기본적으로 한글로 작성한다.
- 개인용 `SKILL.md`, `.codex/`, `docs/workflow/`는 local-only 파일로 GitHub에
  올리지 않는다.
- commit, push, PR 생성은 사용자 승인 후 진행한다.
- 다음 작업자는 contracts 이후 `JudgeService`, `JudgeDispatcher`,
  `EvidenceValidator`, `RubricEvaluator`, `FitnessCalculator`,
  `DecisionRouter` 순서로 이어가면 된다.
