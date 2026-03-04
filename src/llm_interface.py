"""
LLM Interface
Handles communication with the LLM API (OpenAI by default).
"""

import os
from typing import Dict, Optional
import json


class LLMInterface:
    """Interface for interacting with LLM APIs."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM interface.
        
        Args:
            api_key: API key for the LLM service (defaults to env variable)
            model: Model name to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not provided and OPENAI_API_KEY environment variable not set"
            )
        self.model = model
        self._init_client()
    
    def _init_client(self):
        """Initialize the OpenAI client."""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def compare_messages(
        self,
        message1: str,
        message2: str,
        system_prompt: str,
        temperature: float = 0.7
    ) -> Dict[str, any]:
        """
        Ask the LLM to compare two messages and choose a preference.
        
        Args:
            message1: First message for comparison
            message2: Second message for comparison
            system_prompt: System prompt defining the personality
            temperature: Temperature for LLM response
            
        Returns:
            Dictionary with preference and details
        """
        comparison_prompt = f"""You are comparing two messages. Please read both carefully and determine which one you prefer.

MESSAGE 1:
{message1}

MESSAGE 2:
{message2}

Please respond with just the number (1 or 2) of the message you prefer, followed by a brief explanation (1-2 sentences) of why you prefer it."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": comparison_prompt}
                ],
                temperature=temperature,
                max_tokens=100
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse response
            preferred = self._parse_preference(response_text)
            
            return {
                "preferred_message": preferred,
                "explanation": response_text,
                "raw_response": response_text,
                "model": self.model,
                "temperature": temperature
            }
        
        except Exception as e:
            raise RuntimeError(f"Error calling LLM API: {str(e)}")
    
    def _parse_preference(self, response_text: str) -> int:
        """
        Parse the LLM response to extract preference.
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Integer (1 or 2) indicating preference
        """
        # Extract first digit found (1 or 2)
        for char in response_text:
            if char in ['1', '2']:
                return int(char)
        
        # Fallback: look for words indicating preference
        response_lower = response_text.lower()
        if 'first' in response_lower or 'message 1' in response_lower:
            return 1
        elif 'second' in response_lower or 'message 2' in response_lower:
            return 2
        else:
            # Default to 1 if unable to parse
            return 1
    
    def test_connection(self) -> bool:
        """
        Test the API connection.
        
        Returns:
            True if connection successful
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False
