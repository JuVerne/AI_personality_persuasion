# Stimulus_Builder Project Map

This file defines the current working structure for this repository.

## Active Pipeline (keep and maintain)

- `build_simplified_experiment.py`
  - Builds:
    - `design_out_v2/stimuli_index.json`
    - `design_out_v2/stimuli_canonical_p1.json`
    - participant files in `participants_out/`
    - per-participant design files in `design_out_v2/`
- `run_ratings.py`
  - Executes one LLM rating call per trial.
  - Writes one output JSON per trial to `persona_ratings_out/`.
  - Supports resume and test mode.
- `prepare_rating_pipeline.py`
  - Pre-flight checks before ratings.
  - Optional auto-build of missing design assets.
- `analyze_ratings.py`
  - Post-run descriptive summaries and OLS regression outputs.
- `rebuild_stimuli_analysis_summary.py`
  - Rebuilds `stimuli_out_analysed/stimuli_analysis_summary.csv` from analysed JSON files.
- `llm_interface.py`
  - OpenAI client setup and structured rating call (`rate_ad_structured`).
  - Persona context now loads from `persona_templates/*.json`.
- `retry_logic.py`
  - Parse/validation retry logic for strict JSON output.

## Generation Pipeline (legacy but still usable)

- `run_batch.py`, `generation.py`, `prompts.py`, `records.py`, `validation.py`, `config.py`
  - Used for stimulus generation.
  - Not required for rating-only runs once stimuli are already finalized.

## Data / Outputs

- Source stimuli for simplified experiment:
  - `stimuli_out/<model_alias>/*.json` (selected via `--stimuli-model` or `--stimuli-dir`)
- Built design assets:
  - `design_out_v2/`

  1) stimuli_index.json:
    Full catalog of all readable stimuli in the chosen source folder (one row per stimulus JSON).
    Built by build_simplified_experiment.py (line 37).
    Written to build_simplified_experiment.py (line 267).

  2) stimuli_canonical_p1.json
    Reduced “experiment set”: for each product, exactly GENERIC, E_PLUS, O_PLUS.
    Logic: E_PLUS/O_PLUS must be paraphrase_id == 1; GENERIC picks the smallest available paraphrase id.
    Built by build_simplified_experiment.py (line 72), validated at build_simplified_experiment.py (line 270).

  3) PER_*HIGH_0050_design.json (and other *_design.json)
  Participant-specific trial schedule (18 trials), including condition order and the actual ad text used per trial.
  Built by build_simplified_experiment.py (line 150), saved at build_simplified_experiment.py (line 220).
  Current design files explicitly show source stimuli came from stimuli_out/gpt-4o via experiment.source_stimuli_dir (e.g. PER_EHIGH_0050_design.json (line 9)).

- Ratings output:
  - `persona_ratings_out/`


## Notebooks Status

- Primary notebook candidates:
  - `GWDG_Message_builder.ipynb`
  - `persona_rater_v2.ipynb`
- Likely redundant / cleanup candidates:
  - Archived in `_archive/`:
    - `_archive/GWDG_Message_builder copy.ipynb`
    - `_archive/notebooks/analysis.ipynb`
    - `_archive/notebooks/generate.ipynb`

## Cleanup Candidates (review before deletion)

- Root-level folders outside `Stimulus_Builder`:
  - Archived under `_archive/root_level_outputs/`:
    - `_archive/root_level_outputs/design_out_v2_root/`
    - `_archive/root_level_outputs/participants_out_root/`
- Archived legacy design files:
  - `_archive/design_out_v2_legacy/` (old 30-trial schema)
- Unused helper in scripts:
  - `prompts.py::build_batch_prompts` appears unused in current code references.

## Rule of Thumb Going Forward

- Treat this folder as authoritative:
  - `Stimulus_Builder/`
- Prefer scripts over ad-hoc notebook steps for reproducibility.
- Keep only one canonical notebook per task and move backups to a dedicated archive folder.
