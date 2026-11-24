
"""Cross-platform infrastructure monitoring module."""

import platform
from datetime import datetime, timezone
from pathlib import Path

import psutil


def bytes_to_gb(value: int) -> float:
    """Convert bytes to GiB."""
    return round(value / (1024 ** 3), 2)


def collect_system_metrics() -> dict:
    """Collect real-time operating system metrics."""

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(Path.home().anchor)
    swap = psutil.swap_memory()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "local_system",
        "operating_system": platform.system(),
        "os_version": platform.release(),
        "architecture": platform.machine(),

        "cpu": {
            "usage_percent": psutil.cpu_percent(interval=1),
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
        },

        "memory": {
            "total_gb": bytes_to_gb(memory.total),
            "available_gb": bytes_to_gb(memory.available),
            "usage_percent": memory.percent,
        },

        "disk": {
            "total_gb": bytes_to_gb(disk.total),
            "used_gb": bytes_to_gb(disk.used),
            "free_gb": bytes_to_gb(disk.free),
            "usage_percent": disk.percent,
        },

        "swap": {
            "total_gb": bytes_to_gb(swap.total),
            "used_gb": bytes_to_gb(swap.used),
            "usage_percent": swap.percent,
        },

        "process_count": len(psutil.pids()),

        "uptime_hours": round(
            (datetime.now().timestamp() - psutil.boot_time()) / 3600,
            2,
        ),
    }


if __name__ == "__main__":
    import json

    metrics = collect_system_metrics()
    print(json.dumps(metrics, indent=4))
