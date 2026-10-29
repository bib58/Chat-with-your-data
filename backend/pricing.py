"""
Pricing table and financial calculation utility for LLM tokens.
Rates are in USD per 1,000,000 tokens.
"""

from typing import Dict, Any, Optional

MODEL_PRICING = {
    # Gemini models (per 1M tokens)
    "gemini-3.6-flash": {"input": 0.075, "output": 0.30},
    "gemini-2.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    "gemini-2.0-flash-thinking-exp": {"input": 0.10, "output": 0.40},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-2.5-pro": {"input": 1.25, "output": 5.00},
    # DeepSeek models
    "deepseek-reasoner": {"input": 0.55, "output": 2.19},
    "deepseek-chat": {"input": 0.14, "output": 0.28},
    # OpenAI models
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "o1": {"input": 15.00, "output": 60.00},
    "o3-mini": {"input": 1.10, "output": 4.40},
}

DEFAULT_PRICING = {"input": 0.075, "output": 0.30}

def calculate_token_financials(
    model_name: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    reasoning_tokens: int = 0,
) -> Dict[str, Any]:
    """Calculate token totals and estimated cost in USD based on model pricing."""
    pricing = MODEL_PRICING.get(model_name.lower(), DEFAULT_PRICING)
    
    input_cost = (prompt_tokens / 1_000_000.0) * pricing["input"]
    output_cost = (completion_tokens / 1_000_000.0) * pricing["output"]
    total_cost = round(input_cost + output_cost, 6)
    
    total_tokens = prompt_tokens + completion_tokens
    
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": total_cost,
        "model_name": model_name,
    }
