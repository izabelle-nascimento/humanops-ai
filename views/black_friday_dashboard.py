
"""HumanOps AI - Black Friday Capacity Dashboard."""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from services.scenario_simulator import simulate_black_friday
from views.finops_dashboard import currency


GOLD = "#D4AF37"
WHITE = "#F5F5F5"
GRAY = "#454545"
GREEN = "#34D399"
RED = "#EF4444"
AMBER = "#F59E0B"


def capacity_chart(df, target):

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            name="Projected CPU",
            x=df["resource_name"],
            y=df["projected_cpu"],
            marker_color=GOLD,
        )
    )

    fig.add_trace(
        go.Bar(
            name="Projected Memory",
            x=df["resource_name"],
            y=df["projected_memory"],
            marker_color=GRAY,
        )
    )

    fig.add_hline(
        y=target,
        line_dash="dash",
        line_color=GREEN,
        annotation_text="Planning target",
    )

    fig.add_hline(
        y=100,
        line_dash="dot",
        line_color=RED,
        annotation_text="Capacity limit",
    )

    fig.update_layout(
        barmode="group",
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=WHITE,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            y=1.15,
        ),
        yaxis=dict(
            title="Projected Demand (%)",
            gridcolor="#292929",
            rangemode="tozero",
        ),
    )

    return fig


def render_black_friday(financial_data):

    st.header("Black Friday Intelligence")

    st.caption(
        "Capacity Planning | Operational Risk "
        "| Financial Impact"
    )

    st.html(
        """
        <div class="info-panel">
            <div class="info-title">
                Prepare for demand. Eliminate waste.
            </div>
            <div class="info-text">
                Simulate seasonal traffic peaks,
                identify infrastructure bottlenecks
                and estimate temporary scaling costs
                without reducing the workforce.
            </div>
        </div>
        """
    )

    st.subheader("Campaign Configuration")

    c1, c2 = st.columns(2)

    demand = c1.slider(
        "Expected Traffic Multiplier",
        min_value=1.0,
        max_value=5.0,
        value=2.0,
        step=0.25,
        format="%.2fx",
    )

    capacity = c2.slider(
        "Available Capacity Multiplier",
        min_value=1.0,
        max_value=5.0,
        value=1.0,
        step=0.25,
        format="%.2fx",
    )

    c3, c4 = st.columns(2)

    days = c3.slider(
        "Campaign Duration (Days)",
        min_value=1,
        max_value=30,
        value=5,
    )

    target = c4.slider(
        "Target Resource Utilization (%)",
        min_value=50,
        max_value=85,
        value=70,
        step=5,
    )

    result = simulate_black_friday(
        demand_multiplier=demand,
        capacity_multiplier=capacity,
        event_days=days,
        utilization_target=target,
    )

    df = pd.DataFrame(result["resources"])

    st.divider()

    st.subheader("Operational Risk Assessment")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Expected Traffic",
        f"{demand:.2f}x",
    )

    c2.metric(
        "Production Servers",
        result["servers_analyzed"],
    )

    c3.metric(
        "Critical Servers",
        result["critical_servers"],
    )

    c4.metric(
        "Servers Above Target",
        result["servers_above_target"],
    )

    if result["critical_servers"] > 0:

        st.error(
            "CRITICAL: Projected demand exceeds "
            "available infrastructure capacity."
        )

    elif result["servers_above_target"] > 0:

        st.warning(
            "Capacity adjustments are recommended "
            "before the campaign."
        )

    else:

        st.success(
            "All servers are within the configured "
            "planning threshold."
        )

    st.plotly_chart(
        capacity_chart(df, target),
        width="stretch",
        key="black_friday_capacity_chart",
    )

    st.caption(
        "Values above 100% represent projected "
        "demand exceeding available capacity."
    )

    st.divider()

    st.subheader("Targeted Scaling Recommendations")

    for resource in result["resources"]:

        risk = resource["risk"]

        if risk == "CRITICAL":
            color = RED

        elif risk in ("HIGH", "MODERATE"):
            color = AMBER

        else:
            color = GREEN

        with st.container(border=True):

            left, right = st.columns([3, 1])

            with left:

                st.markdown(
                    f"#### {resource['resource_name']}"
                )

                st.markdown(
                    f":{ 'red' if risk == 'CRITICAL' else 'orange' if risk in ('HIGH', 'MODERATE') else 'green' }"
                    f"[{risk} RISK]"
                )

                st.write(
                    "Projected CPU:",
                    f"{resource['projected_cpu']}%",
                )

                st.write(
                    "Projected Memory:",
                    f"{resource['projected_memory']}%",
                )

            with right:

                st.metric(
                    "Recommended Capacity",
                    f"{resource['required_capacity']:.2f}x",
                )

                st.caption(
                    "Additional campaign cost: "
                    + currency(
                        resource["additional_event_cost"]
                    )
                )

    st.divider()

    st.subheader("Financial Impact")

    financial = financial_data

    monthly_savings = financial["net_monthly_savings"]

    scaling_cost = result["total_event_scaling_cost"]

    event_savings = monthly_savings - scaling_cost

    annual_savings = (
        financial["annual_net_savings"] - scaling_cost
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Baseline Monthly Savings",
        currency(monthly_savings),
    )

    c2.metric(
        "Campaign Scaling Cost",
        currency(scaling_cost),
    )

    c3.metric(
        "Event Month Net Savings",
        currency(event_savings),
    )

    c4, c5, c6 = st.columns(3)

    c4.metric(
        "Adjusted First-Year Savings",
        currency(annual_savings),
    )

    c5.metric(
        "Workforce Retained",
        f"{financial['employees']}/{financial['employees']}",
    )

    c6.metric(
        "Planned Layoffs",
        0,
    )

    st.caption(
        "Preliminary combined projection using "
        "current FinOps parameters and baseline "
        "infrastructure capacity. One annual campaign "
        "is assumed."
    )

    st.divider()

    st.subheader("Capacity Planning Report")

    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
    )

    st.download_button(
        "Download Capacity Report",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="humanops_black_friday_report.csv",
        mime="text/csv",
        width="stretch",
    )

    st.caption(
        "Simulated data. Linear demand and pricing "
        "assumptions. Production changes require "
        "load testing and human approval."
    )

    result["financial_impact"] = {
        "currency": "BRL",
        "baseline_monthly_savings": round(monthly_savings, 2),
        "campaign_scaling_cost": round(scaling_cost, 2),
        "event_month_net_savings": round(event_savings, 2),
        "adjusted_first_year_savings": round(annual_savings, 2),
        "employees": financial["employees"],
        "planned_layoffs": 0,
        "annual_campaigns": 1,
        "projection_is_preliminary": True,
    }

    return result
