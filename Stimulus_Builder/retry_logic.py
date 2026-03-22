import json
import re
import time
from typing import Any, Callable

RATING_KEYS = (
    "effectiveness_rating_q1",
    "effectiveness_rating_q2",
    "motivation",
)


class RetryableParseError(ValueError):
    """Raised when model output cannot be parsed or validated as required JSON."""


class RetryExhaustedError(RuntimeError):
    """Raised when all retry attempts fail for parse/validation errors."""


def _extract_json_candidate(raw_text: str) -> dict[str, Any]:
    text = (raw_text or "").strip()
    if not text:
        raise RetryableParseError("Empty model response.")

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end < start:
            raise RetryableParseError("No JSON object found in response.")
        snippet = text[start : end + 1]
        try:
            payload = json.loads(snippet)
        except json.JSONDecodeError as exc:
            raise RetryableParseError(f"Invalid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise RetryableParseError("Top-level JSON must be an object.")
    return payload


def validate_rating_payload(payload: dict[str, Any]) -> dict[str, Any]:
    key_set = set(payload.keys())
    expected = set(RATING_KEYS)
    if key_set != expected:
        missing = sorted(expected - key_set)
        extra = sorted(key_set - expected)
        raise RetryableParseError(f"Unexpected keys. Missing={missing}, extra={extra}")

    out: dict[str, Any] = {}
    for key in ("effectiveness_rating_q1", "effectiveness_rating_q2"):
        raw_value = payload[key]
        if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
            raise RetryableParseError(f"{key} must be numeric in [1,7].")
        value = int(raw_value)
        if value != raw_value:
            raise RetryableParseError(f"{key} must be an integer in [1,7].")
        if value < 1 or value > 7:
            raise RetryableParseError(f"{key}={value} out of range [1,7].")
        out[key] = value

    motivation = payload["motivation"]
    if not isinstance(motivation, str) or not motivation.strip():
        raise RetryableParseError("motivation must be a non-empty string.")
    trimmed = " ".join(motivation.split())
    sentence_parts = [s for s in re.split(r"[.!?]+", trimmed) if s.strip()]
    if len(sentence_parts) != 1:
        raise RetryableParseError("motivation must be exactly one sentence.")
    out["motivation"] = trimmed
    return out


def retry_json_call(
    call_fn: Callable[[], str],
    max_retries: int = 5,
    initial_delay_seconds: float = 0.7,
    backoff_multiplier: float = 1.8,
) -> dict[str, Any]:
    """
    Call the LLM and retry only on parse/validation failures.
    """
    delay = initial_delay_seconds
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        raw_text = call_fn()
        try:
            payload = _extract_json_candidate(raw_text)
            return validate_rating_payload(payload)
        except RetryableParseError as exc:
            last_error = exc
            if attempt == max_retries:
                break
            time.sleep(delay)
            delay *= backoff_multiplier

    raise RetryExhaustedError(
        f"Failed to parse/validate rating JSON after {max_retries} attempts: {last_error}"
    )
