"""
Results Manager
Saves and manages experiment results.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import csv


class ResultsManager:
    """Manages saving and organizing experiment results."""
    
    def __init__(self, results_dir: str = "results"):
        """
        Initialize the results manager.
        
        Args:
            results_dir: Directory to save results
        """
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        self.results = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def add_result(
        self,
        personality_type: str,
        message1_attrs: Dict[str, Any],
        message2_attrs: Dict[str, Any],
        preference: int,
        explanation: str,
        **kwargs
    ) -> None:
        """
        Add a single experiment result.
        
        Args:
            personality_type: The Big-5 personality type used
            message1_attrs: Attributes of first message
            message2_attrs: Attributes of second message
            preference: Which message was preferred (1 or 2)
            explanation: LLM's explanation of preference
            **kwargs: Additional metadata
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "personality_type": personality_type,
            "message1": message1_attrs,
            "message2": message2_attrs,
            "preferred_message": preference,
            "explanation": explanation,
            **kwargs
        }
        self.results.append(result)
    
    def save_json(self, filename: str = None) -> str:
        """
        Save results as JSON.
        
        Args:
            filename: Optional filename (defaults to timestamped file)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"results_{self.timestamp}.json"
        
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to {filepath}")
        return filepath
    
    def save_csv(self, filename: str = None) -> str:
        """
        Save results as CSV for easier analysis.
        
        Args:
            filename: Optional filename (defaults to timestamped file)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"results_{self.timestamp}.csv"
        
        filepath = os.path.join(self.results_dir, filename)
        
        if not self.results:
            print("No results to save")
            return filepath
        
        # Flatten the results for CSV
        flattened = []
        for result in self.results:
            flat = {
                "timestamp": result["timestamp"],
                "personality_type": result["personality_type"],
                "message1_tone": result["message1"].get("tone", ""),
                "message1_topic": result["message1"].get("topic", ""),
                "message1_length": result["message1"].get("length", ""),
                "message2_tone": result["message2"].get("tone", ""),
                "message2_topic": result["message2"].get("topic", ""),
                "message2_length": result["message2"].get("length", ""),
                "preferred_message": result["preferred_message"],
                "explanation": result["explanation"][:100] if result.get("explanation") else ""
            }
            flattened.append(flat)
        
        if flattened:
            fieldnames = flattened[0].keys()
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flattened)
        
        print(f"CSV results saved to {filepath}")
        return filepath
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of results.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.results:
            return {"total_results": 0}
        
        summary = {
            "total_results": len(self.results),
            "personalities_tested": list(set(r["personality_type"] for r in self.results)),
            "preferences_by_personality": {}
        }
        
        # Count preferences by personality type
        for personality in summary["personalities_tested"]:
            personality_results = [
                r for r in self.results 
                if r["personality_type"] == personality
            ]
            message1_preferred = sum(
                1 for r in personality_results 
                if r["preferred_message"] == 1
            )
            message2_preferred = sum(
                1 for r in personality_results 
                if r["preferred_message"] == 2
            )
            
            summary["preferences_by_personality"][personality] = {
                "total": len(personality_results),
                "message1_preferred": message1_preferred,
                "message2_preferred": message2_preferred,
                "message1_ratio": message1_preferred / len(personality_results) if personality_results else 0
            }
        
        return summary
    
    def print_summary(self) -> None:
        """Print a human-readable summary of results."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("EXPERIMENT SUMMARY")
        print("="*60)
        print(f"Total Results: {summary['total_results']}")
        print(f"Personalities Tested: {', '.join(summary['personalities_tested'])}")
        print("\nPreferences by Personality:")
        
        for personality, prefs in summary.get("preferences_by_personality", {}).items():
            print(f"\n  {personality}:")
            print(f"    Total comparisons: {prefs['total']}")
            print(f"    Message 1 preferred: {prefs['message1_preferred']} ({prefs['message1_ratio']:.1%})")
            print(f"    Message 2 preferred: {prefs['message2_preferred']} ({1-prefs['message1_ratio']:.1%})")
        
        print("\n" + "="*60)
