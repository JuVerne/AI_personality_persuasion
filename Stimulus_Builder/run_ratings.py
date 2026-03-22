import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from llm_interface import DEFAULT_RATER_MODEL, get_openai_client, rate_ad_structured

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DESIGN_DIR = BASE_DIR / "design_out_v2"
DEFAULT_OUT_DIR = BASE_DIR / "persona_ratings_out"
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

    env_candidates = [BASE_DIR / ".env", BASE_DIR.parent / ".env"]
    for env_path in env_candidates:
        if env_path.exists():
            if has_dotenv:
                load_dotenv(dotenv_path=env_path, override=False)
            else:
                _load_dotenv_fallback(env_path)

    _ENV_LOADED = True


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _slugify(value: str, max_len: int = 40) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-_.")
    if not slug:
        slug = "model"
    return slug[:max_len]


def _temperature_tag(temperature: float) -> str:
    text = f"{temperature:.4f}".rstrip("0").rstrip(".")
    if not text:
        text = "0"
    return text.replace("-", "m").replace(".", "p")


def _rating_out_path(
    out_dir: Path,
    persona_id: str,
    trial: dict[str, Any],
    model: str,
    temperature: float,
) -> Path:
    trial_index = int(trial["trial_index"])
    output_id = trial["output_id"]
    model_tag = _slugify(model)
    temp_tag = _temperature_tag(temperature)
    filename = (
        f"{persona_id}__t{trial_index:02d}__{output_id}"
        f"__m-{model_tag}__temp-{temp_tag}.json"
    )
    return out_dir / filename


def _is_completed_ok(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        payload = _read_json(path)
        return payload.get("status") == "ok"
    except Exception:
        return False


def _format_duration(seconds: float) -> str:
    whole = max(0, int(round(seconds)))
    hours, rem = divmod(whole, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def _print_progress(
    processed: int,
    total: int,
    n_calls: int,
    n_skipped: int,
    n_failed: int,
    started_at: float,
) -> None:
    elapsed = time.monotonic() - started_at
    throughput = processed / elapsed if elapsed > 0 else 0.0
    remaining = max(0, total - processed)
    eta = (remaining / throughput) if throughput > 0 else 0.0
    print(
        f"[progress] {processed}/{total} saved={n_calls} skipped={n_skipped} failed={n_failed} "
        f"elapsed={_format_duration(elapsed)} eta={_format_duration(eta)}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one LLM rating call per trial and store one JSON per trial."
    )
    parser.add_argument("--design-dir", type=Path, default=DEFAULT_DESIGN_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--model", default=DEFAULT_RATER_MODEL)
    parser.add_argument(
        "--api-key-env",
        default="CHAT_AI_API_KEY",
        help="Environment variable name containing the API key to use for this run (default: CHAT_AI_API_KEY).",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Override API base URL for this run (e.g. https://chat-ai.academiccloud.de/v1).",
    )
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument(
        "--min-call-interval-seconds",
        type=float,
        default=0.0,
        help="Minimum spacing between API call starts. Use this to throttle request rate.",
    )
    parser.add_argument(
        "--request-timeout-seconds",
        type=float,
        default=120.0,
        help="Per-request timeout passed to the OpenAI client.",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=25,
        help="Print progress every N processed trials (including skips).",
    )
    parser.add_argument(
        "--participant-type",
        choices=["TYPE_E_HIGH", "TYPE_O_HIGH", "ALL"],
        default="ALL",
        help="Filter design files by participant type.",
    )
    parser.add_argument(
        "--max-participants",
        type=int,
        default=None,
        help="Cap number of participants processed.",
    )
    parser.add_argument(
        "--max-trials-per-participant",
        type=int,
        default=None,
        help="Cap number of trials processed per participant.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Shortcut test mode (1 participant, 3 trials each).",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        default=True,
        help="Skip already-saved trial output files (default true).",
    )
    parser.add_argument(
        "--no-resume",
        action="store_false",
        dest="resume",
        help="Re-run trials even if output files already exist.",
    )
    return parser.parse_args()


def load_design_paths(design_dir: Path) -> list[Path]:
    return sorted(design_dir.glob("*_design.json"))


def main() -> None:
    args = parse_args()
    _load_env_files_once()
    if args.test:
        if args.max_participants is None:
            args.max_participants = 1
        if args.max_trials_per_participant is None:
            args.max_trials_per_participant = 3

    design_paths = load_design_paths(args.design_dir)
    if not design_paths:
        raise RuntimeError(f"No design files found in {args.design_dir}")

    explicit_api_key = None
    if args.api_key_env:
        explicit_api_key = os.getenv(args.api_key_env)
        if not explicit_api_key:
            raise RuntimeError(
                f"--api-key-env was set to {args.api_key_env}, but that variable is empty or missing."
            )

    client = get_openai_client(api_key=explicit_api_key, base_url=args.base_url)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    jobs: list[tuple[dict[str, Any], str, str, dict[str, Any]]] = []
    processed_participants = 0
    for design_path in design_paths:
        design = _read_json(design_path)
        participant = design["participant"]
        persona_id = participant["persona_id"]
        participant_type = participant["participant_type"]

        if args.participant_type != "ALL" and participant_type != args.participant_type:
            continue

        processed_participants += 1
        if args.max_participants is not None and processed_participants > args.max_participants:
            break

        trials = design["trials"]
        if args.max_trials_per_participant is not None:
            trials = trials[: args.max_trials_per_participant]

        for trial in trials:
            jobs.append((participant, participant_type, persona_id, trial))

    if not jobs:
        raise RuntimeError("No trials selected after applying filters.")

    n_calls = 0
    n_skipped = 0
    n_failed = 0
    total_jobs = len(jobs)
    started_at = time.monotonic()
    last_call_started_at: float | None = None

    print(
        f"[start] total_trials={total_jobs} model={args.model} temperature={args.temperature} "
        f"resume={args.resume} min_interval_s={args.min_call_interval_seconds} "
        f"timeout_s={args.request_timeout_seconds}"
    )

    for idx, (participant, participant_type, persona_id, trial) in enumerate(jobs, start=1):
        out_path = _rating_out_path(
            args.out_dir,
            persona_id,
            trial,
            model=args.model,
            temperature=args.temperature,
        )
        if args.resume and _is_completed_ok(out_path):
            n_skipped += 1
            if idx % max(1, args.progress_every) == 0:
                _print_progress(
                    processed=idx,
                    total=total_jobs,
                    n_calls=n_calls,
                    n_skipped=n_skipped,
                    n_failed=n_failed,
                    started_at=started_at,
                )
            continue

        if args.min_call_interval_seconds > 0 and last_call_started_at is not None:
            elapsed_since_last = time.monotonic() - last_call_started_at
            sleep_needed = args.min_call_interval_seconds - elapsed_since_last
            if sleep_needed > 0:
                time.sleep(sleep_needed)

        try:
            last_call_started_at = time.monotonic()
            rating = rate_ad_structured(
                client=client,
                model=args.model,
                ad_text=trial["full_message"],
                participant_type=participant_type,
                condition_label=trial.get("condition_label"),
                product_name=trial.get("product_name"),
                temperature=args.temperature,
                max_retries=args.max_retries,
                request_timeout_seconds=args.request_timeout_seconds,
            )
            payload = {
                "timestamp_utc": utc_now_iso(),
                "status": "ok",
                "model": args.model,
                "model_temperature": args.temperature,
                "request_timeout_seconds": args.request_timeout_seconds,
                "participant": participant,
                "trial": trial,
                "rating": rating,
            }
            _write_json(out_path, payload)
            n_calls += 1
            print(f"[saved] {out_path}")
        except Exception as exc:
            n_failed += 1
            payload = {
                "timestamp_utc": utc_now_iso(),
                "status": "error",
                "model": args.model,
                "model_temperature": args.temperature,
                "request_timeout_seconds": args.request_timeout_seconds,
                "participant": participant,
                "trial": trial,
                "error": str(exc),
            }
            _write_json(out_path, payload)
            print(f"[error] {out_path}: {exc}")

        if idx % max(1, args.progress_every) == 0 or idx == total_jobs:
            _print_progress(
                processed=idx,
                total=total_jobs,
                n_calls=n_calls,
                n_skipped=n_skipped,
                n_failed=n_failed,
                started_at=started_at,
            )

    elapsed = time.monotonic() - started_at
    avg_per_trial = elapsed / total_jobs if total_jobs else 0.0
    print(
        f"[done] api_calls={n_calls} skipped={n_skipped} failed={n_failed} "
        f"total_trials={total_jobs} elapsed={_format_duration(elapsed)} "
        f"avg_per_trial={avg_per_trial:.2f}s out_dir={args.out_dir}"
    )


if __name__ == "__main__":
    main()
