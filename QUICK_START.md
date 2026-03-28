# Quick Start (Stimulus_Builder)

This repo’s active workflow lives in `Stimulus_Builder/`.

## 1) Environment

Minimal dependencies (enough to run the scripts):

```bash
pip install -r requirements.txt
```

Optional: create the full conda env used during development:

```bash
conda env create -f requirements.yml
conda activate llm
```

## 2) API key

Create a `.env` in the repo root (or in `Stimulus_Builder/`):

```bash
# macOS/Linux
cp .env.example .env

# Windows (PowerShell)
# Copy-Item .env.example .env
```

Then set `CHAT_AI_API_KEY=...` (and optionally `GWDG_BASE_URL=...`).

## 3) Build designs

```bash
python Stimulus_Builder/build_simplified_experiment.py
```

## 4) Validate + run a safe test

```bash
python Stimulus_Builder/prepare_rating_pipeline.py
python Stimulus_Builder/run_ratings.py --test
```

## 5) Analyze

```bash
python Stimulus_Builder/analyze_ratings.py
```

More detail: `Stimulus_Builder/RUNBOOK.md`.
