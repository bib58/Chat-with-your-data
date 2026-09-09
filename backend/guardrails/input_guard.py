import re
from typing import Tuple, Optional

# Regex patterns for detecting prompt injection, jailbreaks, and adversarial manipulation
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+|the\s+)?(previous|prior|above)\s+(instructions|prompts|rules|commands)",
    r"disregard\s+(all\s+|the\s+)?(previous|prior|above)\s+(instructions|prompts|rules|commands)",
    r"forget\s+(all\s+|the\s+)?(previous|prior|above|your)\s+(instructions|prompts|rules)",
    r"you\s+are\s+now\s+(an?\s+)?(unrestricted|jailbroken|evil|unfiltered|terminal)",
    r"(act|operate)\s+as\s+(an?\s+)?(unrestricted|jailbroken|evil|linux\s+terminal)",
    r"developer\s+mode\s+(output|enabled|on|activate)",
    r"\bDAN\s+mode\b",
    r"reveal\s+(the\s+|your\s+)?(system\s+prompt|instructions|initial\s+prompt|api\s*key)",
    r"output\s+(the\s+|your\s+)?(system\s+prompt|internal\s+instructions|hidden\s+rules)",
    r"bypass\s+(all\s+|the\s+)?(guardrails?|filters?|rules?|restrictions?)",
    r"override\s+(all\s+|the\s+)?(system|safety|security)\s+(rules?|guidelines?|policies?)",
]

# Command execution / OS injection attempts
SYSTEM_COMMAND_PATTERNS = [
    r"\bxp_cmdshell\b",
    r"\b(cmd\.exe|powershell(\.exe)?|/bin/bash|/bin/sh)\b",
    r"\b(rm\s+-rf|format\s+[c-z]:)\b",
    r"\b(__import__|os\.system|subprocess\.)\b",
    r"<\s*script[^>]*>",
    r"javascript\s*:",
]

# Destructive / mutating SQL commands in user prompt
DESTRUCTIVE_SQL_PATTERNS = [
    r"\b(drop|truncate)\s+(the\s+)?(table\b|[a-zA-Z0-9_]*table\b|database\b|schema\b)",
    r"\bdelete\s+(all\s+)?(from|rows|records|the)\b",
    r"\b(insert\s+into|update\s+\w+\s+set)\b",
    r"\balter\s+table\b",
]

MAX_PROMPT_LENGTH = 2500


def validate_input(prompt: str) -> Tuple[bool, Optional[str]]:
    """
    Validates user input against prompt injection, malicious commands, and structural anomalies.

    Returns:
        (is_safe, refusal_reason)
    """
    if not prompt or not prompt.strip():
        return False, "Input cannot be empty. Please enter a valid question about your dataset."

    clean_prompt = prompt.strip()

    if len(clean_prompt) > MAX_PROMPT_LENGTH:
        return False, f"Input is too long ({len(clean_prompt)} characters). Maximum allowed length is {MAX_PROMPT_LENGTH} characters."

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, clean_prompt, re.IGNORECASE):
            return False, (
                "Security Notice: Your query was flagged by input safety guardrails "
                "because it contains prohibited instructions or prompt injection patterns. "
                "Please submit only analytical questions related to your dataset."
            )

    for pattern in SYSTEM_COMMAND_PATTERNS:
        if re.search(pattern, clean_prompt, re.IGNORECASE):
            return False, (
                "Security Notice: Your query was flagged by input safety guardrails "
                "due to detected system commands or script injection attempts. "
                "Please submit only analytical questions related to your dataset."
            )

    for pattern in DESTRUCTIVE_SQL_PATTERNS:
        if re.search(pattern, clean_prompt, re.IGNORECASE):
            return False, (
                "Security Notice: Your query was flagged by input safety guardrails "
                "because it attempts destructive database operations (such as DROP or DELETE). "
                "Only read-only analytical questions are permitted."
            )

    return True, None
