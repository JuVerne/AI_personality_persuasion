# Quick Start Guide

## Note on Active Workflow

For current work, use the `Stimulus_Builder/` pipeline:
- `python Stimulus_Builder/build_simplified_experiment.py`
- `python Stimulus_Builder/run_ratings.py --test`

The steps below describe the older `src/` experiment path.

## 1. Setup (2 minutes)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment file
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## 2. Run the Experiment (5-10 minutes)

```bash
python main.py
```

This will:
- Test your API connection
- Run a quick 2-iteration experiment
- Save results to `results/`
- Print a summary

## 3. Explore Results

Check these files after running:
- `results/results_YYYYMMDD_HHMMSS.json` - Full detailed results
- `results/results_YYYYMMDD_HHMMSS.csv` - Easy-to-analyze CSV format

## 4. Advanced Usage

For more examples and customization:
```bash
python advanced_example.py
```

Or customize `main.py` and run:
```python
runner.run_experiment(
    num_iterations=5,
    personalities=["openness", "conscientiousness"],
    tone_pairs=[("academic", "casual")],
    topics=["technology"],
    verbose=True
)
```

## API Key Setup

1. Get an API key from https://platform.openai.com/account/api-keys
2. Add to `.env`: `OPENAI_API_KEY=sk-your-key-here`
3. Run `python main.py`

## What Happens in the Experiment

1. **Generate Messages**: Creates short messages with different linguistic styles
   - Tone: academic vs casual
   - Topics: technology, environment, education
   
2. **Apply Personality**: System prompts make the LLM adopt Big-5 personalities
   - Openness (creative)
   - Conscientiousness (organized)
   - Extraversion (social)
   - Agreeableness (compassionate)
   - Neuroticism (cautious)

3. **Compare Preferences**: Each personality chooses between two messages
   - Records which message it prefers
   - Saves explanation

4. **Analyze Results**: Summary shows preference patterns
   - Which personalities prefer which tone/style
   - Potential insights about AI personality-language interaction

## Expected Results

You should see which personality types prefer different linguistic styles:
- Creative types → casual tone?
- Organized types → academic tone?
- Social types → engaging tone?

## Cost Estimate

Default experiment (2 iterations, 5 personalities, 2 tone pairs, 2 topics):
- ~150 API calls
- ~$0.10 with gpt-3.5-turbo
- ~$5 with gpt-4

## Troubleshooting

**"API key error"** → Check .env file has correct key starting with `sk-`

**"Connection failed"** → Verify internet connection and API credits

**"Import errors"** → Run from project root: `python main.py`

## Next Steps

- Run more iterations for statistical significance
- Add new topics or linguistic attributes
- Analyze patterns by personality type
- Publish findings!

---
See README.md for full documentation
