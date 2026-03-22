# Stimulus_Builder Project Map

High-level map of the current Stimulus_Builder architecture, file ownership, and expected data flow.

## 1. Purpose

`Stimulus_Builder/` contains the end-to-end workflow for:

1. selecting canonical message stimuli,
2. building participant trial designs,
3. collecting persona-based LLM ratings,
4. exporting analysis artifacts.

## 2. Primary Workflow (Canonical)

### Build and validation

- `build_simplified_experiment.py`
  - Builds canonical 3-condition experiment assets.
  - Inputs: `stimuli_out/<model_alias>/*.json`
  - Outputs: `design_out_v2/` and `participants_out/`
- `prepare_rating_pipeline.py`
  - Performs pre-flight checks before rating calls.
  - Can auto-build missing assets (`--build-if-missing`).

### Rating execution

- `run_ratings.py`
  - Runs structured LLM rating calls per trial.
  - Supports resume and `--test`.
  - Writes one JSON per trial into `persona_ratings_out/`.
- `llm_interface.py`
  - API client glue and structured rating call function.
- `retry_logic.py`
  - Retry strategy for parse/validation failures.

### Analysis and exports

- `analyze_ratings.py`
  - Script-based descriptive + OLS outputs.
- `analyze_ratings_pipeline.ipynb`
  - Notebook-based stepwise analysis and interpretation.
- `rebuild_stimuli_analysis_summary.py`
  - Rebuilds `stimuli_out_analysed/stimuli_analysis_summary.csv`.

## 3. Generation Utilities (Used Upstream, Not Required For Rating-Only Runs)

- `run_batch.py`
- `generation.py`
- `prompts.py`
- `records.py`
- `validation.py`
- `config.py`

These are used when creating/validating stimuli, but are not required if finalized stimuli already exist.

## 4. Key Data Directories

- `stimuli_out/<model_alias>/`
  - Source stimuli JSON files (input to design build).
- `design_out_v2/`
  - Design artifacts consumed by rating scripts.
- `participants_out/`
  - Participant definitions by persona type.
- `persona_templates/`
  - Persona cards and rating behavior guidance.
- `persona_ratings_out/`
  - Trial-level rating outputs (`status: ok|error`).
- `stimuli_out_analysed/`
  - Analysis outputs and summary CSVs.

## 5. Core File Contracts

### `design_out_v2/stimuli_index.json`

- Full readable stimulus catalog from chosen source folder.
- One row per source stimulus JSON.

### `design_out_v2/stimuli_canonical_p1.json`

- Canonical subset for experiment:
  - exactly `GENERIC`, `E_PLUS`, `O_PLUS` per product.
- Selection rule:
  - `E_PLUS` and `O_PLUS`: `paraphrase_id == 1`
  - `GENERIC`: smallest available `paraphrase_id`

### `design_out_v2/PER_*_design.json`

- Participant-specific 18-trial schedule.
- Includes actual message text and assigned condition order.

### `persona_ratings_out/*.json`

- One JSON per completed trial rating.
- Expected top-level keys:
  - `status`, `participant`, `trial`, `rating`
- Analysis scripts use only `status == "ok"` rows.

## 6. Notebooks and Archive Policy

- Active analysis notebook:
  - `analyze_ratings_pipeline.ipynb`
- Legacy notebooks and backups:
  - store in `_archive/` to preserve provenance.

## 7. Ownership and Safety Rules

- Treat `Stimulus_Builder/` as the authoritative experiment module.
- Prefer script entry points for reproducibility.
- Keep branch commits scoped to this folder when possible.
- Do not delete historical artifacts unless archived first.

## 8. Quick Entry Points

- Build designs:
  - `python Stimulus_Builder/build_simplified_experiment.py`
- Pre-flight:
  - `python Stimulus_Builder/prepare_rating_pipeline.py`
- Test ratings:
  - `python Stimulus_Builder/run_ratings.py --test`
- Full ratings:
  - `python Stimulus_Builder/run_ratings.py`
- Analyze:
  - `python Stimulus_Builder/analyze_ratings.py`
