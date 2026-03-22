import time
from openai import OpenAI
from prompts import build_prompt, build_system_prompt, append_no_think
from validation import parse_four_lines, validate_message, strip_think_blocks
from records import make_record, save_fail_record
from config import PRODUCTS

def call_model(prompt: str | None,
               client: OpenAI,
               model: str,
               temperature: float,
               system_prompt: str | None = None,
               messages: list | None = None) -> str:
    if messages is None:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
    else:
        if system_prompt and (not messages or messages[0].get("role") != "system"):
            messages = [{"role": "system", "content": system_prompt}] + messages
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return (resp.choices[0].message.content or "").strip()

def _build_correction(raw_text: str, error: Exception, facts_line: str, model: str) -> str:
    err_str = str(error)
    if "Word count" in err_str:
        diagnosis = f"Your word count is outside range. Expand or trim Framing only."
    elif "Facts line mismatch" in err_str:
        diagnosis = f"Facts line mismatch. Must be exactly: {facts_line}"
    elif "lines" in err_str.lower():
        diagnosis = "Output must have exactly four lines: Hook, Facts, Framing, CTA."
    else:
        diagnosis = f"Validation error: {err_str}"
    return append_no_think(model,
        f"Your previous output failed validation.\n\nPROBLEM: {diagnosis}\n\nRegenerate the full four-line ad now, fixing only the problem above."
    )

def generate_one_message(product_id: str,
                         variant: str,
                         paraphrase_id: int,
                         client: OpenAI,
                         model: str,
                         temperature: float,
                         max_retries: int = 10):
    prompt = build_prompt(product_id, variant, paraphrase_id)
    prompt = append_no_think(model, prompt)
    facts_line = PRODUCTS[product_id]["facts_line"]
    system = build_system_prompt(model)
    messages = [{"role": "user", "content": prompt}]
    last_err = None
    for attempt in range(1, max_retries + 1):
        raw_text = call_model(
            prompt=None,
            client=client,
            model=model,
            temperature=temperature,
            system_prompt=system,
            messages=messages,
        )
        raw_text = strip_think_blocks(raw_text)
        parts = None
        try:
            parts = parse_four_lines(raw_text)
            wc, hits = validate_message(parts, facts_line)
            record = make_record(
                product_id=product_id,
                variant=variant,
                paraphrase_id=paraphrase_id,
                parts=parts,
                wc=wc,
                forbidden_hits=hits,
                model=model,
                temperature=temperature,
                prompt=prompt,
            )
            return record
        except Exception as e:
            last_err = e
            fail_path = save_fail_record(
                product_id=product_id,
                variant=variant,
                paraphrase_id=paraphrase_id,
                raw_text=raw_text,
                error=e,
                attempt=attempt,
                prompt=prompt,
                model=model,
                temperature=temperature,
                parts=parts,
            )
            print(f"[attempt {attempt} failed: {e}] -> {fail_path}")
            correction = _build_correction(raw_text, e, facts_line, model)
            messages.append({"role": "assistant", "content": raw_text})
            messages.append({"role": "user", "content": correction})
            time.sleep(0.5 * attempt)
    raise RuntimeError(f"Failed after {max_retries} retries for {product_id}/{variant}/p{paraphrase_id}/{model}: {last_err}")