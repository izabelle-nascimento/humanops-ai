
"""HumanOps AI - Financial Intelligence Dashboard."""

import streamlit as st
import plotly.graph_objects as go

from services.cost_analyzer import (
    analyze_costs,
    load_infrastructure,
)


GOLD = "#D4AF37"
WHITE = "#F5F5F5"
GRAY = "#454545"
GREEN = "#34D399"
RED = "#EF4444"


def currency(value):
    """Format values in Brazilian currency."""

    formatted = f"{value:,.2f}"

    return (
        "R$ "
        + formatted.replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def cost_comparison(result):

    fig = go.Figure(
        go.Bar(
            x=[
                "Current Infrastructure",
                "Optimized + AI",
            ],
            y=[
                result["current_cost"],
                result["total_optimized_cost"],
            ],
            marker_color=[GRAY, GOLD],
            text=[
                currency(result["current_cost"]),
                currency(result["total_optimized_cost"]),
            ],
            textposition="outside",
        )
    )

    fig.update_layout(
        height=340,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=WHITE,
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis=dict(
            title="Monthly Cost (BRL)",
            gridcolor="#292929",
            rangemode="tozero",
        ),
    )

    return fig


def category_comparison():

    df = load_infrastructure()

    grouped = df.groupby("category")[
        ["monthly_cost", "optimized_cost"]
    ].sum().reset_index()

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Current Cost",
            x=grouped["category"],
            y=grouped["monthly_cost"],
            marker_color=GRAY,
        )
    )

    fig.add_trace(
        go.Bar(
            name="Optimized Cost",
            x=grouped["category"],
            y=grouped["optimized_cost"],
            marker_color=GOLD,
        )
    )

    fig.update_layout(
        barmode="group",
        height=340,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=WHITE,
        legend=dict(
            orientation="h",
            y=1.12,
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis=dict(
            title="Monthly Cost (BRL)",
            gridcolor="#292929",
        ),
    )

    return fig


def render_finops():

    st.header("Financial Intelligence")

    st.caption(
        "Black Friday cost optimization "
        "| Simulated enterprise infrastructure"
    )

    st.markdown("### Business Scenario")

    with st.expander(
        "Configure financial parameters",
        expanded=True,
    ):

        c1, c2, c3 = st.columns(3)

        employees = c1.number_input(
            "Total Employees",
            min_value=1,
            value=50,
            step=1,
        )

        employee_cost = c2.number_input(
            "Monthly Cost per Employee (BRL)",
            min_value=1000,
            value=5000,
            step=500,
        )

        target = c3.number_input(
            "Monthly Savings Target (BRL)",
            min_value=0,
            value=15000,
            step=500,
        )

        c4, c5 = st.columns(2)

        ai_cost = c4.number_input(
            "Monthly AI Cost (BRL)",
            min_value=0,
            value=500,
            step=100,
        )

        implementation = c5.number_input(
            "Implementation Cost (BRL)",
            min_value=0,
            value=3000,
            step=500,
        )

    result = analyze_costs(
        employees=employees,
        employee_monthly_cost=employee_cost,
        ai_monthly_cost=ai_cost,
        implementation_cost=implementation,
        savings_target=target,
    )

    st.markdown("### Financial Performance")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Monthly Net Savings",
        currency(result["net_monthly_savings"]),
    )

    c2.metric(
        "First-Year Net Savings",
        currency(result["annual_net_savings"]),
    )

    c3.metric(
        "Cost Reduction",
        f"{result['reduction_percent']:.1f}%",
    )

    c4, c5, c6 = st.columns(3)

    c4.metric(
        "Current Infrastructure",
        currency(result["current_cost"]),
    )

    c5.metric(
        "Optimized Infrastructure + AI",
        currency(result["total_optimized_cost"]),
    )

    c6.metric(
        "Optimization Opportunities",
        result["optimization_opportunities"],
    )

    if result["target_achieved"]:

        st.success(
            "Financial target achieved "
            "without planned workforce reductions."
        )

    else:

        st.warning(
            "Additional monthly savings required: "
            + currency(result["target_gap"])
        )

    st.divider()

    st.markdown("### Operational Cost Analysis")

    left, right = st.columns(2)

    with left:

        st.plotly_chart(
            cost_comparison(result),
            width="stretch",
            key="finops_cost_comparison",
        )

    with right:

        st.plotly_chart(
            category_comparison(),
            width="stretch",
            key="finops_category_comparison",
        )

    st.divider()

    st.markdown("### Workforce Preservation")

    st.caption(
        "Zero layoffs is a scenario constraint, "
        "not a guaranteed business outcome."
    )

    w1, w2, w3 = st.columns(3)

    w1.metric(
        "Workforce Retained",
        f"{employees}/{employees}",
    )

    w2.metric(
        "Planned Layoffs",
        0,
    )

    w3.metric(
        "Equivalent Payroll Cost",
        f"{result['equivalent_positions']:.2f} FTE",
    )

    st.progress(1.0)

    st.caption(
        "100% workforce retention assumed"
    )

    st.info(
        "FTE equivalence compares infrastructure "
        "savings with monthly employee costs. "
        "It does not represent actual jobs saved."
    )

    st.divider()

    st.markdown("### Infrastructure Inventory")

    df = load_infrastructure()

    df["monthly_savings"] = (
        df["monthly_cost"] - df["optimized_cost"]
    )

    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
    )

    st.download_button(
        label="Download Optimization Report",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="humanops_finops_report.csv",
        mime="text/csv",
        width="stretch",
    )

    st.caption(
        "All corporate infrastructure costs "
        "are simulated. Optimization assumptions "
        "require technical validation before "
        "production implementation."
    )

    return result
