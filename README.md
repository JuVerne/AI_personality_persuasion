# AI Personality Persuasion Experiment

A Python framework for testing how different LLM personalities (based on Big-5 personality model) prefer different linguistic styles and message attributes.

## Overview

This project explores the intersection of AI personality models and persuasion linguistics by:

1. **Generating Stimuli Messages** with configurable linguistic attributes (tone, topic, length)
2. **Creating LLM Personalities** based on Big-5 personality types via system prompts with personality scores
3. **Running Comparisons** where the LLM chooses between two messages with different linguistic properties
4. **Collecting Results** showing which personalities prefer which message types
5. **Analyzing Patterns** across multiple iterations to find personality-language preference relationships

## Project Structure

```
AI_personality_persuasion/
├── src/
│   ├── __init__.py                 # Package initialization
│   ├── message_generator.py        # Generates stimuli with linguistic attributes
│   ├── personality_creator.py      # Big-5 personality system prompts with scores
│   ├── llm_interface.py            # OpenAI API interface
│   ├── experiment_runner.py        # Orchestrates the experiment
│   ├── results_manager.py          # Saves and analyzes results
│   └── utils.py                    # Utility functions
├── main.py                         # Entry point
├── advanced_example.py             # Advanced usage examples
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── results/                        # Output directory for results
└── README.md                       # This file
```

## Installation

1. **Clone the repository:**
   ```bash
   cd /workspaces/AI_personality_persuasion
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   nano .env
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

You can also pass the API key directly to the library:

```python
from src.experiment_runner import ExperimentRunner

runner = ExperimentRunner(api_key="sk-...")
```

## Usage

### Basic Usage

Run the default experiment:

```bash
python main.py
```

This will:
- Test your API connection
- Run a small experiment with 2 iterations
- Save results to `results/results_YYYYMMDD_HHMMSS.json` and `.csv`
- Print a summary of findings

### Advanced Usage

Create a custom experiment script:

```python
import sys
sys.path.insert(0, 'src')

from experiment_runner import ExperimentRunner

# Initialize
runner = ExperimentRunner(api_key="sk-...", model="gpt-4")

# Test the setup
runner.test_setup()

# Run custom experiment
runner.run_experiment(
    num_iterations=5,
    personalities=["openness", "conscientiousness", "extraversion"],
    tone_pairs=[("academic", "casual"), ("formal", "informal")],
    topics=["technology", "environment", "education"],
    verbose=True
)

# Save results
runner.save_results()
```

See `advanced_example.py` for more examples.

## Components

### MessageGenerator

Generates short messages with configurable linguistic attributes:

```python
from src.message_generator import MessageGenerator

gen = MessageGenerator()

# Generate single message
msg = gen.generate_message(tone="academic", topic="technology", length="short")
print(msg["message"])

# Generate pair of messages with different tones
msg1, msg2 = gen.generate_pair(tone1="academic", tone2="casual", topic="environment")
```

**Linguistic Attributes:**
- **Tone**: `academic` (formal, technical) or `casual` (conversational, simple)
- **Topic**: `technology`, `environment`, `education` (extensible)
- **Length**: `short` or `long`

### PersonalityCreator

Manages Big-5 personality types with dynamic scoring:

```python
from src.personality_creator import PersonalityCreator

pc = PersonalityCreator(scale=10)  # Scale from 0 to 10

# Available personalities
personalities = pc.list_personalities()
# Output: ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']

# Get system prompt for a personality (uses default high score for that trait)
prompt = pc.get_system_prompt("openness")

# Get custom system prompt with specific scores
custom_prompt = pc.get_system_prompt_with_scores(
    openness=8,
    conscientiousness=6,
    extraversion=7,
    agreeableness=5,
    neuroticism=4
)

# Get full personality info including scores
info = pc.get_personality_info("conscientiousness")
```

**System Prompt Format:**

The personality system prompt presents scores on a scale and instructs the LLM to act as an agent with that personality:

```
People with high openness score are imaginative, curious, and creative. 
Your openness score is 9 out of 10. 

People with high conscientiousness score are disciplined and dependable. 
Your conscientiousness score is 5 out of 10. 

People with high extraversion score are outgoing, enthusiastic, and enjoy 
social interactions. Your extraversion score is 5 out of 10. 

People with high agreeableness score prioritize harmony and positive 
relationships. Your agreeableness score is 5 out of 10. 

People with high neuroticism score are more emotionally reactive and prone 
to mood swings. Your neuroticism score is 5 out of 10. 

From now on, you are an agent with this personality, and you should respond 
based on this personality.
```

**Big-5 Personalities (Default Profiles):**
- **Openness** (9/10): Creative, imaginative, curious
- **Conscientiousness** (9/10): Disciplined, dependable, organized
- **Extraversion** (9/10): Outgoing, enthusiastic, enjoys social interactions
- **Agreeableness** (9/10): Values harmony, prioritizes positive relationships
- **Neuroticism** (9/10): Emotionally reactive, prone to mood swings

Other traits default to 5/10 (moderate) when one is high.

### LLMInterface

Handles communication with the OpenAI API:

```python
from src.llm_interface import LLMInterface

llm = LLMInterface(api_key="sk-...", model="gpt-3.5-turbo")

# Test connection
llm.test_connection()

# Compare two messages
result = llm.compare_messages(
    message1="According to recent research...",
    message2="You know, basically...",
    system_prompt="People with high openness score are imaginative..."
)

print(f"Preferred: Message {result['preferred_message']}")
print(f"Reason: {result['explanation']}")
```

### ResultsManager

Saves and analyzes experiment results:

```python
from src.results_manager import ResultsManager

rm = ResultsManager(results_dir="results")

# Add results
rm.add_result(
    personality_type="openness",
    message1_attrs={"tone": "academic", "topic": "technology"},
    message2_attrs={"tone": "casual", "topic": "technology"},
    preference=1,
    explanation="Preferred the academic version"
)

# Save to files
rm.save_json("my_results.json")
rm.save_csv("my_results.csv")

# Get summary
summary = rm.get_summary()
rm.print_summary()
```

## Results

Results are saved in two formats:

### JSON Format (`results_YYYYMMDD_HHMMSS.json`)

Detailed results including full messages:

```json
[
  {
    "timestamp": "2024-03-04T10:30:45.123456",
    "personality_type": "openness",
    "message1": {
      "tone": "academic",
      "topic": "technology",
      "length": "short",
      "message": "According to recent research..."
    },
    "message2": {
      "tone": "casual",
      "topic": "technology",
      "length": "short",
      "message": "You know, basically..."
    },
    "preferred_message": 1,
    "explanation": "..LLM's explanation..."
  }
]
```

### CSV Format (`results_YYYYMMDD_HHMMSS.csv`)

Tabular format for easy analysis:

```
timestamp,personality_type,message1_tone,message1_topic,message2_tone,message2_topic,preferred_message
2024-03-04T10:30:45.123456,openness,academic,technology,casual,technology,1
```

### Summary Output

```
============================================================
EXPERIMENT SUMMARY
============================================================
Total Results: 30
Personalities Tested: openness, conscientiousness, extraversion, agreeableness, neuroticism

Preferences by Personality:

  openness:
    Total comparisons: 6
    Message 1 preferred: 4 (66.7%)
    Message 2 preferred: 2 (33.3%)

  conscientiousness:
    Total comparisons: 6
    Message 1 preferred: 5 (83.3%)
    Message 2 preferred: 1 (16.7%)
...
============================================================
```

## Examples

See `advanced_example.py` for:
- Custom configuration
- Analyzing specific personality types
- Extending message generator with new topics
- Batch processing

## API Key Setup

### Getting an OpenAI API Key

1. Go to https://platform.openai.com/account/api-keys
2. Click "Create new secret key"
3. Copy the key and add to `.env`:

```bash
OPENAI_API_KEY=sk-your-key-here
```

### Costs

- `gpt-3.5-turbo`: ~$0.0005 per 1K tokens (cheaper)
- `gpt-4`: ~$0.03 per 1K tokens (more capable)

The default experiment (2 iterations, 5 personalities, 2 tone pairs, 2 topics) uses roughly:
- ~150 API calls
- ~$0.10 with gpt-3.5-turbo
- ~$5 with gpt-4

## Troubleshooting

### "API key not found"
- Ensure `.env` file exists in the project root
- Check that `OPENAI_API_KEY` is set correctly
- Verify the key starts with `sk-`

### "Connection test failed"
- Verify your internet connection
- Check your API key is valid
- Ensure you have API credits available
- Try a different model in `.env`

### Import errors
- Ensure you're running from the project root directory
- Verify `src` directory structure is correct
- Try: `python -c "import sys; print(sys.path)"`

## Extending the Framework

### Add New Personality Types

Edit `src/personality_creator.py`:

```python
PERSONALITY_PROFILES = {
    "your_personality": {
        "name": "Your Personality",
        "description": "Description",
        "scores": (8, 6, 5, 4, 3)  # (openness, conscientiousness, extraversion, agreeableness, neuroticism)
    }
}
```

### Add Custom Personality Scores

Generate a system prompt with custom scores:

```python
pc = PersonalityCreator()
custom_prompt = pc.get_system_prompt_with_scores(
    openness=7,
    conscientiousness=8,
    extraversion=6,
    agreeableness=5,
    neuroticism=3
)
```

### Add New Message Topics

Edit `src/message_generator.py`:

```python
TOPICS = {
    "your_topic": [
        "subtopic1",
        "subtopic2",
    ]
}
```

### Add New Linguistic Attributes

Modify the `generate_message()` method to add new parameters and variations.

## Contributing

To extend this project:

1. Add new personality score profiles to `PersonalityCreator`
2. Add new topics to `MessageGenerator`
3. Create new linguistic attributes (complexity, formality, etc.)
4. Analyze patterns in the results
5. Publish findings!

## License

MIT License

## References

- Big-5 Personality Model: Costa & McCrae (1992)
- Language and Personality: Linguistic Inquiry and Word Count (LIWC)
- Persuasion and Linguistics: Cialdini (2006)

## Citation

If you use this framework in research, please cite:

```
@software{ai_personality_persuasion_2024,
  title={AI Personality Persuasion Experiment Framework},
  year={2024}
}
```

---

**Questions?** Check `advanced_example.py` or review the docstrings in each module.
