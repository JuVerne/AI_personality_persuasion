"""
AI Personality Persuasion Experiment
A framework for testing how different LLM personalities prefer different linguistic styles.
"""

from .message_generator import MessageGenerator
from .personality_creator import PersonalityCreator
from .llm_interface import LLMInterface
from .results_manager import ResultsManager
from .experiment_runner import ExperimentRunner

__version__ = "0.1.0"
__all__ = [
    "MessageGenerator",
    "PersonalityCreator",
    "LLMInterface",
    "ResultsManager",
    "ExperimentRunner"
]
