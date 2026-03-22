import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_STIMULI_MODEL = "gpt-4o"
STIMULI_DIR = BASE_DIR / "stimuli_out" / DEFAULT_STIMULI_MODEL
DESIGN_DIR = BASE_DIR / "design_out_v2"
PARTICIPANTS_DIR = BASE_DIR / "participants_out"
RATINGS_DIR = BASE_DIR / "persona_ratings_out"
TEMPLATES_DIR = BASE_DIR / "persona_templates"
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
        from dotenv import load_dotenv
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


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _count_json(path: Path) -> int:
    if not path.exists():
        return 0
    return len(list(path.glob("*.json")))


def _check_openai_package() -> bool:
    return importlib.util.find_spec("openai") is not None


def _check_api_key() -> bool:
    return bool(os.getenv("CHAT_AI_API_KEY"))


def _maybe_build_design_assets(
    build_if_missing: bool,
    participants_per_type: int,
    stimuli_model: str,
    stimuli_dir: Path | None,
) -> None:
    index_path = DESIGN_DIR / "stimuli_index.json"
    canonical_path = DESIGN_DIR / "stimuli_canonical_p1.json"
    e_participants = PARTICIPANTS_DIR / "TYPE_E_HIGH_participants.json"
    o_participants = PARTICIPANTS_DIR / "TYPE_O_HIGH_participants.json"

    has_core = (
        index_path.exists()
        and canonical_path.exists()
        and e_participants.exists()
        and o_participants.exists()
    )

    if has_core or not build_if_missing:
        return

    cmd = [
        sys.executable,
        str(BASE_DIR / "build_simplified_experiment.py"),
        "--participants-per-type",
        str(participants_per_type),
    ]
    if stimuli_dir is not None:
        cmd.extend(["--stimuli-dir", str(stimuli_dir)])
    else:
        cmd.extend(["--stimuli-model", stimuli_model])
    print(f"[build] missing assets detected -> running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=str(BASE_DIR))


def _check_participants_file(path: Path, expected_count: int) -> tuple[bool, str]:
    if not path.exists():
        return False, "missing"
    try:
        rows = _read_json(path)
        if not isinstance(rows, list):
            return False, "not a list"
        if len(rows) != expected_count:
            return False, f"count={len(rows)} expected={expected_count}"
        required = {"participant_type", "persona_id", "respondent_seed"}
        for idx, row in enumerate(rows):
            if not isinstance(row, dict):
                return False, f"row {idx} is not an object"
            if set(row.keys()) != required:
                return False, f"row {idx} keys mismatch"
        return True, "ok"
    except Exception as exc:
        return False, f"invalid JSON: {exc}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pre-flight checks for the Stimulus_Builder rating pipeline."
    )
    parser.add_argument(
        "--participants-per-type",
        type=int,
        default=50,
        help="Expected participants per persona type.",
    )
    parser.add_argument(
        "--build-if-missing",
        action="store_true",
        help="Auto-run build_simplified_experiment.py if core design assets are missing.",
    )
    parser.add_argument(
        "--stimuli-model",
        default=DEFAULT_STIMULI_MODEL,
        help="Model alias under stimuli_out/ used as the source set for design build/checks.",
    )
    parser.add_argument(
        "--stimuli-dir",
        type=Path,
        default=None,
        help="Override source stimuli directory. Takes precedence over --stimuli-model.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    _load_env_files_once()
    resolved_stimuli_dir = args.stimuli_dir or (BASE_DIR / "stimuli_out" / args.stimuli_model)
    _maybe_build_design_assets(
        args.build_if_missing,
        args.participants_per_type,
        args.stimuli_model,
        args.stimuli_dir,
    )

    checks: list[tuple[str, bool, str]] = []

    stimuli_count = _count_json(resolved_stimuli_dir)
    checks.append(
        (
            "stimuli_source_json",
            stimuli_count > 0,
            f"dir={resolved_stimuli_dir} count={stimuli_count}",
        )
    )

    index_path = DESIGN_DIR / "stimuli_index.json"
    canonical_path = DESIGN_DIR / "stimuli_canonical_p1.json"
    checks.append(("stimuli_index_exists", index_path.exists(), str(index_path)))
    checks.append(("stimuli_canonical_exists", canonical_path.exists(), str(canonical_path)))

    e_ok, e_msg = _check_participants_file(
        PARTICIPANTS_DIR / "TYPE_E_HIGH_participants.json",
        args.participants_per_type,
    )
    o_ok, o_msg = _check_participants_file(
        PARTICIPANTS_DIR / "TYPE_O_HIGH_participants.json",
        args.participants_per_type,
    )
    checks.append(("participants_TYPE_E_HIGH", e_ok, e_msg))
    checks.append(("participants_TYPE_O_HIGH", o_ok, o_msg))

    design_files = list(DESIGN_DIR.glob("PER_*_design.json"))
    expected_design_files = args.participants_per_type * 2
    checks.append(
        (
            "participant_design_files",
            len(design_files) == expected_design_files,
            f"count={len(design_files)} expected={expected_design_files}",
        )
    )

    e_template = TEMPLATES_DIR / "TYPE_E_HIGH.json"
    o_template = TEMPLATES_DIR / "TYPE_O_HIGH.json"
    checks.append(("persona_template_TYPE_E_HIGH", e_template.exists(), str(e_template)))
    checks.append(("persona_template_TYPE_O_HIGH", o_template.exists(), str(o_template)))

    checks.append(("python_openai_installed", _check_openai_package(), "pip install openai"))
    checks.append(("api_key_available", _check_api_key(), "CHAT_AI_API_KEY"))

    ratings_existing = _count_json(RATINGS_DIR)
    checks.append(("existing_rating_outputs", True, f"count={ratings_existing}"))

    print("\n=== Rating Pipeline Pre-flight ===")
    for name, ok, msg in checks:
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {name}: {msg}")

    failures = [c for c in checks if not c[1]]
    if failures:
        print(f"\nPre-flight failed with {len(failures)} issue(s).")
        sys.exit(1)

    print("\nPre-flight passed. Ready to run ratings.")
    print("Suggested test run:")
    print(f"  {sys.executable} {BASE_DIR / 'run_ratings.py'} --test")
    print("Suggested full run:")
    print(f"  {sys.executable} {BASE_DIR / 'run_ratings.py'}")


if __name__ == "__main__":
    main()
