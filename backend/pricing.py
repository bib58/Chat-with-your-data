"""
Token usage tracking utility for LLM requests.
"""

from typing import Dict, Any


def calculate_token_financials(
    model_name: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    reasoning_tokens: int = 0,
) -> Dict[str, Any]:
    """Calculate token totals for the request."""
    total_tokens = prompt_tokens + completion_tokens

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": 0.0,
        "model_name": model_name,
    }
