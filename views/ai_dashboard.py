
"""HumanOps AI - Strategic Advisor Dashboard."""

import streamlit as st

from services.ai_optimizer import (
    check_ollama,
    check_ai_resources,
    generate_recommendations,
)


def render_ai_advisor(
    financial_data,
    capacity_data,
    system_data=None,
):

    st.header("AI Strategic Advisor")

    st.caption(
        "Local Intelligence | Responsible AI "
        "| Human-Centric Decisions"
    )

    st.html("""
    <div style="
        background: linear-gradient(135deg, #171717, #211C0E);
        border: 1px solid #514321;
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 20px;
    ">
        <div style="
            color: #D4AF37;
            font-size: 12px;
            letter-spacing: 4px;
        ">
            HUMANOPS INTELLIGENCE
        </div>

        <h2 style="color: #FFFFFF;">
            Intelligence with purpose.
        </h2>

        <p style="color: #AAAAAA;">
            Reduce operational waste.
            Protect business continuity.
            Empower your workforce.
        </p>
    </div>
    """)

    status = check_ollama()
    resources = check_ai_resources()

    if status["online"] and status["model_available"]:
        st.success("LOCAL AI ONLINE")
    else:
        st.error("Local AI service or model unavailable.")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("AI Model", "Qwen 2.5 7B")
    c2.metric("API Fees", "R$ 0,00")
    c3.metric("Processing", "Local")
    c4.metric(
        "Available RAM",
        f"{resources['available_ram_gb']:.1f} GB",
    )

    st.divider()

    st.subheader("Strategic Intelligence")

    st.caption(
        "Analyze the current financial and "
        "Black Friday capacity scenarios."
    )

    ready = (
        status["online"]
        and status["model_available"]
        and resources["ready"]
    )

    if not resources["ready"]:
        st.warning(
            "Insufficient available RAM. "
            "Close unnecessary applications."
        )

    if st.button(
        "Generate Strategic Analysis",
        type="primary",
        width="stretch",
        disabled=not ready,
    ):

        st.session_state.pop("ai_analysis", None)

        try:

            with st.spinner(
                "HumanOps AI is analyzing your scenario..."
            ):

                result = generate_recommendations(
                    financial_data=financial_data,
                    capacity_data=capacity_data,
                    system_data=system_data,
                )

                st.session_state["ai_analysis"] = result

                st.session_state["ai_context"] = {
                    "financial": financial_data,
                    "capacity": capacity_data,
                }

        except RuntimeError as exc:
            st.error(str(exc))

    if "ai_analysis" in st.session_state:

        result = st.session_state["ai_analysis"]

        previous_context = st.session_state.get(
            "ai_context"
        )

        current_context = {
            "financial": financial_data,
            "capacity": capacity_data,
        }

        if previous_context != current_context:
            st.warning(
                "Scenario parameters have changed. "
                "Generate a new analysis."
            )

        st.divider()

        st.subheader("Executive Recommendations")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Generation Time",
            f"{result['generation_time_seconds']:.2f}s",
        )

        c2.metric(
            "Generated Tokens",
            result["generated_tokens"],
        )

        c3.metric(
            "Human Approval",
            "Required",
        )

        with st.container(border=True):
            st.markdown(result["recommendation"])

        report = (
            "# HumanOps AI - Strategic Report\n\n"
            "Model: " + result["model"] + "\n\n"
            "Data source: Simulated enterprise scenario\n\n"
            "Human approval required: Yes\n\n"
            + result["recommendation"]
        )

        st.download_button(
            "Download Executive AI Report",
            data=report.encode("utf-8"),
            file_name="humanops_ai_report.md",
            mime="text/markdown",
            width="stretch",
        )

    st.divider()

    st.subheader("Responsible AI Governance")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        - Local data processing
        - On-demand inference
        - Automatic model unloading
        - Resource availability validation
        """)

    with c2:
        st.markdown("""
        - Human approval required
        - Zero planned layoffs
        - No autonomous infrastructure changes
        - Simulated financial projections
        """)

    st.info(
        "AI recommendations support human decisions. "
        "All proposed infrastructure changes require "
        "technical validation and approval."
    )

    st.html("""
    <div style="
        text-align: center;
        color: #D4AF37;
        font-size: 20px;
        font-weight: 600;
        padding: 25px;
    ">
        Optimize resources. Not people.
    </div>
    """)
