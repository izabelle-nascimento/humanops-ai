
"""HumanOps AI - Local AI Strategic Advisor."""

import json

import psutil
import requests


# ==========================================================
# AI CONFIGURATION
# ==========================================================

OLLAMA_URL = "http://localhost:11434"
MODEL = "qwen2.5:7b"

MIN_AVAILABLE_RAM_GB = 10
CONTEXT_SIZE = 4096
MAX_OUTPUT_TOKENS = 1500
REQUEST_TIMEOUT = 300


# ==========================================================
# STRATEGIC SYSTEM PROMPT
# ==========================================================

SYSTEM_PROMPT = """
You are HumanOps AI, a senior consultant specializing
in infrastructure, FinOps, capacity planning and
responsible artificial intelligence.

MISSION:

Optimize resources. Not people.

Your objective is to identify operational waste,
reduce infrastructure costs and support workforce
preservation without compromising business continuity.

MANDATORY RULES:

- All monetary values are in Brazilian Reais (BRL).
- Always use BRL or R$. Never use USD or $ alone.
- Never recommend employee layoffs.
- Never invent metrics, savings or financial results.
- Do not repeat the entire input dataset.
- Use the financial calculations provided by Python.
- Distinguish baseline savings from seasonal costs.
- Distinguish first-year savings from recurring savings.
- Treat all enterprise infrastructure data as simulated.
- Treat workforce retention as a scenario constraint,
  not a guaranteed real-world outcome.
- Equivalent positions represent cost equivalence,
  not actual jobs saved or positions to eliminate.
- Local computer metrics are not enterprise metrics.
- Do not guarantee service availability.
- Do not recommend shutting down critical services
  without technical validation.
- Require load testing before production changes.
- Require human approval before implementation.
- Identify inconsistencies between financial and
  capacity planning assumptions.
- Prioritize actionable recommendations.
- Distinguish local API fees from simulated enterprise
  AI operating costs.
- Do not calculate new financial metrics.
- If a required metric is unavailable, state that
  additional validation is necessary.

RESPONSE FORMAT:

### Executive Summary

Provide a concise business assessment in three sentences.

### Financial Intelligence

Highlight the most relevant financial findings.
Explain the business impact without repeating all metrics.

### Black Friday Readiness

Identify critical infrastructure bottlenecks and
recommend targeted capacity adjustments.

### Workforce Preservation

Explain how infrastructure optimization and automation
can support employee retention and professional growth.

### Priority Action Plan

Provide a Markdown table with these columns:

Priority | Action | Business Impact | Validation Required

### Risks and Limitations

Explain assumptions, uncertainties and required
human approvals.

Use professional English.
Limit the response to approximately 450 words.
Avoid generic recommendations and unnecessary repetition.
"""


# ==========================================================
# RESOURCE-AWARE AI
# ==========================================================

def check_ai_resources():
    """Check available system memory before AI inference."""

    memory = psutil.virtual_memory()

    available_gb = memory.available / (1024 ** 3)
    total_gb = memory.total / (1024 ** 3)

    return {
        "total_ram_gb": round(total_gb, 2),
        "available_ram_gb": round(available_gb, 2),
        "memory_usage_percent": memory.percent,
        "minimum_ram_gb": MIN_AVAILABLE_RAM_GB,
        "ready": available_gb >= MIN_AVAILABLE_RAM_GB,
    }


# ==========================================================
# OLLAMA HEALTH CHECK
# ==========================================================

def check_ollama():
    """Check local AI service and model availability."""

    try:

        response = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=5,
        )

        response.raise_for_status()

        models = [
            item["name"]
            for item in response.json().get("models", [])
        ]

        return {
            "online": True,
            "model_available": MODEL in models,
            "model": MODEL,
            "provider": "Ollama Local",
        }

    except (requests.RequestException, ValueError):

        return {
            "online": False,
            "model_available": False,
            "model": MODEL,
            "provider": "Ollama Local",
        }


# ==========================================================
# BUSINESS CONTEXT
# ==========================================================

def build_business_context(
    financial_data,
    capacity_data,
    system_data=None,
):
    """Build a structured context for the AI model."""

    return {
        "project": "HumanOps AI",

        "mission": "Optimize resources. Not people.",

        "currency": "BRL",

        "financial_analysis": financial_data,

        "black_friday_simulation": capacity_data,

        "local_system_metrics": system_data,

        "ai_execution": {
            "provider": "Ollama Local",
            "model": MODEL,
            "local_api_fees_brl": 0,
            "inference_mode": "on-demand",
            "automatic_model_unloading": True,
        },

        "constraints": {
            "planned_layoffs": 0,
            "human_approval_required": True,
            "corporate_data_is_simulated": True,
            "financial_projection_is_preliminary": True,
            "capacity_and_finops_not_fully_aligned": True,
            "local_metrics_are_not_corporate_metrics": True,
            "production_changes_require_load_testing": True,
            "autonomous_infrastructure_changes": False,
            "workforce_retention_is_scenario_constraint": True,
            "savings_are_not_guaranteed": True,
        },
    }


# ==========================================================
# AI STRATEGIC RECOMMENDATIONS
# ==========================================================

def generate_recommendations(
    financial_data,
    capacity_data,
    system_data=None,
):
    """Generate strategic recommendations using local AI."""

    # ------------------------------------------------------
    # Validate Ollama service
    # ------------------------------------------------------

    status = check_ollama()

    if not status["online"]:

        raise RuntimeError(
            "Ollama service is offline. "
            "Start Ollama and try again."
        )

    if not status["model_available"]:

        raise RuntimeError(
            f"Model {MODEL} is not installed. "
            f"Run: ollama pull {MODEL}"
        )

    # ------------------------------------------------------
    # Validate available resources
    # ------------------------------------------------------

    resources = check_ai_resources()

    if not resources["ready"]:

        raise RuntimeError(
            "Insufficient available system memory. "
            f"Available: {resources['available_ram_gb']} GB. "
            f"Required: {MIN_AVAILABLE_RAM_GB} GB."
        )

    # ------------------------------------------------------
    # Build AI context
    # ------------------------------------------------------

    context = build_business_context(
        financial_data=financial_data,
        capacity_data=capacity_data,
        system_data=system_data,
    )

    prompt = (
        "Analyze the following business scenario. "
        "All monetary values are in BRL. "
        "Provide concise strategic recommendations "
        "based exclusively on the supplied data.\n\n"
        + json.dumps(
            context,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )

    # ------------------------------------------------------
    # Configure local inference
    # ------------------------------------------------------

    payload = {
        "model": MODEL,

        "system": SYSTEM_PROMPT,

        "prompt": prompt,

        "stream": False,

        # Unload the model after inference.
        "keep_alive": 0,

        "options": {
            "temperature": 0.2,
            "num_ctx": CONTEXT_SIZE,
            "num_predict": MAX_OUTPUT_TOKENS,
        },
    }

    # ------------------------------------------------------
    # Execute local AI inference
    # ------------------------------------------------------

    try:

        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=(5, REQUEST_TIMEOUT),
        )

        response.raise_for_status()

        result = response.json()

        recommendation = result.get(
            "response",
            "",
        ).strip()

        if not recommendation:

            raise RuntimeError(
                "The AI returned an empty response."
            )

        # --------------------------------------------------
        # Return structured AI results
        # --------------------------------------------------

        return {
            "model": MODEL,

            "provider": "Ollama Local",

            "recommendation": recommendation,

            "generation_time_seconds": round(
                result.get("total_duration", 0) / 1e9,
                2,
            ),

            "generated_tokens": result.get(
                "eval_count",
                0,
            ),

            "prompt_tokens": result.get(
                "prompt_eval_count",
                0,
            ),

            "completion_reason": result.get(
                "done_reason",
                "unknown",
            ),

            "currency": "BRL",

            "data_source": "simulated",

            "api_fees_brl": 0,

            "human_approval_required": True,

            "automatic_model_unloading": True,
        }

    except requests.Timeout as exc:

        raise RuntimeError(
            "Local AI inference exceeded the timeout. "
            "Please try again."
        ) from exc

    except requests.RequestException as exc:

        raise RuntimeError(
            f"Local AI inference failed: {exc}"
        ) from exc

    except ValueError as exc:

        raise RuntimeError(
            "Invalid response received from Ollama."
        ) from exc


# ==========================================================
# STANDALONE INTEGRATION TEST
# ==========================================================

if __name__ == "__main__":

    from services.cost_analyzer import analyze_costs

    from services.scenario_simulator import (
        simulate_black_friday,
    )

    print("=" * 60)
    print("HUMANOPS AI - STRATEGIC INTELLIGENCE")
    print("Optimize resources. Not people.")
    print("=" * 60)

    print("\nChecking local AI service...")

    print(
        json.dumps(
            check_ollama(),
            indent=4,
        )
    )

    print("\nChecking available system resources...")

    print(
        json.dumps(
            check_ai_resources(),
            indent=4,
        )
    )

    print("\nGenerating strategic recommendations...")

    try:

        result = generate_recommendations(
            financial_data=analyze_costs(),
            capacity_data=simulate_black_friday(),
        )

        print("\n" + "=" * 60)

        print(result["recommendation"])

        print("\n" + "=" * 60)

        print(
            "AI Model:",
            result["model"],
        )

        print(
            "Generation time:",
            result["generation_time_seconds"],
            "seconds",
        )

        print(
            "Generated tokens:",
            result["generated_tokens"],
        )

        print(
            "Completion reason:",
            result["completion_reason"],
        )

        print(
            "Local API fees: BRL 0.00"
        )

        print(
            "Human approval required:",
            result["human_approval_required"],
        )

        print("=" * 60)

    except RuntimeError as exc:

        print(f"\nERROR: {exc}")

        raise SystemExit(1) from exc
