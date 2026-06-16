# Reward Judge 보안 / 데이터 정책

이 문서는 APRT Reward Judge Core에서 fixture, 평가 데이터, 로그, API 전송 데이터를
다룰 때의 기본 원칙을 정리한다.

## Repository에 저장 가능한 데이터

- synthetic placeholder
- redacted sample
- schema 또는 예시 구조
- 실행 가능한 위험 payload가 없는 smoke fixture

Repository에는 실제 위험한 구체 payload, 내부 prompt, 민감한 target response,
provider raw transcript를 저장하지 않는다.

## Private storage 전제 데이터

실제 human-labeled evaluation set은 repository 밖 private storage에 둔다. 해당
데이터를 사용할 때는 별도 접근 제어, 보관 위치, 삭제 절차, provider 전송 허용 여부를
팀이 명시적으로 결정해야 한다.

## 로그와 raw output

- `reward_input_prompt` 전문을 기본 로그에 남기지 않는다.
- `target_response` 전문을 기본 로그에 남기지 않는다.
- 필요한 경우 hash, 길이, 짧은 redacted preview만 남긴다.
- `raw_outputs`는 Reward LLM의 strict JSON 결과를 디버깅용으로 보존할 수 있지만,
  provider raw text 전문 저장은 명시적 opt-in으로만 다룬다.

## API provider 전송 주의

APRT Reward Judge는 `reward_input_prompt`와 `target_response` pair를 provider로
전송할 수 있다. 실제 데이터 사용 전에는 provider의 데이터 보관, 학습 사용 여부,
retention 설정, enterprise/privacy 옵션을 팀이 확인해야 한다.

## Fixture 이름과 예시 정책

공유 repository의 fixture는 synthetic 또는 smoke 성격이 드러나는 이름을 사용한다.
실제 evaluation set처럼 보이는 이름은 사용하지 않는다.

현재 synthetic smoke fixture:

```text
tests/fixtures/reward_synthetic_smoke_set.json
```

실제 데이터로 보일 수 있는 파일명이나 민감 데이터 저장 경로는 `.gitignore`에서
차단한다.
