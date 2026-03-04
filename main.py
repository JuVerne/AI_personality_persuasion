"""
Main entry point for the AI Personality Persuasion experiment.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils import load_env_file, validate_api_key
from experiment_runner import ExperimentRunner


def main():
    """Run the experiment."""
    
    # Load environment variables from .env file
    load_env_file()
    
    # Validate API key
    try:
        api_key = validate_api_key()
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set your OpenAI API key:")
        print("  1. Create a .env file with: OPENAI_API_KEY=sk-...")
        print("  2. Or set the environment variable: export OPENAI_API_KEY=sk-...")
        sys.exit(1)
    
    print("🚀 AI Personality Persuasion Experiment")
    print("=" * 50)
    
    # Initialize experiment runner
    runner = ExperimentRunner(api_key=api_key)
    
    # Test setup
    print("\nStep 1: Testing Setup")
    print("-" * 50)
    if not runner.test_setup():
        print("Setup test failed. Please check your API key and connection.")
        sys.exit(1)
    
    # Run experiment
    print("\nStep 2: Running Experiment")
    print("-" * 50)
    
    # Configuration for the experiment
    num_iterations = 2  # Number of times to repeat the experiment
    personalities = None  # None = test all personalities
    tone_pairs = [("academic", "casual"), ("casual", "academic")]
    topics = ["technology", "environment"]  # Can add more topics
    
    print(f"Configuration:")
    print(f"  Iterations: {num_iterations}")
    print(f"  Tone pairs: {len(tone_pairs)}")
    print(f"  Topics: {len(topics)}")
    print(f"  Personalities: All available")
    
    try:
        runner.run_experiment(
            num_iterations=num_iterations,
            personalities=personalities,
            tone_pairs=tone_pairs,
            topics=topics,
            verbose=True
        )
    except Exception as e:
        print(f"Error during experiment: {e}")
        sys.exit(1)
    
    # Save results
    print("\nStep 3: Saving Results")
    print("-" * 50)
    runner.save_results()
    
    print("\n✅ Experiment completed successfully!")


if __name__ == "__main__":
    main()
