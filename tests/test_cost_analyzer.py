
"""Tests for HumanOps AI financial optimization engine."""

import pytest

from services.cost_analyzer import (
    analyze_costs,
    load_infrastructure,
)


def test_infrastructure_inventory():
    inventory = load_infrastructure()

    assert not inventory.empty

    required = {
        "resource_id",
        "resource_name",
        "category",
        "environment",
        "monthly_cost",
        "optimized_cost",
        "cpu_p95",
        "memory_p95",
    }

    assert required.issubset(inventory.columns)


def test_default_current_cost():
    result = analyze_costs()

    assert result["current_cost"] == pytest.approx(50000)


def test_default_optimized_cost():
    result = analyze_costs()

    assert result["optimized_cost"] == pytest.approx(34500)


def test_gross_monthly_savings():
    result = analyze_costs()

    assert result["gross_monthly_savings"] == pytest.approx(
        15500
    )


def test_net_monthly_savings():
    result = analyze_costs()

    assert result["net_monthly_savings"] == pytest.approx(
        15000
    )


def test_first_year_savings():
    result = analyze_costs()

    assert result["annual_net_savings"] == pytest.approx(
        177000
    )


def test_cost_reduction_percentage():
    result = analyze_costs()

    assert result["reduction_percent"] == pytest.approx(30)


def test_workforce_preservation():
    result = analyze_costs(employees=100)

    assert result["employees"] == 100
    assert result["planned_layoffs"] == 0
    assert result["workforce_retained_percent"] == 100


def test_equivalent_payroll_cost():
    result = analyze_costs(
        employee_monthly_cost=5000
    )

    assert result["equivalent_positions"] == pytest.approx(3)


def test_equivalent_positions_are_capped():
    result = analyze_costs(
        employees=1,
        employee_monthly_cost=1000,
    )

    assert result["equivalent_positions"] <= 1


def test_savings_target_achieved():
    result = analyze_costs(
        savings_target=15000
    )

    assert result["target_achieved"] is True
    assert result["target_gap"] == 0


def test_savings_target_not_achieved():
    result = analyze_costs(
        savings_target=16500
    )

    assert result["target_achieved"] is False
    assert result["target_gap"] == pytest.approx(1500)


def test_custom_ai_cost():
    result = analyze_costs(
        ai_monthly_cost=1000
    )

    assert result["net_monthly_savings"] == pytest.approx(
        14500
    )


def test_custom_implementation_cost():
    result = analyze_costs(
        implementation_cost=10000
    )

    assert result["annual_net_savings"] == pytest.approx(
        170000
    )


def test_negative_net_savings():
    result = analyze_costs(
        ai_monthly_cost=20000
    )

    assert result["net_monthly_savings"] < 0
    assert result["equivalent_positions"] == 0


@pytest.mark.parametrize(
    "parameters",
    [
        {"employees": 0},
        {"employees": -1},
        {"employee_monthly_cost": 0},
        {"employee_monthly_cost": -1000},
        {"ai_monthly_cost": -500},
        {"implementation_cost": -3000},
        {"savings_target": -1000},
    ],
)
def test_invalid_financial_parameters(parameters):
    with pytest.raises(ValueError):
        analyze_costs(**parameters)
