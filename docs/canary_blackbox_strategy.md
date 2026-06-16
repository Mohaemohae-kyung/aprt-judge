# Canary Black-Box 전략

이 문서는 APRT Judge/QC v0에서 CanaryJudge가 가져야 할 초기 설계 경계를
정리한다. 현재 내용은 초안이며, calibration과 review 데이터가 쌓이면 조정할 수
있어야 한다.

## 원칙

CanaryJudge는 target response 안의 seeded marker 또는 canary-like marker를
탐지하고 evidence를 생성해야 한다. CanaryJudge가 response를 confirmed finding으로
직접 확정해서는 안 된다.

Black-box 환경에서 문자열 match는 보호 대상 system text, 내부 정책, 민감 정보가
실제로 유출되었다는 증거가 아닐 수 있다. 해당 marker는 synthetic marker이거나,
미리 심어 둔 seeded marker이거나, 변형/인용된 문자열이거나, 현재 attack goal과
무관한 문자열일 수 있다.

## Evidence 역할

Canary evidence는 다음과 같은 안전한 metadata를 기록해야 한다.

- matched reference identifier
- response locator
- detector mode
- confidence
- verification class
- redacted match summary

Evidence에는 plaintext secret 또는 raw canary value를 저장하지 않는다.

## 보류해야 하는 판단

다음 판단은 low-level detector가 아니라 별도 계층 또는 이후의 model-assisted
verification 계층에서 다루어야 한다.

- 해당 marker가 실제 보호 대상인지
- 해당 노출이 현재 attack goal과 관련 있는지
- 해당 결과를 finding candidate로 올릴 수 있는지
- semantic review 또는 human review가 필요한지

## v0 방향

v0에서 CanaryJudge는 exact match, prefix/pattern match, synthetic marker
reference를 지원할 수 있는 교체 가능한 detector로 남아야 한다. 최종 scoring,
fitness, decision은 rubric과 routing pipeline에 남겨야 한다.
