"""
Advanced Examples
Demonstrates advanced usage of the AI Personality Persuasion framework.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils import load_env_file
from experiment_runner import ExperimentRunner
from message_generator import MessageGenerator
from personality_creator import PersonalityCreator


def example_1_basic_usage():
    """Example 1: Basic experiment run."""
    print("\n" + "="*60)
    print("Example 1: Basic Experiment Run")
    print("="*60)
    
    load_env_file()
    runner = ExperimentRunner()
    
    # Test setup
    print("\nTesting setup...")
    runner.test_setup()
    
    # Run small experiment
    print("\nRunning 1 iteration with all personalities...")
    runner.run_experiment(
        num_iterations=1,
        personalities=None,  # All personalities
        tone_pairs=[("academic", "casual")],
        topics=["technology"],
        verbose=True
    )
    
    # Show results
    runner.save_results()


def example_2_focus_personalities():
    """Example 2: Focus on specific personalities."""
    print("\n" + "="*60)
    print("Example 2: Focus on Specific Personalities")
    print("="*60)
    
    load_env_file()
    runner = ExperimentRunner()
    
    print("\nTesting specific personalities: Openness vs Conscientiousness")
    print("These represent creative vs organized thinking styles\n")
    
    runner.run_experiment(
        num_iterations=2,
        personalities=["openness", "conscientiousness"],  # Compare these two
        tone_pairs=[("academic", "casual"), ("formal", "informal")],
        topics=["technology", "environment"],
        verbose=True
    )
    
    runner.save_results()


def example_3_message_generation_demo():
    """Example 3: Demonstrate message generation."""
    print("\n" + "="*60)
    print("Example 3: Message Generation Demo")
    print("="*60)
    
    gen = MessageGenerator()
    
    print("\nSame topic, different tones:\n")
    
    # Academic version
    academic = gen.generate_message(tone="academic", topic="technology")
    print("ACADEMIC:")
    print(academic["message"])
    
    # Casual version
    casual = gen.generate_message(tone="casual", topic="technology")
    print("\nCASUAL:")
    print(casual["message"])
    
    print("\n---")
    print(f"\nGenerated {gen.get_generated_count()} total messages")


def example_4_personality_demo():
    """Example 4: Demonstrate personality system prompts."""
    print("\n" + "="*60)
    print("Example 4: Personality System Prompts")
    print("="*60)
    
    pc = PersonalityCreator()
    
    print("\nBig-5 Personality Types:\n")
    
    for personality_id, info in pc.get_all_personalities().items():
        print(f"[{personality_id.upper()}]")
        print(f"Name: {info['name']}")
        print(f"Description: {info['description']}")
        print(f"Prompt (first 100 chars): {info['system_prompt'][:100]}...")
        print()


def example_5_custom_configuration():
    """Example 5: Custom configuration and detailed output."""
    print("\n" + "="*60)
    print("Example 5: Custom Configuration")
    print("="*60)
    
    load_env_file()
    runner = ExperimentRunner(model="gpt-3.5-turbo")  # Specify model
    
    print("\nCustom configuration:")
    print("- Model: gpt-3.5-turbo")
    print("- Iterations: 1")
    print("- Focus: Testing extraversion preference for social content")
    print("- Topics: environment (with social impact)")
    print()
    
    runner.run_experiment(
        num_iterations=1,
        personalities=["extraversion", "agreeableness"],  # Social personalities
        tone_pairs=[("academic", "casual")],
        topics=["environment"],
        verbose=True
    )
    
    # Get and examine results
    summary = runner.results_manager.get_summary()
    print(f"\nTotal comparisons: {summary['total_results']}")
    print(f"Personalities tested: {summary['personalities_tested']}")
    
    runner.save_results()


def example_6_analyze_preferences():
    """Example 6: Analyze preference patterns."""
    print("\n" + "="*60)
    print("Example 6: Analyze Preference Patterns")
    print("="*60)
    
    load_env_file()
    runner = ExperimentRunner()
    
    print("\nRunning focused experiment to analyze preferences...\n")
    
    # Run experiment
    runner.run_experiment(
        num_iterations=2,
        personalities=["openness", "conscientiousness", "extraversion"],
        tone_pairs=[("academic", "casual")],
        topics=["technology", "education"],
        verbose=True
    )
    
    # Analyze results
    summary = runner.results_manager.get_summary()
    
    print("\n" + "="*60)
    print("PREFERENCE ANALYSIS")
    print("="*60)
    
    for personality, prefs in summary.get("preferences_by_personality", {}).items():
        if prefs["total"] > 0:
            msg1_ratio = prefs["message1_ratio"]
            msg2_ratio = 1 - msg1_ratio
            
            print(f"\n{personality.upper()}:")
            print(f"  Total comparisons: {prefs['total']}")
            print(f"  Message 1 (academic): {msg1_ratio:.1%}")
            print(f"  Message 2 (casual):   {msg2_ratio:.1%}")
            
            if msg1_ratio > 0.65:
                print(f"  → Strongly prefers: ACADEMIC tone")
            elif msg1_ratio > 0.55:
                print(f"  → Slightly prefers: ACADEMIC tone")
            elif msg2_ratio > 0.65:
                print(f"  → Strongly prefers: CASUAL tone")
            elif msg2_ratio > 0.55:
                print(f"  → Slightly prefers: CASUAL tone")
            else:
                print(f"  → No clear preference")


def example_7_interpretation():
    """Example 7: Interpret results through personality lens."""
    print("\n" + "="*60)
    print("Example 7: Interpreting Results Through Personality Lens")
    print("="*60)
    
    print("""
Expected Patterns (based on personality theory):

OPENNESS (Creative, Curious):
- Should appreciate novel linguistic structures
- May prefer casual tone (more creative freedom)
- Look for: Preference for unconventional phrasing

CONSCIENTIOUSNESS (Organized, Reliable):
- Should value clear, structured information
- May prefer academic tone (more systematic)
- Look for: Preference for formal, organized messages

EXTRAVERSION (Social, Energetic):
- Should appreciate engaging, interactive language
- May prefer casual tone (more social)
- Look for: Preference for conversational style

AGREEABLENESS (Compassionate, Cooperative):
- Should value empathetic, person-centered language
- May prefer inclusive framing
- Look for: Preference for warm, inclusive tone

NEUROTICISM (Cautious, Sensitive):
- Should appreciate thorough, careful language
- May prefer academic tone (more careful/precise)
- Look for: Preference for detailed, cautious framing

Running experiments and analyzing preference patterns will reveal if
the LLM personalities actually exhibit these linguistic preferences!
    """)


def main():
    """Run examples interactively."""
    print("\n" + "="*60)
    print("AI Personality Persuasion - Advanced Examples")
    print("="*60)
    
    examples = {
        "1": ("Basic Usage", example_1_basic_usage),
        "2": ("Focus on Specific Personalities", example_2_focus_personalities),
        "3": ("Message Generation Demo", example_3_message_generation_demo),
        "4": ("Personality System Prompts", example_4_personality_demo),
        "5": ("Custom Configuration", example_5_custom_configuration),
        "6": ("Analyze Preferences", example_6_analyze_preferences),
        "7": ("Interpretation Guide", example_7_interpretation),
    }
    
    print("\nSelect an example to run:")
    for key, (name, _) in examples.items():
        print(f"  {key}) {name}")
    print("  0) Run all examples")
    print("  q) Quit")
    
    choice = input("\nEnter your choice: ").strip().lower()
    
    try:
        if choice == "q":
            print("Goodbye!")
            return
        elif choice == "0":
            for key in sorted(examples.keys()):
                try:
                    examples[key][1]()
                except Exception as e:
                    print(f"Error in example {key}: {e}")
        elif choice in examples:
            examples[choice][1]()
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
