import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
from config import PRODUCTS, OUT_DIR, FAIL_DIR, WORD_RANGE, model_alias
from validation import word_count

def sha16(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def make_condition_id(product_id, variant, paraphrase_id, facts_line, word_range) -> str:
    canonical = f"{product_id}|{variant}|p{paraphrase_id}|wr={word_range}|facts={facts_line}"
    return sha16(canonical)

def make_output_id(condition_id, model, temperature, full_message) -> str:
    canonical = f"{condition_id}|{model}|temp={temperature}|msg={full_message}"
    return sha16(canonical)

def make_record(product_id: str,
                variant: str,
                paraphrase_id: int,
                parts: Dict[str, str],
                wc: int,
                forbidden_hits: List[str],
                model: str,
                temperature: float,
                prompt: str) -> Dict:
    product = PRODUCTS[product_id]
    trait_axis = "EXTRAVERSION" if variant.startswith("E_") else ("OPENNESS" if variant.startswith("O_") else "NONE")
    full_message = f'{parts["hook"]} {parts["facts"]} {parts["framing"]} {parts["cta"]}'.strip()
    condition_id = make_condition_id(product_id, variant, paraphrase_id, product["facts_line"], WORD_RANGE)
    output_id = make_output_id(condition_id, model, temperature, full_message)
    return {
        "id": {"condition_id": condition_id, "output_id": output_id},
        "generation": {"model": model, "temperature": temperature, "timestamp_utc": utc_now_iso()},
        "meta": {
            "product_id": product_id,
            "product_name": product["product_name"],
            "trait_axis": trait_axis,
            "variant": variant,
            "paraphrase_id": paraphrase_id,
            "word_target": 100,
            "word_range": [WORD_RANGE[0], WORD_RANGE[1]],
        },
        "constraints": {
            "facts_line_must_match_verbatim": True,
            "no_personality_labels": True,
            "no_extra_benefits_or_claims": True,
            "no_social_proof_scarcity_authority": True,
            "cta_strength_equal_across_variants": True,
        },
        "full_prompt": prompt,
        "content": {
            "hook": parts["hook"],
            "facts": parts["facts"],
            "framing": parts["framing"],
            "cta": parts["cta"],
            "full_message": full_message,
        },
        "self_checks": {
            "approx_word_count_full_message": wc,
            "facts_line_verbatim_confirmed": True,
            "forbidden_items_present": forbidden_hits,
        },
    }

def save_record(record: Dict) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    alias = model_alias(record["generation"]["model"])
    model_dir = OUT_DIR / alias
    model_dir.mkdir(parents=True, exist_ok=True)
    m = record["meta"]
    fname = f'{m["product_id"]}_{m["variant"]}_p{m["paraphrase_id"]}_{alias}_{record["id"]["output_id"]}.json'
    path = model_dir / fname
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

def save_fail_record(product_id: str,
                     variant: str,
                     paraphrase_id: int,
                     raw_text: str,
                     error: Exception,
                     attempt: int,
                     prompt: str,
                     model: str,
                     temperature: float,
                     parts=None) -> Path:
    FAIL_DIR.mkdir(parents=True, exist_ok=True)
    alias = model_alias(model)
    fail_model_dir = FAIL_DIR / alias
    fail_model_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "status": "FAILED_VALIDATION",
        "error": str(error),
        "attempt": attempt,
        "generation": {"model": model, "model_alias": alias, "temperature": temperature, "timestamp_utc": utc_now_iso()},
        "meta": {"product_id": product_id, "variant": variant, "paraphrase_id": paraphrase_id, "word_range": [WORD_RANGE[0], WORD_RANGE[1]]},
        "full_prompt": prompt,
        "raw_output": raw_text,
        "parsed_parts": parts,
    }
    if parts is not None:
        full = f'{parts["hook"]} {parts["facts"]} {parts["framing"]} {parts["cta"]}'.strip()
        record["approx_word_count"] = word_count(full)
        record["full_message"] = full
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    fname = f'{product_id}_{variant}_p{paraphrase_id}_attempt{attempt}_{alias}_{ts}.json'
    path = fail_model_dir / fname
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

def load_completed_keys(out_dir: Path) -> set[str]:
    keys = set()
    scanned = parsed = skipped = 0
    for fp in out_dir.rglob("*.json"):
        scanned += 1
        try:
            rec = json.loads(fp.read_text(encoding="utf-8"))
            m = rec.get("meta", {})
            product_id = m.get("product_id")
            variant = m.get("variant")
            pid = m.get("paraphrase_id")
            model = rec.get("generation", {}).get("model", "UNKNOWN")
            if product_id and variant and pid is not None:
                keys.add(f"{product_id}__{variant}__p{pid}__{model}")
            parsed += 1
        except Exception:
            skipped += 1
    print(f"[load_completed_keys] scanned={scanned}, parsed={parsed}, skipped={skipped}, unique_keys={len(keys)}")
    return keys