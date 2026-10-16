import re

# Patterns for noisy things. Order matters: long date/time patterns come first.
NOISE_PATTERNS = [
    r"\d{4}-\d{2}-\d{2}([t ]\d{2}:\d{2}(:\d{2})?)?",   # 2026-10-14 or 2026-10-14T15:00:00
    r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",                  # 14/10/2026
    r"\d{1,2}:\d{2}(:\d{2})?\s?(am|pm)?",              # 14:35 or 2:35:10 PM
    r"\b(just now|\d+\s(seconds?|minutes?|hours?|days?)\sago)\b",  # "5 minutes ago"
    r"\b\d[\d,\.]*\s?(views?|visitors?|likes?|comments?|users?|online|shares?)\b",  # "12,345 views"
    r"\b(?=[a-z0-9]*\d)(?=[a-z0-9]*[a-z])[a-z0-9]{16,}\b",  # random tokens like a8f3k29dj4h2k1l9
]


def tidy(text):
    """Collapse extra spaces and remove blank lines."""
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return [line for line in lines if line]


def clean_text(text, sensitivity="medium"):
    lines = tidy(text)
    text = "\n".join(lines)

    if sensitivity == "high":
        return text

    # medium and low: erase the noisy parts
    for pattern in NOISE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    if sensitivity == "low":
        text = re.sub(r"\d+", "", text)   # remove ALL numbers

    lines = tidy(text)

    if sensitivity == "low":
        lines = [line for line in lines if len(line) >= 4]   # drop tiny fragments

    return "\n".join(lines)