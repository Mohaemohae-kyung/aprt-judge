# Canary / Evidence Detector 전략 보류 메모

현재 구현 방향은 APRT 논문 기반 Reward Judge Core이다. 따라서 CanaryJudge,
RegexJudge, ClassifierJudge, Evidence detector는 이번 구현 범위에서 제외한다.

이 문서는 이전 generic Judge/QC 논의의 흔적을 보존하되, 현재 core의 구현 기준이
아님을 명확히 하기 위한 보류 메모다.

## 현재 상태

- CanaryJudge는 구현하지 않는다.
- RegexJudge는 구현하지 않는다.
- Evidence detector는 구현하지 않는다.
- RewardService는 canary/evidence가 아니라 `reward_input_prompt`와
  `target_response` pair를 Rs/Rh에 전달한다.

## 이후 다시 논의할 때의 원칙

나중에 evidence detector 계층을 별도 모듈로 재개하더라도 다음 원칙은 유지해야 한다.

- detector는 evidence만 생성한다.
- detector가 최종 fitness나 decision을 직접 만들지 않는다.
- plaintext secret 또는 raw canary value를 저장하지 않는다.
- Canary match만으로 confirmed finding을 확정하지 않는다.

현재 PR의 acceptance criteria에는 CanaryJudge 관련 구현이 포함되지 않는다.
