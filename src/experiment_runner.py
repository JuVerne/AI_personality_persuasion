"""
Experiment Runner
Orchestrates the complete experiment workflow.
"""

from typing import List, Optional
from message_generator import MessageGenerator
from personality_creator import PersonalityCreator
from llm_interface import LLMInterface
from results_manager import ResultsManager


class ExperimentRunner:
    """Orchestrates the AI personality persuasion experiment."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        results_dir: str = "results"
    ):
        """
        Initialize the experiment runner.
        
        Args:
            api_key: OpenAI API key
            model: Model to use for LLM
            results_dir: Directory to save results
        """
        self.message_generator = MessageGenerator()
        self.personality_creator = PersonalityCreator()
        self.llm_interface = LLMInterface(api_key=api_key, model=model)
        self.results_manager = ResultsManager(results_dir=results_dir)
    
    def run_single_comparison(
        self,
        personality_type: str,
        tone1: str = "academic",
        tone2: str = "casual",
        topic: str = "technology"
    ) -> dict:
        """
        Run a single message comparison.
        
        Args:
            personality_type: Big-5 personality type
            tone1: Tone for first message
            tone2: Tone for second message
            topic: Topic for messages
            
        Returns:
            Result dictionary
        """
        # Generate message pair
        msg1, msg2 = self.message_generator.generate_pair(
            tone1=tone1,
            tone2=tone2,
            topic=topic
        )
        
        # Get system prompt for personality
        system_prompt = self.personality_creator.get_system_prompt(personality_type)
        
        # Get LLM preference
        preference = self.llm_interface.compare_messages(
            message1=msg1["message"],
            message2=msg2["message"],
            system_prompt=system_prompt
        )
        
        # Save result
        self.results_manager.add_result(
            personality_type=personality_type,
            message1_attrs={
                "tone": msg1["tone"],
                "topic": msg1["topic"],
                "length": msg1["length"],
                "message": msg1["message"]
            },
            message2_attrs={
                "tone": msg2["tone"],
                "topic": msg2["topic"],
                "length": msg2["length"],
                "message": msg2["message"]
            },
            preference=preference["preferred_message"],
            explanation=preference["explanation"]
        )
        
        return preference
    
    def run_experiment(
        self,
        num_iterations: int = 5,
        personalities: Optional[List[str]] = None,
        tone_pairs: Optional[List[tuple]] = None,
        topics: Optional[List[str]] = None,
        verbose: bool = True
    ) -> None:
        """
        Run the full experiment multiple times.
        
        Args:
            num_iterations: Number of times to run the experiment
            personalities: List of personality types to test (None = all)
            tone_pairs: List of (tone1, tone2) tuples (None = academic/casual)
            topics: List of topics to use (None = all)
            verbose: Whether to print progress
        """
        # Set defaults
        if personalities is None:
            personalities = self.personality_creator.list_personalities()
        
        if tone_pairs is None:
            tone_pairs = [("academic", "casual"), ("casual", "academic")]
        
        if topics is None:
            topics = list(self.message_generator.TOPICS.keys())
        
        total_comparisons = 0
        
        try:
            for iteration in range(num_iterations):
                if verbose:
                    print(f"\n--- Iteration {iteration + 1}/{num_iterations} ---")
                
                for personality in personalities:
                    for tone1, tone2 in tone_pairs:
                        for topic in topics:
                            total_comparisons += 1
                            
                            if verbose:
                                print(
                                    f"  {personality}: {tone1} vs {tone2} ({topic})",
                                    end=" ... "
                                )
                            
                            result = self.run_single_comparison(
                                personality_type=personality,
                                tone1=tone1,
                                tone2=tone2,
                                topic=topic
                            )
                            
                            if verbose:
                                preferred = "Message 1" if result["preferred_message"] == 1 else "Message 2"
                                print(f"Prefers: {preferred}")
            
            print(f"\n✓ Completed {total_comparisons} comparisons")
            
        except KeyboardInterrupt:
            print(f"\n⚠ Experiment interrupted. {total_comparisons} comparisons completed.")
        except Exception as e:
            print(f"\n✗ Error during experiment: {str(e)}")
            raise
    
    def save_results(self, json_filename: str = None, csv_filename: str = None) -> None:
        """
        Save experiment results.
        
        Args:
            json_filename: Optional JSON filename
            csv_filename: Optional CSV filename
        """
        self.results_manager.save_json(json_filename)
        self.results_manager.save_csv(csv_filename)
        self.results_manager.print_summary()
    
    def test_setup(self) -> bool:
        """
        Test that all components are working.
        
        Returns:
            True if all tests pass
        """
        print("Testing experiment setup...\n")
        
        # Test message generator
        print("✓ Message generator initialized")
        
        # Test personality creator
        print("✓ Personality creator initialized")
        
        # Test LLM connection
        print("Testing LLM API connection...", end=" ")
        if self.llm_interface.test_connection():
            print("✓ Connected")
        else:
            print("✗ Failed")
            return False
        
        # Test single generation
        print("Testing message generation...", end=" ")
        msg1, msg2 = self.message_generator.generate_pair()
        print("✓ Generated")
        
        print("\nAll tests passed! Ready to run experiments.")
        return True
