"""Safety Reward Judge Rs."""

from dataclasses import dataclass

from aprt.clients.agent_client import AgentClient
from aprt.contracts.reward_spec import RewardSpec
from aprt.reward.judges.types import RewardJudgeOutput
from aprt.reward.prompts.safety_prompt import (
    SAFETY_PROMPT_VERSION,
    SAFETY_SYSTEM_PROMPT,
    build_safety_user_prompt,
)
from aprt.utils.errors import InvalidRewardOutputError
from aprt.utils.json_utils import require_json_object, require_label, require_score

SAFETY_LABELS = {"safe", "unsafe", "uncertain"}


@dataclass(slots=True)
class SafetyRewardJudge:
    """Score `(reward_input_prompt, target_response)` for safety."""

    reward_id: str
    client: AgentClient
    prompt_version: str = SAFETY_PROMPT_VERSION

    async def score_pair(
        self,
        reward_input_prompt: str,
        target_response: str,
        spec: RewardSpec,
    ) -> RewardJudgeOutput:
        user_prompt = build_safety_user_prompt(reward_input_prompt, target_response)
        last_error: Exception | None = None
        invalid_attempts = 0
        api_attempts = 0

        while invalid_attempts <= spec.json_parse_retries and api_attempts <= spec.max_retries:
            try:
                raw = await self.client.complete_json(
                    system_prompt=SAFETY_SYSTEM_PROMPT,
                    user_prompt=user_prompt,
                    temperature=spec.temperature,
                    timeout_sec=spec.timeout_sec,
                )
                payload = require_json_object(raw, self.reward_id)
                score = require_score(payload, self.reward_id)
                label = require_label(payload, SAFETY_LABELS, self.reward_id)
                reason = str(payload.get("reason", ""))
                return RewardJudgeOutput(self.reward_id, score, label, reason, payload)
            except InvalidRewardOutputError as exc:
                invalid_attempts += 1
                last_error = exc
            except Exception as exc:
                api_attempts += 1
                last_error = exc

        if isinstance(last_error, InvalidRewardOutputError):
            raise last_error
        if last_error is not None:
            raise last_error
        raise InvalidRewardOutputError("invalid safety reward output")
