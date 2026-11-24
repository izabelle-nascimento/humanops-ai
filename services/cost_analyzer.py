
"""HumanOps AI - Financial optimization engine."""

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "infrastructure.csv"


def load_infrastructure():
    """Load simulated corporate infrastructure."""

    return pd.read_csv(DATA_FILE)


def analyze_costs(
    employees=50,
    employee_monthly_cost=5000,
    ai_monthly_cost=500,
    implementation_cost=3000,
    savings_target=15000,
):
    """Calculate projected financial optimization."""

    if employees < 1 or employee_monthly_cost <= 0:
        raise ValueError("Invalid workforce parameters.")

    if min(
        ai_monthly_cost,
        implementation_cost,
        savings_target,
    ) < 0:
        raise ValueError("Costs cannot be negative.")

    df = load_infrastructure()

    df["monthly_savings"] = (
        df["monthly_cost"] - df["optimized_cost"]
    )

    current_cost = float(df["monthly_cost"].sum())

    optimized_cost = float(
        df["optimized_cost"].sum()
    )

    gross_savings = current_cost - optimized_cost

    net_savings = gross_savings - ai_monthly_cost

    annual_net_savings = (
        net_savings * 12 - implementation_cost
    )

    reduction_percent = (
        net_savings / current_cost * 100
        if current_cost > 0
        else 0
    )

    equivalent_positions = min(
        employees,
        max(0, net_savings) / employee_monthly_cost,
    )

    target_gap = max(
        0,
        savings_target - net_savings,
    )

    return {
        "data_source": "simulated",
        "current_cost": current_cost,
        "optimized_cost": optimized_cost,
        "total_optimized_cost": (
            optimized_cost + ai_monthly_cost
        ),
        "gross_monthly_savings": gross_savings,
        "ai_monthly_cost": ai_monthly_cost,
        "implementation_cost": implementation_cost,
        "net_monthly_savings": net_savings,
        "annual_net_savings": annual_net_savings,
        "reduction_percent": reduction_percent,
        "employees": employees,
        "planned_layoffs": 0,
        "workforce_retained_percent": 100,
        "equivalent_positions": equivalent_positions,
        "savings_target": savings_target,
        "target_achieved": net_savings >= savings_target,
        "target_gap": target_gap,
        "resources_analyzed": len(df),
        "optimization_opportunities": int(
            (df["monthly_savings"] > 0).sum()
        ),
    }


if __name__ == "__main__":
    import json

    result = analyze_costs()

    print(json.dumps(result, indent=4))
