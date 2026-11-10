import hashlib
import os
from typing import Any, Dict

from langsmith import traceable


def dataset_identifier(dataset_path: str = "", db_uri: str = "") -> str:
    """Return a stable, non-sensitive identifier for the active data source."""
    source = db_uri or dataset_path
    if not source:
        return "unknown"
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:12]


def trace_inputs_without_secrets(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Remove local paths and connection strings from captured trace inputs."""
    safe = dict(inputs)
    for key in ("dataset_path", "db_uri"):
        if key in safe:
            safe[key] = "[redacted]"
    if "state" in safe and isinstance(safe["state"], dict):
        state = dict(safe["state"])
        for key in ("dataset_path", "db_uri"):
            if key in state:
                state[key] = "[redacted]"
        safe["state"] = state
    return safe


def trace_outputs_without_secrets(outputs: Any) -> Any:
    """Remove local paths and connection strings from captured trace outputs."""
    if not isinstance(outputs, dict):
        return outputs
    safe = dict(outputs)
    for key in ("dataset_path", "db_uri"):
        if key in safe:
            safe[key] = "[redacted]"
    return safe


def model_cost(
    model_name: str,
    prompt_tokens: int,
    completion_tokens: int,
    reasoning_tokens: int,
) -> float | None:
    """Calculate cost only when deployment-provided pricing is available."""
    input_rate = os.getenv("LLM_INPUT_COST_PER_1M_USD")
    output_rate = os.getenv("LLM_OUTPUT_COST_PER_1M_USD")
    reasoning_rate = os.getenv("LLM_REASONING_COST_PER_1M_USD", output_rate)

    if not input_rate or not output_rate:
        return None

    try:
        cost = (
            prompt_tokens * float(input_rate)
            + completion_tokens * float(output_rate)
            + reasoning_tokens * float(reasoning_rate or output_rate)
        ) / 1_000_000
    except ValueError:
        return None
    return round(cost, 8)


def trace_metadata(state: Dict[str, Any]) -> Dict[str, Any]:
    """Build metadata that is safe to attach to a request or child operation."""
    return {
        "request_id": state.get("request_id", "unknown"),
        "session_id": state.get("session_id", "unknown"),
        "dataset_id": state.get("dataset_id", "unknown"),
        "model_name": state.get("model_name") or os.getenv("GEMINI_MODEL", "unknown"),
        "sql_dialect": state.get("sql_dialect", "unknown"),
        "execution_mode": state.get("execution_mode", "unknown"),
        "task_type": "text_to_sql",
    }


__all__ = [
    "dataset_identifier",
    "model_cost",
    "trace_inputs_without_secrets",
    "trace_outputs_without_secrets",
    "trace_metadata",
    "traceable",
]
