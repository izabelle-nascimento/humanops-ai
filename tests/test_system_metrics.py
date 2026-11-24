
"""Tests for HumanOps AI system metrics collector."""

import pytest

from collectors.system_metrics import collect_system_metrics


@pytest.fixture(scope="module")
def metrics():
    return collect_system_metrics()


def test_metrics_returns_dictionary(metrics):
    assert isinstance(metrics, dict)


def test_required_metrics_are_present(metrics):
    required = {
        "cpu",
        "memory",
        "disk",
        "swap",
        "operating_system",
        "architecture",
        "process_count",
        "uptime_hours",
        "timestamp",
    }

    assert required.issubset(metrics.keys())


@pytest.mark.parametrize(
    "resource",
    ["cpu", "memory", "disk", "swap"],
)
def test_resource_usage_range(metrics, resource):
    usage = metrics[resource]["usage_percent"]

    assert 0 <= usage <= 100


def test_cpu_core_count(metrics):
    physical = metrics["cpu"]["physical_cores"]
    logical = metrics["cpu"]["logical_cores"]

    assert physical > 0
    assert logical >= physical


def test_memory_capacity(metrics):
    total = metrics["memory"]["total_gb"]
    available = metrics["memory"]["available_gb"]

    assert total > 0
    assert 0 <= available <= total


def test_disk_capacity(metrics):
    assert metrics["disk"]["total_gb"] > 0


def test_process_count(metrics):
    assert metrics["process_count"] > 0


def test_system_uptime(metrics):
    assert metrics["uptime_hours"] >= 0


def test_operating_system(metrics):
    assert isinstance(metrics["operating_system"], str)
    assert metrics["operating_system"]
