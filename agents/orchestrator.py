import json
import os
from typing import Any

from agents.tools import get_latest_alert, get_logs_by_service

try:
    import autogen
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "AutoGen is not installed. Install with: pip install pyautogen"
    ) from exc


# Groq default model (fast + low cost).
MODEL = os.getenv("AUTOGEN_MODEL", "llama-3.1-8b-instant")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")


def _llm_config() -> dict[str, Any]:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Set it before running AutoGen orchestrator."
        )

    return {
        "config_list": [
            {
                "model": MODEL,
                "api_key": groq_api_key,
                "base_url": GROQ_BASE_URL,
            }
        ],
        "temperature": 0,
    }


def run_autogen_incident_flow() -> dict[str, Any]:
    latest_alert = get_latest_alert()
    if latest_alert is None:
        raise RuntimeError("No alerts found in data/logs/alerts.jsonl. Run main.py first.")

    service = latest_alert.get("service", "unknown")
    scoped_logs = get_logs_by_service(service=service, limit=60)

    incident_context = {
        "latest_alert": latest_alert,
        "scoped_logs": scoped_logs,
    }

    triage_agent = autogen.AssistantAgent(
        name="triage_agent",
        system_message=(
            "You are the incident triage agent. Identify impacted service, "
            "severity, and immediate blast radius from provided context. "
            "Return strict JSON with keys: impacted_service, severity, summary."
        ),
        llm_config=_llm_config(),
    )

    log_agent = autogen.AssistantAgent(
        name="log_analysis_agent",
        system_message=(
            "You analyze logs for failure patterns. Use the triage output and logs. "
            "Return strict JSON with keys: key_errors, frequency_estimate, evidence."
        ),
        llm_config=_llm_config(),
    )

    root_cause_agent = autogen.AssistantAgent(
        name="root_cause_agent",
        system_message=(
            "You infer probable root cause from alert + logs. "
            "Return strict JSON with keys: probable_root_cause, confidence, rationale."
        ),
        llm_config=_llm_config(),
    )

    reporter_agent = autogen.AssistantAgent(
        name="reporter_agent",
        system_message=(
            "You write final incident report as strict JSON with keys: "
            "incident_id, service, severity, root_cause, recommended_next_action."
        ),
        llm_config=_llm_config(),
    )

    user_proxy = autogen.UserProxyAgent(
        name="incident_orchestrator",
        human_input_mode="NEVER",
        code_execution_config=False,
    )

    kickoff = (
        "Incident context JSON:\n"
        f"{json.dumps(incident_context, indent=2)}\n\n"
        "Step 1: triage_agent produce JSON only."
    )
    triage = user_proxy.initiate_chat(triage_agent, message=kickoff)

    triage_msg = triage.chat_history[-1]["content"]
    log_prompt = (
        "Use this context and triage output. Return JSON only.\n"
        f"Context: {json.dumps(incident_context)}\n"
        f"Triage: {triage_msg}"
    )
    logs_out = user_proxy.initiate_chat(log_agent, message=log_prompt)
    logs_msg = logs_out.chat_history[-1]["content"]

    rc_prompt = (
        "Infer root cause. Return JSON only.\n"
        f"Alert: {json.dumps(latest_alert)}\n"
        f"Triage: {triage_msg}\n"
        f"Log Analysis: {logs_msg}"
    )
    rc_out = user_proxy.initiate_chat(root_cause_agent, message=rc_prompt)
    rc_msg = rc_out.chat_history[-1]["content"]

    rep_prompt = (
        "Generate final report JSON only.\n"
        f"Alert: {json.dumps(latest_alert)}\n"
        f"Triage: {triage_msg}\n"
        f"Root Cause: {rc_msg}"
    )
    report_out = user_proxy.initiate_chat(reporter_agent, message=rep_prompt)
    report_msg = report_out.chat_history[-1]["content"]

    return {
        "triage": triage_msg,
        "log_analysis": logs_msg,
        "root_cause": rc_msg,
        "report": report_msg,
    }
