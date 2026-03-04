"""
Utility functions for the experiment.
"""

import os
from typing import Optional


def load_env_file(env_file: str = ".env") -> None:
    """
    Load environment variables from a .env file.
    
    Args:
        env_file: Path to .env file
    """
    if not os.path.exists(env_file):
        print(f"Warning: {env_file} not found")
        return
    
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()


def validate_api_key(api_key: Optional[str] = None) -> str:
    """
    Validate and retrieve API key.
    
    Args:
        api_key: Optional API key to validate
        
    Returns:
        Valid API key
        
    Raises:
        ValueError: If no valid API key found
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    
    if not key:
        raise ValueError(
            "No API key provided. Set OPENAI_API_KEY environment variable or pass as argument."
        )
    
    if not key.startswith("sk-"):
        print("Warning: API key doesn't start with 'sk-', may be invalid")
    
    return key


def format_message_for_display(message: str, max_length: int = 80) -> str:
    """
    Format a message for display.
    
    Args:
        message: Message to format
        max_length: Maximum display length
        
    Returns:
        Formatted message
    """
    if len(message) <= max_length:
        return message
    return message[:max_length] + "..."
