"""Adapters for external APRT objects.

External selector, target execution, and archive types are intentionally outside
the Reward Judge Core.
"""

from aprt.adapters.judge_result_adapter import (
    reward_result_to_external_dict,
    reward_result_to_judge_result_like,
    reward_results_to_external_dicts,
)

__all__ = [
    "reward_result_to_external_dict",
    "reward_result_to_judge_result_like",
    "reward_results_to_external_dicts",
]

