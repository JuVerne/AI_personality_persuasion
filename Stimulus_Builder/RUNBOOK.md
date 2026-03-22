# Stimulus_Builder Runbook

Canonical, reproducible execution guide for the simplified 3-condition rating experiment.

## Scope

This runbook covers:

1. Building participant-level trial designs.
2. Pre-flight validation.
3. Running LLM-based persona ratings.
4. Running analysis exports.
5. Rebuilding summary CSV artifacts.

## Prerequisites

- Run commands from repository root (`AI_personality_persuasion-1/`).
- Python environment has required packages installed.
- `.env` contains an API key for rating calls.
  - `CHAT_AI_API_KEY` is the key checked by `prepare_rating_pipeline.py`.
- Stimuli JSON files exist in `Stimulus_Builder/stimuli_out/<model_alias>/`.

Optional environment setup from YAML:

```bash
conda env create -f requirements.yml
conda activate llm
```

## Step 1: Build Design Assets

Default (uses `stimuli_out/gpt-4o`):

```bash
python Stimulus_Builder/build_simplified_experiment.py
```

Model-specific source:

```bash
python Stimulus_Builder/build_simplified_experiment.py --stimuli-model qwen30b
```

Direct source path:

```bash
python Stimulus_Builder/build_simplified_experiment.py --stimuli-dir Stimulus_Builder/stimuli_out/mistral_large
```

Expected outputs:

- `Stimulus_Builder/design_out_v2/stimuli_index.json`
- `Stimulus_Builder/design_out_v2/stimuli_canonical_p1.json`
- `Stimulus_Builder/participants_out/TYPE_E_HIGH_participants.json`
- `Stimulus_Builder/participants_out/TYPE_O_HIGH_participants.json`
- `Stimulus_Builder/design_out_v2/PER_*_design.json`

## Step 2: Pre-flight Validation

Standard check:

```bash
python Stimulus_Builder/prepare_rating_pipeline.py
```

Auto-build missing assets:

```bash
python Stimulus_Builder/prepare_rating_pipeline.py --build-if-missing
```

Model-specific pre-flight:

```bash
python Stimulus_Builder/prepare_rating_pipeline.py --stimuli-model gpt-4o
```

Pre-flight verifies:

- source stimuli count > 0
- design and participant files exist and are internally consistent
- persona templates exist
- `openai` package is installed
- API key is available

## Step 3: Run Ratings

Smoke test mode (safe first run):

```bash
python Stimulus_Builder/run_ratings.py --test
```

`--test` behavior:

- 1 participant
- 3 trials
- up to 3 model calls (less if resume skips)
- writes trial output JSON to `Stimulus_Builder/persona_ratings_out/`

Full run:

```bash
python Stimulus_Builder/run_ratings.py
```

## Step 4: Analyze Ratings

Script analysis:

```bash
python Stimulus_Builder/analyze_ratings.py
```

Primary output folder:

- `Stimulus_Builder/stimuli_out_analysed/ratings_analysis/`

Notebook analysis option:

- `Stimulus_Builder/analyze_ratings_pipeline.ipynb`
- Includes validation, descriptives, plots, regression, manipulation checks, and CSV exports.

## Step 5: Rebuild Stimuli Summary CSV

If `stimuli_analysis_summary.csv` is stale or missing:

```bash
python Stimulus_Builder/rebuild_stimuli_analysis_summary.py
```

Writes:

- `Stimulus_Builder/stimuli_out_analysed/stimuli_analysis_summary.csv`

## Troubleshooting

### Pre-flight fails on API key

- Ensure `.env` contains `CHAT_AI_API_KEY=<your_key>`.

### No ratings found in analysis

- Check `persona_ratings_out/` has `status: "ok"` JSON records.
- Confirm you are pointing to the right folder.

### Notebook path issues

- Re-run notebook from top so the path-resolution cell resets `INPUT_PATH`.

## Reproducibility Checklist

- Keep one command history per run (or save terminal log).
- Do not mix outputs from different stimulus source models unless intentional.
- Commit scripts/docs before large reruns.
- Archive legacy notebooks in `_archive/` rather than deleting run history.
