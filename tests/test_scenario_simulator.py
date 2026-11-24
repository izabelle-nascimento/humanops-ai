
"""Tests for HumanOps AI capacity planning simulator."""

import pytest

from services.scenario_simulator import (
    simulate_black_friday,
)


def test_default_scenario():
    result = simulate_black_friday()

    assert result["demand_multiplier"] == 2.0
    assert result["capacity_multiplier"] == 1.0
    assert result["event_days"] == 5
    assert result["utilization_target"] == 70


def test_production_servers():
    result = simulate_black_friday()

    assert result["servers_analyzed"] == 3
    assert len(result["resources"]) == 3


def test_critical_server_detection():
    result = simulate_black_friday()

    assert result["critical_servers"] == 1


def test_default_scaling_cost():
    result = simulate_black_friday()

    assert result["total_event_scaling_cost"] == pytest.approx(
        1413.33,
        abs=0.01,
    )


def test_projected_cpu():
    result = simulate_black_friday()

    web_server = next(
        resource
        for resource in result["resources"]
        if resource["resource_id"] == "VM001"
    )

    assert web_server["projected_cpu"] == pytest.approx(144)


def test_required_capacity():
    result = simulate_black_friday()

    web_server = next(
        resource
        for resource in result["resources"]
        if resource["resource_id"] == "VM001"
    )

    assert web_server["required_capacity"] == pytest.approx(
        2.06
    )


def test_increased_capacity_reduces_risk():
    baseline = simulate_black_friday(
        capacity_multiplier=1.0
    )

    expanded = simulate_black_friday(
        capacity_multiplier=3.0
    )

    assert (
        expanded["critical_servers"]
        < baseline["critical_servers"]
    )


def test_increased_demand_increases_scaling_cost():
    baseline = simulate_black_friday(
        demand_multiplier=2.0
    )

    increased = simulate_black_friday(
        demand_multiplier=4.0
    )

    assert (
        increased["total_event_scaling_cost"]
        > baseline["total_event_scaling_cost"]
    )


def test_longer_campaign_increases_cost():
    short = simulate_black_friday(event_days=5)
    long = simulate_black_friday(event_days=10)

    assert long["total_event_scaling_cost"] == pytest.approx(
        short["total_event_scaling_cost"] * 2,
        abs=0.02,
    )


def test_total_scaling_cost_consistency():
    result = simulate_black_friday(
        capacity_multiplier=1.5
    )

    expected = (
        result["selected_capacity_cost"]
        + result["additional_event_cost"]
    )

    assert result["total_event_scaling_cost"] == pytest.approx(
        expected
    )


def test_workforce_preservation():
    result = simulate_black_friday(
        demand_multiplier=5.0
    )

    assert result["planned_layoffs"] == 0


def test_scaling_cost_is_non_negative():
    result = simulate_black_friday()

    for resource in result["resources"]:
        assert resource["selected_capacity_cost"] >= 0
        assert resource["additional_event_cost"] >= 0


@pytest.mark.parametrize(
    "parameters",
    [
        {"demand_multiplier": 0.5},
        {"capacity_multiplier": 0.5},
        {"event_days": 0},
        {"event_days": 31},
        {"utilization_target": 0},
        {"utilization_target": 101},
    ],
)
def test_invalid_capacity_parameters(parameters):
    with pytest.raises(ValueError):
        simulate_black_friday(**parameters)
