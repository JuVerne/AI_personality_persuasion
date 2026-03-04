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
    
    def run_single_comparison(
        self,
        personality_type: str,
        emotionality1: str = "emotional",
        emotionality2: str = "rational",
        abstraction1: str = "concrete",
        abstraction2: str = "abstract",
        product: str = "smartwatch"
    ) -> dict:
        """
        Run a single message comparison.
        
        Args:
            personality_type: Big-5 personality type
            emotionality1: Emotionality for first message
            emotionality2: Emotionality for second message
            abstraction1: Abstraction level for first message
            abstraction2: Abstraction level for second message
            product: Product category
            
        Returns:
            Result dictionary
        """
        # Generate message pair
        msg1, msg2 = self.message_generator.generate_pair(
            emotionality1=emotionality1,
            emotionality2=emotionality2,
            abstraction1=abstraction1,
            abstraction2=abstraction2,
            product=product
        )
        
        # Get system prompt for personality
        system_prompt = self.personality_creator.get_system_prompt(personality_type)
        
        # Get LLM evaluation (now with ratings)
        evaluation = self.llm_interface.compare_messages(
            message1=msg1["message"],
            message2=msg2["message"],
            system_prompt=system_prompt
        )
        
        # Save result
        self.results_manager.add_result(
            personality_type=personality_type,
            message1_attrs={
                "emotionality": msg1["emotionality"],
                "abstraction": msg1["abstraction"],
                "product": msg1["product"],
    
    def run_experiment(
        self,
        num_iterations: int = 2,
        personalities: Optional[List[str]] = None,
        emotionality_pairs: Optional[List[tuple]] = None,
        abstraction_pairs: Optional[List[tuple]] = None,
        products: Optional[List[str]] = None,
        verbose: bool = True
    ) -> None:
        """
        Run the full experiment multiple times.
        
        Args:
            num_iterations: Number of times to run the experiment
            personalities: List of personality types to test (None = all)
            emotionality_pairs: List of (emotionality1, emotionality2) tuples
            abstraction_pairs: List of (abstraction1, abstraction2) tuples
            products: List of products to use (None = all)
            verbose: Whether to print progress
        """
        # Set defaults
        if personalities is None:
            personalities = self.personality_creator.list_personalities()
        
        if emotionality_pairs is None:
            emotionality_pairs = [("emotional", "rational"), ("rational", "emotional")]
        
        if abstraction_pairs is None:
            abstraction_pairs = [("concrete", "abstract")]
        
        if products is None:
            products = list(self.message_generator.PRODUCTS.keys())
        
        total_comparisons = 0
        
        try:
            for iteration in range(num_iterations):
                if verbose:
                    print(f"\n--- Iteration {iteration + 1}/{num_iterations} ---")
                
                for personality in personalities:
                    for emo1, emo2 in emotionality_pairs:
                        for abs1, abs2 in abstraction_pairs:
                            for product in products:
                                total_comparisons += 1
                                
                                if verbose:
                                    print(
                                        f"  {personality}: ({emo1}/{abs1}) vs ({emo2}/{abs2}) - {product}",
                                        end=" ... "
                                    )
                                
                                result = self.run_single_comparison(
                                    personality_type=personality,
                                    emotionality1=emo1,
                                    emotionality2=emo2,
                                    abstraction1=abs1,
                                    abstraction2=abs2,
                                    product=product
                                )
                                
                                if verbose:
                                    preferred = "Msg1" if result["preferred_message"] == 1 else "Msg2"
                                    print(f"{preferred} (Ratings: {result['message1_rating']}/7 vs {result['message2_rating']}/7)")
            
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
