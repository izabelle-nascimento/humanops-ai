
"""Integration tests for HumanOps AI business scenarios."""

import inspect
from pathlib import Path
from unittest.mock import Mock

import pytest

from streamlit.testing.v1 import AppTest

from services.cost_analyzer import analyze_costs
from services.scenario_simulator import simulate_black_friday
from services.ai_optimizer import build_business_context
from views.black_friday_dashboard import render_black_friday

import views.ai_dashboard as ai_dashboard


# ==========================================================
# APPLICATION PATH
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
APP_FILE = BASE_DIR / "app.py"


# ==========================================================
# BUSINESS INTEGRATION
# ==========================================================

def test_dashboard_function_compatibility():

    signature = inspect.signature(
        render_black_friday
    )

    signature.bind(financial_data={})


def test_combined_default_financial_projection():

    financial = analyze_costs()
    capacity = simulate_black_friday()

    scaling_cost = capacity["total_event_scaling_cost"]

    event_savings = (
        financial["net_monthly_savings"]
        - scaling_cost
    )

    annual_savings = (
        financial["annual_net_savings"]
        - scaling_cost
    )

    assert event_savings == pytest.approx(
        13586.67,
        abs=0.01,
    )

    assert annual_savings == pytest.approx(
        175586.67,
        abs=0.01,
    )


def test_shared_workforce_constraint():

    financial = analyze_costs(employees=100)
    capacity = simulate_black_friday()

    context = build_business_context(
        financial,
        capacity,
    )

    assert context["financial_analysis"]["employees"] == 100

    assert financial["planned_layoffs"] == 0
    assert capacity["planned_layoffs"] == 0
    assert context["constraints"]["planned_layoffs"] == 0


def test_custom_financial_projection():

    financial = analyze_costs(
        employees=100,
        ai_monthly_cost=1000,
    )

    capacity = simulate_black_friday()

    adjusted = (
        financial["annual_net_savings"]
        - capacity["total_event_scaling_cost"]
    )

    assert adjusted == pytest.approx(
        169586.67,
        abs=0.01,
    )


# ==========================================================
# MOCK LOCAL AI
# ==========================================================

@pytest.fixture
def mock_ai(monkeypatch):

    status = Mock(
        return_value={
            "online": True,
            "model_available": True,
            "model": "qwen2.5:7b",
        }
    )

    resources = Mock(
        return_value={
            "ready": True,
            "available_ram_gb": 16.0,
            "minimum_ram_gb": 10,
        }
    )

    generation = Mock(
        return_value={
            "model": "qwen2.5:7b",
            "provider": "Ollama Local",
            "recommendation": (
                "### Executive Summary\n\n"
                "Optimize infrastructure resources "
                "while preserving the workforce."
            ),
            "generation_time_seconds": 2.5,
            "generated_tokens": 120,
            "human_approval_required": True,
        }
    )

    monkeypatch.setattr(
        ai_dashboard,
        "check_ollama",
        status,
    )

    monkeypatch.setattr(
        ai_dashboard,
        "check_ai_resources",
        resources,
    )

    monkeypatch.setattr(
        ai_dashboard,
        "generate_recommendations",
        generation,
    )

    return {
        "status": status,
        "resources": resources,
        "generation": generation,
    }


# ==========================================================
# STREAMLIT FIXTURE
# ==========================================================

@pytest.fixture
def app(mock_ai):

    assert APP_FILE.is_file()

    application = AppTest.from_file(
        str(APP_FILE),
        default_timeout=60,
    )

    application.run()

    assert not application.exception

    return application


# ==========================================================
# TEST HELPERS
# ==========================================================

def find_widget(widgets, label):

    return next(
        widget
        for widget in widgets
        if widget.label == label
    )


def metric_values(app, label):

    return [
        metric.value
        for metric in app.metric
        if metric.label == label
    ]


def generate_analysis(app):

    button = find_widget(
        app.button,
        "Generate Strategic Analysis",
    )

    button.click()
    app.run()

    assert not app.exception


# ==========================================================
# APPLICATION TESTS
# ==========================================================

def test_application_starts(app):

    assert not app.exception


def test_application_tabs(app):

    expected = {
        "Overview",
        "Infrastructure",
        "FinOps",
        "Black Friday",
        "AI Advisor",
    }

    actual = {
        tab.label
        for tab in app.tabs
    }

    assert expected.issubset(actual)


def test_default_financial_metrics(app):

    assert metric_values(
        app,
        "Monthly Baseline Savings",
    ) == ["R$ 15.000,00"]

    assert metric_values(
        app,
        "Adjusted First-Year Savings",
    ) == [
        "R$ 175.586,67",
        "R$ 175.586,67",
    ]


def test_dashboard_synchronization(app):

    employees = find_widget(
        app.number_input,
        "Total Employees",
    )

    ai_cost = find_widget(
        app.number_input,
        "Monthly AI Cost (BRL)",
    )

    employees.set_value(100)
    ai_cost.set_value(1000)

    app.run()

    assert not app.exception

    assert metric_values(
        app,
        "Workforce Retained (Scenario)",
    ) == ["100/100"]

    assert metric_values(
        app,
        "Workforce Retained",
    ) == ["100/100", "100/100"]

    assert metric_values(
        app,
        "Monthly Baseline Savings",
    ) == ["R$ 14.500,00"]

    assert metric_values(
        app,
        "Adjusted First-Year Savings",
    ) == [
        "R$ 169.586,67",
        "R$ 169.586,67",
    ]

    assert metric_values(
        app,
        "Event Month Net Savings",
    ) == [
        "R$ 13.086,67",
        "R$ 13.086,67",
    ]


def test_financial_target_warning(app):

    target = find_widget(
        app.number_input,
        "Monthly Savings Target (BRL)",
    )

    target.set_value(20000)
    app.run()

    assert not app.exception

    assert any(
        "Additional monthly savings required"
        in warning.value
        for warning in app.warning
    )


# ==========================================================
# BLACK FRIDAY DASHBOARD TESTS
# ==========================================================

def test_critical_capacity_warning(app):

    assert any(
        "CRITICAL" in error.value
        for error in app.error
    )


def test_capacity_within_threshold(app):

    capacity = find_widget(
        app.slider,
        "Available Capacity Multiplier",
    )

    capacity.set_value(3.0)
    app.run()

    assert not app.exception

    assert any(
        "within the configured" in message.value
        for message in app.success
    )


def test_capacity_adjustment_warning(app):

    capacity = find_widget(
        app.slider,
        "Available Capacity Multiplier",
    )

    capacity.set_value(1.5)
    app.run()

    assert not app.exception

    assert any(
        "Capacity adjustments are recommended"
        in warning.value
        for warning in app.warning
    )


def test_campaign_updates_financial_metrics(app):

    original = metric_values(
        app,
        "Black Friday Scaling Cost",
    )[0]

    demand = find_widget(
        app.slider,
        "Expected Traffic Multiplier",
    )

    demand.set_value(4.0)
    app.run()

    assert not app.exception

    updated = metric_values(
        app,
        "Black Friday Scaling Cost",
    )[0]

    assert original != updated


# ==========================================================
# AI DASHBOARD TESTS
# ==========================================================

def test_ai_online(app):

    assert any(
        "LOCAL AI ONLINE" in message.value
        for message in app.success
    )

    button = find_widget(
        app.button,
        "Generate Strategic Analysis",
    )

    assert not button.disabled


def test_ai_offline(app, mock_ai):

    mock_ai["status"].return_value = {
        "online": False,
        "model_available": False,
    }

    app.run()

    assert not app.exception

    assert any(
        "Local AI service or model unavailable"
        in error.value
        for error in app.error
    )

    button = find_widget(
        app.button,
        "Generate Strategic Analysis",
    )

    assert button.disabled


def test_ai_insufficient_memory(app, mock_ai):

    mock_ai["resources"].return_value = {
        "ready": False,
        "available_ram_gb": 4.0,
        "minimum_ram_gb": 10,
    }

    app.run()

    assert not app.exception

    assert any(
        "Insufficient available RAM"
        in warning.value
        for warning in app.warning
    )

    button = find_widget(
        app.button,
        "Generate Strategic Analysis",
    )

    assert button.disabled


def test_ai_report_generation(app, mock_ai):

    generate_analysis(app)

    mock_ai["generation"].assert_called_once()

    assert (
        app.session_state["ai_analysis"]["model"]
        == "qwen2.5:7b"
    )

    assert metric_values(
        app,
        "Human Approval",
    ) == ["Required"]

    assert metric_values(
        app,
        "Generation Time",
    ) == ["2.50s"]

    assert metric_values(
        app,
        "Generated Tokens",
    ) == ["120"]


def test_ai_receives_updated_financial_context(
    app,
    mock_ai,
):

    employees = find_widget(
        app.number_input,
        "Total Employees",
    )

    employees.set_value(100)
    app.run()

    generate_analysis(app)

    arguments = (
        mock_ai["generation"].call_args.kwargs
    )

    assert (
        arguments["financial_data"]["employees"]
        == 100
    )

    assert (
        arguments["capacity_data"]
        ["financial_impact"]["employees"]
        == 100
    )

    assert (
        arguments["financial_data"]["planned_layoffs"]
        == 0
    )


def test_ai_detects_outdated_analysis(app):

    generate_analysis(app)

    employees = find_widget(
        app.number_input,
        "Total Employees",
    )

    employees.set_value(100)
    app.run()

    assert not app.exception

    assert any(
        "Scenario parameters have changed"
        in warning.value
        for warning in app.warning
    )


def test_ai_generation_error(app, mock_ai):

    mock_ai["generation"].side_effect = RuntimeError(
        "Simulated AI generation failure."
    )

    generate_analysis(app)

    assert any(
        "Simulated AI generation failure"
        in error.value
        for error in app.error
    )
