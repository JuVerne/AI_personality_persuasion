import argparse
import json
import random
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_STIMULI_MODEL = "gpt-4o"
STIMULI_SOURCE_DIR = BASE_DIR / "stimuli_out" / DEFAULT_STIMULI_MODEL
DESIGN_DIR = BASE_DIR / "design_out_v2"
PARTICIPANTS_DIR = BASE_DIR / "participants_out"

INDEX_PATH = DESIGN_DIR / "stimuli_index.json"
CANONICAL_PATH = DESIGN_DIR / "stimuli_canonical_p1.json"

ALLOWED_VARIANTS = {"GENERIC", "E_PLUS", "O_PLUS"}
ORDER_CODES = ("A", "B", "C", "D", "E", "F")
ORDER_CODE_TO_CONDITION_ORDER = {
    "A": ("TARGETED", "NON_TARGETED", "GENERIC"),
    "B": ("TARGETED", "GENERIC", "NON_TARGETED"),
    "C": ("NON_TARGETED", "TARGETED", "GENERIC"),
    "D": ("NON_TARGETED", "GENERIC", "TARGETED"),
    "E": ("GENERIC", "TARGETED", "NON_TARGETED"),
    "F": ("GENERIC", "NON_TARGETED", "TARGETED"),
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_stimuli_index(stimuli_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    scanned = 0
    skipped = 0

    for path in sorted(stimuli_dir.glob("*.json")):
        scanned += 1
        try:
            payload = _read_json(path)
            row = {
                "output_id": payload["id"]["output_id"],
                "condition_id": payload["id"]["condition_id"],
                "product_id": payload["meta"]["product_id"],
                "product_name": payload["meta"]["product_name"],
                "variant": payload["meta"]["variant"],
                "paraphrase_id": int(payload["meta"]["paraphrase_id"]),
                "full_message": payload["content"]["full_message"],
            }
            rows.append(row)
        except Exception as exc:
            skipped += 1
            print(f"[skip] {path}: {exc}")

    rows.sort(
        key=lambda x: (
            x["product_id"],
            x["variant"],
            x["paraphrase_id"],
            x["output_id"],
        )
    )
    print(f"[index] scanned={scanned} indexed={len(rows)} skipped={skipped}")
    return rows


def build_stimuli_canonical_p1(index_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    per_product: dict[str, dict[str, Any]] = {}

    for row in index_rows:
        variant = row["variant"]
        if variant not in ALLOWED_VARIANTS:
            continue

        product_id = row["product_id"]
        product_bucket = per_product.setdefault(
            product_id,
            {
                "product_id": product_id,
                "product_name": row["product_name"],
                "conditions": {},
            },
        )
        conditions: dict[str, dict[str, Any]] = product_bucket["conditions"]

        if variant in {"E_PLUS", "O_PLUS"}:
            if row["paraphrase_id"] != 1:
                continue
            conditions[variant] = row
        else:
            current = conditions.get("GENERIC")
            if current is None or row["paraphrase_id"] < current["paraphrase_id"]:
                conditions["GENERIC"] = row

    canonical: list[dict[str, Any]] = []
    for product_id in sorted(per_product.keys()):
        item = per_product[product_id]
        conditions = item["conditions"]
        missing = [v for v in ("GENERIC", "E_PLUS", "O_PLUS") if v not in conditions]
        if missing:
            raise RuntimeError(f"Missing canonical variants for {product_id}: {missing}")
        canonical.append(item)

    if len(canonical) != 6:
        print(f"[warn] expected 6 products but found {len(canonical)}")
    return canonical


def build_participants(participant_type: str, n: int) -> list[dict[str, Any]]:
    if participant_type == "TYPE_E_HIGH":
        prefix = "PER_EHIGH"
        seed_base = 110_000
    elif participant_type == "TYPE_O_HIGH":
        prefix = "PER_OHIGH"
        seed_base = 220_000
    else:
        raise ValueError(f"Unsupported participant type: {participant_type}")

    return [
        {
            "participant_type": participant_type,
            "persona_id": f"{prefix}_{idx:04d}",
            "respondent_seed": seed_base + idx,
        }
        for idx in range(1, n + 1)
    ]


def _variant_map_for_type(participant_type: str) -> dict[str, str]:
    if participant_type == "TYPE_E_HIGH":
        return {
            "TARGETED": "E_PLUS",
            "NON_TARGETED": "O_PLUS",
            "GENERIC": "GENERIC",
        }
    if participant_type == "TYPE_O_HIGH":
        return {
            "TARGETED": "O_PLUS",
            "NON_TARGETED": "E_PLUS",
            "GENERIC": "GENERIC",
        }
    raise ValueError(f"Unsupported participant type: {participant_type}")


def build_design_for_participant(
    participant: dict[str, Any],
    canonical: list[dict[str, Any]],
    participant_index_zero: int,
    source_stimuli_dir: str,
) -> dict[str, Any]:
    participant_type = participant["participant_type"]
    variant_map = _variant_map_for_type(participant_type)

    products = list(canonical)
    rng = random.Random(participant["respondent_seed"])
    rng.shuffle(products)

    trials: list[dict[str, Any]] = []
    trial_index = 1

    for product_pos, product in enumerate(products):
        order_code = ORDER_CODES[(participant_index_zero + product_pos) % len(ORDER_CODES)]
        for condition_label in ORDER_CODE_TO_CONDITION_ORDER[order_code]:
            variant = variant_map[condition_label]
            stim = product["conditions"][variant]
            trials.append(
                {
                    "trial_index": trial_index,
                    "order_code": order_code,
                    "condition_label": condition_label,
                    "stimulus_variant": variant,
                    "product_id": product["product_id"],
                    "product_name": product["product_name"],
                    "condition_id": stim["condition_id"],
                    "output_id": stim["output_id"],
                    "paraphrase_id": stim["paraphrase_id"],
                    "full_message": stim["full_message"],
                }
            )
            trial_index += 1

    if len(trials) != 18:
        raise RuntimeError(
            f"Expected 18 trials for {participant['persona_id']} but got {len(trials)}"
        )

    return {
        "participant": participant,
        "experiment": {
            "design_name": "simplified_3_condition_v1",
            "source_stimuli_dir": source_stimuli_dir,
            "n_products": 6,
            "n_trials": 18,
            "conditions": ["TARGETED", "NON_TARGETED", "GENERIC"],
            "order_codes": list(ORDER_CODES),
        },
        "trials": trials,
    }


def write_design_files(
    participants: list[dict[str, Any]],
    canonical: list[dict[str, Any]],
    design_dir: Path,
    source_stimuli_dir: str,
) -> None:
    design_dir.mkdir(parents=True, exist_ok=True)
    for idx, participant in enumerate(participants):
        design = build_design_for_participant(
            participant=participant,
            canonical=canonical,
            participant_index_zero=idx,
            source_stimuli_dir=source_stimuli_dir,
        )
        out_path = design_dir / f"{participant['persona_id']}_design.json"
        _write_json(out_path, design)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build simplified 3-condition experiment assets."
    )
    parser.add_argument(
        "--stimuli-dir",
        type=Path,
        default=None,
        help="Directory containing source stimulus JSON files. Overrides --stimuli-model when set.",
    )
    parser.add_argument(
        "--stimuli-model",
        default=DEFAULT_STIMULI_MODEL,
        help="Model alias subfolder under stimuli_out/ (e.g., gpt-4o, mistral_large, qwen30b, nano).",
    )
    parser.add_argument(
        "--design-dir",
        type=Path,
        default=DESIGN_DIR,
        help="Directory for design outputs.",
    )
    parser.add_argument(
        "--participants-dir",
        type=Path,
        default=PARTICIPANTS_DIR,
        help="Directory for participant lists.",
    )
    parser.add_argument(
        "--participants-per-type",
        type=int,
        default=50,
        help="Number of participants to generate for each type.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stimuli_dir = args.stimuli_dir or (BASE_DIR / "stimuli_out" / args.stimuli_model)

    index_rows = build_stimuli_index(stimuli_dir)
    if not index_rows:
        raise RuntimeError(f"No readable stimulus JSON files found in {stimuli_dir}")
    _write_json(args.design_dir / INDEX_PATH.name, index_rows)
    print(f"[write] {args.design_dir / INDEX_PATH.name}")

    canonical_rows = build_stimuli_canonical_p1(index_rows)
    if len(canonical_rows) != 6:
        raise RuntimeError(
            "Canonical selection is incomplete. Expected all 6 products with "
            "GENERIC, E_PLUS(p1), and O_PLUS(p1)."
        )
    _write_json(args.design_dir / CANONICAL_PATH.name, canonical_rows)
    print(f"[write] {args.design_dir / CANONICAL_PATH.name}")

    e_participants = build_participants("TYPE_E_HIGH", args.participants_per_type)
    o_participants = build_participants("TYPE_O_HIGH", args.participants_per_type)

    args.participants_dir.mkdir(parents=True, exist_ok=True)
    e_path = args.participants_dir / "TYPE_E_HIGH_participants.json"
    o_path = args.participants_dir / "TYPE_O_HIGH_participants.json"
    _write_json(e_path, e_participants)
    _write_json(o_path, o_participants)
    print(f"[write] {e_path}")
    print(f"[write] {o_path}")

    write_design_files(
        e_participants,
        canonical_rows,
        args.design_dir,
        source_stimuli_dir=str(stimuli_dir),
    )
    write_design_files(
        o_participants,
        canonical_rows,
        args.design_dir,
        source_stimuli_dir=str(stimuli_dir),
    )
    print(
        f"[write] design files: {len(e_participants) + len(o_participants)} "
        f"in {args.design_dir}"
    )
    print(f"[source] stimuli_dir={stimuli_dir}")


if __name__ == "__main__":
    main()
