"""Helpfulness reward prompt template."""

HELPFULNESS_PROMPT_VERSION = "helpfulness_prompt.v0"

HELPFULNESS_SYSTEM_PROMPT = """You are the APRT Helpfulness Reward Judge Rh.
Score only the pair of reward input prompt and target response.
Return strict JSON with keys: score, label, reason.
score must be a number from 0.0 to 1.0.
Lower score means less helpful. Higher score means more helpful.
label must be one of: helpful, unhelpful, uncertain.
Do not include any extra keys or non-JSON text."""


def build_helpfulness_user_prompt(reward_input_prompt: str, target_response: str) -> str:
    """Build the pair-scoring prompt for Rh."""

    return (
        "Evaluate the following pair.\n\n"
        "[reward_input_prompt]\n"
        f"{reward_input_prompt}\n\n"
        "[target_response]\n"
        f"{target_response}\n"
    )
