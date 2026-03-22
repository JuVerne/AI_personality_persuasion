import re
from config import WORD_RANGE

FORBIDDEN_PATTERNS = [
    r"\blimited time\b",
    r"\bact now\b",
    r"\bdon't miss\b",
    r"\bexperts?\b",
    r"\b#\s*1\b",
    r"\beveryone\b",
    r"\bmost popular\b",
    r"\baward\b",
    r"\bguarantee\b",
    r"\bonly today\b",
    r"\brated\b.*\bstars\b",
]

def strip_think_blocks(text: str) -> str:
    return re.sub(r"(?mi)^\s*(/no_think|/think)\s*$", "", text).strip()

def word_count(s: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", s))

def parse_four_lines(text: str) -> dict:
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    if len(lines) != 4:
        raise ValueError(f"Expected exactly 4 non-empty lines, got {len(lines)}.\nRaw:\n{text}")
    def get(prefix: str) -> str:
        for ln in lines:
            if ln.startswith(prefix):
                return ln[len(prefix):].strip()
        raise ValueError(f"Missing required line prefix: {prefix}\nRaw:\n{text}")
    return {
        "hook": get("Hook:"),
        "facts": get("Facts:"),
        "framing": get("Framing:"),
        "cta": get("CTA:"),
    }

def validate_message(parts: dict, facts_line: str):
    if parts["facts"].strip() != facts_line.strip():
        raise ValueError("Facts line mismatch (must match FACTS_LINE verbatim).")
    full = f'{parts["hook"]} {parts["facts"]} {parts["framing"]} {parts["cta"]}'.strip()
    wc = word_count(full)
    if not (WORD_RANGE[0] <= wc <= WORD_RANGE[1]):
        raise ValueError(f"Word count {wc} outside range {WORD_RANGE}.")
    low = full.lower()
    forbidden_hits = [pat for pat in FORBIDDEN_PATTERNS if re.search(pat, low)]
    if forbidden_hits:
        raise ValueError(f"Forbidden cue(s) detected: {forbidden_hits}")
    return wc, forbidden_hits
