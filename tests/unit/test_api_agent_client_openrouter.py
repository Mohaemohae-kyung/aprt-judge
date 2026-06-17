"""Unit tests for the OpenRouter APIAgentClient."""

import asyncio
from io import BytesIO
import json
import os
import socket
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from aprt.clients import APIAgentClient
from aprt.utils.errors import InvalidRewardOutputError, RewardEvaluationError


def run(coro):
    return asyncio.run(coro)


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self) -> bytes:
        return self._body


class FakeOpenRouterClient(APIAgentClient):
    def __init__(self, response: FakeResponse | None = None, error: Exception | None = None) -> None:
        super().__init__(
            provider="openrouter",
            model_name="openrouter/test-model",
            openrouter_api_key="test-api-key",
        )
        self.response = response
        self.error = error
        self.last_request = None
        self.last_timeout = None

    def _open_url(self, request, timeout_sec):
        self.last_request = request
        self.last_timeout = timeout_sec
        if self.error:
            raise self.error
        return self.response


class APIAgentClientOpenRouterTests(unittest.TestCase):
    def test_openrouter_request_body_uses_model_and_strict_json_schema(self) -> None:
        client = APIAgentClient(model_name="openrouter/reward-model")

        body = client.build_openrouter_request_body("system", "user", 0.0)

        self.assertEqual(body["model"], "openrouter/reward-model")
        self.assertEqual(body["messages"][0], {"role": "system", "content": "system"})
        self.assertEqual(body["messages"][1], {"role": "user", "content": "user"})
        self.assertEqual(body["response_format"]["type"], "json_schema")
        schema = body["response_format"]["json_schema"]
        self.assertTrue(schema["strict"])
        self.assertFalse(schema["schema"]["additionalProperties"])
        self.assertEqual(schema["schema"]["required"], ["score", "label", "reason"])

    def test_missing_api_key_raises_evaluation_error(self) -> None:
        client = APIAgentClient(openrouter_api_key=None)

        with self.assertRaises(RewardEvaluationError) as context:
            run(client.complete_json("system", "user", 0.0, 1.0))

        self.assertEqual(context.exception.code, "missing_api_key")

    def test_unsupported_provider_raises_evaluation_error(self) -> None:
        client = APIAgentClient(provider="claude", openrouter_api_key="test-api-key")

        with self.assertRaises(RewardEvaluationError) as context:
            run(client.complete_json("system", "user", 0.0, 1.0))

        self.assertEqual(context.exception.code, "unsupported_provider")

    def test_complete_json_returns_model_content_dict(self) -> None:
        client = FakeOpenRouterClient(
            FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "score": 0.42,
                                        "label": "unsafe",
                                        "reason": "synthetic",
                                    }
                                )
                            }
                        }
                    ]
                }
            )
        )

        result = run(client.complete_json("system", "user", 0.0, 12.0))

        self.assertEqual(result["score"], 0.42)
        self.assertEqual(result["label"], "unsafe")
        self.assertEqual(client.last_timeout, 12.0)

    def test_invalid_json_content_maps_to_invalid_output(self) -> None:
        client = FakeOpenRouterClient(
            FakeResponse({"choices": [{"message": {"content": "not json"}}]})
        )

        with self.assertRaises(InvalidRewardOutputError) as context:
            run(client.complete_json("system", "user", 0.0, 1.0))

        self.assertEqual(context.exception.code, "invalid_json")

    def test_timeout_maps_to_timeout_error(self) -> None:
        client = FakeOpenRouterClient(error=socket.timeout("timed out"))

        with self.assertRaises(TimeoutError):
            run(client.complete_json("system", "user", 0.0, 1.0))

    def test_rate_limit_maps_to_reward_evaluation_error(self) -> None:
        error = HTTPError(
            url="https://openrouter.ai/api/v1/chat/completions",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=BytesIO(b"{}"),
        )
        client = FakeOpenRouterClient(error=error)

        with self.assertRaises(RewardEvaluationError) as context:
            run(client.complete_json("system", "user", 0.0, 1.0))

        self.assertEqual(context.exception.code, "rate_limited")

    def test_safety_and_helpfulness_models_are_split_by_env(self) -> None:
        env = {
            "REWARD_LLM_PROVIDER": "openrouter",
            "OPENROUTER_API_KEY": "test-api-key",
            "REWARD_LLM_SAFETY_MODEL": "openrouter/safety-model",
            "REWARD_LLM_HELPFULNESS_MODEL": "openrouter/helpfulness-model",
        }
        with patch.dict(os.environ, env, clear=False):
            safety_client = APIAgentClient.from_env_for_role("safety")
            helpfulness_client = APIAgentClient.from_env_for_role("helpfulness")

        self.assertEqual(safety_client.openrouter_api_key, "test-api-key")
        self.assertEqual(helpfulness_client.openrouter_api_key, "test-api-key")
        self.assertEqual(safety_client.model_name, "openrouter/safety-model")
        self.assertEqual(helpfulness_client.model_name, "openrouter/helpfulness-model")


if __name__ == "__main__":
    unittest.main()
