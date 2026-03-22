# Stimulus_Builder Runbook

This is the canonical execution flow for the simplified 3-condition experiment.

## 1. Build Design Assets

```bash
python Stimulus_Builder/build_simplified_experiment.py
```

Creates:
- `design_out_v2/stimuli_index.json`
- `design_out_v2/stimuli_canonical_p1.json`
- participant files in `participants_out/`
- participant design files in `design_out_v2/`

To rate a different model's generated stimuli, choose its source folder:

```bash
python Stimulus_Builder/build_simplified_experiment.py --stimuli-model qwen30b
```

You can also pass a direct path:

```bash
python Stimulus_Builder/build_simplified_experiment.py --stimuli-dir Stimulus_Builder/stimuli_out/mistral_large
```

## 2. Pre-flight Check

```bash
python Stimulus_Builder/prepare_rating_pipeline.py
```

Optional auto-build when files are missing:

```bash
python Stimulus_Builder/prepare_rating_pipeline.py --build-if-missing
```

Model-specific pre-flight:

```bash
python Stimulus_Builder/prepare_rating_pipeline.py --stimuli-model gpt-4o
```

## 3. Run Ratings

Test mode:

runs a small smoke test of the rating pipeline.

In this script, --test means:

process only 1 participant
process only 3 trials for that participant
make up to 3 LLM rating calls (fewer if resume skips existing files)
write one output JSON per trial to Stimulus_Builder/persona_ratings_out
It still uses the normal LLM path (llm_interface.rate_ad_structured), so it requires:

openai installed
API key set (OPENAI_API_KEY or CHAT_AI_API_KEY)
valid design files already in Stimulus_Builder/design_out_v2

```bash
python Stimulus_Builder/run_ratings.py --test
```

Full run:

```bash
python Stimulus_Builder/run_ratings.py
```

## 4. Analyze Ratings

```bash
python Stimulus_Builder/analyze_ratings.py
```

Outputs are written to:
- `stimuli_out_analysed/ratings_analysis/`

## 5. Rebuild Stimuli Analysis Summary CSV

If `stimuli_out_analysed/stimuli_analysis_summary.csv` is stale/empty:

```bash
python Stimulus_Builder/rebuild_stimuli_analysis_summary.py
```

## Notes

- Active stimulus generator notebook: `GWDG_Message_builder.ipynb`
- Active persona rater notebook reference: `persona_rater_v2.ipynb`
- Archived backups are in `_archive/`
