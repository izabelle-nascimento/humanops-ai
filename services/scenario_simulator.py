
"""HumanOps AI - Black Friday capacity simulator."""

import math

from services.cost_analyzer import load_infrastructure


def simulate_black_friday(
    demand_multiplier=2.0,
    capacity_multiplier=1.0,
    event_days=5,
    utilization_target=70,
):
    """Estimate capacity requirements during peak demand."""

    if demand_multiplier < 1:
        raise ValueError("Demand multiplier must be >= 1.")

    if capacity_multiplier < 1:
        raise ValueError("Capacity multiplier must be >= 1.")

    if not 1 <= event_days <= 30:
        raise ValueError("Event duration must be 1-30 days.")

    if not 0 < utilization_target <= 100:
        raise ValueError("Invalid utilization target.")

    inventory = load_infrastructure()

    production = inventory[
        (inventory["category"] == "Compute")
        & (inventory["environment"] == "Production")
    ].copy()

    results = []

    for _, resource in production.iterrows():

        cpu = float(resource["cpu_p95"])
        memory = float(resource["memory_p95"])

        projected_cpu = (
            cpu * demand_multiplier / capacity_multiplier
        )

        projected_memory = (
            memory * demand_multiplier / capacity_multiplier
        )

        peak_utilization = max(
            projected_cpu,
            projected_memory,
        )

        required_capacity = max(
            capacity_multiplier,
            math.ceil(
                max(cpu, memory)
                * demand_multiplier
                / utilization_target
                * 100
            ) / 100,
        )

        additional_capacity = max(
            0,
            required_capacity - capacity_multiplier,
        )

        # Linear pricing assumption for temporary capacity.
        baseline_cost = float(resource["monthly_cost"])

        selected_capacity_cost = (
            baseline_cost
            * (capacity_multiplier - 1)
            * event_days / 30
        )

        additional_cost = (
            baseline_cost
            * additional_capacity
            * event_days / 30
        )

        if peak_utilization > 100:
            risk = "CRITICAL"

        elif peak_utilization > 85:
            risk = "HIGH"

        elif peak_utilization > utilization_target:
            risk = "MODERATE"

        else:
            risk = "LOW"

        results.append({
            "resource_id": resource["resource_id"],
            "resource_name": resource["resource_name"],
            "baseline_cpu_p95": cpu,
            "baseline_memory_p95": memory,
            "projected_cpu": round(projected_cpu, 2),
            "projected_memory": round(projected_memory, 2),
            "risk": risk,
            "required_capacity": required_capacity,
            "selected_capacity_cost": round(
                selected_capacity_cost, 2
            ),
            "additional_event_cost": round(
                additional_cost, 2
            ),
        })

    selected_cost = sum(
        item["selected_capacity_cost"]
        for item in results
    )

    additional_cost = sum(
        item["additional_event_cost"]
        for item in results
    )

    return {
        "data_source": "simulated",
        "demand_multiplier": demand_multiplier,
        "capacity_multiplier": capacity_multiplier,
        "event_days": event_days,
        "utilization_target": utilization_target,
        "servers_analyzed": len(results),
        "critical_servers": sum(
            item["risk"] == "CRITICAL"
            for item in results
        ),
        "high_risk_servers": sum(
            item["risk"] == "HIGH"
            for item in results
        ),
        "servers_above_target": sum(
            item["risk"] != "LOW"
            for item in results
        ),
        "selected_capacity_cost": round(
            selected_cost, 2
        ),
        "additional_event_cost": round(
            additional_cost, 2
        ),
        "total_event_scaling_cost": round(
            selected_cost + additional_cost, 2
        ),
        "planned_layoffs": 0,
        "resources": results,
    }


if __name__ == "__main__":
    import json

    result = simulate_black_friday()

    print(json.dumps(result, indent=4))
