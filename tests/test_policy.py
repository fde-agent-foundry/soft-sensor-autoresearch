from __future__ import annotations

import pytest

from soft_sensor_autoresearch.policy import PolicyContractError, build_policy


def request() -> dict:
    return {
        "schema_version": "autoresearch-policy-input/v1",
        "study_id": "soft-001",
        "task_type": "soft_sensing",
        "input_asset_id": "asset-1",
        "input_asset_sha256": "a" * 64,
        "target_column": "quality",
        "target_definition_ref": "D02/target",
        "target_definition_sha256": "b" * 64,
        "acceptance_ref": "D02/acceptance",
        "acceptance_sha256": "c" * 64,
        "input_pool": ["feed", "temperature", "pressure"],
        "windows": [{"window_id": "w1"}, {"window_id": "w2"}],
        "forecast_horizons": [0, 2],
        "enable_input_ablation": True,
        "budget": {"max_candidates": 4, "max_kernel_executions": 8},
    }


def test_policy_is_bounded_and_stops_for_engineer_selection() -> None:
    result = build_policy(request())
    assert result["status"] == "needs_human"
    assert len(result["candidates"]) == 4
    assert result["next_actions"][-1]["code"] == "await_data_modeling_engineer_selection"


def test_policy_rejects_target_leakage() -> None:
    contract = request()
    contract["input_pool"].append("quality")
    with pytest.raises(PolicyContractError, match="target leakage"):
        build_policy(contract)


def test_policy_requires_self_consistency_windows() -> None:
    contract = request()
    contract["windows"] = [{"window_id": "w1"}]
    with pytest.raises(PolicyContractError, match="self-consistency"):
        build_policy(contract)
