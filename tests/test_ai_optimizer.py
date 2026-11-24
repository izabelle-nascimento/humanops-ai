
"""Tests for HumanOps AI local AI integration."""

from unittest.mock import patch, Mock

import pytest
import requests

from services.ai_optimizer import (
    MODEL,
    MIN_AVAILABLE_RAM_GB,
    check_ai_resources,
    check_ollama,
    build_business_context,
    generate_recommendations,
)


@pytest.fixture
def financial_data():
    return {
        "employees": 50,
        "net_monthly_savings": 15000,
        "annual_net_savings": 177000,
        "planned_layoffs": 0,
    }


@pytest.fixture
def capacity_data():
    return {
        "critical_servers": 1,
        "total_event_scaling_cost": 1413.33,
        "planned_layoffs": 0,
    }


def test_model_configuration():
    assert MODEL == "qwen2.5:7b"


def test_minimum_memory_configuration():
    assert MIN_AVAILABLE_RAM_GB == 10


def test_available_memory():
    memory = Mock()
    memory.available = 16 * 1024 ** 3
    memory.total = 32 * 1024 ** 3
    memory.percent = 50

    with patch(
        "services.ai_optimizer.psutil.virtual_memory",
        return_value=memory,
    ):
        result = check_ai_resources()

    assert result["ready"] is True
    assert result["available_ram_gb"] == 16


def test_insufficient_memory():
    memory = Mock()
    memory.available = 4 * 1024 ** 3
    memory.total = 32 * 1024 ** 3
    memory.percent = 87.5

    with patch(
        "services.ai_optimizer.psutil.virtual_memory",
        return_value=memory,
    ):
        result = check_ai_resources()

    assert result["ready"] is False


def test_ollama_online():
    response = Mock()

    response.json.return_value = {
        "models": [{"name": MODEL}]
    }

    with patch(
        "services.ai_optimizer.requests.get",
        return_value=response,
    ):
        result = check_ollama()

    assert result["online"] is True
    assert result["model_available"] is True


def test_ollama_offline():
    with patch(
        "services.ai_optimizer.requests.get",
        side_effect=requests.ConnectionError,
    ):
        result = check_ollama()

    assert result["online"] is False
    assert result["model_available"] is False


def test_model_not_installed():
    response = Mock()

    response.json.return_value = {
        "models": []
    }

    with patch(
        "services.ai_optimizer.requests.get",
        return_value=response,
    ):
        result = check_ollama()

    assert result["online"] is True
    assert result["model_available"] is False


def test_business_context(financial_data, capacity_data):
    context = build_business_context(
        financial_data,
        capacity_data,
    )

    assert context["currency"] == "BRL"

    assert context["financial_analysis"] == financial_data

    assert (
        context["black_friday_simulation"]
        == capacity_data
    )


def test_ai_governance(financial_data, capacity_data):
    context = build_business_context(
        financial_data,
        capacity_data,
    )

    constraints = context["constraints"]

    assert constraints["planned_layoffs"] == 0
    assert constraints["human_approval_required"] is True
    assert constraints["corporate_data_is_simulated"] is True

    assert (
        constraints["autonomous_infrastructure_changes"]
        is False
    )


def test_successful_ai_generation(
    financial_data,
    capacity_data,
):
    response = Mock()

    response.json.return_value = {
        "response": "Optimize infrastructure costs.",
        "total_duration": 2000000000,
        "eval_count": 120,
        "prompt_eval_count": 500,
        "done_reason": "stop",
    }

    with (
        patch(
            "services.ai_optimizer.check_ollama",
            return_value={
                "online": True,
                "model_available": True,
            },
        ),
        patch(
            "services.ai_optimizer.check_ai_resources",
            return_value={"ready": True},
        ),
        patch(
            "services.ai_optimizer.requests.post",
            return_value=response,
        ) as post,
    ):
        result = generate_recommendations(
            financial_data,
            capacity_data,
        )

    assert result["model"] == MODEL
    assert result["currency"] == "BRL"
    assert result["api_fees_brl"] == 0
    assert result["generated_tokens"] == 120
    assert result["generation_time_seconds"] == 2
    assert result["human_approval_required"] is True

    payload = post.call_args.kwargs["json"]

    assert payload["keep_alive"] == 0
    assert payload["stream"] is False


def test_generation_when_ollama_offline(
    financial_data,
    capacity_data,
):
    with patch(
        "services.ai_optimizer.check_ollama",
        return_value={
            "online": False,
            "model_available": False,
        },
    ):
        with pytest.raises(RuntimeError, match="offline"):
            generate_recommendations(
                financial_data,
                capacity_data,
            )


def test_generation_without_model(
    financial_data,
    capacity_data,
):
    with patch(
        "services.ai_optimizer.check_ollama",
        return_value={
            "online": True,
            "model_available": False,
        },
    ):
        with pytest.raises(RuntimeError, match="not installed"):
            generate_recommendations(
                financial_data,
                capacity_data,
            )


def test_generation_with_insufficient_memory(
    financial_data,
    capacity_data,
):
    with (
        patch(
            "services.ai_optimizer.check_ollama",
            return_value={
                "online": True,
                "model_available": True,
            },
        ),
        patch(
            "services.ai_optimizer.check_ai_resources",
            return_value={
                "ready": False,
                "available_ram_gb": 4,
            },
        ),
    ):
        with pytest.raises(RuntimeError, match="Insufficient"):
            generate_recommendations(
                financial_data,
                capacity_data,
            )


def test_generation_timeout(
    financial_data,
    capacity_data,
):
    with (
        patch(
            "services.ai_optimizer.check_ollama",
            return_value={
                "online": True,
                "model_available": True,
            },
        ),
        patch(
            "services.ai_optimizer.check_ai_resources",
            return_value={"ready": True},
        ),
        patch(
            "services.ai_optimizer.requests.post",
            side_effect=requests.Timeout,
        ),
    ):
        with pytest.raises(RuntimeError, match="timeout"):
            generate_recommendations(
                financial_data,
                capacity_data,
            )


def test_empty_ai_response(
    financial_data,
    capacity_data,
):
    response = Mock()

    response.json.return_value = {
        "response": ""
    }

    with (
        patch(
            "services.ai_optimizer.check_ollama",
            return_value={
                "online": True,
                "model_available": True,
            },
        ),
        patch(
            "services.ai_optimizer.check_ai_resources",
            return_value={"ready": True},
        ),
        patch(
            "services.ai_optimizer.requests.post",
            return_value=response,
        ),
    ):
        with pytest.raises(RuntimeError, match="empty response"):
            generate_recommendations(
                financial_data,
                capacity_data,
            )
