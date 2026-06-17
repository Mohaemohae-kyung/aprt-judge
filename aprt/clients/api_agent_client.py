"""Environment-configured API AgentClient for OpenRouter."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import json
import os
import socket
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from aprt.clients.agent_client import AgentClient
from aprt.utils.errors import InvalidRewardOutputError, RewardEvaluationError

OPENROUTER_DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_APP_TITLE = "APRT Reward Judge"

REWARD_OUTPUT_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["score", "label", "reason"],
    "properties": {
        "score": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
        },
        "label": {
            "type": "string",
            "enum": ["safe", "unsafe", "uncertain", "helpful", "unhelpful"],
        },
        "reason": {
            "type": "string",
        },
    },
}


@dataclass(slots=True)
class APIAgentClient(AgentClient):
    """OpenRouter-backed reward LLM client.

    Retry orchestration stays in SafetyRewardJudge/HelpfulnessRewardJudge through
    RewardSpec. This client performs one provider call per complete_json call.
    """

    provider: str = "openrouter"
    model_name: str = "reward-llm"
    timeout_sec: float = 30.0
    max_retries: int = 1
    openrouter_api_key: str | None = None
    openrouter_base_url: str = OPENROUTER_DEFAULT_BASE_URL
    openrouter_http_referer: str | None = None
    openrouter_app_title: str = OPENROUTER_DEFAULT_APP_TITLE
    model_version: str = "api"

    @classmethod
    def from_env(
        cls,
        *,
        model_name: str | None = None,
        model_env_var: str = "REWARD_LLM_MODEL",
    ) -> "APIAgentClient":
        """Create an API client config from environment variables."""

        selected_model = (
            model_name
            or os.getenv(model_env_var)
            or os.getenv("REWARD_LLM_MODEL")
            or "reward-llm"
        )
        return cls(
            provider=os.getenv("REWARD_LLM_PROVIDER", "openrouter"),
            model_name=selected_model,
            timeout_sec=float(os.getenv("REWARD_LLM_TIMEOUT_SEC", "30")),
            max_retries=int(os.getenv("REWARD_LLM_MAX_RETRIES", "1")),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
            openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", OPENROUTER_DEFAULT_BASE_URL),
            openrouter_http_referer=os.getenv("OPENROUTER_HTTP_REFERER") or None,
            openrouter_app_title=os.getenv("OPENROUTER_APP_TITLE", OPENROUTER_DEFAULT_APP_TITLE),
        )

    @classmethod
    def from_env_for_role(cls, role: str) -> "APIAgentClient":
        """Create a role-specific client for Rs or Rh model separation."""

        normalized = role.lower()
        if normalized == "safety":
            return cls.from_env(model_env_var="REWARD_LLM_SAFETY_MODEL")
        if normalized == "helpfulness":
            return cls.from_env(model_env_var="REWARD_LLM_HELPFULNESS_MODEL")
        raise ValueError("role must be safety or helpfulness")

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        timeout_sec: float,
    ) -> dict[str, Any]:
        """Call OpenRouter chat completions and return a strict JSON object."""

        return await asyncio.to_thread(
            self._complete_json_sync,
            system_prompt,
            user_prompt,
            temperature,
            timeout_sec,
        )

    def _complete_json_sync(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        timeout_sec: float,
    ) -> dict[str, Any]:
        if self.provider != "openrouter":
            raise RewardEvaluationError(
                f"Unsupported reward LLM provider: {self.provider}",
                code="unsupported_provider",
            )
        if not self.openrouter_api_key:
            raise RewardEvaluationError(
                "OPENROUTER_API_KEY is required for OpenRouter reward LLM calls",
                code="missing_api_key",
            )

        body = self.build_openrouter_request_body(system_prompt, user_prompt, temperature)
        request = Request(
            self._chat_completions_url(),
            data=json.dumps(body).encode("utf-8"),
            headers=self._openrouter_headers(),
            method="POST",
        )

        try:
            with self._open_url(request, timeout_sec or self.timeout_sec) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except TimeoutError:
            raise
        except socket.timeout as exc:
            raise TimeoutError("OpenRouter request timed out") from exc
        except HTTPError as exc:
            raise self._map_http_error(exc) from exc
        except URLError as exc:
            if isinstance(exc.reason, socket.timeout):
                raise TimeoutError("OpenRouter request timed out") from exc
            raise RewardEvaluationError(
                "OpenRouter request failed",
                code="provider_error",
            ) from exc
        except json.JSONDecodeError as exc:
            raise RewardEvaluationError(
                "OpenRouter response envelope was not valid JSON",
                code="provider_invalid_response",
            ) from exc

        content = self._extract_message_content(response_payload)
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            raise InvalidRewardOutputError(
                "OpenRouter reward content was not strict JSON",
                code="invalid_json",
            ) from exc
        if not isinstance(parsed, dict):
            raise InvalidRewardOutputError(
                "OpenRouter reward content was not a JSON object",
                code="invalid_json",
            )
        return parsed

    def build_openrouter_request_body(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
    ) -> dict[str, Any]:
        """Build the OpenRouter chat completions request body."""

        return {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "reward_judge_output",
                    "strict": True,
                    "schema": REWARD_OUTPUT_JSON_SCHEMA,
                },
            },
        }

    def _openrouter_headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        if self.openrouter_http_referer:
            headers["HTTP-Referer"] = self.openrouter_http_referer
        if self.openrouter_app_title:
            headers["X-OpenRouter-Title"] = self.openrouter_app_title
        return headers

    def _chat_completions_url(self) -> str:
        return f"{self.openrouter_base_url.rstrip('/')}/chat/completions"

    def _open_url(self, request: Request, timeout_sec: float):
        return urlopen(request, timeout=timeout_sec)

    def _map_http_error(self, exc: HTTPError) -> RewardEvaluationError:
        if exc.code == 401:
            code = "authentication_error"
        elif exc.code == 408:
            code = "timeout"
        elif exc.code == 429:
            code = "rate_limited"
        elif 500 <= exc.code <= 599:
            code = "provider_error"
        else:
            code = "provider_error"
        return RewardEvaluationError(
            f"OpenRouter request failed with HTTP {exc.code}",
            code=code,
        )

    def _extract_message_content(self, payload: dict[str, Any]) -> str:
        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RewardEvaluationError(
                "OpenRouter response envelope did not contain message content",
                code="provider_invalid_response",
            ) from exc
        if not isinstance(content, str):
            raise RewardEvaluationError(
                "OpenRouter message content was not a string",
                code="provider_invalid_response",
            )
        return content
