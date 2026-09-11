import re
from typing import Tuple, Optional

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

SYSTEM_COMMAND_PATTERNS = [
    r"\bxp_cmdshell\b",
    r"\b(cmd\.exe|powershell(\.exe)?|/bin/bash|/bin/sh)\b",
    r"\b(rm\s+-rf|format\s+[c-z]:)\b",
    r"\b(__import__|os\.system|subprocess\.)\b",
    r"<\s*script[^>]*>",
    r"javascript\s*:",
]

DESTRUCTIVE_SQL_PATTERNS = [
    r"\b(drop|truncate)\s+(the\s+)?(table\b|[a-zA-Z0-9_]*table\b|database\b|schema\b)",
    r"\bdelete\s+(all\s+)?(from|rows|records|the)\b",
    r"\b(insert\s+into|update\s+\w+\s+set)\b",
    r"\balter\s+table\b",
]

OFF_TOPIC_PATTERNS = [
    r"(?:what|where)\s+is\s+the\s+(capital|president|king|queen|currency|population|language)\s+of\b",
    r"\bwho\s+(is|was|are|were)\s+(the\s+)?(president|prime\s+minister|king|queen|ceo|founder|inventor)\b",
    r"\b(tell|teach)\s+me\s+(about|the\s+history|a\s+joke|a\s+story|a\s+poem|a\s+recipe)\b",
    r"\bwhat\s+is\s+the\s+(meaning|definition)\s+of\b",
    r"\bdefine\s+the\s+word\b",
    r"\bwhat\s+does\s+\w+\s+mean\b",
    # Geography / science / history trivia
    r"\b(tallest|longest|biggest|smallest|deepest|highest)\s+(mountain|river|ocean|building|country|city|lake|desert)\b",
    r"\bwhat\s+(year|date)\s+(did|was)\b.{0,30}\b(born|die|invent|discover|found|happen)\b",
    r"\bhow\s+far\s+is\s+(it\s+from|the\s+distance)\b",
    # Creative / conversational
    r"\bwrite\s+(me\s+)?(a|an|the)\s+(poem|essay|story|song|letter|email|code|script|function)\b",
    r"\b(compose|generate|create)\s+(a|an|the)\s+(poem|essay|story|song|haiku)\b",
    r"\btranslate\s+.{1,50}\s+(to|into)\s+(english|french|spanish|german|hindi|arabic|chinese|japanese)\b",
    r"\bsolve\s+(this|the)\s+(math|equation|problem|riddle|puzzle)\b",
    # Coding help
    r"\b(write|give\s+me|show\s+me)\s+(a\s+)?(python|java|javascript|c\+\+|html|css|react|code)\b",
    r"\bhow\s+to\s+(code|program|implement|build)\s+(a|an|in)\b",
    # Conversational / personal
    r"\b(who|what)\s+are\s+you\b",
    r"\bwhat\s+is\s+your\s+(name|purpose|favorite)\b",
    r"\btell\s+me\s+a\s+joke\b",
    r"\bsing\s+(me\s+)?a\s+song\b",
]

DATA_RELEVANCE_KEYWORDS = [
    r"\b(column|row|table|field|record|data_table|dataset|csv|excel|database|schema)\b",
    r"\b(average|mean|median|sum|count|total|max|min|std|deviation|variance|percentage|percent)\b",
    r"\b(group\s+by|order\s+by|sort\s+by|filter|where|having|distinct|unique|null|missing)\b",
    r"\b(trend|distribution|correlation|outlier|anomaly|breakdown|compare|comparison|versus|vs)\b",
    r"\b(chart|graph|plot|visuali[sz]e|histogram|bar\s+chart|pie\s+chart|scatter)\b",
    r"\b(top\s+\d+|bottom\s+\d+|highest|lowest|most|least|rank|ranking)\b",
    r"\b(sales|revenue|profit|cost|price|quantity|amount|budget|expense|income|growth)\b",
    r"\b(customer|product|order|employee|transaction|invoice|payment|shipment|category)\b",
    r"\b(date|month|year|quarter|week|daily|monthly|yearly|annual|seasonal|time\s*series)\b",
    r"\b(show\s+me|list|display|give\s+me|find|search|look\s+up|get|fetch|query)\b",
    r"\b(how\s+many|how\s+much|what\s+is\s+the\s+(total|average|sum|count))\b",
]

_REFUSAL_MSG = (
    "I'm a data analysis assistant — I can only answer questions about your "
    "uploaded dataset or connected database. Please ask a question related to "
    "your data (e.g. trends, totals, comparisons, filtering, charts)."
)

MAX_PROMPT_LENGTH = 2500


def _is_data_relevant(prompt: str) -> bool:
    """Return True if the prompt contains data-analysis keywords."""
    for pattern in DATA_RELEVANCE_KEYWORDS:
        if re.search(pattern, prompt, re.IGNORECASE):
            return True
    return False


def validate_input(prompt: str) -> Tuple[bool, Optional[str]]:
    """
    Validates user input against prompt injection, malicious commands,
    structural anomalies, and off-topic / general-knowledge questions.

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

    if not _is_data_relevant(clean_prompt):
        for pattern in OFF_TOPIC_PATTERNS:
            if re.search(pattern, clean_prompt, re.IGNORECASE):
                return False, _REFUSAL_MSG

    return True, None
