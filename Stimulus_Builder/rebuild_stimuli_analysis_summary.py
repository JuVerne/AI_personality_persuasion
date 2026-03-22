import argparse
import csv
import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_ANALYSED_ROOT = BASE_DIR / "stimuli_out_analysed"
DEFAULT_OUTPUT_CSV = DEFAULT_ANALYSED_ROOT / "stimuli_analysis_summary.csv"

BUNDLE_KEYS = (
    "E_social",
    "E_energy",
    "O_creative",
    "O_abstract",
    "O_practical",
    "O_novelty",
)

NRC_KEYS = (
    "positive",
    "negative",
    "joy",
    "trust",
    "anticipation",
    "surprise",
    "fear",
    "anger",
    "sadness",
    "disgust",
)


def _safe_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        return [payload]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def _extract_row(record: dict[str, Any], source_path: Path, root_dir: Path) -> dict[str, Any] | None:
    meta = record.get("meta", {})
    if not isinstance(meta, dict):
        return None
    product_id = meta.get("product_id")
    variant = meta.get("variant")
    if not product_id or not variant:
        return None

    rec_id = record.get("id", {}) if isinstance(record.get("id", {}), dict) else {}
    generation = (
        record.get("generation", {})
        if isinstance(record.get("generation", {}), dict)
        else {}
    )
    analysis = (
        record.get("analysis", {})
        if isinstance(record.get("analysis", {}), dict)
        else {}
    )
    anchor = (
        analysis.get("anchor_similarity", {})
        if isinstance(analysis.get("anchor_similarity", {}), dict)
        else {}
    )
    axis_margins = (
        anchor.get("axis_margins", {})
        if isinstance(anchor.get("axis_margins", {}), dict)
        else {}
    )
    empath = (
        analysis.get("empath_bundles", {})
        if isinstance(analysis.get("empath_bundles", {}), dict)
        else {}
    )

    nrc_profile = {}
    nrc_block = analysis.get("nrc_emotions")
    sentiment_block = analysis.get("sentiment_emotions")
    if isinstance(nrc_block, dict) and isinstance(nrc_block.get("profile"), dict):
        nrc_profile = nrc_block["profile"]
    elif isinstance(sentiment_block, dict) and isinstance(sentiment_block.get("normalized"), dict):
        nrc_profile = sentiment_block["normalized"]

    rel_path = source_path.relative_to(root_dir)
    model = generation.get("model")
    if not model and len(rel_path.parts) > 1:
        model = rel_path.parts[0]

    row: dict[str, Any] = {
        "source_relpath": rel_path.as_posix(),
        "source_file": source_path.name,
        "model": model,
        "product_id": product_id,
        "product_name": meta.get("product_name"),
        "variant": variant,
        "paraphrase_id": meta.get("paraphrase_id"),
        "condition_id": rec_id.get("condition_id"),
        "output_id": rec_id.get("output_id"),
        "word_count": (
            record.get("self_checks", {}).get("approx_word_count_full_message")
            if isinstance(record.get("self_checks", {}), dict)
            else None
        ),
        "top_match": anchor.get("top_match"),
        "correct_alignment": _safe_bool(anchor.get("correct_alignment")),
        "alignment_margin": _safe_float(anchor.get("alignment_margin")),
        "margin_extraversion": _safe_float(axis_margins.get("E_margin")),
        "margin_openness": _safe_float(axis_margins.get("O_margin")),
    }

    for key in BUNDLE_KEYS:
        row[f"empath_{key}"] = _safe_float(empath.get(key))
    for key in NRC_KEYS:
        row[f"nrc_{key}"] = _safe_float(nrc_profile.get(key))
    return row


def _dedupe_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    seen: set[tuple[Any, ...]] = set()
    deduped: list[dict[str, Any]] = []
    duplicates = 0

    for row in rows:
        key = (
            row.get("model"),
            row.get("output_id"),
            row.get("variant"),
            row.get("product_id"),
            row.get("paraphrase_id"),
        )
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        deduped.append(row)

    return deduped, duplicates


def build_summary_rows(root_dir: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows: list[dict[str, Any]] = []
    stats = {"scanned_files": 0, "skipped_files": 0, "raw_rows": 0}

    for fp in sorted(root_dir.rglob("*.json")):
        if fp.name.endswith("_summary.json"):
            continue
        stats["scanned_files"] += 1
        try:
            payload = _read_json(fp)
            for record in _iter_records(payload):
                row = _extract_row(record, fp, root_dir)
                if row is not None:
                    rows.append(row)
        except Exception:
            stats["skipped_files"] += 1
            continue

    stats["raw_rows"] = len(rows)
    return rows, stats


def write_summary_csv(rows: list[dict[str, Any]], out_csv: Path) -> None:
    if not rows:
        raise RuntimeError("No valid analysed rows found. Nothing to write.")

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild stimuli_analysis_summary.csv from stimuli_out_analysed JSON files."
    )
    parser.add_argument("--root-dir", type=Path, default=DEFAULT_ANALYSED_ROOT)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows, stats = build_summary_rows(args.root_dir)
    deduped_rows, duplicates = _dedupe_rows(rows)
    write_summary_csv(deduped_rows, args.output_csv)

    print("=== Rebuilt stimuli_analysis_summary.csv ===")
    print(f"root_dir={args.root_dir}")
    print(f"scanned_files={stats['scanned_files']} skipped_files={stats['skipped_files']}")
    print(f"raw_rows={stats['raw_rows']} duplicates_removed={duplicates}")
    print(f"written_rows={len(deduped_rows)}")
    print(f"output_csv={args.output_csv}")


if __name__ == "__main__":
    main()
