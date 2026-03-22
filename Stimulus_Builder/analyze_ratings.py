import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import fmean
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_RATINGS_DIR = BASE_DIR / "persona_ratings_out"
DEFAULT_OUT_DIR = BASE_DIR / "stimuli_out_analysed" / "ratings_analysis"

CONDITIONS = ("GENERIC", "TARGETED", "NON_TARGETED")
PARTICIPANT_TYPES = ("TYPE_E_HIGH", "TYPE_O_HIGH")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _load_rating_rows(ratings_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fp in sorted(ratings_dir.glob("*.json")):
        try:
            payload = _read_json(fp)
            if payload.get("status") != "ok":
                continue
            participant = payload["participant"]
            trial = payload["trial"]
            rating = payload["rating"]
            q1 = int(rating["effectiveness_rating_q1"])
            q2 = int(rating["effectiveness_rating_q2"])
            rows.append(
                {
                    "source_file": fp.name,
                    "persona_id": participant["persona_id"],
                    "participant_type": participant["participant_type"],
                    "respondent_seed": participant["respondent_seed"],
                    "trial_index": int(trial["trial_index"]),
                    "product_id": trial["product_id"],
                    "product_name": trial["product_name"],
                    "condition_label": trial["condition_label"],
                    "stimulus_variant": trial["stimulus_variant"],
                    "q1": q1,
                    "q2": q2,
                    "combined": (q1 + q2) / 2.0,
                    "motivation": rating["motivation"],
                }
            )
        except Exception as exc:
            print(f"[skip] {fp}: {exc}")
    return rows


def _group_stats(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["participant_type"], row["condition_label"])].append(row)

    out: list[dict[str, Any]] = []
    for participant_type in PARTICIPANT_TYPES:
        for condition in CONDITIONS:
            key = (participant_type, condition)
            bucket = grouped.get(key, [])
            if not bucket:
                out.append(
                    {
                        "participant_type": participant_type,
                        "condition_label": condition,
                        "n": 0,
                        "mean_q1": None,
                        "mean_q2": None,
                        "mean_combined": None,
                    }
                )
                continue

            out.append(
                {
                    "participant_type": participant_type,
                    "condition_label": condition,
                    "n": len(bucket),
                    "mean_q1": round(fmean(r["q1"] for r in bucket), 4),
                    "mean_q2": round(fmean(r["q2"] for r in bucket), 4),
                    "mean_combined": round(fmean(r["combined"] for r in bucket), 4),
                }
            )
    return out


def _condition_contrasts(group_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_type: dict[str, dict[str, float | None]] = defaultdict(dict)
    for row in group_rows:
        by_type[row["participant_type"]][row["condition_label"]] = row["mean_combined"]

    contrasts: list[dict[str, Any]] = []
    for participant_type in PARTICIPANT_TYPES:
        means = by_type.get(participant_type, {})
        t = means.get("TARGETED")
        n = means.get("NON_TARGETED")
        g = means.get("GENERIC")

        def _diff(a: float | None, b: float | None) -> float | None:
            if a is None or b is None:
                return None
            return round(a - b, 4)

        contrasts.append(
            {
                "participant_type": participant_type,
                "targeted_minus_generic": _diff(t, g),
                "targeted_minus_non_targeted": _diff(t, n),
                "non_targeted_minus_generic": _diff(n, g),
            }
        )
    return contrasts


def _transpose(m: list[list[float]]) -> list[list[float]]:
    return [list(col) for col in zip(*m)]


def _matmul(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    bt = _transpose(b)
    out: list[list[float]] = []
    for row in a:
        out_row: list[float] = []
        for col in bt:
            out_row.append(sum(x * y for x, y in zip(row, col)))
        out.append(out_row)
    return out


def _matvec(a: list[list[float]], v: list[float]) -> list[float]:
    return [sum(x * y for x, y in zip(row, v)) for row in a]


def _invert_matrix(m: list[list[float]]) -> list[list[float]]:
    n = len(m)
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]

    for i in range(n):
        pivot_row = max(range(i, n), key=lambda r: abs(aug[r][i]))
        if abs(aug[pivot_row][i]) < 1e-12:
            raise RuntimeError("Matrix is singular; cannot invert.")
        aug[i], aug[pivot_row] = aug[pivot_row], aug[i]

        pivot = aug[i][i]
        aug[i] = [x / pivot for x in aug[i]]

        for r in range(n):
            if r == i:
                continue
            factor = aug[r][i]
            aug[r] = [rv - factor * iv for rv, iv in zip(aug[r], aug[i])]

    return [row[n:] for row in aug]


def _regression_design_row(row: dict[str, Any]) -> list[float]:
    is_targeted = 1.0 if row["condition_label"] == "TARGETED" else 0.0
    is_non_targeted = 1.0 if row["condition_label"] == "NON_TARGETED" else 0.0
    is_type_o = 1.0 if row["participant_type"] == "TYPE_O_HIGH" else 0.0
    return [
        1.0,  # intercept
        is_targeted,
        is_non_targeted,
        is_type_o,
        is_targeted * is_type_o,
        is_non_targeted * is_type_o,
    ]


def _run_ols(rows: list[dict[str, Any]], y_key: str) -> dict[str, Any]:
    if not rows:
        raise RuntimeError("No rows available for regression.")

    x = [_regression_design_row(r) for r in rows]
    y = [float(r[y_key]) for r in rows]

    xt = _transpose(x)
    xtx = _matmul(xt, x)
    xtx_inv = _invert_matrix(xtx)
    xty = _matvec(xt, y)
    beta = _matvec(xtx_inv, xty)

    y_hat = [sum(b * xi for b, xi in zip(beta, row_x)) for row_x in x]
    residuals = [yi - ypi for yi, ypi in zip(y, y_hat)]
    sse = sum(r * r for r in residuals)
    y_bar = fmean(y)
    sst = sum((yi - y_bar) ** 2 for yi in y)
    r2 = 1.0 - (sse / sst if sst > 0 else 0.0)

    n = len(y)
    k = len(beta)
    dof = max(n - k, 1)
    sigma2 = sse / dof
    var_beta = [[sigma2 * x for x in row] for row in xtx_inv]
    se_beta = [math.sqrt(max(var_beta[i][i], 0.0)) for i in range(k)]
    t_beta = [beta[i] / se_beta[i] if se_beta[i] > 0 else None for i in range(k)]

    coef_names = [
        "Intercept[E_HIGH + GENERIC baseline]",
        "Condition_TARGETED_vs_GENERIC (E_HIGH)",
        "Condition_NON_TARGETED_vs_GENERIC (E_HIGH)",
        "ParticipantType_O_HIGH_shift_at_GENERIC",
        "Interaction_TARGETED_x_O_HIGH",
        "Interaction_NON_TARGETED_x_O_HIGH",
    ]

    coefficients = []
    for i, name in enumerate(coef_names):
        coefficients.append(
            {
                "term": name,
                "beta": round(beta[i], 6),
                "std_error": round(se_beta[i], 6),
                "t_value": round(t_beta[i], 6) if t_beta[i] is not None else None, # 
            }
        )

    return {
        "outcome": y_key,
        "n": n,
        "k": k,
        "degrees_of_freedom": dof,
        "r_squared": round(r2, 6),
        "sse": round(sse, 6),
        "coefficients": coefficients,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze persona rating outputs with descriptive stats and OLS regression."
    )
    parser.add_argument("--ratings-dir", type=Path, default=DEFAULT_RATINGS_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = _load_rating_rows(args.ratings_dir)
    if not rows:
        raise RuntimeError(f"No successful rating rows found in {args.ratings_dir}")

    args.out_dir.mkdir(parents=True, exist_ok=True)

    row_fields = [
        "source_file",
        "persona_id",
        "participant_type",
        "respondent_seed",
        "trial_index",
        "product_id",
        "product_name",
        "condition_label",
        "stimulus_variant",
        "q1",
        "q2",
        "combined",
        "motivation",
    ]
    _write_csv(args.out_dir / "ratings_rows.csv", rows, row_fields)

    group_rows = _group_stats(rows)
    _write_csv(
        args.out_dir / "descriptive_by_type_condition.csv",
        group_rows,
        ["participant_type", "condition_label", "n", "mean_q1", "mean_q2", "mean_combined"],
    )

    contrasts = _condition_contrasts(group_rows)
    _write_csv(
        args.out_dir / "condition_contrasts.csv",
        contrasts,
        [
            "participant_type",
            "targeted_minus_generic",
            "targeted_minus_non_targeted",
            "non_targeted_minus_generic",
        ],
    )

    regressions = {
        "q1": _run_ols(rows, "q1"),
        "q2": _run_ols(rows, "q2"),
        "combined": _run_ols(rows, "combined"),
    }
    _write_json(args.out_dir / "regression_summary.json", regressions)

    top = {
        "n_rows": len(rows),
        "n_unique_personas": len({r["persona_id"] for r in rows}),
        "n_unique_products": len({r["product_id"] for r in rows}),
        "output_dir": str(args.out_dir),
    }
    _write_json(args.out_dir / "analysis_overview.json", top)

    print("=== Analysis Complete ===")
    print(f"rows={top['n_rows']} personas={top['n_unique_personas']} products={top['n_unique_products']}")
    print(f"wrote: {args.out_dir / 'ratings_rows.csv'}")
    print(f"wrote: {args.out_dir / 'descriptive_by_type_condition.csv'}")
    print(f"wrote: {args.out_dir / 'condition_contrasts.csv'}")
    print(f"wrote: {args.out_dir / 'regression_summary.json'}")
    print(f"wrote: {args.out_dir / 'analysis_overview.json'}")


if __name__ == "__main__":
    main()
