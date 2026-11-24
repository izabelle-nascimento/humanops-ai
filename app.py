
"""HumanOps AI - Black Friday Edition."""

from pathlib import Path

import streamlit as st
import plotly.graph_objects as go

from collectors.system_metrics import collect_system_metrics
from views.finops_dashboard import render_finops, currency
from views.black_friday_dashboard import render_black_friday
from views.ai_dashboard import render_ai_advisor


# Application configuration

st.set_page_config(
    page_title="HumanOps AI | Black Edition",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent

GOLD = "#D4AF37"
WHITE = "#F5F5F5"
MUTED = "#999999"
GREEN = "#34D399"
RED = "#EF4444"
AMBER = "#F59E0B"


# Load design system

def load_css():
    css_file = BASE_DIR / "assets" / "style.css"

    if css_file.exists():
        st.markdown(
            f"<style>{css_file.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


load_css()


# Resource visualization

def resource_gauge(label, value):

    if value >= 85:
        color = RED
    elif value >= 70:
        color = AMBER
    else:
        color = GOLD

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={
                "suffix": "%",
                "font": {
                    "size": 34,
                    "color": WHITE,
                },
            },
            title={
                "text": label.upper(),
                "font": {
                    "size": 13,
                    "color": MUTED,
                },
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "visible": False,
                },
                "bar": {
                    "color": color,
                    "thickness": 0.25,
                },
                "bgcolor": "#292929",
                "borderwidth": 0,
            },
        )
    )

    fig.update_layout(
        height=210,
        margin=dict(l=25, r=25, t=45, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=WHITE,
    )

    return fig


# Sidebar

with st.sidebar:

    st.title("HumanOps AI")
    st.caption("BLACK EDITION")

    st.divider()

    st.markdown("### Our mission")

    st.write(
        "Technology should empower people, "
        "not replace them."
    )

    st.divider()

    st.button(
        "Refresh system metrics",
        width="stretch",
    )

    st.caption("Version 0.2.0")
    st.caption("Development environment")


# Brand

st.html("""
    <div class="brand">
        <div class="brand-icon">H</div>
        <div>
            <div class="brand-name">
                HUMANOPS <span>AI</span>
            </div>
            <div class="brand-description">
                INTELLIGENCE PLATFORM
            </div>
        </div>
    </div>
    """)


# Hero banner

st.html("""
    <div class="hero">
        <div class="hero-label">
            Black Friday / 2026
        </div>

        <div class="hero-title">
            Optimize resources.<br>
            <span>Not people.</span>
        </div>

        <div class="hero-description">
            Artificial intelligence.
            Operational efficiency.
            Human potential.
            <br><br>
            A smarter approach to infrastructure
            optimization and workforce preservation.
        </div>
    </div>
    """)


# Navigation

overview, infrastructure, finops, black_friday, advisor = st.tabs(
    [
        "Overview",
        "Infrastructure",
        "FinOps",
        "Black Friday",
        "AI Advisor",
    ]
)


# Collect local system metrics

metrics = collect_system_metrics()

# Shared business scenario

with finops:
    financial_result = render_finops()

with black_friday:
    black_friday_result = render_black_friday(
        financial_data=financial_result,
    )

business_result = financial_result

financial_impact = black_friday_result["financial_impact"]



# Overview

with overview:

    st.markdown(
        '<div class="status-online">'
        '● LOCAL SYSTEM ONLINE'
        '</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Real-time local operating system metrics"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "CPU Usage",
        f"{metrics['cpu']['usage_percent']}%",
    )

    c2.metric(
        "Memory Usage",
        f"{metrics['memory']['usage_percent']}%",
    )

    c3.metric(
        "Disk Usage",
        f"{metrics['disk']['usage_percent']}%",
    )

    c4.metric(
        "Active Processes",
        metrics["process_count"],
    )

    st.subheader("Resource Health")

    g1, g2, g3 = st.columns(3)

    with g1:
        st.plotly_chart(
            resource_gauge(
                "CPU",
                metrics["cpu"]["usage_percent"],
            ),
            width="stretch",
            key="cpu_gauge",
        )

    with g2:
        st.plotly_chart(
            resource_gauge(
                "Memory",
                metrics["memory"]["usage_percent"],
            ),
            width="stretch",
            key="memory_gauge",
        )

    with g3:
        st.plotly_chart(
            resource_gauge(
                "Disk",
                metrics["disk"]["usage_percent"],
            ),
            width="stretch",
            key="disk_gauge",
        )

    st.divider()

    st.subheader("Consolidated Business Impact")

    b1, b2, b3 = st.columns(3)

    b1.metric(
        "Monthly Baseline Savings",
        currency(business_result["net_monthly_savings"]),
    )

    b2.metric(
        "Adjusted First-Year Savings",
        currency(financial_impact["adjusted_first_year_savings"]),
    )

    b3.metric(
        "Workforce Retained (Scenario)",
        f"{business_result['employees']}/{business_result['employees']}",
    )

    b4, b5, b6 = st.columns(3)

    b4.metric(
        "Black Friday Scaling Cost",
        currency(financial_impact["campaign_scaling_cost"]),
    )

    b5.metric(
        "Event Month Net Savings",
        currency(financial_impact["event_month_net_savings"]),
    )

    b6.metric(
        "Planned Layoffs",
        0,
    )

    st.caption(
        "Simulated enterprise scenario. "
        "One annual campaign is assumed. "
        "Financial projections are preliminary."
    )

    st.html("""
        <div class="info-panel">
            <div class="info-title">
                Human-Centric Intelligence
            </div>
            <div class="info-text">
                Our objective is to identify infrastructure
                waste and reduce operational expenses
                before considering workforce reductions.
            </div>
        </div>
        """)


# Infrastructure

with infrastructure:

    st.header("Infrastructure Intelligence")

    st.caption(
        "Live hardware and operating system profile"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Operating System",
        metrics["operating_system"],
    )

    c2.metric(
        "Physical Cores",
        metrics["cpu"]["physical_cores"],
    )

    c3.metric(
        "Logical Cores",
        metrics["cpu"]["logical_cores"],
    )

    st.divider()

    left, right = st.columns(2)

    with left:

        st.subheader("Resource Utilization")

        resources = [
            ("CPU", metrics["cpu"]["usage_percent"]),
            ("Memory", metrics["memory"]["usage_percent"]),
            ("Disk", metrics["disk"]["usage_percent"]),
            ("Swap", metrics["swap"]["usage_percent"]),
        ]

        for label, value in resources:
            st.write(f"{label}: {value}%")
            st.progress(float(value) / 100)

    with right:

        st.subheader("Hardware Profile")

        st.write(
            "Architecture:",
            metrics["architecture"],
        )

        st.write(
            "Installed Memory:",
            f"{metrics['memory']['total_gb']} GiB",
        )

        st.write(
            "Available Memory:",
            f"{metrics['memory']['available_gb']} GiB",
        )

        st.write(
            "Disk Capacity:",
            f"{metrics['disk']['total_gb']} GiB",
        )

        st.write(
            "Uptime:",
            f"{metrics['uptime_hours']} hours",
        )

        st.write(
            "Last Collection:",
            metrics["timestamp"],
        )


# FinOps







with advisor:
    render_ai_advisor(
        financial_data=financial_result,
        capacity_data=black_friday_result,
        system_data=metrics,
    )

# Footer

st.divider()

st.html("""
    <div class="footer">
        HUMANOPS AI © 2026
        <br><br>
        BLACK FRIDAY EDITION
        &nbsp; | &nbsp;
        HUMAN-CENTRIC TECHNOLOGY
    </div>
    """)
