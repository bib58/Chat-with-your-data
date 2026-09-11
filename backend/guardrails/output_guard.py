import re
from typing import Tuple, Optional, List, Dict, Any

CREDIT_CARD_PATTERN = r"\b(?:\d{4}[ -]?){3}\d{4}\b|\b\d{13,19}\b"
EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
API_KEY_PATTERNS = [
    r"AIza[0-9A-Za-z\-_]{20,}",
    r"sk-[a-zA-Z0-9]{20,}",
    r"Bearer\s+[A-Za-z0-9\-._~+/]+=*",
]

SERVER_PATH_PATTERNS = [
    r"[a-zA-Z]:\\[^\s\"'<>]+"
    r"/(?:Users|home|var|tmp|etc)/[^\s\"'<>]+",
]

HTML_SCRIPT_PATTERN = r"<\s*(script|iframe|object|embed)[^>]*>.*?<\s*/\s*\1\s*>"
HTML_TAG_EVENT_PATTERN = r"<\s*[^>]+\s+on\w+\s*=\s*['\"][^'\"]*['\"][^>]*>"

MAX_DISPLAY_ROWS = 200


def sanitize_text(text: str) -> str:
    """Sanitizes text by redacting PII, secrets, server paths, and dangerous HTML."""
    if not text or not isinstance(text, str):
        return ""

    sanitized = text

    for pattern in API_KEY_PATTERNS:
        sanitized = re.sub(pattern, "[REDACTED_KEY]", sanitized)

    sanitized = re.sub(EMAIL_PATTERN, "[REDACTED_EMAIL]", sanitized)

    def mask_cc(match):
        digits = re.sub(r"\D", "", match.group())
        if 13 <= len(digits) <= 19:
            return f"[REDACTED_CARD_ending_in_{digits[-4:]}]"
        return match.group()

    sanitized = re.sub(CREDIT_CARD_PATTERN, mask_cc, sanitized)

    for pattern in SERVER_PATH_PATTERNS:
        sanitized = re.sub(pattern, "[SERVER_PATH]", sanitized)

    sanitized = re.sub(HTML_SCRIPT_PATTERN, "", sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(HTML_TAG_EVENT_PATTERN, "", sanitized, flags=re.IGNORECASE)

    return sanitized


def sanitize_output(
    answer: str,
    table_data: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[str, Optional[List[Dict[str, Any]]]]:
    """
    Sanitizes the response answer, redacts PII in table rows, and bounds table data rows.

    Returns:
        (sanitized_answer, sanitized_table_data)
    """
    clean_answer = sanitize_text(answer)
    clean_table_data = None

    if isinstance(table_data, list):
        capped_data = table_data[:MAX_DISPLAY_ROWS]
        clean_table_data = []
        for row in capped_data:
            if isinstance(row, dict):
                clean_row = {k: sanitize_text(v) if isinstance(v, str) else v for k, v in row.items()}
                clean_table_data.append(clean_row)
            else:
                clean_table_data.append(row)

        if len(table_data) > MAX_DISPLAY_ROWS:
            truncation_notice = f"\n\n*(Note: Showing first {MAX_DISPLAY_ROWS} rows for optimal performance)*"
            if truncation_notice not in clean_answer:
                clean_answer += truncation_notice

    return clean_answer, clean_table_data
