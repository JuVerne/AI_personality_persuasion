import os
import json
from typing import Any
from pathlib import Path

from retry_logic import retry_json_call

DEFAULT_RATER_MODEL = "gpt-4o"
BASE_DIR = Path(__file__).resolve().parent
PERSONA_TEMPLATE_DIR = BASE_DIR / "persona_templates"

PERSONA_CONTEXT = {
    "TYPE_E_HIGH": (
        "You are high on Extraversion: socially oriented, energized by active settings, "
        "and generally more responsive to lively group-focused framing."
    ),
    "TYPE_O_HIGH": (
        "You are high on Openness: curious, receptive to new perspectives, and generally "
        "more responsive to novelty and idea-oriented framing."
    ),
}

SYSTEM_PROMPT = (
    "You are rating ad effectiveness in a behavioral experiment. "
    "Return valid JSON only."
)

_ENV_LOADED = False


def _load_dotenv_fallback(env_path: Path) -> None:
    try:
        text = env_path.read_text(encoding="utf-8")
    except Exception:
        return

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value


def _load_env_files_once() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    try:
        from dotenv import load_dotenv # type: ignore
        has_dotenv = True
    except ImportError:
        has_dotenv = False

    env_candidates = [
        BASE_DIR / ".env",
        BASE_DIR.parent / ".env",
    ]
    for env_path in env_candidates:
        if env_path.exists():
            if has_dotenv:
                load_dotenv(dotenv_path=env_path, override=False)
            else:
                _load_dotenv_fallback(env_path)

    _ENV_LOADED = True


def _persona_template_path(participant_type: str) -> Path:
    return PERSONA_TEMPLATE_DIR / f"{participant_type}.json"


def _load_persona_context_from_template(participant_type: str) -> str | None:
    path = _persona_template_path(participant_type)
    if not path.exists():
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        card = payload.get("persona_card", {})
        about_me = card.get("about_me", "").strip()
        how_i_judge = card.get("how_i_judge_ads", [])
        rules = card.get("response_style_rules", [])

        lines: list[str] = []
        if about_me:
            lines.append(about_me)
        if isinstance(how_i_judge, list):
            for item in how_i_judge:
                if isinstance(item, str) and item.strip():
                    lines.append(item.strip())
        if isinstance(rules, list):
            for item in rules:
                if isinstance(item, str) and item.strip():
                    lines.append(item.strip())

        if lines:
            return " ".join(lines)
    except Exception:
        return None

    return None


def get_openai_client(api_key: str | None = None, base_url: str | None = None) -> Any:
    from openai import OpenAI # type: ignore

    _load_env_files_once()
    resolved_api_key = api_key or os.getenv("CHAT_AI_API_KEY")
    if not resolved_api_key:
        raise EnvironmentError(
            "Set CHAT_AI_API_KEY in your environment."
        )

    resolved_base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("GWDG_BASE_URL")
    if base_url is not None:
        cleaned = base_url.strip()
        if cleaned.lower() in {"", "none", "null"}:
            resolved_base_url = None
        else:
            resolved_base_url = cleaned
    kwargs: dict[str, Any] = {"api_key": resolved_api_key}
    if resolved_base_url:
        kwargs["base_url"] = resolved_base_url
    return OpenAI(**kwargs)


def _build_user_prompt(
    ad_text: str,
    participant_type: str,
    condition_label: str | None = None,
    product_name: str | None = None,
    persona_context: str | None = None,
) -> str:
    template_context = _load_persona_context_from_template(participant_type)
    resolved_persona = (
        persona_context
        or template_context
        or PERSONA_CONTEXT.get(participant_type, f"You are participant type {participant_type}.")
    )
    # Keep condition labels hidden to avoid leaking experiment assignment to the rater.
    product_line = f"Product: {product_name}." if product_name else "Product: unknown."

    return (
        "Rate the ad as this participant.\n\n"
        f"Participant type: {participant_type}\n"
        f"Persona context: {resolved_persona}\n"
        f"{product_line}\n\n"
        "Ad message:\n"
        f"{ad_text}\n\n"
        "Return exactly one JSON object with exactly these keys and no others:\n"
        "{\n"
        '  "effectiveness_rating_q1": integer 1-7,\n'
        '  "effectiveness_rating_q2": integer 1-7,\n'
        '  "motivation": "one sentence"\n'
        "}\n"
        "Do not include markdown, code fences, or extra text."
    )


def rate_ad_structured(
    client: Any,
    model: str,
    ad_text: str,
    participant_type: str,
    condition_label: str | None = None,
    product_name: str | None = None,
    persona_context: str | None = None,
    temperature: float = 0.0,
    max_retries: int = 5,
    request_timeout_seconds: float | None = 120.0,
) -> dict[str, Any]:
    """
    Returns strictly validated JSON with keys:
    effectiveness_rating_q1, effectiveness_rating_q2, motivation.
    Retries on parse/validation failures.
    """
    user_prompt = _build_user_prompt(
        ad_text=ad_text,
        participant_type=participant_type,
        condition_label=condition_label,
        product_name=product_name,
        persona_context=persona_context,
    )

    def _call_once() -> str:
        request_kwargs: dict[str, Any] = {}
        if request_timeout_seconds is not None:
            request_kwargs["timeout"] = float(request_timeout_seconds)
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            **request_kwargs,
        )
        return (response.choices[0].message.content or "").strip()

    return retry_json_call(call_fn=_call_once, max_retries=max_retries)
